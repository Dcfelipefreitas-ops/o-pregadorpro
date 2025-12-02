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

# --- 2. GESTÃO DE ESTADO (MEMÓRIA) ---
# Aqui juntamos o visual (fundo/layout) com a gamificação (streak)
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60 # Slider do Editor
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())

# Função Gamificação (Streak)
def update_streak():
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

# Importação Segura
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
except: pass

# --- 3. CSS "APPLE GLASS" + ELEMENTOS PREMIUM ---
st.markdown(f"""
<style>
    /* Fonte Apple/Moderna */
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
    
    /* VIDRO (BLUR) NAS CAIXAS */
    [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"] {{
        background-color: rgba(20, 25, 40, 0.85) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }}

    /* HEADER & FOOTER */
    header, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1rem; max-width: 96%;}}

    /* TÍTULO E ÍCONE */
    .brand-container {{
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }}
    .brand-text {{
        font-size: 24px;
        font-weight: 800;
        color: #e0e0e0;
        letter-spacing: 1px;
        margin-top: 10px;
    }}

    /* EDITOR DE TEXTO */
    .stTextArea textarea {{
        font-size: 17px !important;
        line-height: 1.6 !important;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .stTextArea textarea:focus {{
        border-color: #3b82f6 !important; /* Azul Apple */
    }}

    /* BADGE GAMIFICAÇÃO */
    .streak-badge {{
        background: linear-gradient(90deg, #d4a373, #8b5e3c);
        color: black;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }}

    /* RODAPÉ INSTAGRAM */
    .footer-insta {{
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background: rgba(0,0,0,0.9);
        color: white; text-align: center;
        padding: 8px; font-size: 13px; z-index: 9999;
        border-top: 1px solid #333;
    }}
    .footer-insta a {{ color: #E1306C; font-weight: bold; text-decoration: none; }}
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE IA & SEGURANÇA ---
def safety_filter(prompt):
    blacklist = ["porn", "sex", "xxx", "fraude", "hacker", "crime"]
    if any(x in prompt.lower() for x in blacklist): return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    if not key: return "⚠️ IA Offline."
    if not safety_filter(prompt): return "🚫 Bloqueado por Segurança."
    try:
        genai.configure(api_key=key)
        # Personalidades
        roles = {
            "Razão": "Teólogo lógico, use argumentos históricos e exegese profunda.",
            "Sentimento": "Pastor acolhedor, use linguagem emocional e consoladora.",
            "Professor": "Professor de homilética. Corrija o texto e dê nota.",
            "Tradutor": "Traduza para Português Culto Pastoral.",
            "Coder": "Gere código Python."
        }
        full_prompt = f"MODO: {roles.get(mode, 'Assistente')}\n\nPEDIDO: {prompt}"
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(full_prompt).text
    except Exception as e: return f"Erro IA: {e}"

def gerar_qr(link):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def get_bible(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref.replace(' ', '+')}?translation=almeida", timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- 5. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Login Visual Apple + Madeira
        st.markdown("""
        <div style="text-align:center; background: rgba(0,0,0,0.5); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px);">
            <img src="https://cdn-icons-png.flaticon.com/512/9384/9384192.png" width="80">
            <h1 style="color: white; margin: 10px 0;">O PREGADOR</h1>
            <p style="color:#aaa; font-size: 14px">Ambiente Profissional</p>
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
                else: st.error("Acesso Negado")
    st.stop()

# --- 6. APP PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# >>>> BARRA LATERAL (MENU + MADEIRA + CONFIG) <<<<
with st.sidebar:
    # 1. IDENTIDADE (Madeira + Gamificação)
    st.markdown(f"""
    <div class="brand-container">
        <img src="https://cdn-icons-png.flaticon.com/512/9384/9384192.png" width="50">
        <div class="brand-text">O PREGADOR</div>
        <span class='streak-badge'>🔥 {st.session_state['login_streak']} Dias Online</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Bem-vindo, {USER.capitalize()}")
    
    # 2. ABAS DE CONFIGURAÇÃO
    tab_files, tab_conf, tab_social = st.tabs(["📂 PROJ", "⚙️ CONF", "📱 QR"])
    
    with tab_files:
        try: arqs = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: arqs = []
        sel = st.radio("Biblioteca:", ["+ Novo"] + arqs, label_visibility="collapsed")
        
        if st.button("Deslogar"): 
            st.session_state['logado']=False
            st.rerun()

    with tab_conf:
        # SLIDER DE LAYOUT (Recurso Apple)
        tamanho_tela = st.slider("Tamanho Editor", 30, 80, st.session_state['layout_split'])
        st.session_state['layout_split'] = tamanho_tela
        
        # MUDANÇA DE FUNDO
        bg_user = st.text_input("Fundo (URL):", value=st.session_state['bg_url'])
        if st.button("Aplicar Fundo"):
            st.session_state['bg_url'] = bg_user
            st.rerun()
            
        st.divider()
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key: api_key = st.text_input("Chave Google IA:", type="password")

    with tab_social:
        st.caption("Siga no Instagram")
        try:
            buf = BytesIO()
            img = gerar_qr("https://instagram.com/felipefreitashope")
            img.save(buf)
            st.image(buf, width=130)
            st.markdown("[@felipefreitashope](https://instagram.com/felipefreitashope)")
        except: st.error("Instale 'qrcode'")

# >>>> ÁREA DE TRABALHO FLUIDA (LAYOUT DINÂMICO) <<<<
ratio = st.session_state['layout_split'] / 100
c_editor, c_tools = st.columns([ratio, 1 - ratio])

# Carregar Arquivo
txt_display = ""
tit_display = ""
if sel != "+ Novo":
    tit_display = sel
    try: 
        with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: txt_display = f.read()
    except: pass

# --- COLUNA ESQUERDA: EDITOR DE TEXTO ---
with c_editor:
    # 1. Cabeçalho Clean
    c1, c2 = st.columns([4, 1])
    with c1:
        new_title = st.text_input("PROJETO", value=tit_display, placeholder="Título do Estudo...", label_visibility="collapsed")
    with c2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if new_title:
                with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(st.session_state['texto_esboco'])
                st.toast("Salvo na Nuvem!")

    # 2. Editor Principal (Estado Preservado)
    if not st.session_state['texto_esboco'] and txt_display:
        st.session_state['texto_esboco'] = txt_display
        
    text_area = st.text_area("Papel", value=st.session_state['texto_esboco'], height=720, label_visibility="collapsed")
    st.session_state['texto_esboco'] = text_area

    # 3. Barra de IA Embutida (Função Traduzir no Texto)
    st.markdown("##### ✨ Assistente Inteligente")
    b1, b2, b3 = st.columns(3)
    
    with b1:
        if st.button("🗣 TRADUZIR EDITOR"):
            if api_key:
                with st.spinner("Traduzindo..."):
                    res = ai_brain(st.session_state['texto_esboco'], api_key, "Tradutor")
                    st.session_state['texto_esboco'] = res
                    st.rerun()
    with b2:
        if st.button("📝 CORRIGIR"):
            if api_key:
                with st.spinner("Revisando..."):
                    st.info(ai_brain(st.session_state['texto_esboco'], api_key, "Professor"))
    with b3:
        if st.button("👨‍🏫 DAR NOTA"):
            if api_key:
                st.success(ai_brain(f"Dê uma nota e feedback curto: {st.session_state['texto_esboco']}", api_key, "Professor"))

    # Auto Save Simples
    if new_title and text_area != txt_display:
        with open(os.path.join(PASTA, f"{new_title}.txt"), "w") as f: f.write(text_area)

# --- COLUNA DIREITA: CÉREBRO AUXILIAR ---
with c_tools:
    st.markdown("#### 🛰 SATÉLITE")
    
    abas = st.tabs(["IA MODOS", "BÍBLIA", "DEV"])
    
    # 1. MODOS (RAZÃO / SENTIMENTO)
    with abas[0]:
        st.caption("Conselheiro IA")
        pergunta = st.text_area("Dúvida ou Tópico:", height=100)
        
        bt1, bt2 = st.columns(2)
        if bt1.button("🧠 MODO RAZÃO"):
            st.write(ai_brain(pergunta, api_key, "Razão"))
        if bt2.button("❤️ MODO EMOÇÃO"):
            st.write(ai_brain(pergunta, api_key, "Sentimento"))

    # 2. BÍBLIA & ÁUDIO
    with abas[1]:
        ref = st.text_input("Verso (ex: Salmos 23)")
        if ref:
            dados = get_bible(ref.replace(' ', '+'))
            if dados:
                t_b = dados['text']
                st.info(f"{dados['reference']}\n{t_b}")
                
                k1, k2 = st.columns(2)
                if k1.button("⬇ Inserir"):
                    st.session_state['texto_esboco'] += f"\n\n**{dados['reference']}**\n{t_b}"
                    st.rerun()
                if k2.button("🔊 Ouvir"):
                    try:
                        tts = gTTS(t_b, lang='pt')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                            tts.save(f.name)
                            st.audio(f.name)
                    except: st.error("Erro Áudio")
            else: st.warning("Não encontrado")

    # 3. DEV (Códigos)
    with abas[2]:
        st.warning("⚠️ Gerador de Códigos")
        if st.button("Gerar Código Python"):
            if api_key:
                st.code(ai_brain("Crie um código Python simples", api_key, "Coder"))

# --- 8. RODAPÉ INSTAGRAM FIXO ---
st.markdown("""
<div class="footer-insta">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="16" style="vertical-align:middle; margin-right:
