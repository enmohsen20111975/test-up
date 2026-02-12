import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from analytics.query_builder import QueryBuilder

def test_query_builder():
    """Test QueryBuilder functionality directly"""
    print("Testing QueryBuilder functionality...")
    
    # Create test data
    test_data = [
        {"product": "Transformer", "quantity": 10, "price": 150.5, "region": "East"},
        {"product": "Battery", "quantity": 5, "price": 250.0, "region": "West"},
        {"product": "Inverter", "quantity": 8, "price": 180.75, "region": "North"},
        {"product": "Diary", "quantity": 15, "price": 25.5, "region": "South"},
        {"product": "Accessories", "quantity": 20, "price": 45.25, "region": "East"}
    ]
    
    data_json = pd.DataFrame(test_data).to_json(orient='records')
    
    # Test 1: Get data summary
    print("\n1. Testing data summary retrieval...")
    try:
        result = QueryBuilder.get_data_summary(data_json)
        print("Success:", result['success'])
        print("   Row count:", result['summary']['row_count'])
        print("   Column count:", result['summary']['column_count'])
    except Exception as e:
        print("Error:", e)
        return False
    
    # Test 2: Get column distribution
    print("\n2. Testing column distribution...")
    try:
        result = QueryBuilder.get_column_distribution(data_json, 'price')
        print("Success:", result['success'])
        print("   Column:", result['distribution']['column'])
        print("   Min:", result['distribution']['min'])
        print("   Max:", result['distribution']['max'])
        print("   Range:", result['distribution']['range'])
        print("   Mean:", "{0:.2f}".format(result['distribution']['mean']))
    except Exception as e:
        print("Error:", e)
        return False
    
    # Test 3: Execute query with filters
    print("\n3. Testing query with filters...")
    try:
        query = {
            "filters": [{"column": "region", "operator": "equals", "value": "East"}]
        }
        result = QueryBuilder.execute_query(data_json, query)
        print("Success:", result['success'])
        
        import io
        results_df = pd.read_json(io.StringIO(result['results']), orient='records')
        print("   Results:", len(results_df))
    except Exception as e:
        print("Error:", e)
        return False
    
    # Test 4: Execute query with group by
    print("\n4. Testing query with group by...")
    try:
        query = {
            "group_by": "region",
            "aggregates": [{"column": "quantity", "type": "sum"}]
        }
        result = QueryBuilder.execute_query(data_json, query)
        print("Success:", result['success'])
        
        import io
        results_df = pd.read_json(io.StringIO(result['results']), orient='records')
        print("   Groups:", len(results_df))
    except Exception as e:
        print("Error:", e)
        return False
    
    print("\nAll tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_query_builder()
    sys.exit(0 if success else 1)
