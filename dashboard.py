import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# menyiapkan dataframe

def create_sum_order_items_df(df):
    sum_order_items_df = all_df.groupby("product_category_name").order_item_id.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df
    
def create_aggregated_data_df(df):
    aggregated_data_df = all_df.groupby(by=["review_score"]).agg({
        "review_score": "sum"
    })
    return aggregated_data_df

def create_sum_customer_city_df(df):
    sum_customer_city_df = all_df.groupby("customer_city").customer_id.nunique().sort_values(ascending=False)
    return sum_customer_city_df
    
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
    
    return rfm_df
    

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
sum_customer_city_df = create_sum_customer_city_df(main_df)
rfm_df = create_rfm_df(main_df)

# melengkapi dashboard dengan visualisasi data
# menampilkan judul
css = """
<style>
    .custom-header {
        color: #6A9C89; 
        background-color: #F5E8B7; 
        padding: 10px; 
        border-radius: 5px; 
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.markdown('<h1 class="custom-header">Brazilian E-Commerce</h1>', unsafe_allow_html=True)

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
 
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.head(10), hue="product_category_name", palette=colors, legend=False)

ax.set_title("Top Product Category Name", loc="center", fontsize=30)
ax.tick_params(axis ='y', labelsize=15)
 

st.pyplot(fig)

# menampilkan bagian review score customer 
st.subheader("Customer Score Percentage")
labels = aggregated_data_df.index
sizes = aggregated_data_df["review_score"]

colors = ["#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#6A9C89"]
explode = (0, 0, 0, 0, 0.1)

fig, ax = plt.subplots(figsize=(8, 8))
fig.set_size_inches(8, 8)
ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, explode=explode)
ax.set_title('Customers Score Percentage')

ax.set_aspect('equal')

st.pyplot(fig)

# menampilkan bagian top cities transaction
st.subheader('Top Cities Transaction')
 
col1, col2 = st.columns(2)

name_city = all_df.groupby('customer_city').customer_id.nunique().idxmax()
order_total = sum_customer_city_df.max()
 
with col1:
    st.metric("Top City", value=name_city)
 
with col2:
    st.metric("Total Order", value=order_total)
 
fig, ax = plt.subplots(figsize=(24, 6))
colors = ["#6A9C89", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3", "#C1D8C3"]

sns.barplot(x=sum_customer_city_df.index[:10], y=sum_customer_city_df.head(10), palette=colors)


ax.set_title("Top Cities Transaction", loc="center", fontsize=15)
ax.tick_params(axis ='y', labelsize=12)

st.pyplot(fig)

# menampilkan rfm analysis
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#6A9C89", "#6A9C89", "#6A9C89", "#6A9C89", "#6A9C89"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
