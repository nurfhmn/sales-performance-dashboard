import pandas as pd
import json


def load_sales_data(path):
    return pd.read_csv(path)

def load_budget_data(path):
    return pd.read_csv(path)

def load_market_share_data(path):
    return pd.read_csv(path)

def load_commission_models(path):
    with open(path, 'r') as f:
        return json.load(f)