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

# --- 2. SISTEMA DE LOGIN E GAMIFICAÇÃO (STREAK) ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())

# Função para atualizar contador de dias seguidos
def update_streak():
    hoje = str(datetime.now().date())
    # Lógica simples para demonstrar o streak
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

# --- 3. INTEGRAÇÃO E SEGURANÇA IA ---
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
except: pass

def safety_filter(prompt):
    """Filtro de Segurança contra Fraudes e Conteúdo Impróprio"""
    termo = prompt.lower()
    # Lista de bloqueio
    proibidos = ["porn", "sex", "erotic", "xxx", "fraude", "hack", "cartão de crédito", "roubar", "cassino", "bet", "aposta"]
    if any(p in termo for p in proibidos):
        return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    """Cérebro Central da IA (Razão, Emoção, Código, Professor)"""
    if not key: return "⚠️ IA Offline. Configure a Chave Google no menu."
    
    # 1. Filtro de Segurança
    if not safety_filter(prompt):
        return "🚫 ACESSO NEGADO: Este conteúdo viola os termos de ética do aplicativo O Pregador."
    
    try:
        genai.configure(api_key=key)
        
        # 2. Definição de Personalidades (O Prompt do Sistema)
        system_role = ""
        if mode == "Razão":
            system_role = "Você é um teólogo apologético e escolástico. Use lógica, exegese profunda do grego/hebraico, história da igreja e fatos racionais. Seja sério e acadêmico."
        elif mode == "Sentimento":
            system_role = "Você é um pastor conselheiro, cheio de empatia e unção. Use uma linguagem emocional, poética, de consolo e encorajamento espiritual."
        elif mode == "Professor":
            system_role = "Você é um professor de homilética rígido mas justo. Analise o texto do aluno, aponte erros de concordância, lógica teológica e dê uma nota de 0 a 10 com dicas práticas."
        elif mode == "Coder":
            system_role = "Você é um especialista senior em Python e Streamlit. Gere códigos Open Source seguros, limpos e funcionais. Não explique, apenas forneça o bloco de código."
        elif mode == "Tradutor":
            system_role = "Você é um tradutor especialista em literatura cristã. Traduza mantendo a terminologia teológica correta em Português do Brasil."
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"MODO ATIVO: {system_role}\n\nSOLICITAÇÃO: {prompt}"
        
        return model.generate_content(full_prompt).text
    except Exception as e: return f"Erro na conexão com IA: {e}"

# --- 4. FUNÇÕES ÚTEIS (Audio, QR, Bible) ---
def get_bible(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida", timeout=2)
        return r.json() if r.status_code == 200 else None
    except: return None

def gerar_qr_code(link):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="#111")
    return img

