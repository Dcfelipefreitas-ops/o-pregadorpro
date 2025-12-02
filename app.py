import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import PyPDF2
from gtts import gTTS
import time

# --- IMPORTAÇÕES SEGURAS (Evita travamentos se faltar biblioteca) ---
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
st.set_page_config(
    page_title="O Pregador", 
    layout="wide", 
    page_icon="🧷", 
    initial_sidebar_state="expanded"
)

# --- 2. GESTÃO DE ESTADO & MEMÓRIA ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())
if 'anuncio_atual' not in st.session_state: st.session_state['anuncio_atual'] = "📚 Bíblia de Estudo Premium"
if 'idioma' not in st.session_state: st.session_state['idioma'] = "Português"

# --- FUNÇÕES DE LÓGICA E AUTOMAÇÃO ---

def update_streak():
    """Gamificação: Conta dias consecutivos de login"""
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

def safety_filter(prompt):
    """Proteção Ética"""
    blacklist = ["porn", "sex", "erotic", "xxx", "fraude", "hack", "roubar", "cassino", "bet", "apostas"]
    if any(p in prompt.lower() for p in blacklist): return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    """Cérebro de IA"""
    if not key: return "⚠️ Configure a Chave Google no Menu."
    if not safety_filter(prompt): return "🚫 Conteúdo bloqueado por segurança e ética."
    
    try:
        genai.configure(api_key=key)
        
        # Seleção de Idioma para a IA
        lang_instruction = f"Responda sempre em {st.session_state['idioma']}."
        
        roles = {
            "Razão": "Teólogo apologético e histórico. Use lógica e exegese.",
            "Sentimento": "Pastor pentecostal e acolhedor. Use emoção e consolo.",
            "Professor": "Professor de homilética. Corrija o texto, aponte erros gramaticais e teológicos.",
            "Coder": "Programador Senior Python/Streamlit.",
            "Tradutor": "Tradutor especialista em Teologia Cristã.",
            "Marketing": "Gere um título de livro cristão fictício."
        }
        
        system_prompt = f"MODO: {roles.get(mode, 'Assistente')}\n{lang_instruction}\nCONTEXTO: {prompt}"
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(system_prompt).text
    except Exception as e: return f"Erro na Nuvem IA: {e}"

def transcrever_audio_arquivo(uploaded_file):
    """Converte arquivo de áudio em texto (Automacao de Logística)"""
    if not SR_OK: return "Biblioteca speech_recognition não instalada."
    try:
        r = sr.Recognizer()
        with sr.AudioFile(uploaded_file) as source:
            data = r.record(source)
            texto = r.recognize_google(data, language="pt-BR")
            return texto
    except Exception as e: return f"Erro ao transcrever: {e}"

def get_bible(ref):
    """Busca Bíblia Online (API Pública)"""
    try:
        ref_safe = ref.strip().replace(" ", "+")
        # Ajuste inteligente para versiculos tipo "Joao 3:16" virar "Joao+3:16"
        if ":" in ref and "+" not in ref_safe:
            ref_safe = ref.replace(" ", "") # Tenta remover espaços extras
            
        r = requests.get(f"https://bible-api.com/{ref_safe}?translation=almeida", timeout=4)
        return r.json() if r.status_code == 200 else None
    except: return None

def gerar_qr(link):
    """Gera QR Code para Social"""
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def read_pdf_text(file_like):
    """Leitor de PDF Automático"""
    try:
        reader = PyPDF2.PdfReader(file_like)
        pages = [p.extract_text() for p in reader.pages[:40] if p.extract_text()]
        return "\n".join(pages)
    except: return "Erro ao ler PDF."

