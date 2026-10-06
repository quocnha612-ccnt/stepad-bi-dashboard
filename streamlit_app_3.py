st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

* { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}

/* 1. Ép toàn bộ khung nền và màu chữ chính */
.stApp { 
    background-color: #f8fafc !important; 
    color: #0f172a !important; 
}
.stApp > header { 
    background-color: transparent !important; 
}

/* 2. Fix chữ trên thanh TABS (cả tab chọn và chưa chọn) */
button[data-baseweb="tab"] {
    background-color: transparent !important;
}
button[data-baseweb="tab"] div,
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span { 
    color: #475569 !important; 
    font-weight: 700 !important; 
    font-size: 0.95rem !important;
    opacity: 1 !important;
}
button[aria-selected="true"] {
    background-color: #ffffff !important;
}
button[aria-selected="true"] div,
button[aria-selected="true"] p,
button[aria-selected="true"] span { 
    color: #00b87c !important; 
    font-weight: 800 !important; 
}
div[data-baseweb="tab-highlight"] { 
    background-color: #00b87c !important; 
    height: 3px !important;
}
div[data-baseweb="tab-border"] { 
    background-color: #cbd5e1 !important; 
}

/* 3. Fix tiêu đề nhãn FORM (Label) */
label, .stWidgetLabel, .stWidgetLabel p, [data-testid="stWidgetLabel"] {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    opacity: 1 !important;
}

/* 4. Fix triệt để giá trị hiển thị bên trong ô SELECTBOX / DROPDOWN */
div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {
    background-color: #ffffff !important;
}
div[data-baseweb="menu"] li {
    color: #0f172a !important;
}

/* 5. Fix ô nhập TEXT, NUMBER, DATE, TEXTAREA */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
    background-color: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* 6. Nút bấm xanh ngọc */
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
}

/* 7. Metric Cards */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] { 
    color: #00b87c !important; 
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] { 
    color: #475569 !important; 
    font-weight: 700 !important;
}

/* 8. Section Header & Khung Logo */
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