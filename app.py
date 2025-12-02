import streamlit as st
import os
import sys
import subprocess
import time
from datetime import datetime
from duckduckgo_search import DDGS
import requests
from streamlit_lottie import st_lottie
from fpdf import FPDF

# --- 1. INSTALAÇÃO BLINDADA ---
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
    st.rerun()

# --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# Estilos Premium (Dark Theology Theme)
COR_DESTAQUE = "#d4af37" # Ouro Velho
COR_FUNDO = "#1E1E1E" 
COR_SIDEBAR = "#121212"

st.markdown(f"""
    <style>
    /* Remove elementos visuais desnecessários */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COR_SIDEBAR};
        border-right: 1px solid #333;
    }}
    
    /* Inputs de Texto */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: #2b2b2b !important;
        border-color: #444 !important;
        color: white !important;
    }}
    
    /* Área de Texto (Papiro Digital) */
    .stTextArea textarea {{
        background-color: {COR_FUNDO};
        color: #E0E0E0;
        font-family: 'Merriweather', serif; 
        font-size: 20px !important;
        line-height: 1.7;
        padding: 30px;
        border: 1px solid #333;
        border-radius: 8px;
    }}
    
    /* Slide de Apresentação */
    .slide-card {{
        background-color: black;
        color: white;
        padding: 60px;
        border-radius: 15px;
        border: 2px solid {COR_DESTAQUE};
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS E HELPERS SEGUROS ---
LOTTIE_URLS = {
    "book": "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json",
    "study": "https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json",
}

USUARIOS = {"admin": "1234", "pr": "123"}

def load_lottie_safe(url):
    try:
        r = requests.get(url, timeout=1.5)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def consultar_cerebro(prompt, chave, modo="teologo"):
    if not chave: return "⚠️ Conecte a 'Chave Mestra' (API) no menu."
    try:
        genai.configure(api_key=chave)
        instrucao = "Você é um assistente teológico acadêmico erudito."
        if modo == "ilustrador":
            instrucao = "Você é um contador de histórias criativo para sermões."
            
        model = genai.GenerativeModel('gemini-pro')
        full_prompt = f"{instrucao}\n\nTarefa: {prompt}"
        
        with st.spinner("Pesquisando na biblioteca..."):
            return model.generate_content(full_prompt).text
    except Exception as e: return f"Erro: {e}"

# --- 4. LOGIN (ATUALIZADO PARA "O PREGADOR") ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.write("\n\n")
        anim_login = load_lottie_safe(LOTTIE_URLS["book"])
        if anim_login:
            st_lottie(anim_login, height=120)
        else:
            st.header("✝️")
            
        # NOME ATUALIZADO (SEM "STUDIO")
        st.markdown("<h2 style='text-align: center; color: #d4af37;'>O PREGADOR</h2>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            btn = st.form_submit_button("Acessar", type="primary", use_container_width=True)
            
            if btn:
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Acesso negado.")
    st.stop()

# --- 5. SISTEMA PRINCIPAL ---
USER = st.session_state['user']
PASTA_USER = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA_USER, exist_ok=True)

# VARIAVEIS GLOBAIS DE ESTADO
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""
# Variável para o Slide
if 'slide_atual' not in st.session_state: st.session_state['slide_atual'] = 0

arquivos = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]

# === SIDEBAR ===
with st.sidebar:
    anim_sidebar = load_lottie_safe(LOTTIE_URLS["book"])
    if anim_sidebar:
        st_lottie(anim_sidebar, height=60, key="side_logo")
    else:
        st.subheader("✝️")

    st.markdown(f"Olá, **{USER.capitalize()}**")
    
    # Navegação Simplificada
    menu = st.radio("Menu", ["🏠 Início", "✍️ Studio (Editor)", "📚 Exegese", "🕶️ Apresentação (PPT)"])
    
    st.markdown("---")
    
    # Botão Cronômetro
    if 'cron_on' not in st.session_state: st.session_state['cron_on'] = None
    if st.button("⏱️ Cronômetro"):
        st.session_state['cron_on'] = time.time() if not st.session_state['cron_on'] else None
        
    if st.session_state['cron_on']:
        tempo = int(time.time() - st.session_state['cron_on'])
        mm, ss = divmod(tempo, 60)
        st.metric("Tempo", f"{mm:02}:{ss:02}")

    with st.expander("🔑 Chave Grátis (Gemini)"):
        api_key = st.text_input("Cole sua chave aqui", type="password")
        st.caption("A chave é grátis. Obtenha em: [Google AI Studio](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

# === PÁGINAS ===

# > INÍCIO
if menu == "🏠 Início":
    st.title("Central Pastoral")
    st.markdown(f"*{datetime.now().strftime('%d de %B, %Y')}*")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("🕊️ Palavra do Dia")
        if api_key:
            if 'devocional' not in st.session_state:
                prompt = "Aja como um devocional breve. Traga um versículo encorajador."
                st.session_state['devocional'] = consultar_cerebro(prompt, api_key)
            st.info(st.session_state['devocional'])
        else:
            st.warning("AIzaSyBFQuslVRjAHjhLAaolm4xf2P0c__WKiCw")
            
    with c2:
        anim_study = load_lottie_safe(LOTTIE_URLS["study"])
        if anim_study: st_lottie(anim_study, height=180)

# > EDITOR STUDIO
elif menu == "✍️ Studio (Editor)":
    # Seleção
    escolha = st.selectbox("Arquivo:", ["+ Novo"] + arquivos)
    
    # Carregamento
    if 'last_open' not in st.session_state: st.session_state['last_open'] = ""
    if escolha != st.session_state['last_open']:
        st.session_state['last_open'] = escolha
        if escolha != "+ Novo":
            st.session_state['titulo_ativo'] = escolha.replace(".txt", "")
            try:
                with open(os.path.join(PASTA_USER, escolha), 'r', encoding='utf-8') as f:
                    st.session_state['texto_ativo'] = f.read()
            except: pass
        else:
            st.session_state['titulo_ativo'] = ""
            st.session_state['texto_ativo'] = ""

    # Botão Salvar
    if st.button("💾 Salvar", type="primary"):
        if st.session_state['titulo_ativo']:
            path = os.path.join(PASTA_USER, f"{st.session_state['titulo_ativo']}.txt")
            with open(path, 'w', encoding='utf-8') as f: f.write(st.session_state['texto_ativo'])
            st.toast("Salvo!", icon="✅")

    # Editor
    st.text_input("Título", key="titulo_ativo")
    
    # Callbacks
    def inserir(t): st.session_state['texto_ativo'] += t
    
    b1, b2, b3 = st.columns(3)
    b1.button("📌 Intro", on_click=inserir, args=("\n# INTRODUÇÃO\n\n",))
    b2.button("I. Tópico", on_click=inserir, args=("\n## I. TÓPICO\n\n",))
    b3.button("🏁 Fim", on_click=inserir, args=("\n# CONCLUSÃO\n\n",))
    
    st.text_area("Texto", key="texto_ativo", height=500)

# > EXEGESE
elif menu == "📚 Exegese":
    st.title("Laboratório")
    ref = st.text_input("Versículo:")
    if st.button("Analisar") and ref:
        resp = consultar_cerebro(f"Exegese profunda de {ref}", api_key)
        st.write(resp)

# > MODO APRESENTAÇÃO (POWER POINT STYLE)
elif menu == "🕶️ Apresentação (PPT)":
    if not st.session_state['texto_ativo']:
        st.warning("Escreva seu sermão no Studio primeiro.")
    else:
        st.caption("Modo Apresentação Interativa - Use os botões abaixo para navegar.")
        
        # 1. DIVIDIR O TEXTO EM SLIDES
        # Divide sempre que houver duas quebras de linha (\n\n) ou marcação de Título (#)
        raw_text = st.session_state['texto_ativo']
        # Lógica simples de separação: quebra por blocos de parágrafos
        slides = [s.strip() for s in raw_text.split('\n\n') if s.strip()]
        
        # Título como Slide 0
        titulo_slide = f"# {st.session_state['titulo_ativo']}"
        if titulo_slide not in slides:
            slides.insert(0, titulo_slide)

        total_slides = len(slides)
        
        # 2. CONTROLES DE NAVEGAÇÃO
        c_prev, c_info, c_next = st.columns([1, 4, 1])
        
        with c_prev:
            if st.button("⬅️ Anterior", use_container_width=True):
                if st.session_state['slide_atual'] > 0:
                    st.session_state['slide_atual'] -= 1
        
        with c_next:
            if st.button("Próximo ➡️", use_container_width=True):
                if st.session_state['slide_atual'] < total_slides - 1:
                    st.session_state['slide_atual'] += 1

        with c_info:
            percent = (st.session_state['slide_atual'] + 1) / total_slides
            st.progress(percent)
            st.caption(f"Slide {st.session_state['slide_atual'] + 1} de {total_slides}")

        # 3. EXIBIÇÃO DO SLIDE (ESTILO PPT)
        f_size = st.slider("🔍 Zoom", 20, 80, 40)
        conteudo_atual = slides[st.session_state['slide_atual']]
        
        # Converte Markdown para HTML (bold, italic) de forma simples para exibição
        html_content = conteudo_atual.replace("\n", "<br>")
        
        st.markdown(f"""
        <div class="slide-card" style="font-size: {f_size}px;">
            <div>
            {html_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