# --- 3. ESTILOS VISUAIS (DESIGN SYSTEM V13) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {{font-family: 'Inter', sans-serif;}}

    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    /* Efeito de Vidro (Glass) Apple Style */
    [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"], .stSelectbox {{
        background-color: rgba(20, 22, 28, 0.90) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }}

    header, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1rem; max-width: 96%;}}

    /* MARCA PREGADOR (IDENTIDADE VISUAL) */
    .brand-box {{
        text-align: center; padding-bottom: 20px; border-bottom: 1px solid #333; margin-bottom: 15px;
    }}
    .brand-title {{
        font-size: 26px; font-weight: 800; color: #D4AF37; letter-spacing: 2px; margin-top: 5px;
    }}
    
    /* ANUNCIO / MONETIZACAO */
    .ad-card {{
        background: linear-gradient(135deg, #FFD700, #DAA520);
        color: black; padding: 12px; border-radius: 8px; margin-top: 10px; 
        text-align: center; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        animation: fadeIn 2s;
    }}
    
    /* BOTÕES COM HOVER DOURADO */
    .stButton button {{
        background-color: #2b2b2b; color: #eee; border: 1px solid #444; border-radius: 6px; font-weight: 600;
    }}
    .stButton button:hover {{
        border-color: #D4AF37; color: #D4AF37; background-color: #1a1a1a;
    }}
    
    /* RODAPÉ SOCIAL FIXO */
    .footer-insta {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000; color: #666; text-align: center;
        padding: 6px; font-size: 11px; z-index: 9999; border-top: 1px solid #222;
    }}
    .footer-insta a {{ color: #E1306C; font-weight: bold; text-decoration: none; }}
</style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Identidade Visual com Imagem Real (Link CDN Estável)
        st.markdown("""
        <div style="text-align:center; background: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="90">
            <h1 style="color:#D4AF37; font-family:'Inter'; margin-top:10px;">O PREGADOR</h1>
            <p style="color:#ccc">Workstation Pastoral Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_seguro"):
            u = st.text_input("Identificação")
            p = st.text_input("Credencial", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA", type="primary"):
                if u in ["admin", "pastor", "felipe"] and p in ["1234", "pregar", "hope"]:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    update_streak()
                    st.rerun()
                else:
                    st.error("Acesso Não Autorizado")
    st.stop()

# --- 5. APLICAÇÃO PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# >>>> BARRA LATERAL (NAVEGAÇÃO) <<<<
with st.sidebar:
    st.markdown(f"""
    <div class="brand-box">
        <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="50">
        <div class="brand-title">O PREGADOR</div>
        <div style="color:#4CAF50; font-size:12px; margin-top:5px">🟢 {st.session_state['login_streak']} Dias Online</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Pastor(a): {USER.capitalize()}")
    
    # ORGANIZAÇÃO POR ABAS (A Pedido: Configuração separada)
    menu_tabs = st.tabs(["📂 PROJETOS", "⚙️ CONFIG", "📱 SOCIAL"])
    
    with menu_tabs[0]: # Projetos
        try:
            files = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except Exception:
            files = []
        sel = st.radio("Selecione o Estudo:", ["+ Novo Projeto"] + files, label_visibility="collapsed")
        st.write("")
        if st.button("🚪 Sair do Sistema"):
            st.session_state['logado'] = False
            st.rerun()

    with menu_tabs[1]: # Configuração e Ajustes
        st.write("**Personalização**")
        st.session_state['idioma'] = st.selectbox("Idioma da IA:", ["Português", "English", "Español"])
        
        tamanho = st.slider("Área do Editor", 30, 80, st.session_state['layout_split'])
        st.session_state['layout_split'] = tamanho
        
        novo_bg = st.text_input("Wallpaper URL:", st.session_state['bg_url'])
        if st.button("Aplicar Fundo"): 
            st.session_state['bg_url'] = novo_bg
            st.rerun()
            
        st.divider()
        st.write("**Credenciais**")
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key: api_key = st.text_input("Chave Google API:", type="password")

    with menu_tabs[2]: # Social / Monetização
        st.write("**Contato do Dev**")
        try:
            buf = BytesIO()
            img = gerar_qr("https://instagram.com/felipefreitashope")
            img.save(buf)
            st.image(buf, caption="Scan para Instagram")
        except: pass
        
        st.divider()
        st.markdown(f"""
        <div class="ad-card">
            📖 Sugestão:<br>{st.session_state['anuncio_atual']}<br>
            <a href="https://amazon.com.br" style="color:#000; text-decoration:underline;">ADQUIRIR AGORA</a>
        </div>
        """, unsafe_allow_html=True)

# >>>> ÁREA DE TRABALHO FLUIDA <<<<
ratio = st.session_state['layout_split'] / 100
c_editor, c_tools = st.columns([ratio, 1 - ratio])

# Gerenciamento de Arquivo
txt_curr = ""
tit_curr = ""
if sel != "+ Novo Projeto":
    tit_curr = sel
    try: 
        with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: txt_curr = f.read()
    except: pass

if 'last_file' not in st.session_state or st.session_state['last_file'] != sel:
    st.session_state['texto_esboco'] = txt_curr
    st.session_state['last_file'] = sel

# --- EDITOR PRINCIPAL (CENTRO) ---
with c_editor:
    c1, c2 = st.columns([3,1])
    with c1:
        new_tit = st.text_input("TEMA", value=tit_curr, placeholder="Título da Pregação...", label_visibility="collapsed")
    with c2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if new_tit:
                with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(st.session_state['texto_esboco'])
                # Lógica de Anúncio Inteligente
                if api_key:
                    sugestao = ai_brain(f"Indique 1 livro cristão clássico sobre: '{new_tit}'. Apenas Título.", api_key, "Marketing")
                    st.session_state['anuncio_atual'] = sugestao
                st.toast("Estudo Salvo e Seguro!")
                st.rerun()

    # CAMPO DE TEXTO DO USUÁRIO
    main_text = st.text_area("PAPEL", value=st.session_state['texto_esboco'], height=700, label_visibility="collapsed")
    st.session_state['texto_esboco'] = main_text

    # --- BARRA DE AUTOMAÇÃO E CORRETOR (Abaixo do texto) ---
    st.caption("🛠️ Ações Rápidas de IA")
    
    # NOVA FEATURE: Microfone Nativo (Grava -> Texto no Editor)
    try:
        audio_val = st.audio_input("🎤 Ditar para o Editor (Clique para gravar)")
        if audio_val and api_key:
            texto_voz = transcrever_audio_arquivo(audio_val) # Transcreve
            if texto_voz:
                st.session_state['texto_esboco'] += f"\n\n[Voz]: {texto_voz}"
                st.success("Texto transcrito adicionado ao final!")
                st.rerun()
    except: pass

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("✨ REVISAR ORTOGRAFIA"):
            if api_key:
                with st.spinner("Professor revisando..."):
                    res = ai_brain(f"Corrija apenas a gramática mantendo o sentido e estilo pastoral: \n{main_text}", api_key, "Professor")
                    # Automatização de Copia: Mostra em bloco de código
                    st.code(res, language="text")
                    st.success("Copie o texto acima 👆")
    with b2:
        if st.button("🗣 TRADUZIR TUDO"):
            if api_key:
                res = ai_brain(main_text, api_key, "Tradutor")
                st.session_state['texto_esboco'] = res
                st.rerun()
    with b3:
        if st.button("🎓 AVALIAR HOMILÉTICA"):
            if api_key:
                st.info(ai_brain(main_text, api_key, "Professor"))

    # Auto Save (Silent)
    if new_tit and main_text != txt_curr:
        with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(main_text)

# --- SATÉLITE LATERAL (FERRAMENTAS) ---
with c_tools:
    st.markdown("#### 🧠 CENTRAL")
    
    # Organize ferramentas em Abas Claras
    tab_ia, tab_biblia, tab_pdf, tab_dev = st.tabs(["🤖 IA", "📖 BÍBLIA", "📚 LIVRO", "👨‍💻 DEV"])
    
    # 1. MODOS INTELIGENTES (RAZÃO x EMOÇÃO)
    with tab_ia:
        st.write("Conselheiro Virtual")
        ask = st.text_area("Pergunta:", height=100, placeholder="Digite sua dúvida teológica...")
        c_r, c_e = st.columns(2)
        if c_r.button("🧠 Razão"):
            if api_key: st.markdown(ai_brain(ask, api_key, "Razão"))
        if c_e.button("❤️ Emoção"):
            if api_key: st.markdown(ai_brain(ask, api_key, "Sentimento"))

    # 2. BÍBLIA COM ÁUDIO FIX
    with tab_biblia:
        st.write("Consulta Rápida")
        ref = st.text_input("Verso (Ex: Jo 3:16)")
        if ref:
            bd = get_bible(ref)
            if bd:
                t_b = bd['text']
                st.success(f"{bd['reference']}")
                st.write(t_b)
                
                ck1, ck2 = st.columns(2)
                if ck1.button("⬇ Inserir"):
                    st.session_state['texto_esboco'] += f"\n\n**{bd['reference']}**\n{t_b}"
                    st.rerun()
                
                if ck2.button("🔊 Ouvir"):
                    # Fix do bug de audio: usar hash unico no nome ou bytes diretos
                    try:
                        tts = gTTS(t_b, lang='pt')
                        # Salva num buffer de memoria ao inves de arquivo para não dar conflito
                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        st.audio(mp3_fp, format='audio/mp3')
                    except Exception as e: st.error(f"Erro Audio: {e}")
            else: st.warning("Versículo não encontrado. Verifique a grafia.")

    # 3. LEITOR PDF (Extração)
    with tab_pdf:
        st.write("Resumir Livro")
        pdf = st.file_uploader("Upload PDF", type="pdf")
        if pdf and st.button("Analisar PDF"):
            if api_key:
                raw = read_pdf_text(pdf)
                st.success("Lido! Gerando resumo...")
                summary = ai_brain(f"Resuma este texto teológico: {raw[:4000]}", api_key, "Professor")
                st.markdown(summary)

    # 4. MODO DEV (Gerar Código Livre)
    with tab_dev:
        st.caption("Fábrica de Código")
        prompt_dev = st.text_input("O que criar?")
        if st.button("Codar"):
            if api_key: st.code(ai_brain(prompt_dev, api_key, "Coder"))

# --- 8. RODAPÉ FIXO INSTA ---
st.markdown("""
<div class="footer-insta">
    DESENVOLVEDOR: <a href="https://instagram.com/felipefreitashope" target="_blank">@FELIPEFREITASHOPE</a> 
    | V13 PLATINUM
</div>
""", unsafe_allow_html=True)
