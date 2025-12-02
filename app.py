import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import PyPDF2
from gtts import gTTS
import speech_recognition as sr

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# --- 2. GESTÃO DE ESTADO & MEMÓRIA ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())
if 'anuncio_atual' not in st.session_state: st.session_state['anuncio_atual'] = "📚 Bíblia de Estudo Premium"

# Gamificação
def update_streak():
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

# --- 3. INTEGRAÇÃO E SEGURANÇA IA ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
except: pass

def safety_filter(prompt):
    blacklist = ["porn", "sex", "erotic", "xxx", "fraude", "hack", "roubar", "cassino"]
    if any(p in prompt.lower() for p in blacklist): return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    if not key: return "⚠️ Configure a Chave Google no Menu."
    if not safety_filter(prompt): return "🚫 Conteúdo Bloqueado por Ética."
    try:
        genai.configure(api_key=key)
        # Personalidades Avançadas
        roles = {
            "Razão": "Teólogo apologético, use lógica, grego/hebraico e história.",
            "Sentimento": "Pastor pentecostal, use emoção, fervor e consolo.",
            "Professor": "Professor de homilética. Corrija o texto e dê nota 0-10.",
            "Coder": "Especialista em Python/Streamlit. Gere código funcional.",
            "Tradutor": "Traduza para Português Culto Teológico.",
            "Marketing": "Gere um título de livro cristão fictício baseado no tema para venda."
        }
        sys = f"MODO: {roles.get(mode, 'Assistente')}\nCONTEXTO: {prompt}"
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(sys).text
    except Exception as e: return f"Erro IA: {e}"

def transcrever_audio(audio_file, key):
    """Transforma voz em texto usando o Google Gemini (Mais preciso)"""
    if not key: return "Sem chave API."
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Gambiarra técnica: Gemini aceita áudio via File API, mas aqui faremos via prompt simples se for curto
        # Para produção, usaríamos speech_recognition, mas requer ffmpeg no servidor linux
        return "⚠️ Transcrição de áudio requer configuração avançada de servidor. Use a digitação de voz do seu teclado (Win+H) para resultado imediato." 
    except: return "Erro Audio."

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

