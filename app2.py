import streamlit as st
import pandas as pd
import plotly.express as px

# Load file Excel
def load_data(file):
    df = pd.read_excel(file)
    return df
if uploaded_file:
    df = load_data(uploaded_file)
    
    # Hiển thị danh sách cột để kiểm tra
    st.write("### Các cột trong file:", df.columns.tolist())
    
    # Kiểm tra cột 'Thời gian tạo đơn hàng' có tồn tại không
    if "Thời gian tạo đơn hàng" in df.columns:
        df["Thời gian tạo đơn hàng"] = pd.to_datetime(df["Thời gian tạo đơn hàng"], errors="coerce")
        
        # Kiểm tra có giá trị hợp lệ không
        if not df["Thời gian tạo đơn hàng"].isnull().all():
            selected_time = st.sidebar.date_input(
                "Chọn thời gian tạo đơn",
                [df["Thời gian tạo đơn hàng"].min().date(), df["Thời gian tạo đơn hàng"].max().date()]
            )
        else:
            st.sidebar.warning("Cột 'Thời gian tạo đơn hàng' không có dữ liệu hợp lệ.")
    else:
        st.sidebar.error("Cột 'Thời gian tạo đơn hàng' không tồn tại trong file Excel.")

# Đảm bảo cột 'Thời gian tạo đơn hàng' tồn tại và không rỗng
if "Thời gian tạo đơn hàng" in df.columns and not df["Thời gian tạo đơn hàng"].isnull().all():
    # Chuyển đổi sang datetime
    df["Thời gian tạo đơn hàng"] = pd.to_datetime(df["Thời gian tạo đơn hàng"], errors="coerce")
    
    # Loại bỏ giá trị NaT (nếu có)
    df = df.dropna(subset=["Thời gian tạo đơn hàng"])

    # Kiểm tra lại nếu dữ liệu vẫn còn
    if not df.empty:
        selected_time = st.sidebar.date_input(
            "Chọn thời gian tạo đơn",
            [df["Thời gian tạo đơn hàng"].min().date(), df["Thời gian tạo đơn hàng"].max().date()]
        )
    else:
        st.sidebar.warning("Không có dữ liệu hợp lệ trong cột 'Thời gian tạo đơn hàng'.")
        selected_time = []
else:
    st.sidebar.error("Cột 'Thời gian tạo đơn hàng' không tồn tại hoặc toàn bộ dữ liệu bị lỗi.")
    selected_time = []

st.set_page_config(layout="wide")
st.title("Phân tích & Báo cáo Shopee")

uploaded_file = st.file_uploader("Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Dữ liệu đơn hàng:")
    st.dataframe(df)
    
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
    
    # Xuất báo cáo
    st.write("### Xuất báo cáo")
    st.download_button("Tải về Excel", data=df_filtered.to_csv(index=False).encode("utf-8"), file_name="bao_cao_shopee.csv", mime="text/csv")
