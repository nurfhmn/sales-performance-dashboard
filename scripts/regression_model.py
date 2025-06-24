import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import root_mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os

def train_compare_models(data_path=rf"...\data\sales_data.csv", plot_output="regression_comparison.png"):
    # Veri yükleme
    df = pd.read_csv(data_path, parse_dates=["Date"])
    
    
    df["Day"] = df["Date"].dt.day
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year

    X = df[["LoB", "Channel", "Product","SalesQty", "CustomerSegment", "Day", "Month", "Year"]]
    y = df["SalesAmount"]

    cat_features = ["LoB", "Channel", "Product", "CustomerSegment"]

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown='ignore'), cat_features)
    ], remainder='passthrough')

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    }

    results = []

    for name, model in models.items():
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        #rmse = root_mean_squared_error(y_test, y_pred, squared=False)
        results.append((name, r2))

    # 📊 Görsel
    model_names = [r[0] for r in results]
    r2_scores = [r[1] for r in results]
    #rmse_scores = [r[2] for r in results]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(model_names, r2_scores, label="R² Skoru", color="royalblue")
    ax1.set_ylabel("R² Skoru", color="royalblue")
    ax1.set_ylim(0, 1)

    #ax2 = ax1.twinx()
    #ax2.plot(model_names, rmse_scores, label="RMSE", color="darkred", marker="o")
    #ax2.set_ylabel("RMSE", color="darkred")

    plt.title("Model Performance Comparison")
    plt.tight_layout()
    plt.savefig(plot_output)
    print(f"İmage Created: {plot_output}")

    return results
