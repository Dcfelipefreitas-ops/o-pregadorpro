import streamlit as st
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from io import BytesIO

# --- 0. AUTO-INSTALAÇÃO DE DEPENDÊNCIAS ---
def install_packages():
    required = ["google-generativeai", "duckduckgo-search", "streamlit-lottie", "fpdf", "Pillow"]
    for package in required:
        try:
            __import__(package.replace("-", "_").replace("google_generativeai", "google.generativeai").replace("Pillow", "PIL"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            st.rerun()

install_packages()

import google.generativeai as genai
from duckduckgo_search import DDGS
from streamlit_lottie import st_lottie
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- 1. CONFIGURAÇÃO INICIAL E ESTADO ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# DIRETÓRIOS E DADOS
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
PASTA_AUDIO = os.path.join(PASTA_RAIZ, "Audios")
os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)
os.makedirs(PASTA_AUDIO, exist_ok=True)

# INICIALIZAÇÃO DO ESTADO DE SESSÃO
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Home"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "avatar_bytes": None,
    "current_nav_title": "Visão Geral", "humor": "Bem"
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 2. SISTEMA DE NAVEGAÇÃO "APPLE-LIKE" ---
def navigate_to(page_name, title=None):
    st.session_state['page_stack'].append(page_name)
    st.session_state['current_nav_title'] = title if title else page_name
    st.rerun()

def navigate_back():
    if len(st.session_state['page_stack']) > 1:
        st.session_state['page_stack'].pop()
        st.rerun()

def current_page():
    return st.session_state['page_stack'][-1]

# --- 3. UI KIT (CSS ESTILO IOS/MACOS) ---
def carregar_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    :root { --bg: #000000; --card: #1c1c1e; --acc: #0A84FF; --txt: #F2F2F7; }
    
    .stApp { background-color: var(--bg); font-family: 'Inter', sans-serif; color: var(--txt); }
    header, footer {visibility: hidden;}

    /* CABEÇALHO FIXO FLUTUANTE */
    .nav-header {
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: rgba(28,28,30, 0.85); backdrop-filter: blur(20px);
        border-bottom: 1px solid #333; z-index: 9999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 80px 0 20px;
    }
    .nav-title { font-size: 17px; font-weight: 600; color: white; position: absolute; left: 50%; transform: translateX(-50%); }
    .nav-back { cursor: pointer; color: var(--acc); font-size: 16px; display: flex; align-items: center; gap: 5px;}
    
    .block-container { padding-top: 80px !important; }
    
    /* INPUTS & CARDS */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #2C2C2E !important; border: none !important; border-radius: 10px; color: white !important;
    }
    
    .ios-card {
        background: var(--card); border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); margin-bottom: 15px;
    }
    
    div.stButton > button {
        background: #3A3A3C; color: white; border-radius: 8px; border: none; font-weight: 500;
        transition: 0.2s;
    }
    div.stButton > button:hover { background: var(--acc); }
    
    /* Perfil Imagem Arredondada */
    .profile-pic { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--acc); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

carregar_css()

# --- 4. FUNÇÕES DE SUPORTE (BACKEND SIMULADO) ---

# IA GERAL
def consultar_ia(prompt, role="teologo"):
    if not st.session_state['api_key']: return "⚠️ Configuração Necessária: Adicione a API Key."
    try:
        genai.configure(api_key=st.session_state['api_key'])
        sys = "Você é um assistente pastoral." 
        if role == "biblioteca": sys = "Você é uma biblioteca teológica completa (Bíblia, Comentários, Dicionários)."
        if role == "care": sys = "Você é um assistente de cuidado pastoral e gestão eclesiástica."
        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys}\n{prompt}").text
    except Exception as e: return f"Erro: {e}"

# PERSISTÊNCIA SIMPLES
def salvar_membro(dados):
    file = os.path.join(PASTA_CARE, "membros.json")
    lista = []
    if os.path.exists(file):
        with open(file, 'r') as f: lista = json.load(f)
    lista.append(dados)
    with open(file, 'w') as f: json.dump(lista, f)

