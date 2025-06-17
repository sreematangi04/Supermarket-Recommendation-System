# app.py

import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# ---------------------- APP CONFIG ----------------------
st.set_page_config(page_title="🛒 Supermarket Recommender", layout="wide")

# ---------------------- DATA LOADING ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Groceries_dataset.csv")
    basket = df.groupby(['Member_number', 'itemDescription'])['Date'].count().unstack().fillna(0)
    basket = basket.apply(lambda x: x > 0).astype(bool)
    return df, basket

df, basket = load_data()

# ---------------------- APRIORI + RULES ----------------------


# Generate frequent itemsets with min_support of 1%
frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)

# Generate all possible association rules with low threshold
rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.01)

# Filter rules to match support >= 0.023, confidence >= 0.5, lift >= 1.2
strong_rules = rules[
    (rules['support'] >= 0.023) &
    (rules['confidence'] >= 0.5) &
    (rules['lift'] >= 1.2)
].reset_index(drop=True)


# ---------------------- SIDEBAR UI ----------------------
st.sidebar.title("🛍️ Your Basket")
item_list = df['itemDescription'].unique().tolist()
selected_items = st.sidebar.multiselect("Select items you've bought", sorted(item_list))

# ---------------------- RECOMMENDER FUNCTION ----------------------
def get_recommendations(input_items):
    input_set = set(input_items)
    recommended = set()
    for _, row in strong_rules.iterrows():
        if input_set.issuperset(row['antecedents']):
            recommended.update(row['consequents'])
    return list(recommended - input_set)

# ---------------------- MAIN UI ----------------------
st.title("🛒 Supermarket Product Recommendation System")
st.markdown("Built using **Apriori Algorithm** and Market Basket Analysis.\n"
            "Select the items you've purchased and get recommendations based on frequent itemsets.")

if selected_items:
    recs = get_recommendations(selected_items)
    if recs:
        st.success("✅ Recommended Products Based on Your Basket:")
        st.write(recs)
    else:
        st.warning("No recommendations found for this combination.")
else:
    st.info("Please select items from the sidebar to see recommendations.")

# ---------------------- EXPANDERS ----------------------
with st.expander("📊 View Strong Association Rules"):
    st.dataframe(strong_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
