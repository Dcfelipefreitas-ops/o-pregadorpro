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
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 0. LINHA 1 OBRIGATÓRIA (NÃO APAGAR)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

# ==============================================================================
# [-] GENESIS PROTOCOL: RESTAURADO (COM ROTINAS V32)
# ==============================================================================
def _genesis_boot_protocol():
    ROOT = "Dados_Pregador_Final"
    DIRS = {
        "SERMOES": os.path.join(ROOT, "Sermoes"),
        "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
        "USER": os.path.join(ROOT, "User_Data"),
        "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
        "LOGS": os.path.join(ROOT, "System_Logs"),
        "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
        "MEMBROS": os.path.join(ROOT, "Membresia")
    }
    
    # Cria Pastas
    for p in DIRS.values(): os.makedirs(p, exist_ok=True)

    # Cria Arquivos Base
    files_check = {
        os.path.join(DIRS["USER"], "users_db.json"): {"ADMIN": hashlib.sha256("admin".encode()).hexdigest()},
        os.path.join(DIRS["USER"], "config.json"): {"theme_color": "#D4AF37", "font_size": 18, "enc_password": "", "theme_bg": "#000000", "theme_panel": "#0A0A0A"},
        os.path.join(DIRS["USER"], "routines.json"): ["Orar na Madrugada", "Leitura Bíblica"], # Nova Feature
        os.path.join(DIRS["MEMBROS"], "members.json"): []
    }
    
    for path, content in files_check.items():
        if not os.path.exists(path):
            with open(path, "w", encoding='utf-8') as f: json.dump(content, f)
            
    return DIRS

DIRS = _genesis_boot_protocol()
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "ROUTINES": os.path.join(DIRS["USER"], "routines.json"), # FEATURE NOVA
    "MEMBERS": os.path.join(DIRS["MEMBROS"], "members.json")
}

# ==============================================================================
# 0.1 KERNEL V31 (ORIGINAL)
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = ["streamlit-quill", "plotly", "pandas", "cryptography", "mammoth"]
    @staticmethod
    def _install_quiet(pkg):
        try: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        except: pass
    @staticmethod
    def boot():
        try: 
            import streamlit_quill
            import plotly
        except:
            for lib in SystemOmegaKernel.REQUIRED: SystemOmegaKernel._install_quiet(lib)
            st.rerun()

SystemOmegaKernel.boot()
try: from streamlit_quill import st_quill; QUILL_AVAILABLE = True
except: QUILL_AVAILABLE = False
try: from cryptography.hazmat.primitives.ciphers.aead import AESGCM; CRYPTO_OK = True
except: CRYPTO_OK = False
try: import mammoth; HTML2DOCX = "mammoth"
except: HTML2DOCX = None

