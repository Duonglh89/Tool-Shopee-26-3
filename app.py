import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Hàm đọc file Excel
def load_data(file):
    try:
        df = pd.read_excel(file, engine='openpyxl')
        st.write("Dữ liệu đã tải lên thành công!")
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
        return None

# Hàm xử lý dữ liệu
def process_data(df):
    required_columns = ["Thời gian tạo đơn hàng", "Tổng số tiền được người bán trợ giá", "Mã giảm giá của Shop", "Phí cố định", "Phí Dịch Vụ", "Phí thanh toán", "Giá gốc"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Thiếu các cột sau trong file: {', '.join(missing_columns)}")
        return None
    
    # Chuyển đổi cột ngày tháng
    df["Thời gian tạo đơn hàng"] = pd.to_datetime(df["Thời gian tạo đơn hàng"], errors='coerce')
    
    # Tính toán doanh thu và chi phí
    df["Chi phí kinh doanh"] = df["Tổng số tiền được người bán trợ giá"] + df["Mã giảm giá của Shop"]
    df["Phí sàn"] = df["Phí cố định"] + df["Phí Dịch Vụ"] + df["Phí thanh toán"]
    df["Tổng giá bán sản phẩm"] = df["Giá gốc"] - df["Tổng số tiền được người bán trợ giá"]
    
    return df

# Hàm hiển thị báo cáo
def display_report(df):
    st.write("## Báo cáo Doanh thu & Chi phí")
    st.write(df.head())
    
    # Vẽ biểu đồ tròn
    fig, ax = plt.subplots()
    labels = ["Chi phí Kinh Doanh", "Phí Sàn"]
    values = [df["Chi phí kinh doanh"].sum(), df["Phí sàn"].sum()]
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=["#66b3ff", "#ff9999"])
    st.pyplot(fig)

# Giao diện Streamlit
st.title("Phân tích dữ liệu Shopee")

uploaded_file = st.file_uploader("Tải file Excel lên", type=["xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        df = process_data(df)
        if df is not None:
            display_report(df)
