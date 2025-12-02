import streamlit as st
import json
import os
import requests
import PyPDF2

# --- 1. CONFIGURAÇÃO DIVINA (Tela Cheia e Ícone) ---
st.set_page_config(page_title="O Pregador Supremo", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. PROTEÇÃO DE IMPORTAÇÃO ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False
    st.warning("⚠️ Instale: streamlit-lottie duckduckgo-search google-generativeai")

# --- 3. CSS "LOGOS GOLD" (Visual Definitivo) ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem; max-width: 98%;}
    .stApp {background-color: #0b0d10;}
    
    /* Efeito Dourado Logos */
    .gold {color: #C5A059; font-weight: bold;}
    
    [data-testid="stSidebar"] {background-color: #111318; border-right: 1px solid #333;}
    
    .stTextArea textarea {
        font-family: 'Merriweather', serif; font-size: 19px !important;
        background-color: #16191f; color: #d1d5db; border: 1px solid #2d313a; padding: 25px;
    }
    .stTextArea textarea:focus {border-color: #C5A059;}
    
    .stTabs [aria-selected="true"] {
        background-color: #16191f !important; border-top: 2px solid #C5A059 !important; color: #C5A059 !important;
    }
    
    /* Card de Notícia/Ref */
    .card {
        background-color: #1c2027; border-left: 3px solid #C5A059; padding: 10px; margin-bottom: 8px; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. BACKEND: BANCO DE BÍBLIA HÍBRIDO ---
# O sistema tenta ler seu JSON local. Se não achar, usa API pública para não travar.

def carregar_biblia(livro, cap, vers, versao="almeida"):
    # 1. Tenta Modo Local (Seus Arquivos)
    try:
        path = f"Banco_Biblia/bibles/{versao}.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data[livro][str(cap)][str(vers)]
    except: pass
    
    # 2. Tenta Modo API Online (Salva vidas se não tiver arquivo)
    try:
        # Normaliza nomes (ex: João -> john) - Simplificado para demo
        url = f"https://bible-api.com/{livro}+{cap}:{vers}?translation={versao}"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            return r.json()['text']
    except: pass
    
    return "Texto não encontrado ou offline."

def consultar_lexico_strong(termo):
    try:
        with open("Banco_Biblia/lexico/strongs.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(termo, "Termo não encontrado no banco local.")
    except:
        return "⚠️ Arquivo 'Banco_Biblia/lexico/strongs.json' não encontrado. Suba o arquivo para usar."

def referencias_cruzadas(ref):
    # Simula inteligência se não tiver arquivo
    try:
        with open("Banco_Biblia/crossrefs/referencias.json", "r") as f:
            data = json.load(f)
            return data.get(ref, [])
    except:
        return ["Isaias 53:4", "Romanos 5:8", "1 Pedro 2:24"] # Fallback genérico para demo

# --- 5. IAs (O DUETO) ---
def ia_google(prompt, key):
    if not key: return "Configure a chave do Google."
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
    except Exception as e: return str(e)

def ia_gratis(prompt):
    try:
        url = "https://api-free-llm.gptfree.cc/v1/chat/completions"
        payload = {
            "model": "llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post(url, json=payload, timeout=10)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Erro na IA Gratuita (Servidor Ocupado). Tente Google."

# --- 6. SISTEMA DE LOGIN ---
USUARIOS = {"admin": "1234", "pastor": "pregar"}

if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})

if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><h1 style='text-align:center; color:#C5A059'>O PREGADOR</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("ID")
            p = st.text_input("SENHA", type="password")
            if st.form_submit_button("ACESSAR BIBLIOTECA", type="primary"):
                if u in USUARIOS and USUARIOS[u] == p:
                    st.session_state.update({'logado': True, 'user': u})
                    st.rerun()
                else: st.error("Negado.")
    st.stop()

# --- 7. APP PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

with st.sidebar:
    st.markdown("### ✝️ BIBLIOTECA")
    st.caption(f"Usuário: {USER}")
    
    # Menu Principal
    api_key = st.secrets.get("GOOGLE_API_KEY", st.text_input("🔑 Chave Google", type="password"))
    ia_escolhida = st.selectbox("MOTOR IA:", ["Google Gemini (Rápido)", "Llama 3.1 (Grátis)"])
    
    st.markdown("---")
    
    # Seletor de Sermão
    try: docs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: docs = []
    sel = st.radio("PROJETOS:", ["+ NOVO"] + docs)
    
    st.divider()
    if st.button("SAIR"): st.session_state['logado']=False; st.rerun()

# Layout Logos
c_edit, c_tools = st.columns([1.8, 1])

with c_edit:
    # EDITOR CENTRAL
    txt_val, tit_val = "", ""
    if sel != "+ NOVO":
        tit_val = sel
        try:
            with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: txt_val = f.read()
        except: pass
        
    c1, c2 = st.columns([3,1])
    with c1: novo_titulo = st.text_input("TEMA", value=tit_val, label_visibility="collapsed", placeholder="Título do Sermão...")
    with c2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if novo_titulo:
                with open(os.path.join(PASTA, f"{novo_titulo}.txt"), "w") as f: f.write(txt_val) 
                st.toast("Salvo na Nuvem!")
    
    texto = st.text_area("Papel", value=txt_val, height=720, label_visibility="collapsed")
    if novo_titulo and texto != txt_val: # Auto-save state
         with open(os.path.join(PASTA, f"{novo_titulo}.txt"), "w") as f: f.write(texto)

with c_tools:
    # FERRAMENTAS AVANÇADAS
    t1, t2, t3, t4 = st.tabs(["BÍBLIA", "LÉXICO", "NOTÍCIAS", "LIVROS"])
    
    with t1: # Aba Bíblia Híbrida
        st.markdown("<span class='gold'>CONSULTA RÁPIDA</span>", unsafe_allow_html=True)
        ref_b = st.text_input("Referência:", placeholder="Joao 3 16") # Espaço ao invés de :
        versao_b = st.selectbox("Versão:", ["almeida", "bbe"])
        
        if st.button("📖 LER TEXTO"):
            if ref_b:
                try:
                    livro, rest = ref_b.split(" ", 1)
                    cap, vers = rest.split(" ")
                    res_txt = carregar_biblia(livro, cap, vers, versao_b)
                    st.success(f"Running text: {res_txt}")
                    st.info("💡 Dica: Para textos completos, configure os arquivos JSON.")
                except: st.error("Formato: 'Joao 3 16'")
    
    with t2: # Léxico e Chave
        st.markdown("<span class='gold'>FERRAMENTAS ORIGINAIS</span>", unsafe_allow_html=True)
        cod_strong = st.text_input("Código Strong (ex: G25):")
        if st.button("PESQUISAR NO GREGO/HEBRAICO"):
            definicao = consultar_lexico_strong(cod_strong)
            st.markdown(f"<div class='card'>{definicao}</div>", unsafe_allow_html=True)
            
        st.divider()
        st.caption("Inteligência Artificial Exegética")
        ref_analise = st.text_input("Versículo para Exegese:")
        if st.button("ANALISAR PROFUNDAMENTE"):
            p = f"Faça uma análise exegética profunda de {ref_analise}. Inclua Strongs, morfologia e contexto histórico."
            
            with st.status("Consultando Teólogos Digitais...", expanded=True):
                if ia_escolhida == "Google Gemini (Rápido)":
                    resp = ia_google(p, api_key)
                else:
                    resp = ia_gratis(p)
                st.markdown(resp)

    with t3: # Notícias & Web
        termo_n = st.text_input("Tema Atual:")
        if st.button("BUSCAR ILUSTRAÇÃO"):
            try:
                res = DDGS().news(keywords=termo_n, region="br-pt", max_results=3)
                if res:
                    links = ""
                    for n in res:
                        st.markdown(f"<div class='card'><a href='{n['url']}'>{n['title']}</a></div>", unsafe_allow_html=True)
                        links += f"{n['title']} "
                    
                    st.write("---")
                    st.caption("Sugestão de Ponte Homilética:")
                    prompt_il = f"Crie uma introdução de sermão ligando o tema {termo_n} e essas notícias: {links} à Bíblia."
                    st.write(ia_google(prompt_il, api_key))
            except: st.warning("Nada encontrado.")
            
    with t4: # PDF
        pdf_f = st.file_uploader("Subir Livro (PDF)", type="pdf")
        if pdf_f and st.button("ESTUDAR LIVRO"):
            try:
                leitor = PyPDF2.PdfReader(pdf_f)
                txt_livro = ""
                for p in leitor.pages[:20]: txt_livro += p.extract_text()
                st.success("Livro Indexado!")
                st.markdown(ia_google(f"Resuma este conteúdo teológico para sermão: {txt_livro[:3000]}", api_key))
            except: st.error("Erro na leitura.")
