import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
import PyPDF2
from gtts import gTTS

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# --- 2. SISTEMA DE LOGIN E GAMIFICAÇÃO (STREAK) ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())

# Função para atualizar contador de dias seguidos
def update_streak():
    hoje = str(datetime.now().date())
    ontem = str((datetime.now() - timedelta(days=1)).date())
    if st.session_state['last_login'] == ontem:
        st.session_state['login_streak'] += 1
    elif st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] = 1 # Reset se perdeu um dia
    st.session_state['last_login'] = hoje

# --- 3. INTEGRAÇÃO E SEGURANÇA IA ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    HAS_LIB = True
except: HAS_LIB = False

def safety_filter(prompt):
    """Filtro contra fraudes e conteúdo impróprio"""
    blacklist = ["porn", "sex", "fraude", "hack", "cartão", "roubo", "xxx", "cassino"]
    if any(word in prompt.lower() for word in blacklist):
        return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    """Cérebro Central da IA (Razão, Emoção, Código, Professor)"""
    if not key: return "⚠️ IA Offline. Configure a Chave Google no menu."
    if not safety_filter(prompt): return "🚫 Conteúdo bloqueado pelo filtro de segurança e ética cristã."
    
    try:
        genai.configure(api_key=key)
        
        # Definição de Personalidades
        system_role = ""
        if mode == "Razão":
            system_role = "Você é um teólogo escolástico, lógico e profundo. Foque na exegese, história e doutrina. Use argumentos racionais."
        elif mode == "Sentimento":
            system_role = "Você é um pastor pentecostal com coração de ovelha. Foque na emoção, consolo, esperança e fervor espiritual."
        elif mode == "Professor":
            system_role = "Você é um professor de homilética. Analise o texto do aluno, aponte erros e dê uma nota de 0 a 10 com dicas construtivas."
        elif mode == "Coder":
            system_role = "Você é um especialista em Python e Streamlit. Gere apenas códigos funcionais e seguros. Não explique, mostre o código."
        else:
            system_role = "Você é um assistente cristão sábio."

        full_prompt = f"PAINEL DE CONTROLE: {system_role}\n\nPEDIDO DO USUÁRIO: {prompt}"
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(full_prompt).text
    except Exception as e: return f"Erro na conexão com IA Studio: {e}"

# --- 4. FUNÇÕES ÚTEIS (Audio, QR, Bible) ---
def get_bible(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida", timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

def gerar_qr_code(link):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# --- 5. CSS (VISUAL EMPRESARIAL / LAN HOUSE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;600&family=Lato:wght@400;700&display=swap');

    /* Geral */
    .stApp {background-color: #050505; color: #fff;}
    .block-container {padding-top: 1rem;}
    header, footer {visibility: hidden;}

    /* Sidebar - Estilo Painel de Controle */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f;
        border-right: 1px solid #333;
    }

    /* Logo Personalizada */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 20px 0;
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
    }
    .app-title {
        font-family: 'Lato', sans-serif;
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(90deg, #d4a373, #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Text Area - O Centro de Comando */
    .stTextArea textarea {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #333;
        border-radius: 8px;
        font-family: 'Roboto Mono', monospace; /* Fonte estilo Código/Lan House */
        font-size: 16px;
    }
    .stTextArea textarea:focus { border-color: #d4a373; box-shadow: 0 0 10px rgba(212, 163, 115, 0.2); }

    /* Botões de Ação */
    .stButton button {
        width: 100%;
        background-color: #262626;
        color: white;
        border: 1px solid #444;
        border-radius: 6px;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #d4a373;
        color: black;
    }

    /* Footer Social */
    .footer-insta {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111;
        padding: 10px;
        text-align: center;
        border-top: 1px solid #333;
        font-size: 14px;
        z-index: 999;
    }
    .footer-insta a { text-decoration: none; color: #E1306C; font-weight: bold;}
    
    /* Contador de Streak */
    .streak-badge {
        background: #2e7d32;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 6. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Ícone do Pregador de Madeira (Link público)
        st.markdown("""
        <div style='text-align: center'>
            <img src='https://cdn-icons-png.flaticon.com/512/9430/9430594.png' width='80'>
            <h1 style='color: white;'>O PREGADOR</h1>
            <p style='color: #888;'>Sistema Pastoral Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            u = st.text_input("ID")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", type="primary"):
                if (u=="admin" and p=="1234") or (u=="pastor" and p=="pregar") or (u=="felipe" and p=="hope"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    update_streak()
                    st.rerun()
                else: st.error("Incorreto.")
    st.stop()

# --- 7. SISTEMA PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# ==================== BARRA LATERAL ====================
with st.sidebar:
    # Logo e Marca
    st.markdown(f"""
    <div class="logo-container">
        <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="40">
        <span class="app-title">O PREGADOR</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Streak / Login
    st.markdown(f"<span class='streak-badge'>🔥 {st.session_state['login_streak']} Dias na Presença</span>", unsafe_allow_html=True)
    st.caption(f"Logado: {USER.upper()}")
    
    # Chave API
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key: api_key = st.text_input("Chave Google IA", type="password")
    if api_key: st.caption("Status IA: 🟢 Online")
    else: st.caption("Status IA: 🔴 Offline")

    st.markdown("---")
    
    # Gerenciamento de Arquivos
    try: arquivos = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: arquivos = []
    
    escolha = st.radio("SEUS PROJETOS", ["+ NOVO PROJETO"] + arquivos)
    
    # Monetização e Anúncios (Simulação Inteligente)
    st.markdown("---")
    st.info("🛒 **Loja do Reino**")
    if "Familia" in escolha or "Casamento" in escolha:
        st.markdown("[📘 Livro: O Casamento Blindado](https://amazon.com.br)")
    elif "Espirito" in escolha:
        st.markdown("[📕 Livro: Bom Dia Espírito Santo](https://amazon.com.br)")
    else:
        st.caption("Escreva um título para ver sugestões...")

    if st.button("Sair"): st.session_state['logado']=False; st.rerun()

# ==================== ÁREA DE TRABALHO ====================
c_editor, c_tools = st.columns([2, 1])

# LOGICA CARREGAMENTO
texto = ""
titulo_input = ""
if escolha != "+ NOVO PROJETO":
    titulo_input = escolha
    try:
        with open(os.path.join(PASTA, f"{escolha}.txt"), "r") as f: texto = f.read()
    except: pass

with c_editor:
    # HEADER DE AÇÃO
    col_tit, col_act = st.columns([3, 1])
    with col_tit:
        novo_titulo = st.text_input("TÍTULO", value=titulo_input, placeholder="Tema da Mensagem...", label_visibility="collapsed")
    with col_act:
        if st.button("💾 GRAVAR NA NUVEM", type="primary", use_container_width=True):
            if novo_titulo:
                with open(os.path.join(PASTA, f"{novo_titulo}.txt"), "w") as f: f.write(texto)
                st.toast("Salvo com sucesso!")
                
    # BARRA DE FERRAMENTAS DO EDITOR (EMBUTIDA)
    st.markdown("#### ⚡ Ações Rápidas n
