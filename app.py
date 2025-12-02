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

# --- 2. GESTÃO DE ESTADO ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())

# Função Gamificação
def update_streak():
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
except: pass

# --- 3. CSS ESTILO "GLASS APPLE" ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {{font-family: 'Inter', sans-serif;}}

    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"] {{
        background-color: rgba(15, 20, 30, 0.9) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }}

    header, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1rem; max-width: 96%;}}

    /* MARCA PREGADOR */
    .brand-container {{
        text-align: center; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;
    }}
    .brand-text {{
        font-size: 24px; font-weight: 800; color: #D4AF37; letter-spacing: 1px; margin-top: 5px;
    }}

    .stTextArea textarea:focus {{border-color: #D4AF37 !important;}}
    
    .footer-insta {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(0,0,0,0.95); color: #888; text-align: center;
        padding: 5px; font-size: 12px; z-index: 9999; border-top: 1px solid #333;
    }}
    .footer-insta a {{ color: #E1306C; font-weight: bold; text-decoration: none; }}
</style>
""", unsafe_allow_html=True)

# --- 4. CÉREBRO IA & SEGURANÇA ---
def safety_check(prompt):
    bad = ["porn", "xxx", "fraude", "hacker", "roubo", "sex"]
    return not any(x in prompt.lower() for x in bad)

def ai_brain(prompt, key, mode="Professor"):
    if not key: return "⚠️ IA Offline. Configure Chave no Menu."
    if not safety_check(prompt): return "🚫 Bloqueado por Segurança."
    
    try:
        genai.configure(api_key=key)
        roles = {
            "Razão": "Teólogo lógico e acadêmico. Use exegese e história.",
            "Sentimento": "Pastor acolhedor. Use linguagem emocional e poética.",
            "Professor": "Professor de português e homilética. Corrija o texto.",
            "Tradutor": "Traduza para Português Culto Cristão.",
            "Coder": "Gere código Python seguro."
        }
        sys = f"MODO: {roles.get(mode, 'Assistente')}\n\nCONTEXTO: {prompt}"
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(sys).text
    except Exception as e: return f"Erro IA: {e}"

def get_bible(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref.replace(' ', '+')}?translation=almeida", timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

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
        st.markdown("""
        <div style="text-align:center; background: rgba(0,0,0,0.6); padding: 30px; border-radius: 15px;">
            <h1 style="color:#D4AF37;">🧷 O PREGADOR</h1>
            <p style="color:#ddd">Sistema Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR", type="primary"):
                if u in ["admin", "pastor", "felipe"] and p in ["1234", "pregar", "hope"]:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    update_streak()
                    st.rerun()
                else: st.error("Negado")
    st.stop()

# --- 6. SISTEMA PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# SIDEBAR (MENU)
with st.sidebar:
    st.markdown(f"""
    <div class="brand-container">
        <span style="font-size:40px;">🧷</span><br>
        <span class="brand-text">O PREGADOR</span><br>
        <span style="font-size:12px; color:#4CAF50">🔥 {st.session_state['login_streak']} Dias Online</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Olá, {USER}")
    
    tab_files, tab_conf, tab_qr = st.tabs(["📂", "⚙️", "📱"])
    
    with tab_files:
        try: arqs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: arqs = []
        sel = st.radio("Seus Estudos:", ["+ Novo"] + arqs, label_visibility="collapsed")
        if st.button("Sair"): 
            st.session_state['logado']=False
            st.rerun()

    with tab_conf:
        val = st.slider("Tamanho Tela", 30, 80, st.session_state['layout_split'])
        st.session_state['layout_split'] = val
        bg = st.text_input("Fundo URL:", value=st.session_state['bg_url'])
        if st.button("Mudar"): st.session_state['bg_url'] = bg; st.rerun()
        
        st.divider()
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key: api_key = st.text_input("Chave IA:", type="password")

    with tab_qr:
        try:
            buf = BytesIO()
            img = gerar_qr("https://instagram.com/felipefreitashope")
            img.save(buf)
            st.image(buf, caption="@felipefreitashope")
        except: st.error("Erro QR")

# ÁREA DE TRABALHO
ratio = st.session_state['layout_split'] / 100
c_editor, c_tools = st.columns([ratio, 1-ratio])

# Lógica Texto
txt_load = ""
tit_load = ""
if sel != "+ Novo":
    tit_load = sel
    try: 
        with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: txt_load = f.read()
    except: pass

with c_editor:
    c1, c2 = st.columns([4, 1])
    with c1: new_title = st.text_input("PROJETO", value=tit_load, placeholder="Título...", label_visibility="collapsed")
    with c2:
        if st.button("💾", type="primary", help="Salvar"):
            if new_title:
                with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(st.session_state['texto_esboco'])
                st.toast("Salvo!")

    # Editor Inteligente
    if not st.session_state['texto_esboco'] and txt_load:
        st.session_state['texto_esboco'] = txt_load
        
    area_texto = st.text_area("Papel", value=st.session_state['texto_esboco'], height=720, label_visibility="collapsed")
    st.session_state['texto_esboco'] = area_texto

    # Barra Flutuante de Ação (Abaixo do texto)
    st.caption("✨ IA DO EDITOR")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🗣 TRADUZIR"):
            if api_key:
                res = ai_brain(area_texto, api_key, "Tradutor")
                st.session_state['texto_esboco'] = res
                st.rerun()
    with b2:
        if st.button("📝 CORRIGIR"):
            if api_key:
                res = ai_brain(f"Corrija ortografia: {area_texto}", api_key, "Professor")
                st.code(res, language="text")
    with b3:
        if st.button("🎓 AVALIAR"):
            if api_key:
                st.info(ai_brain(area_texto, api_key, "Professor"))

    # Autosave
    if new_title and area_texto != txt_load:
        with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(area_texto)

with c_tools:
    st.markdown("#### 🧠 CENTRAL")
    abas = st.tabs(["CHAT", "BÍBLIA", "DEV"])
    
    with abas[0]:
        pg = st.text_area("Pergunta:")
        col_raz, col_emo = st.columns(2)
