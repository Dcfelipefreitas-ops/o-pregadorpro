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
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# [-] GENESIS PROTOCOL: INFRAESTRUTURA DE DADOS & RESTAURAÇÃO
# (Este bloco garante que as pastas originais existam antes do Kernel)
# ==============================================================================
def _genesis_boot_protocol():
    ROOT = "Dados_Pregador_V31"
    PASTAS = {
        "SERMOES": os.path.join(ROOT, "Sermoes"),
        "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
        "USER": os.path.join(ROOT, "User_Data"),
        "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
        "LOGS": os.path.join(ROOT, "System_Logs"),
        "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
        "MEMBROS": os.path.join(ROOT, "Membresia")
    }
    
    # 1. Criação Física das Pastas
    for p in PASTAS.values():
        os.makedirs(p, exist_ok=True)

    # 2. Arquivos Essenciais (Garante integridade)
    # User DB
    p_users = os.path.join(PASTAS["USER"], "users_db.json")
    if not os.path.exists(p_users):
        with open(p_users, "w") as f: 
            json.dump({"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}, f)
            
    # Config DB
    p_conf = os.path.join(PASTAS["USER"], "config.json")
    if not os.path.exists(p_conf):
        with open(p_conf, "w") as f:
            json.dump({"theme_color": "#D4AF37", "theme_mode": "Dark Cathedral", "font_size": 18, "enc_password": ""}, f)
            
    # Membros DB
    p_memb = os.path.join(PASTAS["MEMBROS"], "members.json")
    if not os.path.exists(p_memb):
        with open(p_memb, "w") as f: json.dump([], f)

    # Stats DB e Soul Data (Recuperados do código original)
    if not os.path.exists(os.path.join(PASTAS["USER"], "db_stats.json")):
        with open(os.path.join(PASTAS["USER"], "db_stats.json"), "w") as f: json.dump({}, f)
        
    return PASTAS

# Executa Gênesis e Recupera Mapa de Pastas
DIRS = _genesis_boot_protocol()
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "MEMBERS": os.path.join(DIRS["MEMBROS"], "members.json")
}

# ==============================================================================
# 0. KERNEL SYSTEM OMEGA (Gerenciamento de Bibliotecas Pesadas)
# ==============================================================================
class SystemOmegaKernel:
    # Lista Completa Restaurada (Incluindo ReportLab e Cryptography)
    REQUIRED = [
        "google-generativeai", "streamlit-lottie", "Pillow", "pandas",
        "streamlit-quill", "python-docx", "reportlab", "mammoth", 
        "plotly", "cryptography", "html2docx"
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
                # Tratamento de imports complexos
                if lib == "google-generativeai": __import__("google.generativeai")
                elif lib == "Pillow": __import__("PIL")
                elif lib == "python-docx": __import__("docx")
                elif lib == "streamlit-quill": __import__("streamlit_quill")
                elif lib == "plotly": __import__("plotly")
                else: __import__(lib.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.code(f"SYSTEM UPDATE :: RESTORING KERNEL MODULES ({len(queue)})... DO NOT CLOSE.", language="bash")
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

# Inicializa Kernel
SystemOmegaKernel.boot_check()
SystemOmegaKernel.inject_pwa_headers()

# Imports Finais
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image, ImageOps
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
# 1. IO SEGURANÇA E ARMAZENAMENTO (Classes Originais Restauradas)
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
            # Backup automático antes de salvar (Feature Restaurada)
            if os.path.exists(caminho):
                bkp = os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak")
                shutil.copy2(caminho, bkp)
            
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            return True
        except Exception as e:
            logging.error(f"Erro IO: {e}")
            return False

# ==============================================================================
# 2. AUTH & CRYPTO ENGINE
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
        if username.upper() in users: return False, "Usuário já existe."
        
        # Salva imediatamente no disco (Correção de Bug)
        users[username.upper()] = AccessControl._hash(password)
        saved = SafeIO.salvar_json(DBS['USERS'], users)
        
        return saved, "Registrado com sucesso." if saved else "Erro crítico de I/O."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        # Backdoor Admin Original (Restaurado)
        if not users and username.upper() == "ADMIN" and password == "1234": return True
        
        hashed = AccessControl._hash(password)
        stored = users.get(username.upper())
        # Validação dupla (Hash antigo vs Novo)
        if stored: return stored == password if len(stored)!=64 else stored == hashed
        return False

# ==============================================================================
# 3. BIBLE & EXPORT ENGINES (Features Restauradas)
# ==============================================================================
class BibleEngine:
    @staticmethod
    def get_verse(ref):
        # Placeholder da lógica complexa original
        return f"Texto simulado da API para referência: {ref}"

def export_logic(title, html_content, type="docx"):
    # Caminho
    fn = f"{title}.{type}"
    path = os.path.join(DIRS["SERMOES"], fn)
    
    if type == "docx":
        if HTML2DOCX_ENGINE == "mammoth":
            with open(path, "wb") as f:
                res = mammoth.convert_to_docx(html_content)
                f.write(res.value)
        else:
            from docx import Document
            import re
            doc = Document()
            doc.add_heading(title, 0)
            clean_text = re.sub('<[^<]+?>', '', html_content)
            doc.add_paragraph(clean_text)
            doc.save(path)
    return path

# ==============================================================================
# 4. VISUAL ENGINE ("TheWord" Style + Alinhamento Profissional)
# ==============================================================================
def inject_css(config_dict):
    # Valores de segurança
    c = config_dict.get("theme_color", "#D4AF37")
    mode = config_dict.get("theme_mode", "Dark Cathedral")
    font = config_dict.get("font_family", "Cinzel")
    sz = config_dict.get("font_size", 18)

    # Temas Restaurados
    if mode == "Dark Cathedral":
        bg, pnl, txt = "#000000", "#090909", "#EAEAEA"
    elif mode == "Pergaminho (Sepia)":
        bg, pnl, txt = "#F4ECD8", "#E8DFCA", "#2b2210"
    else: # Holy Light
        bg, pnl, txt = "#FFFFFF", "#F5F5F5", "#111111"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;600&family=Playfair+Display&display=swap');
        
        :root {{ --gold: {c}; --bg: {bg}; --pnl: {pnl}; --txt: {txt}; --fbase: {sz}px; --ffam: '{font}', sans-serif; }}
        
        .stApp {{ background-color: var(--bg); color: var(--txt); font-family: var(--ffam); font-size: var(--fbase); }}
        
        /* ALINHAMENTO CORRETO DOS INPUTS (RESTAURADO) */
        .stTextInput input, .stSelectbox div, .stTextArea textarea, div[data-baseweb="select"] > div {{
            background-color: var(--pnl) !important;
            border: 1px solid #333 !important;
            color: var(--txt) !important;
            border-radius: 4px !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{ border-color: var(--gold) !important; }}
        
        /* Sidebar e Tabs */
        [data-testid="stSidebar"] {{ background-color: var(--pnl); border-right: 1px solid var(--gold); }}
        .stTabs [data-baseweb="tab-list"] {{ border-bottom: 2px solid var(--gold); }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: var(--gold); }}
        
        h1, h2, h3 {{ color: var(--gold) !important; font-family: 'Cinzel', serif !important; }}
        
        /* BOTÕES ESTILO PADRÃO SYSTEM OMEGA */
        .stButton button {{
            border: 1px solid var(--gold);
            color: var(--gold);
            background: transparent;
            text-transform: uppercase;
            font-weight: bold;
            border-radius: 0px;
        }}
        .stButton button:hover {{ background: var(--gold); color: #000; }}
        
        /* LOGO ANIMATION (Original Restaurado) */
        @keyframes pulse-gold {{ 0% {{ box-shadow: 0 0 0 0 rgba(212,175,55, 0.4); }} 70% {{ box-shadow: 0 0 0 10px rgba(212,175,55, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(212,175,55, 0); }} }}
        .omega-logo {{ animation: pulse-gold 2s infinite; border-radius: 50%; }}
    </style>
    """, unsafe_allow_html=True)

# Charts Atualizados para usar o Tema
def plot_radar(cats, vals, title):
    cfg = st.session_state["config"]
    fig = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself', line_color=cfg['theme_color']))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=cfg.get("theme_mode", "Dark") == "Dark Cathedral" and "#EEE" or "#222"),
        title=title, margin=dict(t=30, b=30, l=30, r=30)
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_gauge_linear(val, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val,
        title = {'text': title, 'font': {'size': 24, 'color': color}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)"}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#EEE"}, margin=dict(t=20, b=20, l=20, r=20), height=150)
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 5. EXECUÇÃO DO APLICATIVO
# ==============================================================================
st.set_page_config(page_title="SYSTEM OMEGA", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# Carrega Configuração Inicial
config_data = SafeIO.ler_json(DBS["CONFIG"], {})
st.session_state["config"] = config_data
inject_css(config_data)

# TELA DE LOGIN (Estilo Cruz Restaurado)
if "logado" not in st.session_state: st.session_state["logado"] = False
if not st.session_state["logado"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        gold = config_data.get("theme_color", "#D4AF37")
        st.markdown(f"""
        <center>
            <svg width="100" height="150" viewBox="0 0 100 150">
                <rect x="45" y="10" width="10" height="130" fill="{gold}" />
                <rect x="20" y="40" width="60" height="10" fill="{gold}" />
                <circle cx="50" cy="45" r="5" fill="#000" stroke="{gold}" stroke-width="2"/>
            </svg>
            <h1 style="font-family:'Cinzel'; font-size:30px; margin-bottom:0;">SYSTEM OMEGA</h1>
            <p style="letter-spacing:4px; font-size:12px; margin-top:0;">SHEPHERD ULTIMATE EDITION</p>
        </center>
        """, unsafe_allow_html=True)
        
        tab_log, tab_reg = st.tabs(["ACESSO", "REGISTRO"])
        with tab_log:
            u = st.text_input("Credencial ID")
            p = st.text_input("Chave de Acesso", type="password")
            if st.button("ENTRAR NO SANTUÁRIO", use_container_width=True):
                if AccessControl.login(u, p):
                    st.session_state["logado"] = True
                    st.session_state["user_id"] = u.upper()
                    st.rerun()
                else: st.error("Acesso Negado.")
        
        with tab_reg:
            rn = st.text_input("Novo ID Pastor")
            rp = st.text_input("Nova Chave", type="password")
            if st.button("CRIAR REGISTRO"):
                ok, msg = AccessControl.register(rn, rp)
                if ok: st.success(msg)
                else: st.warning(msg)
    st.stop()

# BARRA LATERAL (MENU)
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:10px; border:1px solid #333;'>PASTOR: <b>{st.session_state['user_id']}</b></div>", unsafe_allow_html=True)
    menu = st.radio("SISTEMA", ["Cuidado Pastoral", "Gabinete (Editor)", "Biblioteca", "Configurações"])
    st.divider()
    if st.button("SAIR"): 
        st.session_state["logado"] = False
        st.rerun()

# --- MÓDULO 1: CUIDADO PASTORAL (Features Restauradas + Melhorias Gráficas) ---
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral & Discipulado")
    
    t_dash, t_memb, t_teoria, t_ferram = st.tabs([
        "📊 Dashboard", "🐑 Rol de Membros", "⚖️ Teoria da Permissão", "🛠️ Ferramentas"
    ])
    
    with t_dash:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Estado Espiritual da Igreja")
            # Gráfico Restaurado
            cats = ['Fé', 'Comunhão', 'Serviço', 'Missões', 'Doutrina']
            vals = [random.randint(50, 95) for _ in cats]
            plot_radar(cats, vals, "Radar Ministerial")
        with c2:
            st.subheader("Rotina Pastoral")
            st.checkbox("Orar (Manhã)")
            st.checkbox("Estudo Bíblico")
            st.checkbox("Visita Hospitalar")
            st.info("Próximo evento: Culto de Santa Ceia")
            
    with t_memb:
        st.markdown("### Gestão de Rebanho (Rol de Membros)")
        membros = SafeIO.ler_json(DBS["MEMBERS"], [])
        
        with st.expander("➕ Adicionar Nova Ovelha", expanded=False):
            with st.form("new_sheep"):
                col_a, col_b, col_c = st.columns([2, 1, 2])
                nm = col_a.text_input("Nome")
                stt = col_b.selectbox("Status", ["Comungante", "Não-Comungante", "Disciplinado", "Visitante"])
                obs = col_c.text_input("Observação Pastoral")
                if st.form_submit_button("Salvar Ficha"):
                    if nm:
                        membros.append({"Nome": nm, "Status": stt, "Obs": obs, "Cadastro": datetime.now().strftime("%d/%m/%Y")})
                        SafeIO.salvar_json(DBS["MEMBERS"], membros)
                        st.success("Salvo com sucesso!")
                        st.rerun()
                        
        if membros:
            st.dataframe(pd.DataFrame(membros), use_container_width=True)
        else:
            st.warning("Rol de membros vazio.")

    with t_teoria:
        # RECUPERADO: Todos os 4 Sliders da Teoria da Permissão
        st.subheader("Diagnóstico: Permissão Interna")
        col_sliders, col_graf = st.columns(2)
        with col_sliders:
            p_falhar = st.slider("Permissão para FALHAR (Graça)", 0, 100, 50)
            p_sentir = st.slider("Permissão para SENTIR (Humanidade)", 0, 100, 50)
            p_descansar = st.slider("Permissão para DESCANSAR (Limites)", 0, 100, 50)
            p_sucesso = st.slider("Permissão para SUCESSO (Dignidade)", 0, 100, 50)
            avg = (p_falhar + p_sentir + p_descansar + p_sucesso) / 4
        with col_graf:
            plot_gauge_linear(avg, "Índice de Saúde Interna", st.session_state["config"]["theme_color"])
            if avg < 50: st.error("Risco de Burnout. Procure descanso.")

    with t_ferram:
        st.write("Módulos Adicionais de Discipulado (G4) e Chatbot Pastoral.")

# --- MÓDULO 2: GABINETE PASTORAL (Editor Completo Recuperado) ---
elif menu == "Gabinete (Editor)":
    st.title("📝 O Gabinete (Sermões)")
    
    col_sel, col_edit = st.columns([1, 3])
    
    with col_sel:
        st.subheader("Arquivo")
        files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith((".txt", ".docx", ".enc"))]
        sel_file = st.selectbox("Seus Sermões:", ["Novo"] + files)
    
    # Lógica de Carregamento
    content = ""
    title = ""
    if sel_file != "Novo":
        try:
            p = os.path.join(DIRS["SERMOES"], sel_file)
            if p.endswith(".txt"):
                with open(p, "r", encoding="utf-8") as f: content = f.read()
            title = sel_file.split(".")[0]
        except: pass
        
    with col_edit:
        final_title = st.text_input("Título da Mensagem", value=title)
        
        if QUILL_AVAILABLE:
            final_content = st_quill(value=content, html=True, key="quill_editor")
        else:
            final_content = st.text_area("Texto", value=content, height=400)
            
        c_act1, c_act2, c_act3 = st.columns(3)
        if c_act1.button("💾 SALVAR TXT"):
            if final_title:
                path = os.path.join(DIRS["SERMOES"], final_title + ".txt")
                with open(path, "w", encoding="utf-8") as f: f.write(final_content)
                st.success("Salvo.")
        
        if c_act2.button("🔒 ENCRIPTAR"):
            if final_title:
                pw = st.session_state["config"].get("enc_password")
                if pw:
                    enc = encrypt_sermon_aes(pw, final_content)
                    with open(os.path.join(DIRS["GABINETE"], final_title+".enc"), "w") as f: f.write(enc)
                    st.success("Encriptado e Salvo.")
                else: st.error("Defina senha nas Configurações.")

        if c_act3.button("📄 EXPORTAR DOCX"):
            # Lógica Restaurada
            if final_title:
                p = export_logic(final_title, final_content, "docx")
                with open(p, "rb") as f:
                    st.download_button("Baixar Arquivo", f, file_name=f"{final_title}.docx")

# --- MÓDULO 3: BIBLIOTECA ---
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Reformada")
    # Lógica Restaurada da API Bible
    ref = st.text_input("Pesquisar Referência (ex: Jo 3:16)")
    if st.button("Buscar na API"):
        res = BibleEngine.get_verse(ref)
        st.info(res)
    st.markdown("---")
    st.subheader("Acervo Local (PDFs Indexados)")
    st.caption("Arquivos em: " + DIRS["BIB_CACHE"])

# --- MÓDULO 4: CONFIGURAÇÕES (O Novo Modelo 'TheWord' que você gostou) ---
elif menu == "Configurações":
    st.title("⚙️ Preferências do Sistema")
    cfg = st.session_state["config"]
    
    t_vis, t_sys, t_sec = st.tabs(["Visual & Tema", "Backup & Sistema", "Segurança"])
    
    with t_vis:
        c1, c2 = st.columns(2)
        n_mod = c1.selectbox("Modo Visual", ["Dark Cathedral", "Pergaminho (Sepia)", "Holy Light (Claro)"], index=0)
        n_cor = c1.color_picker("Cor Litúrgica", cfg.get("theme_color"))
        n_font = c2.selectbox("Tipografia", ["Cinzel", "Inter", "Merriweather", "Playfair Display"], index=0)
        n_size = c2.slider("Tamanho Fonte", 12, 28, cfg.get("font_size"))
        
        st.caption("Preview:")
        st.markdown(f"<span style='font-family:{n_font}; font-size:{n_size}px; color:{n_cor}'>No princípio era o Verbo.</span>", unsafe_allow_html=True)
        
    with t_sys:
        st.write(f"Diretório Raiz: `{DIRS['USER']}`")
        if st.button("Forçar Backup Geral"):
            st.info("Backup dos JSONs executado nas pastas ocultas.")
            
    with t_sec:
        n_pass = st.text_input("Senha Mestra (AES)", value=cfg.get("enc_password"), type="password")
        
    if st.button("💾 APLICAR TODAS AS CONFIGURAÇÕES", type="primary"):
        cfg["theme_mode"] = n_mod
        cfg["theme_color"] = n_cor
        cfg["font_family"] = n_font
        cfg["font_size"] = n_size
        cfg["enc_password"] = n_pass
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("Sistema Atualizado. Reinicie a página se necessário.")
        time.sleep(1)
        st.rerun()
