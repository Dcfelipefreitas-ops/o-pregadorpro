# app.py (corrigido - cole por cima do arquivo atual)
import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime
import PyPDF2
from gtts import gTTS

# speech_recognition é opcional — se não estiver disponível, app mostra instrução
try:
    import speech_recognition as sr
    SR_OK = True
except Exception:
    SR_OK = False

# generative AI (opcional)
try:
    import google.generativeai as genai
    GENAI_INSTALLED = True
except Exception:
    GENAI_INSTALLED = False

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# --- 2. GESTÃO DE ESTADO & MEMÓRIA ---
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state:
    st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state:
    st.session_state['layout_split'] = 60
if 'texto_esboco' not in st.session_state:
    st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state:
    st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state:
    st.session_state['last_login'] = str(datetime.now().date())
if 'anuncio_atual' not in st.session_state:
    st.session_state['anuncio_atual'] = "📚 Bíblia de Estudo Premium"
if 'api_input' not in st.session_state:
    st.session_state['api_input'] = ""

# Gamificação
def update_streak():
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

# --- 3. INTEGRAÇÃO E SEGURANÇA IA ---
def safety_filter(prompt):
    blacklist = ["porn", "sex", "erotic", "xxx", "fraude", "hack", "roubar", "cassino"]
    if any(p in prompt.lower() for p in blacklist):
        return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    """
    Usa google.generativeai se instalado e chave fornecida.
    Caso contrário, devolve mensagem instructiva.
    """
    if not key:
        return "⚠️ Configure a Chave Google no Menu (st.secrets['GOOGLE_API_KEY'] ou no campo de configurações)."
    if not safety_filter(prompt):
        return "🚫 Conteúdo Bloqueado por Ética."
    if not GENAI_INSTALLED:
        return "⚠️ Biblioteca google.generativeai não está instalada no ambiente."
    try:
        genai.configure(api_key=key)
        roles = {
            "Razão": "Teólogo apologético, use lógica, grego/hebraico e história.",
            "Sentimento": "Pastor pentecostal, use emoção, fervor e consolo.",
            "Professor": "Professor de homilética. Corrija o texto e dê nota 0-10.",
            "Coder": "Especialista em Python/Streamlit. Gere código funcional.",
            "Tradutor": "Traduza para Português Culto Teológico.",
            "Marketing": "Gere um título de livro cristão fictício baseado no tema para venda."
        }
        system_prompt = f"MODO: {roles.get(mode,'Assistente')}\nCONTEXTO: {prompt}"
        model = genai.GenerativeModel('gemini-1.5-flash')
        out = model.generate_content(system_prompt)
        # some SDKs return object with .text, others nested; handle both
        if hasattr(out, "text"):
            return out.text
        if isinstance(out, dict):
            return str(out)
        return str(out)
    except Exception as e:
        return f"Erro IA: {e}"

# Transcrição de áudio simples via speech_recognition (WAV aceito)
def transcrever_arquivo_audio(uploaded_file):
    if not SR_OK:
        return ("Transcrição local não disponível. Instale 'speechrecognition' e 'pydub' + 'ffmpeg' no servidor "
                "para suportar formatos além de WAV.")
    # speech_recognition suporta WAV nativamente
    try:
        recognizer = sr.Recognizer()
        # precisamos salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_file.read())
            tmp.flush()
            tmp_path = tmp.name
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="pt-BR")
                return text
            except sr.UnknownValueError:
                return "Não foi possível reconhecer o áudio."
            except sr.RequestError as e:
                return f"Erro no serviço de reconhecimento: {e}"
    except Exception as e:
        return f"Erro ao processar áudio: {e}"

# --- 4. FUNÇÕES AUXILIARES ---
def get_bible(ref):
    """
    Aceita formatos como:
    - 'Jo 3 16'
    - 'John 3:16'
    Faz tentativas seguras de chamada ao bible-api.
    """
    if not ref:
        return None
    # normalizar
    cleaned = ref.strip().replace(":", " ").replace(",", " ")
    parts = cleaned.split()
    if len(parts) < 3:
        # se o usuário passou 'Jo 3' ou similar - aborta
        try_url = ref.replace(" ", "+")
    else:
        book = parts[0]
        chapter = parts[1]
        verse = parts[2]
        try_url = f"{book}+{chapter}:{verse}"
    url = f"https://bible-api.com/{try_url}?translation=almeida"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            j = r.json()
            # esperado: {'reference': 'John 3:16', 'text': '...'}
            return j
        return None
    except Exception:
        return None

def gerar_qr(link):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def read_pdf_text(file_like, max_pages=20):
    try:
        reader = PyPDF2.PdfReader(file_like)
        pages = []
        for i, p in enumerate(reader.pages):
            if i >= max_pages: break
            pages.append(p.extract_text() or "")
        return "\n\n".join(pages)
    except Exception as e:
        return f"Erro lendo PDF: {e}"

# --- 5. CSS VISUAL (mantive seu visual) ---
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

# --- 6. TELA DE LOGIN (mantive seu fluxo) ---
if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
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
                    st.experimental_rerun()
                else:
                    st.error("Acesso Negado")
    st.stop()

# --- 7. APP PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA, exist_ok=True)

# SIDEBAR (CONFIGURAÇÕES E ADS)
with st.sidebar:
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
        try:
            files = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except Exception:
            files = []
        sel = st.radio("Biblioteca:", ["+ Novo"] + files, label_visibility="collapsed")

        if st.button("Sair"):
            st.session_state['logado'] = False
            st.experimental_rerun()

    with tab_set:
        val = st.slider("Tamanho", 30, 80, st.session_state['layout_split'])
        st.session
