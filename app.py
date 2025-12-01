# --- INÍCIO DO BLOCO DE DESIGN PROFISSIONAL ---
st.markdown
    style
    /* 1. Fundo Geral (Cinza Chumbo Profissional) */
    .stApp {
        background-color: #0e1117;
    }
    
    /* 2. Barra Lateral (Estilo Couro Escuro com Borda Dourada) */
    [data-testid="stSidebar"] {
        background-color: #1a1c24;
        border-right: 2px solid #C5A059; /* Cor Dourada Clássica */
    }
    
    /* 3. Títulos e Textos */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
        color: #E0E0E0;
    }
    
    /* 4. O Papel de Escrita (A parte mais importante) */
    .stTextArea textarea {
        font-family: 'Merriweather', 'Georgia', serif; /* Fonte de Livro Teológico */
        font-size: 19px !important;
        line-height: 1.6 !important;
        background-color: #16171a; /* Fundo bem escuro para não cansar a vista */
        color: #dcdcdc; /* Texto cinza claro */
        border: 1px solid #333;
        border-radius: 4px;
        padding: 15px;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.5); /* Sombra interna */
    }
    
    /* 5. Botões (Estilo Premium) */
    .stButton button {
        background-color: #2b303b;
        color: white;
        border-radius: 6px;
        border: 1px solid #444;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton button:hover {
        border-color: #C5A059; /* Fica dourado ao passar o mouse */
        color: #C5A059;
        background-color: #1a1c24;
    }
    
    /* 6. Limpeza Visual (Remove menu padrão do Streamlit) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 7. Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c24;
        border-radius: 4px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C5A059 !important; /* Aba selecionada fica dourada */
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --- FIM DO BLOCO DE DESIGN ---
import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import time

# --- TENTA IMPORTAR ANIMAÇÕES (SEM TRAVAR O APP) ---
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# --- 2. SISTEMA DE LOGIN ---
USUARIOS = {
    "admin": "1234",
    "pastor": "pregar",
    "visitante": "jesus"
}

def load_lottie_url(url):
    """Tenta baixar a animação."""
    if not LOTTIE_OK:
        return None
    try:
        r = requests.get(url, timeout=1.5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Carrega animação da entrada
anim_entrada = load_lottie_url("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")
anim_ia = load_lottie_url("https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json")

def verificar_login():
    """Tela de Login"""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.write("")
            st.write("")
            if anim_entrada:
                st_lottie(anim_entrada, height=150, key="intro")
            else:
                st.markdown("<h1 style='text-align: center;'>✝️</h1>", unsafe_allow_html=True)
            
            st.markdown("<h2 style='text-align: center;'>Bem-vindo ao O Pregador</h2>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                user = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                btn_entrar = st.form_submit_button("Entrar no Sistema", type="primary")
                
                if btn_entrar:
                    if user in USUARIOS and USUARIOS[user] == senha:
                        st.session_state['logado'] = True
                        st.session_state['usuario_atual'] = user
                        st.rerun()
                    else:
                        st.error("Acesso negado. Tente novamente.")
        return False
    return True

if not verificar_login():
    st.stop()

# --- DAQUI PRA BAIXO SÓ RODA DEPOIS DO LOGIN ---
USUARIO_ATUAL = st.session_state['usuario_atual']

# --- 3. CONFIGURAÇÃO DE ARQUIVOS ---
PASTA_RAIZ = "Banco_Sermoes"
PASTA_USER = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)
if not os.path.exists(PASTA_USER):
    os.makedirs(PASTA_USER)

# --- 4. FUNÇÕES DO SISTEMA ---
def consultar_gemini(prompt, chave):
    if not chave:
        return "⚠️ Cole a chave API no menu."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro Google: {e}"

def buscar_noticias(tema):
    try:
        res = DDGS().news(keywords=tema, region="br-pt", max_results=3)
        return res if res else []
    except:
        return []

# --- 5. VISUAL ESTILO THEWORD ---
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    [data-testid="stSidebar"] {background-color: #2b2b2b;}
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 18px !important;
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #444;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. INTERFACE PRINCIPAL ---

# MENU LATERAL
with st.sidebar:
    st.markdown("### ✝️ O Pregador")
    st.caption(f"Logado como: {USUARIO_ATUAL}")
    
    if st.button("Sair (Logout)"):
        st.session_state['logado'] = False
        st.rerun()
        
    st.divider()
    with st.expander("🔐 Chave Google API"):
        api_key = st.text_input("Cole aqui", type="password")
        
    st.markdown("---")
    # LISTAGEM SEGURA
    try:
        arquivos = [f for f in os.listdir(PASTA_USER) if f.endswith(".txt")]
    except:
        arquivos = []
    
    arquivo_atual = st.radio("Seus Estudos:", ["+ Novo Estudo"] + arquivos)

# COLUNAS: EDITOR E FERRAMENTAS
col_esq, col_dir = st.columns([2.5, 1.5])

# ESQUERDA: EDITOR DE TEXTO
with col_esq:
    titulo_padrao = ""
    conteudo_padrao = ""
    
    if arquivo_atual != "+ Novo Estudo":
        titulo_padrao = arquivo_atual.replace(".txt", "")
        try:
            with open(os.path.join(PASTA_USER, arquivo_atual), "r") as f:
                conteudo_padrao = f.read()
        except:
            pass
        
    novo_titulo = st.text_input("Título da Mensagem", value=titulo_padrao)
    texto = st.text_area("Esboço", value=conteudo_padrao, height=650)
    
    if st.button("💾 Salvar Estudo", type="primary"):
        if novo_titulo:
            with open(os.path.join(PASTA_USER, f"{novo_titulo}.txt"), "w") as f:
                f.write(texto)
            st.toast("Estudo salvo com sucesso!", icon="✅")

# DIREITA: FERRAMENTAS
with col_dir:
    aba1, aba2, aba3 = st.tabs(["📖 Bíblia", "🏛️ Análise", "📰 Notícias"])
    
    # ABA BÍBLIA
    with aba1:
        st.caption("Comparar Traduções")
        ref = st.text_input("Versículo (ex: Jo 14:6)")
        if st.button("Comparar"):
            if not api_key:
                st.warning("Precisa da Chave Google.")
            else:
                resp = consultar_gemini(f"Traga {ref} na NVI, Almeida e Grego. Explique diferenças.", api_key)
                st.markdown(resp)
                
    # ABA ANÁLISE (IA)
    with aba2:
        st.caption("Raio-X Teológico")
        if st.button("Analisar Esboço"):
            if not api_key:
                st.warning("Precisa da Chave Google.")
            else:
                with st.status("Consultando teologia...", expanded=True):
                    if anim_ia:
                        st_lottie(anim_ia, height=60, key="loading")
                    analise = consultar_gemini(f"Faça uma análise homilética e teológica deste texto: {texto[:1000]}...", api_key)
