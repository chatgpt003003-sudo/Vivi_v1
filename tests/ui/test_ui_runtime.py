#!/usr/bin/env python
"""
UI Runtime Test - Simulates UI functions without launching Streamlit
Tests the UI logic without the Streamlit server
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock streamlit before importing
class MockStreamlit:
    def set_page_config(self, **kwargs):
        print(f"✓ Page config set: {kwargs.get('page_title', 'N/A')}")

    def title(self, text):
        print(f"✓ Title: {text}")

    def markdown(self, text):
        pass

    def header(self, text):
        print(f"✓ Header: {text}")

    def subheader(self, text):
        print(f"✓ Subheader: {text}")

    def metric(self, label, value):
        print(f"  {label}: {value}")

    def dataframe(self, *args, **kwargs):
        print(f"✓ DataFrame displayed")

    def selectbox(self, label, options):
        print(f"✓ Selectbox: {label} ({len(options)} options)")
        return options[0] if options else None

    def radio(self, label, options):
        print(f"✓ Radio: {label}")
        return options[0] if options else None

    def slider(self, label, min_val, max_val, default):
        print(f"✓ Slider: {label} ({min_val}-{max_val}, default={default})")
        return default

    def plotly_chart(self, fig, **kwargs):
        print(f"✓ Plotly chart rendered")

    def warning(self, text):
        print(f"⚠ Warning: {text}")

    def info(self, text):
        print(f"ℹ Info: {text}")

    def columns(self, num):
        return [self] * num

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    class sidebar:
        @staticmethod
        def header(text):
            print(f"✓ Sidebar header: {text}")

        @staticmethod
        def radio(label, options):
            print(f"✓ Sidebar radio: {label}")
            return options[0] if options else None

        @staticmethod
        def selectbox(label, options):
            print(f"✓ Sidebar selectbox: {label}")
            return options[0] if options else None

        @staticmethod
        def markdown(text):
            pass

        @staticmethod
        def info(text):
            pass

# Inject mock
sys.modules['streamlit'] = MockStreamlit()

def test_ui_class_initialization():
    """Test CelebrityDashboard class"""
    print("=" * 60)
    print("Test 1: UI Class Initialization")
    print("=" * 60)

    try:
        # Import after mocking
        from src.ui.app import CelebrityDashboard

        dashboard = CelebrityDashboard()
        print("✓ CelebrityDashboard initialized")

        return True

    except Exception as e:
        print(f"✗ Initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rankings_method():
    """Test get_latest_rankings method"""
    print("\n" + "=" * 60)
    print("Test 2: Rankings Method")
    print("=" * 60)

    try:
        from src.ui.app import CelebrityDashboard

        dashboard = CelebrityDashboard()
        df = dashboard.get_latest_rankings(limit=10)

        print(f"✓ Rankings method executed")
        print(f"✓ Retrieved {len(df)} records")
        print(f"✓ Columns: {list(df.columns)}")

        if not df.empty:
            print(f"\nTop 3:")
            for i, row in df.head(3).iterrows():
                print(f"  {i+1}. {row['Name']}: {row['Sentiment Score']:.2f}")

        return True

    except Exception as e:
        print(f"✗ Rankings method error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics_method():
    """Test get_statistics method"""
    print("\n" + "=" * 60)
    print("Test 3: Statistics Method")
    print("=" * 60)

    try:
        from src.ui.app import CelebrityDashboard

        dashboard = CelebrityDashboard()
        stats = dashboard.get_statistics()

        print(f"✓ Statistics method executed")
        print(f"\nStatistics:")
        print(f"  Total records: {stats['total_records']}")
        print(f"  Unique celebrities: {stats['unique_celebrities']}")
        print(f"  Average sentiment: {stats['avg_sentiment']:.2f}")
        print(f"  Positive: {stats['positive']}")
        print(f"  Neutral: {stats['neutral']}")
        print(f"  Negative: {stats['negative']}")

        return True

    except Exception as e:
        print(f"✗ Statistics method error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_trend_method():
    """Test get_celebrity_trend method"""
    print("\n" + "=" * 60)
    print("Test 4: Trend Method")
    print("=" * 60)

    try:
        from src.ui.app import CelebrityDashboard

        dashboard = CelebrityDashboard()

        # Get a celebrity name
        df = dashboard.get_latest_rankings(limit=1)
        if df.empty:
            print("✗ No celebrities in database")
            return False

        test_celeb = df.iloc[0]['Name']
        print(f"\nTesting trend for: {test_celeb}")

        trend_df = dashboard.get_celebrity_trend(test_celeb, days=7)

        print(f"✓ Trend method executed")
        print(f"✓ Retrieved {len(trend_df)} trend records")

        if not trend_df.empty:
            print(f"\nTrend data:")
            for i, row in trend_df.iterrows():
                print(f"  {row['Date']}: {row['Sentiment Score']:.2f}")

        return True

    except Exception as e:
        print(f"✗ Trend method error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_chart_generation():
    """Test chart generation (without rendering)"""
    print("\n" + "=" * 60)
    print("Test 5: Chart Generation")
    print("=" * 60)

    try:
        from src.ui.app import CelebrityDashboard
        import plotly.express as px
        import plotly.graph_objects as go

        dashboard = CelebrityDashboard()
        df = dashboard.get_latest_rankings(limit=20)

        if df.empty:
            print("✗ No data for charts")
            return False

        # Test bar chart
        fig1 = px.bar(
            df.head(10),
            x='Name',
            y='Sentiment Score',
            color='Sentiment Score',
            color_continuous_scale=['red', 'yellow', 'green']
        )
        print("✓ Bar chart created")

        # Test line chart (if trend data exists)
        test_celeb = df.iloc[0]['Name']
        trend_df = dashboard.get_celebrity_trend(test_celeb, days=7)

        if not trend_df.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=trend_df['Date'],
                y=trend_df['Sentiment Score'],
                mode='lines+markers'
            ))
            print("✓ Line chart created")

        # Test pie chart
        stats = dashboard.get_statistics()
        fig3 = go.Figure(data=[go.Pie(
            labels=['Positive', 'Neutral', 'Negative'],
            values=[stats['positive'], stats['neutral'], stats['negative']]
        )])
        print("✓ Pie chart created")

        return True

    except Exception as e:
        print(f"✗ Chart generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("CELEBRITY INDEX COLLECTOR - UI RUNTIME TEST")
    print("=" * 60)
    print()

    tests = [
        ("UI Class Initialization", test_ui_class_initialization),
        ("Rankings Method", test_rankings_method),
        ("Statistics Method", test_statistics_method),
        ("Trend Method", test_trend_method),
        ("Chart Generation", test_chart_generation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 60)
        print("✓ ALL RUNTIME TESTS PASSED")
        print("=" * 60)
        print("\nUI is ready to launch!")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ SOME RUNTIME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
