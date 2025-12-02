import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import PyPDF2
from gtts import gTTS

# --- IMPORTAÇÕES OPCIONAIS (PREVENÇÃO DE ERROS) ---
try:
    import speech_recognition as sr
    SR_OK = True
except Exception:
    SR_OK = False

try:
    import google.generativeai as genai
    GENAI_INSTALLED = True
except Exception:
    GENAI_INSTALLED = False

try:
    from duckduckgo_search import DDGS
    DDGS_OK = True
except:
    DDGS_OK = False

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
    blacklist = ["porn", "sex", "erotic", "xxx", "fraude", "hack", "roubar", "cassino", "bet"]
    if any(p in prompt.lower() for p in blacklist):
        return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    """
    Cérebro IA Principal
    """
    if not key:
        return "⚠️ Configure a Chave Google no Menu Lateral."
    if not safety_filter(prompt):
        return "🚫 Conteúdo Bloqueado por Ética."
    if not GENAI_INSTALLED:
        return "⚠️ Biblioteca google-generativeai não instalada."
        
    try:
        genai.configure(api_key=key)
        roles = {
            "Razão": "Teólogo apologético, use lógica, grego/hebraico e história.",
            "Sentimento": "Pastor pentecostal, use emoção, fervor e consolo.",
            "Professor": "Professor de homilética. Corrija o texto e dê nota 0-10 com dicas.",
            "Coder": "Especialista em Python/Streamlit. Gere código funcional.",
            "Tradutor": "Traduza para Português Culto Teológico.",
            "Marketing": "Gere sugestões de livros cristãos reais baseados no tema."
        }
        system_prompt = f"MODO: {roles.get(mode, 'Assistente')}\nCONTEXTO: {prompt}"
        model = genai.GenerativeModel('gemini-1.5-flash')
        out = model.generate_content(system_prompt)
        return out.text if hasattr(out, 'text') else str(out)
    except Exception as e:
        return f"Erro IA: {e}"

# --- 4. FUNÇÕES AUXILIARES ---
def get_bible(ref):
    if not ref: return None
    try:
        ref_safe = ref.strip().replace(" ", "+")
        # Correção para formato 'Jo+3:16'
        if ":" not in ref_safe and "+" in ref_safe:
            parts = ref_safe.split("+")
            if len(parts) >= 3:
                ref_safe = f"{parts[0]}+{parts[1]}:{parts[2]}"
        
        url = f"https://bible-api.com/{ref_safe}?translation=almeida"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def gerar_qr(link):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def read_pdf_text(file_like, max_pages=30):
    try:
        reader = PyPDF2.PdfReader(file_like)
        pages = []
        for i, p in enumerate(reader.pages):
            if i >= max_pages: break
            text = p.extract_text()
            if text: pages.append(text)
        return "\n\n".join(pages)
    except Exception as e:
        return f"Erro lendo PDF: {e}"