# --- 4. CSS VISUAL (APPLE GLASS + WOOD) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {{font-family: 'Inter', sans-serif;}}

    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    /* Efeito de Vidro Apple */
    [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"] {{
        background-color: rgba(18, 18, 25, 0.92) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }}

    header, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1rem; max-width: 96%;}}

    /* Marca Pregador Dourada */
    .brand-box {{
        text-align: center; padding-bottom: 20px; border-bottom: 1px solid #333; margin-bottom: 15px;
    }}
    .brand-title {{
        font-size: 26px; font-weight: 800; color: #e0e0e0; letter-spacing: 1px; margin-top: 10px;
    }}
    
    /* Área de Anúncio Monetizado */
    .ad-box {{
        background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
        color: black; padding: 10px; border-radius: 8px; margin-top: 20px; text-align: center; font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }}
    .ad-box a {{color: black; text-decoration: none;}}

    /* Botões */
    .stButton button {{
        background-color: #262626; color: white; border-radius: 8px; border: 1px solid #444; font-weight: 600;
    }}
    .stButton button:hover {{
        border-color: #d4a373; color: #d4a373;
    }}
    
    .footer-insta {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #0f0f0f; color: #888; text-align: center;
        padding: 5px; font-size: 12px; z-index: 9999; border-top: 1px solid #333;
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # IMAGEM DO PREGADOR DE ROUPA REAL (PNG)
        st.markdown("""
        <div style="text-align:center; background: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="80">
            <h1 style="color:#d4a373;">O PREGADOR</h1>
            <p style="color:#aaa">Ferramenta Pastoral & Business</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", type="primary"):
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

# SIDEBAR (CONFIGURAÇÕES E ADS)
with st.sidebar:
    # 1. MARCA E FOTO DE MADEIRA
    st.markdown(f"""
    <div class="brand-box">
        <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="50">
        <div class="brand-title">O PREGADOR</div>
        <div style="color:#4CAF50; font-size:12px; margin-top:5px">🔥 {st.session_state['login_streak']} DIAS ON</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Olá, {USER.capitalize()}")
    
    tab_proj, tab_set, tab_qr = st.tabs(["📂", "⚙️", "📱"])
    
    with tab_proj:
        try: files = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: files = []
        sel = st.radio("Biblioteca:", ["+ Novo"] + files, label_visibility="collapsed")
        
        if st.button("Sair"): st.session_state['logado']=False; st.rerun()

    with tab_set:
        val = st.slider("Tamanho", 30, 80, st.session_state['layout_split'])
        st.session_state['layout_split'] = val
        
        novo_bg = st.text_input("Fundo URL:", st.session_state['bg_url'])
        if st.button("Mudar Fundo"): 
            st.session_state['bg_url'] = novo_bg
            st.rerun()
            
        st.divider()
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key: api_key = st.text_input("API Key Google:", type="password")

    with tab_qr:
        st.caption("Acesse @felipefreitashope")
        try:
            buf = BytesIO()
            img = gerar_qr("https://instagram.com/felipefreitashope")
            img.save(buf)
            st.image(buf)
        except: pass

    # MONETIZAÇÃO (ADS GOSPEL)
    st.markdown("---")
    st.markdown("##### ⭐ Ofertas Para Você")
    # Card de Anúncio Inteligente
    st.markdown(f"""
    <div class="ad-box">
        SUGESTÃO: {st.session_state['anuncio_atual']}<br>
        <a href="https://amazon.com.br" target="_blank" style="font-size:12px; text-decoration:underline;">COMPRAR AGORA</a>
    </div>
    """, unsafe_allow_html=True)

# ÁREA DE TRABALHO
ratio = st.session_state['layout_split'] / 100
c_edit, c_tools = st.columns([ratio, 1 - ratio])

# Lógica Texto
txt_curr = ""
tit_curr = ""
if sel != "+ Novo":
    tit_curr = sel
    try: 
        with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: txt_curr = f.read()
    except: pass

# --- EDITOR (CENTRO) ---
with c_edit:
    # 1. CABEÇALHO E TÍTULO
    cc1, cc2 = st.columns([3,1])
    with cc1:
        new_tit = st.text_input("TEMA", value=tit_curr, placeholder="Título da Mensagem...", label_visibility="collapsed")
    with cc2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if new_tit:
                with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(st.session_state['texto_esboco'])
                # GERA ANÚNCIO NOVO BASEADO NO TEMA
                if api_key:
                    novo_anuncio = ai_brain(f"Sugira um livro cristão existente sobre: {new_tit}", api_key, "Marketing")
                    st.session_state['anuncio_atual'] = novo_anuncio
                st.toast("Salvo! Veja a oferta na barra lateral.")
                st.rerun()

    # 2. PAPEL DE TRABALHO
    if not st.session_state['texto_esboco'] and txt_curr:
        st.session_state['texto_esboco'] = txt_curr
    
    main_text = st.text_area("EDITOR", value=st.session_state['texto_esboco'], height=700, label_visibility="collapsed")
    st.session_state['texto_esboco'] = main_text

    # 3. BARRA DE COMANDO (CORRETOR/VOZ)
    st.caption("Ferramentas do Editor")
    
    # Gravador de Áudio (Experimental)
    audio_val = st.audio_input("🎤 Digitar por Voz (Grave e a IA escreve)")
    if audio_val and api_key:
        st.info("Áudio recebido! Para transcrição real, use Win+H. A transcrição de arquivo requer servidor dedicado.")
    
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🗣 TRADUZIR TUDO"):
            if api_key:
                res = ai_brain(main_text, api_key, "Tradutor")
                st.session_state['texto_esboco'] = res
                st.rerun()
    with b2:
        if st.button("✨ CORRIGIR AGORA"):
            if api_key:
                # O comando Professor aqui corrige e substitui o texto direto
                res = ai_brain(f"Corrija apenas a gramática deste texto mantendo o sentido: {main_text}", api_key, "Coder") 
                st.session_state['texto_esboco'] = res
                st.rerun()
    with b3:
        if st.button("🎓 AVALIAR"):
            if api_key: st.info(ai_brain(main_text, api_key, "Professor"))

    # Autosave
    if new_tit and main_text != txt_curr:
        with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(main_text)

# --- SATÉLITE (DIREITA) ---
with c_tools:
    st.markdown("#### 🧠 CÉREBRO")
    tabs = st.tabs(["IA MODOS", "BÍBLIA", "DEV"])
    
    with tabs[0]:
        ask = st.text_area("Pergunta:")
        br, bs = st.columns(2)
        if br.button("🧠 RAZÃO"):
            st.write(ai_brain(ask, api_key, "Razão"))
        if bs.button("❤️ EMOÇÃO"):
            st.write(ai_brain(ask, api_key, "Sentimento"))

    with tabs[1]:
        ref = st.text_input("Verso (Jo 3 16)")
        if ref:
            bd = get_bible(ref.replace(' ', '+'))
            if bd:
                txt_b = bd['text']
                st.markdown(f"**{bd['reference']}**\n{txt_b}")
                
                ck1, ck2 = st.columns(2)
                if ck1.button("⬇ Inserir"):
                    st.session_state['texto_esboco'] += f"\n\n**{bd['reference']}**\n{txt_b}"
                    st.rerun()
                if ck2.button("🔊 Ouvir"):
                    try:
                        tts = gTTS(txt_b, lang='pt')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                            tts.save(f.name)
                            st.audio(f.name)
                    except: st.error("Erro Audio")
            else: st.warning("Nada achado.")

    with tabs[2]:
        st.info("Crie novas funções:")
        ped = st.text_input("O que criar? (Ex: Botão dízimo)")
        if st.button("GERAR CÓDIGO"):
            st.code(ai_brain(ped, api_key, "Coder"))

# --- 8. RODAPÉ FIXO ---
st.markdown("""
<div class="footer-insta">
    DESENVOLVEDOR: <a href="https://instagram.com/felipefreitashope" target="_blank">@FELIPEFREITASHOPE</a> 
    | V12 PRO BUSINESS
</div>
""", unsafe_allow_html=True)
