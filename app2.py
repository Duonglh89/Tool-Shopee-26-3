import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Phân tích Shopee", page_icon="📊")
st.title("📊 Phân tích & Báo cáo Shopee")

# Bộ nhớ cache để load file nhanh hơn
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace("\\n", " ").str.replace("\\s+", " ", regex=True)
    return df

uploaded_file = st.file_uploader("📂 Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Xử lý hàng tặng
    df.loc[df['Loại hàng'] == 'Tặng', ['Doanh thu', 'Chi phí Kinh Doanh', 'Phí sàn']] = 0
    
    # Xác định các cột quan trọng
    df['Giá gốc'] = pd.to_numeric(df['Giá gốc'], errors='coerce')
    df['Tổng trợ giá'] = pd.to_numeric(df['Tổng số tiền người bán trợ giá'], errors='coerce')
    df['Mã giảm giá Shop'] = pd.to_numeric(df['Mã giảm giá của Shop'], errors='coerce')
    df['Phí cố định'] = pd.to_numeric(df['Phí cố định'], errors='coerce')
    df['Phí dịch vụ'] = pd.to_numeric(df['Phí Dịch Vụ'], errors='coerce')
    df['Phí thanh toán'] = pd.to_numeric(df['Phí Thanh Toán'], errors='coerce')
    
    # Tính toán doanh thu và chi phí
    df['Doanh thu'] = df['Giá gốc'] - df['Tổng trợ giá']
    df['Chi phí Kinh Doanh'] = df['Tổng trợ giá'] + df['Mã giảm giá Shop']
    df['Phí sàn'] = df['Phí cố định'] + df['Phí dịch vụ'] + df['Phí thanh toán']
    
    # Sidebar bộ lọc
    st.sidebar.header("🔎 Bộ lọc dữ liệu")
    selected_status = st.sidebar.multiselect("📌 Trạng thái đơn hàng", sorted(df["Trạng Thái Đơn Hàng"].dropna().unique()))
    selected_products = st.sidebar.multiselect("📦 Tên sản phẩm", sorted(df["Tên sản phẩm"].dropna().unique()))
    
    df_filtered = df
    if selected_status:
        df_filtered = df_filtered[df_filtered["Trạng Thái Đơn Hàng"].isin(selected_status)]
    if selected_products:
        df_filtered = df_filtered[df_filtered["Tên sản phẩm"].isin(selected_products)]
    
    # Tổng hợp doanh thu & chi phí
    st.write("### 📈 Tổng hợp Doanh thu & Chi phí")
    col1, col2 = st.columns(2)
    col1.metric("💰 Tổng Doanh thu", f"{df_filtered['Doanh thu'].sum():,.0f} VNĐ")
    col2.metric("📉 Tổng Chi phí Kinh Doanh", f"{df_filtered['Chi phí Kinh Doanh'].sum():,.0f} VNĐ")
    
    # Biểu đồ doanh thu theo sản phẩm
    st.write("### 📊 Doanh thu theo sản phẩm")
    fig = px.bar(df_filtered, x="Tên sản phẩm", y="Doanh thu", title="📊 Doanh thu theo sản phẩm", text_auto=True, color="Doanh thu", color_continuous_scale="blues")
    st.plotly_chart(fig, use_container_width=True)
    
    # Biểu đồ tròn phân bổ chi phí
    st.write("### 🏷️ Tỷ lệ Chi phí Kinh Doanh & Phí sàn")
    cost_pie = pd.DataFrame({
        "Loại phí": ["Chi phí Kinh Doanh", "Phí sàn"],
        "Giá trị": [df_filtered['Chi phí Kinh Doanh'].sum(), df_filtered['Phí sàn'].sum()]
    })
    pie_chart = px.pie(cost_pie, values="Giá trị", names="Loại phí", title="Phân bổ chi phí", color_discrete_sequence=["#3498db", "#2ecc71"])
    st.plotly_chart(pie_chart)
    
    # Xuất báo cáo
    st.write("### 📤 Xuất báo cáo")
    st.download_button("📥 Tải về Excel", data=df_filtered.to_csv(index=False).encode("utf-8"), file_name="bao_cao_shopee.csv", mime="text/csv")
