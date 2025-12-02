import streamlit as st
import json
import os
import requests
import time
import PyPDF2
from pathlib import Path

# --- 1. CONFIGURAÇÃO DIVINA ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. CLASSE DE UTILIDADES (Helpers Embutidos) ---
# Aqui está a mágica dos arquivos separados, unificada para facilitar sua vida.

def carregar_biblia(livro, cap, vers, versao="almeida"):
    # 1. Tenta Arquivo Local (Se você tiver subido)
    try:
        path = f"Banco_Biblia/bibles/{versao}.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data[livro][str(cap)][str(vers)]
    except: pass
    
    # 2. Fallback: API Online (Para não dar erro se não tiver arquivo)
    try:
        # Simplificação para demonstração (na prática precisaria tratar nomes de livros)
        url = f"https://bible-api.com/{livro}+{cap}:{vers}?translation={versao}"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            return r.json()['text']
    except: pass
    return "Texto indisponível. Verifique a referência ou suba os JSONs."

def ia_gratis(prompt):
    """Sua IA Gratuita Llama integrada"""
    try:
        url = "https://api-free-llm.gptfree.cc/v1/chat/completions"
        payload = {
            "model": "llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post(url, json=payload, timeout=10)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ IA Gratuita instável. Tente usar a do Google (Configurações)."

def ler_pdf_texto(file_like):
    """Lê PDFs arrastados para o app"""
    try:
        reader = PyPDF2.PdfReader(file_like)
        text = []
        for i, p in enumerate(reader.pages):
            if i > 40: break # Limite para não travar
            text.append(p.extract_text() or "")
        return "\n".join(text)
    except: return "Erro ao ler PDF."

# Simulando o carregamento de léxicos/crossrefs para não quebrar sem arquivos
def get_cross_refs(ref):
    # Aqui entraria a leitura do seu arquivo kai.json
    # Como fallback, usamos IA se não tiver arquivo
    return ["Jo 3:16", "Rm 5:8"] 

# --- 3. ESTILO VISUAL "LOGOS GOLD" ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem; max-width: 98%;}
    .stApp {background-color: #0b0d10;}
    
    /* Efeito Dourado Logos */
    .gold-text {
        background: linear-gradient(to bottom, #cfc09f, #D4AF37, #3a2c0f); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        color: #C5A059;
        font-family: 'Times New Roman', serif;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {background-color: #111318; border-right: 1px solid #333;}
    
    /* Editor de Texto Premium */
    .stTextArea textarea {
        font-family: 'Merriweather', serif; font-size: 19px !important; line-height: 1.6;
        background-color: #16191f; color: #d1d5db; border: 1px solid #2d313a; padding: 25px;
    }
    .stTextArea textarea:focus {border-color: #C5A059;}
    
    /* Tabs e Botões */
    .stTabs [aria-selected="true"] {
        background-color: #16191f !important; border-top: 2px solid #C5A059 !important; color: #C5A059 !important;
    }
    .stButton button {
        background-color: #1f2329; color: #9da5b4; border: 1px solid #3e4451; font-weight: bold;
    }
    .stButton button:hover {
        border-color: #D4AF37; color: #D4AF37;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. GOOGLE AI CONFIG ---
try:
    import google.generativeai as genai
    HAS_GOOGLE = True
except: HAS_GOOGLE = False

def ia_google(prompt, key):
    if not key or not HAS_GOOGLE: return "⚠️ Configure Chave Google."
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except Exception as e: return f"Erro Google: {e}"

# --- 5. LOGIN DO SISTEMA ---
USUARIOS = {"admin": "1234", "pastor": "pregar"}

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['user'] = ''

if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'><span class='gold-text' style='font-size: 40px'>O PREGADOR SUPREMO</span></h1>", unsafe_allow_html=True)
        with st.form("frm_login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", type="primary"):
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# --- 6. INTERFACE PRINCIPAL ---
USER = st.session_state['user']
PASTA = Path("Banco_Sermoes") / USER
PASTA.mkdir(parents=True, exist_ok=True)

with st.sidebar:
    st.markdown("<h2 class='gold-text'>✝ PREGADOR</h2>", unsafe_allow_html=True)
    st.caption(f"Logado: {USER}")
    
    # Seleção de IA
    motor_ia = st.selectbox("MOTOR IA:", ["Google Gemini (Estável)", "Llama Grátis (Experimental)"])
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Chave Google API", type="password")
    
    st.divider()
    
    # Arquivos
    try: docs = [f.stem for f in PASTA.glob("*.txt")]
    except: docs = []
    sel = st.radio("BIBLIOTECA:", ["+ NOVO PROJETO"] + docs)
    
    st.markdown("---")
    if st.button("SAIR"):
        st.session_state['logado'] = False
        st.rerun()

# Layout
c_left, c_right = st.columns([2, 1.2])

with c_left:
    # EDITOR
    content = ""
    title_val = ""
    if sel != "+ NOVO PROJETO":
        title_val = sel
        try: content = (PASTA / f"{sel}.txt").read_text(encoding="utf-8")
        except: pass
    
    col_t1, col_t2 = st.columns([3,1])
    with col_t1:
        new_title = st.text_input("TEMA", value=title_val, label_visibility="collapsed", placeholder="Título...")
    with col_t2:
        if st.button("💾 GRAVAR", use_container_width=True, type="primary"):
            if new_title:
                (PASTA / f"{new_title}.txt").write_text(content, encoding="utf-8")
                st.toast("Salvo na Nuvem!")

    # Editor que atualiza variável
    text_area = st.text_area("Papel", value=content, height=720, label_visibility="collapsed")
    if new_title and text_area != content:
        # Autosave simples no próximo clique
        (PASTA / f"{new_title}.txt").write_text(text_area, encoding="utf-8")

with c_right:
    # FERRAMENTAS COM ABAS
    st.markdown("<p style='color:#C5A059; font-weight:bold'>PAINEL TEOLÓGICO</p>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["BÍBLIA", "ESTUDO", "IA CHAT", "LIVROS"])
    
    # ABA 1: BÍBLIA HÍBRIDA
    with t1:
        ref_in = st.text_input("Ref (ex: Joao 3 16)")
        vers_in = st.selectbox("Versão", ["almeida", "kjv"])
        if st.button("📖 LER TEXTO"):
            if ref_in:
                try:
                    livro, resto = ref_in.split(" ", 1)
                    cap, vers = resto.split(" ")
                    txt = carregar_biblia(livro, cap, vers, versao=vers_in)
                    st.success(f"TEXTO ({vers_in}):\n{txt}")
                except: st.error("Use formato: Livro Cap Verso (Joao 3 16)")

    # ABA 2: FERRAMENTAS ORIGINAIS (Strong/Cross)
    with t2:
        st.caption("Cross Reference & Léxico")
        strong_id = st.text_input("Strong ID (ex: G25)")
        if st.button("Pesquisar Strong"):
            # Aqui simulamos a busca local se não tiver arquivo
            st.info("Função requer arquivo 'Banco_Biblia/lexico/strongs.json'. (Modo Demonstração)")
        
        cross_ref = st.text_input("Ref Cruzada (ex: Jo 3:16)")
        if st.button("Ver Referências"):
             st.write(["Is 53:1", "Rm 5:8"]) # Exemplo

    # ABA 3: INTELIGÊNCIA ARTIFICIAL (SELETORA)
    with t3:
        st.caption(f"Usando: {motor_ia}")
        prompt_ia = st.text_area("Pergunta Teológica:")
        if st.button("ENVIAR PERGUNTA"):
            if not prompt_ia: st.warning("Digite algo.")
            else:
                with st.spinner("Processando..."):
                    resposta = ""
                    if motor_ia == "Llama 3.1 (Grátis)":
                        resposta = ia_gratis(prompt_ia)
                    else:
                        resposta = ia_google(prompt_ia, api_key)
                    st.markdown(resposta)

    # ABA 4: LEITOR PDF
    with t4:
        st.caption("Biblioteca Digital")
        pdf_file = st.file_uploader("Upload PDF", type="pdf")
        if pdf_file:
            if st.button("LER E RESUMIR"):
                raw_txt = ler_pdf_texto(pdf_file)
                st.success("PDF Lido.")
                # Usa a IA selecionada para resumir
                p_sum = f"Resuma este conteúdo teológico para sermão: {raw_txt[:3000]}"
                if motor_ia == "Llama Grátis":
                    st.write(ia_gratis(p_sum))
                else:
                    st.write(ia_google(p_sum, api_key))
