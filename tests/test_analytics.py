import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.query_builder import QueryBuilder

class TestQueryBuilder:
    """Tests for the QueryBuilder class"""
    
    def test_get_data_summary(self):
        """Test data summary retrieval"""
        test_data = [
            {"product": "Transformer", "quantity": 10, "price": 150.5, "region": "East"},
            {"product": "Battery", "quantity": 5, "price": 250.0, "region": "West"},
            {"product": "Inverter", "quantity": 8, "price": 180.75, "region": "North"},
            {"product": "Diary", "quantity": 15, "price": 25.5, "region": "South"},
            {"product": "Accessories", "quantity": 20, "price": 45.25, "region": "East"}
        ]
        
        import io
        data_json = pd.DataFrame(test_data).to_json(orient='records')
        result = QueryBuilder.get_data_summary(data_json)
        
        assert result['success'] == True
        assert 'summary' in result
        
        summary = result['summary']
        assert summary['row_count'] == 5
        assert summary['column_count'] == 4
        
        columns = summary['columns']
        assert len(columns) == 4
        
        # Check product column (string type)
        product_col = next(col for col in columns if col['name'] == 'product')
        assert product_col['type'] == 'object'
        assert product_col['null_count'] == 0
        assert product_col['unique_count'] == 5
        
        # Check quantity column (numeric type)
        quantity_col = next(col for col in columns if col['name'] == 'quantity')
        assert quantity_col['type'] in ['int64', 'int32']
        assert quantity_col['null_count'] == 0
        assert quantity_col['unique_count'] == 5
        assert quantity_col['min'] == 5
        assert quantity_col['max'] == 20
        assert quantity_col['mean'] == 11.6  # (10+5+8+15+20)/5
        assert quantity_col['sum'] == 58
        
        # Check price column (numeric type)
        price_col = next(col for col in columns if col['name'] == 'price')
        assert price_col['type'] in ['float64', 'float32']
        assert price_col['null_count'] == 0
        assert price_col['unique_count'] == 5
        assert price_col['min'] == 25.5
        assert price_col['max'] == 250.0
    
    def test_get_column_distribution(self):
        """Test column distribution"""
        test_data = [
            {"product": "محول", "quantity": 10, "price": 150.5, "region": "الشرق"},
            {"product": "بطارية", "quantity": 5, "price": 250.0, "region": "الغرب"},
            {"product": "مؤكسِل", "quantity": 8, "price": 180.75, "region": "الشمال"},
            {"product": "دفتر", "quantity": 15, "price": 25.5, "region": "الجنوب"},
            {"product": "ملحقات", "quantity": 20, "price": 45.25, "region": "الشرق"}
        ]
        
        import io
        data_json = pd.DataFrame(test_data).to_json(orient='records')
        
        # Test numeric column distribution
        result = QueryBuilder.get_column_distribution(data_json, 'price')
        
        assert result['success'] == True
        assert 'distribution' in result
        
        distribution = result['distribution']
        assert distribution['column'] == 'price'
        assert distribution['data_type'] in ['float64', 'float32']
        assert distribution['non_null_count'] == 5
        assert distribution['null_count'] == 0
        assert distribution['min'] == 25.5
        assert distribution['max'] == 250.0
        assert distribution['range'] == 224.5
        assert distribution['mean'] == (150.5 + 250.0 + 180.75 + 25.5 + 45.25) / 5
        
        # Test histogram
        assert 'histogram' in distribution
        assert len(distribution['histogram']['bins']) > 0
        assert len(distribution['histogram']['counts']) > 0
        
        # Test categorical column distribution
        result = QueryBuilder.get_column_distribution(data_json, 'region')
        
        assert result['success'] == True
        
        distribution = result['distribution']
        assert distribution['column'] == 'region'
        assert distribution['data_type'] == 'object'
        assert distribution['non_null_count'] == 5
        assert distribution['null_count'] == 0
        
        # Check value counts
        assert 'value_counts' in distribution
        assert len(distribution['value_counts']['values']) == 4  # 4 regions
        assert distribution['value_counts']['counts'] == [2, 1, 1, 1]
    
    def test_execute_query_filters(self):
        """Test query with various filter conditions"""
        test_data = [
            {"product": "محول", "quantity": 10, "price": 150.5, "region": "الشرق"},
            {"product": "بطارية", "quantity": 5, "price": 250.0, "region": "الغرب"},
            {"product": "مؤكسِل", "quantity": 8, "price": 180.75, "region": "الشمال"},
            {"product": "دفتر", "quantity": 15, "price": 25.5, "region": "الجنوب"},
            {"product": "ملحقات", "quantity": 20, "price": 45.25, "region": "الشرق"}
        ]
        
        data_json = pd.DataFrame(test_data).to_json(orient='records')
        
        # Test equals filter
        query = {
            "filters": [{"column": "region", "operator": "equals", "value": "الشرق"}]
        }
        
        result = QueryBuilder.execute_query(data_json, query)
        assert result['success'] == True
        
        results_df = pd.read_json(result['results'], orient='records')
        assert len(results_df) == 2
        assert all(results_df['region'] == 'الشرق')
        
        # Test greater than filter
        query = {
            "filters": [{"column": "quantity", "operator": "greater_than", "value": 10}]
        }
        
        result = QueryBuilder.execute_query(data_json, query)
        results_df = pd.read_json(result['results'], orient='records')
        assert len(results_df) == 2
        assert all(results_df['quantity'] > 10)
    
    def test_execute_query_groupby(self):
        """Test query with group by operations"""
        test_data = [
            {"product": "محول", "quantity": 10, "price": 150.5, "region": "الشرق"},
            {"product": "بطارية", "quantity": 5, "price": 250.0, "region": "الغرب"},
            {"product": "مؤكسِل", "quantity": 8, "price": 180.75, "region": "الشمال"},
            {"product": "دفتر", "quantity": 15, "price": 25.5, "region": "الجنوب"},
            {"product": "ملحقات", "quantity": 20, "price": 45.25, "region": "الشرق"}
        ]
        
        data_json = pd.DataFrame(test_data).to_json(orient='records')
        
        # Test group by region with sum of quantity
        query = {
            "group_by": "region",
            "aggregates": [{"column": "quantity", "type": "sum"}]
        }
        
        result = QueryBuilder.execute_query(data_json, query)
        assert result['success'] == True
        
        results_df = pd.read_json(result['results'], orient='records')
        assert len(results_df) == 4  # 4 distinct regions
        
        # Check total quantity by region
        region_totals = results_df.groupby('region')['quantity'].sum().to_dict()
        assert region_totals['الشرق'] == 30  # 10 + 20
        assert region_totals['الغرب'] == 5
        assert region_totals['الشمال'] == 8
        assert region_totals['الجنوب'] == 15
    
    def test_execute_query_aggregates(self):
        """Test query with various aggregate functions"""
        test_data = [
            {"product": "محول", "quantity": 10, "price": 150.5, "region": "الشرق"},
            {"product": "بطارية", "quantity": 5, "price": 250.0, "region": "الغرب"},
            {"product": "مؤكسِل", "quantity": 8, "price": 180.75, "region": "الشمال"},
            {"product": "دفتر", "quantity": 15, "price": 25.5, "region": "الجنوب"},
            {"product": "ملحقات", "quantity": 20, "price": 45.25, "region": "الشرق"}
        ]
        
        data_json = pd.DataFrame(test_data).to_json(orient='records')
        
        query = {
            "group_by": "region",
            "aggregates": [
                {"column": "quantity", "type": "sum"},
                {"column": "price", "type": "avg"}
            ]
        }
        
        result = QueryBuilder.execute_query(data_json, query)
        assert result['success'] == True
        
        results_df = pd.read_json(result['results'], orient='records')
        
        # Check average price by region
        price_avg = results_df[results_df['region'] == 'الشرق']['price'].iloc[0]
        expected_avg = (150.5 + 45.25) / 2
        assert abs(price_avg - expected_avg) < 0.01


