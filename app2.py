import streamlit as st
import pandas as pd
import plotly.express as px

# Load file Excel
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace("\\n", " ").str.replace("\\s+", " ", regex=True)
    return df

st.set_page_config(layout="wide")
st.title("Phân tích & Báo cáo Shopee")

uploaded_file = st.file_uploader("Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Dữ liệu đơn hàng:")
    st.dataframe(df)
    
    # Kiểm tra và xử lý cột thời gian
    time_column = None
    for col in df.columns:
        if "Thời gian tạo đơn" in col:
            time_column = col
            break
    
    if time_column:
        df[time_column] = pd.to_datetime(df[time_column], errors="coerce")
    
    # Bộ lọc thông minh
    st.sidebar.header("Bộ lọc dữ liệu")
    selected_status = st.sidebar.multiselect("Trạng thái đơn hàng", df["Trạng Thái Đơn Hàng"].unique(), default=df["Trạng Thái Đơn Hàng"].unique())
    
    if time_column:
        selected_time = st.sidebar.date_input("Chọn thời gian tạo đơn", [df[time_column].min(), df[time_column].max()])
        df_filtered = df[(df["Trạng Thái Đơn Hàng"].isin(selected_status)) & (df[time_column].between(pd.Timestamp(selected_time[0]), pd.Timestamp(selected_time[1])))]
    else:
        df_filtered = df[df["Trạng Thái Đơn Hàng"].isin(selected_status)]
    
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
    shipping_column = None
    for col in df_filtered.columns:
        if "Phí vận chuyển" in col:
            shipping_column = col
            break
    
    if shipping_column:
        df_filtered[shipping_column] = pd.to_numeric(df_filtered[shipping_column], errors="coerce")
    
    # Biểu đồ chi phí vận chuyển
    st.write("### Tỷ lệ Chi phí Vận Chuyển")
    if shipping_column and df_filtered[shipping_column].notnull().sum() > 0:
        cost_chart = px.pie(df_filtered, values=shipping_column, names="Tên sản phẩm", title="Tỷ lệ chi phí vận chuyển")
        st.plotly_chart(cost_chart)
    else:
        st.write("Không có dữ liệu vận chuyển hợp lệ.")
    
    # Xuất báo cáo
    st.write("### Xuất báo cáo")
    st.download_button("Tải về Excel", data=df_filtered.to_csv(index=False).encode("utf-8"), file_name="bao_cao_shopee.csv", mime="text/csv")
