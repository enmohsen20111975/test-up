import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from analytics.query_builder import QueryBuilder

def debug_test():
    test_data = [
        {"product": "Transformer", "quantity": 10, "price": 150.5, "region": "East"},
        {"product": "Battery", "quantity": 5, "price": 250.0, "region": "West"},
        {"product": "Inverter", "quantity": 8, "price": 180.75, "region": "North"},
        {"product": "Diary", "quantity": 15, "price": 25.5, "region": "South"},
        {"product": "Accessories", "quantity": 20, "price": 45.25, "region": "East"}
    ]
    
    data_json = pd.DataFrame(test_data).to_json(orient='records')
    
    print("Data JSON:", data_json)
    
    try:
        result = QueryBuilder.get_data_summary(data_json)
        print("Result:", result)
        
        if result['success']:
            print("Summary keys:", list(result['summary'].keys()))
            print("Row count:", result['summary']['row_count'])
        else:
            print("Error:", result['error'])
            
    except Exception as e:
        print("Exception type:", type(e).__name__)
        print("Exception:", e)
        import traceback
        print("Stack trace:", traceback.format_exc())

if __name__ == "__main__":
    debug_test()
