import streamlit as st

# --- 1. CONFIGURAÇÃO INICIAL (Layout Expandido) ---
st.set_page_config(page_title="O Pregador Supremo", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. IMPORTAÇÕES SEGURAS (Blindagem contra Tela Preta) ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    import os
    import requests
    import PyPDF2
except ImportError as e:
    st.error(f"Erro de Instalação: {e}. Verifique o requirements.txt")
    st.stop()

# --- 3. ESTILO VISUAL "LOGOS GOLD" (CSS Supremo) ---
st.markdown("""
<style>
    /* Reset e Fundo Dark Premium */
    header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem; max-width: 98%;}
    .stApp {background-color: #0b0d10;} /* Preto Profundo */
    
    /* Efeito DOURADO no Título */
    .gold-text {
        background: linear-gradient(to bottom, #cfc09f 22%, #634f2c 24%, #cfc09f 26%, #cfc09f 27%, #ffecb3 40%, #3a2c0f 78%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        color: #fff; 
        font-family: 'Times New Roman', serif;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #111318;
        border-right: 1px solid #333;
    }
    
    /* O Papel (Editor) */
    .stTextArea textarea {
        font-family: 'Georgia', 'Merriweather', serif; /* Fonte Clássica */
        font-size: 19px !important;
        line-height: 1.7 !important;
        background-color: #16191f;
        color: #d1d5db;
        border: 1px solid #2d313a;
        padding: 25px;
        border-radius: 4px;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);
    }
    .stTextArea textarea:focus {
        border-color: #D4AF37; /* Borda Dourada ao digitar */
    }
    
    /* Botões Premium */
    .stButton button {
        background-color: #1f2329;
        color: #9da5b4;
        border: 1px solid #3e4451;
        font-weight: 600;
        border-radius: 3px;
        text-transform: uppercase;
        font-size: 12px;
    }
    .stButton button:hover {
        border-color: #D4AF37;
        color: #D4AF37; /* Texto dourado ao passar mouse */
        background-color: #2c313a;
    }
    
    /* Inputs de Texto */
    .stTextInput input {
        background-color: #0b0d10;
        color: white;
        border: 1px solid #333;
    }
    
    /* Abas do Menu */
    .stTabs [data-baseweb="tab-list"] { background-color: #0b0d10; }
    .stTabs [aria-selected="true"] {
        background-color: #16191f !important;
        border-top: 2px solid #D4AF37 !important;
        color: #D4AF37 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES LÓGICAS DO SISTEMA ---
def login():
    if 'logado' not in st.session_state:
        st.session_state.update({'logado': False, 'user': ''})

    # Dicionário de Senhas
    usuarios = {"admin": "1234", "pastor": "pregar", "obreiro": "jesus"}

    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            # Título Dourado na Tela de Login
            st.markdown("<h1 style='text-align: center;'><span class='gold-text' style='font-size: 50px'>O PREGADOR</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666; font-size: 14px'>AMBIENTE DE ESTUDOS AVANÇADO</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.form("frm_login"):
                u = st.text_input("USUÁRIO")
                s = st.text_input("SENHA", type="password")
                if st.form_submit_button("ACESSAR BIBLIOTECA", type="primary"):
                    if u in usuarios and usuarios[u] == s:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas.")
        return False
    return True

# Bloqueia se não estiver logado
if not login(): st.stop()

# --- VARIÁVEIS DO USUÁRIO ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# --- FUNÇÕES INTELIGENTES (CÉREBRO GOOGLE) ---
def ai_gemini(prompt, key, system_role=""):
    if not key: return "⚠️ API Key não configurada."
    try:
        genai.configure(api_key=key)
        # Instrução de Persona para a IA
        full_prompt = f"{system_role}\n\nPERGUNTA DO PREGADOR: {prompt}"
        return genai.GenerativeModel('gemini-pro').generate_content(full_prompt).text
    except Exception as e: return f"Erro na IA: {e}"

def get_news(term):
    try: return DDGS().news(keywords=term, region="br-pt", max_results=3)
    except: return []

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        # Lê até 30 páginas para não sobrecarregar
        for i, p in enumerate(reader.pages):
            if i > 30: break
            text += p.extract_text()
        return text
    except: return "Erro na leitura do PDF."

# --- 5. INTERFACE PRINCIPAL ---

# >>>> BARRA LATERAL (MENU)
with st.sidebar:
    # Logo Dourado Pequeno
    st.markdown("<h2 class='gold-text' style='text-align: left; font-size: 24px'>✝ O PREGADOR</h2>", unsafe_allow_html=True)
    st.caption(f"Licença: {USER.upper()}")
    
    st.divider()
    
    # 1. API KEY (SEGREDO OU MANUAL)
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    if not api_key:
        api_key = st.text_input("CHAVE GOOGLE (API)", type="password")
        if not api_key:
            st.warning("⚠️ Insira a chave para usar a IA.")
    else:
        st.success("IA Ativada e Pronta")

    st.markdown("---")
    
    # 2. BIBLIOTECA DE ARQUIVOS
    st.markdown("<p style='color:#D4AF37; font-weight:bold'>MINHA BIBLIOTECA</p>", unsafe_allow_html=True)
    try: docs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: docs = []
    
    selecao = st.radio("SELECIONAR:", ["+ NOVO PROJETO"] + docs)
    
    st.divider()
    if st.button("SAIR (LOGOUT)"):
        st.session_state['logado'] = False
        st.rerun()

# >>>> ÁREA DE TRABALHO (EDITOR + TOOLS)
c_edit, c_tools = st.columns([1.8, 1])

# COLUNA DO EDITOR
with c_edit:
    # Lógica de Carregamento
    content = ""
    title_val = ""
    
    if selecao != "+ NOVO PROJETO":
        title_val = selecao
        try:
            with open(os.path.join(PASTA, f"{selecao}.txt"), "r") as f: content = f.read()
        except: pass

    # Cabeçalho do Editor
    c_tit, c_btn = st.columns([3, 1])
    with c_tit:
        new_title = st.text_input("TEMA DA MENSAGEM", value=title_val, placeholder="Título do Sermão...", label_visibility="collapsed")
    with c_btn:
        if st.button("💾 GRAVAR CLOUD", use_container_width=True, type="primary"):
            if new_title:
                with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(content) # Salva estado anterior
                st.toast("Projeto Salvo na Nuvem", icon="☁️")

    # O PAPEL (TEXT AREA)
    text_area = st.text_area("Papel", value=content, height=720, label_visibility="collapsed")
    
    # Gambiarra para salvar o texto novo quando aperta botão
    if new_title and text_area != content:
        with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(text_area)

# COLUNA DAS FERRAMENTAS
with c_tools:
    st.markdown("<p style='color:#D4AF37; font-weight:bold; margin-bottom: 10px'>FERRAMENTAS AUXILIARES</p>", unsafe_allow_html=True)
    
    tab_ia, tab_biblia, tab_web, tab_pdf = st.tabs(["CÉREBRO IA", "BÍBLIA", "WEB/NEWS", "LIVROS"])
    
    # 1. IA CHAT
    with tab_ia:
        st.info("Assistente Teológico Conectado.")
        acao = st.selectbox("Comando:", ["Analisar Esboço", "Sugerir Tópicos", "Criar Introdução", "Aplicação Prática"])
        
        if st.button("EXECUTAR COMANDO"):
            if not new_title: st.warning("Dê um título primeiro.")
            else:
                persona = "Você é um assistente teológico sábio, conservador e eloquente."
                p = f"Ação: {acao}. Título: {new_title}. Texto atual: {text_area[:1500]}"
                with st.spinner("Analisando teologia..."):
                    res = ai_gemini(p, api_key, persona)
                    st.markdown(res)

    # 2. BÍBLIA & EXEGESE
    with tab_biblia:
        ref = st.text_input("Passagem (Ex: Efésios 2:8)")
        if st.button("REALIZAR EXEGESE"):
            prompt = f"Faça uma análise exegética de {ref}. 1. Texto original (Grego/Hebraico). 2. Contexto Histórico. 3. Significado Teológico."
            st.write(ai_gemini(prompt, api_key))

    # 3. NOTÍCIAS
    with tab_web:
        busca = st.text_input("Tema Atual:")
        if st.button("BUSCAR FONTES"):
            news = get_news(busca)
            if news:
                for n in news: st.markdown(f"🔹 [{n['title']}]({n['url']})")
                st.write(ai_gemini(f"Crie uma ponte entre '{busca}' e o evangelho usando estas notícias: {news}", api_key))
            else: st.warning("Sem resultados.")

    # 4. LEITOR PDF
    with tab_pdf:
        pdf_file = st.file_uploader("Arrastar PDF aqui", type="pdf")
        if pdf_file and st.button("LER DOCUMENTO"):
            with st.spinner("Indexando livro..."):
                raw_text = read_pdf(pdf_file)
                st.success("Leitura Concluída!")
                st.markdown(ai_gemini(f"Resuma os principais insights teológicos deste texto para usar em sermão: {raw_text[:3000]}", api_key))
