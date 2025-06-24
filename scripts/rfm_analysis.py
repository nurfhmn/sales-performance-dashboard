import pandas as pd
def safe_qcut(series, q=5, ascending=True):
    try:
        bins = pd.qcut(series, q=q, duplicates='drop')
        bin_count = bins.cat.categories.size
        labels = list(range(1, bin_count + 1))
        if not ascending:
            labels = labels[::-1]
        return pd.qcut(series, q=bin_count, labels=labels, duplicates='drop').astype(int)
    except ValueError:
        return pd.Series([3] * len(series))
def calculate_rfm(df, reference_date=None):
    df["Date"] = pd.to_datetime(df["Date"])

    if reference_date is None:
        reference_date = df["Date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg({
        "Date": lambda x: (reference_date - x.max()).days,
        "SalesQty": "count",
        "SalesAmount": "sum"
    }).reset_index()



    rfm.columns = ["Customer", "Recency", "Frequency", "Monetary"]

    # Skorlar
    rfm["R_Score"] = safe_qcut(rfm["Recency"], q=5, ascending=False)
    rfm["F_Score"] = safe_qcut(rfm["Frequency"], q=5, ascending=True)
    rfm["M_Score"] = safe_qcut(rfm["Monetary"], q=5, ascending=True)


    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

    # Segment etiketleri
    def segment(row):
        try: 
            r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
            if pd.isnull(r) or pd.isnull(f) or pd.isnull(m):
                return "Unknown"
            if r >= 4 and f >= 4 and m >= 4:
                return "Loyal"
            elif r >= 4 and f <= 2:
                return "New"
            elif r <= 2 and f >= 4:
                return "Risky But Frequent Shoppers"
            elif r <= 2 and f <= 2:
                return "Lost"
            elif m >= 4:
                return "High Value"
            else:
                return "Standard"
        except:
            return "Unknown"
    rfm["Segment"] = rfm.apply(segment, axis=1)

    return rfm

