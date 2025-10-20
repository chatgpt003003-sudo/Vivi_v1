import sys
import os
# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src.storage.db_connection import DatabaseConnection
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Celebrity Index Collector",
    page_icon="⭐",
    layout="wide"
)

class CelebrityDashboard:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        if self.conn is None:
            self.conn = DatabaseConnection.get_connection()
        return self.conn

    def get_latest_rankings(self, limit=100):
        """Get latest sentiment rankings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get most recent data for each celebrity
        query = """
            WITH ranked_data AS (
                SELECT
                    name,
                    sentiment,
                    created_at,
                    cleaned_paragraph,
                    source,
                    ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) as rn
                FROM celebrity_data
            )
            SELECT
                name,
                sentiment,
                created_at,
                cleaned_paragraph,
                source
            FROM ranked_data
            WHERE rn = 1
            ORDER BY sentiment DESC
            LIMIT %s
        """

        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()

        df = pd.DataFrame(results, columns=[
            'Name', 'Sentiment Score', 'Date', 'Summary', 'Source'
        ])

        return df

    def get_celebrity_trend(self, celebrity_name, days=7):
        """Get sentiment trend for a celebrity"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT created_at, sentiment, cleaned_paragraph
            FROM celebrity_data
            WHERE name = %s
            AND created_at >= %s
            ORDER BY created_at ASC
        """

        start_date = datetime.now() - timedelta(days=days)
        cursor.execute(query, (celebrity_name, start_date))
        results = cursor.fetchall()
        cursor.close()

        df = pd.DataFrame(results, columns=['Date', 'Sentiment Score', 'Summary'])
        return df

    def get_statistics(self):
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total records and unique celebrities
        cursor.execute("""
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT name) as unique_celebrities,
                AVG(sentiment) as avg_sentiment
            FROM celebrity_data
        """)
        total, unique, avg_sent = cursor.fetchone()

        # Sentiment distribution
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN sentiment > 0.3 THEN 1 END) as positive,
                COUNT(CASE WHEN sentiment BETWEEN -0.3 AND 0.3 THEN 1 END) as neutral,
                COUNT(CASE WHEN sentiment < -0.3 THEN 1 END) as negative
            FROM (
                SELECT DISTINCT ON (name) name, sentiment
                FROM celebrity_data
                ORDER BY name, created_at DESC
            ) latest
        """)
        pos, neu, neg = cursor.fetchone()

        cursor.close()

        return {
            'total_records': total,
            'unique_celebrities': unique,
            'avg_sentiment': float(avg_sent) if avg_sent else 0.0,
            'positive': pos,
            'neutral': neu,
            'negative': neg
        }

