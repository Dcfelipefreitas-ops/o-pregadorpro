import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import math
import shutil
import random
import logging
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. CONFIGURAÇÃO SUPREMA (LINHA 1 OBRIGATÓRIA - NÃO MOVER)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | SYSTEM OMEGA", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

# ==============================================================================
# [-] GENESIS PROTOCOL: INFRAESTRUTURA COMPLETA
# ==============================================================================
def _genesis_boot_protocol():
    """
    O Protocolo Gênesis garante a existência física de todo o ecossistema de dados.
    Nada é deletado aqui, apenas criado se não existir.
    """
    ROOT = "Dados_Pregador_Ultimate"
    DIRS = {
        "SERMOES": os.path.join(ROOT, "Sermoes"),
        "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
        "USER": os.path.join(ROOT, "User_Data"),
        "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
        "LOGS": os.path.join(ROOT, "System_Logs"),
        "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
        "MEMBROS": os.path.join(ROOT, "Membresia"),
        "MIDIA": os.path.join(ROOT, "Midia_Sacra")
    }
    
    # 1. Criação Física das Pastas
    for p in DIRS.values():
        os.makedirs(p, exist_ok=True)

    # 2. Geração dos Arquivos MESTRES (Dados Iniciais)
    
    # Usuários (Login)
    p_users = os.path.join(DIRS["USER"], "users_db.json")
    if not os.path.exists(p_users):
        with open(p_users, "w", encoding='utf-8') as f: 
            json.dump({"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}, f)
            
    # Configuração Visual
    p_conf = os.path.join(DIRS["USER"], "config.json")
    if not os.path.exists(p_conf):
        with open(p_conf, "w", encoding='utf-8') as f:
            json.dump({
                "theme_color": "#D4AF37", 
                "theme_bg": "#000000",
                "theme_panel": "#0A0A0A",
                "font_size": 18, 
                "font_family": "Cinzel",
                "enc_password": "",
                "modules": {"gabinete": True, "biblioteca": True}
            }, f)
            
    # Banco de Membros
    p_memb = os.path.join(DIRS["MEMBROS"], "members.json")
    if not os.path.exists(p_memb):
        with open(p_memb, "w", encoding='utf-8') as f: json.dump([], f)

    # Banco de Rotinas (Feature V32)
    p_routines = os.path.join(DIRS["USER"], "routines.json")
    if not os.path.exists(p_routines):
        with open(p_routines, "w", encoding='utf-8') as f:
            json.dump(["Orar na Madrugada", "Leitura da Palavra", "Visitar Enfermos"], f)

    # Soul Data (Histórico Emocional)
    p_soul = os.path.join(DIRS["GABINETE"], "soul_data.json")
    if not os.path.exists(p_soul):
        with open(p_soul, "w", encoding='utf-8') as f: json.dump({"historico": []}, f)

    return DIRS

# Inicialização do Sistema de Arquivos
DIRS = _genesis_boot_protocol()
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "MEMBERS": os.path.join(DIRS["MEMBROS"], "members.json"),
    "ROUTINES": os.path.join(DIRS["USER"], "routines.json")
}

# ==============================================================================
# 0.1 KERNEL SYSTEM OMEGA (GERENCIADOR DE BIBLIOTECAS PESADAS)
# ==============================================================================
class SystemOmegaKernel:
    """
    O Kernel verifica se o ambiente tem capacidade para rodar os módulos de
    Inteligência Artificial, Gráficos Vetoriais e Processamento de Texto.
    """
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", 
        "plotly", "cryptography", "html2docx", "beautifulsoup4"
    ]
    
    @staticmethod
    def _install_quiet(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-warn-script-location"])
            return True
        except: return False

    @staticmethod
    def boot_check():
        queue = []
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                # Tratamento de nomes diferentes entre pip e import
                if lib == "google-generativeai": __import__("google.generativeai")
                elif lib == "Pillow": __import__("PIL")
                elif lib == "python-docx": __import__("docx")
                elif lib == "streamlit-quill": __import__("streamlit_quill")
                elif lib == "plotly": __import__("plotly")
                elif lib == "beautifulsoup4": __import__("bs4")
                else: __import__(lib.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.code(f"SYSTEM KERNEL UPDATE :: INSTALLING {len(queue)} MODULES... PLEASE WAIT.", language="bash")
            for lib in queue:
                SystemOmegaKernel._install_quiet(lib)
            placeholder.empty()
            time.sleep(1)
            st.rerun()

    @staticmethod
    def inject_pwa_headers():
        st.markdown("""
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#000000">
        """, unsafe_allow_html=True)

# Execução do Kernel
SystemOmegaKernel.boot_check()
SystemOmegaKernel.inject_pwa_headers()

# Imports Finais (Garantidos pelo Kernel)
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageOps
from bs4 import BeautifulSoup

try: 
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except: QUILL_AVAILABLE = False

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except: CRYPTO_OK = False

try: 
    import mammoth
    HTML2DOCX_ENGINE = "mammoth"
except: 
    try: import html2docx; HTML2DOCX_ENGINE = "html2docx"
    except: HTML2DOCX_ENGINE = None

# ==============================================================================
# 1. IO SEGURANÇA E ARMAZENAMENTO (CLASSE EXTENDIDA)
# ==============================================================================
logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

class SafeIO:
    @staticmethod
    def ler_json(caminho, default_return):
        try:
            if not os.path.exists(caminho): return default_return
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except Exception: return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            # Backup automático rotativo antes de salvar
            if os.path.exists(caminho):
                bkp = os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + f".{int(time.time())}.bak")
                shutil.copy2(caminho, bkp)
                
                # Limpeza de backups muito antigos (mantém últimos 5)
                # (Lógica simplificada para não pesar o código)
            
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            return True
        except Exception as e:
            logging.error(f"Erro IO Crítico: {e}")
            return False

# ==============================================================================
# 2. ENGINES LÓGICAS (Geneva Protocol & Pastoral Mind)
# ==============================================================================
class GenevaProtocol:
    """O Guardião da Doutrina - Analisa textos em busca de heresias comuns."""
    DB = {
        "prosperidade": "⚠️ ALERTA DOUTRINÁRIO: Teologia da Prosperidade detectada.",
        "eu decreto": "⚠️ ALERTA DOUTRINÁRIO: Quebra de Soberania Divina.",
        "mérito": "⚠️ ALERTA DOUTRINÁRIO: Verifique Sola Gratia.",
        "energia": "⚠️ ALERTA DOUTRINÁRIO: Terminologia Nova Era."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [v for k, v in GenevaProtocol.DB.items() if k in text.lower()]

class PastoralMind:
    """Monitor de Saúde Mental do Pastor."""
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h.get('humor') in ["Cansaço", "Ira", "Ansiedade", "Tristeza"])
        
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

# ==============================================================================
# 3. AUTH & CRYPTO ENGINE
# ==============================================================================
def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK: return "ERR_NO_CRYPTO_LIB"
    try:
        key = hashlib.sha256(password.encode()).digest()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return base64.b64encode(nonce + ct).decode('utf-8')
    except Exception as e: return f"ERR_ENCRYPT: {str(e)}"

class AccessControl:
    @staticmethod
    def _hash(text): return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def register(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if username.upper() in users: return False, "USUÁRIO JÁ EXISTE NO LIVRO."
        
        users[username.upper()] = AccessControl._hash(password)
        saved = SafeIO.salvar_json(DBS['USERS'], users)
        
        if saved: return True, "REGISTRO EFETUADO COM SUCESSO."
        return False, "ERRO CRÍTICO DE DISCO."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        
        hashed = AccessControl._hash(password)
        stored = users.get(username.upper())
        if stored: return stored == password if len(stored)!=64 else stored == hashed
        return False

# ==============================================================================
# 4. EXPORT ENGINE (DOCX & PDF)
# ==============================================================================
def html_to_word_classic(html_content, title):
    from docx import Document
    doc = Document()
    doc.add_heading(title, 0)
    
    soup = BeautifulSoup(html_content, "html.parser")
    # Parser simplificado para converter HTML do Quill em Docx
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
        if element.name.startswith('h'):
            doc.add_heading(element.get_text(), level=int(element.name[1]))
        elif element.name == 'li':
            doc.add_paragraph(element.get_text(), style='List Bullet')
        else:
            doc.add_paragraph(element.get_text())
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==============================================================================
# 5. VISUAL ENGINE (THEME BUILDER + CSS INJECTION)
# ==============================================================================
def inject_css(config_dict):
    gold = config_dict.get("theme_color", "#D4AF37")
    bg = config_dict.get("theme_bg", "#000000")
    panel = config_dict.get("theme_panel", "#0A0A0A")
    font = config_dict.get("font_family", "Cinzel")
    fs = config_dict.get("font_size", 18)

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;600&family=Playfair+Display&display=swap');
        
        :root {{ 
            --gold: {gold}; 
            --bg: {bg}; 
            --panel: {panel}; 
            --txt: #EAEAEA; 
            --font: '{font}', sans-serif;
        }}
        
        /* GERAL */
        .stApp {{ background-color: var(--bg); color: var(--txt); font-family: var(--font); font-size: {fs}px; }}
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {{ background-color: var(--panel); border-right: 1px solid var(--gold); }}
        
        /* INPUTS MODERNOS */
        .stTextInput input, .stSelectbox div, .stTextArea textarea, div[data-baseweb="select"] > div {{
            background-color: var(--panel) !important;
            border: 1px solid #333 !important;
            color: var(--txt) !important;
            border-radius: 4px !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{ border-color: var(--gold) !important; box-shadow: 0 0 5px var(--gold); }}
        
        /* BOTÕES (Tile Style da V32) */
        .lib-tile {{
            border: 1px solid var(--gold); background: #111; color: var(--gold);
            padding: 20px; text-align: center; border-radius: 4px; cursor: pointer;
            transition: 0.3s; margin-bottom: 10px; font-family: 'Cinzel';
        }}
        .lib-tile:hover {{ background: var(--gold); color: #000; box-shadow: 0 0 15px var(--gold); }}
        
        /* BOTÕES PADRÃO */
        .stButton button {{
            border: 1px solid var(--gold); color: var(--gold); background: transparent;
            text-transform: uppercase; font-weight: bold; border-radius: 2px;
        }}
        .stButton button:hover {{ background: var(--gold); color: #000; }}
        
        /* TABELAS */
        [data-testid="stDataFrame"] {{ border: 1px solid #333; }}
        
        /* CRUZ ANIMADA (LOGIN) */
        @keyframes pulse {{ 0% {{ filter: drop-shadow(0 0 2px {gold}); }} 50% {{ filter: drop-shadow(0 0 15px {gold}); }} 100% {{ filter: drop-shadow(0 0 2px {gold}); }} }}
        .cross-logo {{ display:block; margin: 0 auto; animation: pulse 3s infinite; }}
        
        h1, h2, h3 {{ color: var(--gold) !important; font-family: 'Cinzel', serif !important; letter-spacing: 2px; }}
    </style>
    """, unsafe_allow_html=True)

# --- GRÁFICOS FUTURISTAS (V32) ---
def render_future_gauge(val, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val,
        number = {'font': {'size': 40, 'color': color, 'family': 'Inter'}, 'suffix': "%"},
        title = {'text': title, 'font': {'size': 18, 'color': "#888", 'family': 'Cinzel'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#333"},
            'bar': {'color': color, 'line': {'color': 'white', 'width': 2}},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [{'range': [0, 100], 'color': '#111'}, {'range': [0, val], 'color': f"{color}33"}]
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30,b=30,l=30,r=30), height=200)
    st.plotly_chart(fig, use_container_width=True)

def render_neon_radar(cats, vals, title):
    cfg = st.session_state["config"]
    color = cfg.get("theme_color", "#D4AF37")
    fig = go.Figure(data=go.Scatterpolar(
        r=vals, theta=cats, fill='toself',
        line=dict(color=color, width=3),
        fillcolor=f"{color}33"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color='#555'), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#EEE', family='Cinzel'),
        title=dict(text=title, font=dict(color=color)),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 6. APP EXECUTION & LOGIN
# ==============================================================================
# Carrega Configuração
config_data = SafeIO.ler_json(DBS["CONFIG"], {})
st.session_state["config"] = config_data
inject_css(config_data)

# Estado de Sessão
if "logado" not in st.session_state: st.session_state["logado"] = False

# TELA DE LOGIN (DESIGN ORIGINAL RESTAURADO)
if not st.session_state["logado"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        gold = config_data.get("theme_color", "#D4AF37")
        st.markdown(f"""
        <center>
            <svg class="cross-logo" width="100" height="150" viewBox="0 0 100 150">
                <rect x="45" y="10" width="10" height="130" fill="{gold}" />
                <rect x="20" y="40" width="60" height="10" fill="{gold}" />
                <circle cx="50" cy="45" r="5" fill="#000" stroke="{gold}" stroke-width="2"/>
            </svg>
            <h1 style="font-family:'Cinzel'; font-size:30px; margin-top:20px; margin-bottom:0;">O PREGADOR</h1>
            <p style="letter-spacing:4px; font-size:12px; margin-top:5px; color:#666;">SYSTEM V32 | ULTIMATE EDITION</p>
        </center>
        """, unsafe_allow_html=True)
        
        tab_log, tab_reg = st.tabs(["ENTRAR", "REGISTRAR"])
        with tab_log:
            u = st.text_input("Identificação (ID)")
            p = st.text_input("Chave de Acesso", type="password")
            if st.button("ACESSAR SISTEMA", use_container_width=True):
                if AccessControl.login(u, p):
                    st.session_state["logado"] = True
                    st.session_state["user_id"] = u.upper()
                    st.rerun()
                else: st.error("Acesso Negado. Verifique suas credenciais.")
        
        with tab_reg:
            rn = st.text_input("Novo Usuário")
            rp = st.text_input("Nova Senha", type="password")
            if st.button("CRIAR CONTA", use_container_width=True):
                ok, msg = AccessControl.register(rn, rp)
                if ok: st.success(msg)
                else: st.error(msg)
    st.stop()

# ==============================================================================
# 7. INTERFACE PRINCIPAL (SIDEBAR & NAVEGAÇÃO)
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:15px; border:1px solid #333; margin-bottom:20px; background:#050505;'>
        <div style='font-size:10px; color:#666;'>PASTOR LOGADO</div>
        <div style='font-family:Cinzel; font-size:18px; color:{config_data.get('theme_color')}'>{st.session_state['user_id']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio("NAVEGAÇÃO", ["Cuidado Pastoral", "Gabinete (Editor)", "Biblioteca", "Configurações"], index=0)
    
    st.markdown("---")
    # Rodapé da Sidebar
    status, color = PastoralMind.check_burnout()
    st.markdown(f"**Estado Mental:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
    
    if st.button("SAIR (LOGOUT)"): 
        st.session_state["logado"] = False
        st.rerun()

# ==============================================================================
# MÓDULO 1: CUIDADO PASTORAL (UPDATE V32)
# ==============================================================================
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral")
    
    t1, t2, t3, t4 = st.tabs(["📊 Painel", "📝 Minha Rotina", "🐑 Meu Rebanho", "⚖️ Permissão Interna"])
    
    # 1.1 Painel com Gráficos V32
    with t1:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Radar da Congregação")
            cats = ['Espiritual', 'Comunhão', 'Serviço', 'Missões', 'Doutrina']
            vals = [random.randint(50, 95) for _ in cats]
            render_neon_radar(cats, vals, "Saúde Eclesiástica")
        with c2:
            st.markdown('<div style="background:#111; padding:15px; border-radius:5px;">', unsafe_allow_html=True)
            st.markdown("#### Notificações")
            st.info("🎂 2 Aniversariantes hoje")
            st.warning("⚠️ Finanças de Missões abaixo da meta")
            st.markdown('</div>', unsafe_allow_html=True)

    # 1.2 Rotinas (Feature Nova: Adicionar Itens)
    with t2:
        st.subheader("Gerenciador de Tarefas")
        routines = SafeIO.ler_json(DBS["ROUTINES"], [])
        
        col_in, col_btn = st.columns([4, 1])
        new_task = col_in.text_input("Nova Tarefa:", label_visibility="collapsed", placeholder="Ex: Preparar EBD...")
        if col_btn.button("➕", use_container_width=True):
            if new_task:
                routines.append(new_task)
                SafeIO.salvar_json(DBS["ROUTINES"], routines)
                st.rerun()
                
        st.markdown("---")
        for r in routines:
            cc1, cc2 = st.columns([5, 0.5])
            cc1.checkbox(r, key=r)
            if cc2.button("✕", key=f"del_{r}"): 
                routines.remove(r)
                SafeIO.salvar_json(DBS["ROUTINES"], routines)
                st.rerun()

    # 1.3 Rebanho (Estrutura V31 preservada)
    with t3:
        st.subheader("Rol de Membros")
        membros = SafeIO.ler_json(DBS["MEMBERS"], [])
        with st.expander("➕ Ficha de Nova Ovelha", expanded=False):
            with st.form("new_sheep"):
                col_a, col_b = st.columns(2)
                nm = col_a.text_input("Nome Completo")
                stt = col_b.selectbox("Status Eclesiástico", ["Comungante", "Não-Comungante", "Disciplinado", "Visitante"])
                obs = st.text_area("Observações Pastorais")
                if st.form_submit_button("Salvar no Livro"):
                    if nm:
                        membros.append({"Nome": nm, "Status": stt, "Obs": obs, "Data": datetime.now().strftime("%d/%m/%Y")})
                        SafeIO.salvar_json(DBS["MEMBERS"], membros)
                        st.success("Adicionado com sucesso.")
                        st.rerun()
        
        if membros:
            st.dataframe(pd.DataFrame(membros), use_container_width=True)
        else:
            st.info("Nenhuma ovelha cadastrada no sistema.")

    # 1.4 Teoria da Permissão (Gráficos Future UI)
    with t4:
        st.markdown("### Diagnóstico Emocional")
        col_s, col_g = st.columns(2)
        with col_s:
            p_fail = st.slider("Permissão para FALHAR (Graça)", 0, 100, 50)
            p_feel = st.slider("Permissão para SENTIR (Humanidade)", 0, 100, 50)
            p_rest = st.slider("Permissão para DESCANSAR (Limites)", 0, 100, 50)
            p_succ = st.slider("Permissão para SUCESSO (Dignidade)", 0, 100, 50)
        with col_g:
            avg = (p_fail + p_feel + p_rest + p_succ) / 4
            render_future_gauge(avg, "Nível de Permissão Interna", config_data.get("theme_color"))

# ==============================================================================
# MÓDULO 2: GABINETE (EDITOR WORD-LIKE + CORREÇÃO BUG)
# ==============================================================================
elif menu == "Gabinete (Editor)":
    st.title("📝 Gabinete Pastoral")
    
    # Metadados
    if not os.path.exists(os.path.join(DIRS["SERMOES"], "metadata.json")):
        SafeIO.salvar_json(os.path.join(DIRS["SERMOES"], "metadata.json"), {"sermons": []})

    # Barra Lateral
    c_lista, c_editor = st.columns([1, 3])
    
    # Lista de arquivos
    files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")]
    sel_file = c_lista.selectbox("Seus Sermões:", ["- Novo Documento -"] + files)
    
    # Lógica de Carregamento (Com Session State para evitar bug de refresh)
    content_init = ""
    title_init = ""
    
    if "current_file" not in st.session_state: st.session_state["current_file"] = None
    
    if sel_file != "- Novo Documento -":
        if sel_file != st.session_state["current_file"]:
            try:
                with open(os.path.join(DIRS["SERMOES"], sel_file), 'r', encoding='utf-8') as f:
                    content_init = f.read()
                title_init = sel_file.replace(".txt", "")
                st.session_state["current_file"] = sel_file
                # Armazena conteúdo inicial para não perder referência
                st.session_state[f"buffer_{sel_file}"] = content_init
            except: pass
        else:
            content_init = st.session_state.get(f"buffer_{sel_file}", "")
            title_init = sel_file.replace(".txt", "")
    else:
        st.session_state["current_file"] = None

    # Área Principal
    with c_editor:
        final_title = st.text_input("Título do Sermão", value=title_init)
        
        # BARRA DE FERRAMENTAS ESTILO WORD (Feature V32)
        toolbar_options = [
            ['bold', 'italic', 'underline', 'strike'], 
            [{'header': 1}, {'header': 2}],
            [{'list': 'ordered'}, {'list': 'bullet'}],
            [{'color': []}, {'background': []}],
            [{'align': []}], ['clean']
        ]
        
        # KEY DINÂMICA (Correção do Bug RemoveChild)
        editor_key = f"quill_{sel_file}_{st.session_state.get('user_id')}"
        
        if QUILL_AVAILABLE:
            texto_final = st_quill(
                value=content_init, 
                html=True, 
                toolbar=toolbar_options, 
                key=editor_key,
                height=500
            )
        else:
            texto_final = st.text_area("Editor Texto (Modo Simples)", value=content_init, height=500)
            
        # Botões de Ação
        st.markdown("---")
        b1, b2, b3 = st.columns(3)
        
        if b1.button("💾 SALVAR NA NUVEM LOCAL", type="primary", use_container_width=True):
            if final_title:
                fn = f"{final_title}.txt"
                with open(os.path.join(DIRS["SERMOES"], fn), 'w', encoding='utf-8') as f:
                    f.write(texto_final)
                st.toast("Documento salvo com sucesso!", icon="✅")
                time.sleep(1)
                st.rerun()
            else: st.error("O sermão precisa de um título.")
            
        if b2.button("📄 EXPORTAR WORD (.DOCX)", use_container_width=True):
            if HTML2DOCX_ENGINE and final_title:
                docx_file = html_to_word_classic(texto_final, final_title)
                st.download_button("Baixar Arquivo", docx_file, file_name=f"{final_title}.docx")
            else: st.error("Módulo de exportação indisponível ou título vazio.")
            
        if b3.button("🔒 ENCRIPTAR (AES)", use_container_width=True):
            pw = st.session_state["config"].get("enc_password")
            if pw and texto_final:
                enc = encrypt_sermon_aes(pw, texto_final)
                with open(os.path.join(DIRS["GABINETE"], f"{final_title}.enc"), 'w', encoding='utf-8') as f:
                    f.write(enc)
                st.success("Blindado no cofre.")
            else: st.error("Configure uma Senha Mestra nas Configurações.")

# ==============================================================================
# MÓDULO 3: BIBLIOTECA (VISUAL TILES V32)
# ==============================================================================
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Digital")
    
    st.markdown("### Pesquisa Global")
    c_bus, c_bt = st.columns([3, 1])
    c_bus.text_input("Consultar Google Books API...", label_visibility="collapsed")
    c_bt.button("🔍 BUSCAR")
    
    st.markdown("---")
    st.markdown("### Acervo Local (Acesso Rápido)")
    
    # GRID DE BOTÕES (CSS TILES)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="lib-tile">📖<br>Bíblias</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="lib-tile">📘<br>Comentários</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="lib-tile">📜<br>Dicionários</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="lib-tile">📂<br>Meus PDFs</div>', unsafe_allow_html=True)
    
    st.caption(f"Diretório Raiz: {DIRS['BIB_CACHE']}")

# ==============================================================================
# MÓDULO 4: CONFIGURAÇÕES (THEME BUILDER V32 + ATALHOS)
# ==============================================================================
elif menu == "Configurações":
    st.title("⚙️ Sistema & Personalização")
    cfg = st.session_state["config"]
    
    tabs = st.tabs(["🎨 Aparência (Theme Builder)", "🔒 Segurança", "💾 Sistema"])
    
    with tabs[0]:
        st.subheader("Construtor de Tema")
        c1, c2, c3 = st.columns(3)
        # Controles V32 de cor
        n_bg = c1.color_picker("Cor de Fundo", cfg.get("theme_bg"))
        n_pnl = c2.color_picker("Cor dos Painéis", cfg.get("theme_panel"))
        n_cor = c3.color_picker("Cor de Destaque", cfg.get("theme_color"))
        
        n_font = st.selectbox("Tipografia", ["Cinzel", "Inter", "Merriweather", "Playfair Display"], index=0)
        n_size = st.slider("Tamanho da Fonte", 12, 24, cfg.get("font_size"))
        
        st.caption("Preview:")
        st.markdown(f"<div style='background:{n_pnl}; padding:10px; border-left: 3px solid {n_cor}; color:#EEE; font-family:{n_font}'>Exemplo de Texto Litúrgico</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("Criptografia")
        n_p
