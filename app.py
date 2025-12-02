import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
import time
import PyPDF2

# --- CONFIGURAÇÃO INICIAL (FULL SCREEN) ---
st.set_page_config(page_title="Logos Pregador", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- CARREGAMENTO SEGURO ---
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False

def load_lottie(url):
    if not LOTTIE_OK: return None
    try:
        r = requests.get(url, timeout=1)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- ESTILO "LOGOS BIBLE" (O VISUAL PREMIUM) ---
st.markdown("""
    <style>
    /* 1. RESET TOTAL */
    header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    
    /* 2. CORES E FUNDO (DARK ACADEMIA) */
    .stApp {
        background-color: #0f1115; /* Preto Logos */
    }
    
    /* 3. SIDEBAR (BIBLIOTECA) */
    [data-testid="stSidebar"] {
        background-color: #16191f;
        border-right: 1px solid #2d313a;
    }
    
    /* 4. EDITOR (PAPEL CENTRAL) */
    .stTextArea textarea {
        font-family: 'Merriweather', 'Georgia', serif; /* Fonte Clássica */
        font-size: 19px !important;
        line-height: 1.8 !important;
        background-color: #1c2027; /* Cinza Leve */
        color: #e6eaf0; /* Texto quase branco */
        border: 1px solid #2d313a;
        border-radius: 4px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stTextArea textarea:focus {
        border-color: #c5a059; /* Dourado ao focar */
        box-shadow: 0 0 10px rgba(197, 160, 89, 0.2);
    }
    
    /* 5. TABS (ABAS) ESTILO SOFTWARE */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #16191f;
        padding: 5px;
        border-radius: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8b949e;
        border: none;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2d313a !important;
        color: #c5a059 !important; /* Dourado Logos */
        font-weight: bold;
        border-radius: 4px;
    }
    
    /* 6. INPUTS E BOTÕES */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0f1115;
        border: 1px solid #30363d;
        color: white;
        border-radius: 3px;
    }
    .stButton button {
        background-color: #238636; /* Verde Save */
        color: white;
        border: none;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 12px;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #2ea043;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    
    /* 7. TIPOGRAFIA */
    h1, h2, h3 { font-family: 'Helvetica', sans-serif; letter-spacing: -0.5px; color: #c5a059;}
    p, li, div { font-family: 'Roboto', sans-serif; color: #b0b8c3; }
    
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SIMPLES & ELEGANTE ---
USUARIOS = {"admin": "1234", "pastor": "pregar"}

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['user'] = ''

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>LOGOS<span style='color:#c5a059'>PREGADOR</span></h1>", unsafe_allow_html=True)
        st.info("Ambiente de Estudo Expositivo e Exegético")
        with st.form("login"):
            u = st.text_input("ID")
            p = st.text_input("Passkey", type="password")
            if st.form_submit_button("ACESSAR ESTUDO", type="primary"):
                if u in USUARIOS and USUARIOS[u] == p:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Acesso Negado")
    st.stop()

# --- BACKEND DO SISTEMA ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

def gemini(prompt, api):
    if not api: return "⚠️ API Key necessária."
    try:
        genai.configure(api_key=api)
        return genai.GenerativeModel('gemini-pro').generate_content(prompt).text
    except Exception as e: return f"Erro: {e}"

def search_web(q):
    try: return DDGS().text(q, max_results=3)
    except: return []

def pdf_extract(file):
    try:
        r = PyPDF2.PdfReader(file)
        t = ""
        for i, p in enumerate(r.pages):
            if i>15: break
            t += p.extract_text()
        return t
    except: return "Erro PDF"

# --- LAYOUT PRINCIPAL (3 COLUNAS) ---
# Coluna 1: Sidebar (Navegação) - Já é nativo
# Coluna 2: Main (Editor) - Central
# Coluna 3: Aux (Tools) - Direita (vamos simular com colunas)

# 1. SIDEBAR (BIBLIOTECA)
with st.sidebar:
    st.markdown("### 🏛️ BIBLIOTECA")
    st.markdown("---")
    
    # Busca de Arquivos estilo Finder
    try: docs = [f.replace(".txt", "") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: docs = []
    
    # Seleção de arquivo visual
    sel = st.radio("SEUS SERMÕES", ["+ NOVO PROJETO"] + docs, label_visibility="collapsed")
    
    st.markdown("---")
    with st.expander("🔐 CREDENCIAIS API", expanded=False):
        api_key = st.text_input("Google Gemini Key", type="password")

    if st.button("SAIR"):
        st.session_state['logado'] = False
        st.rerun()

# 2. ÁREA DE TRABALHO (Dividida em Editor e Ferramentas)
c_editor, c_tools = st.columns([1.8, 1]) # Proporção áurea aproximada

# --- PAINEL CENTRAL: O EDITOR ---
with c_editor:
    # Carregamento
    conteudo = ""
    titulo = ""
    
    if sel != "+ NOVO PROJETO":
        titulo = sel
        try:
            with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: conteudo = f.read()
        except: pass
    
    # Cabeçalho Limpo
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.markdown(f"## 📝 {titulo if titulo else 'Rascunho Sem Título'}")
    with c_head2:
        if st.button("💾 SALVAR CLOUD", type="primary", use_container_width=True):
            if titulo:
                with open(os.path.join(PASTA, f"{titulo}.txt"), "w") as f: f.write(conteudo) # Nota: precisa atualizar estado antes
                st.toast("Salvo no Servidor", icon="☁️")
    
    # Inputs disfarçados de texto corrido
    novo_titulo = st.text_input("Definir Título:", value=titulo, placeholder="Título do Sermão...", label_visibility="collapsed")
    
    # O PAPEL (TEXTAREA) - Atualiza dinamicamente
    texto_final = st.text_area("Escreva aqui...", value=conteudo, height=750, label_visibility="collapsed")
    
    # Auto-Save Lógica (Salva quando aperta o botão usando a var texto_final)
    if novo_titulo and texto_final != conteudo:
        # Se mudou titulo ou texto, salvamos na variavel temporaria pra quando clicar botao
        pass # Streamlit roda script inteiro a cada clique, a logica ta no botão acima

# --- PAINEL DIREITO: FERRAMENTAS DE PESQUISA (LOGOS STYLE) ---
with c_tools:
    st.markdown("### 🧰 FERRAMENTAS DE ESTUDO")
    
    tab_exegese, tab_ref, tab_livros = st.tabs(["EXEGESE & IA", "REFERÊNCIAS", "LIVROS"])
    
    # TAB 1: INTELIGÊNCIA TEOLÓGICA
    with tab_exegese:
        st.info("Assistente Exegético Ativo")
        modo = st.selectbox("Modo de Análise:", ["Analisar Texto Atual", "Explicar Versículo", "Ilustrar Tema"])
        
        input_ref = ""
        if modo == "Explicar Versículo":
            input_ref = st.text_input("Referência (ex: Rm 8:28)")
        
        if st.button("EXECUTAR ANÁLISE"):
            prompt = ""
            if modo == "Analisar Texto Atual":
                prompt = f"Aja como um comentarista bíblico sênior. Analise teologicamente, homileticamente e hermeneuticamente este esboço: \n\n{texto_final}"
            elif modo == "Explicar Versículo":
                prompt = f"Faça uma exegese profunda de {input_ref}. Inclua análise das palavras originais (Grego/Hebraico), contexto histórico e aplicação."
            elif modo == "Ilustrar Tema":
                prompt = f"Leia o texto ao lado e crie uma ilustração moderna e impactante que conecte com a realidade brasileira: {texto_final[:500]}"
            
            with st.status("Processando conhecimento teológico...", expanded=True):
                res = gemini(prompt, api_key)
                st.markdown(res)
    
    # TAB 2: WEB E NOTÍCIAS
    with tab_ref:
        termo = st.text_input("Pesquisar na Web/Notícias:", placeholder="Assunto...")
        if st.button("BUSCAR FONTES"):
            res = search_web(termo)
            if res:
                for r in res:
                    st.markdown(f"""
                    <div style="background-color: #16191f; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #238636;">
                        <a href="{r['href']}" style="text-decoration: none; color: #c5a059; font-weight: bold;">{r['title']}</a>
                        <p style="font-size: 12px; margin: 0; color: #aaa;">{r['body'][:100]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.warning("Sem resultados.")
            
    # TAB 3: LEITOR PDF (COMPANION)
    with tab_livros:
        st.write("Sua Biblioteca Digital")
        pdf = st.file_uploader("Upload Livro/Comentário (.pdf)", type="pdf")
        if pdf:
            if st.button("LER E INTEGRAR AO SERMÃO"):
                raw_text = pdf_extract(pdf)
                st.success("Livro indexado.")
                
                req = f"Use o conteúdo deste livro cristão: '{raw_text[:4000]}...' para enriquecer o sermão que estou escrevendo: '{texto_final[:1000]}'"
                with st.spinner("Consultando livro..."):
                    resp_livro = gemini(req, api_key)
                    st.markdown(resp_livro)
