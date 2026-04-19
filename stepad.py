import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Cấu hình giao diện Stepad Tech-Dark
st.set_page_config(page_title="Stepad | Business Intelligence", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background-color: #0d0d0d; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'JetBrains Mono', monospace; }
    button[data-baseweb="tab"] p { color: #888888 !important; }
    button[aria-selected="true"] p { color: #00FF00 !important; font-weight: bold; }
    div[data-baseweb="tab-highlight"] { background-color: #00FF00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Khai báo 5 Link CSV của ông
URL_DON_HANG   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFyaex58psvVRtkjjnBOVp1Ey4t3QYvcRetSuCq0rjl18_TYzGzkZFV4G5MjUnuyzyz0A2FUbYz1I1/pub?gid=1885967217&single=true&output=csv"
URL_SAN_PHAM   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFyaex58psvVRtkjjnBOVp1Ey4t3QYvcRetSuCq0rjl18_TYzGzkZFV4G5MjUnuyzyz0A2FUbYz1I1/pub?gid=0&single=true&output=csv"
URL_KHACH_HANG = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFyaex58psvVRtkjjnBOVp1Ey4t3QYvcRetSuCq0rjl18_TYzGzkZFV4G5MjUnuyzyz0A2FUbYz1I1/pub?gid=1232323261&single=true&output=csv"
URL_DASH_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFyaex58psvVRtkjjnBOVp1Ey4t3QYvcRetSuCq0rjl18_TYzGzkZFV4G5MjUnuyzyz0A2FUbYz1I1/pub?gid=66029731&single=true&output=csv"
URL_CIRCLE_K   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFyaex58psvVRtkjjnBOVp1Ey4t3QYvcRetSuCq0rjl18_TYzGzkZFV4G5MjUnuyzyz0A2FUbYz1I1/pub?gid=1403222115&single=true&output=csv"

def load(url):
    try:
        return pd.read_csv(url)
    except:
        return None

# 3. Thanh điều hướng
st.title("🚀 STEPAD - QUẢN LÝ DOANH SỐ")
t_dash, t_don, t_sp, t_kh, t_ck = st.tabs([
    "🏠 Bảng điều khiển", "📦 Đơn hàng", "🏷️ Sản phẩm", "👥 Khách hàng", "🏪 CircleK"
])

# --- TAB 1: BẢNG ĐIỀU KHIỂN (PHẦN 1: TÀI CHÍNH) ---
with t_dash:
    df_sum = load(URL_DASH_SHEET) # Link tab Dashboard của ông
    
    if df_sum is not None and len(df_sum) > 0:
        try:
            # Hàm làm sạch dữ liệu để hiển thị số chuẩn
            def clean(val):
                if pd.isna(val): return 0
                s = str(val).replace('đ', '').replace('.', '').replace(',', '').strip()
                return pd.to_numeric(s, errors='coerce') or 0

            st.markdown("## 💳 PHẦN 1: TÀI CHÍNH & HỆ THỐNG CỬA HÀNG")
            
            # --- HÀNG TRÊN (Doanh thu & Nợ) ---
            st.markdown("#### 💰 Chỉ số tài chính")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("TỔNG DOANH THU", f"{clean(df_sum.iloc[0, 0]):,} đ") # Ô A2
            with col2:
                st.metric("DOANH THU THỰC NHẬN", f"{clean(df_sum.iloc[0, 1]):,} đ") # Ô B2
            with col3:
                st.metric("NỢ CẦN THU", f"{clean(df_sum.iloc[0, 2]):,} đ") # Ô C2

            st.markdown("<br>", unsafe_allow_html=True) # Tạo khoảng cách nhẹ giữa 2 hàng

            # --- HÀNG DƯỚI (Số liệu cửa hàng) ---
            st.markdown("#### 🏪 Hiệu suất điểm bán")
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("TỔNG CỬA HÀNG", f"{df_sum.iloc[0, 3]} điểm") # Ô D2
            with col5:
                st.metric("CH CÓ ĐƠN (3 THÁNG)", f"{df_sum.iloc[0, 4]} điểm") # Ô E2
            with col6:
                # Tỷ lệ thường là % nên ta giữ nguyên định dạng từ Sheets
                ty_le = df_sum.iloc[0, 5]
                st.metric("TỶ LỆ CỬA HÀNG", f"{ty_le}") # Ô F2

            st.markdown("---")
# --- PHẦN 2: KHU VỰC NHA TRANG ---
            st.markdown("## 🌊 PHẦN 2: KHU VỰC NHA TRANG")
            
            # Tạo hàng ngang gồm 3 phần tử
            col_nt1, col_nt2, col_nt3 = st.columns(3)
            
            with col_nt1:
                # Ô A7 tương ứng với iloc[5, 0]
                st.metric("TỔNG TIỀN KÝ GỬI", f"{clean(df_sum.iloc[5, 0]):,} đ")
                
            with col_nt2:
                # Ô B7 tương ứng với iloc[5, 1]
                st.metric("TIỀN NỢ CẦN THU", f"{clean(df_sum.iloc[5, 1]):,} đ", delta_color="inverse")
                
            with col_nt3:
                # Ô C7 tương ứng với iloc[5, 2]
                st.metric("DOANH THU ĐÃ THANH TOÁN", f"{clean(df_sum.iloc[5, 2]):,} đ")

            st.markdown("---")
# --- PHẦN 3: DOANH SỐ CIRCLE K ---
            st.markdown("## 🏪 PHẦN 3: DOANH SỐ CIRCLE K")
            
            # Chia đều không gian Trái và Phải
            col_trai, col_phai = st.columns(2)

            # --- BÊN TRÁI: DOANH SỐ (So sánh Nam - Bắc) ---
            with col_trai:
                st.markdown("### 📊 SO SÁNH DOANH SỐ")
                
                # Chia đôi dọc để so sánh
                c_nam, c_bac = st.columns(2)
                
                with c_nam:
                    st.info("📍 MIỀN NAM")
                    st.metric("SL PO", f"{df_sum.iloc[9, 0]}")    # A11 (Index 9)
                    st.metric("(Min)", f"{df_sum.iloc[11, 0]}") # A13 (Index 11)
                    st.metric("Cao nhất (Max)", f"{df_sum.iloc[13, 0]}")  # A15 (Index 13)
                    st.metric("Trung bình", f"{df_sum.iloc[15, 0]}")      # A17 (Index 15)

                with c_bac:
                    st.success("📍 MIỀN BẮC")
                    st.metric("SL PO", f"{df_sum.iloc[9, 1]}")    # B11 (Index 9)
                    st.metric("(Min)", f"{df_sum.iloc[11, 1]}") # B13 (Index 11)
                    st.metric("Cao nhất (Max)", f"{df_sum.iloc[13, 1]}")  # B15 (Index 13)
                    st.metric("Trung bình", f"{df_sum.iloc[15, 1]}")      # B17 (Index 15)

            # --- BÊN PHẢI: PHÂN TÍCH MÃ HÀNG (SKU) ---
            with col_phai:
                st.markdown("### 📦 PHÂN TÍCH MÃ HÀNG")
                
                # Nhóm 1: Top 3 Mã bán chạy
                st.write("🔥 **TOP 3 MÃ BÁN CHẠY**")
                # Tạo bảng nhỏ cho gọn
                data_top = {
                    "Tên sản phẩm": [df_sum.iloc[9, 4], df_sum.iloc[10, 4], df_sum.iloc[11, 4]], # E11, E12, E13
                    "Sản lượng": [df_sum.iloc[9, 5], df_sum.iloc[10, 5], df_sum.iloc[11, 5]]    # F11, F12, F13
                }
                st.table(pd.DataFrame(data_top))

                st.markdown("<br>", unsafe_allow_html=True)

                # Nhóm 2: Top 3 Mã bán chậm (Cần chú ý)
                st.write("⚠️ **TOP 3 MÃ BÁN CHẬM**")
                data_slow = {
                    "Tên sản phẩm": [df_sum.iloc[14, 4], df_sum.iloc[15, 4], df_sum.iloc[16, 4]], # E16, E17, E18
                    "Sản lượng": [df_sum.iloc[14, 5], df_sum.iloc[15, 5], df_sum.iloc[16, 5]]    # F16, F17, F18
                }
                st.table(pd.DataFrame(data_slow))

            st.markdown("---")

        except Exception as e:
            st.error(f"Lỗi tọa độ ô: {e}. Hãy đảm bảo hàng 2 trong Sheets (A2-F2) có dữ liệu.")
    else:
        st.warning("⚡ Đang chờ kết nối dữ liệu tài chính từ hệ thống...")
# --- CÁC TRANG DỮ LIỆU THÔ ---
with t_don:
    st.dataframe(load(URL_DON_HANG), use_container_width=True)
with t_sp:
    st.dataframe(load(URL_SAN_PHAM), use_container_width=True)
with t_kh:
    st.dataframe(load(URL_KHACH_HANG), use_container_width=True)
with t_ck:
    st.dataframe(load(URL_CIRCLE_K), use_container_width=True)