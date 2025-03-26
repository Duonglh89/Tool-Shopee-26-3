import streamlit as st
import pandas as pd
import plotly.express as px

# Load file Excel
def load_data(file):
    df = pd.read_excel(file)
    df.rename(columns=lambda x: x.strip(), inplace=True)  # Xóa khoảng trắng ở tên cột
    return df

st.set_page_config(layout="wide")
st.title("Phân tích & Báo cáo Shopee")

uploaded_file = st.file_uploader("Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Dữ liệu đơn hàng:")
    st.dataframe(df)
    
    # Kiểm tra và xử lý cột thời gian
    if "Thời gian tạo đơn hàng" in df.columns and not df["Thời gian tạo đơn hàng"].isnull().all():
        df["Thời gian tạo đơn hàng"] = pd.to_datetime(df["Thời gian tạo đơn hàng"], errors="coerce")
    
    # Bộ lọc thông minh
    st.sidebar.header("Bộ lọc dữ liệu")
    selected_status = st.sidebar.multiselect("Trạng thái đơn hàng", df["Trạng Thái Đơn Hàng"].unique(), default=df["Trạng Thái Đơn Hàng"].unique())
    selected_time = st.sidebar.date_input("Chọn thời gian tạo đơn", [df["Thời gian tạo đơn hàng"].min(), df["Thời gian tạo đơn hàng"].max()])
    df_filtered = df[(df["Trạng Thái Đơn Hàng"].isin(selected_status)) & (df["Thời gian tạo đơn hàng"].between(pd.Timestamp(selected_time[0]), pd.Timestamp(selected_time[1])))]
    
    # Tổng hợp doanh thu & chi phí
    st.write("### Tổng hợp Doanh thu & Chi phí")
    total_revenue = df_filtered["Doanh thu"].sum()
    total_cost = df_filtered["Chi phí Kinh Doanh"].sum()
    total_fee = df_filtered["Phí sàn"].sum()
    st.metric(label="Tổng Doanh thu", value=f"{total_revenue:,.0f} VNĐ")
    st.metric(label="Tổng Chi phí Kinh Doanh", value=f"{total_cost:,.0f} VNĐ")
    st.metric(label="Tổng Phí sàn", value=f"{total_fee:,.0f} VNĐ")
    
    # Phân tích theo sản phẩm
    st.write("### Phân tích theo sản phẩm")
    product_sales = df_filtered.groupby("Tên sản phẩm")["Doanh thu"].sum().reset_index()
    fig = px.bar(product_sales, x="Tên sản phẩm", y="Doanh thu", title="Doanh thu theo sản phẩm", text_auto=True)
    st.plotly_chart(fig)
    
    # Xử lý lỗi tên cột phí vận chuyển
    df_filtered.rename(columns={"Phí vận chuyển (dự kiến)": "Phí vận chuyển"}, inplace=True)
    df_filtered["Phí vận chuyển"] = pd.to_numeric(df_filtered["Phí vận chuyển"], errors="coerce")
    
    # Biểu đồ chi phí vận chuyển
    st.write("### Tỷ lệ Chi phí Vận Chuyển")
    if "Phí vận chuyển" in df_filtered.columns and df_filtered["Phí vận chuyển"].notnull().sum() > 0:
        cost_chart = px.pie(df_filtered, values="Phí vận chuyển", names="Tên sản phẩm", title="Tỷ lệ chi phí vận chuyển")
        st.plotly_chart(cost_chart)
    else:
        st.write("Không có dữ liệu vận chuyển hợp lệ.")
    
    # Xuất báo cáo
    st.write("### Xuất báo cáo")
    st.download_button("Tải về Excel", data=df_filtered.to_csv(index=False).encode("utf-8"), file_name="bao_cao_shopee.csv", mime="text/csv")
