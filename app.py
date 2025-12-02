import streamlit as st
import os
import requests
import json
import PyPDF2
from gtts import gTTS
import tempfile

# --- 1. CONFIGURAÇÃO ESTÁVEL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# --- 2. VARIAVEIS DE ESTADO ---
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60

# --- 3. CSS SEPARADO (PARA NÃO DAR ERRO DE RENDERIZAÇÃO) ---
def apply_style():
    st.markdown(f"""
    <style>
        /* Import Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        /* Wallpaper Fixo (Não pisca na atualização) */
        [data-testid="stAppViewContainer"] {{
            background-image: url("{st.session_state['bg_url']}");
            background-size: cover;
            background-position: center; 
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Vidro (Glassmorphism) */
        [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"] {{
            background-color: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 12px !important;
            color: #e2e8f0 !important;
        }}
        
        /* Ajuste Editor */
        .stTextArea textarea {{
            font-family: 'Inter', sans-serif;
            font-size: 16px !important;
            line-height: 1.6 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .stTextArea textarea:focus {{ border-color: #3b82f6 !important; }}
        
        /* Botões Apple Style */
        .stButton button {{
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            color: white;
            border-radius: 8px;
            font-weight: 500;
        }}
        .stButton button:hover {{
            border-color: #3b82f6;
            color: #3b82f6;
        }}
        
        /* Limpeza Geral */
        header, footer {{visibility: hidden;}}
        .block-container {{padding-top: 1rem;}}
        
        /* Logo Titulo */
        .big-font {{ font-size:40px !important; font-weight: 800; color: white; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

apply_style()

# --- 4. FUNÇÕES DE SUPORTE ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    LIBS_OK = True
except: LIBS_OK = False

def gemini(prompt, key):
    if not key or not LIBS_OK: return "⚠️ API Key ou Libs faltando."
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
    except Exception as e: return str(e)

def bible_api(ref):
    try:
        # Ex: Joao+3:16
        r = requests.get(f"https://bible-api.com/{ref.replace(' ', '+')}?translation=almeida", timeout=3)
        if r.status_code == 200: return r.json()
    except: return None

# --- 5. TELA DE LOGIN ---
def login_screen():
    if not st.session_state['logado']:
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<p class='big-font'>🧷 O PREGADOR</p>", unsafe_allow_html=True)
            with st.form("login_safe"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Acessar Área de Trabalho", type="primary"):
                    if (u=="admin" and p=="1234") or (u=="pastor" and p=="pregar"):
                        st.session_state['logado'] = True
                        st.session_state['user'] = u
                        st.rerun()
                    else: st.error("Erro no login")
        return False
    return True

if not login_screen(): st.stop()

# --- 6. APP PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# > SIDEBAR
with st.sidebar:
    st.markdown("## 🧷 PREGADOR OS")
    st.caption(f"Usuário: {USER}")
    
    tab_arq, tab_conf = st.tabs(["📂 Projetos", "⚙️ Ajustes"])
    
    with tab_arq:
        try: files = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: files = []
        project = st.radio("Selecione:", ["+ Novo"] + files, label_visibility="collapsed")
        
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    with tab_conf:
        # Ajuste Fundo
        bg = st.text_input("Wallpaper URL:", value=st.session_state['bg_url'])
        if st.button("Trocar Fundo"):
            st.session_state['bg_url'] = bg
            st.rerun()
            
        # API Key
        key = st.text_input("Google Key:", type="password")
        if not key: key = st.secrets.get("GOOGLE_API_KEY", "")

# > LOGICA ARQUIVO
current_text = ""
current_title = ""

if project != "+ Novo":
    current_title = project
    try:
        with open(os.path.join(PASTA, f"{project}.txt"), "r") as f:
            current_text = f.read()
    except: pass

# > ÁREA DE TRABALHO (SLIDER)
c_editor, c_tools = st.columns([2, 1]) # Fixo para evitar erro de calculo

with c_editor:
    # Header do Editor
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        new_title = st.text_input("Título", value=current_title, placeholder="Nome do Sermão...", label_visibility="collapsed")
    with c_head2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if new_title:
                with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f:
                    f.write(current_text) # Salva o que estava na memoria
                st.toast("Salvo!", icon="☁️")
    
    # O PAPEL (TEXTO)
    text_body = st.text_area("Papel", value=current_text, height=700, label_visibility="collapsed")
    
    # Auto-Sync (Gambiarrinha segura)
    if new_title and text_body != current_text:
        with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f:
            f.write(text_body)

with c_tools:
    # FERRAMENTAS ESTILO IOS
    st.markdown("#### 📱 Apps")
    
    with st.expander("📖 Bíblia + Áudio", expanded=True):
        ref_b = st.text_input("Verso (ex: Salmos 23)")
        if ref_b:
            res = bible_api(ref_b)
            if res:
                t_bib = res['text']
                st.info(f"{t_bib}")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("⬇ Inserir"):
                        with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f:
                            f.write(text_body + f"\n\n**{res['reference']}**\n{t_bib}")
                        st.rerun()
                with c_btn2:
                    if st.button("🔊 Tocar"):
                        try:
                            mp3 = gTTS(text=t_bib, lang='pt')
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                                mp3.save(fp.name)
                                st.audio(fp.name, format="audio/mp3")
                        except: st.warning("Erro Áudio")

    with st.expander("🗣 Tradutor IA"):
        tr_text = st.text_area("Texto Original:")
        if st.button("Traduzir PT-BR"):
            st.write(gemini(f"Traduza para português culto e pastoral: {tr_text}", key))

    with st.expander("⚡ Assistente & Corretor"):
        opt = st.selectbox("Ação:", ["Corrigir Texto", "Sugerir Introdução", "Analisar Teologia"])
        if st.button("Executar IA"):
            prompt_final = ""
            if opt == "Corrigir Texto":
                prompt_final = f"Corrija este texto gramaticalmente e melhore o estilo: {text_body}"
            elif opt == "Analisar Teologia":
                prompt_final = f"Analise teologicamente: {text_body}"
            else:
                prompt_final = f"Crie uma introdução para o sermão '{new_title}'"
            
            with st.spinner("Processando..."):
                st.success(gemini(prompt_final, key))
