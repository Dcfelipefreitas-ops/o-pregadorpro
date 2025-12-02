import streamlit as st
import json
import os
import requests
import time
import PyPDF2
from pathlib import Path

# --- 1. CONFIGURAÇÃO GERAL (Nome Corrigido) ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# --- 2. PREVENÇÃO DE ERROS ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False

# --- 3. ESTILO "LOGOS GOLD" (Visual Premium) ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem; max-width: 98%;}
    .stApp {background-color: #0b0d10;}
    
    /* Efeito Dourado */
    .gold-text {
        background: linear-gradient(to bottom, #cfc09f, #D4AF37, #7a5c2f); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        color: #C5A059;
        font-family: 'Times New Roman', serif;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* Menu Lateral */
    [data-testid="stSidebar"] {background-color: #111318; border-right: 1px solid #333;}
    
    /* Editor */
    .stTextArea textarea {
        font-family: 'Merriweather', serif; font-size: 19px !important; line-height: 1.6;
        background-color: #16191f; color: #d1d5db; border: 1px solid #2d313a; padding: 25px;
    }
    .stTextArea textarea:focus {border-color: #C5A059;}
    
    /* Abas */
    .stTabs [aria-selected="true"] {
        background-color: #16191f !important; border-top: 2px solid #C5A059 !important; color: #C5A059 !important;
    }
    
    /* Cartões de Info */
    .card {
        background-color: #1c2027; border-left: 3px solid #C5A059; padding: 15px; margin-bottom: 10px; border-radius: 4px;
    }
    a {text-decoration: none; color: #D4AF37;}
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES HÍBRIDAS (Aqui resolvemos o problema de "não acessar nada") ---

def pegar_biblia_online(ref):
    """Se não tiver arquivo, busca na internet"""
    try:
        # Tenta formatar 'Joao 3 16' para 'john+3:16'
        partes = ref.split()
        if len(partes) >= 2:
            livro = partes[0]
            cap_ver = partes[1] if ":" in partes[1] else f"{partes[1]}:{partes[2] if len(partes)>2 else '1'}"
            
            # API Gratuita (Almeida/KJV)
            url = f"https://bible-api.com/{livro}+{cap_ver}?translation=almeida"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                return f"{data['reference']}\n\n{data['text']}"
    except:
        pass
    return "Não encontrado. Tente formato: 'Joao 3 16'"

def carregar_biblia(ref, versao="almeida"):
    # 1. Tenta Arquivo Local (Caso você tenha subido)
    try:
        parts = ref.split()
        livro, cap, ver = parts[0], parts[1], parts[2]
        path = f"Banco_Biblia/bibles/{versao}.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data[livro][str(cap)][str(ver)]
    except: 
        # 2. Se falhar, usa ONLINE (Para funcionar AGORA)
        return pegar_biblia_online(ref)

def lexico_strong_fallback(codigo):
    # Link direto para estudo já que o JSON é gigante para baixar agora
    base_url = "https://biblehub.com/greek" if "G" in codigo.upper() else "https://biblehub.com/hebrew"
    num = ''.join(filter(str.isdigit, codigo))
    return f"""
    Termo: {codigo}
    <br>Devido ao tamanho do léxico completo, <a href='{base_url}/{num}.htm' target='_blank'>Clique aqui para ver a definição completa no BibleHub</a>.
    """

def ia_gratis(prompt):
    """Llama 3 Grátis"""
    try:
        url = "https://api-free-llm.gptfree.cc/v1/chat/completions"
        payload = {
            "model": "llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post(url, json=payload, timeout=8)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ IA Grátis instável. Configure a chave do Google no menu lateral para estabilidade total."

def ler_pdf_texto(file_like):
    try:
        reader = PyPDF2.PdfReader(file_like)
        text = []
        for i, p in enumerate(reader.pages):
            if i > 40: break 
            text.append(p.extract_text() or "")
        return "\n".join(text)
    except: return "Erro ao ler PDF."

# --- 5. GOOGLE IA (GEMINI) ---
def ia_google(prompt, key):
    if not key: return None # Retorna vazio se nao tiver chave
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
    except: return "Erro na API Google."

# --- 6. TELA DE LOGIN ---
USUARIOS = {"admin": "1234", "pastor": "pregar"}

if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['user'] = ''

if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # NOME CORRIGIDO AQUI
        st.markdown("<h1 style='text-align: center;'><span class='gold-text' style='font-size: 50px'>O PREGADOR</span></h1>", unsafe_allow_html=True)
        with st.form("frm_login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR", type="primary"):
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# --- 7. INTERFACE PRINCIPAL ---
USER = st.session_state['user']
PASTA = Path("Banco_Sermoes") / USER
PASTA.mkdir(parents=True, exist_ok=True)

with st.sidebar:
    st.markdown("<h2 class='gold-text'>✝ O PREGADOR</h2>", unsafe_allow_html=True)
    st.caption(f"Bem-vindo, {USER}")
    
    # Seleção de IA
    motor_ia = st.selectbox("INTELIGÊNCIA:", ["Llama 3 (Grátis)", "Google Gemini (Chave)"])
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Chave Google API", type="password")
    
    st.divider()
    
    # Arquivos
    try: docs = [f.stem for f in PASTA.glob("*.txt")]
    except: docs = []
    sel = st.radio("BIBLIOTECA:", ["+ NOVO ESTUDO"] + docs)
    
    st.divider()
    if st.button("SAIR"):
        st.session_state['logado'] = False
        st.rerun()

# Layout Principal
c_left, c_right = st.columns([2, 1.2])

# EDITOR DE TEXTO (Esquerda)
with c_left:
    content = ""
    title_val = ""
    if sel != "+ NOVO ESTUDO":
        title_val = sel
        try: content = (PASTA / f"{sel}.txt").read_text(encoding="utf-8")
        except: pass
    
    col_t1, col_t2 = st.columns([3,1])
    with col_t1:
        new_title = st.text_input("TEMA", value=title_val, label_visibility="collapsed", placeholder="Título do Sermão...")
    with col_t2:
        if st.button("💾 GRAVAR", use_container_width=True, type="primary"):
            if new_title:
                (PASTA / f"{new_title}.txt").write_text(content, encoding="utf-8")
                st.toast("Salvo na Nuvem!")

    # Editor que atualiza variável
    text_area = st.text_area("Papel", value=content, height=720, label_visibility="collapsed")
    if new_title and text_area != content:
        (PASTA / f"{new_title}.txt").write_text(text_area, encoding="utf-8")

# FERRAMENTAS (Direita)
with c_right:
    st.markdown("<p style='color:#C5A059; font-weight:bold'>PAINEL DE ESTUDOS</p>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["BÍBLIA", "ORIGINAL", "IA/CHAT", "LIVROS"])
    
    # ABA 1: BÍBLIA
    with t1:
        st.info("Digite ref: Joao 3 16 (Sem dois pontos)")
        ref_in = st.text_input("Referência:")
        
        if st.button("📖 LER TEXTO"):
            if ref_in:
                # Aqui usa a função que busca ONLINE se não tiver arquivo
                res_txt = carregar_biblia(ref_in) 
                st.markdown(f"<div class='card'>{res_txt}</div>", unsafe_allow_html=True)
            else:
                st.warning("Digite algo (ex: Joao 3 16)")

    # ABA 2: ORIGINAIS (LEXICO/STRONG)
    with t2:
        st.caption("Strong & Referências")
        strong_id = st.text_input("Strong ID (ex: G25)")
        if st.button("BUSCAR SIGNIFICADO"):
            # Usa o fallback online
            res_strong = lexico_strong_fallback(strong_id)
            st.markdown(f"<div class='card'>{res_strong}</div>", unsafe_allow_html=True)
        
        st.divider()
        cross = st.text_input("Tema / Ref Cruzada (ex: Fé)")
        if st.button("VER REFERÊNCIAS"):
             prompt_ref = f"Dê 5 referências cruzadas bíblicas sobre: {cross}"
             if motor_ia == "Llama 3 (Grátis)":
                 st.write(ia_gratis(prompt_ref))
             else:
                 st.write(ia_google(prompt_ref, api_key))

    # ABA 3: INTELIGÊNCIA ARTIFICIAL
    with t3:
        st.caption(f"Motor: {motor_ia}")
        prompt_ia = st.text_area("Pergunta ao Assistente:")
        if st.button("ENVIAR"):
            if not prompt_ia: st.warning("Digite a pergunta.")
            else:
                with st.spinner("Pesquisando..."):
                    resposta = ""
                    if motor_ia == "Llama 3 (Grátis)":
                        resposta = ia_gratis(prompt_ia)
                    else:
                        resp_google = ia_google(prompt_ia, api_key)
                        if resp_google: resposta = resp_google
                        else: resposta = "Erro ou falta de Chave Google."
                    
                    st.markdown(resposta)

    # ABA 4: PDF
    with t4:
        st.caption("Leitor de Livros PDF")
        pdf_file = st.file_uploader("Arrastar PDF aqui", type="pdf")
        if pdf_file:
            if st.button("LER E RESUMIR"):
                with st.spinner("Lendo..."):
                    raw_txt = ler_pdf_texto(pdf_file)
                    st.success("Lido!")
                    p_sum = f"Resuma os pontos teológicos principais para pregador: {raw_txt[:3000]}"
                    
                    if motor_ia == "Llama 3 (Grátis)":
                        st.write(ia_gratis(p_sum))
                    else:
                        st.write(ia_google(p_sum, api_key))
