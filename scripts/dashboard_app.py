import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import streamlit as st
import os

from rfm_analysis import calculate_rfm
from data_loader import load_sales_data, load_budget_data
from performance_analysis import analyze_sales_performance
from incentive_model import calculate_commissions
from cost_benefit import cost_benefit_analysis
from regression_model import train_compare_models
from benchmark_analysis import calculate_market_share


# Başlık
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
st.title("📊 Sales Performance Dashboard")


st.markdown(
    "<div style='position: absolute; top: 20px; right: 30px; color: gray;'>by Fehime Nur Göbeller | 2025</div>",
    unsafe_allow_html=True
)

# Veri yükleme
sales_df = load_sales_data(r"...\data\sales_data.csv")
budget_df = load_budget_data(r"...\data\budget_data.csv")

# Tarih sütununu datetime formatına çevir
sales_df["Date"] = pd.to_datetime(sales_df["Date"])

# Kâr hesaplaması
if "TotalCost" in sales_df.columns:
    sales_df["Profit"] = sales_df["SalesAmount"] - sales_df["TotalCost"]
else:
    sales_df["Profit"] = 0

# Sekmelerle görünüm bölme
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["🔍 General", "📈 Visualization", "📊 Budget & Segment Analysis" ,"🛒 Market Share" ,"💰 Incentives & Commission",
    "📈 Cost/Benefit", "💼 Profit", "🆚 Regression Model Compare", "📂 Customer Segmentation"])

with tab1:
    st.subheader("Product, LoB and Segment Based Performance")
    performance = analyze_sales_performance(sales_df)
    st.dataframe(performance)

    st.subheader("Total Sales Amount (General)")
    st.metric(label="Total Sales ($)", value=f"{sales_df['SalesAmount'].sum():,.0f}")

with tab2:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Sales Amount by Channel")
        channel_sales = sales_df.groupby("Channel")["SalesAmount"].sum().sort_values()
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        channel_sales.plot(kind="barh", ax=ax1)
        ax1.set_xlabel("Sales Amount")
        ax1.set_ylabel("Channel")
        st.pyplot(fig1,use_container_width=False)
    with col2:
        st.subheader("🕒 Sales Trends (Daily / Monthly / Annuanly)")

        # Buton seçenekleri
        col1, col2, col3 = st.columns(3)
        trend_type = "daily"  # default

        with col1:
            if st.button("Daily Trend"):
                trend_type = "daily"
        with col2:
            if st.button("Monthly Trend"):
                trend_type = "monthly"
        with col3:
            if st.button("Annually Trend"):
                trend_type = "yearly"

        # Grup anahtarı belirle
        if trend_type == "daily":
            trend_data = sales_df.groupby("Date")["SalesAmount"].sum()
            x_label = "Date (Daily)"
        elif trend_type == "monthly":
            trend_data = sales_df.groupby(sales_df["Date"].dt.to_period("M"))["SalesAmount"].sum()
            trend_data.index = trend_data.index.to_timestamp()
            x_label = "Date (Monthly)"
        else:
            trend_data = sales_df.groupby(sales_df["Date"].dt.to_period("Y"))["SalesAmount"].sum()
            trend_data.index = trend_data.index.to_timestamp()
            x_label = "Date (Annually)"

        # En yüksek ve en düşük noktalar
        max_date = trend_data.idxmax()
        min_date = trend_data.idxmin()
        max_value = trend_data.max()
        min_value = trend_data.min()

        # Grafik çizimi
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        trend_data.plot(marker='*', linestyle='-', color='mediumvioletred', ax=ax2)

        # Etiketler
        ax2.annotate(f"High\n{max_value:,.0f}$", xy=(max_date, max_value),
             xytext=(max_date, max_value + max_value*0.05),
             arrowprops=dict(arrowstyle="->", color="green"),
             ha='center', color="green", fontsize=9)

        ax2.annotate(f"Low\n{min_value:,.0f}$", xy=(min_date, min_value),
             xytext=(min_date, min_value - min_value*0.1),
             arrowprops=dict(arrowstyle="->", color="red"),
             ha='center', color="red", fontsize=9)

        # Eksen başlıkları
        ax2.set_title("Sales Trend")
        ax2.set_xlabel(x_label)
        ax2.set_ylabel("Sales Amount ($)")

        st.pyplot(fig2, use_container_width=False)


