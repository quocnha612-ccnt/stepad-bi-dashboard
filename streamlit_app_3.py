import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime, date
import json
import os

# ============================================================
# 1. CẤU HÌNH TRANG & CSS GIAO DIỆN
# ============================================================
st.set_page_config(
    page_title="Stepad | Business Intelligence",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

* { 
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
}

/* Nền app xám nhẹ chống chói mắt */
.stApp { 
    background-color: #f8fafc !important; 
    color: #0f172a !important; 
}
.stApp > header { 
    background-color: transparent !important; 
}

/* ============================================================
   ĐẶC TRỊ MÀU CHỮ CÁC TAB
============================================================ */
div[data-baseweb="tab-list"],
div[data-testid="stTabs"] [data-baseweb="tab-list"],
[data-testid="stTabs"] > div:first-child {
    background-color: transparent !important;
    gap: 8px !important;
}

div[data-baseweb="tab-list"] button,
div[data-testid="stTabs"] button,
button[data-baseweb="tab"],
button[role="tab"] {
    background-color: transparent !important;
    border: none !important;
    padding: 10px 16px !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div[data-baseweb="tab-list"] button *,
div[data-testid="stTabs"] button *,
button[data-baseweb="tab"] *,
button[role="tab"] *,
button[role="tab"] p,
button[role="tab"] span,
button[role="tab"] div,
[data-testid="stMarkdownContainer"] p {
    color: #1e293b !important;
    -webkit-text-fill-color: #1e293b !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div[data-baseweb="tab-list"] button[aria-selected="true"],
div[data-testid="stTabs"] button[aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"],
button[role="tab"][aria-selected="true"] {
    background-color: #ffffff !important;
    border-radius: 8px 8px 0 0 !important;
    box-shadow: 0 -2px 5px rgba(0,0,0,0.03) !important;
}

div[data-baseweb="tab-list"] button[aria-selected="true"] *,
div[data-testid="stTabs"] button[aria-selected="true"] *,
button[data-baseweb="tab"][aria-selected="true"] *,
button[role="tab"][aria-selected="true"] *,
button[role="tab"][aria-selected="true"] p,
button[role="tab"][aria-selected="true"] span,
button[role="tab"][aria-selected="true"] div {
    color: #00b87c !important;
    -webkit-text-fill-color: #00b87c !important;
    font-weight: 800 !important;
}

div[data-baseweb="tab-highlight"],
[data-baseweb="tab-highlight"] {
    background-color: #00b87c !important;
    height: 3px !important;
}

div[data-baseweb="tab-border"],
[data-baseweb="tab-border"] {
    background-color: #cbd5e1 !important;
}

/* ============================================================
   THIẾT KẾ CARD HIỂN THỊ KÊNH BÁN HÀNG
============================================================ */
.channel-box {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
}
.channel-name {
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin-bottom: 12px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px dashed #e2e8f0 !important;
}
.metric-row {
    margin-bottom: 8px !important;
}
.metric-lbl {
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 2px !important;
}
.metric-val-main {
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    color: #00b87c !important;
}
.metric-val-sub {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #334155 !important;
}
.metric-val-debt {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #ef4444 !important;
}

/* ============================================================
   CÁC THÀNH PHẦN KHÁC (FORM INPUT, LABELS, METRICS)
============================================================ */
label, .stWidgetLabel, .stWidgetLabel p, [data-testid="stWidgetLabel"] {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
    background-color: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-weight: 600 !important;
}

div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
    background-color: #ffffff !important;
}

div[data-baseweb="menu"] li {
    color: #0f172a !important;
}

.stButton > button {
    background-color: #00b87c !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 9px 22px !important;
    box-shadow: 0 2px 5px rgba(0, 184, 124, 0.25) !important;
}

.stButton > button:hover {
    background-color: #009966 !important;
    color: #ffffff !important;
}

[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
}

[data-testid="stMetricValue"] { 
    color: #00b87c !important; 
    font-weight: 800 !important;
    font-size: 1.55rem !important;
}

[data-testid="stMetricLabel"] { 
    color: #64748b !important; 
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
}

.stDataFrame { 
    border: 1px solid #cbd5e1 !important; 
    border-radius: 12px !important; 
    background-color: #ffffff !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
}

.section-header {
    color: #0f172a !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    margin-bottom: 14px !important;
    padding-bottom: 8px !important;
    border-bottom: 2px solid #cbd5e1 !important;
}

.logo-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 6px 14px;
    display: inline-flex;
    align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.role-badge {
    background-color: #ecfdf5;
    color: #00b87c;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
    border: 1px solid #a7f3d0;
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

@st.cache_data(ttl=1800)
def load_sheet(sheet_name):
    import time
    for attempt in range(3):
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
            if "429" in str(e) or "Quota" in str(e):
                time.sleep((attempt + 1) * 5)
            else:
                st.error(f"Lỗi tải {sheet_name}: {e}")
                return pd.DataFrame()
    st.error(f"Không thể tải {sheet_name} sau 3 lần thử.")
    return pd.DataFrame()

def append_row(sheet_name, row_data):
    import time
    for attempt in range(3):
        try:
            client = get_gsheet_client()
            sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
            sheet.append_row(row_data)
            return True
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep((attempt + 1) * 3)
            else:
                st.error(f"Lỗi ghi vào {sheet_name}: {e}")
                return False
    st.error(f"Không thể ghi vào {sheet_name} sau 3 lần thử.")
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

LANG = {
    "vi": {
        "title": "STEPAD CRM",
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
    },
    "zh": {
        "title": "STEPAD CRM",
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

def render_logo(width=160):
    logo_candidates = ["logo.png", "logo Trang chủ.png", "logo_stepad.png", "assets/logo.png"]
    found_logo = next((p for p in logo_candidates if os.path.exists(p)), None)
    if found_logo:
        st.image(found_logo, width=width)
    else:
        st.markdown("""
        <div class="logo-container">
            <span style="font-family:'Plus Jakarta Sans',sans-serif; font-size:1.45rem; font-weight:900; letter-spacing:1px; color:#334155;">
                stepad<sup style="font-size:0.6rem; color:#64748b;">®</sup>
            </span>
        </div>
        """, unsafe_allow_html=True)

def login_page():
    st.markdown("<div style='text-align:center; margin-top:60px;'>", unsafe_allow_html=True)
    render_logo(width=220)
    st.markdown("""
        <div style="color:#64748b; font-size:0.85rem; letter-spacing:2px; margin-top:8px; font-weight:700;">
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
# 4. HÀM CHUẨN HÓA VÀ XỬ LÝ SỐ LIỆU ĐẶC TRỊ LỖI THẬP PHÂN
# ============================================================
def parse_num(s):
    try:
        if s is None or s == "":
            return 0.0
        s = str(s).strip().replace("đ", "").replace("VND", "").replace("\xa0", "").replace(" ", "")
        if not s or s.lower() in ["-", "n/a", "nan", "none"]:
            return 0.0

        is_negative = s.startswith("-")
        if is_negative:
            s = s[1:]

        # Nếu có cả dấu chấm và dấu phẩy
        if "." in s and "," in s:
            if s.rfind(".") > s.rfind(","):
                # Dạng 1,194.50 (US) -> bỏ phẩy
                s = s.replace(",", "")
            else:
                # Dạng 1.194,50 (VN) -> bỏ chấm, phẩy thành chấm
                s = s.replace(".", "").replace(",", ".")
        elif "." in s:
            # Chỉ có dấu chấm
            if s.count(".") > 1:
                # Dạng 1.000.000 -> bỏ chấm
                s = s.replace(".", "")
            else:
                parts = s.split(".")
                # Nếu sau dấu chấm có đúng 3 chữ số (1.194 hoặc 74.000) -> phân cách hàng nghìn VN
                if len(parts[-1]) == 3:
                    s = s.replace(".", "")
                else:
                    # Số thập phân (1.5 hoặc 1.25)
                    pass
        elif "," in s:
            # Chỉ có dấu phẩy: 0,4000000004 hoặc 4651434,4 hoặc 1,194
            if s.count(",") > 1:
                s = s.replace(",", "")
            else:
                parts = s.split(",")
                # Nếu sau dấu phẩy có đúng 3 chữ số và phần đầu khác 0 (1,194)
                if len(parts[-1]) == 3 and parts[0] != "0":
                    s = s.replace(",", "")
                else:
                    # Số thập phân kiểu VN (0,4000000004 -> 0.4000000004)
                    s = parts[0] + "." + parts[1]

        val = float(s)
        if is_negative:
            val = -val

        if abs(val) < 1.0:
            return 0.0
        return round(val)
    except Exception:
        return 0.0

def fmt_currency(val):
    try:
        num = parse_num(val)
        return f"{num:,.0f} đ"
    except Exception:
        return "0 đ"

COL_TRANSLATE = {
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
    "Tên cửa hàng":              {"zh": "门店名称"},
    "Địa chỉ":                   {"zh": "地址"},
    "Kênh phân phối":            {"zh": "渠道"},
    "Tổng doanh thu":            {"zh": "总营业额"},
    "Tỷ lệ TT":                  {"zh": "付款率"},
    "Giá Nha Trang":             {"zh": "芽庄价"},
    "Giá Circle K":              {"zh": "Circle K价"},
    "Giá MT":                    {"zh": "现代贸易价"},
    "Giá GT":                    {"zh": "传统贸易价"},
    "Trạng thái tồn kho":        {"zh": "库存状态"},
    "Tổng kho":                  {"zh": "总库存"},
    "Ngày":                      {"zh": "日期"},
    "Thời gian":                 {"zh": "时间"},
    "Kho":                       {"zh": "仓库"},
    "Người nhập":                {"zh": "录入人"},
    "Ghi chú":                   {"zh": "备注"},
    "Số tiền trả":               {"zh": "还款金额"},
    "Tên khách":                 {"zh": "客户名称"},
    "SL nhập Bắc":               {"zh": "北区入库"},
    "SL nhập Nam":               {"zh": "南区入库"},
    "SL xuất Bắc":               {"zh": "北区出库"},
    "SL xuất Nam":               {"zh": "南区出库"},
    "Tồn kho Bắc":               {"zh": "北区库存"},
    "Tồn kho Nam":               {"zh": "南区库存"},
    "Ngưỡng cảnh báo":           {"zh": "预警阈值"},
    "Tồn hệ thống":              {"zh": "系统库存"},
    "Tồn thực tế":               {"zh": "实际库存"},
    "Chênh lệch":                {"zh": "差异数量"},
    "Người kiểm kê":             {"zh": "盘点人员"},
    "Lý do / Ghi chú":           {"zh": "原因/备注"},
}

def translate_columns(df):
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
    except Exception:
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
# 5. KHỞI TẠO VÀ XÁC THỰC
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

# Header chính hiển thị Logo Stepad
col_h1, col_h2 = st.columns([3, 1.2])
with col_h1:
    render_logo(width=175)
with col_h2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 6px; margin-bottom: 6px;">
        <span style="color: #334155; font-weight: 700; font-size: 0.92rem;">{st.session_state.name}</span> &nbsp;
        <span class="role-badge">{st.session_state.role.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    col_lang, col_out = st.columns([1, 1])
    with col_lang:
        if st.button("🌐 VI / 中文", key="lang_toggle"):
            st.session_state.lang = "zh" if st.session_state.get("lang","vi") == "vi" else "vi"
            st.rerun()
    with col_out:
        if st.button(T("logout"), key="logout"):
            st.session_state.logged_in = False
            st.rerun()

st.markdown("<hr style='border-color:#cbd5e1; margin: 6px 0 18px 0;'>", unsafe_allow_html=True)

# ============================================================
# 6. TABS ĐIỀU HƯỚNG
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
if st.session_state.role == "admin":
    with t_dash:
        with st.spinner("Đang tải dữ liệu..."):
            df_dash    = load_sheet("Dashboard")
            df_kh      = load_sheet("Khach_Hang")
            df_chitiet = load_sheet("Chi_tiet_don")
            df_donhang = load_sheet("Don_Hang")

        st.markdown('<div class="section-header">🗓️ BỘ LỌC THỜI GIAN</div>', unsafe_allow_html=True)

        available_years = []
        available_months_map = {}

        if not df_chitiet.empty:
            col_thang_ct = next((c for c in df_chitiet.columns if "tháng" in c.lower() or c.lower() == "tháng"), None)
            col_ngay_ct  = next((c for c in df_chitiet.columns if "ngày" in c.lower() or "ngay" in c.lower()), None)

            if col_ngay_ct:
                parsed = pd.to_datetime(df_chitiet[col_ngay_ct], format="%Y-%m-%d", errors="coerce")
                mask_failed = parsed.isna()
                if mask_failed.any():
                    parsed2 = pd.to_datetime(df_chitiet.loc[mask_failed, col_ngay_ct], dayfirst=True, errors="coerce")
                    parsed[mask_failed] = parsed2
                df_chitiet["_parsed_date"] = parsed
                df_chitiet["_year"]  = df_chitiet["_parsed_date"].dt.year
                df_chitiet["_month"] = df_chitiet["_parsed_date"].dt.month
            elif col_thang_ct:
                def parse_thang(x):
                    s = str(x).strip().upper().replace("THÁNG","").replace("T","").strip()
                    try: return int(s)
                    except Exception: return None
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
                    f"<div style='padding-top:28px; color:#00b87c; font-weight:800; font-size:0.85rem;'>"
                    f"🔍 Đang lọc theo: <b>{' — '.join(filter_info)}</b></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='padding-top:28px; color:#64748b; font-size:0.85rem; font-weight:600;'>🔍 Đang xem: Toàn bộ thời gian</div>",
                    unsafe_allow_html=True
                )

        st.markdown("<hr style='border-color:#cbd5e1; margin:8px 0 16px 0;'>", unsafe_allow_html=True)

        use_filtered = not df_chitiet.empty and "_year" in df_chitiet.columns

        if use_filtered:
            df_ct_filtered = df_chitiet.copy()
            if sel_year:
                df_ct_filtered = df_ct_filtered[df_ct_filtered["_year"] == sel_year]
            if sel_month:
                df_ct_filtered = df_ct_filtered[df_ct_filtered["_month"] == sel_month]
        else:
            df_ct_filtered = df_chitiet.copy() if not df_chitiet.empty else pd.DataFrame()

        col_sau_thue = next((c for c in df_chitiet.columns if "sau thuế" in c.lower() or "sau thue" in c.lower()), None)

        def sum_col(df, col):
            if col and col in df.columns and not df.empty:
                return df[col].apply(parse_num).sum()
            return 0.0

        col_kv_ct = next((c for c in df_chitiet.columns if "khu vực" in c.lower()), None)

        def sum_by_kenh(kenh_keyword):
            if df_ct_filtered.empty or col_kv_ct is None or col_sau_thue is None:
                return 0.0
            mask = df_ct_filtered[col_kv_ct].astype(str).str.contains(kenh_keyword, case=False, na=False)
            return df_ct_filtered[mask][col_sau_thue].apply(parse_num).sum()

        st.markdown('<div class="section-header">💳 TÀI CHÍNH TỔNG QUAN</div>', unsafe_allow_html=True)

        show_filtered_metrics = use_filtered and (sel_year or sel_month)

        if show_filtered_metrics:
            tong_dt_val  = sum_col(df_ct_filtered, col_sau_thue)
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
                        except Exception: return None
                    df_don_filtered["_month"] = df_don_filtered[col_thang_don].apply(parse_thang2)
                    if sel_month:
                        df_don_filtered = df_don_filtered[df_don_filtered["_month"] == sel_month]

            col_da_tt_don = next((c for c in df_donhang.columns if "đã thanh toán" in c.lower() or "đã tt" in c.lower()), None)
            col_con_no_don = next((c for c in df_donhang.columns if "còn nợ" in c.lower() or "con no" in c.lower()), None)
            da_tt_val = sum_col(df_don_filtered, col_da_tt_don)
            con_no_val = sum_col(df_don_filtered, col_con_no_don)
            if da_tt_val == 0 and con_no_val == 0:
                da_tt_val = tong_dt_val * 0.0
                con_no_val = tong_dt_val

            try:
                col_id_kh_don = next((c for c in df_don_filtered.columns if "id khách" in c.lower() or "id_khach" in c.lower()), None)
                tong_ch_val = df_don_filtered[col_id_kh_don].nunique() if col_id_kh_don and not df_don_filtered.empty else 0

                if col_id_kh_don and "_parsed_date" in df_don_filtered.columns:
                    max_date = df_don_filtered["_parsed_date"].max()
                    if pd.notna(max_date):
                        date_3m_ago = max_date - pd.DateOffset(months=3)
                        df_active = df_don_filtered[df_don_filtered["_parsed_date"] >= date_3m_ago]
                        ch_active_val = df_active[col_id_kh_don].nunique()
                    else:
                        ch_active_val = 0
                else:
                    ch_active_val = 0

                ty_le_val = f"{ch_active_val/tong_ch_val*100:.2f}%" if tong_ch_val > 0 else "0%"

                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1: st.metric(T("tong_dt"), fmt_currency(tong_dt_val))
                with col2: st.metric(T("da_nhan"), fmt_currency(da_tt_val))
                with col3: st.metric(T("no_thu"), fmt_currency(con_no_val))
                with col4: st.metric(T("tong_ch"), f'{tong_ch_val} {T("diem")}')
                with col5: st.metric(T("ch_active"), f'{ch_active_val} {T("diem")}')
                with col6: st.metric(T("ty_le_phu"), ty_le_val)
            except Exception as e:
                st.error(f"Lỗi tính metrics: {e}")
        else:
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

        # ============================================================
        # KHỐI HIỂN THỊ DOANH THU THEO KÊNH (TINH CHỈNH MÀU SẮC)
        # ============================================================
        st.markdown('<div class="section-header">📊 DOANH THU THEO KÊNH</div>', unsafe_allow_html=True)

        if show_filtered_metrics and use_filtered and col_kv_ct and col_sau_thue:
            try:
                ck_val  = sum_by_kenh("Circle K|CK")
                mt_val  = sum_by_kenh("MT|Modern Trade")
                gt_val  = sum_by_kenh("GT|General Trade")
                nt_val  = sum_by_kenh("Nha Trang|NT|Ký gửi")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    bac_val = 0.0
                    nam_val = 0.0
                    col_kho = next((c for c in df_ct_filtered.columns if "kho" in c.lower()), None)
                    if col_kho:
                        mask_ck = df_ct_filtered[col_kv_ct].astype(str).str.contains("Circle K|CK", case=False, na=False)
                        ck_df = df_ct_filtered[mask_ck]
                        bac_val = ck_df[ck_df[col_kho].astype(str).str.contains("Bắc|bac|Bac", case=False, na=False)][col_sau_thue].apply(parse_num).sum()
                        nam_val = ck_df[ck_df[col_kho].astype(str).str.contains("Nam|nam", case=False, na=False)][col_sau_thue].apply(parse_num).sum()

                    st.markdown(f"""
                    <div class="channel-box">
                        <div class="channel-name">🏪 CIRCLE K</div>
                        <div class="metric-row">
                            <div class="metric-lbl">{T("tong")}</div>
                            <div class="metric-val-main">{fmt_currency(ck_val)}</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-lbl">{T("mien_bac")}</div>
                            <div class="metric-val-sub">{fmt_currency(bac_val)}</div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-lbl">{T("mien_nam")}</div>
                            <div class="metric-val-sub">{fmt_currency(nam_val)}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="channel-box">
                        <div class="channel-name">🏬 MODERN TRADE</div>
                        <div class="metric-row">
                            <div class="metric-lbl">{T("tong_dt2")}</div>
                            <div class="metric-val-main">{fmt_currency(mt_val)}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="channel-box">
                        <div class="channel-name">🛒 GENERAL TRADE</div>
                        <div class="metric-row">
                            <div class="metric-lbl">{T("tong_dt2")}</div>
                            <div class="metric-val-main">{fmt_currency(gt_val)}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="channel-box">
                        <div class="channel-name">🌊 NHA TRANG</div>
                        <div class="metric-row">
                            <div class="metric-lbl">{T("ky_gui")}</div>
                            <div class="metric-val-main">{fmt_currency(nt_val)}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Lỗi tính doanh thu kênh: {e}")
        else:
            if not df_dash.empty:
                try:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="channel-box">
                            <div class="channel-name">🏪 CIRCLE K</div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("tong")}</div>
                                <div class="metric-val-main">{fmt_currency(df_dash.iloc[4, 0])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("mien_bac")}</div>
                                <div class="metric-val-sub">{fmt_currency(df_dash.iloc[4, 1])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("mien_nam")}</div>
                                <div class="metric-val-sub">{fmt_currency(df_dash.iloc[4, 2])}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="channel-box">
                            <div class="channel-name">🏬 MODERN TRADE</div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("tong_dt2")}</div>
                                <div class="metric-val-main">{fmt_currency(df_dash.iloc[7, 0])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("da_tt")}</div>
                                <div class="metric-val-sub">{fmt_currency(df_dash.iloc[7, 1])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("no")}</div>
                                <div class="metric-val-debt">{fmt_currency(df_dash.iloc[7, 2])}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"""
                        <div class="channel-box">
                            <div class="channel-name">🛒 GENERAL TRADE</div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("tong_dt2")}</div>
                                <div class="metric-val-main">{fmt_currency(df_dash.iloc[9, 0])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("da_tt")}</div>
                                <div class="metric-val-sub">{fmt_currency(df_dash.iloc[9, 1])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("no")}</div>
                                <div class="metric-val-debt">{fmt_currency(df_dash.iloc[9, 2])}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col4:
                        st.markdown(f"""
                        <div class="channel-box">
                            <div class="channel-name">🌊 NHA TRANG</div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("ky_gui")}</div>
                                <div class="metric-val-main">{fmt_currency(df_dash.iloc[13, 0])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("da_tt")}</div>
                                <div class="metric-val-sub">{fmt_currency(df_dash.iloc[13, 1])}</div>
                            </div>
                            <div class="metric-row">
                                <div class="metric-lbl">{T("no")}</div>
                                <div class="metric-val-debt">{fmt_currency(df_dash.iloc[13, 2])}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Đang chờ dữ liệu kênh phân phối...")

        st.markdown("<br>", unsafe_allow_html=True)

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
                    if not sel_year:
                        df_trend_grp["Tháng"] = df_trend_grp.apply(
                            lambda r: f"T{int(r['Tháng số'])}/{int(r['Năm'])}", axis=1
                        )
                    else:
                        df_trend_grp["Tháng"] = df_trend_grp["Tháng số"].apply(lambda m: f"T{int(m)}")
                    df_trend_grp = df_trend_grp.sort_values(["Năm", "Tháng số"])
                    fig_trend = px.bar(
                        df_trend_grp, x="Tháng", y="Doanh thu", color="Kênh",
                        barmode="group",
                        color_discrete_sequence=["#00b87c","#10b981","#34d399","#6ee7b7"],
                    )
                    fig_trend.update_layout(
                        height=350, 
                        paper_bgcolor="#ffffff", 
                        plot_bgcolor="#ffffff",
                        xaxis=dict(tickfont=dict(color="#475569")),
                        yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#475569")),
                        legend=dict(font=dict(color="#0f172a"), orientation="h", y=1.1),
                        margin=dict(l=10, r=10, t=30, b=10),
                    )
                    fig_trend.update_traces(hovertemplate="%{y:,.0f} đ")
                    st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e:
                st.caption(f"Chưa thể vẽ biểu đồ: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown('<div class="section-header">🔴 TOP KHÁCH NỢ NHIỀU</div>', unsafe_allow_html=True)
            if not df_kh.empty and 'Còn nợ' in df_kh.columns and 'Tên cửa hàng' in df_kh.columns:
                try:
                    df_no = df_kh.copy()
                    df_no['_no_num'] = df_no['Còn nợ'].apply(parse_num)
                    df_no = df_no[df_no['_no_num'] > 0]
                    df_no = df_no.nlargest(5, '_no_num')[['Tên cửa hàng', '_no_num', 'Khu vực']]
                    df_no = df_no.rename(columns={'_no_num': 'Còn nợ'})
                    df_no['Còn nợ'] = df_no['Còn nợ'].apply(fmt_currency)
                    st.dataframe(translate_columns(df_no), use_container_width=True, hide_index=True)
                except Exception:
                    st.info(T("chua_du_lieu_no"))
            else:
                st.info(T("chua_du_lieu"))

        with col_right:
            st.markdown('<div class="section-header">🟢 TOP KHÁCH HIỆU SUẤT TỐT</div>', unsafe_allow_html=True)
            if not df_kh.empty:
                try:
                    cols_lower = {c: c.lower().strip() for c in df_kh.columns}
                    col_dt = next((c for c, cl in cols_lower.items() if 'doanh thu' in cl or 'tổng' in cl), None)
                    col_tt = next((c for c, cl in cols_lower.items() if 'đã thanh toán' in cl or 'đã tt' in cl or ('thanh toán' in cl and 'đã' in cl)), None)
                    if col_dt is None:
                        numeric_cols = df_kh.select_dtypes(include='number').columns.tolist()
                        if numeric_cols:
                            col_dt = numeric_cols[0]
                    if col_dt:
                        df_perf = df_kh.copy()
                        df_perf[col_dt] = df_perf[col_dt].apply(parse_num)
                        df_perf = df_perf[df_perf[col_dt] > 0]
                        show_cols = ["Tên cửa hàng", col_dt]
                        if col_tt:
                            df_perf[col_tt] = df_perf[col_tt].apply(parse_num)
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

    if "order_items" not in st.session_state:
        st.session_state.order_items = [{"sku": "", "sl": 1}]
    if "order_success" not in st.session_state:
        st.session_state.order_success = False
    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    if st.session_state.order_success:
        st.success(T("luu_ok"))
        st.session_state.order_success = False

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
        st.markdown(f"<small style='color:#00b87c; font-weight:700;'>📍 Khu vực: <b>{khu_vuc}</b></small>", unsafe_allow_html=True)

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

    st.markdown('<div class="section-header">🛒 SẢN PHẨM ĐẶT HÀNG</div>', unsafe_allow_html=True)

    ds_sku = df_sp['SKU Sản phẩm'].tolist() if 'SKU Sản phẩm' in df_sp.columns else []
    ds_ten_sp = df_sp['Tên sản phẩm'].tolist() if 'Tên sản phẩm' in df_sp.columns else []
    ds_sku_display = [f"{sku} — {ten}" for sku, ten in zip(ds_sku, ds_ten_sp)]

    tong_truoc_thue = 0
    items_data = []

    h1, h2, h3, h4, h5 = st.columns([3, 1, 1.5, 1.5, 0.5])
    with h1: st.markdown("<small style='color:#475569; font-weight:800;'>Sản phẩm</small>", unsafe_allow_html=True)
    with h2: st.markdown("<small style='color:#475569; font-weight:800;'>Số lượng</small>", unsafe_allow_html=True)
    with h3: st.markdown("<small style='color:#475569; font-weight:800;'>Đơn giá</small>", unsafe_allow_html=True)
    with h4: st.markdown("<small style='color:#475569; font-weight:800;'>Thành tiền</small>", unsafe_allow_html=True)

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
        don_gia_mac_dinh = get_gia_theo_khu_vuc(df_sp, sku_code, khu_vuc) if sku_code else 0

        with col_gia:
            if "nha trang" in khu_vuc.lower() and sku_code:
                don_gia = st.number_input(
                    "Giá", min_value=0,
                    value=int(don_gia_mac_dinh),
                    step=1000,
                    key=f"gia_{st.session_state.form_key}_{i}",
                    label_visibility="collapsed"
                )
            else:
                don_gia = don_gia_mac_dinh
                st.markdown(f"<div style='padding-top:8px; color:#1e293b; font-weight:700;'>{fmt_currency(don_gia)}</div>", unsafe_allow_html=True)

        thanh_tien = don_gia * sl
        tong_truoc_thue += thanh_tien

        with col_tt:
            st.markdown(f"<div style='padding-top:8px; color:#00b87c; font-weight:800;'>{fmt_currency(thanh_tien)}</div>", unsafe_allow_html=True)
        with col_del:
            if st.button("✕", key=f"del_{st.session_state.form_key}_{i}") and len(st.session_state.order_items) > 1:
                st.session_state.order_items.pop(i)
                st.rerun()

        if sku_code:
            items_data.append({"sku": sku_code, "sl": sl, "don_gia": don_gia, "thanh_tien": thanh_tien})

    if st.button(T("them_sp"), key=f"add_sku_{st.session_state.form_key}"):
        st.session_state.order_items.append({"sku": "", "sl": 1})
        st.rerun()

    st.markdown("<hr style='border-color:#cbd5e1; margin:16px 0'>", unsafe_allow_html=True)

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
                except Exception:
                    pass

                nhan_vien = st.session_state.name
                success = True

                for item in items_data:
                    row_don_hang = [
                        id_don,
                        id_khach,
                        str(ngay_don),
                        loai_don,
                        item['sku'],
                        "",
                        item['sl'],
                        thue_suat,
                        item['don_gia'],
                        item['thanh_tien'],
                        item['thanh_tien'] * thue_suat,
                        item['thanh_tien'] * (1 + thue_suat),
                        da_thanh_toan,
                        con_no,
                        khu_vuc,
                        ma_po,
                        thang,
                        tt_thanh_toan,
                        tt_hd,
                        ten_khach,
                        kho,
                        nhan_vien,
                        ""
                    ]
                    if not append_row("Don_Hang", row_don_hang):
                        success = False
                        break

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
                    st.session_state.order_items = [{"sku": "", "sl": 1}]
                    st.session_state.order_success = True
                    st.session_state.form_key += 1
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(T("loi_luu"))

# ============================================================
# TAB: ĐƠN HÀNG & GHI NHẬN THANH TOÁN (TÌM TẤT CẢ KHÁCH HÀNG)
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

    if st.session_state.role == "admin":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">💰 GHI NHẬN THANH TOÁN</div>', unsafe_allow_html=True)

        with st.spinner("Đang tải danh sách khách hàng..."):
            df_kh_tt = load_sheet("Khach_Hang")

        if not df_kh_tt.empty:
            if "tt_form_key" not in st.session_state:
                st.session_state.tt_form_key = 0

            col_id_kh  = next((c for c in df_kh_tt.columns if c.lower() == "id khách"), None)
            col_ten_kh = next((c for c in df_kh_tt.columns if "tên cửa hàng" in c.lower()), None)
            col_no     = next((c for c in df_kh_tt.columns if "còn nợ" in c.lower()), None)

            if col_id_kh and col_ten_kh and col_no:
                df_kh_tt["_no_num"] = df_kh_tt[col_no].apply(parse_num)
                col_dia_kh = next((c for c in df_kh_tt.columns if "địa chỉ" in c.lower()), None)

                # DANH SÁCH TOÀN BỘ KHÁCH HÀNG (KỂ CẢ KHÔNG CÒN NỢ)
                ds_kh_all = []
                for _, row in df_kh_tt.iterrows():
                    cid = str(row[col_id_kh]).strip()
                    cten = str(row[col_ten_kh]).strip()
                    cdia = str(row[col_dia_kh]).strip() if col_dia_kh and pd.notna(row[col_dia_kh]) else ""
                    if cid and cid.lower() not in ["none", "nan", ""]:
                        ds_kh_all.append(f"{cid} — {cten} — {cdia}".strip(" — "))

                col_tt1, col_tt2 = st.columns([2, 1])
                with col_tt1:
                    sel_kh_tt = st.selectbox("👤 Chọn khách hàng *", ["-- Chọn --"] + ds_kh_all, key=f"tt_kh_{st.session_state.tt_form_key}")
                with col_tt2:
                    ghi_chu_tt = st.text_input("📝 Ghi chú", placeholder="Chuyển khoản, tiền mặt...", key=f"tt_ghichu_{st.session_state.tt_form_key}")

                if sel_kh_tt != "-- Chọn --":
                    id_kh_sel = sel_kh_tt.split(" — ")[0].strip()
                    matched_rows = df_kh_tt[df_kh_tt[col_id_kh] == id_kh_sel]
                    
                    if not matched_rows.empty:
                        row_kh = matched_rows.iloc[0]
                        so_no = row_kh["_no_num"]
                        ten_kh_sel = row_kh[col_ten_kh]

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("💳 Tổng nợ hiện tại", fmt_currency(so_no))
                            if so_no <= 0:
                                st.markdown("<span style='color:#00b87c; font-weight:700;'>✅ Khách hàng này không còn nợ tồn đọng!</span>", unsafe_allow_html=True)
                        
                        with col_b:
                            if so_no > 0:
                                so_tien_tt = st.number_input(
                                    "💵 Số tiền trả *",
                                    min_value=0,
                                    max_value=int(so_no),
                                    value=int(so_no),
                                    step=100000,
                                    key=f"tt_sotien_{st.session_state.tt_form_key}"
                                )
                            else:
                                so_tien_tt = 0

                        if so_no > 0:
                            if st.button("✅ XÁC NHẬN THANH TOÁN", key=f"btn_tt_{st.session_state.tt_form_key}"):
                                if so_tien_tt <= 0:
                                    st.error("Số tiền phải lớn hơn 0!")
                                else:
                                    ngay_tt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    row_tt = [ngay_tt, id_kh_sel, ten_kh_sel, so_tien_tt, st.session_state.name, ghi_chu_tt]
                                    if append_row("Thanh_Toan", row_tt):
                                        st.success(f"✅ Đã ghi nhận **{fmt_currency(so_tien_tt)}** từ **{ten_kh_sel}**!")
                                        st.session_state.tt_form_key += 1
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("Có lỗi khi ghi dữ liệu, vui lòng thử lại!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🕐 LỊCH SỬ THANH TOÁN</div>', unsafe_allow_html=True)
        df_tt_lich_su = load_sheet("Thanh_Toan")
        if not df_tt_lich_su.empty:
            st.dataframe(
                translate_columns(df_tt_lich_su.tail(20).iloc[::-1]),
                use_container_width=True, hide_index=True
            )
            st.caption(f"Hiển thị 20 lần gần nhất | Tổng: {len(df_tt_lich_su)} lần")
        else:
            st.info("Chưa có lịch sử thanh toán.")

# ============================================================
# TAB: SẢN PHẨM & KIỂM KÊ KHO (Admin only)
# ============================================================
if st.session_state.role == "admin":
    with t_sp:
        with st.spinner("Đang tải dữ liệu kho..."):
            df_sp_full = load_sheet("San_Pham")

        if not df_sp_full.empty and 'Trạng thái tồn kho' in df_sp_full.columns:
            df_canh_bao = df_sp_full[
                df_sp_full['Trạng thái tồn kho'].astype(str).str.contains('Cảnh báo|Hết', na=False)
            ]
            if not df_canh_bao.empty:
                st.warning(f"⚠️ **{len(df_canh_bao)} sản phẩm** cần chú ý tồn kho!")

        st.markdown('<div class="section-header">📦 TỒN KHO HIỆN TẠI</div>', unsafe_allow_html=True)

        if not df_sp_full.empty:
            ton_kho_cols = ['SKU Sản phẩm', 'Tên sản phẩm',
                            'SL nhập Bắc', 'SL xuất Bắc', 'Tồn kho Bắc',
                            'SL nhập Nam', 'SL xuất Nam', 'Tồn kho Nam',
                            'Tổng kho', 'Ngưỡng cảnh báo', 'Trạng thái tồn kho']
            show_cols = [c for c in ton_kho_cols if c in df_sp_full.columns]
            df_ton_kho = df_sp_full[show_cols].copy() if show_cols else df_sp_full.copy()

            st.dataframe(
                translate_columns(df_ton_kho),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------------------------
        # TÍNH NĂNG MỚI: KIỂM KÊ & CÂN KHO THỰC TẾ (NHIỀU SẢN PHẨM)
        # ------------------------------------------------------------
        st.markdown('<div class="section-header">⚖️ KIỂM KÊ & CÂN KHO THỰC TẾ</div>', unsafe_allow_html=True)

        if not df_sp_full.empty:
            if "kk_items" not in st.session_state:
                st.session_state.kk_items = [{"sku": T("chon"), "sl_thucte": 0, "last_sku": T("chon")}]
            if "kk_form_key" not in st.session_state:
                st.session_state.kk_form_key = 0

            ds_sku_sp = df_sp_full['SKU Sản phẩm'].tolist() if 'SKU Sản phẩm' in df_sp_full.columns else []
            ds_ten_sp_kk = df_sp_full['Tên sản phẩm'].tolist() if 'Tên sản phẩm' in df_sp_full.columns else []
            ds_sku_kk_display = [f"{s} — {t}" for s, t in zip(ds_sku_sp, ds_ten_sp_kk)]

            col_kk1, col_kk2 = st.columns([1, 2])
            with col_kk1:
                # Mặc định chọn Nam do bạn trực tiếp quản lý kho Nam
                kho_kk = st.selectbox("🏭 Kho kiểm kê *", ["Nam", "Bắc"], key=f"kk_kho_{st.session_state.kk_form_key}")
            with col_kk2:
                ghi_chu_kk = st.text_input(
                    "📝 Lý do kiểm kê / Ghi chú chung",
                    placeholder="Ví dụ: Kiểm kê định kỳ tháng 10, hao hụt thực tế...",
                    key=f"kk_ghichu_{st.session_state.kk_form_key}"
                )

            st.markdown("**📦 Danh sách sản phẩm kiểm kê:**")
            h1, h2, h3, h4, h5 = st.columns([3, 1.2, 1.2, 1.5, 0.4])
            with h1: st.markdown("<small style='color:#475569; font-weight:800;'>Sản phẩm</small>", unsafe_allow_html=True)
            with h2: st.markdown("<small style='color:#475569; font-weight:800;'>Tồn hệ thống</small>", unsafe_allow_html=True)
            with h3: st.markdown("<small style='color:#475569; font-weight:800;'>Tồn thực tế</small>", unsafe_allow_html=True)
            with h4: st.markdown("<small style='color:#475569; font-weight:800;'>Chênh lệch</small>", unsafe_allow_html=True)
            with h5: st.markdown("", unsafe_allow_html=True)

            items_to_process = []

            for i, item in enumerate(st.session_state.kk_items):
                col_sku, col_sys, col_act, col_diff, col_del = st.columns([3, 1.2, 1.2, 1.5, 0.4])

                with col_sku:
                    options = [T("chon")] + ds_sku_kk_display
                    idx = 0
                    if item.get("sku") in options:
                        idx = options.index(item["sku"])
                    sku_sel = st.selectbox(
                        f"SP KK {i+1}",
                        options,
                        index=idx,
                        key=f"kk_sku_{st.session_state.kk_form_key}_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.kk_items[i]["sku"] = sku_sel

                sku_code_kk = sku_sel.split(" — ")[0].strip() if sku_sel != T("chon") else ""
                ten_sp_kk = ""
                ton_he_thong = 0

                if sku_code_kk:
                    matched_sp = df_sp_full[df_sp_full['SKU Sản phẩm'] == sku_code_kk]
                    if not matched_sp.empty:
                        row_sp = matched_sp.iloc[0]
                        ten_sp_kk = str(row_sp.get('Tên sản phẩm', ''))
                        col_target = 'Tồn kho Nam' if kho_kk == "Nam" else 'Tồn kho Bắc'
                        ton_he_thong = int(parse_num(row_sp.get(col_target, 0)))

                with col_sys:
                    if sku_code_kk:
                        st.markdown(f"<div style='padding-top:8px; font-weight:700; color:#334155;'>{ton_he_thong:,} cái</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='padding-top:8px; color:#94a3b8;'>-</div>", unsafe_allow_html=True)

                # Tự động gán tồn thực tế bằng tồn hệ thống khi mới chọn SKU
                if item.get("last_sku") != sku_sel:
                    st.session_state.kk_items[i]["last_sku"] = sku_sel
                    st.session_state.kk_items[i]["sl_thucte"] = max(0, ton_he_thong)

                with col_act:
                    if sku_code_kk:
                        val_default = int(st.session_state.kk_items[i].get("sl_thucte", max(0, ton_he_thong)))
                        sl_val = st.number_input(
                            f"SL TT {i+1}",
                            min_value=0,
                            value=val_default,
                            step=1,
                            key=f"kk_sl_{st.session_state.kk_form_key}_{i}",
                            label_visibility="collapsed"
                        )
                        st.session_state.kk_items[i]["sl_thucte"] = sl_val
                    else:
                        st.markdown("<div style='padding-top:8px; color:#94a3b8;'>-</div>", unsafe_allow_html=True)
                        sl_val = 0

                chenh_lech = int(sl_val - ton_he_thong) if sku_code_kk else 0

                with col_diff:
                    if sku_code_kk:
                        if chenh_lech > 0:
                            st.markdown(f"<div style='padding-top:8px; font-weight:800; color:#00b87c;'>+{chenh_lech:,} (Thừa)</div>", unsafe_allow_html=True)
                        elif chenh_lech < 0:
                            st.markdown(f"<div style='padding-top:8px; font-weight:800; color:#ef4444;'>{chenh_lech:,} (Thiếu)</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='padding-top:8px; font-weight:700; color:#64748b;'>0 (Khớp)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='padding-top:8px; color:#94a3b8;'>-</div>", unsafe_allow_html=True)

                with col_del:
                    if st.button("✕", key=f"kk_del_{st.session_state.kk_form_key}_{i}") and len(st.session_state.kk_items) > 1:
                        st.session_state.kk_items.pop(i)
                        st.rerun()

                if sku_code_kk:
                    items_to_process.append({
                        "sku_code": sku_code_kk,
                        "ten_sp": ten_sp_kk,
                        "ton_he_thong": ton_he_thong,
                        "sl_thuc_te": sl_val,
                        "chenh_lech": chenh_lech
                    })

            if st.button("➕ Thêm sản phẩm kiểm kê", key=f"kk_add_{st.session_state.kk_form_key}"):
                st.session_state.kk_items.append({"sku": T("chon"), "sl_thucte": 0, "last_sku": T("chon")})
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ XÁC NHẬN CÂN KHO TẤT CẢ", key=f"btn_kk_submit_{st.session_state.kk_form_key}"):
                if not items_to_process:
                    st.error("Vui lòng chọn ít nhất 1 sản phẩm để kiểm kê!")
                else:
                    skus_in_batch = [it["sku_code"] for it in items_to_process]
                    if len(skus_in_batch) != len(set(skus_in_batch)):
                        st.warning("⚠️ Có mã sản phẩm bị trùng lặp trong danh sách kiểm kê. Vui lòng kiểm tra lại!")
                    else:
                        items_diff = [it for it in items_to_process if it["chenh_lech"] != 0]
                        if not items_diff:
                            st.info("ℹ️ Tất cả các sản phẩm đã chọn đều khớp 100% với tồn hệ thống, không có chênh lệch cần điều chỉnh.")
                        else:
                            with st.spinner("Đang lưu dữ liệu kiểm kê vào Google Sheets..."):
                                ngay_kk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                success_count = 0
                                for it in items_diff:
                                    row_kk = [
                                        ngay_kk,
                                        it["sku_code"],
                                        it["ten_sp"],
                                        kho_kk,
                                        it["ton_he_thong"],
                                        it["sl_thuc_te"],
                                        it["chenh_lech"],
                                        st.session_state.name,
                                        ghi_chu_kk
                                    ]
                                    if append_row("Kiem_Ke", row_kk):
                                        success_count += 1
                                
                                if success_count == len(items_diff):
                                    st.success(f"✅ Đã cân kho thành công {success_count} sản phẩm có chênh lệch tại kho **{kho_kk}**!")
                                    st.session_state.kk_items = [{"sku": T("chon"), "sl_thucte": 0, "last_sku": T("chon")}]
                                    st.session_state.kk_form_key += 1
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"Chỉ ghi nhận được {success_count}/{len(items_diff)} sản phẩm, vui lòng thử lại!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🕐 LỊCH SỬ KIỂM KÊ KHO</div>', unsafe_allow_html=True)
        df_kiem_ke = load_sheet("Kiem_Ke")
        if not df_kiem_ke.empty:
            st.dataframe(
                translate_columns(df_kiem_ke.tail(15).iloc[::-1]),
                use_container_width=True, hide_index=True
            )
            st.caption(f"Hiển thị 15 lần kiểm kê gần nhất | Tổng: {len(df_kiem_ke)} lần")
        else:
            st.info("Chưa có dữ liệu kiểm kê kho.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------------------------
        # NHẬP HÀNG VÀO KHO
        # ------------------------------------------------------------
        st.markdown('<div class="section-header">📥 NHẬP HÀNG VÀO KHO</div>', unsafe_allow_html=True)

        if not df_sp_full.empty:
            ds_sku_sp = df_sp_full['SKU Sản phẩm'].tolist() if 'SKU Sản phẩm' in df_sp_full.columns else []
            ds_ten_sp2 = df_sp_full['Tên sản phẩm'].tolist() if 'Tên sản phẩm' in df_sp_full.columns else []
            ds_sku_nk = [f"{s} — {t}" for s, t in zip(ds_sku_sp, ds_ten_sp2)]

            if "nk_items" not in st.session_state:
                st.session_state.nk_items = [{"sku": T("chon"), "sl": 1}]
            if "nk_form_key" not in st.session_state:
                st.session_state.nk_form_key = 0

            col_nk1, col_nk2 = st.columns([1, 2])
            with col_nk1:
                kho_nhap = st.selectbox("🏭 Kho nhập *", ["Nam", "Bắc"], key=f"nk_kho_{st.session_state.nk_form_key}")
            with col_nk2:
                ghi_chu_nk = st.text_input("📝 Ghi chú chung", placeholder="Nhập lý do, nguồn hàng...", key=f"nk_ghichu_{st.session_state.nk_form_key}")

            st.markdown("**📦 Danh sách sản phẩm nhập:**")

            for i, item in enumerate(st.session_state.nk_items):
                col_a, col_b, col_c = st.columns([3, 1, 0.3])
                with col_a:
                    sku_sel = st.selectbox(
                        f"Sản phẩm {i+1}",
                        [T("chon")] + ds_sku_nk,
                        key=f"nk_sku_{st.session_state.nk_form_key}_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.nk_items[i]["sku"] = sku_sel
                with col_b:
                    sl_sel = st.number_input(
                        f"SL {i+1}", min_value=1, value=item["sl"],
                        key=f"nk_sl_{st.session_state.nk_form_key}_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.nk_items[i]["sl"] = sl_sel
                with col_c:
                    if st.button("✕", key=f"nk_del_{st.session_state.nk_form_key}_{i}") and len(st.session_state.nk_items) > 1:
                        st.session_state.nk_items.pop(i)
                        st.rerun()

            if st.button("➕ Thêm sản phẩm", key=f"nk_add_{st.session_state.nk_form_key}"):
                st.session_state.nk_items.append({"sku": T("chon"), "sl": 1})
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✅ XÁC NHẬN NHẬP KHO", key=f"btn_nhap_kho_{st.session_state.nk_form_key}"):
                valid_items = [it for it in st.session_state.nk_items if it["sku"] != T("chon")]
                if not valid_items:
                    st.error("Vui lòng chọn ít nhất 1 sản phẩm!")
                else:
                    success_count = 0
                    ngay_nk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for it in valid_items:
                        sku_code_nk = it["sku"].split(" — ")[0]
                        ten_sp_nk = it["sku"].split(" — ")[1] if " — " in it["sku"] else ""
                        row_nk = [ngay_nk, sku_code_nk, ten_sp_nk, it["sl"], kho_nhap, st.session_state.name, ghi_chu_nk]
                        if append_row("Nhap_Kho", row_nk):
                            success_count += 1
                    if success_count == len(valid_items):
                        st.success(f"✅ Đã nhập {success_count} sản phẩm vào kho {kho_nhap}!")
                        st.session_state.nk_items = [{"sku": T("chon"), "sl": 1}]
                        st.session_state.nk_form_key += 1
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Chỉ nhập được {success_count}/{len(valid_items)} sản phẩm, vui lòng thử lại!")

        st.markdown("<br>", unsafe_allow_html=True)

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
            try:
                cols = df_ck_raw.columns.tolist()
                if len(cols) >= 4:
                    df_ck_plot = df_ck_raw.copy()
                    col_thang = cols[0]
                    col_bac = cols[1]
                    col_nam = cols[2]
                    col_tong = cols[3]

                    df_ck_plot[col_bac] = df_ck_plot[col_bac].apply(parse_num)
                    df_ck_plot[col_nam] = df_ck_plot[col_nam].apply(parse_num)
                    df_ck_plot[col_tong] = df_ck_plot[col_tong].apply(parse_num)

                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df_ck_plot[col_thang], y=df_ck_plot[col_bac], name='Miền Bắc', marker_color='#10b981', hovertemplate='%{y:,.0f} đ'))
                    fig.add_trace(go.Bar(x=df_ck_plot[col_thang], y=df_ck_plot[col_nam], name='Miền Nam', marker_color='#34d399', hovertemplate='%{y:,.0f} đ'))
                    fig.add_trace(go.Bar(x=df_ck_plot[col_thang], y=df_ck_plot[col_tong], name='TỔNG', marker_color='#00b87c', hovertemplate='%{y:,.0f} đ'))
                    fig.update_layout(
                        title={'text': T("bieu_do_title"), 'x': 0.5, 'font': {'color': '#0f172a', 'size': 14, 'family': 'Plus Jakarta Sans'}},
                        barmode='group', height=400,
                        xaxis=dict(tickfont=dict(color='#475569')),
                        yaxis=dict(gridcolor='#f1f5f9', tickfont=dict(color='#475569')),
                        legend=dict(font=dict(color='#0f172a'), orientation="h", y=1.1),
                        paper_bgcolor='#ffffff',
                        plot_bgcolor='#ffffff',
                        margin=dict(l=10, r=10, t=40, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Đang tải biểu đồ... ({e})")

        st.markdown('<div class="section-header">📋 THỐNG KÊ PO</div>', unsafe_allow_html=True)
        df_dash_ck = load_sheet("Dashboard")



        if not df_dash_ck.empty:
            try:
                col1, col2 = st.columns(2)
                n_rows = df_dash_ck.shape[0]
                n_cols = df_dash_ck.shape[1]

                def safe_iloc(r, c):
                    if r < n_rows and c < n_cols:
                        return df_dash_ck.iloc[r, c]
                    return 0

                with col1:
                    st.markdown("<div style='font-weight:800; color:#0f172a; margin-bottom:8px;'>📍 Miền Nam</div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("SL PO", int(parse_num(safe_iloc(17, 0))))
                    with c2: st.metric("Min", fmt_currency(parse_num(safe_iloc(19, 0))))
                    with c3: st.metric("Max", fmt_currency(parse_num(safe_iloc(21, 0))))
                    with c4: st.metric("Avg", fmt_currency(parse_num(safe_iloc(23, 0))))
                with col2:
                    st.markdown("<div style='font-weight:800; color:#0f172a; margin-bottom:8px;'>📍 Miền Bắc</div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.metric("SL PO", int(parse_num(safe_iloc(17, 1))))
                    with c2: st.metric("Min", fmt_currency(parse_num(safe_iloc(19, 1))))
                    with c3: st.metric("Max", fmt_currency(parse_num(safe_iloc(21, 1))))
                    with c4: st.metric("Avg", fmt_currency(parse_num(safe_iloc(23, 1))))
            except Exception as e:
                st.warning(f"Lỗi hiển thị PO: {e}")

        st.markdown('<div class="section-header">🏷️ PHÂN TÍCH SKU</div>', unsafe_allow_html=True)
        col_top, col_slow = st.columns(2)

        def safe_get(df, r, c):
            try:
                if r < df.shape[0] and c < df.shape[1]:
                    v = df.iloc[r, c]
                    return v if str(v).strip() not in ["", "nan", "None"] else None
            except Exception:
                pass
            return None

        with col_top:
            st.markdown(f'🔥 **{T("sku_chay")}**')
            try:
                rows_top = [16, 17, 18]
                skus = [safe_get(df_dash_ck, r, 4) for r in rows_top]
                sls  = [safe_get(df_dash_ck, r, 5) for r in rows_top]
                data_top = [(s, q) for s, q in zip(skus, sls) if s is not None]
                if data_top:
                    st.table(pd.DataFrame(data_top, columns=[T("ma_sku"), T("san_luong")]))
                else:
                    st.info("Chưa có dữ liệu.")
            except Exception as e:
                st.info(f"Lỗi đọc SKU chạy: {e}")

        with col_slow:
            st.markdown(f'⚠️ **{T("sku_cham")}**')
            try:
                rows_slow = [21, 22, 23]
                skus = [safe_get(df_dash_ck, r, 4) for r in rows_slow]
                sls  = [safe_get(df_dash_ck, r, 5) for r in rows_slow]
                data_slow = [(s, q) for s, q in zip(skus, sls) if s is not None]
                if data_slow:
                    st.table(pd.DataFrame(data_slow, columns=[T("ma_sku"), T("san_luong")]))
                else:
                    st.info("Chưa có dữ liệu.")
            except Exception as e:
                st.info(f"Lỗi đọc SKU chậm: {e}")
