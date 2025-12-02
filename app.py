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
    
    /* Inputs de Texto mais bonitos */
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
    
    /* Cards Exegese */
    .info-card {{
        background-color: #25262B;
        padding: 15px;
        border-left: 3px solid {COR_DESTAQUE};
        border-radius: 6px;
        margin-bottom: 10px;
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
    """Carrega animação com segurança. Se falhar, retorna None."""
    try:
        r = requests.get(url, timeout=1.5) # Timeout rápido para não travar
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def consultar_cerebro(prompt, chave, modo="teologo"):
    """Motor de Inteligência Teológica"""
    if not chave: return "⚠️ Conecte a 'Chave Mestra' (API) no menu."
    try:
        genai.configure(api_key=chave)
        # Personas da IA
        instrucao = "Você é um assistente teológico acadêmico erudito. Responda com profundidade bíblica e histórica."
        if modo == "ilustrador":
            instrucao = "Você é um contador de histórias criativo para sermões. Crie narrativas envolventes."
            
        model = genai.GenerativeModel('gemini-pro')
        full_prompt = f"{instrucao}\n\nTarefa: {prompt}"
        
        with st.spinner("Pesquisando na biblioteca..."):
            return model.generate_content(full_prompt).text
    except Exception as e: return f"Erro ao consultar: {e}"

# --- 4. LOGIN (CORRIGIDO PARA NÃO TRAVAR ANIMAÇÃO) ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.write("\n\n")
        # Animação protegida
        anim_login = load_lottie_safe(LOTTIE_URLS["book"])
        if anim_login:
            st_lottie(anim_login, height=120)
        else:
            st.header("✝️")
            
        st.markdown("<h3 style='text-align: center; color:#CCC'>O Pregador <span style='color:#d4af37'>STUDIO</span></h3>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            btn = st.form_submit_button("Acessar Púlpito", type="primary", use_container_width=True)
            
            if btn:
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
    st.stop()

# --- 5. SISTEMA PRINCIPAL ---
USER = st.session_state['user']
PASTA_USER = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA_USER, exist_ok=True)

# === SIDEBAR (Com Animação Protegida) ===
with st.sidebar:
    # AQUI ESTAVA O ERRO, AGORA PROTEGIDO:
    anim_sidebar = load_lottie_safe(LOTTIE_URLS["book"])
    if anim_sidebar:
        st_lottie(anim_sidebar, height=60, key="side_logo")
    else:
        st.subheader("✝️ Studio")

    st.markdown(f"Olá, **{USER.capitalize()}**")
    
    menu = st.radio("Menu", ["🏠 Início", "✍️ Studio (Editor)", "📚 Exegese Profunda", "🕶️ Modo Púlpito"])
    
    st.markdown("---")
    st.caption("FERRAMENTAS")
    
    # Botão Cronômetro
    if 'cron_on' not in st.session_state: st.session_state['cron_on'] = None
    if st.button("⏱️ Cronômetro"):
        st.session_state['cron_on'] = time.time() if not st.session_state['cron_on'] else None
        
    if st.session_state['cron_on']:
        tempo = int(time.time() - st.session_state['cron_on'])
        mm, ss = divmod(tempo, 60)
        st.metric("Tempo", f"{mm:02}:{ss:02}")

    with st.expander("🔑 Chave Mestra (Google)"):
        api_key = st.text_input("API Key", type="password")
    
    st.divider()
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

# VARIAVEIS GLOBAIS
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""
arquivos = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]

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
                prompt = "Aja como Charles Spurgeon. Escreva um pequeno devocional encorajador para um pastor."
                st.session_state['devocional'] = consultar_cerebro(prompt, api_key)
            st.info(st.session_state['devocional'])
        else:
            st.warning("Insira sua chave API no menu para ativar a inteligência devocional.")

        st.markdown("### 📂 Últimos Esboços")
        if arquivos:
            for a in arquivos[:3]:
                st.markdown(f"📄 **{a.replace('.txt','')}**")
        else:
            st.caption("Nenhum sermão criado ainda.")
            
    with c2:
        # Animação decorativa segura
        anim_study = load_lottie_safe(LOTTIE_URLS["study"])
        if anim_study: st_lottie(anim_study, height=200)

# > EDITOR STUDIO (TURBINADO)
elif menu == "✍️ Studio (Editor)":
    # Barra Superior
    c_sel, c_save = st.columns([3, 1])
    with c_sel:
        escolha = st.selectbox("Selecione:", ["+ Novo Esboço"] + arquivos, label_visibility="collapsed")
        
        # Carregamento Inteligente
        if 'last_open' not in st.session_state: st.session_state['last_open'] = ""
        if escolha != st.session_state['last_open']:
            st.session_state['last_open'] = escolha
            if escolha != "+ Novo Esboço":
                st.session_state['titulo_ativo'] = escolha.replace(".txt", "")
                try:
                    with open(os.path.join(PASTA_USER, escolha), 'r', encoding='utf-8') as f:
                        st.session_state['texto_ativo'] = f.read()
                except: pass
            else:
                st.session_state['titulo_ativo'] = ""
                st.session_state['texto_ativo'] = ""

    with c_save:
        if st.button("💾 Guardar", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                path = os.path.join(PASTA_USER, f"{st.session_state['titulo_ativo']}.txt")
                with open(path, 'w', encoding='utf-8') as f: f.write(st.session_state['texto_ativo'])
                st.toast("Esboço salvo com sucesso!", icon="✅")

    # Área de Trabalho
    col_e, col_f = st.columns([2.2, 1])
    
    with col_e:
        st.text_input("Tema da Mensagem", key="titulo_ativo", placeholder="Ex: A Graça Superabundante")
        
        # Botões Rápidos (Callbacks)
        def inserir(t): st.session_state['texto_ativo'] += t
        b1, b2, b3, b4 = st.columns(4)
        b1.button("📌 Intro", on_click=inserir, args=("\n\n# INTRODUÇÃO\n",), use_container_width=True)
        b2.button("I. Ponto", on_click=inserir, args=("\n\n## I. TÓPICO\n",), use_container_width=True)
        b3.button("⚔️ Aplicar", on_click=inserir, args=("\n> APLICAÇÃO:\n",), use_container_width=True)
        b4.button("🏁 Fim", on_click=inserir, args=("\n\n# CONCLUSÃO\n",), use_container_width=True)
        
        st.text_area("Canvas de Escrita", key="texto_ativo", height=600, label_visibility="collapsed")

    with col_f:
        st.markdown("### 🧩 Assistente")
        t1, t2 = st.tabs(["🎨 Ilustrar", "🔍 Referências"])
        
        with t1:
            st.caption("Crie ilustrações como Max Lucado")
            tema = st.text_input("Tema:", placeholder="Ex: Perdão")
            estilo = st.selectbox("Estilo:", ["História Emocionante", "Fato Científico", "Analogia", "Biografia"])
            if st.button("Gerar História"):
                resp = consultar_cerebro(f"Crie uma ilustração de sermão estilo '{estilo}' sobre '{tema}'.", api_key, "ilustrador")
                st.info(resp)
        
        with t2:
            st.caption("Cruzamento Bíblico")
            v = st.text_input("Versículo:", placeholder="Rm 8:28")
            if st.button("Buscar Conexões"):
                prompt = f"Aja como Bíblia Thompson. Liste 3 versículos conectados a {v} e explique o elo teológico."
                st.markdown(consultar_cerebro(prompt, api_key))

# > EXEGESE PROFUNDA (LOGOS STYLE)
elif menu == "📚 Exegese Profunda":
    st.title("🔬 Laboratório Exegético")
    
    c_in, c_out = st.columns([1, 2])
    with c_in:
        ref = st.text_input("Texto para Análise:", placeholder="Ex: João 1:1")
        nivel = st.radio("Nível:", ["Básico (Explicação)", "Avançado (Grego/Hebraico)", "Hermenêutico (História)"])
        btn_analise = st.button("Analisar Texto", type="primary")
        
        st.caption("Esta ferramenta simula softwares teológicos usando IA para dissecar o original.")
    
    with c_out:
        if btn_analise and ref:
            st.markdown(f"### Raio-X de: {ref}")
            
            prompt_exe = ""
            if "Avançado" in nivel:
                prompt_exe = f"""
                Analise {ref} como um erudito em línguas originais.
                1. Traga o texto original (Grego/Hebraico).
                2. Transliteração.
                3. **Word Study:** Escolha 2 palavras chaves, dê o Strong e significado profundo.
                4. Analise os tempos verbais e sua implicação.
                """
            elif "Hermenêutico" in nivel:
                prompt_exe = f"Faça uma análise histórico-cultural de {ref}. Quem escreveu? Qual o cenário político? Aplicação hoje."
            else:
                prompt_exe = f"Explique {ref} versículo a versículo de forma didática."
            
            resultado = consultar_cerebro(prompt_exe, api_key)
            st.markdown(f"<div class='info-card'>{resultado}</div>", unsafe_allow_html=True)

# > MODO PÚLPITO
elif menu == "🕶️ Modo Púlpito":
    if not st.session_state['texto_ativo']:
        st.warning("Abra um sermão no Studio primeiro.")
    else:
        f_size = st.slider("Tamanho da Fonte", 20, 60, 28)
        # Transforma quebras de linha em <br> para HTML
        html_text = st.session_state['texto_ativo'].replace("\n", "<br>")
        st.markdown(f"""
        <div style="
            background-color: black; color: white; padding: 40px; border-radius: 10px;
            font-size: {f_size}px; line-height: 1.6; font-family: Arial, sans-serif;">
            <h1 style='color: #d4af37; border-bottom: 2px solid #333'>{st.session_state['titulo_ativo']}</h1>
            {html_text}
        </div>
        """, unsafe_allow_html=True)
        # --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="O Pregador",  # Renomeado
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# ... (código anterior)

# === SIDEBAR ===
with st.sidebar:
    anim_sidebar = load_lottie_safe(LOTTIE_URLS["book"])
    if anim_sidebar:
        st_lottie(anim_sidebar, height=60, key="side_logo")
    else:
        st.subheader("✝️ O Pregador")  # Renomeado

    st.markdown(f"Olá, **{USER.capitalize()}**")
    
    menu = st.radio("Menu", ["🏠 Início", "🕶️ Modo Púlpito"])  # Removido "Studio"

    st.markdown("---")
    st.caption("FERRAMENTAS")
    
    # (Código das ferramentas como Cronômetro)

# VARIAVEIS GLOBAIS
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""

# === PÁGINAS ===

# > INÍCIO
if menu == "🏠 Início":
    st.title("Central Pastoral")
    st.markdown(f"*{datetime.now().strftime('%d de %B, %Y')}*")
    # (Seu código existente do Início aqui)

# > MODO PÚLPITO
elif menu == "🕶️ Modo Púlpito":
    if not st.session_state['texto_ativo']:
        st.warning("Abra um sermão no Studio primeiro.")
    else:
        f_size = st.slider("Tamanho da Fonte", 20, 60, 28)
        html_text = st.session_state['texto_ativo'].replace("\n", "<br>")
        st.markdown(f"""
        <div style="
            background-color: black; color: white; padding: 40px; border-radius: 10px;
            font-size: {f_size}px; line-height: 1.6; font-family: Arial, sans-serif;">
            <h1 style='color: #d4af37; border-bottom: 2px solid #333'>{st.session_state['titulo_ativo']}</h1>
            {html_text}
        </div>
        """, unsafe_allow_html=True)

        # Botão para entrar em modo apresentação
        if st.button("Entrar em Modo Apresentação"):
            st.session_state['modo_apresentacao'] = True
            st.experimental_rerun()

        if st.session_state.get('modo_apresentacao'):
            st.markdown(f"""
            <div style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background-color: black; color: white; display: flex;
                align-items: center; justify-content: center; flex-direction: column;
                font-size: {f_size}px; line-height: 1.6; font-family: Arial, sans-serif;">
                <h1 style='color: #d4af37; margin: 0;'>{st.session_state['titulo_ativo']}</h1>
                <div style='margin-top: 20px; white-space: pre-wrap;'>{html_text}</div>
                <button onclick="window.close()">Fechar Apresentação</button>
            </div>
            """, unsafe_allow_html=True)

# ... (código posterior)

