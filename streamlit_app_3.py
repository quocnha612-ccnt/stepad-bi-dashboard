import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime, date
import json

# ============================================================
# 1. CẤU HÌNH TRANG
# ============================================================
st.set_page_config(
    page_title="Stepad | Business Intelligence",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0a0a0a; color: #ffffff; }
.stApp > header { background-color: transparent; }

/* Tabs */
button[data-baseweb="tab"] p { color: #555555 !important; font-family: 'JetBrains Mono', monospace !important; }
button[aria-selected="true"] p { color: #00FF00 !important; font-weight: bold !important; }
div[data-baseweb="tab-highlight"] { background-color: #00FF00 !important; }
div[data-baseweb="tab-border"] { background-color: #222222 !important; }

/* Metrics */
[data-testid="stMetricValue"] { 
    color: #00FF00 !important; 
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
}
[data-testid="stMetricLabel"] { color: #888888 !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] {
    background: #111111;
    border: 1px solid #222222;
    border-radius: 8px;
    padding: 16px;
}

/* Inputs */
.stTextInput input, .stSelectbox select, .stNumberInput input {
    background-color: #111111 !important;
    color: #ffffff !important;
    border: 1px solid #333333 !important;
    border-radius: 6px !important;
}
.stSelectbox > div > div {
    background-color: #111111 !important;
    color: #ffffff !important;
    border: 1px solid #333333 !important;
}

/* Buttons */
.stButton > button {
    background-color: #00FF00 !important;
    color: #000000 !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 24px !important;
}
.stButton > button:hover {
    background-color: #00CC00 !important;
    transform: translateY(-1px);
}

/* Dataframe */
.stDataFrame { border: 1px solid #222222 !important; border-radius: 8px !important; }

/* Section headers */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    color: #00FF00;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #222222;
}

/* Cards */
.info-card {
    background: #111111;
    border: 1px solid #222222;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Login */
.login-container {
    max-width: 400px;
    margin: 100px auto;
    background: #111111;
    border: 1px solid #222222;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
}

/* Warning/debt cards */
.debt-high { border-left: 3px solid #FF4444 !important; }
.debt-medium { border-left: 3px solid #FF8800 !important; }
.perf-good { border-left: 3px solid #00FF00 !important; }

/* Order form */
.sku-row {
    background: #111111;
    border: 1px solid #222222;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 8px;
}

div[data-testid="stVerticalBlock"] > div:has(> div > .stAlert) {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. KẾT NỐI GOOGLE SHEETS
# ============================================================
SPREADSHEET_ID = "1Ib1oZck9IwnBy_Ld-Ludb8jcWOFYxYPj7__gqW7FLN4"

@st.cache_resource
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_sheet(sheet_name):
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        values = sheet.get_all_values()
        if not values:
            return pd.DataFrame()
        headers = values[0]
        seen = {}
        clean_headers = []
        for h in headers:
            if h == '' or h is None:
                h = f'_col_{len(clean_headers)}'
            if h in seen:
                seen[h] += 1
                h = f'{h}_{seen[h]}'
            else:
                seen[h] = 0
            clean_headers.append(h)
        df = pd.DataFrame(values[1:], columns=clean_headers)
        df = df.loc[:, ~df.columns.str.startswith('_col_')]
        return df
    except Exception as e:
        st.error(f"Lỗi tải {sheet_name}: {e}")
        return pd.DataFrame()

def append_row(sheet_name, row_data):
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        sheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Lỗi ghi vào {sheet_name}: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False

def update_cell(sheet_name, row, col, value):
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        sheet.update_cell(row, col, value)
        return True
    except Exception as e:
        st.error(f"Lỗi cập nhật: {e}")
        return False

# ============================================================
# 3. HỆ THỐNG ĐĂNG NHẬP
# ============================================================
USERS = {
    "admin": {"password": "stepad2024", "role": "admin", "name": "Admin"},
    "tienmai": {"password": "tien123", "role": "sale", "name": "Mai Xuân Tiến"},
    "canhmai": {"password": "canh123", "role": "sale", "name": "Mai Anh Cảnh"},
    "diepdang": {"password": "diep123", "role": "sale", "name": "Điệp Đặng"},
    "ctv1": {"password": "ctv001", "role": "sale", "name": "CTV1"},
    "ctv2": {"password": "ctv002", "role": "sale", "name": "CTV2"},
    "ctv3": {"password": "ctv003", "role": "sale", "name": "CTV3"},
    "ctv4": {"password": "ctv004", "role": "sale", "name": "CTV4"},
    "ctv5": {"password": "ctv005", "role": "sale", "name": "CTV5"},
}

def login_page():
    st.markdown("""
    <div style="text-align:center; margin-top: 80px;">
        <div style="font-family:'JetBrains Mono',monospace; color:#00FF00; font-size:2rem; font-weight:700; letter-spacing:4px;">
            🚀 STEPAD
        </div>
        <div style="color:#555555; font-size:0.85rem; letter-spacing:2px; margin-top:8px;">
            BUSINESS INTELLIGENCE SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("👤 Tên đăng nhập", placeholder="Nhập username...")
        password = st.text_input("🔒 Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
        
        if st.button("ĐĂNG NHẬP", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = USERS[username]["role"]
                st.session_state.name = USERS[username]["name"]
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu!")

# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================
def fmt_currency(val):
    try:
        return f"{float(val):,.0f} đ"
    except:
        return "0 đ"

def fmt_pct(val):
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return "0%"

def get_gia_theo_khu_vuc(df_sp, sku, khu_vuc):
    try:
        row = df_sp[df_sp['SKU Sản phẩm'] == sku].iloc[0]
        if khu_vuc == "Nha Trang": return float(str(row.get('Giá Nha Trang', 0)).replace(',','').replace('.',''))
        if khu_vuc == "Circle K": return float(str(row.get('Giá Circle K', 0)).replace(',','').replace('.',''))
        if khu_vuc == "MT": return float(str(row.get('Giá MT', 0)).replace(',','').replace('.',''))
        if khu_vuc == "GT": return float(str(row.get('Giá GT', 0)).replace(',','').replace('.',''))
        return 0
    except:
        return 0

def get_khu_vuc(id_khach):
    prefix = str(id_khach)[:2].upper()
    if prefix == "CK": return "Circle K"
    if prefix == "NT": return "Nha Trang"
    if prefix == "MT": return "MT"
    if prefix == "GT": return "GT"
    return "Khác"

def get_kho(khu_vuc, id_khach=""):
    prefix = str(id_khach)[:4].upper()
    if "MB" in prefix or "BAC" in prefix: return "Bắc"
    if "MN" in prefix or "NAM" in prefix: return "Nam"
    if khu_vuc == "Nha Trang": return "Nam"
    return "Nam"

# ============================================================
# 5. MAIN APP
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Header
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace; color:#00FF00; font-size:1.4rem; font-weight:700; letter-spacing:3px; padding: 8px 0;">
        🚀 STEPAD — QUẢN LÝ DOANH SỐ
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
    <div style="text-align:right; color:#555555; font-size:0.8rem; padding-top:12px;">
        👤 {st.session_state.name} &nbsp;|&nbsp; 
        <span style="color:#00FF00">{st.session_state.role.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Đăng xuất", key="logout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='border-color:#222222; margin: 0 0 16px 0;'>", unsafe_allow_html=True)

# ============================================================
# 6. TABS
# ============================================================
if st.session_state.role == "admin":
    tabs = st.tabs(["🏠 Dashboard", "📝 Lên đơn", "📦 Đơn hàng", "🏷️ Sản phẩm", "👥 Khách hàng", "🏪 Circle K"])
    t_dash, t_order, t_don, t_sp, t_kh, t_ck = tabs
else:
    tabs = st.tabs(["📝 Lên đơn", "📦 Đơn hàng của tôi"])
    t_order, t_don = tabs

# ============================================================
# TAB: DASHBOARD
# ============================================================
if st.session_state.role == "admin":
    with t_dash:
        df_dash = load_sheet("Dashboard")
        df_kh = load_sheet("Khach_Hang")

        if not df_dash.empty:
            st.markdown('<div class="section-header">💳 TÀI CHÍNH TỔNG QUAN</div>', unsafe_allow_html=True)
            
            try:
                row = df_dash.iloc[0]
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1: st.metric("TỔNG DOANH THU", fmt_currency(row.iloc[0]))
                with col2: st.metric("ĐÃ THỰC NHẬN", fmt_currency(row.iloc[1]))
                with col3: st.metric("NỢ CẦN THU", fmt_currency(row.iloc[2]))
                with col4: st.metric("TỔNG CỬA HÀNG", f"{row.iloc[3]} điểm")
                with col5: st.metric("CH ACTIVE 3T", f"{row.iloc[4]} điểm")
                with col6: st.metric("TỶ LỆ PHỦ", f"{row.iloc[5]}")
            except Exception as e:
                st.error(f"Lỗi đọc Dashboard: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">📊 DOANH THU THEO KÊNH</div>', unsafe_allow_html=True)

            try:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🏪 CIRCLE K**")
                    st.metric("Tổng", fmt_currency(df_dash.iloc[4, 0]))
                    st.metric("Miền Bắc", fmt_currency(df_dash.iloc[4, 1]))
                    st.metric("Miền Nam", fmt_currency(df_dash.iloc[4, 2]))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🏬 MODERN TRADE**")
                    st.metric("Tổng DT", fmt_currency(df_dash.iloc[7, 0]))
                    st.metric("Đã TT", fmt_currency(df_dash.iloc[7, 1]))
                    st.metric("Nợ", fmt_currency(df_dash.iloc[7, 2]))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🛒 GENERAL TRADE**")
                    st.metric("Tổng DT", fmt_currency(df_dash.iloc[9, 0]))
                    st.metric("Đã TT", fmt_currency(df_dash.iloc[9, 1]))
                    st.metric("Nợ", fmt_currency(df_dash.iloc[9, 2]))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🌊 NHA TRANG**")
                    st.metric("Ký gửi", fmt_currency(df_dash.iloc[14, 0]))
                    st.metric("Đã TT", fmt_currency(df_dash.iloc[14, 1]))
                    st.metric("Nợ", fmt_currency(df_dash.iloc[14, 2]))
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Đang chờ dữ liệu kênh phân phối...")

        st.markdown("<br>", unsafe_allow_html=True)

        # Cảnh báo nợ & hiệu suất
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown('<div class="section-header">🔴 TOP KHÁCH NỢ NHIỀU</div>', unsafe_allow_html=True)
            if not df_kh.empty and 'Còn nợ' in df_kh.columns and 'Tên cửa hàng' in df_kh.columns:
                try:
                    df_no = df_kh[pd.to_numeric(df_kh['Còn nợ'], errors='coerce') > 0].copy()
                    df_no['Còn nợ'] = pd.to_numeric(df_no['Còn nợ'], errors='coerce')
                    df_no = df_no.nlargest(5, 'Còn nợ')[['Tên cửa hàng', 'Còn nợ', 'Khu vực']]
                    df_no['Còn nợ'] = df_no['Còn nợ'].apply(fmt_currency)
                    st.dataframe(df_no, use_container_width=True, hide_index=True)
                except:
                    st.info("Chưa có dữ liệu nợ")
            else:
                st.info("Chưa có dữ liệu")

        with col_right:
            st.markdown('<div class="section-header">🟢 TOP KHÁCH HIỆU SUẤT TỐT</div>', unsafe_allow_html=True)
            if not df_kh.empty and 'Tổng doanh thu' in df_kh.columns:
                try:
                    col_dt = [c for c in df_kh.columns if 'doanh thu' in c.lower() or 'Tổng' in c][0]
                    col_tt = [c for c in df_kh.columns if 'thanh toán' in c.lower() or 'Đã' in c][0]
                    df_perf = df_kh.copy()
                    df_perf[col_dt] = pd.to_numeric(df_perf[col_dt], errors='coerce').fillna(0)
                    df_perf[col_tt] = pd.to_numeric(df_perf[col_tt], errors='coerce').fillna(0)
                    df_perf = df_perf[df_perf[col_dt] > 0]
                    df_perf["Tỷ lệ TT"] = (df_perf[col_tt] / df_perf[col_dt] * 100).round(1).astype(str) + "%"
                    df_perf = df_perf.nlargest(5, col_dt)[["Tên cửa hàng", col_dt, "Tỷ lệ TT"]]
                    df_perf = df_perf.rename(columns={col_dt: "Tổng doanh thu"})
                    df_perf["Tổng doanh thu"] = df_perf["Tổng doanh thu"].apply(fmt_currency)
                    st.dataframe(df_perf, use_container_width=True, hide_index=True)
                except:
                    st.info("Chưa có dữ liệu hiệu suất")
            else:
                st.info("Chưa có dữ liệu")

# ============================================================
# TAB: LÊN ĐƠN HÀNG
# ============================================================
with t_order:
    df_kh = load_sheet("Khach_Hang")
    df_sp = load_sheet("San_Pham")

    if df_kh.empty or df_sp.empty:
        st.error("Không thể tải dữ liệu. Vui lòng thử lại!")
        st.stop()

    # Khởi tạo session state
    if "order_items" not in st.session_state:
        st.session_state.order_items = [{"sku": "", "sl": 1}]
    if "order_success" not in st.session_state:
        st.session_state.order_success = False
    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    # Hiện thông báo thành công nếu vừa lưu xong
    if st.session_state.order_success:
        st.success(f"✅ Đơn hàng đã được lưu thành công! Form đã được làm mới.")
        st.session_state.order_success = False

    # ---- THÔNG TIN ĐƠN HÀNG ----
    st.markdown('<div class="section-header">📋 THÔNG TIN ĐƠN HÀNG</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        ds_khach = df_kh['ID Khách'].tolist() if 'ID Khách' in df_kh.columns else []
        ds_ten = df_kh['Tên cửa hàng'].tolist() if 'Tên cửa hàng' in df_kh.columns else []
        ds_khach_display = [f"{id} — {ten}" for id, ten in zip(ds_khach, ds_ten)]
        khach_selected = st.selectbox("👤 Khách hàng *", ds_khach_display, key=f"sel_khach_{st.session_state.form_key}")
        id_khach = khach_selected.split(" — ")[0] if khach_selected else ""
        khu_vuc = get_khu_vuc(id_khach)
        st.markdown(f"<small style='color:#00FF00'>📍 Khu vực: <b>{khu_vuc}</b></small>", unsafe_allow_html=True)

    with col2:
        ngay_don = st.date_input("📅 Ngày đơn", value=date.today(), key=f"ngay_{st.session_state.form_key}")

    col3, col4, col5 = st.columns(3)
    with col3:
        loai_don = st.selectbox("📋 Loại đơn *", ["Ký gửi", "Bổ sung hàng", "Circle K"], key=f"loai_{st.session_state.form_key}")
    with col4:
        thue_suat = st.selectbox("💰 Thuế suất", [0.08, 0.0], format_func=lambda x: f"{int(x*100)}%", key=f"thue_{st.session_state.form_key}")
    with col5:
        ma_po = st.text_input("🔖 Mã PO", placeholder="Nhập nếu có...", key=f"mapo_{st.session_state.form_key}")

    tt_hd = st.selectbox("🧾 Xuất hóa đơn VAT?", ["Không xuất HĐ", "Có xuất HĐ"], key=f"tthd_{st.session_state.form_key}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- DANH SÁCH SẢN PHẨM ----
    st.markdown('<div class="section-header">🛒 SẢN PHẨM ĐẶT HÀNG</div>', unsafe_allow_html=True)

    ds_sku = df_sp['SKU Sản phẩm'].tolist() if 'SKU Sản phẩm' in df_sp.columns else []
    ds_ten_sp = df_sp['Tên sản phẩm'].tolist() if 'Tên sản phẩm' in df_sp.columns else []
    ds_sku_display = [f"{sku} — {ten}" for sku, ten in zip(ds_sku, ds_ten_sp)]

    tong_truoc_thue = 0
    items_data = []

    # Header bảng
    h1, h2, h3, h4, h5 = st.columns([3, 1, 1.5, 1.5, 0.5])
    with h1: st.markdown("<small style='color:#555'>Sản phẩm</small>", unsafe_allow_html=True)
    with h2: st.markdown("<small style='color:#555'>Số lượng</small>", unsafe_allow_html=True)
    with h3: st.markdown("<small style='color:#555'>Đơn giá</small>", unsafe_allow_html=True)
    with h4: st.markdown("<small style='color:#555'>Thành tiền</small>", unsafe_allow_html=True)

    for i, item in enumerate(st.session_state.order_items):
        col_sku, col_sl, col_gia, col_tt, col_del = st.columns([3, 1, 1.5, 1.5, 0.5])

        with col_sku:
            sku_sel = st.selectbox(
                f"SP{i+1}",
                ["-- Chọn --"] + ds_sku_display,
                key=f"sku_{st.session_state.form_key}_{i}",
                label_visibility="collapsed"
            )
        with col_sl:
            sl = st.number_input("SL", min_value=1, value=1, key=f"sl_{st.session_state.form_key}_{i}", label_visibility="collapsed")

        sku_code = sku_sel.split(" — ")[0] if sku_sel != "-- Chọn --" else ""
        don_gia = get_gia_theo_khu_vuc(df_sp, sku_code, khu_vuc) if sku_code else 0
        thanh_tien = don_gia * sl
        tong_truoc_thue += thanh_tien

        with col_gia:
            st.markdown(f"<div style='padding-top:8px; color:#888'>{fmt_currency(don_gia)}</div>", unsafe_allow_html=True)
        with col_tt:
            st.markdown(f"<div style='padding-top:8px; color:#00FF00; font-weight:700'>{fmt_currency(thanh_tien)}</div>", unsafe_allow_html=True)
        with col_del:
            if st.button("✕", key=f"del_{st.session_state.form_key}_{i}") and len(st.session_state.order_items) > 1:
                st.session_state.order_items.pop(i)
                st.rerun()

        if sku_code:
            items_data.append({"sku": sku_code, "sl": sl, "don_gia": don_gia, "thanh_tien": thanh_tien})

    if st.button("➕ Thêm sản phẩm", key=f"add_sku_{st.session_state.form_key}"):
        st.session_state.order_items.append({"sku": "", "sl": 1})
        st.rerun()

    # ---- TỔNG KẾT ----
    st.markdown("<hr style='border-color:#222222; margin:16px 0'>", unsafe_allow_html=True)

    tien_thue = tong_truoc_thue * thue_suat
    tong_sau_thue = tong_truoc_thue + tien_thue

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1: st.metric("Trước thuế", fmt_currency(tong_truoc_thue))
    with col_s2: st.metric(f"Thuế {int(thue_suat*100)}%", fmt_currency(tien_thue))
    with col_s3: st.metric("💰 TỔNG SAU THUẾ", fmt_currency(tong_sau_thue))

    col_tt1, col_tt2 = st.columns(2)
    with col_tt1:
        da_thanh_toan = st.number_input("💵 Đã thanh toán (đ)", min_value=0, value=0, step=100000, key=f"datt_{st.session_state.form_key}")
    with col_tt2:
        con_no = tong_sau_thue - da_thanh_toan
        st.metric("Còn nợ", fmt_currency(con_no))

    ghi_chu = st.text_area("📝 Ghi chú", placeholder="Ghi chú đặc biệt cho đơn hàng này...", height=80, key=f"ghichu_{st.session_state.form_key}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✅ XÁC NHẬN ĐƠN HÀNG", use_container_width=True, key="submit_order"):
        if not id_khach:
            st.error("Vui lòng chọn khách hàng!")
        elif not items_data:
            st.error("Vui lòng thêm ít nhất 1 sản phẩm!")
        else:
            with st.spinner("Đang lưu đơn hàng..."):
                now = datetime.now()
                id_don = f"DH{now.strftime('%Y%m%d%H%M%S')}"
                thang = now.strftime("%m/%Y")
                kho = get_kho(khu_vuc, id_khach)

                if da_thanh_toan == 0:
                    tt_thanh_toan = "Chưa TT"
                elif da_thanh_toan < tong_sau_thue:
                    tt_thanh_toan = "Thanh toán 1 phần"
                else:
                    tt_thanh_toan = "Đã TT đủ"

                ten_khach = ""
                try:
                    ten_khach = df_kh[df_kh['ID Khách'] == id_khach]['Tên cửa hàng'].iloc[0]
                except:
                    pass

                nhan_vien = st.session_state.name
                success = True

                # Ghi vào Don_Hang — đúng thứ tự 23 cột A→W
                for item in items_data:
                    row_don_hang = [
                        id_don,           # A: ID Đơn
                        id_khach,         # B: ID Khách hàng
                        str(ngay_don),    # C: Ngày tạo đơn
                        loai_don,         # D: Loại đơn
                        item['sku'],      # E: SKU Sản phẩm
                        "",               # F: Tên sản phẩm (công thức tự điền)
                        item['sl'],       # G: Số lượng
                        thue_suat,        # H: Thuế suất
                        item['don_gia'],  # I: Đơn giá
                        item['thanh_tien'],                    # J: Thành tiền trước thuế
                        item['thanh_tien'] * thue_suat,       # K: Tiền thuế
                        item['thanh_tien'] * (1 + thue_suat), # L: Tổng sau thuế
                        da_thanh_toan,    # M: Đã thanh toán
                        con_no,           # N: Còn nợ
                        khu_vuc,          # O: Khu vực
                        ma_po,            # P: Mã PO
                        thang,            # Q: Tháng
                        tt_thanh_toan,    # R: Trạng thái TT
                        tt_hd,            # S: Trạng thái HĐ
                        ten_khach,        # T: Tên khách hàng
                        kho,              # U: Kho xuất
                        nhan_vien,        # V: Nhân viên
                        ""                # W: Ngày thanh toán
                    ]
                    if not append_row("Don_Hang", row_don_hang):
                        success = False
                        break

                # Ghi vào Phieu_nhap_don
                if success:
                    row_phieu = [
                        id_don,
                        str(ngay_don),
                        id_khach,
                        ten_khach,
                        khu_vuc,
                        loai_don,
                        ma_po,
                        nhan_vien,
                        f"{int(thue_suat*100)}%",
                        tong_sau_thue,
                        da_thanh_toan,
                        con_no,
                        tt_hd,
                        tt_thanh_toan,
                        ghi_chu,
                        kho
                    ]
                    append_row("Phieu_nhap_don", row_phieu)

                if success:
                    # Reset form hoàn toàn bằng cách tăng form_key
                    st.session_state.order_items = [{"sku": "", "sl": 1}]
                    st.session_state.order_success = True
                    st.session_state.form_key += 1
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Có lỗi xảy ra khi lưu đơn hàng. Vui lòng thử lại!")

# ============================================================
# TAB: ĐƠN HÀNG
# ============================================================
with t_don:
    st.markdown('<div class="section-header">📦 DANH SÁCH ĐƠN HÀNG</div>', unsafe_allow_html=True)
    df_don = load_sheet("Don_Hang")
    
    if not df_don.empty:
        if st.session_state.role == "sale":
            df_don = df_don[df_don.get('Nhân viên', '') == st.session_state.name]
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search = st.text_input("🔍 Tìm kiếm", placeholder="Tìm theo ID khách, tên...")
        with col_f2:
            if 'Khu vực' in df_don.columns:
                kv_filter = st.selectbox("Lọc khu vực", ["Tất cả"] + df_don['Khu vực'].dropna().unique().tolist())
        
        if search:
            mask = df_don.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
            df_don = df_don[mask]
        if 'Khu vực' in df_don.columns and kv_filter != "Tất cả":
            df_don = df_don[df_don['Khu vực'] == kv_filter]
        
        st.dataframe(df_don, use_container_width=True, hide_index=True)
        st.caption(f"Tổng: {len(df_don)} dòng")
    else:
        st.info("Chưa có đơn hàng nào.")

# ============================================================
# TAB: SẢN PHẨM (Admin only)
# ============================================================
if st.session_state.role == "admin":
    with t_sp:
        st.markdown('<div class="section-header">🏷️ DANH SÁCH SẢN PHẨM</div>', unsafe_allow_html=True)
        df_sp_full = load_sheet("San_Pham")
        if not df_sp_full.empty:
            # Highlight cảnh báo tồn kho
            st.dataframe(df_sp_full, use_container_width=True, hide_index=True)
            
            # Cảnh báo tồn kho thấp
            if 'Trạng thái tồn kho' in df_sp_full.columns:
                df_canh_bao = df_sp_full[df_sp_full['Trạng thái tồn kho'].astype(str).str.contains('Cảnh báo|Hết', na=False)]
                if not df_canh_bao.empty:
                    st.warning(f"⚠️ **{len(df_canh_bao)} sản phẩm** cần chú ý tồn kho!")
                    st.dataframe(df_canh_bao[['SKU Sản phẩm', 'Tên sản phẩm', 'Tổng kho', 'Trạng thái tồn kho']], use_container_width=True, hide_index=True)

    # ============================================================
    # TAB: KHÁCH HÀNG (Admin only)
    # ============================================================
    with t_kh:
        st.markdown('<div class="section-header">👥 DANH SÁCH KHÁCH HÀNG</div>', unsafe_allow_html=True)
        df_kh_full = load_sheet("Khach_Hang")
        if not df_kh_full.empty:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_kh = st.text_input("🔍 Tìm kiếm khách hàng", placeholder="Tên, ID, khu vực...")
            with col_f2:
                if 'Kênh phân phối' in df_kh_full.columns:
                    kenh_filter = st.selectbox("Lọc kênh", ["Tất cả"] + df_kh_full['Kênh phân phối'].dropna().unique().tolist())
            
            df_display = df_kh_full.copy()
            if search_kh:
                mask = df_display.astype(str).apply(lambda x: x.str.contains(search_kh, case=False)).any(axis=1)
                df_display = df_display[mask]
            if 'Kênh phân phối' in df_kh_full.columns and kenh_filter != "Tất cả":
                df_display = df_display[df_display['Kênh phân phối'] == kenh_filter]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Tổng: {len(df_display)} khách hàng")

    # ============================================================
    # TAB: CIRCLE K
    # ============================================================
    with t_ck:
        st.markdown('<div class="section-header">🏪 PHÂN TÍCH CIRCLE K</div>', unsafe_allow_html=True)
        
        df_ck_raw = load_sheet("Biểu đồ CircleK")
        df_don_ck = load_sheet("Don_Hang")

        if not df_ck_raw.empty:
            # Biểu đồ doanh thu theo tháng
            try:
                cols = df_ck_raw.columns.tolist()
                if len(cols) >= 4:
                    df_ck_plot = df_ck_raw.copy()
                    col_thang = cols[0]
                    col_bac = cols[1]
                    col_nam = cols[2]
                    col_tong = cols[3]

                    def to_num(s):
                        try:
                            return float(str(s).replace('đ','').replace('.','').replace(',','.').strip())
                        except:
                            return 0

                    df_ck_plot[col_bac] = df_ck_plot[col_bac].apply(to_num)
                    df_ck_plot[col_nam] = df_ck_plot[col_nam].apply(to_num)
                    df_ck_plot[col_tong] = df_ck_plot[col_tong].apply(to_num)

                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df_ck_plot[col_thang], y=df_ck_plot[col_bac], name='Miền Bắc', marker_color='#006400', hovertemplate='%{y:,.0f} đ'))
                    fig.add_trace(go.Bar(x=df_ck_plot[col_thang], y=df_ck_plot[col_nam], name='Miền Nam', marker_color='#00A300', hovertemplate='%{y:,.0f} đ'))
                    fig.add_trace(go.Bar(x=df_ck_plot[col_thang], y=df_ck_plot[col_tong], name='TỔNG', marker_color='#00FF00', hovertemplate='%{y:,.0f} đ'))
                    fig.update_layout(
                        title={'text': "📊 DOANH THU CIRCLE K THEO THÁNG", 'x': 0.5, 'font': {'color': '#00FF00', 'size': 14}},
                        barmode='group', height=400,
                        xaxis=dict(tickfont=dict(color='#888888')),
                        yaxis=dict(gridcolor='#222222', tickfont=dict(color='#888888')),
                        legend=dict(font=dict(color='#ffffff'), orientation="h", y=1.1),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Đang tải biểu đồ... ({e})")

        # Thống kê PO
        st.markdown('<div class="section-header">📋 THỐNG KÊ PO</div>', unsafe_allow_html=True)
        df_dash_ck = load_sheet("Dashboard")
        if not df_dash_ck.empty:
            try:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📍 Miền Nam**")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("SL PO", df_dash_ck.iloc[18, 0])
                    with c2: st.metric("Min", fmt_currency(df_dash_ck.iloc[20, 0]))
                    with c3: st.metric("Max", fmt_currency(df_dash_ck.iloc[22, 0]))
                    with c4: st.metric("Avg", fmt_currency(df_dash_ck.iloc[24, 0]))
                with col2:
                    st.markdown("**📍 Miền Bắc**")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("SL PO", df_dash_ck.iloc[18, 1])
                    with c2: st.metric("Min", fmt_currency(df_dash_ck.iloc[20, 1]))
                    with c3: st.metric("Max", fmt_currency(df_dash_ck.iloc[22, 1]))
                    with c4: st.metric("Avg", fmt_currency(df_dash_ck.iloc[24, 1]))
            except:
                st.info("Chưa có dữ liệu PO")

        # Top SKU
        st.markdown('<div class="section-header">🏷️ PHÂN TÍCH SKU</div>', unsafe_allow_html=True)
        col_top, col_slow = st.columns(2)
        with col_top:
            st.markdown("🔥 **TOP 3 MÃ BÁN CHẠY**")
            try:
                data_top = {
                    "Mã SKU": [df_dash_ck.iloc[17, 4], df_dash_ck.iloc[18, 4], df_dash_ck.iloc[19, 4]],
                    "Sản lượng": [df_dash_ck.iloc[17, 5], df_dash_ck.iloc[18, 5], df_dash_ck.iloc[19, 5]]
                }
                st.table(pd.DataFrame(data_top))
            except:
                st.info("Chưa có dữ liệu")
        with col_slow:
            st.markdown("⚠️ **TOP 3 MÃ BÁN CHẬM**")
            try:
                data_slow = {
                    "Mã SKU": [df_dash_ck.iloc[22, 4], df_dash_ck.iloc[23, 4], df_dash_ck.iloc[24, 4]],
                    "Sản lượng": [df_dash_ck.iloc[22, 5], df_dash_ck.iloc[23, 5], df_dash_ck.iloc[24, 5]]
                }
                st.table(pd.DataFrame(data_slow))
            except:
                st.info("Chưa có dữ liệu")
