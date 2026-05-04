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

@st.cache_data(ttl=300)
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

# ============================================================
# NGÔN NGỮ / 语言
# ============================================================
LANG = {
    "vi": {
        "title": "🚀 STEPAD — QUẢN LÝ DOANH SỐ",
        "logout": "Đăng xuất", "login_btn": "ĐĂNG NHẬP",
        "login_user": "👤 Tên đăng nhập", "login_pass": "🔒 Mật khẩu",
        "login_err": "Sai tên đăng nhập hoặc mật khẩu!",
        "tab_dash": "🏠 Dashboard", "tab_order": "📝 Lên đơn", "tab_don": "📦 Đơn hàng",
        "tab_sp": "🏷️ Sản phẩm", "tab_kh": "👥 Khách hàng", "tab_ck": "🏪 Circle K",
        "tab_don_sale": "📦 Đơn hàng của tôi",
        "tai_chinh": "💳 TÀI CHÍNH TỔNG QUAN",
        "tong_dt": "TỔNG DOANH THU", "da_nhan": "ĐÃ THỰC NHẬN", "no_thu": "NỢ CẦN THU",
        "tong_ch": "TỔNG CỬA HÀNG", "ch_active": "CH ACTIVE 3T", "ty_le_phu": "TỶ LỆ PHỦ",
        "diem": "điểm", "dt_kenh": "📊 DOANH THU THEO KÊNH",
        "tong": "Tổng", "mien_bac": "Miền Bắc", "mien_nam": "Miền Nam",
        "tong_dt2": "Tổng DT", "da_tt": "Đã TT", "no": "Nợ", "ky_gui": "Ký gửi",
        "top_no": "🔴 TOP KHÁCH NỢ NHIỀU", "top_hieu_suat": "🟢 TOP KHÁCH HIỆU SUẤT TỐT",
        "chua_du_lieu": "Chưa có dữ liệu", "chua_du_lieu_no": "Chưa có dữ liệu nợ",
        "thong_tin_don": "📋 THÔNG TIN ĐƠN HÀNG",
        "khach_hang": "👤 Khách hàng *", "khu_vuc_label": "📍 Khu vực:",
        "ngay_don": "📅 Ngày đơn", "loai_don": "📋 Loại đơn *",
        "thue_suat": "💰 Thuế suất", "ma_po": "🔖 Mã PO", "nhap_neu_co": "Nhập nếu có...",
        "xuat_hd": "🧾 Xuất hóa đơn VAT?", "sp_dat_hang": "🛒 SẢN PHẨM ĐẶT HÀNG",
        "san_pham": "Sản phẩm", "so_luong": "Số lượng", "don_gia": "Đơn giá", "thanh_tien": "Thành tiền",
        "them_sp": "➕ Thêm sản phẩm", "truoc_thue": "Trước thuế", "tong_sau_thue": "💰 TỔNG SAU THUẾ",
        "da_tt2": "💵 Đã thanh toán (đ)", "con_no": "Còn nợ", "ghi_chu": "📝 Ghi chú",
        "xac_nhan": "✅ XÁC NHẬN ĐƠN HÀNG", "dang_luu": "Đang lưu đơn hàng...",
        "luu_ok": "✅ Đơn hàng đã được lưu thành công!",
        "loi_chon_kh": "Vui lòng chọn khách hàng!", "loi_them_sp": "Vui lòng thêm ít nhất 1 sản phẩm!",
        "loi_luu": "Có lỗi xảy ra khi lưu đơn hàng!",
        "ds_don_hang": "📦 DANH SÁCH ĐƠN HÀNG", "tim_kiem": "🔍 Tìm kiếm",
        "tim_placeholder": "Tìm theo ID khách, tên...", "loc_khu_vuc": "Lọc khu vực", "tat_ca": "Tất cả",
        "tong_label": "Tổng:", "chua_don": "Chưa có đơn hàng nào.",
        "ds_sp": "🏷️ DANH SÁCH SẢN PHẨM", "sp_canh_bao": "sản phẩm cần chú ý tồn kho!",
        "ds_kh": "👥 DANH SÁCH KHÁCH HÀNG", "tim_kh": "🔍 Tìm kiếm khách hàng",
        "tim_kh_ph": "Tên, ID, khu vực...", "loc_kenh": "Lọc kênh", "tong_kh": "khách hàng",
        "ck_title": "🏪 PHÂN TÍCH CIRCLE K", "bieu_do_title": "📊 DOANH THU CIRCLE K THEO THÁNG",
        "thong_ke_po": "📋 THỐNG KÊ PO", "sku_title": "🏷️ PHÂN TÍCH SKU",
        "sku_chay": "🔥 TOP 3 MÃ BÁN CHẠY", "sku_cham": "⚠️ TOP 3 MÃ BÁN CHẬM",
        "ma_sku": "Mã SKU", "san_luong": "Sản lượng", "chon": "-- Chọn --",
        "ton_kho_bac": "Tồn kho Bắc", "ton_kho_nam": "Tồn kho Nam", "tong_ton": "Tổng tồn kho",
        "nhap_kho": "📥 NHẬP HÀNG VÀO KHO", "lich_su_nhap": "🕐 LỊCH SỬ NHẬP KHO",
    },
    "zh": {
        "title": "🚀 STEPAD — 销售管理系统",
        "logout": "退出登录", "login_btn": "登录",
        "login_user": "👤 用户名", "login_pass": "🔒 密码",
        "login_err": "用户名或密码错误！",
        "tab_dash": "🏠 仪表板", "tab_order": "📝 下单", "tab_don": "📦 订单",
        "tab_sp": "🏷️ 产品", "tab_kh": "👥 客户", "tab_ck": "🏪 Circle K",
        "tab_don_sale": "📦 我的订单",
        "tai_chinh": "💳 财务总览",
        "tong_dt": "总营业额", "da_nhan": "已收款", "no_thu": "待收款",
        "tong_ch": "门店总数", "ch_active": "活跃门店(3月)", "ty_le_phu": "覆盖率",
        "diem": "家", "dt_kenh": "📊 各渠道营业额",
        "tong": "合计", "mien_bac": "北区", "mien_nam": "南区",
        "tong_dt2": "总营业额", "da_tt": "已付款", "no": "欠款", "ky_gui": "寄售",
        "top_no": "🔴 欠款最多客户", "top_hieu_suat": "🟢 业绩最佳客户",
        "chua_du_lieu": "暂无数据", "chua_du_lieu_no": "暂无欠款数据",
        "thong_tin_don": "📋 订单信息",
        "khach_hang": "👤 客户 *", "khu_vuc_label": "📍 区域:",
        "ngay_don": "📅 订单日期", "loai_don": "📋 订单类型 *",
        "thue_suat": "💰 税率", "ma_po": "🔖 PO编号", "nhap_neu_co": "如有请填写...",
        "xuat_hd": "🧾 开具增值税发票？", "sp_dat_hang": "🛒 订购产品",
        "san_pham": "产品", "so_luong": "数量", "don_gia": "单价", "thanh_tien": "金额",
        "them_sp": "➕ 添加产品", "truoc_thue": "税前", "tong_sau_thue": "💰 税后总计",
        "da_tt2": "💵 已付款 (đ)", "con_no": "欠款", "ghi_chu": "📝 备注",
        "xac_nhan": "✅ 确认订单", "dang_luu": "正在保存订单...",
        "luu_ok": "✅ 订单保存成功！表单已重置。",
        "loi_chon_kh": "请选择客户！", "loi_them_sp": "请至少添加1个产品！",
        "loi_luu": "保存订单时出错，请重试！",
        "ds_don_hang": "📦 订单列表", "tim_kiem": "🔍 搜索",
        "tim_placeholder": "按客户ID、名称搜索...", "loc_khu_vuc": "按区域筛选", "tat_ca": "全部",
        "tong_label": "共:", "chua_don": "暂无订单。",
        "ds_sp": "🏷️ 产品列表", "sp_canh_bao": "个产品库存需注意！",
        "ds_kh": "👥 客户列表", "tim_kh": "🔍 搜索客户",
        "tim_kh_ph": "名称、ID、区域...", "loc_kenh": "按渠道筛选", "tong_kh": "位客户",
        "ck_title": "🏪 Circle K 分析", "bieu_do_title": "📊 Circle K 月度营业额",
        "thong_ke_po": "📋 PO统计", "sku_title": "🏷️ SKU分析",
        "sku_chay": "🔥 销量TOP 3", "sku_cham": "⚠️ 滞销TOP 3",
        "ma_sku": "SKU编码", "san_luong": "销量", "chon": "-- 请选择 --",
    }
}

