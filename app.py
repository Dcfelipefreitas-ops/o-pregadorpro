import json

def load_bible(version="acf"):
    try:
        path = f"Banco_Biblia/bibles/{version}.json"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"erro": str(e)}

import streamlit as st

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="O Pregador Supremo", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. IMPORTAÇÕES ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    import os
    import requests
    import PyPDF2
except ImportError as e:
    st.error(f"Erro de Instalação: {e}")
    st.stop()

# --- 3. ESTILO VISUAL "LOGOS GOLD" ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem; max-width: 98%;}
    .stApp {background-color: #0b0d10;}
    
    /* Título Dourado */
    .gold-text {
        background: linear-gradient(to bottom, #cfc09f 22%, #634f2c 24%, #cfc09f 26%, #cfc09f 27%, #ffecb3 40%, #3a2c0f 78%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        color: #fff; 
        font-family: 'Times New Roman', serif;
        font-weight: bold;
        letter-spacing: 2px;
    }
    
    [data-testid="stSidebar"] {background-color: #111318; border-right: 1px solid #333;}
    
    .stTextArea textarea {
        font-family: 'Georgia', serif;
        font-size: 19px !important;
        background-color: #16191f;
        color: #d1d5db;
        border: 1px solid #2d313a;
        padding: 25px;
        border-radius: 4px;
    }
    .stTextArea textarea:focus {border-color: #D4AF37;}
    
    .stButton button {
        background-color: #1f2329;
        color: #9da5b4;
        border: 1px solid #3e4451;
        font-weight: 600;
        text-transform: uppercase;
    }
    .stButton button:hover {
        border-color: #D4AF37;
        color: #D4AF37;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #16191f !important;
        border-top: 2px solid #D4AF37 !important;
        color: #D4AF37 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGIN ---
def login():
    if 'logado' not in st.session_state:
        st.session_state.update({'logado': False, 'user': ''})
    
    # Senhas
    usuarios = {"admin": "1234", "pastor": "pregar"}

    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'><span class='gold-text' style='font-size: 50px'>O PREGADOR</span></h1>", unsafe_allow_html=True)
            with st.form("frm_login"):
                u = st.text_input("USUÁRIO")
                s = st.text_input("SENHA", type="password")
                if st.form_submit_button("ACESSAR", type="primary"):
                    if u in usuarios and usuarios[u] == s:
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else: st.error("Erro.")
        return False
    return True

if not login(): st.stop()

# --- VARIÁVEIS DO USUÁRIO ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# --- FUNÇÕES INTELIGENTES (CORRIGIDAS) ---
def ai_gemini(prompt, key, role=""):
    if not key: return "⚠️ API Key necessária."
    try:
        genai.configure(api_key=key)
        # AQUI FOI A CORREÇÃO: Mudamos para gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{role}\n\nPERGUNTA DO PREGADOR: {prompt}"
        return model.generate_content(full_prompt).text
    except Exception as e: return f"Erro na IA: {e}"

def get_news(term):
    try: return DDGS().news(keywords=term, region="br-pt", max_results=3)
    except: return []

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i, p in enumerate(reader.pages):
            if i > 30: break
            text += p.extract_text()
        return text
    except: return "Erro PDF."

# --- 5. INTERFACE ---
with st.sidebar:
    st.markdown("<h2 class='gold-text' style='font-size: 24px'>✝ PREGADOR</h2>", unsafe_allow_html=True)
    st.caption(f"Usuário: {USER}")
    
    st.divider()
    
    # API Key Automática (Secrets)
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    if not api_key:
        api_key = st.text_input("CHAVE GOOGLE (API)", type="password")
    
    if api_key: st.success("Sistema Online")

    st.markdown("---")
    st.markdown("<p style='color:#D4AF37; font-weight:bold'>BIBLIOTECA</p>", unsafe_allow_html=True)
    try: docs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: docs = []
    
    selecao = st.radio("SELECIONAR:", ["+ NOVO PROJETO"] + docs)
    
    st.divider()
    if st.button("SAIR"):
        st.session_state['logado'] = False
        st.rerun()

c_edit, c_tools = st.columns([1.8, 1])

# EDITOR
with c_edit:
    content = ""
    title_val = ""
    
    if selecao != "+ NOVO PROJETO":
        title_val = selecao
        try:
            with open(os.path.join(PASTA, f"{selecao}.txt"), "r") as f: content = f.read()
        except: pass

    c_tit, c_btn = st.columns([3, 1])
    with c_tit:
        new_title = st.text_input("TÍTULO", value=title_val, label_visibility="collapsed", placeholder="Título do Sermão...")
    with c_btn:
        if st.button("💾 SALVAR", use_container_width=True, type="primary"):
            if new_title:
                with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(content) 
                st.toast("Salvo!", icon="☁️")

    text_area = st.text_area("Papel", value=content, height=720, label_visibility="collapsed")
    
    if new_title and text_area != content:
        with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(text_area)

# FERRAMENTAS
with c_tools:
    st.markdown("<p style='color:#D4AF37; font-weight:bold; margin-bottom: 10px'>FERRAMENTAS</p>", unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["IA", "BÍBLIA", "WEB", "PDF"])
    
    with t1:
        st.info("Assistente Conectado")
        acao = st.selectbox("Comando:", ["Analisar Esboço", "Sugerir Tópicos", "Criar Introdução"])
        if st.button("EXECUTAR"):
            if not new_title: st.warning("Crie um título.")
            else:
                role = "Você é um assistente teológico experiente."
                p = f"Ação: {acao}. Texto: {text_area[:2000]}"
                with st.spinner("Pensando..."):
                    st.write(ai_gemini(p, api_key, role))

    with t2:
        ref = st.text_input("Versículo (ex: Jo 3:16)")
        if st.button("EXEGESE"):
            prompt = f"Faça uma análise exegética profunda de {ref}."
            st.write(ai_gemini(prompt, api_key))

    with t3:
        busca = st.text_input("Tema Atual:")
        if st.button("BUSCAR"):
            news = get_news(busca)
            if news:
                for n in news: st.markdown(f"🔹 [{n['title']}]({n['url']})")
                st.write(ai_gemini(f"Ligue '{busca}' ao evangelho com essas notícias: {news}", api_key))

    with t4:
        pdf_file = st.file_uploader("Upload PDF", type="pdf")
        if pdf_file and st.button("LER"):
            with st.spinner("Lendo..."):
                raw = read_pdf(pdf_file)
                st.success("Lido!")
                st.markdown(ai_gemini(f"Resuma este conteúdo teológico: {raw[:3000]}", api_key))
                biblia = load_bible("acf")
texto = biblia["João"]["3"]["16"]
def load_crossrefs():
    try:
        with open("Banco_Biblia/crossrefs/referencias.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
xref = crossrefs.get("João 3:16",
def load_lexico():
    try:
        with open("Banco_Biblia/lexico/strongs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
lex = lexico.get("G25")  # exemplo: ágape
def load_kai():
    try:
        with open("Banco_Biblia/chave/kai.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
def load_kai():
    try:
        with open("Banco_Biblia/chave/kai.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

kai_refs = kai["fé"]
def ia_gratis(prompt):
    try:
        url = "https://api-free-llm.gptfree.cc/v1/chat/completions"
        payload = {
            "model": "llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post(url, json=payload)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Erro na IA gratuita"
texto = ia_gratis("Faça uma introdução sobre João 3:16")
with t2:
    ref = st.text_input("Versículo (ex: Jo 3:16)")
    ver = st.selectbox("Versão:", ["acf", "nvi"])

    if st.button("BUSCAR TEXTO"):
        biblia = load_bible(ver)
        try:
            livro, cap_vers = ref.split(" ")
            cap, vers = cap_vers.split(":")
            texto = biblia[livro][cap][vers]
            st.success(texto)
        except:
            st.error("Referência inválida")
    
    if st.button("REFERÊNCIAS CRUZADAS"):
        cross = load_crossrefs()
        refs = cross.get(ref, [])
        st.write(refs)

    if st.button("LÉXICO STRONGS"):
        lexico = load_lexico()
        termo = st.text_input("ID Strong (ex: G25)")
        if termo:
            st.write(lexico.get(termo, "Não encontrado"))