with tab3:
    st.subheader("Budget Comparison - LoB & Channel ")
    merged = sales_df.groupby(["LoB", "Channel"])["SalesAmount"].sum().reset_index()
    comparison = pd.merge(merged, budget_df, on=["LoB", "Channel"], how="left")
    comparison["GerçekleşmeOranı"] = comparison["SalesAmount"] / comparison["BudgetAmount"]
    st.dataframe(comparison)

    st.subheader("Average Sales by Cutomer Segment")
    fig3, ax3 = plt.subplots(figsize=(4, 4))
    sns.barplot(data=sales_df, x="CustomerSegment", y="SalesAmount", estimator="mean", ax=ax3, color='r')
    ax3.set_ylabel("Average Sales")
    st.pyplot(fig3,use_container_width=False)

with tab9:
    col1, col2 = st.columns([1,1])
    st.subheader("📂 Customer Segmentation - RFM ")

    rfm_df = calculate_rfm(sales_df)

    st.dataframe(rfm_df)
    with col1:
        st.markdown("### Segments by RFM Score")

    # Basit segment analizi
        segment_counts = rfm_df["RFM_Score"].value_counts().reset_index()
        cust_counts = rfm_df.groupby("Segment")["Customer"].nunique().reset_index()
        cust_counts.columns = ["Segment", "Müşteri Sayısı"]
        segment_counts.columns = ["RFM_Score", "Müşteri Sayısı"]
        st.dataframe(segment_counts)


    # Görsel
    segment_colors = {
    "Loyal": "green",
    "New": "dodgerblue",
    "Risky But Frequent Shoppers": "orange",
    "Lost": "red",
    "High Value": "purple",
    "Standard": "gray",
    "Unknown": "lightgray"
}

    # Renk listesini veriye göre oluştur
    colors = cust_counts["Segment"].map(segment_colors)


    with col2:
        fig_seg, ax_seg = plt.subplots(figsize=(6, 3))
        bars = ax_seg.bar(
        x=cust_counts["Segment"],
        height=cust_counts["Müşteri Sayısı"],
        color=colors
        )

    
        ax_seg.set_ylabel("Num of Customer")
        ax_seg.set_title("Customer Segments")
        ax_seg.set_xticklabels(cust_counts["Segment"], rotation=45, ha="right")

        for p in ax_seg.patches:
            value = int(p.get_height())
            ax_seg.text(
                x=p.get_x() + p.get_width() / 2,
                y=p.get_height() + 0.5,
                s=str(value),
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )
    
        st.pyplot(fig_seg, use_container_width=False)

with tab5:
    st.subheader("💰 Incentive and Commission")
    commission_model = {"rate": 0.05, "threshold": 10000}
    commission_df = calculate_commissions(sales_df.copy(), commission_model)

    # 🔍 Sadece komisyonu > 0 olanlar
    commission_df = commission_df[commission_df["Commission"] > 0]

    # 🔽 Komisyona göre büyükten küçüğe sırala
    commission_df = commission_df.sort_values(by="Commission", ascending=False)

    # 🎯 Toplam komisyon metriği
    st.metric("Total Commission ($)", value=f"{commission_df['Commission'].sum():,.0f}")

    # 📋 İlk 20 kaydı göster
    #st.dataframe(commission_df[["CustomerID", "SalesAmount", "Commission"]].head(20))
    
    # 🔎 CustomerID filtreleme alanı
    customer_filter = st.text_input("🔍 Filter by CustomerID (exp: C001)", value="")

    if customer_filter:
        commission_df = commission_df[commission_df["CustomerID"].str.contains(customer_filter.strip(), case=False)]

    # 🎯 Metriği göster
    st.metric("Total Commission ($)", value=f"{commission_df['Commission'].sum():,.0f}")

    # 📋 İlk 20 kaydı göster
    st.dataframe(commission_df[["CustomerID", "SalesAmount", "Commission"]].head(20))

