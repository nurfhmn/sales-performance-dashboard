def calculate_market_share(df, market_df):
    merged = df.merge(market_df, on='LoB')
    merged['MarketShare'] = merged['SalesAmount'] / merged['TotalMarketSales']
    return merged
