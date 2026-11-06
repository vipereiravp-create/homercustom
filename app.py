import os
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
# ESTILOS CSS CUSTOMIZADOS (BARRA NO TOPO, SEM SIDEBAR, MOBILE & MEIA-TELA)
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
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 720px !important;
    }

    /* Header Superior Moderno */
    .top-navbar {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

    /* Banners e Cartões da Garagem */
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

    /* Crachá de Mecânico */
    .mechanic-badge {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 5px solid #3b82f6;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    
    .mechanic-badge.master-badge {
        border-left: 5px solid #f59e0b;
        background: linear-gradient(135deg, #1c1917 0%, #1e293b 100%);
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

    /* Abas de Navegação Principal e Sub-abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: rgba(15, 23, 42, 0.9);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(51, 65, 85, 0.6);
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 9px 16px;
        color: #94a3b8;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        font-weight: 800;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    }

    /* Botões */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease-in-out;
    }

    input[type="number"], input[type="text"], input[type="password"] {
        border-radius: 10px !important;
    }

    /* -------------------------------------------------------------
       LINHAS DE ITENS: RESPONSIVAS, COMPACTAS E ALINHADAS LADO A LADO
       (Ordem compacta: Nome do Item - R$ X.XXX,XX  |  [ Qtd ])
       ------------------------------------------------------------- */
    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.7)) !important;
        border: 1px solid rgba(51, 65, 85, 0.75) !important;
        border-radius: 14px !important;
        padding: 9px 13px !important;
        margin-bottom: 8px !important;
        gap: 10px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) > div[data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.item-card-marker) > div[data-testid="column"]:last-child {
        flex: 0 0 110px !important;
        width: 110px !important;
        max-width: 110px !important;
        min-width: 95px !important;
    }

    .item-card-marker {
        display: flex !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 6px 8px !important;
    }

    /* Tipografia: Nome do item maior e preço na frente */
    .item-title-large {
        font-size: 1.16rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.01em !important;
        line-height: 1.2 !important;
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

    .item-price-tag.revenda {
        color: #60a5fa !important;
    }

    .item-price-tag.parceiro {
        color: #c084fc !important;
    }

    /* Campo de quantidade ultra compacto para até 4 dígitos */
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
        padding: 0 !important;
        color: #cbd5e1 !important;
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
            st.toast(f"Bem-vindo à oficina, {user_match['nome']}!", icon="🏎️")
            st.rerun()
        else:
            st.error("🔒 Senha incorreta. Verifique maiúsculas e caracteres digitados.")
    except Exception as e:
        st.error(f"Erro ao autenticar com o banco de dados: {e}")

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_data'] = None
    st.rerun()

# -----------------------------------------------------------------------------
# TELA DE LOGIN (QUANDO NÃO ESTIVER LOGADO)
# -----------------------------------------------------------------------------
if not st.session_state['logged_in']:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #090d16 0%, #172554 50%, #1e1b4b 100%); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 18px; padding: 22px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6); margin-top: 1rem; margin-bottom: 1.2rem;">
            <div style="display: inline-block; background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 14px; border-radius: 18px; box-shadow: 0 8px 24px rgba(37,99,235,0.4); font-size: 1.9rem; margin-bottom: 8px;">
                ⚡
            </div>
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
# BARRA SUPERIOR (HEADER NO TOPO DA PÁGINA)
# Canto Esquerdo: "Homer Custom"
# Canto Direito: Usuário Logado, Cargo e Botão Sair
# -----------------------------------------------------------------------------
user = st.session_state['user_data']
is_master = (user.get('cargo') == 'master')
cargo_badge_color = "#f59e0b" if is_master else "#3b82f6"
cargo_icone = "👑" if is_master else "🛠️"

col_head_left, col_head_right = st.columns([1.7, 1.3])

with col_head_left:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 4px 0;">
            <div style="background: linear-gradient(135deg, #2563eb, #1e4ed8); color: white; width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.35rem; box-shadow: 0 4px 14px rgba(37,99,235,0.4); flex-shrink: 0;">
                ⚡
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.3rem; font-weight: 900; color: #ffffff; letter-spacing: -0.02em; line-height: 1.1;">Homer Custom</h2>
                <span style="color: #60a5fa; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">Oficina & Tunagem</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_head_right:
    c_user_meta, c_btn_exit = st.columns([2.3, 1])
    with c_user_meta:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 2px;">
                <div style="font-weight: 800; font-size: 0.9rem; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {user['nome']}
                </div>
                <div style="margin-top: 2px;">
                    <span style="background: rgba({ '245, 158, 11' if is_master else '59, 130, 246' }, 0.18); color: {cargo_badge_color}; border: 1px solid {cargo_badge_color}55; font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 6px; text-transform: uppercase; display: inline-flex; align-items: center; gap: 3px;">
                        <span>{cargo_icone}</span> {user['cargo'].upper()}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c_btn_exit:
        if st.button("Sair", key="btn_logout_top", use_container_width=True):
            logout_user()
        
        # Botão de engrenagem abaixo do botão Sair com menu de cores/tema
        with st.popover("⚙️", use_container_width=True):
            st.markdown("<p style='font-size: 0.8rem; font-weight: 800; margin-bottom: 6px;'>🎨 Modo Visual</p>", unsafe_allow_html=True)
            tema_sel = st.radio(
                "Tema",
                options=["🌙 Escuro (Oficina)", "☀️ Claro"],
                index=0,
                label_visibility="collapsed",
                key="radio_modo_visual"
            )

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
    # Buscar itens do banco de dados Supabase
    try:
        res_itens = supabase.table('itens').select('*').order('descricao').execute()
        lista_itens = res_itens.data if res_itens.data else []
    except Exception as e:
        lista_itens = []
        st.error(f"Erro ao carregar itens: {e}")

    itens_revenda = [i for i in lista_itens if i.get('tipo') == 'revenda']
    itens_parceiro = [i for i in lista_itens if i.get('tipo') == 'parceiro']

    # Sub-abas de Cálculo: Tunagem | Peças | Parceiros
    sub_tunagem, sub_pecas, sub_parceiros = st.tabs([
        "🔧 Tunagem & Serviços",
        f"📦 Peças Revenda ({len(itens_revenda)})",
        f"🤝 Itens Parceiro ({len(itens_parceiro)})"
    ])

    # --- SUB-ABA: TUNAGEM ---
    with sub_tunagem:
        st.markdown("<h4 style='margin-bottom: 8px; font-weight: 700;'>⚙️ Cálculo de Tunagem</h4>", unsafe_allow_html=True)
        
        val_base_tunagem = st.number_input(
            "Valor Base da Tunagem (R$)",
            min_value=0.0,
            step=50.0,
            format="%.2f",
            key="input_tunagem_base"
        )
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            perc_mecanica = st.number_input(
                "Margem Mecânica (%)",
                min_value=0.0,
                value=50.0,
                step=5.0,
                key="input_margem_mec"
            )
        with col_m2:
            perc_deposito = st.number_input(
                "Depósito (%)",
                min_value=0.0,
                value=15.0,
                step=1.0,
                key="input_perc_dep"
            )

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

    # --- SUB-ABA: PEÇAS (REVENDA) ---
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

    # --- SUB-ABA: ITENS PARCEIRO ---
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
        
        tab_users_master, tab_itens_master = st.tabs([
            "👥 Equipe de Mecânicos & Usuários",
            "📦 Gerenciar Peças / Catálogo"
        ])
        
        # --- GERENCIAMENTO DE USUÁRIOS ---
        with tab_users_master:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid rgba(59,130,246,0.3); border-radius: 14px; padding: 14px; margin-bottom: 16px;">
                    <h5 style="margin: 0; color: #f8fafc; font-weight: 800;">🏁 Gerenciamento da Equipe Técnica</h5>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.78rem;">
                        Cadastre novos mecânicos ou operadores e defina o nível de acesso à oficina.
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
                    
                    st.caption("ℹ️ **Operador**: Acessa cálculo e depósitos. | **Master**: Acesso completo ao painel e equipe.")
                    
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
                                    supabase.table('usuarios').insert({
                                        'nome': nome_clean,
                                        'login': login_clean,
                                        'senha': senha_clean,
                                        'cargo': cargo_u
                                    }).execute()
                                    st.success(f"✅ Mecânico '{nome_clean}' registrado com sucesso!")
                                    st.toast(f"Mecânico {login_clean} cadastrado!", icon="🏎️")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar usuário no banco de dados: {e}")

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
                    badge_class = "master-badge" if u_is_master else ""
                    chip_class = "badge-chip-master" if u_is_master else "badge-chip-operador"
                    cargo_label = "👑 Chefe da Oficina" if u_is_master else "🛠️ Mecânico de Pista"
                    icone_avatar = "🏎️" if u_is_master else "🔧"

                    st.markdown(f"""
                        <div class="mechanic-badge {badge_class}">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                                <div>
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="font-size: 1.25rem;">{icone_avatar}</span>
                                        <div>
                                            <strong style="color: #f8fafc; font-size: 1rem;">{u['nome']}</strong>
                                            <div style="margin-top: 2px;">
                                                <span class="badge-chip {chip_class}">{cargo_label}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="cred-box">
                                        Login: <span style="color: #60a5fa; font-weight: bold;">{u['login']}</span> &nbsp;|&nbsp; 
                                        Senha: <span style="color: #cbd5e1; font-weight: bold;">{u.get('senha', '***')}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if u['login'] != 'admin':
                        col_espaco, col_del = st.columns([3, 1])
                        with col_del:
                            if st.button(f"🗑️ Remover", key=f"btn_del_u_{u['cod_usuario']}", use_container_width=True):
                                try:
                                    supabase.table('usuarios').delete().eq('cod_usuario', u['cod_usuario']).execute()
                                    st.success(f"Mecânico {u['nome']} removido!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {e}")

        # --- GERENCIAMENTO DE PEÇAS ---
        with tab_itens_master:
            with st.expander("➕ Cadastrar Nova Peça no Estoque", expanded=False):
                with st.form("form_novo_item_mod"):
                    desc_item = st.text_input("Descrição da Peça", placeholder="Ex: Turbo T3/T4")
                    valor_item = st.number_input("Preço Unitário (R$)", min_value=0.0, step=50.0, format="%.2f")
                    tipo_item = st.selectbox("Categoria", ["revenda", "parceiro"])
                    btn_item = st.form_submit_button("Cadastrar Peça", use_container_width=True, type="primary")
                    
                    if btn_item:
                        if desc_item.strip() and valor_item > 0:
                            try:
                                supabase.table('itens').insert({
                                    'descricao': desc_item.strip(),
                                    'valor': valor_item,
                                    'tipo': tipo_item
                                }).execute()
                                st.success("Peça cadastrada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar: {e}")
                        else:
                            st.warning("Preencha a descrição e um valor maior que zero.")

            try:
                res_itens = supabase.table('itens').select('*').order('tipo').order('descricao').execute()
                itens_cadastrados = res_itens.data if res_itens.data else []
            except Exception as e:
                itens_cadastrados = []
                st.error(f"Erro ao listar itens: {e}")

            st.write("")
            st.markdown(f"**Itens Cadastrados ({len(itens_cadastrados)})**")
            for it in itens_cadastrados:
                col_info, col_del = st.columns([4, 1])
                tipo_cor = "#60a5fa" if it.get('tipo') == 'revenda' else "#c084fc"
                with col_info:
                    st.markdown(f"""
                        <div style="padding: 6px 0;">
                            <strong>{it['descricao']}</strong> 
                            <span style="color: {tipo_cor}; font-size: 0.75rem; text-transform: uppercase; font-weight: bold;">[{it.get('tipo', 'revenda')}]</span>
                            <div style="font-family: monospace; font-size: 0.85rem; color: #94a3b8;">R$ {float(it['valor']):,.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    if st.button("Excluir", key=f"del_item_{it['cod_item']}", use_container_width=True):
                        try:
                            supabase.table('itens').delete().eq('cod_item', it['cod_item']).execute()
                            st.success("Item removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
