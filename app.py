import os
import json
import base64
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (STREAMLIT)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Homer Custom - Oficina & Tunagem",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# PERSISTÊNCIA DE CONFIGURAÇÕES LOCAIS (LOGO, FOTOS 3x4 E PARÂMETROS)
# -----------------------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "oficina_config.json")

def load_oficina_config():
    default_cfg = {
        "logo_url": "",
        "margem_mecanica_padrao": 50.0,
        "deposito_padrao": 15.0,
        "fotos_usuarios": {}
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_cfg.update(saved)
        except Exception:
            pass
    return default_cfg

def save_oficina_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erro ao salvar config:", e)

def processar_upload_imagem(uploaded_file):
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.getvalue()
            b64 = base64.b64encode(bytes_data).decode()
            mime_type = uploaded_file.type or "image/png"
            return f"data:{mime_type};base64,{b64}"
        except Exception:
            return None
    return None

oficina_cfg = load_oficina_config()

# -----------------------------------------------------------------------------
# ESTILOS CSS CUSTOMIZADOS (DESIGN OFICINA MODERNA & MOBILE-FIRST)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Oculta completamente a barra lateral e a tarja preta superior nativa do Streamlit */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    header[data-testid="stHeader"], div[data-testid="stHeader"], .stAppHeader {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
        display: none !important;
    }

    /* Tipografia e espaçamentos gerais */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 720px !important;
    }

    /* Header Superior Moderno */
    .top-header-marker {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .user-avatar-3x4 {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
        flex-shrink: 0;
    }

    .user-avatar-placeholder {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 2px solid #3b82f6;
        color: #60a5fa;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .user-title-large {
        font-size: 1.35rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        letter-spacing: -0.02em !important;
        line-height: 1.1 !important;
        white-space: nowrap !important;
    }

    /* Botões Compactos no Topo (Tamanho Ícone) */
    .icon-btn-container div.stButton > button {
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .icon-btn-container div[data-testid="stPopover"] > button {
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Abas Ultra Modernas, Arredondadas (Pill) e Centralizadas */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        gap: 6px !important;
        background: rgba(15, 23, 42, 0.9) !important;
        padding: 6px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(51, 65, 85, 0.65) !important;
        overflow-x: auto !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.4) !important;
    }

    .stTabs [data-baseweb="tab"] {
        flex: 1 1 auto !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        padding: 9px 16px !important;
        color: #94a3b8 !important;
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        align-items: center !important;
        transition: all 0.25s ease-in-out !important;
        border: 1px solid transparent !important;
        white-space: nowrap !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #f8fafc !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.45) !important;
        border: 1px solid rgba(96, 165, 250, 0.6) !important;
        transform: scale(1.02) !important;
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Linhas de Itens: Centralização Vertical e Não-Quebra */
    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.7)) !important;
        border: 1px solid rgba(51, 65, 85, 0.75) !important;
        border-radius: 14px !important;
        padding: 9px 13px !important;
        margin-bottom: 8px !important;
        gap: 10px !important;
        min-height: 54px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) > div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: flex-start !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) > div[data-testid="column"]:last-child {
        flex: 0 0 110px !important;
        width: 110px !important;
        max-width: 110px !important;
        min-width: 95px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: flex-end !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) .stMarkdown p {
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        line-height: 1.1 !important;
    }

    .item-card-marker {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        flex-wrap: nowrap !important;
        white-space: nowrap !important;
        gap: 8px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .item-title-large {
        font-size: 1.16rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.01em !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    .item-sep {
        color: #64748b !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }

    .item-price-tag {
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        font-family: monospace !important;
        white-space: nowrap !important;
    }

    .item-price-tag.revenda { color: #60a5fa !important; }
    .item-price-tag.parceiro { color: #c084fc !important; }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) div[data-testid="stNumberInput"] {
        width: 100% !important;
        max-width: 110px !important;
        margin-bottom: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) div[data-baseweb="input"] {
        height: 38px !important;
        border-radius: 10px !important;
        background-color: #0b1120 !important;
        border: 1px solid rgba(59, 130, 246, 0.45) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) input[type="number"] {
        text-align: center !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        font-family: monospace !important;
        color: #ffffff !important;
        padding: 0 4px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) button[data-testid="stNumberInputStepDown"],
    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) button[data-testid="stNumberInputStepUp"] {
        width: 25px !important;
        height: 36px !important;
        padding: 0 !important;
        color: #cbd5e1 !important;
    }

    /* Banners e Métricas */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
    }
    
    .total-banner {
        background: linear-gradient(135deg, #1d4ed8 0%, #0f172a 100%);
        border: 1px solid rgba(96, 165, 250, 0.5);
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 12px 28px rgba(37, 99, 235, 0.3);
        margin: 16px 0;
    }

    .total-title {
        color: #bfdbfe;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 4px;
    }

    .total-value {
        color: #ffffff;
        font-size: 2.1rem;
        font-weight: 900;
        font-family: monospace;
        letter-spacing: -0.02em;
    }

    /* Crachá de Mecânico & Linha de Usuário Cadastrado */
    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-left: 5px solid #3b82f6 !important;
        border-radius: 14px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
        gap: 8px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row.is-master) {
        border-left: 5px solid #f59e0b !important;
        background: linear-gradient(135deg, #1c1917 0%, #1e293b 100%) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) > div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) > div[data-testid="column"]:not(:first-child) {
        flex: 0 0 42px !important;
        width: 42px !important;
        max-width: 42px !important;
        min-width: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) .stMarkdown p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) button {
        height: 38px !important;
        width: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        color: #ffffff !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) button:hover {
        background: rgba(59, 130, 246, 0.35) !important;
        border-color: #60a5fa !important;
        transform: scale(1.08) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.user-badge-row) button:disabled {
        opacity: 0.45 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    /* Linha de Peça no Painel Master */
    div[data-testid="stHorizontalBlock"]:has(.item-master-row) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.7)) !important;
        border: 1px solid rgba(59, 130, 246, 0.28) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        gap: 6px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row.parceiro) {
        border-color: rgba(192, 132, 252, 0.35) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row) > div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row) > div[data-testid="column"]:not(:first-child) {
        flex: 0 0 38px !important;
        width: 38px !important;
        max-width: 38px !important;
        min-width: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row) .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row) .stMarkdown p {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row) button {
        height: 36px !important;
        width: 36px !important;
        min-width: 36px !important;
        max-width: 36px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid rgba(59, 130, 246, 0.35) !important;
        color: #ffffff !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-master-row) button:hover {
        background: rgba(59, 130, 246, 0.35) !important;
        border-color: #60a5fa !important;
        transform: scale(1.08) !important;
    }

    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
    }

    .badge-chip-master {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }

    .badge-chip-operador {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.35);
    }

    .cred-box {
        background: rgba(2, 6, 23, 0.85);
        border: 1px solid rgba(51, 65, 85, 0.6);
        border-radius: 8px;
        padding: 4px 10px;
        font-family: monospace;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 6px;
    }

    /* Animação Push de Boas-Vindas (Duração de 2 segundos) */
    @keyframes pushWelcomeAnim {
        0% {
            opacity: 0;
            transform: translate(-50%, -35px) scale(0.92);
        }
        12% {
            opacity: 1;
            transform: translate(-50%, 0) scale(1.02);
        }
        20% {
            transform: translate(-50%, 0) scale(1);
        }
        78% {
            opacity: 1;
            transform: translate(-50%, 0) scale(1);
        }
        100% {
            opacity: 0;
            transform: translate(-50%, -45px) scale(0.92);
            visibility: hidden;
            display: none;
        }
    }

    @keyframes pushTimerBar {
        0% { width: 100%; }
        100% { width: 0%; }
    }

    .welcome-push-banner {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translate(-50%, 0);
        z-index: 9999999;
        width: 90%;
        max-width: 440px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 58, 138, 0.96));
        border: 2px solid #3b82f6;
        border-radius: 18px;
        padding: 14px 18px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.85), 0 0 25px rgba(59, 130, 246, 0.45);
        pointer-events: none;
        animation: pushWelcomeAnim 2.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .welcome-push-timer {
        width: 100%;
        height: 3px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 3px;
        margin-top: 10px;
        overflow: hidden;
    }

    .welcome-push-timer-bar {
        height: 100%;
        background: linear-gradient(90deg, #60a5fa, #3b82f6);
        animation: pushTimerBar 2.0s linear forwards;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DO SUPABASE (Lê variáveis de ambiente do Render ou fallback)
# -----------------------------------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mytpyxiiducuulyfelnl.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_IMeUV5B2f81iLEhE62-Ugw_A-n072W_")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"⚠️ Erro ao inicializar cliente Supabase: {e}")
    supabase = None

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE SESSÃO E LOGIN
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

def login_user(login, senha):
    if not supabase:
        st.error("Serviço do banco de dados indisponível.")
        return
    try:
        user_clean = login.strip().lower()
        pass_clean = senha.strip()
        
        response = supabase.table('usuarios').select('*').ilike('login', user_clean).execute()
        
        if not response.data or len(response.data) == 0:
            st.error(f"❌ Mecânico/Usuário '{login.strip()}' não encontrado no sistema.")
            return
            
        user_match = None
        for u in response.data:
            if str(u.get('senha', '')).strip() == pass_clean:
                user_match = u
                break
                
        if user_match:
            st.session_state['logged_in'] = True
            st.session_state['user_data'] = user_match
            st.session_state['show_welcome'] = True
            st.rerun()
        else:
            st.error("🔒 Senha incorreta. Verifique maiúsculas e caracteres digitados.")
    except Exception as e:
        st.error(f"Erro ao autenticar com o banco de dados: {e}")

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_data'] = None
    st.session_state['show_welcome'] = False
    st.rerun()

# -----------------------------------------------------------------------------
# TELA DE LOGIN (QUANDO NÃO ESTIVER LOGADO)
# -----------------------------------------------------------------------------
if not st.session_state['logged_in']:
    logo_topo = oficina_cfg.get("logo_url")
    if logo_topo:
        logo_html = f'<img src="{logo_topo}" style="width: 58px; height: 58px; border-radius: 16px; object-fit: cover; box-shadow: 0 8px 24px rgba(37,99,235,0.4); margin-bottom: 8px;" />'
    else:
        logo_html = '<div style="display: inline-block; background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 14px; border-radius: 18px; box-shadow: 0 8px 24px rgba(37,99,235,0.4); font-size: 1.9rem; margin-bottom: 8px;">⚡</div>'

    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #090d16 0%, #172554 50%, #1e1b4b 100%); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 18px; padding: 22px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6); margin-top: 1.2rem; margin-bottom: 1.2rem;">
            {logo_html}
            <h1 style="margin: 0; font-weight: 900; font-size: 1.8rem; color: #ffffff; letter-spacing: -0.02em;">HOMER CUSTOM</h1>
            <p style="color: #93c5fd; font-size: 0.85rem; font-weight: 600; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em;">
                🛠️ Garagem de Tunagem & Depósitos
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        with st.form("form_login_oficina"):
            st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #cbd5e1; margin-bottom: 6px;'>🔑 Identificação do Mecânico / Operador</p>", unsafe_allow_html=True)
            usuario_input = st.text_input("Usuário", placeholder="Ex: admin ou seu login", label_visibility="collapsed")
            senha_input = st.text_input("Senha", type="password", placeholder="Sua senha de acesso", label_visibility="collapsed")
            
            submit_btn = st.form_submit_button("🏎️ Entrar na Oficina", use_container_width=True, type="primary")
            
            if submit_btn:
                if usuario_input.strip() and senha_input.strip():
                    login_user(usuario_input, senha_input)
                else:
                    st.warning("Preencha o login e a senha.")
    st.stop()

# -----------------------------------------------------------------------------
# PUSH NOTIFICATION DE BOAS-VINDAS (ANIMAÇÃO AUTOMÁTICA DE 2 SEGUNDOS)
# -----------------------------------------------------------------------------
user = st.session_state['user_data']
is_master = (user.get('cargo') == 'master')
cargo_badge_color = "#f59e0b" if is_master else "#3b82f6"
cargo_icone = "👑" if is_master else "🛠️"

foto_user_logado = oficina_cfg.get("fotos_usuarios", {}).get(user['login'])

if st.session_state.get('show_welcome'):
    st.session_state['show_welcome'] = False
    
    if foto_user_logado:
        avatar_push = f'<img src="{foto_user_logado}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; border: 2px solid #60a5fa; box-shadow: 0 2px 10px rgba(59,130,246,0.5); flex-shrink: 0;" />'
    else:
        avatar_push = f'<div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #3b82f6; color: #60a5fa; font-size: 1.5rem; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{cargo_icone}</div>'

    st.markdown(f"""
        <div class="welcome-push-banner">
            <div style="display: flex; align-items: center; gap: 14px;">
                {avatar_push}
                <div style="min-width: 0;">
                    <div style="color: #ffffff; font-weight: 900; font-size: 1.12rem; letter-spacing: -0.01em; line-height: 1.2;">
                        Bem-vindo à Homer Custom! 🏎️
                    </div>
                    <div style="color: #bfdbfe; font-size: 0.82rem; margin-top: 2px;">
                        Mecânico <strong>{user['nome']}</strong> conectado com sucesso.
                    </div>
                </div>
            </div>
            <div class="welcome-push-timer">
                <div class="welcome-push-timer-bar"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA SUPERIOR (HEADER NO TOPO DA PÁGINA)
# Canto Esquerdo: Logo da Oficina + "Homer Custom"
# Canto Direito: Foto 3x4 + Nome do Usuário (Centralizado verticalmente) + Botões [⚙️] [🚪 Sair]
# -----------------------------------------------------------------------------
col_head_left, col_head_right = st.columns([1.1, 1.3])

with col_head_left:
    logo_atual = oficina_cfg.get("logo_url")
    if logo_atual:
        logo_left_html = f'<img src="{logo_atual}" style="width: 44px; height: 44px; border-radius: 12px; object-fit: cover; box-shadow: 0 4px 14px rgba(37,99,235,0.4); flex-shrink: 0;" />'
    else:
        logo_left_html = '<div style="background: linear-gradient(135deg, #2563eb, #1e4ed8); color: white; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.45rem; box-shadow: 0 4px 14px rgba(37,99,235,0.4); flex-shrink: 0;">⚡</div>'

    st.markdown(f"""
        <div class="top-header-marker">
            {logo_left_html}
            <div style="min-width: 0;">
                <h2 style="margin: 0; font-size: 1.35rem; font-weight: 900; color: #ffffff; letter-spacing: -0.02em; line-height: 1.1; white-space: nowrap;">Homer Custom</h2>
                <span style="color: #60a5fa; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; white-space: nowrap;">Oficina & Tunagem</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_head_right:
    # 1. Foto do Usuário + Nome + Cargo (Alinhados perfeitamente no topo)
    if foto_user_logado:
        avatar_html = f'<img src="{foto_user_logado}" class="user-avatar-3x4" alt="Foto 3x4" />'
    else:
        avatar_html = f'<div class="user-avatar-placeholder">{user["nome"][:1].upper()}</div>'

    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin-bottom: 6px;">
            {avatar_html}
            <div style="text-align: right; min-width: 0;">
                <div class="user-title-large">{user['nome']}</div>
                <div style="margin-top: 2px;">
                    <span style="background: rgba({ '245, 158, 11' if is_master else '59, 130, 246' }, 0.2); color: {cargo_badge_color}; border: 1px solid {cargo_badge_color}66; font-size: 0.7rem; font-weight: 800; padding: 2px 7px; border-radius: 6px; text-transform: uppercase; display: inline-flex; align-items: center; gap: 3px; white-space: nowrap;">
                        <span>{cargo_icone}</span> {user['cargo'].upper()}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Botões em tamanho de ícone: [⚙️ Engrenagem] depois [🚪 Sair]
    st.markdown('<div class="icon-btn-container">', unsafe_allow_html=True)
    c_space, c_gear_btn, c_exit_btn = st.columns([2.0, 1.0, 1.0])
    with c_gear_btn:
        with st.popover("⚙️", use_container_width=True):
            st.markdown("<p style='font-size: 0.8rem; font-weight: 800; margin-bottom: 6px;'>🎨 Modo Visual</p>", unsafe_allow_html=True)
            st.radio(
                "Tema",
                options=["🌙 Escuro (Oficina)", "☀️ Claro"],
                index=0,
                label_visibility="collapsed",
                key="radio_modo_visual"
            )
    with c_exit_btn:
        if st.button("🚪", key="btn_logout_top", use_container_width=True, help="Sair do sistema"):
            logout_user()
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# NAVEGAÇÃO PRINCIPAL EM ABAS NO TOPO:
# - "🧮 Cálculo"
# - "📋 Lista de Depósitos"
# - "⚙️ Painel Master" (Apenas para usuário com cargo de Master!)
# -----------------------------------------------------------------------------
if is_master:
    tab_calculo, tab_depositos, tab_master = st.tabs([
        "🧮 Cálculo",
        "📋 Lista de Depósitos",
        "⚙️ Painel Master"
    ])
else:
    tab_calculo, tab_depositos = st.tabs([
        "🧮 Cálculo",
        "📋 Lista de Depósitos"
    ])

# =============================================================================
# ABA 1: CÁLCULO (TUNAGEM, PEÇAS, PARCEIROS & TOTAL)
# =============================================================================
with tab_calculo:
    try:
        res_itens = supabase.table('itens').select('*').order('descricao').execute()
        lista_itens = res_itens.data if res_itens.data else []
    except Exception as e:
        lista_itens = []
        st.error(f"Erro ao carregar itens: {e}")

    itens_revenda = [i for i in lista_itens if i.get('tipo') == 'revenda']
    itens_parceiro = [i for i in lista_itens if i.get('tipo') == 'parceiro']

    # Sub-abas de Cálculo: Tunagem e Serviço | Peças Revenda | Itens Parceiros
    sub_tunagem, sub_pecas, sub_parceiros = st.tabs([
        "🔧 Tunagem & Serviço",
        f"📦 Peças Revenda ({len(itens_revenda)})",
        f"🤝 Itens Parceiros ({len(itens_parceiro)})"
    ])

    # --- SUB-ABA: TUNAGEM & SERVIÇO ---
    with sub_tunagem:
        st.markdown("<h4 style='margin-bottom: 8px; font-weight: 700;'>⚙️ Cálculo de Tunagem</h4>", unsafe_allow_html=True)
        
        val_base_tunagem = st.number_input(
            "Valor Base da Tunagem (R$)",
            min_value=0.0,
            step=50.0,
            format="%.2f",
            key="input_tunagem_base"
        )
        
        # Parâmetros: se for Master, pode alterar; se for Operador, fica bloqueado!
        perc_mecanica_default = float(oficina_cfg.get('margem_mecanica_padrao', 50.0))
        perc_deposito_default = float(oficina_cfg.get('deposito_padrao', 15.0))

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if is_master:
                perc_mecanica = st.number_input(
                    "Margem Mecânica (%)",
                    min_value=0.0,
                    value=perc_mecanica_default,
                    step=5.0,
                    key="input_margem_mec"
                )
            else:
                perc_mecanica = st.number_input(
                    "Margem Mecânica (%) 🔒",
                    value=perc_mecanica_default,
                    disabled=True,
                    key="input_margem_mec_disabled",
                    help="Configuração restrita ao usuário Master"
                )
        with col_m2:
            if is_master:
                perc_deposito = st.number_input(
                    "Depósito (%)",
                    min_value=0.0,
                    value=perc_deposito_default,
                    step=1.0,
                    key="input_perc_dep"
                )
            else:
                perc_deposito = st.number_input(
                    "Depósito (%) 🔒",
                    value=perc_deposito_default,
                    disabled=True,
                    key="input_perc_dep_disabled",
                    help="Configuração restrita ao usuário Master"
                )

        if not is_master:
            st.caption("🔒 *As porcentagens são fixadas pelo Chefe da Oficina (Master) nas configurações.*")

        total_tunagem = val_base_tunagem + (val_base_tunagem * (perc_mecanica / 100.0))
        val_deposito = total_tunagem * (perc_deposito / 100.0)

        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="color: #94a3b8; font-size: 0.85rem;">Margem Mecânica ({perc_mecanica:.0f}%):</span>
                    <span style="font-weight: 600; font-family: monospace;">+ R$ {(val_base_tunagem * (perc_mecanica / 100.0)):,.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 8px; border-top: 1px solid rgba(51,65,85,0.6);">
                    <span style="color: #ffffff; font-weight: 700;">Total da Tunagem:</span>
                    <span style="color: #4ade80; font-weight: 800; font-size: 1.15rem; font-family: monospace;">R$ {total_tunagem:,.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 8px; margin-top: 8px; border-top: 1px dashed rgba(245,158,11,0.5);">
                    <span style="color: #f59e0b; font-weight: 700;">Depósito Requerido ({perc_deposito:.0f}%):</span>
                    <span style="color: #fbbf24; font-weight: 800; font-size: 1.15rem; font-family: monospace;">R$ {val_deposito:,.2f}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- SUB-ABA: PEÇAS REVENDA ---
    with sub_pecas:
        st.markdown("<h4 style='margin-bottom: 12px; font-weight: 800; font-size: 1.15rem;'>📦 Peças de Revenda</h4>", unsafe_allow_html=True)
        subtotal_revenda = 0.0
        
        if not itens_revenda:
            st.info("Nenhuma peça cadastrada na categoria revenda.")
        else:
            for item in itens_revenda:
                c1, c2 = st.columns([3.5, 1.2])
                with c1:
                    st.markdown(f"""
                        <div class="item-card-marker">
                            <span class="item-title-large">{item['descricao']}</span>
                            <span class="item-sep">-</span>
                            <span class="item-price-tag revenda">R$ {float(item['valor']):,.2f}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    qtd = st.number_input(
                        "Qtd",
                        min_value=0,
                        max_value=9999,
                        step=1,
                        key=f"rev_{item['cod_item']}",
                        label_visibility="collapsed"
                    )
                    subtotal_revenda += qtd * float(item['valor'])
            
            st.markdown(f"""
                <div style="text-align: right; padding: 12px 14px; background: rgba(15,23,42,0.8); border: 1px solid rgba(59,130,246,0.3); border-radius: 12px; margin-top: 10px;">
                    <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">Subtotal Revenda: </span>
                    <strong style="color: #60a5fa; font-size: 1.15rem; font-family: monospace;">R$ {subtotal_revenda:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

    # --- SUB-ABA: ITENS PARCEIROS ---
    with sub_parceiros:
        st.markdown("<h4 style='margin-bottom: 12px; font-weight: 800; font-size: 1.15rem;'>🤝 Itens de Parceiros</h4>", unsafe_allow_html=True)
        subtotal_parceiros = 0.0
        
        if not itens_parceiro:
            st.info("Nenhum item de parceiro cadastrado.")
        else:
            for item in itens_parceiro:
                c1, c2 = st.columns([3.5, 1.2])
                with c1:
                    st.markdown(f"""
                        <div class="item-card-marker">
                            <span class="item-title-large">{item['descricao']}</span>
                            <span class="item-sep">-</span>
                            <span class="item-price-tag parceiro">R$ {float(item['valor']):,.2f}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    qtd_p = st.number_input(
                        "Qtd",
                        min_value=0,
                        max_value=9999,
                        step=1,
                        key=f"parc_{item['cod_item']}",
                        label_visibility="collapsed"
                    )
                    subtotal_parceiros += qtd_p * float(item['valor'])

            st.markdown(f"""
                <div style="text-align: right; padding: 12px 14px; background: rgba(15,23,42,0.8); border: 1px solid rgba(192,132,252,0.3); border-radius: 12px; margin-top: 10px;">
                    <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">Subtotal Parceiros: </span>
                    <strong style="color: #c084fc; font-size: 1.15rem; font-family: monospace;">R$ {subtotal_parceiros:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # RESUMO TOTAL GERAL
    # -------------------------------------------------------------------------
    total_geral = subtotal_revenda + subtotal_parceiros + total_tunagem

    st.markdown(f"""
        <div class="total-banner">
            <div class="total-title">Valor Final para o Cliente</div>
            <div class="total-value">R$ {total_geral:,.2f}</div>
            <div style="display: flex; justify-content: center; gap: 14px; margin-top: 8px; font-size: 0.75rem; color: #94a3b8; flex-wrap: wrap;">
                <span>Peças: <strong style="color: #e2e8f0;">R$ {subtotal_revenda:,.2f}</strong></span>
                <span>·</span>
                <span>Parceiros: <strong style="color: #e2e8f0;">R$ {subtotal_parceiros:,.2f}</strong></span>
                <span>·</span>
                <span>Tunagem: <strong style="color: #e2e8f0;">R$ {total_tunagem:,.2f}</strong></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SALVAR DEPÓSITO
    # -------------------------------------------------------------------------
    if val_deposito > 0:
        with st.expander("📝 Salvar Depósito no Supabase", expanded=True):
            st.markdown(f"""
                <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); padding: 10px 14px; border-radius: 12px; margin-bottom: 12px;">
                    <span style="color: #f59e0b; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;">Depósito Requerido:</span>
                    <span style="color: #fbbf24; font-size: 1.2rem; font-weight: 800; font-family: monospace; margin-left: 8px;">R$ {val_deposito:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_deposito_modern"):
                nome_cli = st.text_input("Nome do Cliente", placeholder="Ex: Roberto Carlos")
                veic_cli = st.text_input("Veículo / Placa", placeholder="Ex: Skyline R34 / ABC-1234")
                btn_salvar_dep = st.form_submit_button("Confirmar e Salvar Depósito", use_container_width=True, type="primary")
                
                if btn_salvar_dep:
                    if not nome_cli.strip():
                        st.error("Por favor, informe o nome do cliente.")
                    else:
                        try:
                            supabase.table('depositos').insert({
                                'cliente': nome_cli.strip(),
                                'veiculo': veic_cli.strip() if veic_cli else "N/A",
                                'valor_deposito': val_deposito,
                                'total_tunagem': total_tunagem
                            }).execute()
                            st.success("✅ Depósito registrado no Supabase com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")

# =============================================================================
# ABA 2: LISTA DE DEPÓSITOS
# =============================================================================
with tab_depositos:
    st.markdown("<h4 style='font-weight: 800; margin-bottom: 6px;'>📋 Depósitos Registrados</h4>", unsafe_allow_html=True)
    
    try:
        res_deps = supabase.table('depositos').select('*').order('cod_deposito', desc=True).execute()
        lista_deps = res_deps.data if res_deps.data else []
    except Exception as e:
        lista_deps = []
        st.error(f"Erro ao carregar depósitos: {e}")
    
    if len(lista_deps) == 0:
        st.info("Nenhum depósito registrado no momento.")
    else:
        st.caption(f"Total de {len(lista_deps)} registro(s) encontrado(s).")
        
        for dep in lista_deps:
            with st.container():
                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(51, 65, 85, 0.7); border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                            <div>
                                <strong style="font-size: 1rem; color: #ffffff;">{dep.get('cliente', 'Sem Nome')}</strong>
                                <span style="background: rgba(51,65,85,0.7); color: #cbd5e1; font-size: 0.72rem; padding: 2px 6px; border-radius: 6px; margin-left: 6px;">
                                    {dep.get('veiculo', 'N/A')}
                                </span>
                                <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">
                                    Cód: #{dep.get('cod_deposito')} · Data: {str(dep.get('data_criacao', ''))[:16]}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: #fbbf24; font-weight: 800; font-size: 1.15rem; font-family: monospace;">
                                    R$ {float(dep.get('valor_deposito', 0)):,.2f}
                                </div>
                                <div style="color: #94a3b8; font-size: 0.72rem;">
                                    Total: R$ {float(dep.get('total_tunagem', 0)):,.2f}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_sp, col_btn = st.columns([4, 1])
                with col_btn:
                    if st.button("🗑️ Excluir", key=f"del_dep_{dep['cod_deposito']}", use_container_width=True):
                        try:
                            supabase.table('depositos').delete().eq('cod_deposito', dep['cod_deposito']).execute()
                            st.success(f"Depósito #{dep['cod_deposito']} removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")

# =============================================================================
# ABA 3: PAINEL MASTER (VISÍVEL APENAS PARA QUEM TIVER O CARGO MASTER!)
# =============================================================================
if is_master:
    with tab_master:
        st.markdown("<h4 style='font-weight: 900; letter-spacing: -0.01em;'>⚙️ Painel Master de Administração</h4>", unsafe_allow_html=True)
        
        tab_users_master, tab_config_master, tab_itens_master = st.tabs([
            "👥 Equipe & Fotos 3x4",
            "⚙️ Parâmetros & Logo",
            "📦 Gerenciar Peças"
        ])
        
        # --- SUB-ABA 1: GERENCIAMENTO DE USUÁRIOS E FOTO 3x4 ---
        with tab_users_master:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid rgba(59,130,246,0.3); border-radius: 14px; padding: 14px; margin-bottom: 16px;">
                    <h5 style="margin: 0; color: #f8fafc; font-weight: 800;">🏁 Gerenciamento da Equipe Técnica</h5>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.78rem;">
                        Cadastre novos mecânicos ou operadores com importação de foto 3x4.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            with st.expander("⚡ Cadastrar Novo Mecânico / Operador", expanded=True):
                with st.form("form_novo_mecanico_oficina"):
                    c_nom, c_log = st.columns(2)
                    with c_nom:
                        nome_u = st.text_input("👤 Nome Completo", placeholder="Ex: Roberto Pitstop")
                    with c_log:
                        login_u = st.text_input("🔑 Login de Acesso", placeholder="Ex: roberto")

                    c_sen, c_carg = st.columns(2)
                    with c_sen:
                        senha_u = st.text_input("🔒 Senha de Acesso", type="password", placeholder="Digite a senha")
                    with c_carg:
                        cargo_u = st.selectbox(
                            "🏷️ Cargo / Acesso na Oficina",
                            options=["operador", "master"],
                            format_func=lambda x: "🛠️ Mecânico de Pista (Operador)" if x == "operador" else "👑 Chefe da Oficina (Master)"
                        )

                    foto_upload = st.file_uploader("📷 Importar Foto 3x4 do Mecânico (PNG, JPG)", type=["png", "jpg", "jpeg", "webp"], key="upload_foto_mecanico")
                    
                    st.caption("ℹ️ A foto 3x4 aparecerá no crachá e na barra superior ao lado do nome do mecânico.")
                    
                    btn_cadastrar_mecanico = st.form_submit_button("🏁 Adicionar Mecânico à Equipe", use_container_width=True, type="primary")
                    
                    if btn_cadastrar_mecanico:
                        nome_clean = nome_u.strip()
                        login_clean = login_u.strip().lower()
                        senha_clean = senha_u.strip()

                        if not nome_clean or not login_clean or not senha_clean:
                            st.warning("⚠️ Preencha Nome, Login e Senha para continuar.")
                        else:
                            try:
                                check_user = supabase.table('usuarios').select('login').ilike('login', login_clean).execute()
                                if check_user.data and len(check_user.data) > 0:
                                    st.error(f"⚠️ O login '{login_clean}' já está em uso por outro membro da oficina!")
                                else:
                                    # Salva usuário no banco de dados
                                    supabase.table('usuarios').insert({
                                        'nome': nome_clean,
                                        'login': login_clean,
                                        'senha': senha_clean,
                                        'cargo': cargo_u
                                    }).execute()

                                    # Se enviou foto 3x4, processa e salva na config local
                                    if foto_upload is not None:
                                        foto_b64 = processar_upload_imagem(foto_upload)
                                        if foto_b64:
                                            oficina_cfg.setdefault("fotos_usuarios", {})[login_clean] = foto_b64
                                            save_oficina_config(oficina_cfg)

                                    st.success(f"✅ Mecânico '{nome_clean}' registrado com sucesso!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar usuário: {e}")

            st.markdown("<h5 style='margin-top: 18px; margin-bottom: 10px; font-weight: 800;'>📋 Crachás da Equipe Cadastrada</h5>", unsafe_allow_html=True)
            
            try:
                res_users = supabase.table('usuarios').select('*').order('cargo', desc=True).order('nome').execute()
                users_cadastrados = res_users.data if res_users.data else []
            except Exception as e:
                users_cadastrados = []
                st.error(f"Erro ao listar equipe de mecânicos: {e}")

            if not users_cadastrados:
                st.info("Nenhum usuário cadastrado.")
            else:
                for u in users_cadastrados:
                    u_is_master = (u.get('cargo') == 'master')
                    chip_class = "badge-chip-master" if u_is_master else "badge-chip-operador"
                    cargo_label = "👑 Chefe da Oficina" if u_is_master else "🛠️ Mecânico de Pista"
                    
                    foto_membro = oficina_cfg.get("fotos_usuarios", {}).get(u['login'])
                    if foto_membro:
                        avatar_card = f'<img src="{foto_membro}" style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover; border: 2px solid #3b82f6; flex-shrink: 0;" />'
                    else:
                        avatar_card = f'<div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #3b82f6; color: #60a5fa; font-size: 1.15rem; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{"👑" if u_is_master else "🔧"}</div>'

                    # Card com informações e botões de ação integrados no mesmo quadro (centralizados na vertical)
                    col_info, col_edit, col_del = st.columns([5.5, 0.6, 0.6])
                    
                    with col_info:
                        master_cls = "is-master" if u_is_master else ""
                        st.markdown(f"""
                            <div class="user-badge-row {master_cls}">
                                <div style="display: flex; align-items: center; gap: 12px; min-width: 0;">
                                    {avatar_card}
                                    <div style="min-width: 0;">
                                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                            <strong style="color: #f8fafc; font-size: 1.05rem;">{u['nome']}</strong>
                                            <span class="badge-chip {chip_class}">{cargo_label}</span>
                                        </div>
                                        <div class="cred-box">
                                            Login: <span style="color: #60a5fa; font-weight: bold;">{u['login']}</span> &nbsp;|&nbsp; 
                                            Senha: <span style="color: #cbd5e1; font-weight: bold;">{u.get('senha', '***')}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col_edit:
                        if st.button("✏️", key=f"btn_edit_u_{u['cod_usuario']}", help=f"Alterar dados de {u['nome']}", use_container_width=True):
                            edit_key = f"editing_u_{u['cod_usuario']}"
                            st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                            st.rerun()
                            
                    with col_del:
                        if u['login'] != 'admin':
                            if st.button("🗑️", key=f"btn_del_u_{u['cod_usuario']}", help=f"Remover {u['nome']}", use_container_width=True):
                                try:
                                    supabase.table('usuarios').delete().eq('cod_usuario', u['cod_usuario']).execute()
                                    if u['login'] in oficina_cfg.get("fotos_usuarios", {}):
                                        del oficina_cfg["fotos_usuarios"][u['login']]
                                        save_oficina_config(oficina_cfg)
                                    st.success(f"Mecânico {u['nome']} removido!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {e}")
                        else:
                            st.button("🔒", key=f"btn_admin_lock_{u['cod_usuario']}", disabled=True, help="Administrador principal protegido", use_container_width=True)

                    # Painel de Alteração / Edição de Dados do Usuário
                    if st.session_state.get(f"editing_u_{u['cod_usuario']}", False):
                        with st.container():
                            st.markdown(f"""
                                <div style="background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(59, 130, 246, 0.45); border-radius: 14px; padding: 14px 16px; margin: -2px 0 14px 0; box-shadow: 0 8px 24px rgba(0,0,0,0.45);">
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                        <span style="color: #60a5fa; font-weight: 800; font-size: 0.95rem; display: flex; align-items: center; gap: 6px;">
                                            ✏️ Alterar Dados do Mecânico: <strong style="color: #ffffff;">{u['nome']}</strong>
                                        </span>
                                        <span style="font-size: 0.72rem; color: #94a3b8; font-family: monospace;">ID #{u['cod_usuario']}</span>
                                    </div>
                                    <p style="margin: 0; font-size: 0.75rem; color: #94a3b8;">Altere os dados de acesso, cargo ou importe uma nova foto 3x4.</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            with st.form(f"form_alterar_usuario_{u['cod_usuario']}"):
                                c_ed_nome, c_ed_log = st.columns(2)
                                with c_ed_nome:
                                    edit_nome = st.text_input("👤 Nome Completo", value=u.get('nome', ''))
                                with c_ed_log:
                                    edit_login = st.text_input("🔑 Login de Acesso", value=u.get('login', ''))
                                
                                c_ed_sen, c_ed_carg = st.columns(2)
                                with c_ed_sen:
                                    edit_senha = st.text_input("🔒 Senha de Acesso", value=u.get('senha', ''))
                                with c_ed_carg:
                                    cargo_options = ["operador", "master"]
                                    cargo_idx = 1 if u.get('cargo') == 'master' else 0
                                    edit_cargo = st.selectbox(
                                        "🏷️ Cargo / Acesso na Oficina",
                                        options=cargo_options,
                                        index=cargo_idx,
                                        format_func=lambda x: "🛠️ Mecânico de Pista (Operador)" if x == "operador" else "👑 Chefe da Oficina (Master)"
                                    )
                                
                                edit_foto_up = st.file_uploader(
                                    "📷 Importar Nova Foto 3x4 do Mecânico (PNG, JPG)",
                                    type=["png", "jpg", "jpeg", "webp"],
                                    key=f"edit_foto_upload_{u['cod_usuario']}"
                                )
                                
                                c_btn_salvar, c_btn_canc = st.columns(2)
                                with c_btn_salvar:
                                    btn_salvar_alt = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                                with c_btn_canc:
                                    btn_cancelar_alt = st.form_submit_button("❌ Cancelar", use_container_width=True)
                                
                                if btn_cancelar_alt:
                                    st.session_state[f"editing_u_{u['cod_usuario']}"] = False
                                    st.rerun()
                                    
                                if btn_salvar_alt:
                                    nome_c = edit_nome.strip()
                                    login_c = edit_login.strip().lower()
                                    senha_c = edit_senha.strip()
                                    
                                    if not nome_c or not login_c or not senha_c:
                                        st.warning("⚠️ Nome, Login e Senha não podem ficar vazios.")
                                    else:
                                        try:
                                            # Se o login mudou, verifica duplicidade
                                            if login_c != u['login'].lower():
                                                chk = supabase.table('usuarios').select('cod_usuario').ilike('login', login_c).execute()
                                                if chk.data and any(x['cod_usuario'] != u['cod_usuario'] for x in chk.data):
                                                    st.error(f"⚠️ O login '{login_c}' já está em uso por outro membro da oficina.")
                                                    st.stop()
                                                    
                                            supabase.table('usuarios').update({
                                                'nome': nome_c,
                                                'login': login_c,
                                                'senha': senha_c,
                                                'cargo': edit_cargo
                                            }).eq('cod_usuario', u['cod_usuario']).execute()
                                            
                                            old_login = u['login'].lower()
                                            if old_login in oficina_cfg.get("fotos_usuarios", {}) and old_login != login_c:
                                                oficina_cfg["fotos_usuarios"][login_c] = oficina_cfg["fotos_usuarios"].pop(old_login)
                                                
                                            if edit_foto_up is not None:
                                                b64_nova_foto = processar_upload_imagem(edit_foto_up)
                                                if b64_nova_foto:
                                                    oficina_cfg.setdefault("fotos_usuarios", {})[login_c] = b64_nova_foto
                                                    
                                            save_oficina_config(oficina_cfg)
                                            
                                            # Atualiza sessão se for o usuário logado
                                            if st.session_state['user_data'] and st.session_state['user_data'].get('cod_usuario') == u['cod_usuario']:
                                                st.session_state['user_data']['nome'] = nome_c
                                                st.session_state['user_data']['login'] = login_c
                                                st.session_state['user_data']['senha'] = senha_c
                                                st.session_state['user_data']['cargo'] = edit_cargo
                                                
                                            st.session_state[f"editing_u_{u['cod_usuario']}"] = False
                                            st.success(f"✅ Mecânico '{nome_c}' atualizado com sucesso!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Erro ao salvar alterações: {e}")

        # --- SUB-ABA 2: PARÂMETROS E LOGO DA OFICINA ---
        with tab_config_master:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid rgba(59,130,246,0.3); border-radius: 14px; padding: 14px; margin-bottom: 16px;">
                    <h5 style="margin: 0; color: #f8fafc; font-weight: 800;">⚙️ Parâmetros & Identidade da Oficina</h5>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.78rem;">
                        Altere a Logo da Oficina e defina as porcentagens padrão que ficam bloqueadas para operadores.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("form_oficina_parametros"):
                st.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #ffffff;'>🎨 Logo da Oficina</p>", unsafe_allow_html=True)
                logo_file_input = st.file_uploader("Upload da Logo (PNG, JPG)", type=["png", "jpg", "jpeg", "webp"], key="upload_logo_oficina")
                logo_url_input = st.text_input("Ou Link/URL da Imagem da Logo", value=oficina_cfg.get("logo_url", ""), placeholder="https://exemplo.com/logo.png")

                st.divider()

                st.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #ffffff;'>📊 Porcentagens Padrão da Mecânica</p>", unsafe_allow_html=True)
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    nova_margem = st.number_input(
                        "Margem Mecânica Padrão (%)",
                        min_value=0.0,
                        value=float(oficina_cfg.get("margem_mecanica_padrao", 50.0)),
                        step=5.0
                    )
                with c_p2:
                    novo_deposito = st.number_input(
                        "Porcentagem de Depósito Padrão (%)",
                        min_value=0.0,
                        value=float(oficina_cfg.get("deposito_padrao", 15.0)),
                        step=1.0
                    )

                btn_salvar_parametros = st.form_submit_button("💾 Salvar Parâmetros da Oficina", use_container_width=True, type="primary")

                if btn_salvar_parametros:
                    # Processa logo se enviada
                    if logo_file_input is not None:
                        b64_logo = processar_upload_imagem(logo_file_input)
                        if b64_logo:
                            oficina_cfg["logo_url"] = b64_logo
                    elif logo_url_input.strip():
                        oficina_cfg["logo_url"] = logo_url_input.strip()

                    oficina_cfg["margem_mecanica_padrao"] = nova_margem
                    oficina_cfg["deposito_padrao"] = novo_deposito
                    save_oficina_config(oficina_cfg)
                    st.success("✅ Parâmetros e Logo salvos com sucesso!")
                    st.rerun()

        # --- SUB-ABA 3: GERENCIAMENTO DE PEÇAS (SEPARAÇÃO POR ABAS) ---
        with tab_itens_master:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid rgba(59,130,246,0.3); border-radius: 14px; padding: 14px; margin-bottom: 16px;">
                    <h5 style="margin: 0; color: #f8fafc; font-weight: 800;">📦 Gerenciamento de Estoque & Peças</h5>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.78rem;">
                        Cadastre, altere e exclua peças de estoque separadas por abas: Revenda e Parceiros.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            with st.expander("➕ Cadastrar Nova Peça no Estoque", expanded=False):
                with st.form("form_novo_item_mod"):
                    c_desc, c_val = st.columns([2.5, 1.2])
                    with c_desc:
                        desc_item = st.text_input("Descrição da Peça", placeholder="Ex: Turbo T3/T4, Pastilha de Freio...")
                    with c_val:
                        valor_item = st.number_input("Preço Unitário (R$)", min_value=0.0, step=50.0, format="%.2f")
                    
                    tipo_item = st.selectbox(
                        "Categoria da Peça",
                        options=["revenda", "parceiro"],
                        format_func=lambda x: "📦 1 - Item Revenda (Oficina)" if x == "revenda" else "🤝 2 - Item Parceiro"
                    )
                    btn_item = st.form_submit_button("🏁 Cadastrar Peça", use_container_width=True, type="primary")
                    
                    if btn_item:
                        if desc_item.strip() and valor_item > 0:
                            try:
                                supabase.table('itens').insert({
                                    'descricao': desc_item.strip(),
                                    'valor': valor_item,
                                    'tipo': tipo_item
                                }).execute()
                                st.success(f"✅ Peça '{desc_item.strip()}' cadastrada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar: {e}")
                        else:
                            st.warning("⚠️ Preencha a descrição e um valor maior que zero.")

            # Carrega itens do banco
            try:
                res_itens = supabase.table('itens').select('*').order('descricao').execute()
                itens_cadastrados = res_itens.data if res_itens.data else []
            except Exception as e:
                itens_cadastrados = []
                st.error(f"Erro ao listar itens: {e}")

            # Separação dos itens em Revenda e Parceiros
            itens_revenda_master = [it for it in itens_cadastrados if it.get('tipo') == 'revenda']
            itens_parceiro_master = [it for it in itens_cadastrados if it.get('tipo') == 'parceiro']

            # Abas dedicadas conforme solicitado: 1 - Item Revenda e 2 - Item Parceiro
            tab_item_revenda, tab_item_parceiro = st.tabs([
                f"📦 1 - Itens Revenda ({len(itens_revenda_master)})",
                f"🤝 2 - Itens Parceiros ({len(itens_parceiro_master)})"
            ])

            def render_item_peca(it, tipo_categoria):
                cor_preco = "#60a5fa" if tipo_categoria == "revenda" else "#c084fc"
                badge_tipo = "REVENDA" if tipo_categoria == "revenda" else "PARCEIRO"
                cls_tipo = "revenda" if tipo_categoria == "revenda" else "parceiro"
                
                col_info, col_edit, col_del = st.columns([5.5, 0.6, 0.6])
                with col_info:
                    st.markdown(f"""
                        <div class="item-master-row {cls_tipo}">
                            <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; min-width: 0;">
                                <div style="min-width: 0;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <strong style="color: #ffffff; font-size: 1.05rem;">{it['descricao']}</strong>
                                        <span style="font-size: 0.68rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; background: rgba(15,23,42,0.8); border: 1px solid {cor_preco}; color: {cor_preco};">
                                            {badge_tipo}
                                        </span>
                                    </div>
                                    <div style="color: {cor_preco}; font-size: 0.95rem; font-family: monospace; font-weight: 800; margin-top: 2px;">
                                        R$ {float(it['valor']):,.2f}
                                    </div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                with col_edit:
                    if st.button("✏️", key=f"btn_edit_it_{it['cod_item']}", help=f"Alterar {it['descricao']}", use_container_width=True):
                        edit_key = f"editing_item_{it['cod_item']}"
                        st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                        st.rerun()
                        
                with col_del:
                    if st.button("🗑️", key=f"btn_del_it_{it['cod_item']}", help=f"Remover {it['descricao']}", use_container_width=True):
                        try:
                            supabase.table('itens').delete().eq('cod_item', it['cod_item']).execute()
                            st.success(f"Item '{it['descricao']}' removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")

                # Formulário inline de edição da peça
                if st.session_state.get(f"editing_item_{it['cod_item']}", False):
                    with st.container():
                        st.markdown(f"""
                            <div style="background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(59, 130, 246, 0.45); border-radius: 12px; padding: 12px 14px; margin: -2px 0 12px 0;">
                                <span style="color: #60a5fa; font-weight: 800; font-size: 0.9rem;">
                                    ✏️ Alterar Peça: <strong style="color: #ffffff;">{it['descricao']}</strong>
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        with st.form(f"form_editar_item_{it['cod_item']}"):
                            c_ed_desc, c_ed_val = st.columns([2.5, 1.2])
                            with c_ed_desc:
                                edit_desc = st.text_input("Descrição", value=it['descricao'])
                            with c_ed_val:
                                edit_val = st.number_input("Preço Unitário (R$)", value=float(it['valor']), min_value=0.0, step=50.0, format="%.2f")
                                
                            edit_tipo = st.selectbox(
                                "Categoria",
                                options=["revenda", "parceiro"],
                                index=0 if it.get('tipo') == 'revenda' else 1,
                                format_func=lambda x: "📦 1 - Item Revenda" if x == "revenda" else "🤝 2 - Item Parceiro"
                            )
                            
                            c_save_it, c_canc_it = st.columns(2)
                            with c_save_it:
                                btn_save_it = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                            with c_canc_it:
                                btn_canc_it = st.form_submit_button("❌ Cancelar", use_container_width=True)
                                
                            if btn_canc_it:
                                st.session_state[f"editing_item_{it['cod_item']}"] = False
                                st.rerun()
                                
                            if btn_save_it:
                                if edit_desc.strip() and edit_val > 0:
                                    try:
                                        supabase.table('itens').update({
                                            'descricao': edit_desc.strip(),
                                            'valor': edit_val,
                                            'tipo': edit_tipo
                                        }).eq('cod_item', it['cod_item']).execute()
                                        st.session_state[f"editing_item_{it['cod_item']}"] = False
                                        st.success(f"✅ Peça '{edit_desc.strip()}' atualizada!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao salvar: {e}")
                                else:
                                    st.warning("⚠️ Preencha descrição e valor válidos.")

            # --- CONTEÚDO DA ABA 1: ITENS REVENDA ---
            with tab_item_revenda:
                if not itens_revenda_master:
                    st.info("Nenhuma peça de revenda cadastrada.")
                else:
                    for it in itens_revenda_master:
                        render_item_peca(it, "revenda")

            # --- CONTEÚDO DA ABA 2: ITENS PARCEIROS ---
            with tab_item_parceiro:
                if not itens_parceiro_master:
                    st.info("Nenhuma peça de parceiro cadastrada.")
                else:
                    for it in itens_parceiro_master:
                        render_item_peca(it, "parceiro")