# --- 5. CSS VISUAL (MANTIDO EXATAMENTE COMO PEDIU) ---
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
                if (u=="admin" and p=="1234") or (u=="pastor" and p=="pregar") or (u=="felipe" and p=="hope"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    update_streak()
                    st.rerun()
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
            st.rerun()

    with tab_set:
        # AQUI FOI FEITA A CORREÇÃO DA LINHA CORTADA
        st.write("Ajustes Visuais")
        val_slider = st.slider("Layout", 30, 80, st.session_state['layout_split'])
        st.session_state['layout_split'] = val_slider
        
        novo_bg = st.text_input("Fundo URL:", st.session_state['bg_url'])
        if st.button("Aplicar Fundo"): 
            st.session_state['bg_url'] = novo_bg
            st.rerun()
            
        st.divider()
        # Chave API (Salva ou input)
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key: api_key = st.text_input("API Key Google:", type="password")

    with tab_qr:
        st.caption("Acesse @felipefreitashope")
        try:
            buf = BytesIO()
            img = gerar_qr("https://instagram.com/felipefreitashope")
            img.save(buf)
            st.image(buf)
        except: st.error("Instale qrcode e pillow no requirements.txt")

    # ÁREA DE ADS GOSPEL (Monetização)
    st.markdown("---")
    st.markdown("##### ⭐ Loja do Reino")
    st.markdown(f"""
    <div class="ad-box">
        {st.session_state['anuncio_atual']}<br>
        <a href="https://amazon.com.br" target="_blank" style="font-size:12px; text-decoration:underline;">VER OFERTA</a>
    </div>
    """, unsafe_allow_html=True)

# LAYOUT FLUIDO (CENTRO)
ratio = st.session_state['layout_split'] / 100
c_editor, c_tools = st.columns([ratio, 1 - ratio])

# Lógica Texto e Arquivo
txt_curr = ""
tit_curr = ""
if sel != "+ Novo":
    tit_curr = sel
    try: 
        with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: txt_curr = f.read()
    except: pass

# Se estiver abrindo arquivo novo, carrega no editor
if 'last_loaded' not in st.session_state or st.session_state['last_loaded'] != sel:
    st.session_state['texto_esboco'] = txt_curr
    st.session_state['last_loaded'] = sel

# >>> PAINEL ESQUERDO: EDITOR
with c_editor:
    cc1, cc2 = st.columns([3,1])
    with cc1:
        new_tit = st.text_input("TEMA", value=tit_curr, placeholder="Título da Mensagem...", label_visibility="collapsed")
    with cc2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if new_tit:
                with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(st.session_state['texto_esboco'])
                # Gera novo anúncio baseado no título
                if api_key:
                    sugestao = ai_brain(f"Sugira um livro cristão para o tema '{new_tit}'", api_key, "Marketing")
                    st.session_state['anuncio_atual'] = sugestao
                st.toast("Salvo!")
                st.rerun()

    # Campo de Texto Principal
    main_text = st.text_area("EDITOR", value=st.session_state['texto_esboco'], height=720, label_visibility="collapsed")
    st.session_state['texto_esboco'] = main_text # Sincroniza estado

    # Barra de Ferramentas IA (No pé do texto)
    st.caption("Ferramentas do Editor")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🗣 TRADUZIR TUDO"):
            if api_key:
                with st.spinner("Traduzindo..."):
                    res = ai_brain(main_text, api_key, "Tradutor")
                    st.session_state['texto_esboco'] = res
                    st.rerun()
    with b2:
        if st.button("📝 CORRIGIR GRAMÁTICA"):
            if api_key:
                with st.spinner("Corrigindo..."):
                    res = ai_brain(f"Corrija apenas a gramática mantendo a teologia: {main_text}", api_key, "Coder")
                    st.session_state['texto_esboco'] = res
                    st.rerun()
    with b3:
        if st.button("🎓 AVALIAR ESBOÇO"):
            if api_key:
                with st.spinner("Avaliando..."):
                    feedback = ai_brain(main_text, api_key, "Professor")
                    st.info(feedback)

    # Autosave
    if new_tit and main_text != txt_curr and txt_curr != "":
        # Salvamento automático suave
        pass

# >>> PAINEL DIREITO: CÉREBRO
with c_tools:
    st.markdown("#### 🧠 CENTRAL")
    abas = st.tabs(["IA CHAT", "BÍBLIA", "LIVROS"])
    
    with abas[0]:
        st.write("Conselheiro Virtual")
        ask = st.text_area("Pergunta:", height=100)
        col_raz, col_emo = st.columns(2)
        if col_raz.button("🧠 RAZÃO"):
            st.markdown(ai_brain(ask, api_key, "Razão"))
        if col_emo.button("❤️ EMOÇÃO"):
            st.markdown(ai_brain(ask, api_key, "Sentimento"))

    with abas[1]:
        st.write("Bíblia Rápida")
        ref = st.text_input("Verso (Jo 3 16)")
        if ref:
            bd = get_bible(ref)
            if bd:
                txt_b = bd['text']
                st.success(f"{bd['reference']}")
                st.write(txt_b)
                
                ck1, ck2 = st.columns(2)
                if ck1.button("⬇ Inserir no Texto"):
                    st.session_state['texto_esboco'] += f"\n\n**{bd['reference']}**\n{txt_b}"
                    st.rerun()
                if ck2.button("🔊 Ouvir"):
                    try:
                        tts = gTTS(txt_b, lang='pt')
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                            tts.save(f.name)
                            st.audio(f.name)
                    except: st.error("Erro Áudio")
            else: st.warning("Não encontrado. Tente 'Jo 3 16'")

    with abas[2]:
        st.write("Leitor de Livros (PDF)")
        pdf_up = st.file_uploader("Upload PDF", type="pdf")
        if pdf_up:
            if st.button("Ler e Resumir"):
                raw = read_pdf_text(pdf_up)
                st.success("Lido!")
                summary = ai_brain(f"Resuma este conteúdo teológico: {raw[:3000]}", api_key, "Professor")
                st.markdown(summary)

# --- 8. RODAPÉ FIXO ---
st.markdown("""
<div class="footer-insta">
    DESENVOLVEDOR: <a href="https://instagram.com/felipefreitashope" target="_blank">@FELIPEFREITASHOPE</a> 
    | V12 PRO BUSINESS
</div>
""", unsafe_allow_html=True)