with tab6:
    col1, col2 = st.columns([1, 2])
    
    
    cb_df = calculate_commissions(sales_df.copy(), commission_model)
    cb_df = cost_benefit_analysis(cb_df).sort_values(by='ROI',ascending=False)
    
    with col2:
        st.subheader("📈 Cost / Benefit (ROI) Analysis")
        st.metric("Average ROI", value=f"{cb_df['ROI'].mean():,.0f}")
        st.subheader("📈 Cost / Benefit (ROI) Analysis")

        st.dataframe(cb_df[["CustomerID", "SalesAmount","TotalCost", "Commission", "ROI"]].head(20))
    with col1:
        fig_cb, ax_cb = plt.subplots(figsize=(5,4))
        cb_df.plot.scatter(x="SalesAmount", y="ROI", ax=ax_cb, alpha=0.6)
        ax_cb.set_title("Sales Amount vs. ROI")
        st.pyplot(fig_cb, use_container_width=False)


with tab7:
    st.subheader("💼 Profit Analysis - Sales Amount vs. Cost vs. Profit")
    profit_df = sales_df.copy()

    profit_df["Date"] = pd.to_datetime(profit_df["Date"]) 
    profit_df["Month"] = profit_df["Date"].dt.to_period("M").dt.to_timestamp()

    # 🎯 Toplam Profit metriği
    st.metric("Total Profit ($)", value=f"{profit_df['Profit'].sum():,.0f}")

    st.dataframe(profit_df[["CustomerID", "SalesAmount", "TotalCost", "Profit"]].head(20))

    monthly_profit = profit_df.groupby("Month")["Profit"].sum()

    fig_profit, ax_profit = plt.subplots(figsize=(4,4))
    monthly_profit.plot(ax=ax_profit, marker="o", color="seagreen")
    
    ax_profit.set_title("Monthly Profit")
    ax_profit.set_ylabel("$")
    st.pyplot(fig_profit, use_container_width=False)

with tab8:
    st.subheader("Appropriate model selection is included in the planned updates.")
    with st.expander("🔍 Regression Models Comparison"):
        if st.button("Start Model Comparison"):
            with st.spinner("Models training..."):
                results = train_compare_models()
            st.success("Comparison completed!")

            st.image("regression_comparison.png", caption="Model Comparion Chart")

            for model, r2 in results:
                st.write(f"**{model}** → R²: `{r2:.2f}` ")

with tab4:
    col1,col2 = st.columns([1, 1])
    

    # Veriler
    sales_df["Date"] = pd.to_datetime(sales_df["Date"])
    market_df = pd.read_csv(rf"...\data\market_share_data.csv")

    # LoB bazında toplam satışlar
    lob_sales = sales_df.groupby("LoB")["SalesAmount"].sum().reset_index()

    # Pazar payı hesapla
    market_share_df = calculate_market_share(lob_sales, market_df)

    # Yüzdelik formatta gösterim
    market_share_df["MarketSharePercent"] = market_share_df["MarketShare"] * 100
    with col2:
    # Tablo gösterimi
        st.dataframe(market_share_df[["LoB", "SalesAmount", "TotalMarketSales", "MarketSharePercent"]])
    with col1:
        st.subheader("📊 Benchmark & Market Share Analysis")
    # Grafik
        fig_bm, ax_bm = plt.subplots(figsize=(4, 4))
        ax_bm.bar(market_share_df["LoB"], market_share_df["MarketSharePercent"], color="mediumpurple")
        ax_bm.set_ylabel("Market Share (%)")
        ax_bm.set_title("Market Share by LoB")
        ax_bm.set_ylim(0, 100)
        for i, v in enumerate(market_share_df["MarketSharePercent"]):
            ax_bm.text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=9)
    
        st.pyplot(fig_bm, use_container_width=False)

# Footer
st.markdown("---")
st.caption("by Fehime Nur Göbeller | 2025")
