import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import PyPDF2
from gtts import gTTS

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# --- 2. GESTÃO DE ESTADO (Para Manter o Fundo e Login) ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1

# Importação Segura
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
except: pass

# --- 3. CSS APPLE / GLASSMORPHISM (O VISUAL QUE VOCÊ GOSTOU) ---
st.markdown(f"""
<style>
    /* Fonte Moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* WALLPAPER (FUNDO) */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* MODAL DE VIDRO (BLUR) */
    [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"], .glass-card {{
        background-color: rgba(20, 25, 40, 0.85) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }}

    /* Header e Footer invisíveis padrão */
    header, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1rem; max-width: 95%;}}

    /* TÍTULO DOURADO + IMAGEM MADEIRA */
    .brand-container {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }}
    .brand-text {{
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(to right, #cfc09f, #D4AF37, #cfc09f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* EDITOR DE TEXTO LIMPO */
    .stTextArea textarea {{
        font-size: 17px !important;
        line-height: 1.6 !important;
        padding: 20px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }}
    .stTextArea textarea:focus {{
        border-color: #D4AF37 !important; /* Borda Dourada ao focar */
    }}

    /* RODAPÉ DO INSTAGRAM FIXO */
    .footer-insta {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0,0,0,0.9);
        color: white;
        text-align: center;
        padding: 8px;
        font-size: 13px;
        z-index: 9999;
        border-top: 1px solid #333;
    }}
    .footer-insta a {{ color: #E1306C; font-weight: bold; text-decoration: none; }}

</style>
""", unsafe_allow_html=True)

# --- 4. CÉREBRO DA IA (MODOS: RAZÃO / SENTIMENTO / SEGURANÇA) ---
def safety_filter(prompt):
    blacklist = ["porn", "sex", "xxx", "fraude", "hacker", "crime"]
    if any(x in prompt.lower() for x in blacklist): return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    if not key: return "⚠️ IA Offline."
    if not safety_filter(prompt): return "🚫 Conteúdo Bloqueado por Segurança."
    
    try:
        genai.configure(api_key=key)
        
        # As Personalidades que você pediu
        roles = {
            "Razão": "Você é um teólogo lógico e racional. Use argumentos históricos, exegese bíblica e fatos.",
            "Sentimento": "Você é um pastor acolhedor. Use linguagem emocional, consoladora e poética.",
            "Professor": "Você é um professor de português e homilética. Corrija o texto e ensine como melhorar.",
            "Tradutor": "Traduza o texto para Português Culto Pastoral.",
            "Coder": "Gere código Python seguro."
        }
        
        full_prompt = f"MODO: {roles.get(mode, 'Assistente')}\n\nPEDIDO: {prompt}"
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(full_prompt).text
    except Exception as e: return f"Erro IA: {e}"

def gerar_qr(link):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

# --- 5. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # TÍTULO E ÍCONE MADEIRA NA TELA DE LOGIN
        st.markdown("""
        <div style="text-align:center; background: rgba(0,0,0,0.5); padding: 20px; border-radius: 20px; backdrop-filter: blur(10px);">
            <img src="https://img.icons8.com/color/96/clothes-peg.png" width="80">
            <h1 class="brand-text" style="font-size: 40px; -webkit-text-fill-color: #D4AF37;">O PREGADOR</h1>
            <p style="color:#ccc">Ambiente de Trabalho Pastoral</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR", type="primary"):
                if u in ["admin", "pastor", "felipe"] and p in ["1234", "pregar", "hope"]:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Negado")
    st.stop()

# --- 6. APP PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# >>>> BARRA LATERAL (MENU + MADEIRA + CONFIG) <<<<
with st.sidebar:
    # 1. IDENTIDADE VISUAL (PREGADOR MADEIRA)
    # Usando HTML para garantir o alinhamento perfeito Imagem + Texto Dourado
    st.markdown("""
    <div class="brand-container">
        <img src="https://img.icons8.com/color/96/clothes-peg.png" width="50">
        <span class="brand-text">O PREGADOR</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Usuário: {USER} | Login Streak: 🔥 {st.session_state['login_streak']} Dias")
    
    # 2. MENU ARQUIVOS & CONFIG
    tab_files, tab_conf, tab_social = st.tabs(["📂 ARQ", "⚙️ CONF", "📱 INSTA"])
    
    with tab_files:
        try: arqs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: arqs = []
        sel = st.radio("Sermões:", ["+ Novo"] + arqs, label_visibility="collapsed")
        
        if st.button("Sair"): 
            st.session_state['logado']=False
            st.rerun()

    with tab_conf:
        st.write("🎨 **Personalizar**")
        bg_user = st.text_input("Link Imagem Fundo:", v