def T(key):
    lang = st.session_state.get("lang", "vi")
    return LANG[lang].get(key, LANG["vi"].get(key, key))


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
        username = st.text_input(T("login_user"), placeholder="Nhập username...")
        password = st.text_input(T("login_pass"), type="password", placeholder="Nhập mật khẩu...")
        
        if st.button(T("login_btn"), use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.query_params["user"] = username
                st.session_state.username = username
                st.session_state.role = USERS[username]["role"]
                st.session_state.name = USERS[username]["name"]
                st.rerun()
            else:
                st.error(T("login_err"))

# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================
def fmt_currency(val):
    try:
        s = str(val).strip().replace(" ","").replace("đ","")
        if not s or s in ["-","N/A",""]: return "0 đ"
        # VN format: 1.234.567 hoặc 1.234,56
        if s.count(".") > 1:
            s = s.replace(".","").replace(",",".")
        elif "," in s and "." in s:
            if s.index(".") < s.index(","):
                s = s.replace(".","").replace(",",".")
            else:
                s = s.replace(",","")
        elif "," in s:
            parts = s.split(",")
            if len(parts[-1]) > 2:
                s = s.replace(",","")
            else:
                s = s.replace(",",".")
        return f"{float(s):,.0f} đ"
    except:
        return "0 đ"

def fmt_pct(val):
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return "0%"

# ── DỊCH TIÊU ĐỀ CỘT KHI HIỂN THỊ ─────────────────────────
COL_TRANSLATE = {
    # Don_Hang / Chi_tiet_don
    "ID Đơn":                    {"zh": "订单ID"},
    "Ngày lên đơn":              {"zh": "下单日期"},
    "ID Khách":                  {"zh": "客户ID"},
    "ID Khách hàng":             {"zh": "客户ID"},
    "Khu vực":                   {"zh": "区域"},
    "Tổng tiền PO":              {"zh": "PO总金额"},
    "Đã thanh toán":             {"zh": "已付款"},
    "Còn nợ":                    {"zh": "欠款"},
    "Tháng":                     {"zh": "月份"},
    "Trạng thái TT":             {"zh": "付款状态"},
    "Loại đơn":                  {"zh": "订单类型"},
    "Mã PO":                     {"zh": "PO编号"},
    # Chi_tiet_don
    "ID Chi tiết":               {"zh": "明细ID"},
    "SKU":                       {"zh": "SKU"},
    "SKU Sản phẩm":              {"zh": "SKU编码"},
    "Tên SP":                    {"zh": "产品名称"},
    "Tên sản phẩm":              {"zh": "产品名称"},
    "Số lượng":                  {"zh": "数量"},
    "Đơn giá":                   {"zh": "单价"},
    "Thuế suất":                 {"zh": "税率"},
    "Thành tiền trước thuế":     {"zh": "税前金额"},
    "Tiền thuế":                 {"zh": "税额"},
    "Tổng sau thuế":             {"zh": "税后总计"},
    "Kho xuất":                  {"zh": "出库仓"},
    # Khach_Hang
    "Tên cửa hàng":              {"zh": "门店名称"},
    "Địa chỉ":                   {"zh": "地址"},
    "Kênh phân phối":            {"zh": "渠道"},
    "Tổng doanh thu":            {"zh": "总营业额"},
    "Tỷ lệ TT":                  {"zh": "付款率"},
    # San_Pham
    "Giá Nha Trang":             {"zh": "芽庄价"},
    "Giá Circle K":              {"zh": "Circle K价"},
    "Giá MT":                    {"zh": "现代贸易价"},
    "Giá GT":                    {"zh": "传统贸易价"},
    "Trạng thái tồn kho":        {"zh": "库存状态"},
    "Tổng kho":                  {"zh": "总库存"},
    # Nhap_Kho
    "Ngày":                      {"zh": "日期"},
    "Số lượng":                  {"zh": "数量"},
    "Kho":                       {"zh": "仓库"},
    "Người nhập":                {"zh": "录入人"},
    "Ghi chú":                   {"zh": "备注"},
    "SL nhập Bắc":               {"zh": "北区入库"},
    "SL nhập Nam":               {"zh": "南区入库"},
    "SL xuất Bắc":               {"zh": "北区出库"},
    "SL xuất Nam":               {"zh": "南区出库"},
    "Tồn kho Bắc":               {"zh": "北区库存"},
    "Tồn kho Nam":               {"zh": "南区库存"},
    "Ngưỡng cảnh báo":           {"zh": "预警阈值"},
}

def translate_columns(df):
    """Rename cột để hiển thị theo ngôn ngữ hiện tại. Không đổi data gốc."""
    lang = st.session_state.get("lang", "vi")
    if lang == "vi":
        return df
    rename_map = {col: COL_TRANSLATE[col][lang]
                  for col in df.columns
                  if col in COL_TRANSLATE and lang in COL_TRANSLATE[col]}
    return df.rename(columns=rename_map)

def get_gia_theo_khu_vuc(df_sp, sku, khu_vuc):
    try:
        row = df_sp[df_sp['SKU Sản phẩm'] == sku].iloc[0]
        if khu_vuc in ["Nha Trang","Ký gửi"]: return float(str(row.get('Giá Nha Trang', 0)).replace(',','').replace('.',''))
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
if "lang" not in st.session_state:
    st.session_state.lang = "vi"
    if "user" in st.query_params:
        u = st.query_params["user"]
        if u in USERS:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.role = USERS[u]["role"]
            st.session_state.name = USERS[u]["name"]

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Header
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace; color:#00FF00; font-size:1.4rem; font-weight:700; letter-spacing:3px; padding: 8px 0;">
        {T("title")}
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
    <div style="text-align:right; color:#555555; font-size:0.8rem; padding-top:12px;">
        👤 {st.session_state.name} &nbsp;|&nbsp; 
        <span style="color:#00FF00">{st.session_state.role.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    col_lang, col_out = st.columns([1,1])
    with col_lang:
        if st.button("🌐 VI / 中文", key="lang_toggle"):
            st.session_state.lang = "zh" if st.session_state.get("lang","vi") == "vi" else "vi"
            st.rerun()
    with col_out:
        if st.button(T("logout"), key="logout"):
            st.session_state.logged_in = False
            st.rerun()

st.markdown("<hr style='border-color:#222222; margin: 0 0 16px 0;'>", unsafe_allow_html=True)

# ============================================================
# 6. TABS
# ============================================================
if st.session_state.role == "admin":
    tabs = st.tabs([T("tab_dash"), T("tab_order"), T("tab_don"), T("tab_sp"), T("tab_kh"), T("tab_ck")])
    t_dash, t_order, t_don, t_sp, t_kh, t_ck = tabs
else:
    tabs = st.tabs([T("tab_order"), T("tab_don_sale")])
    t_order, t_don = tabs

# ============================================================
# TAB: DASHBOARD
# ============================================================

def parse_num(s):
    """Parse số VN format (1.234.567) hoặc bình thường về float."""
    try:
        s = str(s).strip().replace(" ", "").replace("đ", "").replace("\xa0", "")
        if not s or s in ["-", "N/A", "", "nan", "None"]:
            return 0.0
        if s.count(".") > 1:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." in s:
            if s.index(".") < s.index(","):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "," in s:
            parts = s.split(",")
            s = s.replace(",", "") if len(parts[-1]) > 2 else s.replace(",", ".")
        elif "." in s:
            parts = s.split(".")
            if len(parts[-1]) > 2:
                s = s.replace(".", "")
        return float(s)
    except:
        return 0.0

if st.session_state.role == "admin":
    with t_dash:
        with st.spinner("Đang tải dữ liệu..."):
            df_dash    = load_sheet("Dashboard")
            df_kh      = load_sheet("Khach_Hang")
            df_chitiet = load_sheet("Chi_tiet_don")
            df_donhang = load_sheet("Don_Hang")

        # ── BỘ LỌC THÁNG / NĂM ────────────────────────────────
        st.markdown('<div class="section-header">🗓️ BỘ LỌC THỜI GIAN</div>', unsafe_allow_html=True)

        # Lấy danh sách năm & tháng từ Chi_tiet_don
        available_years = []
        available_months_map = {}   # year → sorted list of months (int)

        if not df_chitiet.empty:
            # Chuẩn hóa cột Tháng (dạng "T1", "1", "Tháng 1", v.v.)
            col_thang_ct = next((c for c in df_chitiet.columns if "tháng" in c.lower() or c.lower() == "tháng"), None)
            col_ngay_ct  = next((c for c in df_chitiet.columns if "ngày" in c.lower() or "ngay" in c.lower()), None)

            # Ưu tiên dùng cột Ngày để trích xuất năm, tháng
            if col_ngay_ct:
                df_chitiet["_parsed_date"] = pd.to_datetime(
                    df_chitiet[col_ngay_ct], dayfirst=True, errors="coerce"
                )
                df_chitiet["_year"]  = df_chitiet["_parsed_date"].dt.year
                df_chitiet["_month"] = df_chitiet["_parsed_date"].dt.month
            elif col_thang_ct:
                # Chỉ có cột Tháng (không có năm) → lấy năm hiện tại
                def parse_thang(x):
                    s = str(x).strip().upper().replace("THÁNG","").replace("T","").strip()
                    try: return int(s)
                    except: return None
                df_chitiet["_month"] = df_chitiet[col_thang_ct].apply(parse_thang)
                df_chitiet["_year"]  = datetime.now().year

            if "_year" in df_chitiet.columns:
                df_chitiet["_year"] = pd.to_numeric(df_chitiet["_year"], errors="coerce")
                df_chitiet["_month"] = pd.to_numeric(df_chitiet["_month"], errors="coerce")
                valid = df_chitiet.dropna(subset=["_year", "_month"])
                available_years = sorted(valid["_year"].astype(int).unique().tolist(), reverse=True)
                for yr in available_years:
                    available_months_map[yr] = sorted(
                        valid[valid["_year"] == yr]["_month"].astype(int).unique().tolist()
                    )

        MONTH_NAMES_VI = {1:"Tháng 1",2:"Tháng 2",3:"Tháng 3",4:"Tháng 4",
                          5:"Tháng 5",6:"Tháng 6",7:"Tháng 7",8:"Tháng 8",
                          9:"Tháng 9",10:"Tháng 10",11:"Tháng 11",12:"Tháng 12"}
        MONTH_NAMES_ZH = {1:"1月",2:"2月",3:"3月",4:"4月",5:"5月",6:"6月",
                          7:"7月",8:"8月",9:"9月",10:"10月",11:"11月",12:"12月"}

        filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])

        with filter_col1:
            year_options = ["Tất cả năm"] + [str(y) for y in available_years] if available_years else ["Tất cả năm"]
            sel_year_str = st.selectbox(
                "📅 Năm" if st.session_state.get("lang","vi") == "vi" else "📅 年份",
                year_options, key="dash_year"
            )
        with filter_col2:
            sel_year = int(sel_year_str) if sel_year_str != "Tất cả năm" else None
            if sel_year and sel_year in available_months_map:
                month_list = available_months_map[sel_year]
            elif available_years:
                all_months = set()
                for ml in available_months_map.values():
                    all_months.update(ml)
                month_list = sorted(all_months)
            else:
                month_list = list(range(1, 13))

            if st.session_state.get("lang","vi") == "vi":
                month_display = ["Tất cả tháng"] + [MONTH_NAMES_VI[m] for m in month_list]
            else:
                month_display = ["全部月份"] + [MONTH_NAMES_ZH[m] for m in month_list]

            sel_month_label = st.selectbox(
                "📅 Tháng" if st.session_state.get("lang","vi") == "vi" else "📅 月份",
                month_display, key="dash_month"
            )
            sel_month = None
            if sel_month_label not in ["Tất cả tháng", "全部月份"]:
                # lấy số tháng từ label
                for m, name in (MONTH_NAMES_VI if st.session_state.get("lang","vi") == "vi" else MONTH_NAMES_ZH).items():
                    if name == sel_month_label:
                        sel_month = m
                        break

        with filter_col3:
            if sel_year or sel_month:
                filter_info = []
                if sel_year: filter_info.append(f"Năm {sel_year}")
                if sel_month: filter_info.append(MONTH_NAMES_VI.get(sel_month, ""))
                st.markdown(
                    f"<div style='padding-top:28px; color:#00FF00; font-family:JetBrains Mono; font-size:0.8rem;'>"
                    f"🔍 Đang xem: <b>{' — '.join(filter_info)}</b></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='padding-top:28px; color:#555; font-size:0.8rem;'>🔍 Đang xem: Toàn bộ thời gian</div>",
                    unsafe_allow_html=True
                )

        st.markdown("<hr style='border-color:#1a1a1a; margin:8px 0 16px 0;'>", unsafe_allow_html=True)

        # ── LỌC DỮ LIỆU CHI_TIET_DON THEO BỘ LỌC ─────────────
        use_filtered = not df_chitiet.empty and "_year" in df_chitiet.columns

        if use_filtered:
            df_ct_filtered = df_chitiet.copy()
            if sel_year:
                df_ct_filtered = df_ct_filtered[df_ct_filtered["_year"] == sel_year]
            if sel_month:
                df_ct_filtered = df_ct_filtered[df_ct_filtered["_month"] == sel_month]
        else:
            df_ct_filtered = df_chitiet.copy() if not df_chitiet.empty else pd.DataFrame()

        # Cột tiền trong Chi_tiet_don
        col_truoc_thue = next((c for c in df_chitiet.columns if "trước thuế" in c.lower() or "truoc thue" in c.lower()), None)
        col_sau_thue   = next((c for c in df_chitiet.columns if "sau thuế" in c.lower() or "sau thue" in c.lower()), None)
        col_tien_thue  = next((c for c in df_chitiet.columns if c.lower().startswith("tiền thuế") or c.lower() == "tiền thuế"), None)

        def sum_col(df, col):
            if col and col in df.columns and not df.empty:
                return df[col].apply(parse_num).sum()
            return 0.0

        # Lấy khu vực từ Chi_tiet_don
        col_kv_ct = next((c for c in df_chitiet.columns if "khu vực" in c.lower()), None)

        def sum_by_kenh(kenh_keyword):
            if df_ct_filtered.empty or col_kv_ct is None or col_sau_thue is None:
                return 0.0
            mask = df_ct_filtered[col_kv_ct].astype(str).str.contains(kenh_keyword, case=False, na=False)
            return df_ct_filtered[mask][col_sau_thue].apply(parse_num).sum()

        # ── TÀI CHÍNH TỔNG QUAN (từ Chi_tiet_don nếu có bộ lọc, từ Dashboard sheet nếu không) ──
        st.markdown('<div class="section-header">💳 TÀI CHÍNH TỔNG QUAN</div>', unsafe_allow_html=True)

        show_filtered_metrics = use_filtered and (sel_year or sel_month)

        if show_filtered_metrics:
            # Tính từ Chi_tiet_don đã lọc
            tong_dt_val  = sum_col(df_ct_filtered, col_sau_thue)

            # Lấy từ Don_Hang nếu có bộ lọc
            df_don_filtered = df_donhang.copy() if not df_donhang.empty else pd.DataFrame()
            if not df_don_filtered.empty:
                col_ngay_don = next((c for c in df_don_filtered.columns if "ngày" in c.lower()), None)
                col_thang_don = next((c for c in df_don_filtered.columns if "tháng" in c.lower() or c.lower() == "tháng"), None)
                if col_ngay_don:
                    df_don_filtered["_parsed_date"] = pd.to_datetime(df_don_filtered[col_ngay_don], dayfirst=True, errors="coerce")
                    df_don_filtered["_year"]  = df_don_filtered["_parsed_date"].dt.year
                    df_don_filtered["_month"] = df_don_filtered["_parsed_date"].dt.month
                    if sel_year:
                        df_don_filtered = df_don_filtered[df_don_filtered["_year"] == sel_year]
                    if sel_month:
                        df_don_filtered = df_don_filtered[df_don_filtered["_month"] == sel_month]
                elif col_thang_don:
                    def parse_thang2(x):
                        s = str(x).strip().upper().replace("THÁNG","").replace("T","").strip()
                        try: return int(s)
                        except: return None
                    df_don_filtered["_month"] = df_don_filtered[col_thang_don].apply(parse_thang2)
                    if sel_month:
                        df_don_filtered = df_don_filtered[df_don_filtered["_month"] == sel_month]

            col_da_tt_don = next((c for c in df_donhang.columns if "đã thanh toán" in c.lower() or "đã tt" in c.lower()), None)
            col_con_no_don = next((c for c in df_donhang.columns if "còn nợ" in c.lower() or "con no" in c.lower()), None)
            da_tt_val = sum_col(df_don_filtered, col_da_tt_don)
            con_no_val = sum_col(df_don_filtered, col_con_no_don)
            if da_tt_val == 0 and con_no_val == 0:
                # Fallback: tính từ tong_dt
                da_tt_val = tong_dt_val * 0.0
                con_no_val = tong_dt_val

            try:
                col1, col2, col3 = st.columns(3)
                with col1: st.metric(T("tong_dt"), fmt_currency(tong_dt_val))
                with col2: st.metric(T("da_nhan"), fmt_currency(da_tt_val))
                with col3: st.metric(T("no_thu"), fmt_currency(con_no_val))
            except Exception as e:
                st.error(f"Lỗi tính metrics: {e}")
        else:
            # Toàn bộ: đọc từ Dashboard sheet (giữ nguyên logic cũ)
            if not df_dash.empty:
                try:
                    row = df_dash.iloc[0]
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1: st.metric(T("tong_dt"), fmt_currency(row.iloc[0]))
                    with col2: st.metric(T("da_nhan"), fmt_currency(row.iloc[1]))
                    with col3: st.metric(T("no_thu"), fmt_currency(row.iloc[2]))
                    with col4: st.metric(T("tong_ch"), f'{row.iloc[3]} {T("diem")}')
                    with col5: st.metric(T("ch_active"), f'{row.iloc[4]} {T("diem")}')
                    with col6: st.metric(T("ty_le_phu"), f"{row.iloc[5]}")
                except Exception as e:
                    st.error(f"Lỗi đọc Dashboard: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── DOANH THU THEO KÊNH ────────────────────────────────
        st.markdown('<div class="section-header">📊 DOANH THU THEO KÊNH</div>', unsafe_allow_html=True)

        if show_filtered_metrics and use_filtered and col_kv_ct and col_sau_thue:
            # Tính từ Chi_tiet_don đã lọc
            try:
                ck_val  = sum_by_kenh("Circle K|CK")
                mt_val  = sum_by_kenh("MT|Modern Trade")
                gt_val  = sum_by_kenh("GT|General Trade")
                nt_val  = sum_by_kenh("Nha Trang|NT|Ký gửi")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🏪 CIRCLE K**")
                    st.metric(T("tong"), fmt_currency(ck_val))
                    # Bắc / Nam từ cột Kho xuất
                    col_kho = next((c for c in df_ct_filtered.columns if "kho" in c.lower()), None)
                    if col_kho:
                        mask_ck = df_ct_filtered[col_kv_ct].astype(str).str.contains("Circle K|CK", case=False, na=False)
                        ck_df = df_ct_filtered[mask_ck]
                        bac_val = ck_df[ck_df[col_kho].astype(str).str.contains("Bắc|bac|Bac", case=False, na=False)][col_sau_thue].apply(parse_num).sum()
                        nam_val = ck_df[ck_df[col_kho].astype(str).str.contains("Nam|nam", case=False, na=False)][col_sau_thue].apply(parse_num).sum()
                        st.metric(T("mien_bac"), fmt_currency(bac_val))
                        st.metric(T("mien_nam"), fmt_currency(nam_val))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🏬 MODERN TRADE**")
                    st.metric(T("tong_dt2"), fmt_currency(mt_val))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🛒 GENERAL TRADE**")
                    st.metric(T("tong_dt2"), fmt_currency(gt_val))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("**🌊 NHA TRANG**")
                    st.metric(T("ky_gui"), fmt_currency(nt_val))
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Lỗi tính doanh thu kênh: {e}")
        else:
            # Toàn bộ: đọc từ Dashboard sheet
            if not df_dash.empty:
                try:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.markdown("**🏪 CIRCLE K**")
                        st.metric(T("tong"), fmt_currency(df_dash.iloc[4, 0]))
                        st.metric(T("mien_bac"), fmt_currency(df_dash.iloc[4, 1]))
                        st.metric(T("mien_nam"), fmt_currency(df_dash.iloc[4, 2]))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.markdown("**🏬 MODERN TRADE**")
                        st.metric(T("tong_dt2"), fmt_currency(df_dash.iloc[7, 0]))
                        st.metric(T("da_tt"), fmt_currency(df_dash.iloc[7, 1]))
                        st.metric(T("no"), fmt_currency(df_dash.iloc[7, 2]))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.markdown("**🛒 GENERAL TRADE**")
                        st.metric(T("tong_dt2"), fmt_currency(df_dash.iloc[9, 0]))
                        st.metric(T("da_tt"), fmt_currency(df_dash.iloc[9, 1]))
                        st.metric(T("no"), fmt_currency(df_dash.iloc[9, 2]))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col4:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.markdown("**🌊 NHA TRANG**")
                        st.metric(T("ky_gui"), fmt_currency(df_dash.iloc[13, 0]))
                        st.metric(T("da_tt"), fmt_currency(df_dash.iloc[13, 1]))
                        st.metric(T("no"), fmt_currency(df_dash.iloc[13, 2]))
                        st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Đang chờ dữ liệu kênh phân phối...")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── BIỂU ĐỒ DOANH THU THEO THÁNG (từ Chi_tiet_don) ────
        if use_filtered and col_sau_thue and col_kv_ct:
            st.markdown('<div class="section-header">📈 BIỂU ĐỒ DOANH THU THEO THÁNG</div>', unsafe_allow_html=True)
            try:
                df_trend = df_chitiet.copy()
                if sel_year:
                    df_trend = df_trend[df_trend["_year"] == sel_year]
                if not sel_month and not df_trend.empty:
                    df_trend["_val"] = df_trend[col_sau_thue].apply(parse_num)
                    df_trend_grp = df_trend.groupby(["_year", "_month", col_kv_ct])["_val"].sum().reset_index()
                    df_trend_grp.columns = ["Năm", "Tháng số", "Kênh", "Doanh thu"]
                    # Tạo nhãn tháng có năm để phân biệt (ví dụ: T3/2025 vs T3/2026)
                    if not sel_year:
                        df_trend_grp["Tháng"] = df_trend_grp.apply(
                            lambda r: f"T{int(r['Tháng số'])}/{int(r['Năm'])}", axis=1
                        )
                    else:
                        df_trend_grp["Tháng"] = df_trend_grp["Tháng số"].apply(lambda m: f"T{int(m)}")
                    # Sắp xếp đúng thứ tự thời gian
                    df_trend_grp = df_trend_grp.sort_values(["Năm", "Tháng số"])
                    fig_trend = px.bar(
                        df_trend_grp, x="Tháng", y="Doanh thu", color="Kênh",
                        barmode="group",
                        color_discrete_sequence=["#00FF00","#006400","#00A300","#88FF88"],
                    )
                    fig_trend.update_layout(
                        height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(tickfont=dict(color="#888888")),
                        yaxis=dict(gridcolor="#222222", tickfont=dict(color="#888888")),
                        legend=dict(font=dict(color="#ffffff"), orientation="h", y=1.1),
                        margin=dict(l=0, r=0, t=20, b=0),
                    )
                    fig_trend.update_traces(hovertemplate="%{y:,.0f} đ")
                    st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e:
                st.caption(f"Chưa thể vẽ biểu đồ: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Cảnh báo nợ & hiệu suất
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown('<div class="section-header">🔴 TOP KHÁCH NỢ NHIỀU</div>', unsafe_allow_html=True)
            if not df_kh.empty and 'Còn nợ' in df_kh.columns and 'Tên cửa hàng' in df_kh.columns:
                try:
                    df_no = df_kh.copy()
                    df_no['_no_num'] = pd.to_numeric(
                        df_no['Còn nợ'].astype(str).str.replace('.','',regex=False).str.replace(',','.',regex=False),
                        errors='coerce').fillna(0)
                    df_no = df_no[df_no['_no_num'] > 0]
                    df_no = df_no.nlargest(5, '_no_num')[['Tên cửa hàng', '_no_num', 'Khu vực']]
                    df_no = df_no.rename(columns={'_no_num': 'Còn nợ'})
                    df_no['Còn nợ'] = df_no['Còn nợ'].apply(fmt_currency)
                    st.dataframe(translate_columns(df_no), use_container_width=True, hide_index=True)
                except:
                    st.info(T("chua_du_lieu_no"))
            else:
                st.info(T("chua_du_lieu"))

        with col_right:
            st.markdown('<div class="section-header">🟢 TOP KHÁCH HIỆU SUẤT TỐT</div>', unsafe_allow_html=True)
            if not df_kh.empty:
                try:
                    # Detect cột doanh thu linh hoạt (không phân biệt hoa thường, khoảng trắng)
                    cols_lower = {c: c.lower().strip() for c in df_kh.columns}
                    col_dt = next((c for c, cl in cols_lower.items() 
                                   if 'doanh thu' in cl or 'tổng' in cl), None)
                    col_tt = next((c for c, cl in cols_lower.items() 
                                   if 'đã thanh toán' in cl or 'đã tt' in cl or ('thanh toán' in cl and 'đã' in cl)), None)
                    if col_dt is None:
                        # fallback: tìm cột số có giá trị lớn nhất
                        numeric_cols = df_kh.select_dtypes(include='number').columns.tolist()
                        if numeric_cols:
                            col_dt = numeric_cols[0]
                    if col_dt:
                        df_perf = df_kh.copy()
                        df_perf[col_dt] = pd.to_numeric(df_perf[col_dt].astype(str).str.replace('.','').str.replace(',','.'), errors='coerce').fillna(0)
                        df_perf = df_perf[df_perf[col_dt] > 0]
                        show_cols = ["Tên cửa hàng", col_dt]
                        if col_tt:
                            df_perf[col_tt] = pd.to_numeric(df_perf[col_tt].astype(str).str.replace('.','').str.replace(',','.'), errors='coerce').fillna(0)
                            df_perf["Tỷ lệ TT"] = (df_perf[col_tt] / df_perf[col_dt] * 100).round(1).astype(str) + "%"
                            show_cols.append("Tỷ lệ TT")
                        df_perf = df_perf.nlargest(5, col_dt)[show_cols]
                        df_perf = df_perf.rename(columns={col_dt: "Tổng doanh thu"})
                        df_perf["Tổng doanh thu"] = df_perf["Tổng doanh thu"].apply(fmt_currency)
                        st.dataframe(translate_columns(df_perf), use_container_width=True, hide_index=True)
                    else:
                        st.info("Không tìm thấy cột doanh thu")
                except Exception as e:
                    st.info(f"Chưa có dữ liệu hiệu suất: {e}")
            else:
                st.info(T("chua_du_lieu"))

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
        st.success(T("luu_ok"))
        st.session_state.order_success = False

    # ---- THÔNG TIN ĐƠN HÀNG ----
    st.markdown('<div class="section-header">📋 THÔNG TIN ĐƠN HÀNG</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        ds_khach = df_kh['ID Khách'].tolist() if 'ID Khách' in df_kh.columns else []
        ds_ten = df_kh['Tên cửa hàng'].tolist() if 'Tên cửa hàng' in df_kh.columns else []
        ds_diachi = df_kh['Địa chỉ'].tolist() if 'Địa chỉ' in df_kh.columns else ['' for _ in ds_khach]
        ds_khach_display = [f"{id} — {ten} — {dc}" for id, ten, dc in zip(ds_khach, ds_ten, ds_diachi)]
        khach_selected = st.selectbox(T("khach_hang"), ds_khach_display, key=f"sel_khach_{st.session_state.form_key}")
        id_khach = khach_selected.split(" — ")[0] if khach_selected else ""
        khu_vuc = get_khu_vuc(id_khach)
        st.markdown(f"<small style='color:#00FF00'>📍 Khu vực: <b>{khu_vuc}</b></small>", unsafe_allow_html=True)

    with col2:
        ngay_don = st.date_input(T("ngay_don"), value=date.today(), key=f"ngay_{st.session_state.form_key}")

    col3, col4, col5 = st.columns(3)
    with col3:
        loai_don = st.selectbox(T("loai_don"), [T("ky_gui"), "Bổ sung hàng", "Circle K"], key=f"loai_{st.session_state.form_key}")
    with col4:
        thue_suat = st.selectbox(T("thue_suat"), [0.0, 0.08, 0.10], format_func=lambda x: f"{int(x*100)}%", key=f"thue_{st.session_state.form_key}")
    with col5:
        ma_po = st.text_input(T("ma_po"), placeholder=T("nhap_neu_co"), key=f"mapo_{st.session_state.form_key}")

    tt_hd = st.selectbox(T("xuat_hd"), ["Không xuất HĐ", "Có xuất HĐ"], key=f"tthd_{st.session_state.form_key}")

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
                [T("chon")] + ds_sku_display,
                key=f"sku_{st.session_state.form_key}_{i}",
                label_visibility="collapsed"
            )
        with col_sl:
            sl = st.number_input("SL", min_value=1, value=1, key=f"sl_{st.session_state.form_key}_{i}", label_visibility="collapsed")

        sku_code = sku_sel.split(" — ")[0] if sku_sel != T("chon") else ""
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

    if st.button(T("them_sp"), key=f"add_sku_{st.session_state.form_key}"):
        st.session_state.order_items.append({"sku": "", "sl": 1})
        st.rerun()

    # ---- TỔNG KẾT ----
    st.markdown("<hr style='border-color:#222222; margin:16px 0'>", unsafe_allow_html=True)

    # Giảm giá đặc biệt
    ap_dung_giam = st.checkbox("🏷️ Áp dụng giảm giá đặc biệt", value=False, key=f"giam_{st.session_state.form_key}")
    pct_giam = 0
    if ap_dung_giam:
        pct_giam = st.number_input("% Giảm giá", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key=f"pct_giam_{st.session_state.form_key}")

    tien_giam = tong_truoc_thue * (pct_giam / 100)
    tong_sau_giam = tong_truoc_thue - tien_giam
    tien_thue = tong_sau_giam * thue_suat
    tong_sau_thue = tong_sau_giam + tien_thue

    col_s1, col_s2, col_s3, col_s4 = st.columns(4) if ap_dung_giam else st.columns([1,1,0.01,1])
    with col_s1: st.metric(T("truoc_thue"), fmt_currency(tong_truoc_thue))
    if ap_dung_giam:
        with col_s2: st.metric(f"Giảm {pct_giam}%", f"-{fmt_currency(tien_giam)}")
        with col_s3: st.metric(f"Thuế {int(thue_suat*100)}%", fmt_currency(tien_thue))
        with col_s4: st.metric(T("tong_sau_thue"), fmt_currency(tong_sau_thue))
    else:
        with col_s2: st.metric(f"Thuế {int(thue_suat*100)}%", fmt_currency(tien_thue))
        with col_s4: st.metric(T("tong_sau_thue"), fmt_currency(tong_sau_thue))

    col_tt1, col_tt2 = st.columns(2)
    with col_tt1:
        da_thanh_toan = st.number_input(T("da_tt2"), min_value=0, value=0, step=100000, key=f"datt_{st.session_state.form_key}")
    with col_tt2:
        con_no = tong_sau_thue - da_thanh_toan
        st.metric(T("con_no"), fmt_currency(con_no))

    ghi_chu = st.text_area(T("ghi_chu"), placeholder="Ghi chú đặc biệt cho đơn hàng này...", height=80, key=f"ghichu_{st.session_state.form_key}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(T("xac_nhan"), use_container_width=True, key="submit_order"):
        if not id_khach:
            st.error(T("loi_chon_kh"))
        elif not items_data:
            st.error(T("loi_them_sp"))
        else:
            with st.spinner(T("dang_luu")):
                now = datetime.now()
                id_don = f"DH{now.strftime('%Y%m%d%H%M%S')}"
                thang = ngay_don.strftime("%m/%Y")
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

                # Ghi vào Chi_tiet_don
                if success:
                    for i, item in enumerate(items_data):
                        id_ct = f"CT{now.strftime('%Y%m%d%H%M%S')}{i+1:02d}"
                        row_ct = [
                            id_ct,
                            id_don,
                            item["sku"],
                            "",
                            item["sl"],
                            item["don_gia"],
                            thue_suat,
                            item["thanh_tien"],
                            item["thanh_tien"] * thue_suat,
                            item["thanh_tien"] * (1 + thue_suat),
                            khu_vuc,
                            kho,
                            thang,
                            str(ngay_don)
                        ]
                        append_row("Chi_tiet_don", row_ct)

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
                    st.error(T("loi_luu"))

# ============================================================
# TAB: ĐƠN HÀNG
# ============================================================
with t_don:
    st.markdown('<div class="section-header">📦 DANH SÁCH ĐƠN HÀNG</div>', unsafe_allow_html=True)
    with st.spinner("Đang tải..."):
        df_don = load_sheet("Don_Hang")
    
    if not df_don.empty:
        if st.session_state.role == "sale":
            df_don = df_don[df_don.get('Nhân viên', '') == st.session_state.name]
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search = st.text_input(T("tim_kiem"), placeholder=T("tim_placeholder"))
        with col_f2:
            if 'Khu vực' in df_don.columns:
                kv_filter = st.selectbox(T("loc_khu_vuc"), [T("tat_ca")] + df_don['Khu vực'].dropna().unique().tolist())
        
        if search:
            mask = df_don.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
            df_don = df_don[mask]
        if 'Khu vực' in df_don.columns and kv_filter != T("tat_ca"):
            df_don = df_don[df_don['Khu vực'] == kv_filter]
        
        st.dataframe(translate_columns(df_don), use_container_width=True, hide_index=True)
        st.caption(f'{T("tong_label")} {len(df_don)}')
    else:
        st.info(T("chua_don"))

# ============================================================
# TAB: SẢN PHẨM (Admin only)
# ============================================================
if st.session_state.role == "admin":
    with t_sp:
        with st.spinner("Đang tải..."):
            df_sp_full = load_sheet("San_Pham")

        # ── CẢNH BÁO TỒN KHO ──────────────────────────────────
        if not df_sp_full.empty and 'Trạng thái tồn kho' in df_sp_full.columns:
            df_canh_bao = df_sp_full[
                df_sp_full['Trạng thái tồn kho'].astype(str).str.contains('Cảnh báo|Hết', na=False)
            ]
            if not df_canh_bao.empty:
                st.warning(f"⚠️ **{len(df_canh_bao)} sản phẩm** cần chú ý tồn kho!")

        # ── BẢNG TỒN KHO TỔNG QUAN ────────────────────────────
        st.markdown('<div class="section-header">📦 TỒN KHO HIỆN TẠI</div>', unsafe_allow_html=True)

        if not df_sp_full.empty:
            # Chọn cột hiển thị tồn kho
            ton_kho_cols = ['SKU Sản phẩm', 'Tên sản phẩm',
                            'SL nhập Bắc', 'SL xuất Bắc', 'Tồn kho Bắc',
                            'SL nhập Nam', 'SL xuất Nam', 'Tồn kho Nam',
                            'Tổng kho', 'Ngưỡng cảnh báo', 'Trạng thái tồn kho']
            show_cols = [c for c in ton_kho_cols if c in df_sp_full.columns]

            df_ton_kho = df_sp_full[show_cols].copy() if show_cols else df_sp_full.copy()

            # Tô màu theo trạng thái
            def color_status(val):
                if '🔴' in str(val) or 'Hết' in str(val):
                    return 'color: #FF4444'
                if '🟡' in str(val) or 'Cảnh báo' in str(val):
                    return 'color: #FF8800'
                if '🟢' in str(val) or 'Còn' in str(val):
                    return 'color: #00FF00'
                return ''

            st.dataframe(
                translate_columns(df_ton_kho),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── FORM NHẬP KHO ──────────────────────────────────────
        st.markdown('<div class="section-header">📥 NHẬP HÀNG VÀO KHO</div>', unsafe_allow_html=True)

        if not df_sp_full.empty:
            col_nk1, col_nk2 = st.columns([2, 1])
            with col_nk1:
                ds_sku_sp = df_sp_full['SKU Sản phẩm'].tolist() if 'SKU Sản phẩm' in df_sp_full.columns else []
                ds_ten_sp2 = df_sp_full['Tên sản phẩm'].tolist() if 'Tên sản phẩm' in df_sp_full.columns else []
                ds_sku_nk = [f"{s} — {t}" for s, t in zip(ds_sku_sp, ds_ten_sp2)]
                sku_nhap = st.selectbox("🏷️ Chọn sản phẩm *", [T("chon")] + ds_sku_nk, key="nk_sku")
            with col_nk2:
                kho_nhap = st.selectbox("🏭 Kho nhập *", ["Bắc", "Nam"], key="nk_kho")

            col_nk3, col_nk4 = st.columns([1, 2])
            with col_nk3:
                sl_nhap = st.number_input("📦 Số lượng nhập *", min_value=1, value=1, key="nk_sl")
            with col_nk4:
                ghi_chu_nk = st.text_input("📝 Ghi chú", placeholder="Nhập lý do, nguồn hàng...", key="nk_ghichu")

            # Hiển thị tồn kho hiện tại của SP được chọn
            if sku_nhap != T("chon"):
                sku_code_nk = sku_nhap.split(" — ")[0]
                row_sp = df_sp_full[df_sp_full['SKU Sản phẩm'] == sku_code_nk]
                if not row_sp.empty:
                    r = row_sp.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        ton_bac = r.get('Tồn kho Bắc', 0)
                        st.metric("Tồn kho Bắc hiện tại", f"{ton_bac}")
                    with c2:
                        ton_nam = r.get('Tồn kho Nam', 0)
                        st.metric("Tồn kho Nam hiện tại", f"{ton_nam}")
                    with c3:
                        tong_ton = r.get('Tổng kho', 0)
                        st.metric("Tổng tồn kho", f"{tong_ton}")

            if st.button("✅ XÁC NHẬN NHẬP KHO", key="btn_nhap_kho"):
                if sku_nhap == T("chon"):
                    st.error("Vui lòng chọn sản phẩm!")
                elif sl_nhap <= 0:
                    st.error("Số lượng phải lớn hơn 0!")
                else:
                    sku_code_nk = sku_nhap.split(" — ")[0]
                    ten_sp_nk = sku_nhap.split(" — ")[1] if " — " in sku_nhap else ""
                    ngay_nk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_nk = [
                        ngay_nk,
                        sku_code_nk,
                        ten_sp_nk,
                        sl_nhap,
                        kho_nhap,
                        st.session_state.name,
                        ghi_chu_nk
                    ]
                    if append_row("Nhap_Kho", row_nk):
                        st.success(f"✅ Đã nhập **{sl_nhap}** sản phẩm **{sku_code_nk}** vào kho **{kho_nhap}**!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Có lỗi khi ghi dữ liệu, vui lòng thử lại!")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── LỊCH SỬ NHẬP KHO GẦN NHẤT ────────────────────────
        st.markdown('<div class="section-header">🕐 LỊCH SỬ NHẬP KHO</div>', unsafe_allow_html=True)
        df_nhap_kho = load_sheet("Nhap_Kho")
        if not df_nhap_kho.empty:
            st.dataframe(
                translate_columns(df_nhap_kho.tail(10).iloc[::-1]),
                use_container_width=True, hide_index=True
            )
            st.caption(f"Hiển thị 10 lần nhập gần nhất | Tổng: {len(df_nhap_kho)} lần")
        else:
            st.info("Chưa có lịch sử nhập kho.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── DANH SÁCH SẢN PHẨM ĐẦY ĐỦ ────────────────────────
        st.markdown('<div class="section-header">🏷️ DANH SÁCH SẢN PHẨM ĐẦY ĐỦ</div>', unsafe_allow_html=True)
        if not df_sp_full.empty:
            st.dataframe(translate_columns(df_sp_full), use_container_width=True, hide_index=True)

    # ============================================================
    # TAB: KHÁCH HÀNG (Admin only)
    # ============================================================
    with t_kh:
        st.markdown('<div class="section-header">👥 DANH SÁCH KHÁCH HÀNG</div>', unsafe_allow_html=True)
        with st.spinner("Đang tải..."):
            df_kh_full = load_sheet("Khach_Hang")
        if not df_kh_full.empty:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_kh = st.text_input(T("tim_kh"), placeholder=T("tim_kh_ph"))
            with col_f2:
                if 'Kênh phân phối' in df_kh_full.columns:
                    kenh_filter = st.selectbox(T("loc_kenh"), [T("tat_ca")] + df_kh_full['Kênh phân phối'].dropna().unique().tolist())
            
            df_display = df_kh_full.copy()
            if search_kh:
                mask = df_display.astype(str).apply(lambda x: x.str.contains(search_kh, case=False)).any(axis=1)
                df_display = df_display[mask]
            if 'Kênh phân phối' in df_kh_full.columns and kenh_filter != T("tat_ca"):
                df_display = df_display[df_display['Kênh phân phối'] == kenh_filter]
            
            st.dataframe(translate_columns(df_display), use_container_width=True, hide_index=True)
            st.caption(f'{T("tong_label")} {len(df_display)} {T("tong_kh")}')

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
                        title={'text': T("bieu_do_title"), 'x': 0.5, 'font': {'color': '#00FF00', 'size': 14}},
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

        # ---- DEBUG PANEL (ẩn, chỉ admin) ----
        with st.expander("🔧 Debug: Xem nội dung Dashboard sheet (để xác định đúng row/col)"):
            if not df_dash_ck.empty:
                st.caption(f"Kích thước: {df_dash_ck.shape[0]} hàng × {df_dash_ck.shape[1]} cột")
                st.caption(f"Tên cột: {list(df_dash_ck.columns)}")
                st.dataframe(df_dash_ck.reset_index(), use_container_width=True)
            else:
                st.warning("Dashboard sheet rỗng!")

        if not df_dash_ck.empty:
            def to_num_po(v):
                s = str(v).strip().replace(" ","").replace("đ","")
                if not s or s in ["-","N/A",""]: return 0
                if s.count(".") > 1:
                    s = s.replace(".","").replace(",",".")
                elif "," in s and "." in s:
                    if s.index(".") < s.index(","):
                        s = s.replace(".","").replace(",",".")
                    else:
                        s = s.replace(",","")
                elif "," in s:
                    parts = s.split(",")
                    s = s.replace(",","") if len(parts[-1]) > 2 else s.replace(",",".")
                elif "." in s:
                    parts = s.split(".")
                    if len(parts[-1]) > 2: s = s.replace(".","")
                try: return float(s)
                except: return 0

            try:
                col1, col2 = st.columns(2)
                n_rows = df_dash_ck.shape[0]
                n_cols = df_dash_ck.shape[1]

                def safe_iloc(r, c):
                    if r < n_rows and c < n_cols:
                        return df_dash_ck.iloc[r, c]
                    return 0

                with col1:
                    st.markdown("**📍 Miền Nam**")
                    c1, c2, c3, c4 = st.columns(4)
                    # Sheets hàng 19 = iloc[17] (trừ 1 header, trừ 1 vì 0-indexed)
                    with c1: st.metric("SL PO", int(to_num_po(safe_iloc(17, 0))))
                    with c2: st.metric("Min", fmt_currency(to_num_po(safe_iloc(19, 0))))
                    with c3: st.metric("Max", fmt_currency(to_num_po(safe_iloc(21, 0))))
                    with c4: st.metric("Avg", fmt_currency(to_num_po(safe_iloc(23, 0))))
                with col2:
                    st.markdown("**📍 Miền Bắc**")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("SL PO", int(to_num_po(safe_iloc(17, 1))))
                    with c2: st.metric("Min", fmt_currency(to_num_po(safe_iloc(19, 1))))
                    with c3: st.metric("Max", fmt_currency(to_num_po(safe_iloc(21, 1))))
                    with c4: st.metric("Avg", fmt_currency(to_num_po(safe_iloc(23, 1))))
            except Exception as e:
                st.warning(f"Lỗi hiển thị PO: {e}")
                st.info("Vui lòng mở Debug panel bên trên để xem đúng vị trí row/col")

        # Top SKU
        st.markdown('<div class="section-header">🏷️ PHÂN TÍCH SKU</div>', unsafe_allow_html=True)
        col_top, col_slow = st.columns(2)

        def safe_get(df, r, c):
            try:
                if r < df.shape[0] and c < df.shape[1]:
                    v = df.iloc[r, c]
                    return v if str(v).strip() not in ["", "nan", "None"] else None
            except:
                pass
            return None

        with col_top:
            st.markdown(f'🔥 **{T("sku_chay")}**')
            try:
                # Sheets hàng 18-20 = iloc[16, 17, 18]
                rows_top = [16, 17, 18]
                skus = [safe_get(df_dash_ck, r, 4) for r in rows_top]
                sls  = [safe_get(df_dash_ck, r, 5) for r in rows_top]
                # Lọc ra các dòng có dữ liệu thực
                data_top = [(s, q) for s, q in zip(skus, sls) if s is not None]
                if data_top:
                    st.table(pd.DataFrame(data_top, columns=[T("ma_sku"), T("san_luong")]))
                else:
                    st.info("Chưa có dữ liệu (kiểm tra Debug panel để xem đúng vị trí)")
            except Exception as e:
                st.info(f"Lỗi đọc SKU chạy: {e}")

        with col_slow:
            st.markdown(f'⚠️ **{T("sku_cham")}**')
            try:
                # Sheets hàng 23-25 = iloc[21, 22, 23]
                rows_slow = [21, 22, 23]
                skus = [safe_get(df_dash_ck, r, 4) for r in rows_slow]
                sls  = [safe_get(df_dash_ck, r, 5) for r in rows_slow]
                data_slow = [(s, q) for s, q in zip(skus, sls) if s is not None]
                if data_slow:
                    st.table(pd.DataFrame(data_slow, columns=[T("ma_sku"), T("san_luong")]))
                else:
                    st.info("Chưa có dữ liệu (kiểm tra Debug panel để xem đúng vị trí)")
            except Exception as e:
                st.info(f"Lỗi đọc SKU chậm: {e}")
