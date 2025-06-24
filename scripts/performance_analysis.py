def analyze_sales_performance(df):
    grouped = df.groupby(['LoB', 'Product', 'CustomerSegment']).agg({
        'SalesAmount': 'sum',
        'SalesQty': 'sum'
    }).reset_index()
    return grouped

