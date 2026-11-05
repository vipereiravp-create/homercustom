import os
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (STREAMLIT)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Homer Custom - Calculadora & Depósitos",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS CUSTOMIZADOS (DESIGN MODERNO, MEIA-TELA & MOBILE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Estilo geral e tipografia */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Otimização de margens no topo */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 680px !important;
    }

    /* Cartão de Resumo e Destaques */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    
    .total-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e1b4b 100%);
        border: 1px solid rgba(96, 165, 250, 0.4);
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 12px 28px rgba(30, 58, 138, 0.35);
        margin: 18px 0;
    }

    .total-title {
        color: #93c5fd;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 4px;
    }

    .total-value {
        color: #ffffff;
        font-size: 2.1rem;
        font-weight: 900;
        font-family: monospace;
        letter-spacing: -0.02em;
    }

    .item-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(51, 65, 85, 0.7);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    /* Botões estilizados */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.55rem 1rem;
        transition: all 0.2s ease-in-out;
    }

    /* Abas modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: rgba(15, 23, 42, 0.8);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(51, 65, 85, 0.6);
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 14px;
        color: #94a3b8;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Entradas numéricas e formulários */
    input[type="number"], input[type="text"], input[type="password"] {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DO SUPABASE (Lê variáveis de ambiente do Render ou usa fallback)
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
        user_clean = login.lower().strip()
        pass_clean = senha.strip()
        response = supabase.table('usuarios').select('*').eq('login', user_clean).eq('senha', pass_clean).execute()
        if response.data and len(response.data) > 0:
            st.session_state['logged_in'] = True
            st.session_state['user_data'] = response.data[0]
            st.rerun()
        else:
            st.error("Login ou senha incorretos.")
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_data'] = None
    st.rerun()

# -----------------------------------------------------------------------------
# TELA DE LOGIN (MODERNA & RESPONSIVA)
# -----------------------------------------------------------------------------
if not st.session_state['logged_in']:
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;">
            <div style="display: inline-block; background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 16px; border-radius: 20px; box-shadow: 0 10px 20px rgba(37,99,235,0.3); font-size: 2rem;">
                ⚡
            </div>
            <h1 style="margin-top: 12px; margin-bottom: 2px; font-weight: 900; font-size: 1.8rem; color: #ffffff;">Homer Custom</h1>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0;">Calculadora de Serviços & Gestão de Depósitos</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        with st.form("form_login"):
            st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #cbd5e1; margin-bottom: 4px;'>Acesse sua conta</p>", unsafe_allow_html=True)
            usuario_input = st.text_input("Usuário", placeholder="Ex: admin", label_visibility="collapsed")
            senha_input = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
            submit_btn = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")
            
            if submit_btn:
                if usuario_input and senha_input:
                    login_user(usuario_input, senha_input)
                else:
                    st.warning("Preencha o login e a senha.")
    st.stop()

# -----------------------------------------------------------------------------
# CABEÇALHO SUPERIOR
# -----------------------------------------------------------------------------
user = st.session_state['user_data']

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="background: #2563eb; color: white; padding: 6px 10px; border-radius: 10px; font-weight: bold;">⚡</span>
            <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: #f8fafc;">Homer Custom</h3>
                <p style="margin: 0; font-size: 0.78rem; color: #94a3b8;">
                    <strong>{user['nome']}</strong> · <span style="color: #60a5fa;">{user['cargo'].upper()}</span>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
with header_col2:
    if st.button("Sair", use_container_width=True):
        logout_user()

st.write("")

# -----------------------------------------------------------------------------
# NAVEGAÇÃO PRINCIPAL (ABAS DE TOPO)
# -----------------------------------------------------------------------------
nav_opcoes = ["🧮 Calculadora", "📋 Depósitos"]
if user['cargo'] == 'master':
    nav_opcoes.append("⚙️ Painel Master")

nav_principal = st.radio("Navegação Principal", nav_opcoes, horizontal=True, label_visibility="collapsed")

st.divider()

# -----------------------------------------------------------------------------
# SEÇÃO 1: CALCULADORA COM SUB-ABAS (TUNAGEM, PEÇAS, PARCEIROS)
# -----------------------------------------------------------------------------
if nav_principal == "🧮 Calculadora":
    # Buscar itens do banco de dados
    try:
        res_itens = supabase.table('itens').select('*').order('descricao').execute()
        lista_itens = res_itens.data if res_itens.data else []
    except Exception as e:
        lista_itens = []
        st.error(f"Erro ao carregar itens: {e}")

    itens_revenda = [i for i in lista_itens if i.get('tipo') == 'revenda']
    itens_parceiro = [i for i in lista_itens if i.get('tipo') == 'parceiro']

    # Inicializar quantidades no session_state se necessário
    if 'qtd_revenda' not in st.session_state:
        st.session_state['qtd_revenda'] = {}
    if 'qtd_parceiro' not in st.session_state:
        st.session_state['qtd_parceiro'] = {}

    # SUB-ABAS PEDIDAS: Tunagem | Peças | Parceiros
    tab_tunagem, tab_pecas, tab_parceiros = st.tabs([
        "🔧 Tunagem & Serviços",
        f"📦 Peças Revenda ({len(itens_revenda)})",
        f"🤝 Itens Parceiro ({len(itens_parceiro)})"
    ])

    # --- SUB-ABA 1: TUNAGEM ---
    with tab_tunagem:
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

        # Cartão de métrica da Tunagem
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
                    <span style="color: #f59e0b; font-weight: 700;">Depósito Calculado ({perc_deposito:.0f}%):</span>
                    <span style="color: #fbbf24; font-weight: 800; font-size: 1.15rem; font-family: monospace;">R$ {val_deposito:,.2f}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- SUB-ABA 2: PEÇAS (REVENDA) ---
    with tab_pecas:
        st.markdown("<h4 style='margin-bottom: 8px; font-weight: 700;'>📦 Peças de Revenda</h4>", unsafe_allow_html=True)
        subtotal_revenda = 0.0
        
        if not itens_revenda:
            st.info("Nenhuma peça cadastrada na categoria revenda.")
        else:
            for item in itens_revenda:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{item['descricao']}**<br><span style='color: #60a5fa; font-family: monospace; font-size: 0.85rem;'>R$ {float(item['valor']):,.2f}</span>", unsafe_allow_html=True)
                with c2:
                    qtd = st.number_input("Qtd", min_value=0, step=1, key=f"rev_{item['cod_item']}", label_visibility="collapsed")
                    subtotal_revenda += qtd * float(item['valor'])
            
            st.markdown(f"""
                <div style="text-align: right; padding: 10px; background: rgba(15,23,42,0.7); border-radius: 10px; margin-top: 8px;">
                    <span style="color: #94a3b8; font-size: 0.85rem;">Subtotal Revenda: </span>
                    <strong style="color: #60a5fa; font-size: 1.1rem; font-family: monospace;">R$ {subtotal_revenda:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

    # --- SUB-ABA 3: ITENS PARCEIRO ---
    with tab_parceiros:
        st.markdown("<h4 style='margin-bottom: 8px; font-weight: 700;'>🤝 Itens de Parceiros</h4>", unsafe_allow_html=True)
        subtotal_parceiros = 0.0
        
        if not itens_parceiro:
            st.info("Nenhum item de parceiro cadastrado.")
        else:
            for item in itens_parceiro:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{item['descricao']}**<br><span style='color: #c084fc; font-family: monospace; font-size: 0.85rem;'>R$ {float(item['valor']):,.2f}</span>", unsafe_allow_html=True)
                with c2:
                    qtd_p = st.number_input("Qtd", min_value=0, step=1, key=f"parc_{item['cod_item']}", label_visibility="collapsed")
                    subtotal_parceiros += qtd_p * float(item['valor'])

            st.markdown(f"""
                <div style="text-align: right; padding: 10px; background: rgba(15,23,42,0.7); border-radius: 10px; margin-top: 8px;">
                    <span style="color: #94a3b8; font-size: 0.85rem;">Subtotal Parceiros: </span>
                    <strong style="color: #c084fc; font-size: 1.1rem; font-family: monospace;">R$ {subtotal_parceiros:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # RESUMO TOTAL GERAL (SEMPRE VISÍVEL)
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
    # REGISTRO DE DEPÓSITO
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

# -----------------------------------------------------------------------------
# SEÇÃO 2: LISTA DE DEPÓSITOS
# -----------------------------------------------------------------------------
elif nav_principal == "📋 Depósitos":
    st.markdown("<h4 style='font-weight: 800;'>📋 Depósitos Registrados</h4>", unsafe_allow_html=True)
    
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
        
        # Renderização em cards adaptáveis (ótimo para celular e meia tela)
        for dep in lista_deps:
            with st.container():
                st.markdown(f"""
                    <div class="item-card">
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
                
                # Botão de remoção rápida
                col_sp, col_btn = st.columns([4, 1])
                with col_btn:
                    if st.button("🗑️ Excluir", key=f"del_dep_{dep['cod_deposito']}", use_container_width=True):
                        try:
                            supabase.table('depositos').delete().eq('cod_deposito', dep['cod_deposito']).execute()
                            st.success(f"Depósito #{dep['cod_deposito']} removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")

# -----------------------------------------------------------------------------
# SEÇÃO 3: PAINEL MASTER (ADMIN)
# -----------------------------------------------------------------------------
elif nav_principal == "⚙️ Painel Master" and user['cargo'] == 'master':
    st.markdown("<h4 style='font-weight: 800;'>⚙️ Painel Master de Administração</h4>", unsafe_allow_html=True)
    
    tab_itens, tab_users = st.tabs(["📦 Gerenciar Peças/Itens", "👥 Gerenciar Usuários"])
    
    # GERENCIAMENTO DE ITENS
    with tab_itens:
        with st.expander("➕ Cadastrar Novo Item / Peça", expanded=False):
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

        # Listagem de itens existentes
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

    # GERENCIAMENTO DE USUÁRIOS
    with tab_users:
        with st.expander("➕ Cadastrar Novo Usuário", expanded=False):
            with st.form("form_novo_user_mod"):
                nome_u = st.text_input("Nome Completo", placeholder="Ex: Carlos Silva")
                login_u = st.text_input("Login de Acesso", placeholder="Ex: carlos")
                senha_u = st.text_input("Senha", type="password", placeholder="Senha de acesso")
                cargo_u = st.selectbox("Cargo", ["operador", "master"])
                btn_user = st.form_submit_button("Salvar Usuário", use_container_width=True, type="primary")
                
                if btn_user:
                    if nome_u.strip() and login_u.strip() and senha_u.strip():
                        try:
                            supabase.table('usuarios').insert({
                                'nome': nome_u.strip(),
                                'login': login_u.lower().strip(),
                                'senha': senha_u.strip(),
                                'cargo': cargo_u
                            }).execute()
                            st.success("Usuário cadastrado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar usuário: {e}")
                    else:
                        st.warning("Preencha todos os campos obrigatórios.")

        try:
            res_users = supabase.table('usuarios').select('cod_usuario, nome, login, cargo').order('nome').execute()
            users_cadastrados = res_users.data if res_users.data else []
        except Exception as e:
            users_cadastrados = []
            st.error(f"Erro ao listar usuários: {e}")

        st.write("")
        st.markdown(f"**Usuários Ativos ({len(users_cadastrados)})**")
        for u in users_cadastrados:
            col_u_info, col_u_del = st.columns([4, 1])
            with col_u_info:
                st.markdown(f"""
                    <div style="padding: 6px 0;">
                        <strong>{u['nome']}</strong> (<span style="color: #60a5fa;">{u.get('cargo', 'operador').upper()}</span>)
                        <div style="font-size: 0.8rem; color: #94a3b8;">Login: <code>{u['login']}</code></div>
                    </div>
                """, unsafe_allow_html=True)
            with col_u_del:
                if u['login'] != 'admin':
                    if st.button("Excluir", key=f"del_u_{u['cod_usuario']}", use_container_width=True):
                        try:
                            supabase.table('usuarios').delete().eq('cod_usuario', u['cod_usuario']).execute()
                            st.success("Usuário removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