def main():
    st.title("⭐ Celebrity Index Collector")
    st.markdown("Real-time celebrity sentiment analysis for Taiwan")

    dashboard = CelebrityDashboard()

    # Sidebar
    st.sidebar.header("Settings")
    view_mode = st.sidebar.radio("View Mode", ["Rankings", "Celebrity Trend", "Statistics"])

    if view_mode == "Rankings":
        st.header("📊 Celebrity Sentiment Rankings")

        # Get data
        df = dashboard.get_latest_rankings()

        if not df.empty:
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Celebrities", len(df))
            with col2:
                avg_sentiment = df['Sentiment Score'].mean()
                st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
            with col3:
                positive_count = len(df[df['Sentiment Score'] > 0.3])
                st.metric("Positive Sentiment", positive_count)

            # Sort options
            sort_by = st.selectbox(
                "Sort by",
                ["Highest Sentiment", "Lowest Sentiment", "Most Recent"]
            )

            if sort_by == "Highest Sentiment":
                df = df.sort_values('Sentiment Score', ascending=False)
            elif sort_by == "Lowest Sentiment":
                df = df.sort_values('Sentiment Score', ascending=True)
            else:
                df = df.sort_values('Date', ascending=False)

            # Display table
            st.subheader("Celebrity Rankings")

            # Create display dataframe
            display_df = df[['Name', 'Sentiment Score', 'Date']].copy()
            display_df['Sentiment Score'] = display_df['Sentiment Score'].apply(lambda x: f"{x:.2f}")
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d %H:%M')

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Expandable details
            st.subheader("Details")
            selected_celebrity = st.selectbox("Select celebrity for details", df['Name'].tolist())

            if selected_celebrity:
                celeb_data = df[df['Name'] == selected_celebrity].iloc[0]

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown("**Summary:**")
                    st.write(celeb_data['Summary'])

                with col2:
                    st.metric("Sentiment", f"{celeb_data['Sentiment Score']:.2f}")
                    sentiment_category = "Positive" if celeb_data['Sentiment Score'] > 0.3 else "Negative" if celeb_data['Sentiment Score'] < -0.3 else "Neutral"
                    st.write(f"**Category:** {sentiment_category}")

                if celeb_data['Source']:
                    st.markdown(f"**Source:** [{celeb_data['Source'][:50]}...]({celeb_data['Source']})")

            # Visualization
            st.subheader("📈 Sentiment Distribution")

            # Top 20 celebrities chart
            top_20 = df.head(20)

            fig = px.bar(
                top_20,
                x='Name',
                y='Sentiment Score',
                color='Sentiment Score',
                color_continuous_scale=['red', 'yellow', 'green'],
                title='Top 20 Celebrities by Sentiment',
                labels={'Sentiment Score': 'Sentiment', 'Name': 'Celebrity'}
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No data available. Run the data pipeline first to collect celebrity data.")
            st.info("💡 Run: `venv/bin/python tests/integration/test_pipeline.py`")

    elif view_mode == "Celebrity Trend":
        st.header("📈 Celebrity Sentiment Trend")

        # Get celebrity list
        df = dashboard.get_latest_rankings()

        if not df.empty:
            celebrity_names = sorted(df['Name'].unique().tolist())
            selected_celebrity = st.selectbox("Select Celebrity", celebrity_names)

            days = st.slider("Days to show", 1, 30, 7)

            # Get trend data
            trend_df = dashboard.get_celebrity_trend(selected_celebrity, days)

            if not trend_df.empty:
                # Line chart
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=trend_df['Date'],
                    y=trend_df['Sentiment Score'],
                    mode='lines+markers',
                    name='Sentiment Score',
                    line=dict(color='royalblue', width=3),
                    marker=dict(size=8)
                ))

                # Add horizontal lines for sentiment thresholds
                fig.add_hline(y=0.3, line_dash="dash", line_color="green", annotation_text="Positive threshold")
                fig.add_hline(y=-0.3, line_dash="dash", line_color="red", annotation_text="Negative threshold")
                fig.add_hline(y=0, line_dash="dot", line_color="gray", annotation_text="Neutral")

                fig.update_layout(
                    title=f'Sentiment Trend for {selected_celebrity}',
                    xaxis_title='Date',
                    yaxis_title='Sentiment Score',
                    yaxis_range=[-1.1, 1.1],
                    height=500,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

                # Data table
                st.subheader("Historical Data")
                display_trend = trend_df[['Date', 'Sentiment Score']].copy()
                display_trend['Date'] = pd.to_datetime(display_trend['Date']).dt.strftime('%Y-%m-%d %H:%M')
                display_trend['Sentiment Score'] = display_trend['Sentiment Score'].apply(lambda x: f"{x:.2f}")

                st.dataframe(display_trend, use_container_width=True, hide_index=True)

                # Show latest summary
                if not trend_df['Summary'].isna().all():
                    st.subheader("Latest Summary")
                    latest_summary = trend_df.iloc[-1]['Summary']
                    st.write(latest_summary)

            else:
                st.info(f"No trend data available for {selected_celebrity} in the last {days} days.")

        else:
            st.warning("No celebrities in database yet.")

    else:  # Statistics view
        st.header("📊 Overall Statistics")

        stats = dashboard.get_statistics()

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Records", stats['total_records'])

        with col2:
            st.metric("Unique Celebrities", stats['unique_celebrities'])

        with col3:
            st.metric("Average Sentiment", f"{stats['avg_sentiment']:.2f}")

        with col4:
            total = stats['positive'] + stats['neutral'] + stats['negative']
            if total > 0:
                positive_pct = stats['positive'] / total * 100
                st.metric("Positive %", f"{positive_pct:.1f}%")
            else:
                st.metric("Positive %", "0%")

        # Sentiment distribution pie chart
        st.subheader("Sentiment Distribution")

        if stats['positive'] + stats['neutral'] + stats['negative'] > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Positive', 'Neutral', 'Negative'],
                values=[stats['positive'], stats['neutral'], stats['negative']],
                marker_colors=['green', 'gray', 'red'],
                hole=.3
            )])

            fig.update_layout(
                title="Celebrity Sentiment Distribution",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Detailed breakdown
            col1, col2, col3 = st.columns(3)

            total = stats['positive'] + stats['neutral'] + stats['negative']

            with col1:
                st.success(f"**Positive:** {stats['positive']} ({stats['positive']/total*100:.1f}%)")

            with col2:
                st.info(f"**Neutral:** {stats['neutral']} ({stats['neutral']/total*100:.1f}%)")

            with col3:
                st.error(f"**Negative:** {stats['negative']} ({stats['negative']/total*100:.1f}%)")

        else:
            st.warning("No data available for statistics.")

        # Recent activity
        st.subheader("Recent Activity")

        df = dashboard.get_latest_rankings(limit=10)
        if not df.empty:
            recent_df = df[['Name', 'Sentiment Score', 'Date']].copy()
            recent_df['Sentiment Score'] = recent_df['Sentiment Score'].apply(lambda x: f"{x:.2f}")
            recent_df['Date'] = pd.to_datetime(recent_df['Date']).dt.strftime('%Y-%m-%d %H:%M')

            st.dataframe(recent_df, use_container_width=True, hide_index=True)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Celebrity Index Collector**

    🔍 Data Collection: Google Search API
    🧹 Text Cleaning: Google Gemini API
    💭 Sentiment Analysis: Google Gemini API
    💾 Database: PostgreSQL
    """)

if __name__ == "__main__":
    main()
