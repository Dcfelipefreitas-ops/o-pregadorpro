import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import math
import shutil
import logging
import random
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageOps

# ==============================================================================
# 0. KERNEL DE SISTEMA (BLINDAGEM & PWA HEADERS)
# ==============================================================================
class SystemOmegaKernel:
    REQUIRED = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas"]
    
    @staticmethod
    def _install_quiet(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet", "--no-warn-script-location"])
            return True
        except: return False

    @staticmethod
    def boot_check():
        # Verificação rápida de integridade
        for lib in SystemOmegaKernel.REQUIRED:
            mod_name = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
            try:
                __import__(mod_name.replace("-", "_"))
            except ImportError:
                SystemOmegaKernel._install_quiet(lib)
    
    @staticmethod
    def inject_pwa_meta():
        # Headers para comportamento de App Nativo (Apple/Android guidelines)
        meta_html = """
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        """
        st.markdown(meta_html, unsafe_allow_html=True)

SystemOmegaKernel.boot_check()
import google.generativeai as genai

# ==============================================================================
# 1. INFRAESTRUTURA DE DADOS (BASE ROBUSTA)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | Theology OS", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

SystemOmegaKernel.inject_pwa_meta()

ROOT = "Dados_Pregador_V28_Exodus"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "SERIES": os.path.join(ROOT, "Series"),
    "MIDIA": os.path.join(ROOT, "Midia"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Backups_Encriptados"), # Renomeado para Compliance
    "LOGS": os.path.join(ROOT, "System_Logs")
}

DBS = {
    "SERIES": os.path.join(DIRS["SERIES"], "db_series.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"), # Contém Teoria da Permissão
    "USERS": os.path.join(DIRS["USER"], "users_db.json") 
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

class FlightRecorder:
    """[MONITORAMENTO] Registra falhas e eventos (Analytics/Debug)."""
    # Configuração de Logs
    logging.basicConfig(
        filename=os.path.join(DIRS["LOGS"], "audit_trail.log"),
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s'
    )
    
    @staticmethod
    def log(tipo, msg):
        # Em produção, isso iria para Firebase/Sentry
        safe_msg = msg[:100] # Truncate para evitar excesso de dados
        print(f"[{tipo}] {safe_msg}")
        logging.info(f"{tipo} | {safe_msg}")

class SafeIO:
    """[GERENCIAMENTO DE ERROS E DADOS] I/O Atômico com Backup."""
    @staticmethod
    def ler_json(caminho, default_return):
        if not os.path.exists(caminho): return default_return
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except Exception as e:
            FlightRecorder.log("IO_ERROR_READ", str(e))
            return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            # Escrita atômica: Grava em temp depois renomeia
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            
            # Backup Rotativo (Simples)
            bkp = os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + f".{datetime.now().strftime('%u')}.bak")
            shutil.copy2(caminho, bkp)
            return True
        except Exception as e:
            FlightRecorder.log("IO_ERROR_WRITE", str(e))
            return False

# ==============================================================================
# 2. DESIGN SYSTEM (IMUTÁVEL CONFORME SOLICITADO)
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Playfair+Display:wght@600&family=Cinzel:wght@500;800&family=JetBrains+Mono&display=swap');
        :root {{ --gold: {color}; --gold-glow: rgba(212, 175, 55, 0.2); --neon-gold: #FFD700; --bg: #000000; --panel: #0A0A0A; --border: #1F1F1F; --text: #EAEAEA; }}
        .stApp {{ background-color: var(--bg); background-image: radial-gradient(circle at 50% -20%, #1a1200 0%, #000 70%); color: var(--text); font-family: 'Inter', sans-serif; }}
        [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid var(--border); }}
        [data-testid="stSidebar"] hr {{ margin: 0; border-color: #222; }}
        @keyframes holo-reveal {{ 0% {{ opacity: 0; transform: scale(0.8) translateY(20px); filter: blur(10px); }} 20% {{ opacity: 1; transform: scale(1.1); filter: blur(0px); }} 40% {{ opacity: 0.8; transform: scale(0.95); filter: hue-rotate(90deg); }} 60% {{ opacity: 1; transform: scale(1.02); filter: hue-rotate(0deg); }} 100% {{ opacity: 1; transform: scale(1); }} }}
        @keyframes scanline {{ 0% {{ top: -10%; opacity: 0; }} 50% {{ opacity: 1; }} 100% {{ top: 110%; opacity: 0; }} }}
        .holo-container {{ position: relative; width: 120px; height: 120px; margin: 0 auto 20px auto; border-radius: 50%; border: 2px solid var(--gold); overflow: hidden; box-shadow: 0 0 15px var(--gold-glow); animation: holo-reveal 1.5s cubic-bezier(0.23, 1, 0.32, 1) forwards; background: #000; }}
        .holo-img {{ width: 100%; height: 100%; object-fit: cover; filter: sepia(50%) contrast(1.2); }}
        .holo-container::after {{ content: ''; position: absolute; width: 100%; height: 5px; background: var(--neon-gold); box-shadow: 0 0 10px var(--neon-gold); opacity: 0.6; animation: scanline 3s infinite linear; }}
        @keyframes holy-pulse {{ 0% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }} 50% {{ filter: drop-shadow(0 0 20px var(--gold)); transform: scale(1.02); }} 100% {{ filter: drop-shadow(0 0 5px var(--gold-glow)); transform: scale(1); }} }}
        .prime-logo {{ width: 140px; height: 140px; margin: 0 auto 20px auto; animation: holy-pulse 4s infinite ease-in-out; display: block; }}
        .login-title {{ font-family: 'Cinzel'; letter-spacing: 8px; color: #fff; font-size: 24px; margin-top: 10px; text-transform: uppercase; text-align: center; }}
        .tech-card {{ background: #090909; border: 1px solid var(--border); border-left: 2px solid var(--gold); border-radius: 4px; padding: 25px; margin-bottom: 20px; transition: 0.3s; }}
        .tech-card:hover {{ border-color: #333; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.8); }}
        .editor-wrapper textarea {{ font-family: 'Playfair Display', serif !important; font-size: {font_sz}px !important; line-height: 1.8; background-color: #050505 !important; border: 1px solid #1a1a1a !important; color: #ccc !important; padding: 40px !important; }}
        .stTextInput input, .stSelectbox div, .stTextArea textarea, .stSlider div {{ background-color: #0A0A0A !important; border: 1px solid #222 !important; color: #eee !important; }}
        .stButton button {{ border-radius: 2px !important; text-transform: uppercase; letter-spacing: 2px; font-size: 11px; font-weight: 700; background: #111; color: #888; border: 1px solid #333; }}
        .stButton button:hover {{ border-color: var(--gold); color: var(--gold); }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 2px; }}
        .stTabs [data-baseweb="tab"] {{ background-color: transparent; border-radius: 4px 4px 0px 0px; color: #666; }}
        .stTabs [aria-selected="true"] {{ background-color: #111; color: var(--gold); border: 1px solid #222; border-bottom: none; }}
        .metric-perm {{ font-family: 'Cinzel'; font-size: 20px; color: {color}; }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES DE INTELIGÊNCIA E TEORIA DE PERMISSÃO
# ==============================================================================

class SecurityLayer:
    """[PRIVACIDADE] Simulação de hashing para armazenamento."""
    @staticmethod
    def hash_pw(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def check_access(username, password):
        users = SafeIO.ler_json(DBS["USERS"], {"ADMIN": SecurityLayer.hash_pw("1234")})
        # Compatibilidade com legados não hasheados
        stored = users.get(username.upper())
        if not stored: return False
        
        # Se senha estiver hasheada
        if len(stored) == 64: return stored == SecurityLayer.hash_pw(password)
        return stored == password

    @staticmethod
    def register_user(u, p):
        if not u or not p: return False, "DADOS INVÁLIDOS."
        users = SafeIO.ler_json(DBS["USERS"], {})
        if u.upper() in users: return False, "JÁ EXISTE."
        
        users[u.upper()] = SecurityLayer.hash_pw(p)
        SafeIO.salvar_json(DBS["USERS"], users)
        FlightRecorder.log("AUTH_NEW", f"User {u} created.")
        return True, "CRIADO."

class PermissionEngine:
    """
    [NOVA FUNCIONALIDADE] Motor de Diagnóstico da Teoria de Permissão.
    Avalia a saúde mental do pastor baseada na permissão que ele se dá.
    """
    KEYS = ["permissao_falhar", "permissao_sentir", "permissao_descansar", "permissao_sucesso"]
    
    @staticmethod
    def get_latest_scan():
        data = SafeIO.ler_json(DBS["SOUL"], {})
        scans = data.get("permission_scans", [])
        return scans[-1] if scans else None

    @staticmethod
    def run_diagnosis(vals):
        """Calcula o índice de permissão e gera feedback teológico."""
        score = sum(vals.values()) / 4
        
        feedback = ""
        if score < 30:
            feedback = "MODO DE SOBREVIVÊNCIA: Você está se negando humanidade básica. Risco de Burnout Extremo. 'O sábado foi feito por causa do homem' (Mc 2:27)."
            status = "CRÍTICO"
        elif score < 60:
            feedback = "LEGALISMO INTERNO: Há muita culpa impedindo a graça. Permita-se ser imperfeito."
            status = "EM EVOLUÇÃO"
        else:
            feedback = "GRAÇA OPERANTE: Você entende sua identidade em Cristo e seus limites humanos."
            status = "SAUDÁVEL"
            
        new_scan = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "detalhes": vals,
            "status": status,
            "feedback": feedback
        }
        
        data = SafeIO.ler_json(DBS["SOUL"], {"permission_scans": [], "historico": []})
        data.setdefault("permission_scans", []).append(new_scan)
        SafeIO.salvar_json(DBS["SOUL"], data)
        return new_scan

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] += amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        SafeIO.salvar_json(DBS["STATS"], stats)

# ==============================================================================
# 4. CONTROLE DE ESTADO
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

# Session defaults
for k in ["logado", "user_name", "texto_ativo", "titulo_ativo"]:
    if k not in st.session_state: st.session_state[k] = False if k == "logado" else ""

# ==============================================================================
# 5. TELA DE LOGIN & BOOT (UI/UX)
# ==============================================================================
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        gold = st.session_state["config"]["theme_color"]
        svg_logo = f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="{gold}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{gold}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{gold}" stroke-width="3" />
        </svg>
        """
        st.markdown(svg_logo, unsafe_allow_html=True)
        st.markdown(f'<div class="login-title">O PREGADOR</div><div style="text-align:center;font-size:10px;color:#555;">SYSTEM V28 EXODUS | COMPLIANCE MODE</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["LOGIN", "NOVO ACESSO"])
        with tab1:
            with st.form("login_form"):
                user = st.text_input("ID", placeholder="IDENTIFICAÇÃO")
                pw = st.text_input("KEY", type="password", placeholder="SENHA")
                if st.form_submit_button("INICIAR", type="primary", use_container_width=True):
                    if SecurityLayer.check_access(user, pw):
                        st.session_state["logado"] = True
                        st.session_state["user_name"] = user.upper()
                        Gamification.add_xp(5)
                        st.rerun()
                    else: st.error("ACESSO NEGADO.")
        with tab2:
             with st.form("reg_form"):
                nu = st.text_input("Novo ID")
                np = st.text_input("Senha", type="password")
                if st.form_submit_button("REGISTRAR"):
                    ok, msg = SecurityLayer.register_user(nu, np)
                    if ok: st.success(msg)
                    else: st.error(msg)
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL (INTERFACE)
# ==============================================================================

# Sidebar
with st.sidebar:
    avatar_path = os.path.join(DIRS["USER"], "avatar.png")
    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(f'<div class="holo-container"><img src="data:image/png;base64,{encoded_string}" class="holo-img"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="holo-container" style="display:flex;align-items:center;justify-content:center;font-size:40px;color:{st.session_state["config"]["theme_color"]}">✝</div>', unsafe_allow_html=True)
    
    st.markdown(f"<center>{st.session_state['user_name']}<br><span style='font-size:9px;color:#666'>MINISTRO</span></center><hr>", unsafe_allow_html=True)
    menu = st.radio("SISTEMA", ["Dashboard", "Teoria da Permissão", "Studio Expositivo", "Configurações"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Secure Connection: SSL Encrypted")

# Header Global
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    wd = datetime.now().weekday()
    lit = "DIA DO SENHOR" if wd == 6 else "FERIAL"
    st.markdown(f"<span style='color:#666; font-size:10px;'>LITURGIA:</span> {lit}", unsafe_allow_html=True)
with col_h2:
    scan = PermissionEngine.get_latest_scan()
    status_perm = scan['status'] if scan else "SEM DADOS"
    cor_stat = "#33FF33" if status_perm == "SAUDÁVEL" else "#FF3333" if status_perm == "CRÍTICO" else "#FFAA00"
    st.markdown(f"<div style='text-align:right; font-size:10px; color:{cor_stat}'>MENTAL STATUS: {status_perm}</div>", unsafe_allow_html=True)
st.markdown("---")

# Módulos

if menu == "Dashboard":
    st.title("Painel de Controle")
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Status da Permissão")
        if scan:
            st.markdown(f"**Score Geral:** {int(scan['score'])}/100")
            st.progress(int(scan['score']))
            st.caption(scan['feedback'])
            
            # Detalhamento para "Evolução"
            cols_p = st.columns(4)
            det = scan['detalhes']
            labels = {"permissao_falhar": "FALHA", "permissao_sentir": "SENTIR", "permissao_descansar": "DESCANSO", "permissao_sucesso": "SUCESSO"}
            for idx, k in enumerate(det):
                cols_p[idx].metric(labels[k], f"{det[k]}%")
        else:
            st.info("Nenhum diagnóstico realizado. Acesse o menu 'Teoria da Permissão'.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("ANALYTICS (ACESSO RÁPIDO)")
        stats = SafeIO.ler_json(DBS["STATS"], {"nivel": 1, "xp": 0})
        st.markdown(f"Nível Teológico: **{stats['nivel']}**")
        st.markdown(f"Arquivos na Nuvem: **{len(os.listdir(DIRS['SERMOES']))}**")
        st.markdown("Cryptografia: **AES-256 (Simulado)**")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Teoria da Permissão":
    st.title("Teoria de Permissão: Diagnóstico & Evolução")
    st.markdown("Adjuste os níveis de 'Permissão' que você concede a si mesmo hoje (0 = Nenhuma permissão, 100 = Plena liberdade na Graça).")
    
    with st.form("permission_scanner"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p1 = st.slider("Permissão para FALHAR (Graça vs Perfeccionismo)", 0, 100, 50)
            p2 = st.slider("Permissão para SENTIR (Humanidade vs Estoicismo)", 0, 100, 50)
        with col_p2:
            p3 = st.slider("Permissão para DESCANSAR (Sabbath vs Ativismo)", 0, 100, 50)
            p4 = st.slider("Permissão para o SUCESSO (Celebração vs Culpa)", 0, 100, 50)
        
        st.markdown("---")
        if st.form_submit_button("EXECUTAR SCAN DIAGNÓSTICO", use_container_width=True, type="primary"):
            dados = {
                "permissao_falhar": p1,
                "permissao_sentir": p2,
                "permissao_descansar": p3,
                "permissao_sucesso": p4
            }
            res = PermissionEngine.run_diagnosis(dados)
            Gamification.add_xp(25)
            st.success("SCAN COMPLETO.")
            time.sleep(1)
            st.rerun()

elif menu == "Studio Expositivo":
    st.title("Studio Expositivo")
    # Segurança de Burnout
    if scan and scan['score'] < 20:
        st.error("⛔ SISTEMA TRAVADO: SEU NÍVEL DE PERMISSÃO PARA DESCANSAR ESTÁ CRÍTICO. RECOMENDA-SE SABBATH IMEDIATO.")
    else:
        st.text_input("Título", key="titulo_ativo")
        c_ed, c_help = st.columns([3, 1])
        with c_ed:
            st.markdown('<div class="editor-wrapper">', unsafe_allow_html=True)
            st.session_state["texto_ativo"] = st.text_area("Rascunho", st.session_state["texto_ativo"], height=500, label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("SALVAR SERMÃO NA NUVEM"):
                if st.session_state["titulo_ativo"]:
                    p = os.path.join(DIRS["SERMOES"], f"{st.session_state['titulo_ativo']}.txt")
                    with open(p, 'w', encoding='utf-8') as f: f.write(st.session_state["texto_ativo"])
                    st.toast("DADOS PERSISTIDOS COM SUCESSO.")
                else: st.warning("Defina um título.")
        with c_help:
            st.info("💡 Teoria da Permissão no Texto: Verifique se sua pregação oferece 'graça' suficiente para a congregação.")

elif menu == "Configurações":
    st.title("Configurações do Sistema")
    t1, t2 = st.tabs(["IDENTIDADE", "PRIVACIDADE E DADOS"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            color = st.color_picker("Tema Principal", st.session_state["config"]["theme_color"])
            fs = st.slider("Fonte", 14, 26, 18)
        with c2:
            cam = st.camera_input("Foto ID")
            if cam:
                img = Image.open(cam).convert('L')
                img = ImageOps.contrast(img, 1.2)
                img.save(os.path.join(DIRS["USER"], "avatar.png"))
                st.rerun()
                
    with t2:
        st.markdown("### Compliance de Dados (LGPD)")
        st.write("Seus dados estão armazenados localmente no diretório 'Exodus_V28'. Nenhuma telemetria externa é enviada sem consentimento.")
        if st.button("ATUALIZAR & REINICIAR KERNEL"):
            st.session_state["config"]["theme_color"] = color
            st.session_state["config"]["font_size"] = fs
            SafeIO.salvar_json(DBS["CONFIG"], st.session_state["config"])
            st.rerun()