# --- 5. CSS (VISUAL EMPRESARIAL DARK / LAN HOUSE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;600&family=Lato:wght@400;700&display=swap');

    /* Geral */
    .stApp {background-color: #080808; color: #fff;}
    .block-container {padding-top: 1rem;}
    header, footer {visibility: hidden;}

    /* Sidebar - Estilo Painel de Controle */
    [data-testid="stSidebar"] {
        background-color: #111;
        border-right: 1px solid #333;
    }

    /* Logo Personalizada */
    .logo-area {
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
    }
    .app-title {
        font-family: 'Lato', sans-serif;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #d4a373; /* Cor Madeira */
        text-transform: uppercase;
    }

    /* Text Area - O Centro de Comando */
    .stTextArea textarea {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #333;
        border-radius: 8px;
        font-family: 'Roboto Mono', monospace; /* Fonte estilo Código */
        font-size: 16px;
        padding: 20px;
    }
    .stTextArea textarea:focus { border-color: #d4a373; box-shadow: 0 0 10px rgba(212, 163, 115, 0.2); }

    /* Botões de Ação */
    .stButton button {
        width: 100%;
        background-color: #222;
        color: white;
        border: 1px solid #444;
        border-radius: 6px;
        transition: 0.3s;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 12px;
    }
    .stButton button:hover {
        background-color: #d4a373;
        color: black;
        border-color: #d4a373;
    }

    /* Footer Social */
    .footer-insta {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0f0f0f;
        padding: 12px;
        text-align: center;
        border-top: 1px solid #333;
        font-size: 14px;
        z-index: 99999;
        color: #777;
    }
    .footer-insta a { text-decoration: none; color: #E1306C; font-weight: bold; }
    
    /* Streak Badge */
    .streak-badge {
        background: linear-gradient(45deg, #d4a373, #8b5e3c);
        color: black;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 6. TELA DE LOGIN ---
# Link direto para imagem de pregador de madeira clássico (vintage clothespin)
ICON_URL = "https://cdn-icons-png.flaticon.com/512/9384/9384192.png" 

if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Login Visual
        st.markdown(f"""
        <div style='text-align: center'>
            <img src='{ICON_URL}' width='100'>
            <h1 style='color: white; font-family: Lato;'>O PREGADOR</h1>
            <p style='color: #666; letter-spacing: 1px;'>VERSÃO EMPRESARIAL PRO</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            u = st.text_input("ID DE ACESSO")
            p = st.text_input("CHAVE DE SEGURANÇA", type="password")
            if st.form_submit_button("CONECTAR AO SISTEMA", type="primary"):
                # Senhas permitidas
                if (u=="admin" and p=="1234") or (u=="pastor" and p=="pregar") or (u=="felipe" and p=="hope"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    update_streak()
                    st.rerun()
                else: st.error("Acesso Negado.")
    st.stop()

# --- 7. SISTEMA PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# ==================== BARRA LATERAL ====================
with st.sidebar:
    # Marca do Pregador
    st.markdown(f"""
    <div class="logo-area">
        <img src="{ICON_URL}" width="60"><br>
        <span class="app-title">O PREGADOR</span><br>
        <span style="font-size: 10px; color: #555;">SISTEMA v3.0 | BY FELIPE FREITAS</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Gamificação
    st.markdown(f"<div style='text-align:center'><span class='streak-badge'>🔥 {st.session_state['login_streak']} DIAS CONECTADO</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Chave API Google (Essencial)
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key: api_key = st.text_input("CHAVE GOOGLE IA (API)", type="password")
    if api_key: st.caption("✅ INTELIGÊNCIA ARTIFICIAL: ONLINE")
    else: st.caption("🔴 INTELIGÊNCIA ARTIFICIAL: OFFLINE")

    # Arquivos
    st.write("📂 **MEUS PROJETOS**")
    try: arquivos = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: arquivos = []
    escolha = st.radio("Selecione:", ["+ NOVO PROJETO"] + arquivos, label_visibility="collapsed")
    
    st.markdown("---")
    
    # ÁREA DE QR CODE (Conexão Social)
    st.write("📱 **ACESSO SOCIAL**")
    try:
        link_app = "https://instagram.com/felipefreitashope"
        img_qr = gerar_qr_code(link_app)
        buf = BytesIO()
        img_qr.save(buf)
        st.image(buf, caption="Scan para Instagram", width=150)
    except: st.error("Erro QR")

    st.markdown("---")
    if st.button("DESLOGAR"): 
        st.session_state['logado']=False
        st.rerun()

# ==================== ÁREA DE TRABALHO (CENTER) ====================
c_editor, c_tools = st.columns([2, 1])

# Lógica de Carregamento de Arquivos
texto = ""
titulo_input = ""
if escolha != "+ NOVO PROJETO":
    titulo_input = escolha
    try:
        with open(os.path.join(PASTA, f"{escolha}.txt"), "r") as f: texto = f.read()
    except: pass

with c_editor:
    # 1. CABEÇALHO DO EDITOR
    col_tit, col_act = st.columns([3, 1])
    with col_tit:
        novo_titulo = st.text_input("TEMA DA MENSAGEM", value=titulo_input, placeholder="Digite o Título...", label_visibility="collapsed")
    with col_act:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if novo_titulo:
                with open(os.path.join(PASTA, f"{novo_titulo}.txt"), "w") as f: f.write(texto)
                st.toast("Projeto Salvo e Sincronizado!")
    
    # 2. O EDITOR DE TEXTO (Papel)
    # Importante: A altura está ajustada para ser o foco principal
    txt_area = st.text_area("CORPO", value=texto, height=700, label_visibility="collapsed")
    
    # 3. BARRA DE COMANDO DA IA (No pé do editor)
    st.markdown("### ⚡ AÇÕES DE INTELIGÊNCIA")
    
    # Botão de TRADUTOR INTERNO
    c_tr1, c_tr2, c_tr3 = st.columns(3)
    with c_tr1:
        if st.button("🗣 TRADUZIR O TEXTO"):
            if not api_key: st.warning("IA Offline")
            else:
                with st.spinner("Traduzindo..."):
                    res = ai_brain(f"Traduza: {txt_area}", api_key, "Tradutor")
                    txt_area = res # Substitui na visualização
                    st.rerun()
                    
    with c_tr2:
        if st.button("👨‍🏫 PROFESSOR AVALIA"):
            if not api_key: st.warning("IA Offline")
            else:
                with st.spinner("Avaliando Homilética..."):
                    feedback = ai_brain(txt_area, api_key, "Professor")
                    st.info(feedback)
                    
    with c_tr3:
        if st.button("✨ REVISÃO ORTOGRÁFICA"):
            if not api_key: st.warning("IA Offline")
            else:
                res = ai_brain(f"Corrija este texto: {txt_area}", api_key, "Tradutor") # Tradutor tb serve como revisor de língua
                st.code(res, language="text")

    # Salvamento Automático do que está na tela (se tiver título)
    if novo_titulo and txt_area != texto:
        with open(os.path.join(PASTA, f"{novo_titulo}.txt"), "w") as f: f.write(txt_area)

# ==================== FERRAMENTAS LATERAIS (SIDE TOOLS) ====================
with c_tools:
    st.markdown("### 📡 SATÉLITE")
    
    tabs = st.tabs(["🤖 IA MODOS", "📖 BÍBLIA", "👨‍💻 CÓDIGO"])
    
    # ABA 1: MODOS DE PENSAMENTO (Razão x Emoção)
    with tabs[0]:
        st.info("Pergunte ao Assistente:")
        pergunta = st.text_area("Dúvida teológica ou pastoral:", height=100)
        
        cc1, cc2 = st.columns(2)
        if cc1.button("🧠 RAZÃO"):
            if api_key:
                with st.spinner("Analisando logica..."):
                    st.write(ai_brain(pergunta, api_key, "Razão"))
            else: st.error("Sem Chave")
            
        if cc2.button("❤️ EMOÇÃO"):
            if api_key:
                with st.spinner("Buscando consolo..."):
                    st.write(ai_brain(pergunta, api_key, "Sentimento"))
            else: st.error("Sem Chave")

    # ABA 2: BÍBLIA
    with tabs[1]:
        ref_b = st.text_input("Versículo (Ex: Mateus 6 33)")
        if ref_b:
            dado_b = get_bible(ref_b.replace(" ",""))
            if dado_b:
                t_b = dado_b['text']
                st.markdown(f"> **{dado_b['reference']}**\n\n{t_b}")
                if st.button("⬇ Copiar para Texto"):
                    # Aqui apenas mostramos, o user copia. (Automação total precisa de refresh)
                    st.code(f"{dado_b['reference']} - {t_b}")
            else: st.warning("Ref não encontrada.")

    # ABA 3: FÁBRICA DE CÓDIGO (Open Source)
    with tabs[2]:
        st.warning("⚠️ Gerador de Código")
        pedido_dev = st.text_input("O que criar? (Ex: Botão para doar)")
        if st.button("GERAR"):
            if api_key:
                res_dev = ai_brain(pedido_dev, api_key, "Coder")
                st.code(res_dev, language='python')
            else: st.error("Sem Chave")

# --- 8. RODAPÉ INSTAGRAM (Social Footprint) ---
st.markdown("""
<div class="footer-insta">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="18" style="vertical-align:middle">
    SIGA O DESENVOLVEDOR: <a href="https://instagram.com/felipefreitashope" target="_blank">@FELIPEFREITASHOPE</a>
</div>
""", unsafe_allow_html=True)
