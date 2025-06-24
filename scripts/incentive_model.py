def calculate_commissions(df, commission_model):
    df['Commission'] = df['SalesAmount'].apply(lambda x: x * commission_model.get('rate') if x > commission_model.get('threshold') else 0)
    return df

