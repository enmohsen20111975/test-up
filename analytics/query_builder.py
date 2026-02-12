import pandas as pd
import json
import numpy as np

class QueryBuilder:
    @staticmethod
    def execute_query(data: str, query: dict):
        """Execute advanced queries on uploaded data"""
        try:
            import io
            df = pd.read_json(io.StringIO(data), orient='records')
            
            # Process query with advanced functionality
            result = df.copy()
            
            # Filter operations
            if query.get('filters'):
                for filter in query['filters']:
                    col = filter.get('column')
                    operator = filter.get('operator')
                    value = filter.get('value')
                    
                    if col in result.columns:
                        # Convert value to appropriate type
                        try:
                            if pd.api.types.is_numeric_dtype(result[col]):
                                value = float(value)
                            elif pd.api.types.is_datetime64_dtype(result[col]):
                                value = pd.to_datetime(value)
                        except:
                            pass
                        
                        # Apply filter based on operator
                        if operator == 'equals':
                            result = result[result[col] == value]
                        elif operator == 'not_equals':
                            result = result[result[col] != value]
                        elif operator == 'greater_than':
                            result = result[result[col] > value]
                        elif operator == 'less_than':
                            result = result[result[col] < value]
                        elif operator == 'greater_equals':
                            result = result[result[col] >= value]
                        elif operator == 'less_equals':
                            result = result[result[col] <= value]
                        elif operator == 'contains':
                            result = result[result[col].astype(str).str.contains(value, case=False)]
                        elif operator == 'starts_with':
                            result = result[result[col].astype(str).str.startswith(value, na=False)]
                        elif operator == 'ends_with':
                            result = result[result[col].astype(str).str.endswith(value, na=False)]
                        elif operator == 'is_null':
                            result = result[result[col].isnull()]
                        elif operator == 'not_null':
                            result = result[result[col].notnull()]
            
            # Group by and aggregation
            if query.get('group_by') and query.get('aggregates'):
                group_cols = query['group_by']
                if isinstance(group_cols, str):
                    group_cols = [group_cols]
                
                # Process aggregates
                agg_dict = {}
                for agg in query['aggregates']:
                    col = agg.get('column')
                    agg_type = agg.get('type', 'sum')
                    
                    if col in result.columns:
                        if agg_type == 'sum':
                            agg_dict[col] = 'sum'
                        elif agg_type == 'avg':
                            agg_dict[col] = 'mean'
                        elif agg_type == 'count':
                            agg_dict[col] = 'count'
                        elif agg_type == 'min':
                            agg_dict[col] = 'min'
                        elif agg_type == 'max':
                            agg_dict[col] = 'max'
                        elif agg_type == 'count_distinct':
                            agg_dict[col] = 'nunique'
                        elif agg_type == 'median':
                            agg_dict[col] = 'median'
                        elif agg_type == 'std':
                            agg_dict[col] = 'std'
                        elif agg_type == 'var':
                            agg_dict[col] = 'var'
                
                if agg_dict:
                    result = result.groupby(group_cols).agg(agg_dict).reset_index()
            
            # Pivot Table functionality
            if query.get('pivot'):
                pivot_config = query['pivot']
                index = pivot_config.get('index')
                columns = pivot_config.get('columns')
                values = pivot_config.get('values')
                aggfunc = pivot_config.get('aggfunc', 'sum')
                
                if index and columns and values:
                    # Map aggfunc to pandas compatible names
                    agg_map = {
                        'sum': np.sum,
                        'avg': np.mean,
                        'mean': np.mean,
                        'count': 'count',
                        'min': np.min,
                        'max': np.max,
                        'median': np.median,
                        'std': np.std
                    }
                    func = agg_map.get(aggfunc.lower(), np.sum)
                    result = pd.pivot_table(result, index=index, columns=columns, values=values, aggfunc=func).reset_index()
            
            # Sorting
            if query.get('order_by'):
                order_cols = query['order_by']
                if isinstance(order_cols, str):
                    order_cols = [order_cols]
                
                ascending = query.get('ascending', True)
                if isinstance(ascending, bool):
                    ascending = [ascending] * len(order_cols)
                
                result = result.sort_values(by=order_cols, ascending=ascending)
            
            # Limit and offset
            if query.get('limit'):
                limit = int(query['limit'])
                offset = int(query.get('offset', 0))
                result = result.iloc[offset:offset+limit]
            
            # Calculated fields (safe arithmetic only)
            if query.get('calculated_fields'):
                for field in query['calculated_fields']:
                    field_name = field.get('name')
                    expression = field.get('expression')

                    try:
                        if expression and field_name:
                            calc_result = QueryBuilder._safe_eval_expression(result, expression)
                            if calc_result is not None:
                                result[field_name] = calc_result
                    except Exception as e:
                        print(f"Error evaluating expression {expression}: {e}")
            
            return {
                "results": result.to_json(orient='records'),
                "summary": {
                    "row_count": len(result),
                    "columns": list(result.columns),
                    "total_columns": len(result.columns),
                    "numeric_columns": list(result.select_dtypes(include=[np.number]).columns),
                    "categorical_columns": list(result.select_dtypes(include=['object', 'category']).columns),
                    "date_columns": list(result.select_dtypes(include=['datetime64']).columns)
                },
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def _safe_eval_expression(df, expression: str):
        """Safely evaluate arithmetic expressions using column references like [col_name].
        Only allows basic arithmetic: +, -, *, /, parentheses, and numeric literals."""
        import re

        # Extract column references [col_name]
        col_refs = re.findall(r'\[([^\]]+)\]', expression)

        # Validate all referenced columns exist
        for col_ref in col_refs:
            if col_ref not in df.columns:
                raise ValueError(f"Column '{col_ref}' not found in data")

        # Only allow: column references, numbers, arithmetic operators, parentheses, spaces
        sanitized = re.sub(r'\[[^\]]+\]', '0', expression)  # Replace col refs with 0 for validation
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.\,]+$', sanitized.strip()):
            raise ValueError(f"Expression contains disallowed characters: {expression}")

        # Build the result using pandas operations
        result = None
        try:
            # Replace column references with actual series
            calc_expr = expression
            for col_ref in set(col_refs):
                calc_expr = calc_expr.replace(f'[{col_ref}]', f'__df__["{col_ref}"]')

            # Use numexpr via pandas eval for safe evaluation
            result = df.eval(calc_expr.replace('__df__["', '`').replace('"]', '`'))
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression: {e}")

        return result

    @staticmethod
    def get_data_summary(data: str):
        """Get comprehensive data summary statistics"""
        try:
            import io
            df = pd.read_json(io.StringIO(data), orient='records')
            
            summary = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": [],
                "numeric_summary": {},
                "categorical_summary": {}
            }
            
            for col in df.columns:
                col_summary = {
                    "name": col,
                    "type": str(df[col].dtype),
                    "null_count": int(df[col].isnull().sum()),
                    "unique_count": int(df[col].nunique())
                }
                
                # Numeric column statistics
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_summary["min"] = float(df[col].min()) if not pd.isnull(df[col].min()) else None
                    col_summary["max"] = float(df[col].max()) if not pd.isnull(df[col].max()) else None
                    col_summary["mean"] = float(df[col].mean()) if not pd.isnull(df[col].mean()) else None
                    col_summary["median"] = float(df[col].median()) if not pd.isnull(df[col].median()) else None
                    col_summary["std"] = float(df[col].std()) if not pd.isnull(df[col].std()) else None
                    col_summary["sum"] = float(df[col].sum()) if not pd.isnull(df[col].sum()) else None
                
                summary["columns"].append(col_summary)
            
            return {
                "summary": summary,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def get_column_distribution(data: str, column: str, bins: int = 10):
        """Get distribution statistics for a specific column"""
        try:
            import io
            df = pd.read_json(io.StringIO(data), orient='records')
            
            if column not in df.columns:
                return {"error": f"Column '{column}' not found", "success": False}
            
            col = df[column].dropna()
            
            distribution = {
                "column": column,
                "data_type": str(df[column].dtype),
                "non_null_count": len(col),
                "null_count": int(df[column].isnull().sum())
            }
            
            if pd.api.types.is_numeric_dtype(df[column]):
                # Numeric column distribution
                distribution["min"] = float(col.min())
                distribution["max"] = float(col.max())
                distribution["range"] = float(col.max() - col.min())
                distribution["mean"] = float(col.mean())
                distribution["median"] = float(col.median())
                distribution["std"] = float(col.std())
                
                # Create histogram bins
                hist, bin_edges = np.histogram(col, bins=bins)
                distribution["histogram"] = {
                    "bins": bin_edges.tolist(),
                    "counts": hist.tolist()
                }
            elif pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_categorical_dtype(df[column]):
                # Categorical column distribution
                value_counts = col.value_counts().head(20)  # Limit to top 20 values
                distribution["value_counts"] = {
                    "values": value_counts.index.tolist(),
                    "counts": value_counts.values.tolist()
                }
            elif pd.api.types.is_datetime64_dtype(df[column]):
                # Date column distribution
                distribution["min_date"] = col.min().isoformat()
                distribution["max_date"] = col.max().isoformat()
                
                # Monthly distribution
                monthly_counts = col.groupby(col.dt.to_period('M')).count()
                distribution["monthly_counts"] = {
                    "months": monthly_counts.index.astype(str).tolist(),
                    "counts": monthly_counts.values.tolist()
                }
            
            return {
                "distribution": distribution,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
