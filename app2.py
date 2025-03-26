import streamlit as st
import pandas as pd
import plotly.express as px

# Tải dữ liệu từ file Excel
@st.cache_data
def load_data(file):
    xls = pd.ExcelFile(file)
    df = pd.read_excel(xls, sheet_name="orders")
    return df

st.set_page_config(page_title="Phân tích Shopee", layout="wide")
st.title("📊 Phân tích & Báo cáo Shopee")

# Upload file
uploaded_file = st.file_uploader("Tải lên file Excel đơn hàng", type=["xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)
    st.success("Dữ liệu đã được tải lên thành công!")
    
    # Bộ lọc thông minh
    st.sidebar.header("🔍 Bộ lọc")
    date_range = st.sidebar.date_input("📅 Chọn khoảng thời gian", [])
    status_filter = st.sidebar.multiselect("📌 Trạng thái đơn hàng", df["Trạng Thái Đơn Hàng"].unique())
    
    # Áp dụng bộ lọc
    if date_range:
        df = df[(df["Ngày đặt hàng"] >= str(date_range[0])) & (df["Ngày đặt hàng"] <= str(date_range[-1]))]
    if status_filter:
        df = df[df["Trạng Thái Đơn Hàng"].isin(status_filter)]
    
    # Biểu đồ doanh thu theo ngày
    st.subheader("📈 Doanh thu theo ngày")
    revenue_chart = px.line(df, x="Ngày đặt hàng", y="Tổng giá trị đơn hàng (VND)", title="Biểu đồ doanh thu")
    st.plotly_chart(revenue_chart)
    
    # Top sản phẩm bán chạy
    st.subheader("🔥 Sản phẩm bán chạy")
    top_products = df.groupby("Tên sản phẩm")["Số lượng"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_products)
    
    # Thống kê chi phí
    st.subheader("💰 Thống kê chi phí")
    cost_chart = px.pie(df, values="Phí vận chuyển (dự kiến)", names="Tên sản phẩm", title="Tỷ lệ chi phí vận chuyển")
    st.plotly_chart(cost_chart)
    
    # Hiển thị dữ liệu chi tiết
    st.subheader("📋 Dữ liệu đơn hàng")
    st.dataframe(df)
