import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# menyiapkan dataframe

def create_sum_order_items_df(df):
    sum_order_items_df = all_df.groupby("product_category_name").order_item_id.sum().sort_values(ascending=False).reset_index()
    return create_sum_order_items_df
    
def create_aggregated_data_df(df):
    aggregated_data = all_df.groupby(by=["review_score"]).agg({
        "review_score": "sum"
    })
    return create_aggregated_data_df

def create_sum_customer_city_df(df):
    sum_customer_city = all_df.groupby("customer_city").customer_id.nunique().sort_values(ascending=False)
    return create_sum_customer_city_df
    
def create_rfm_df(df):
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp_y": "max", 
        "order_id_x": "nunique", 
        "price": "sum" 
    })
    
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
 
    rfm_df = rfm_df.dropna(subset=["max_order_timestamp"])
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"])
    
    recent_date = all_df["order_purchase_timestamp_y"].max().date()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x.date()).days)
    
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return create_rfm_df
    

url = "https://drive.google.com/uc?export=download&id=1ch0rbg7aOm-F1gnEaoRoZlBRcCsWgTEY"
all_df = pd.read_csv(url)

# kunci pembuatan filter

datetime_columns = ["order_purchase_timestamp_y", "order_delivered_customer_date_y"]
all_df.sort_values(by="order_purchase_timestamp_y", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
# membuat komponen filter

min_date = all_df["order_purchase_timestamp_y"].min()
max_date = all_df["order_purchase_timestamp_y"].max()
 
with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = all_df[(all_df["order_purchase_timestamp_y"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp_y"] <= str(end_date))]
                
                
    
    
sum_order_items_df = create_sum_order_items_df(main_df)
aggregated_data_df = create_aggregated_data_df(main_df)
sum_customer_city = create_sum_customer_city_df(main_df)
rfm_df = create_rfm_df(main_df)

# melengkapi dashboard dengan visualisasi data
st.header('Brazilian E-Commerce: ')

# menampilkan bagian top product category name 
st.subheader('Top Product Category Name')
 
col1, col2 = st.columns(2)

name_product = all_df.groupby('product_category_name').order_item_id.sum().idxmax()
total_order = all_df.groupby('product_category_name').order_item_id.sum().max()
 
with col1:
    st.metric("Product Category Name", value=name_product)
 
with col2:
    st.metric("Total Order", value=total_order)
 
fig, ax = plt.subplots(figsize=(24, 6))
colors = ["#6A9C89", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3"]
 
sns.barplot(x="order_item_id", y="product_category_name", data=name_product_df.head(10), palette=colors)

ax.set_title("Top Product Category Name", loc="center", fontsize=30)
ax.tick_params(axis ='y', labelsize=15)
 

st.plypot(fig)
    