# ==============================================================================
# 1. IO SEGURANÇA
# ==============================================================================
class SafeIO:
    @staticmethod
    def ler(p, d): 
        try: return json.load(open(p, encoding='utf-8'))
        except: return d
    @staticmethod
    def salvar(p, d):
        try: 
            json.dump(d, open(p, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
            return True
        except: return False

def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK: return None
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ct).decode('utf-8')

class AccessControl:
    @staticmethod
    def register(u, p):
        db = SafeIO.ler(DBS["USERS"], {})
        if u.upper() in db: return False
        db[u.upper()] = hashlib.sha256(p.encode()).hexdigest()
        SafeIO.salvar(DBS["USERS"], db) # Salva Imediato
        return True
    @staticmethod
    def login(u, p):
        db = SafeIO.ler(DBS["USERS"], {})
        if not db and u=="ADMIN" and p=="1234": return True # Backdoor inicial
        h = hashlib.sha256(p.encode()).hexdigest()
        return db.get(u.upper()) == h

# ==============================================================================
# 2. VISUAL V31 RESTAURADO + RECURSOS NOVOS (TILES & EDITOR)
# ==============================================================================
def inject_css(cfg):
    gold = cfg.get("theme_color", "#D4AF37")
    bg = cfg.get("theme_bg", "#000000")      # Config nova integrada ao visual velho
    panel = cfg.get("theme_panel", "#0A0A0A") # Config nova
    font = cfg.get("font_family", "Cinzel")
    fs = cfg.get("font_size", 18)

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;600&family=Playfair+Display&display=swap');
        
        :root {{ --gold: {gold}; --bg: {bg}; --panel: {panel}; --txt: #EAEAEA; }}
        
        .stApp {{ background-color: var(--bg); color: var(--txt); font-family: 'Inter', sans-serif; font-size: {fs}px; }}
        [data-testid="stSidebar"] {{ background-color: var(--panel); border-right: 1px solid var(--gold); }}
        
        /* RESTAURADO V31 */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{ background-color: var(--panel) !important; border: 1px solid #333 !important; color: #EEE !important; }}
        h1, h2, h3 {{ color: var(--gold) !important; font-family: 'Cinzel', serif !important; }}
        
        /* BOTÕES NOVOS (TILES DA BIBLIOTECA) */
        .lib-tile {{
            border: 1px solid var(--gold); background: #111; color: var(--gold);
            padding: 20px; text-align: center; border-radius: 4px; cursor: pointer;
            transition: 0.3s; margin-bottom: 10px;
        }}
        .lib-tile:hover {{ background: var(--gold); color: #000; box-shadow: 0 0 10px var(--gold); }}

        /* GRÁFICOS TRANSPARENTES */
        .js-plotly-plot .plotly .main-svg {{ background: rgba(0,0,0,0) !important; }}
        
        .stButton button {{ border: 1px solid var(--gold); color: var(--gold); background: transparent; text-transform: uppercase; font-weight: bold; }}
        .stButton button:hover {{ background: var(--gold); color: #000; }}
        
        /* LOGO CRUZ LOGIN V31 */
        @keyframes pulse {{ 0% {{ filter: drop-shadow(0 0 2px {gold}); }} 50% {{ filter: drop-shadow(0 0 10px {gold}); }} }}
        .cross-logo {{ display:block; margin: 0 auto; animation: pulse 4s infinite; }}
    </style>
    """, unsafe_allow_html=True)

# GRÁFICOS FUTURISTAS (Nova demanda, Visual Aprovado V32)
def render_future_gauge(val, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val,
        number = {'font': {'size': 30, 'color': color, 'family': 'Inter'}, 'suffix': "%"},
        title = {'text': title, 'font': {'size': 18, 'color': "#888", 'family': 'Cinzel'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [{'range': [0, 100], 'color': '#111'}, {'range': [0, val], 'color': f"{color}33"}]
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20), height=180)
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 3. APP LOGIC V31
# ==============================================================================
config = SafeIO.ler(DBS["CONFIG"], {})
st.session_state["config"] = config
inject_css(config)

if "logado" not in st.session_state: st.session_state["logado"] = False

# TELA DE LOGIN ORIGINAL (CRUZ + O PREGADOR) - RESTAURADO 100%
if not st.session_state["logado"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        gold = config.get("theme_color")
        # SUA CRUZ SVG
        st.markdown(f"""
        <center>
            <svg class="cross-logo" width="100" height="150" viewBox="0 0 100 150">
                <rect x="45" y="10" width="10" height="130" fill="{gold}" />
                <rect x="20" y="40" width="60" height="10" fill="{gold}" />
                <circle cx="50" cy="45" r="5" fill="#000" stroke="{gold}" stroke-width="2"/>
            </svg>
            <h1 style="font-family:'Cinzel'; font-size:28px; margin-top:10px;">O PREGADOR</h1>
            <small style="letter-spacing:3px;">SYSTEM V31 | SHEPHERD EDITION</small>
        </center>
        """, unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["ENTRAR", "REGISTRAR"])
        with t1:
            u = st.text_input("ID")
            p = st.text_input("Senha", type="password")
            if st.button("ACESSAR", use_container_width=True):
                if AccessControl.login(u, p):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = u.upper()
                    st.rerun()
                else: st.error("Acesso Negado.")
        with t2:
            nu = st.text_input("Novo ID")
            np = st.text_input("Nova Senha", type="password")
            if st.button("CRIAR"):
                if AccessControl.register(nu, np): st.success("Registrado.")
                else: st.error("Erro ou Existente.")
    st.stop()

# MENUS ORIGINAIS
with st.sidebar:
    st.markdown(f"<div style='text-align:center'>Pastor: <b>{st.session_state['user_name']}</b></div>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["Cuidado Pastoral", "Gabinete Pastoral", "Biblioteca", "Configurações"], index=0)
    st.markdown("---")
    if st.button("SAIR"): 
        st.session_state["logado"] = False
        st.rerun()

# ------------------------------------------------------------------------------
# 1. CUIDADO PASTORAL (Visual Antigo + Funcionalidades Novas)
# ------------------------------------------------------------------------------
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral")
    
    # Abas Originais
    t1, t2, t3 = st.tabs(["Minha Rotina (Update)", "Teoria da Permissão (Gráficos Future)", "Meu Rebanho"])
    
    # 1.1 ROTINAS COM O BOTÃO "+" QUE VOCÊ PEDIU
    with t1:
        st.subheader("Gerenciar Tarefas")
        routines = SafeIO.ler(DBS["ROUTINES"], [])
        
        # O Update do "+"
        c_in, c_btn = st.columns([4, 1])
        new_task = c_in.text_input("Nova Tarefa Personalizada", label_visibility="collapsed")
        if c_btn.button("➕"):
            if new_task:
                routines.append(new_task)
                SafeIO.salvar(DBS["ROUTINES"], routines)
                st.rerun()
        
        st.markdown("---")
        for r in routines:
            cc1, cc2 = st.columns([5, 0.5])
            cc1.checkbox(r)
            if cc2.button("✕", key=r): 
                routines.remove(r)
                SafeIO.salvar(DBS["ROUTINES"], routines)
                st.rerun()

    # 1.2 TEORIA DA PERMISSÃO COM GRÁFICOS FUTURISTAS
    with t2:
        st.markdown("### Diagnóstico Emocional")
        col_s, col_g = st.columns(2)
        with col_s:
            pf = st.slider("FALHAR", 0, 100, 50)
            ps = st.slider("SENTIR", 0, 100, 50)
            pd = st.slider("DESCANSAR", 0, 100, 50)
            pi = st.slider("SUCESSO", 0, 100, 50)
        with col_g:
            # Novo gráfico dentro da estrutura velha
            render_future_gauge((pf+ps+pd+pi)/4, "Permissão Interna", config.get("theme_color"))

    # 1.3 REBANHO (Tabela Alinhada V31)
    with t3:
        st.subheader("Rol de Membros")
        membros = SafeIO.ler(DBS["MEMBERS"], [])
        with st.expander("➕ Nova Ovelha"):
            with st.form("add_mem"):
                nm = st.text_input("Nome")
                stt = st.selectbox("Status", ["Comungante", "Não-Comungante"])
                if st.form_submit_button("Salvar"):
                    membros.append({"Nome": nm, "Status": stt, "Data": datetime.now().strftime("%d/%m")})
                    SafeIO.salvar(DBS["MEMBERS"], membros)
                    st.rerun()
        if membros: st.dataframe(pd.DataFrame(membros), use_container_width=True)

# ------------------------------------------------------------------------------
# 2. GABINETE (Visual Antigo + Editor WORD + Correções)
# ------------------------------------------------------------------------------
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete (Editor)")
    
    c_lista, c_editor = st.columns([1, 4])
    files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")]
    sel = c_lista.selectbox("Arquivos:", ["Novo"] + files)
    
    texto_init = ""
    tit_init = ""
    if sel != "Novo":
        try:
            texto_init = open(os.path.join(DIRS["SERMOES"], sel), 'r').read()
            tit_init = sel.replace(".txt", "")
        except: pass
        
    with c_editor:
        titulo = st.text_input("Título", value=tit_init)
        
        # BARRA ESTILO WORD (Toolbar Full) - UPDATE V32 aplicado no V31
        word_toolbar = [
            ['bold', 'italic', 'underline', 'strike'], ['blockquote'],
            [{'header': 1}, {'header': 2}], [{'list': 'ordered'}, {'list': 'bullet'}],
            [{'color': []}, {'background': []}], [{'align': []}], ['clean']
        ]
        
        if QUILL_AVAILABLE:
            texto_final = st_quill(value=texto_init, html=True, toolbar=word_toolbar, key="editor_word")
        else:
            texto_final = st.text_area("Texto", value=texto_init, height=400)
            
        col_btns = st.columns(3)
        if col_btns[0].button("💾 SALVAR TXT"):
            if titulo:
                with open(os.path.join(DIRS["SERMOES"], f"{titulo}.txt"), 'w') as f: f.write(texto_final)
                st.success("Salvo.")
        
        if col_btns[1].button("🖨️ DOCX"):
            if titulo and HTML2DOCX:
                 path = os.path.join(DIRS["SERMOES"], f"{titulo}.docx")
                 with open(path, "wb") as f: f.write(mammoth.convert_to_docx(texto_final).value)
                 st.success("Gerado.")

# ------------------------------------------------------------------------------
# 3. BIBLIOTECA (Visual Antigo + TILES Melhorados)
# ------------------------------------------------------------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca")
    st.markdown("Busca Global e Local")
    st.text_input("Pesquisar Google Books...")
    st.markdown("---")
    st.markdown("### Acesso Rápido")
    # BOTÕES TILES NO V31
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="lib-tile">Bíblias</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="lib-tile">Comentários</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="lib-tile">Dicionários</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="lib-tile">PDFs Locais</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. CONFIGURAÇÕES (Visual Antigo + Funções Novas)
# ------------------------------------------------------------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    
    # Aba única (V31 Style) mas com mais controles
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Visual (Theme Builder)")
        # A pedido: mudar cores (Features V32 dentro da casca V31)
        bg = st.color_picker("Cor Fundo", config.get("theme_bg"))
        pn = st.color_picker("Cor Painel", config.get("theme_panel"))
        cl = st.color_picker("Cor Destaque", config.get("theme_color"))
        
    with c2:
        st.subheader("Sistema")
        fs = st.number_input("Tamanho Fonte", 12, 30, config.get("font_size"))
        pw = st.text_input("Senha Mestra (Crypto)", value=config.get("enc_password"), type="password")
    
    st.markdown("---")
    st.markdown("### Mapeamento de Funções")
    c3, c4 = st.columns(2)
    c3.checkbox("Ativar Autocorreção (Gabinete)", value=True)
    c4.checkbox("Ativar Notificações", value=True)

    if st.button("SALVAR E APLICAR PERSONALIZAÇÃO"):
        config.update({"theme_bg": bg, "theme_panel": pn, "theme_color": cl, "font_size": fs, "enc_password": pw})
        SafeIO.salvar(DBS["CONFIG"], config)
        st.success("Aplicado.")
        time.sleep(1)
        st.rerun()
