import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cấu hình giao diện
st.set_page_config(page_title="Phân Tích Đơn Hàng", layout="wide")
st.title("📊 Phân Tích Dữ Liệu Đơn Hàng Shopee")

# Tải file lên
uploaded_file = st.file_uploader("📂 Tải lên tệp Excel chứa dữ liệu đơn hàng", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Tệp đã tải lên thành công!")
    
    # Chọn khoảng thời gian để phân tích
    st.sidebar.header("📅 Chọn thời gian so sánh")
    date_col = "Thời gian tạo đơn hàng"
    df[date_col] = pd.to_datetime(df[date_col])
    min_date, max_date = df[date_col].min(), df[date_col].max()
    date_range = st.sidebar.slider("Chọn khoảng thời gian", min_value=min_date, max_value=max_date, value=(min_date, max_date))
    df_filtered = df[(df[date_col] >= date_range[0]) & (df[date_col] <= date_range[1])]
    
    # Tính các chỉ số
    doanh_thu = df_filtered["Tổng giá bán (sản phẩm)"].sum()
    so_luong_ban = df_filtered["Số lượng bán"].sum()
    chi_phi_kinh_doanh = df_filtered["Tổng số tiền được người bán trợ giá"].sum() + df_filtered["Mã giảm giá của Shop"].sum()
    phi_san = df_filtered["Phí cố định"].sum() + df_filtered["Phí Dịch Vụ"].sum() + df_filtered["Phí thanh toán"].sum()
    doanh_thu_thuc_nhan = doanh_thu - chi_phi_kinh_doanh - phi_san
    
    # Hiển thị Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Doanh thu", f"{doanh_thu:,.0f} VND")
    col2.metric("📦 Số lượng bán", f"{so_luong_ban:,}")
    col3.metric("💰 Chi phí Kinh Doanh", f"{chi_phi_kinh_doanh:,.0f} VND")
    
    # Biểu đồ tròn chi phí
    fig, ax = plt.subplots()
    labels = ["Chi phí Kinh Doanh", "Phí sàn", "Doanh thu thực nhận"]
    sizes = [chi_phi_kinh_doanh, phi_san, doanh_thu_thuc_nhan]
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#FF9999", "#66B3FF", "#99FF99"])
    ax.set_title("Tỷ lệ Chi phí & Doanh thu")
    st.pyplot(fig)
    
    # Xuất báo cáo
    if st.button("📤 Xuất báo cáo Excel"):
        output_file = "report.xlsx"
        df_filtered.to_excel(output_file, index=False)
        st.download_button(label="📥 Tải xuống báo cáo", data=open(output_file, "rb").read(), file_name="Phan_Tich_Don_Hang.xlsx")