def ler_membros():
    file = os.path.join(PASTA_CARE, "membros.json")
    if os.path.exists(file):
        with open(file, 'r') as f: return json.load(f)
    return []

# BUSCA AVANÇADA
def busca_global(termo):
    resultados = []
    # Busca sermões
    for f in os.listdir(PASTA_SERMOES):
        if f.endswith(".txt"):
            path = os.path.join(PASTA_SERMOES, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                if termo.lower() in content.lower():
                    resultados.append({"tipo": "Sermão", "titulo": f, "path": path})
    # Busca Membros
    membros = ler_membros()
    for m in membros:
        if termo.lower() in str(m).lower():
            resultados.append({"tipo": "Membro", "titulo": m['nome'], "path": "Membro"})
    return resultados

# COMPONENTE DE CABEÇALHO PERSONALIZADO
def render_header():
    prev = "Início"
    if len(st.session_state['page_stack']) > 2:
        prev = st.session_state['page_stack'][-2]
    elif len(st.session_state['page_stack']) == 1:
        prev = ""

    back_html = f'<div class="nav-back" onclick="window.parent.postMessage({{type: \'streamlit:setComponentValue\', value: true}}, \'*\')">‹ {prev}</div>' if prev else "<div></div>"
    if prev == "": back_html = f"<div style='color:gray'>🏠 Início</div>"

    st.markdown(f"""
        <div class="nav-header">
            {back_html}
            <div class="nav-title">{st.session_state['current_nav_title']}</div>
            <div style="font-size: 20px;">✝️</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Botão de voltar funcional (Hack Streamlit)
    if prev and len(st.session_state['page_stack']) > 1:
        if st.sidebar.button(f"🔙 Voltar para {prev}"):
            navigate_back()


# --- 5. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.title("O PREGADOR")
        st.markdown("**Ecosystem 5.0**")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                st.session_state['logado'] = True
                st.session_state['user'] = user
                st.rerun()
            else:
                st.error("Dados incorretos.")
    st.stop()


# --- 6. ESTRUTURA PRINCIPAL ---

# MENU LATERAL (SIDEBAR)
with st.sidebar:
    # 1. Foto do Usuário
    st.markdown("### Perfil")
    if st.session_state['avatar_bytes']:
        st.image(st.session_state['avatar_bytes'], width=100)
    else:
        st.markdown("<div style='width:80px; height:80px; background:#333; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:30px;'>👤</div>", unsafe_allow_html=True)
    
    new_pic = st.file_uploader("Alterar Foto", type=["jpg", "png"], label_visibility="collapsed")
    if new_pic:
        st.session_state['avatar_bytes'] = new_pic.getvalue()
        st.rerun()

    st.write(f"**Pr. {st.session_state['user'].capitalize()}**")
    
    # 2. Navegação Global
    st.divider()
    if st.button("🏠 Central", use_container_width=True): navigate_to("Home", "Visão Geral")
    if st.button("📖 Estudo & Bíblia", use_container_width=True): navigate_to("Bible", "Centro de Estudos")
    if st.button("✍️ Sermões", use_container_width=True): navigate_to("Studio", "Editor de Mensagem")
    if st.button("👥 Cuidado Pastoral", use_container_width=True): navigate_to("Care", "Membros & Visitas")
    if st.button("📅 Agenda", use_container_width=True): navigate_to("Agenda", "Calendário")
    if st.button("⚙️ Ajustes", use_container_width=True): navigate_to("Config", "Configurações")
    
    st.divider()
    st.session_state['humor'] = st.selectbox("Status Emocional", ["Bem", "Cansado", "Ansioso", "Grato"])


# CABEÇALHO COM NAVIGATION TITLE AUTOMÁTICO
render_header()

# ROTEAMENTO DE PÁGINAS (NAVSTACK)
pagina = current_page()


# --- PÁGINA: HOME ---
if pagina == "Home":
    st.markdown(f"## Olá, Pr. {st.session_state['user'].capitalize()}")
    
    # Busca Rápida Global
    busca = st.text_input("🔍 Buscar em todo o sistema...", placeholder="Digite um versículo, nome de membro ou tema de sermão")
    if busca:
        res = busca_global(busca)
        st.markdown("### Resultados")
        for r in res:
            with st.container():
                st.markdown(f"**{r['tipo']}**: {r['titulo']}")
                
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="ios-card"><h4>🔥 Palavra do Dia</h4><p>Confie no Senhor de todo o seu coração (Pv 3:5).</p></div>', unsafe_allow_html=True)
    with c2:
         st.markdown(f'<div class="ios-card"><h4>📊 Estatísticas</h4><p>{len(os.listdir(PASTA_SERMOES))} Sermões | {len(ler_membros())} Membros</p></div>', unsafe_allow_html=True)

    # Ações Rápidas
    st.markdown("### Atalhos")
    c3, c4, c5 = st.columns(3)
    if c3.button("🎙️ Gravar Ideia", use_container_width=True): navigate_to("Record", "Gravador")
    if c4.button("✍️ Novo Esboço", use_container_width=True): navigate_to("Studio", "Novo Sermão")
    if c5.button("👥 Novo Visitante", use_container_width=True): navigate_to("Care", "Cadastro")


# --- PÁGINA: ESTUDO & BÍBLIA (HUB) ---
elif pagina == "Bible":
    st.markdown("### Biblioteca Teológica")
    
    tab1, tab2 = st.tabs(["Comparar Versões", "Comentário IA"])
    
    with tab1:
        ref = st.text_input("Versículo (ex: Jo 3:16)")
        versoes = st.multiselect("Versões", ["NVI", "Almeida", "KJA", "Grego", "Hebraico"], default=["NVI", "Almeida"])
        if st.button("Comparar") and ref:
            prompt = f"Mostre o texto de {ref} nas seguintes versões: {', '.join(versoes)}. Destaque diferenças importantes."
            st.info(consultar_ia(prompt, "biblioteca"))
            
    with tab2:
        tema = st.text_input("Tópico Teológico ou Passagem")
        if st.button("Pesquisar na Biblioteca") and tema:
            st.markdown(consultar_ia(f"Faça uma análise profunda e teológica sobre: {tema}. Cite autores clássicos se possível.", "biblioteca"))

# --- PÁGINA: STUDIO (SERMÕES) ---
elif pagina == "Studio":
    # Lista lateral de arquivos ou editor full
    c_list, c_edit = st.columns([1, 3])
    
    with c_list:
        st.markdown("##### Arquivos")
        arquivos = [f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")]
        sel_file = st.radio("Sermão:", ["+ Novo"] + arquivos)
        
        # Load logic
        if 'last_studio' not in st.session_state: st.session_state['last_studio'] = ""
        if sel_file != st.session_state['last_studio']:
            st.session_state['last_studio'] = sel_file
            if sel_file != "+ Novo":
                with open(os.path.join(PASTA_SERMOES, sel_file), 'r') as f:
                    st.session_state['texto_ativo'] = f.read()
                st.session_state['titulo_ativo'] = sel_file.replace(".txt", "")
            else:
                st.session_state['titulo_ativo'] = ""
                st.session_state['texto_ativo'] = ""

    with c_edit:
        st.markdown("#### Editor")
        titulo = st.text_input("Título", value=st.session_state['titulo_ativo'], placeholder="Título da Mensagem...")
        
        # Ferramentas
        toll_c1, toll_c2, toll_c3, toll_c4 = st.columns(4)
        def add(x): st.session_state['texto_ativo'] += x
        toll_c1.button("H1", on_click=add, args=("\n# ",))
        toll_c2.button("**B**", on_click=add, args=(" **text** ",))
        toll_c3.button("Ref.", on_click=add, args=("\n> ",))
        toll_c4.button("Limpar", on_click=add, args=("",))
        
        texto = st.text_area("Corpo do texto", value=st.session_state['texto_ativo'], height=500)
        st.session_state['texto_ativo'] = texto
        
        c_save, c_share, c_pres = st.columns(3)
        if c_save.button("💾 Salvar", type="primary", use_container_width=True):
            if titulo:
                with open(os.path.join(PASTA_SERMOES, f"{titulo}.txt"), 'w') as f: f.write(texto)
                st.toast("Salvo na nuvem!")
        
        # Social Share Simulation
        if c_share.button("📤 Compartilhar"):
            st.info(f"Link gerado para equipe: opregador.app/s/{titulo.replace(' ', '_').lower()}")
            
        if c_pres.button("🖥️ Projetar"):
            navigate_to("ModeView", f"Apresentando: {titulo}")


# --- PÁGINA: MODO APRESENTAÇÃO ---
elif pagina == "ModeView":
    if not st.session_state['texto_ativo']:
        st.warning("Nada para apresentar.")
    else:
        # Modo Púlpito Limpo
        f_size = st.slider("Tamanho Fonte", 20, 80, 40)
        texto_html = st.session_state['texto_ativo'].replace("\n", "<br>")
        st.markdown(f"""
        <div style="background:black; color:white; padding:40px; border-radius:15px; font-size:{f_size}px; line-height:1.6; min-height:80vh;">
            {texto_html}
        </div>
        """, unsafe_allow_html=True)


# --- PÁGINA: CUIDADO PASTORAL (NOTEBIRD STYLE) ---
elif pagina == "Care":
    st.markdown("### Membros e Visitas")
    
    with st.expander("➕ Adicionar Novo Membro / Visitante", expanded=False):
        with st.form("care_form"):
            c_nome = st.text_input("Nome")
            c_status = st.selectbox("Status", ["Membro", "Visitante", "Necessita Visita", "Em Luto"])
            c_nota = st.text_area("Notas / Pedidos de Oração")
            c_data = str(datetime.now().date())
            if st.form_submit_button("Salvar Ficha"):
                salvar_membro({"nome": c_nome, "status": c_status, "nota": c_nota, "data": c_data})
                st.success("Registrado.")

    # Listagem estilo Tabela/Cards
    membros = ler_membros()
    if membros:
        st.dataframe(membros, use_container_width=True)
    else:
        st.info("Nenhum registro.")


# --- PÁGINA: GRAVADOR (IDEIAS) ---
elif pagina == "Record":
    st.markdown("### 🎙️ Notas de Áudio")
    st.caption("Grave ideias rápidas para sermões.")
    
    # Feature nova do Streamlit 1.39+
    audio_val = st.audio_input("Gravar")
    if audio_val:
        st.audio(audio_val)
        with open(os.path.join(PASTA_AUDIO, f"nota_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"), "wb") as f:
            f.write(audio_val.getbuffer())
        st.success("Nota salva.")
        
    st.divider()
    st.markdown("**Biblioteca de Áudios**")
    for aud in os.listdir(PASTA_AUDIO):
        st.write(aud)
        st.audio(os.path.join(PASTA_AUDIO, aud))


# --- PÁGINA: AGENDA ---
elif pagina == "Agenda":
    st.markdown("### Calendário Pastoral")
    col_cal1, col_cal2 = st.columns([2,1])
    with col_cal1:
        # Simulando uma view de agenda
        data = st.date_input("Data", datetime.now())
        evento = st.text_input("Novo Compromisso")
        if st.button("Adicionar à Agenda"):
            st.toast(f"Agendado: {evento} para {data}")
    
    with col_cal2:
        st.markdown("**Próximos Eventos:**")
        st.info("Domingo: Culto Ceia (19h)")
        st.info("Quarta: Estudo Bíblico (20h)")


# --- PÁGINA: CONFIGURAÇÕES ---
elif pagina == "Config":
    st.markdown("### Ajustes do Ecossistema")
    
    st.text_input("Sua Igreja", "Igreja Local")
    k = st.text_input("API Key (Google Gemini)", value=st.session_state['api_key'], type="password")
    if k: st.session_state['api_key'] = k
    
    if st.checkbox("Habilitar Modo Offline"):
        st.caption("O conteúdo será baixado para o cache local.")
        
    st.divider()
    if st.button("Logout", type="primary"):
        st.session_state['logado'] = False
        st.rerun()

# --- VALIDACAO DE ERROS ---
if not st.session_state['api_key'] and pagina in ["Bible"]:
    st.warning("⚠️ Algumas funções precisam da API Key configurada.")