if __name__ == "__main__":
    # Make sure pandas is available
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        print("Error: This test requires pandas and numpy to be installed")
        print("Please run: pip install pandas numpy")
        sys.exit(1)
    
    print("=" * 50)
    print("Running QueryBuilder Tests")
    print("=" * 50)
    
    test_builder = TestQueryBuilder()
    
    try:
        test_builder.test_get_data_summary()
        print("✅ Test 1: Data summary retrieval - PASSED")
    except Exception as e:
        print(f"❌ Test 1: Data summary retrieval - FAILED: {e}")
    
    try:
        test_builder.test_get_column_distribution()
        print("✅ Test 2: Column distribution - PASSED")
    except Exception as e:
        print(f"❌ Test 2: Column distribution - FAILED: {e}")
    
    try:
        test_builder.test_execute_query_filters()
        print("✅ Test 3: Query with filters - PASSED")
    except Exception as e:
        print(f"❌ Test 3: Query with filters - FAILED: {e}")
    
    try:
        test_builder.test_execute_query_groupby()
        print("✅ Test 4: Query with group by - PASSED")
    except Exception as e:
        print(f"❌ Test 4: Query with group by - FAILED: {e}")
    
    try:
        test_builder.test_execute_query_aggregates()
        print("✅ Test 5: Query with aggregates - PASSED")
    except Exception as e:
        print(f"❌ Test 5: Query with aggregates - FAILED: {e}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)
