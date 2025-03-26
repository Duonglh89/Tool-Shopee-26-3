import streamlit as st
import pandas as pd
import plotly.express as px

# Load file Excel
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace("\\n", " ").str.replace("\\s+", " ", regex=True)
    return df

st.set_page_config(layout="wide", page_title="Phân tích Shopee", page_icon="📊")
st.title("📊 Phân tích & Báo cáo Shopee")
st.markdown("<style>body { background-color: #f0f8ff; }</style>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### 🛒 Dữ liệu đơn hàng:")
    st.dataframe(df, height=400, use_container_width=True)
    
    # Kiểm tra và xử lý cột thời gian
    time_column = next((col for col in df.columns if "Thời gian tạo đơn" in col), None)
    if time_column:
        df[time_column] = pd.to_datetime(df[time_column], errors="coerce")
    
    # Sidebar bộ lọc
    st.sidebar.header("🔎 Bộ lọc dữ liệu")
    selected_status = st.sidebar.multiselect("📌 Trạng thái đơn hàng", sorted(df["Trạng Thái Đơn Hàng"].dropna().unique()))
    selected_products = st.sidebar.multiselect("📦 Tên sản phẩm", sorted(df["Tên sản phẩm"].dropna().unique()))
    
    if time_column:
        selected_time = st.sidebar.date_input("📅 Chọn thời gian tạo đơn", [df[time_column].min(), df[time_column].max()])
        df_filtered = df[(df["Trạng Thái Đơn Hàng"].isin(selected_status)) & (df["Tên sản phẩm"].isin(selected_products)) & (df[time_column].between(pd.Timestamp(selected_time[0]), pd.Timestamp(selected_time[1])))]
    else:
        df_filtered = df[(df["Trạng Thái Đơn Hàng"].isin(selected_status)) & (df["Tên sản phẩm"].isin(selected_products))]
    
    # Xác định cột doanh thu & chi phí
    revenue_column = next((col for col in df_filtered.columns if "Doanh thu" in col), None)
    cost_column = next((col for col in df_filtered.columns if "Chi phí Kinh Doanh" in col), None)
    fee_column = next((col for col in df_filtered.columns if "Phí sàn" in col), None)
    
    # Tổng hợp doanh thu & chi phí
    st.write("### 📈 Tổng hợp Doanh thu & Chi phí")
    total_revenue = df_filtered[revenue_column].sum() if revenue_column else 0
    total_cost = df_filtered[cost_column].sum() if cost_column else 0
    total_fee = df_filtered[fee_column].sum() if fee_column else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="💰 Tổng Doanh thu", value=f"{total_revenue:,.0f} VNĐ")
    col2.metric(label="📉 Tổng Chi phí Kinh Doanh", value=f"{total_cost:,.0f} VNĐ")
    col3.metric(label="💸 Tổng Phí sàn", value=f"{total_fee:,.0f} VNĐ")
    
    # Phân tích theo sản phẩm
    st.write("### 📊 Phân tích theo sản phẩm")
    if revenue_column:
        product_sales = df_filtered.groupby("Tên sản phẩm")[revenue_column].sum().reset_index()
        fig = px.bar(product_sales, x="Tên sản phẩm", y=revenue_column, title="📊 Doanh thu theo sản phẩm", text_auto=True, color=revenue_column, color_continuous_scale="blues")
        st.plotly_chart(fig, use_container_width=True)
    
    # Xử lý lỗi tên cột phí vận chuyển
    shipping_column = next((col for col in df_filtered.columns if "Phí vận chuyển" in col), None)
    if shipping_column:
        df_filtered[shipping_column] = pd.to_numeric(df_filtered[shipping_column], errors="coerce")
    
    # Biểu đồ chi phí vận chuyển
    st.write("### 🚚 Tỷ lệ Chi phí Vận Chuyển")
    if shipping_column and df_filtered[shipping_column].notnull().sum() > 0:
        cost_chart = px.pie(df_filtered, values=shipping_column, names="Tên sản phẩm", title="🚚 Tỷ lệ chi phí vận chuyển", color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(cost_chart, use_container_width=True)
    else:
        st.write("Không có dữ liệu vận chuyển hợp lệ.")
    
    # Xuất báo cáo
    st.write("### 📤 Xuất báo cáo")
    st.download_button("📥 Tải về Excel", data=df_filtered.to_csv(index=False).encode("utf-8"), file_name="bao_cao_shopee.csv", mime="text/csv")
