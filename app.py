import streamlit as st
import json
import os
import requests
import PyPDF2
from gtts import gTTS
import tempfile
import io

# --- 1. CONFIGURAÇÃO MODERN (Glassmorphism) ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="⚡", initial_sidebar_state="expanded")

# --- 2. CSS FUTURISTA (LAN HOUSE / NEON / GLASS) ---
st.markdown("""
<style>
    /* FUNDO E GERAL */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0f172a 0%, #000000 90%);
        color: #fff;
    }
    
    /* REMOVER PADS */
    .block-container {padding-top: 1rem; max-width: 98%;}
    header, footer {visibility: hidden;}
    
    /* TEXT AREAS (EFEITO VIDRO) */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6; /* Azul Neon */
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
    }
    
    /* INPUTS */
    .stTextInput input {
        background: rgba(0,0,0,0.3) !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
        color: white !important;
    }
    
    /* BOTÕES MODERNOS */
    .stButton button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #333;
        color: #94a3b8;
        border-radius: 8px;
        transition: 0.3s;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 1px;
    }
    .stButton button:hover {
        background: #3b82f6;
        color: white;
        border-color: #3b82f6;
        box-shadow: 0 0 10px #3b82f6;
    }
    
    /* CARD DE BÍBLIA */
    .verse-card {
        background: rgba(255,255,255,0.03);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE GERENCIAMENTO (ESTADO) ---
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'titulo_sermao' not in st.session_state: st.session_state['titulo_sermao'] = ""
if 'audio_cache' not in st.session_state: st.session_state['audio_cache'] = None

# Importação Segura
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    HAS_LIBS = True
except: HAS_LIBS = False

# --- 4. FUNÇÕES PODEROSAS ---
def speak_text(text):
    """Gera áudio MP3 do texto (Google TTS)"""
    try:
        tts = gTTS(text=text, lang='pt')
        # Cria arquivo temporário em memória
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        return fp.name
    except: return None

def get_bible_online(ref):
    """Busca Bíblia Online"""
    try:
        livro, resto = ref.split(" ", 1)
        # Tenta formatar para API (Simples)
        url = f"https://bible-api.com/{livro}+{resto}?translation=almeida"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json()
    except: pass
    return None

def gemini_fixer(texto, key):
    """IA que corrige e melhora texto"""
    if not key: return texto
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Pede para agir como revisor editorial
        p = f"Corrija a gramática, melhore a coesão e dê um tom pastoral culto a este texto, mantendo o sentido original: \n\n{texto}"
        return model.generate_content(p).text
    except: return texto

# --- 5. LOGIN MODERNO ---
def login_screen():
    if 'logado' not in st.session_state:
        st.session_state.update({'logado': False, 'user': ''})
        
    if not st.session_state['logado']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align:center; font-weight:900; background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>⚡ PREGADOR AI</h1>", unsafe_allow_html=True)
            with st.form("log"):
                u = st.text_input("ID")
                p = st.text_input("SENHA", type="password")
                if st.form_submit_button("LOGIN DE ACESSO", type="primary"):
                    if (u=="admin" and p=="1234") or (u=="pastor" and p=="pregar"):
                        st.session_state.update({'logado': True, 'user': u})
                        st.rerun()
                    else: st.error("Acesso Negado")
        return False
    return True

if not login_screen(): st.stop()

# --- 6. APLICAÇÃO PRINCIPAL ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# SIDEBAR (Perfil)
with st.sidebar:
    st.title("⚡ CONFIG")
    st.caption(f"Operador: {USER}")
    
    # API KEY
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key: api_key = st.text_input("🔑 Chave AI (Google)", type="password")
    
    st.divider()
    
    # ARQUIVOS
    try: files = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
    except: files = []
    
    st.markdown("### 📂 PROJETOS")
    choice = st.radio("Arquivo:", ["+ NOVO"] + files, label_visibility="collapsed")
    
    st.markdown("### 🎤 DICTATION")
    st.info("Para digitar com a voz: No Windows, clique na caixa de texto e aperte `Win + H`. No Mac, aperte `Fn + Fn`.")
    
    st.divider()
    if st.button("DESCONECTAR"):
        st.session_state['logado'] = False
        st.rerun()

# LÓGICA DE CARREGAMENTO
if choice != "+ NOVO" and choice != st.session_state['titulo_sermao']:
    # Carrega arquivo se mudou a seleção
    try:
        with open(os.path.join(PASTA, f"{choice}.txt"), "r") as f:
            st.session_state['texto_esboco'] = f.read()
            st.session_state['titulo_sermao'] = choice
    except: pass
elif choice == "+ NOVO":
    # Se escolheu novo, não limpa tudo para não perder trabalho, só o título
    if st.session_state['titulo_sermao'] in files:
        st.session_state['titulo_sermao'] = ""
        st.session_state['texto_esboco'] = ""

# --- LAYOUT PRINCIPAL (3 Painéis) ---
col_biblia, col_editor, col_ferramenta = st.columns([1, 2, 0.8])

# 1. PAINEL ESQUERDO: BÍBLIA INSTANTÂNEA
with col_biblia:
    st.markdown("### 📖 BÍBLIA")
    ref_input = st.text_input("Buscar Ref:", placeholder="Joao 3 16")
    
    # Busca Texto
    json_biblia = None
    if ref_input:
        json_biblia = get_bible_online(ref_input)
    
    if json_biblia:
        texto_limpo = json_biblia['text'].strip()
        ref_limpa = json_biblia['reference']
        
        # Mostra o card
        st.markdown(f"""
        <div class="verse-card">
            <b>{ref_limpa}</b><br>
            <i>{texto_limpo}</i>
        </div>
        """, unsafe_allow_html=True)
        
        c_insert, c_audio = st.columns(2)
        
        # BOTÃO INSERIR
        with c_insert:
            if st.button("⬇ Inserir"):
                # Adiciona ao final do texto atual
                st.session_state['texto_esboco'] += f"\n\n**{ref_limpa}**\n{texto_limpo}"
                st.toast("Versículo adicionado ao esboço!")
                
        # BOTÃO ÁUDIO
        with c_audio:
            if st.button("🔊 Ouvir"):
                audio_file = speak_text(f"{ref_limpa}. {texto_limpo}")
                if audio_file:
                    st.audio(audio_file, format='audio/mp3')

# 2. PAINEL CENTRAL: EDITOR
with col_editor:
    c_tit_e, c_save_e = st.columns([3, 1])
    with c_tit_e:
        # Título gerenciado pelo estado
        novo_tit = st.text_input("PROJETO", value=st.session_state['titulo_sermao'], placeholder="Nome da Pregação...")
        st.session_state['titulo_sermao'] = novo_tit
    with c_save_e:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if st.session_state['titulo_sermao']:
                caminho = os.path.join(PASTA, f"{st.session_state['titulo_sermao']}.txt")
                with open(caminho, "w") as f:
                    f.write(st.session_state['texto_esboco'])
                st.toast("Projeto salvo com segurança.")
    
    # Editor Principal
    txt = st.text_area("EDITOR", value=st.session_state['texto_esboco'], height=600, label_visibility="collapsed")
    st.session_state['texto_esboco'] = txt
    
    # Barra de Ferramentas do Editor
    st.markdown("---")
    cf1, cf2 = st.columns([1, 1])
    with cf1:
        if st.button("✨ CORRIGIR & MELHORAR TEXTO"):
            if not api_key: st.error("Requer chave Google")
            else:
                with st.spinner("IA Revisando seu texto..."):
                    corrected = gemini_fixer(st.session_state['texto_esboco'], api_key)
                    st.session_state['texto_esboco'] = corrected
                    st.rerun()

# 3. PAINEL DIREITO: ATALHOS RÁPIDOS
with col_ferramenta:
    st.markdown("### 🧰 TOOLS")
    
    with st.expander("🗣 TRADUTOR", expanded=True):
        trad_txt = st.text_area("Texto em Inglês:")
        if st.button("Traduzir"):
            # Lógica simples de tradução via IA
            genai.configure(api_key=api_key)
            t = genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Traduza para português: {trad_txt}").text
            st.info(t)
            if st.button("Inserir Tradução"):
                 st.session_state['texto_esboco'] += f"\n\n[Tradução]: {t}"
                 
    with st.expander("🔎 WEB SEARCH"):
        q = st.text_input("Tema:")
        if st.button("Buscar"):
            try:
                r = DDGS().text(q, max_results=2)
                for res in r:
                    st.caption(f"{res['title']}")
                    st.write(res['body'][:100]+"...")
            except: st.error("Erro busca")
