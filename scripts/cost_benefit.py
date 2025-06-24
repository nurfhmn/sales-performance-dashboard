def cost_benefit_analysis(df):
    # ROI: Satış - Komisyon / Komisyon (eski metrik)
    

    # Yeni: Net Kâr = Satış - Komisyon - Maliyet
    if "TotalCost" in df.columns:
        df["NetProfit"] = df["SalesAmount"] - df["Commission"] - df["TotalCost"]
        df["ProfitMargin"] = df["NetProfit"] / df["SalesAmount"].replace(0, 1)
        df['ROI'] = df['NetProfit']  / (df["Commission"] + df["TotalCost"]).replace(0, 1)
    else:
        df["NetProfit"] = None
        df["ProfitMargin"] = None
        df['ROI'] = None

    return df