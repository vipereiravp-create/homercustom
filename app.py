
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DO SUPABASE
# -----------------------------------------------------------------------------
# Substitua pelas suas credenciais do painel do Supabase (Project Settings > API)
SUPABASE_URL = "https://mytpyxiiduoulyfelnl.supabase.co"
SUPABASE_KEY = "sb_publishable_IMeUV5B2f8i1LEhE62-Ugw_A-n072W_"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Configuração da página Streamlit
st.set_page_config(
    page_title="Homer Custom - Calculadora & Depósitos",
    page_icon="🛠️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE SESSÃO E LOGIN
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

def login_user(login, senha):
    try:
        response = supabase.table('usuarios').select('*').eq('login', login.lower().strip()).eq('senha', senha.strip()).execute()
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
# TELA DE LOGIN
# -----------------------------------------------------------------------------
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>⚡ Homer Custom</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Sistema de Calculadora & Depósitos</p>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário (Login)")
            senha_input = st.text_input("Senha", type="password")
            submit_btn = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit_btn:
                login_user(usuario_input, senha_input)
    st.stop()

# -----------------------------------------------------------------------------
# CABEÇALHO E MENU NAVEGAÇÃO
# -----------------------------------------------------------------------------
user = st.session_state['user_data']
st.sidebar.title("🛠️ Homer Custom")
st.sidebar.write(f"Usuário: **{user['nome']}** ({user['cargo'].upper()})")

menu_options = ["Calculadora", "Lista de Depósitos"]
if user['cargo'] == 'master':
    menu_options.append("Painel Master (Admin)")

aba_selecionada = st.sidebar.radio("Navegação", menu_options)

if st.sidebar.button("Sair / Logout", use_container_width=True):
    logout_user()

# -----------------------------------------------------------------------------
# ABA 1: CALCULADORA DE SERVIÇOS
# -----------------------------------------------------------------------------
if aba_selecionada == "Calculadora":
    st.header("🧮 Calculadora de Peças & Tunagem")
    
    # Buscar itens do banco de dados
    res_itens = supabase.table('itens').select('*').execute()
    lista_itens = res_itens.data if res_itens.data else []
    
    itens_revenda = [i for i in lista_itens if i.get('tipo') == 'revenda']
    itens_parceiro = [i for i in lista_itens if i.get('tipo') == 'parceiro']
    
    col_revenda, col_parceiro = st.columns(2)
    
    qtd_revenda = {}
    subtotal_revenda = 0.0
    with col_revenda:
        st.subheader("Revenda de Peças")
        for item in itens_revenda:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{item['descricao']}**  \nR$ {item['valor']:,.2f}")
            qtd = c2.number_input("Qtd", min_value=0, step=1, key=f"rev_{item['cod_item']}")
            qtd_revenda[item['cod_item']] = qtd
            subtotal_revenda += qtd * float(item['valor'])
        st.markdown(f"**Subtotal Revenda:** `R$ {subtotal_revenda:,.2f}`")

    qtd_parceiro = {}
    subtotal_parceiros = 0.0
    with col_parceiro:
        st.subheader("Itens Parceiros")
        for item in itens_parceiro:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{item['descricao']}**  \nR$ {item['valor']:,.2f}")
            qtd = c2.number_input("Qtd", min_value=0, step=1, key=f"parc_{item['cod_item']}")
            qtd_parceiro[item['cod_item']] = qtd
            subtotal_parceiros += qtd * float(item['valor'])
        st.markdown(f"**Subtotal Parceiros:** `R$ {subtotal_parceiros:,.2f}`")

    st.divider()
    
    # Cálculos de Tunagem
    st.subheader("Tunagem & Depósito")
    c_tun1, c_tun2 = st.columns(2)
    
    with c_tun1:
        val_base_tunagem = st.number_input("Valor Base da Tunagem (R$)", min_value=0.0, step=50.0)
        perc_mecanica = st.number_input("Margem Mecânica (%)", min_value=0.0, value=50.0, step=5.0)
        perc_deposito = st.number_input("Porcentagem Depósito (%)", min_value=0.0, value=15.0, step=1.0)

    total_tunagem = val_base_tunagem + (val_base_tunagem * (perc_mecanica / 100.0))
    val_deposito = total_tunagem * (perc_deposito / 100.0)
    total_geral = subtotal_revenda + subtotal_parceiros + total_tunagem

    with c_tun2:
        st.info(f"**Total Tunagem (com Margem):** R$ {total_tunagem:,.2f}")
        st.warning(f"**Valor do Depósito ({perc_deposito:.0f}%):** R$ {val_deposito:,.2f}")
        st.success(f"### Valor Total para o Cliente: R$ {total_geral:,.2f}")

    # Salvar Depósito no Supabase
    st.divider()
    if val_deposito > 0:
        st.subheader("Salvar Depósito na Nuvem")
        with st.form("form_deposito"):
            c_d1, c_d2 = st.columns(2)
            nome_cli = c_d1.text_input("Nome do Cliente")
            veic_cli = c_d2.text_input("Veículo / Placa")
            btn_salvar_dep = st.form_submit_button("Confirmar e Salvar Depósito")
            
            if btn_salvar_dep:
                if not nome_cli:
                    st.error("Digite o nome do cliente.")
                else:
                    supabase.table('depositos').insert({
                        'cliente': nome_cli,
                        'veiculo': veic_cli,
                        'valor_deposito': val_deposito,
                        'total_tunagem': total_tunagem
                    }).execute()
                    st.success("Depósito gravado no banco de dados Supabase com sucesso!")

# -----------------------------------------------------------------------------
# ABA 2: LISTA DE DEPÓSITOS
# -----------------------------------------------------------------------------
elif aba_selecionada == "Lista de Depósitos":
    st.header("📋 Depósitos Registrados")
    
    res_deps = supabase.table('depositos').select('*').order('cod_deposito', desc=True).execute()
    lista_deps = res_deps.data if res_deps.data else []
    
    if len(lista_deps) == 0:
        st.info("Nenhum depósito encontrado no banco de dados.")
    else:
        df_deps = pd.DataFrame(lista_deps)
        st.dataframe(df_deps[['cod_deposito', 'cliente', 'veiculo', 'valor_deposito', 'total_tunagem', 'data_criacao']], use_container_width=True)
        
        st.divider()
        st.subheader("Remover Depósito Concluído")
        cod_remover = st.number_input("Digite o Cód. do Depósito para remover", min_value=1, step=1)
        if st.button("Excluir Depósito"):
            supabase.table('depositos').delete().eq('cod_deposito', cod_remover).execute()
            st.success(f"Depósito {cod_remover} removido com sucesso!")
            st.rerun()

# -----------------------------------------------------------------------------
# ABA 3: PAINEL MASTER (ADMIN)
# -----------------------------------------------------------------------------
elif aba_selecionada == "Painel Master (Admin)" and user['cargo'] == 'master':
    st.header("⚙️ Painel Master de Administração")
    
    tab_itens, tab_users = st.tabs(["Gerenciar Itens/Peças", "Gerenciar Usuários"])
    
    # GERENCIAMENTO DE ITENS
    with tab_itens:
        st.subheader("Cadastrar Novo Item")
        with st.form("form_novo_item"):
            c_i1, c_i2, c_i3 = st.columns([3, 2, 2])
            desc_item = c_i1.text_input("Descrição da Peça")
            valor_item = c_i2.number_input("Preço (R$)", min_value=0.0, step=100.0)
            tipo_item = c_i3.selectbox("Tipo", ["revenda", "parceiro"])
            btn_item = st.form_submit_button("Cadastrar Item")
            
            if btn_item:
                if desc_item and valor_item > 0:
                    supabase.table('itens').insert({
                        'descricao': desc_item,
                        'valor': valor_item,
                        'tipo': tipo_item
                    }).execute()
                    st.success("Peça cadastrada no Supabase!")
                    st.rerun()
        
        st.subheader("Itens Existentes no Banco")
        res_itens = supabase.table('itens').select('*').order('cod_item').execute()
        if res_itens.data:
            df_itens = pd.DataFrame(res_itens.data)
            st.dataframe(df_itens, use_container_width=True)
            
            c_del1, c_del2 = st.columns([3, 1])
            cod_item_del = c_del1.number_input("Cód. Item para Excluir", min_value=1, step=1)
            if c_del2.button("Excluir Item"):
                supabase.table('itens').delete().eq('cod_item', cod_item_del).execute()
                st.success("Item excluído!")
                st.rerun()

    # GERENCIAMENTO DE USUÁRIOS
    with tab_users:
        st.subheader("Cadastrar Novo Usuário")
        with st.form("form_novo_user"):
            c_u1, c_u2, c_u3, c_u4 = st.columns([3, 2, 2, 2])
            nome_u = c_u1.text_input("Nome Completo")
            login_u = c_u2.text_input("Login")
            senha_u = c_u3.text_input("Senha", type="password")
            cargo_u = c_u4.selectbox("Cargo", ["operador", "master"])
            btn_user = st.form_submit_button("Cadastrar Usuário")
            
            if btn_user:
                if nome_u and login_u and senha_u:
                    supabase.table('usuarios').insert({
                        'nome': nome_u,
                        'login': login_u.lower().strip(),
                        'senha': senha_u.strip(),
                        'cargo': cargo_u
                    }).execute()
                    st.success("Usuário registrado no banco de dados!")
                    st.rerun()

        st.subheader("Usuários Cadastrados")
        res_users = supabase.table('usuarios').select('cod_usuario, nome, login, cargo').execute()
        if res_users.data:
            df_users = pd.DataFrame(res_users.data)
            st.dataframe(df_users, use_container_width=True)
            
            c_udel1, c_udel2 = st.columns([3, 1])
            cod_user_del = c_udel1.number_input("Cód. Usuário para Excluir", min_value=1, step=1)
            if c_udel2.button("Excluir Usuário"):
                supabase.table('usuarios').delete().eq('cod_usuario', cod_user_del).execute()
                st.success("Usuário excluído!")
                st.rerun()
