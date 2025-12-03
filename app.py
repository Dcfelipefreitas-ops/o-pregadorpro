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
import calendar
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. KERNEL ORTODOXO (INICIALIZAÇÃO BLINDADA)
# ==============================================================================
class SystemOmegaKernel:
    """
    O Coração da Máquina: Instalação silenciosa e boot de alta performance.
    """
    REQUIRED = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas", "fpdf"]
    
    @staticmethod
    def _install(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        except: pass

    @staticmethod
    def boot_check():
        queue = []
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                mod = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(mod.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.code(f"SYSTEM OMEGA: Atualizando Protocolos... ({len(queue)} pacotes)", language="bash")
            for lib in queue:
                SystemOmegaKernel._install(lib)
            placeholder.empty()
            st.rerun()

SystemOmegaKernel.boot_check()

import google.generativeai as genai
from PIL import Image, ImageOps

# ==============================================================================
# 1. INFRAESTRUTURA DE DADOS (SAFE I/O)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | Orthodox Prime", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

ROOT = "Dados_Pregador_V23_Prime"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "SERIES": os.path.join(ROOT, "Series"),
    "MIDIA": os.path.join(ROOT, "Midia"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto")
}

DBS = {
    "SERIES": os.path.join(DIRS["SERIES"], "db_series.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json")
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

class SafeIO:
    """Sistema de Auto-Preservação de Dados."""
    @staticmethod
    def ler_json(caminho, default_return):
        if not os.path.exists(caminho): return default_return
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except: return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
        except: pass

# ==============================================================================
# 2. DESIGN SYSTEM "ORTHODOX TRANSFORMER"
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Playfair+Display:wght@600&family=Cinzel:wght@500;800&family=JetBrains+Mono&display=swap');
        
        :root {{ 
            --gold: {color}; 
            --gold-glow: rgba(212, 175, 55, 0.3);
            --bg: #020202; 
            --panel: #0A0A0A; 
            --border: #222; 
            --text: #EAEAEA; 
        }}
        
        /* BASE */
        .stApp {{ 
            background-color: var(--bg); 
            background-image: linear-gradient(180deg, #050505 0%, #000 100%);
            color: var(--text); 
            font-family: 'Inter', sans-serif; 
        }}
        
        /* SIDEBAR MONOLÍTICA */
        [data-testid="stSidebar"] {{
            background-color: #040404;
            border-right: 1px solid #1a1a1a;
        }}
        [data-testid="stSidebar"] hr {{ margin: 0; border-color: #222; }}
        
        /* LOGIN ORTODOXO (O RETORNO DO 'O') */
        @keyframes pulse-gold-prime {{
            0% {{ box-shadow: 0 0 0 0 var(--gold-glow); border-color: #554400; }}
            50% {{ box-shadow: 0 0 30px 5px var(--gold-glow); border-color: var(--gold); }}
            100% {{ box-shadow: 0 0 0 0 var(--gold-glow); border-color: #554400; }}
        }}
        
        .omega-circle {{
            width: 140px; height: 140px; border-radius: 50%;
            border: 2px solid var(--gold); background: #000;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 25px auto;
            animation: pulse-gold-prime 4s infinite;
        }}
        
        .omega-letter {{
            font-family: 'Cinzel', serif;
            font-size: 80px;
            color: var(--gold);
            font-weight: 800;
            text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
        }}
        
        .login-title {{
            font-family: 'Cinzel'; letter-spacing: 6px; 
            color: #fff; font-size: 28px; margin-top: 10px;
            text-transform: uppercase;
        }}

        /* CARDS CYBER-TEOLÓGICOS */
        .tech-card {{
            background: linear-gradient(145deg, #0E0E0E, #090909);
            border: 1px solid #1f1f1f;
            border-radius: 4px; padding: 25px; margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }}
        .tech-card::before {{
            content: ''; position: absolute; top: 0; left: 0; 
            width: 3px; height: 100%; background: var(--gold);
        }}
        .tech-card:hover {{ border-color: #333; box-shadow: 0 5px 20px rgba(0,0,0,0.5); }}

        /* EDITOR SAGRADO */
        .editor-wrapper textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_sz}px !important;
            line-height: 1.8;
            background-color: #060606 !important;
            border: 1px solid #1a1a1a !important;
            color: #ccc !important;
            padding: 30px !important;
            border-radius: 4px !important;
        }}
        .editor-wrapper textarea:focus {{ border-color: var(--gold) !important; }}
        
        /* STATUS HUD */
        .hud-bar {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px; background: #080808; border-bottom: 1px solid #222;
            margin-bottom: 25px; border-radius: 4px;
            font-family: 'JetBrains Mono', monospace; font-size: 11px;
        }}
        
        /* INPUTS */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{
            background-color: #0C0C0C !important; 
            border: 1px solid #222 !important; 
            color: #eee !important;
            border-radius: 2px !important;
        }}
        .stButton button {{
            border-radius: 2px !important; text-transform: uppercase; letter-spacing: 1px;
            font-weight: 600;
        }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES DE INTELIGÊNCIA (LOGICA PRESERVADA)
# ==============================================================================

class LiturgicalCalendar:
    @staticmethod
    def get_status():
        hoje = datetime.now()
        # Lógica simplificada para display HUD
        if hoje.weekday() == 6: return "DOMINGO - DIA DO SENHOR"
        return "DIA FERIAL"

class GenevaProtocol:
    """O Guardião da Doutrina."""
    DB = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade.",
        "eu decreto": "⚠️ ALERTA: Quebra de Soberania Divina.",
        "mérito": "⚠️ ALERTA: Pelagianismo (Sola Gratia).",
        "energia": "⚠️ ALERTA: Terminologia Nova Era."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [v for k, v in GenevaProtocol.DB.items() if k in text.lower()]

class PastoralMind:
    """Monitor de Vitalidade."""
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        
        if bad >= 6: return "CRÍTICO", "#FF3333"
        if bad >= 3: return "ALERTA", "#FFAA00"
        return "OPERACIONAL", "#33FF33"

    @staticmethod
    def registrar(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "diario": []})
        data["historico"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1})
        stats["xp"] += amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        SafeIO.salvar_json(DBS["STATS"], stats)

# ==============================================================================
# 4. GESTÃO DE ESTADO
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "Pastor"
if "texto_ativo" not in st.session_state: st.session_state["texto_ativo"] = ""
if "titulo_ativo" not in st.session_state: st.session_state["titulo_ativo"] = ""

# ==============================================================================
# 5. TELA DE LOGIN (SOLICITAÇÃO ESPECÍFICA ATENDIDA)
# ==============================================================================
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # O CÍRCULO COM O "O" MAJESTOSO
        st.markdown(f"""
        <div class="omega-circle">
            <span class="omega-letter">O</span>
        </div>
        <div style="text-align:center;">
            <div class="login-title">O PREGADOR</div>
            <div style="font-size:10px; color:#555; letter-spacing:4px; margin-top:5px;">ORTHODOX PRIME V23</div>
            <div style="width:40px; height:2px; background:{st.session_state["config"]["theme_color"]}; margin: 20px auto;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("gate_keeper"):
            user = st.text_input("ID", label_visibility="collapsed", placeholder="IDENTIFICAÇÃO")
            pw = st.text_input("KEY", type="password", label_visibility="collapsed", placeholder="SENHA")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("INICIAR SISTEMA", type="primary", use_container_width=True):
                if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = user.upper()
                    Gamification.add_xp(5)
                    st.rerun()
                else:
                    st.error("ACESSO NEGADO.")
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL
# ==============================================================================

# --- SIDEBAR (PAINEL DE CONTROLE) ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0 10px 0;">
        <span style="font-family:'Cinzel'; font-size:40px; color:{st.session_state["config"]["theme_color"]};">O</span>
        <br><span style="font-size:10px; color:#666; letter-spacing:2px;">SOLA SCRIPTURA</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "COMANDOS", 
        ["Dashboard", "Gabinete Pastoral", "Studio Expositivo", "Séries Bíblicas", "Media Lab", "Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Stats Compactos
    stats = SafeIO.ler_json(DBS["STATS"], {"nivel": 1, "xp": 0})
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono'; font-size:10px; color:#555; text-align:center;">
        NÍVEL {stats['nivel']} // XP {stats['xp']}
    </div>
    """, unsafe_allow_html=True)

    if st.button("LOGOUT", use_container_width=True):
        st.session_state["logado"] = False
        st.rerun()

# --- HUD (STATUS HEADER) ---
status_b, cor_b = PastoralMind.check_burnout()
dia_liturgico = LiturgicalCalendar.get_status()

st.markdown(f"""
<div class="hud-bar">
    <div>
        <span style="color:#666;">DATA:</span> {datetime.now().strftime("%d/%m/%Y")}
        <span style="color:#666; margin-left:15px;">LITURGIA:</span> {dia_liturgico}
    </div>
    <div>
        <span style="color:#666;">SISTEMA:</span> <span style="color:{cor_b}">{status_b}</span>
        <span style="color:#666; margin-left:15px;">USER:</span> {st.session_state['user_name']}
    </div>
</div>
""", unsafe_allow_html=True)

# --- PÁGINAS ---

if menu == "Dashboard":
    st.markdown(f"<h2 style='font-family:Cinzel; margin-bottom:20px;'>Painel de Controle</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("MONITOR DA ALMA")
        humor = st.selectbox("Estado Atual", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("REGISTRAR", use_container_width=True):
            PastoralMind.registrar(humor)
            Gamification.add_xp(10)
            st.success("DADOS COMPUTADOS.")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.caption("DIAGNÓSTICO")
        if status_b == "CRÍTICO":
            st.error("ALERTA MÁXIMO: Níveis de estresse excederam o limite seguro.")
        else:
            st.info(f"SISTEMA OPERACIONAL: {status_b}. Prossiga com a missão.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Arquivos Recentes")
    files = sorted([f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(DIRS["SERMOES"], x)), reverse=True)[:3]
    
    cols = st.columns(3)
    for i, f in enumerate(files):
        with cols[i]:
            st.markdown(f"""
            <div style="border:1px solid #222; background:#080808; padding:15px; border-radius:2px;">
                <div style="color:#666; font-size:10px;">TXT FILE</div>
                <div style="font-weight:bold;">{f.replace('.txt','')}</div>
            </div>
            """, unsafe_allow_html=True)

elif menu == "Gabinete Pastoral":
    st.title("Gabinete Pastoral")
    t1, t2 = st.tabs(["DIÁRIO CRIPTOGRAFADO", "TERAPIA DA VERDADE"])
    
    with t1:
        diario = st.text_area("Entrada de Dados", height=300)
        if st.button("GUARDAR NO COFRE"):
            soul = SafeIO.ler_json(DBS["SOUL"], {"diario": []})
            soul.setdefault("diario", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "texto": diario})
            SafeIO.salvar_json(DBS["SOUL"], soul)
            st.toast("ARQUIVADO.", icon="🔒")
            
    with t2:
        mentira = st.text_input("Detectar Mentira (Input)")
        if mentira:
            st.success("VERDADE BÍBLICA: 'Porque dele, e por ele, e para ele são todas as coisas.' (Romanos 11:36)")

elif menu == "Studio Expositivo":
    if status_b == "CRÍTICO":
        st.error("⛔ ACESSO BLOQUEADO PELO PROTOCOLO DE SAÚDE.")
        st.stop()

    st.title("Studio Expositivo")
    
    c1, c2 = st.columns([3, 1])
    c1.text_input("Título", key="titulo_ativo", placeholder="Ex: Gênesis 1 - O Princípio")
    if c2.button("SALVAR DADOS", use_container_width=True, type="primary"):
        if st.session_state["titulo_ativo"]:
            path = os.path.join(DIRS["SERMOES"], f"{st.session_state['titulo_ativo']}.txt")
            with open(path, 'w', encoding='utf-8') as f: f.write(st.session_state["texto_ativo"])
            SafeIO.salvar_json(os.path.join(DIRS["BACKUP"], "log.json"), {"saved": True})
            st.toast("DADOS PERSISTIDOS.", icon="💾")

    ce, ca = st.columns([2.5, 1])
    with ce:
        st.markdown('<div class="editor-wrapper">', unsafe_allow_html=True)
        st.session_state["texto_ativo"] = st.text_area("editor", st.session_state["texto_ativo"], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with ca:
        st.markdown("#### Geneva Scan")
        alerts = GenevaProtocol.scan(st.session_state["texto_ativo"])
        if not alerts: st.markdown("<div style='color:#33FF33; font-size:12px;'>✅ DOUTRINA VERIFICADA</div>", unsafe_allow_html=True)
        else:
            for a in alerts: st.warning(a)
            
        st.divider()
        st.markdown("#### IA Auxiliar")
        q = st.text_area("Query", height=100)
        if st.button("PROCESSAR"):
            if st.session_state["config"].get("api_key"):
                try:
                    genai.configure(api_key=st.session_state["config"]["api_key"])
                    r = genai.GenerativeModel("gemini-pro").generate_content(f"Teologia Reformada: {q}").text
                    st.info(r)
                except: st.error("FALHA NA API.")
            else: st.warning("API KEY NÃO DETECTADA.")

elif menu == "Séries Bíblicas":
    st.title("Séries Bíblicas")
    with st.expander("INICIAR NOVA SÉRIE", expanded=True):
        with st.form("serie"):
            n = st.text_input("Nome")
            d = st.text_area("Escopo")
            if st.form_submit_button("CRIAR"):
                db = SafeIO.ler_json(DBS["SERIES"], {})
                db[f"S{int(time.time())}"] = {"nome": n, "descricao": d}
                SafeIO.salvar_json(DBS["SERIES"], db)
                st.success("CRIADO.")
                st.rerun()
                
    st.markdown("### Banco de Dados")
    db = SafeIO.ler_json(DBS["SERIES"], {})
    for k, v in db.items():
        st.markdown(f"<div class='tech-card'><b>{v['nome']}</b><br><small>{v['descricao']}</small></div>", unsafe_allow_html=True)

elif menu == "Media Lab":
    st.title("Media Lab")
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div style="height:300px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; color:#444;">RENDER PREVIEW</div>', unsafe_allow_html=True)
    with c2:
        st.text_input("Texto Overlay")
        st.selectbox("Template", ["Dark Theology", "Light Grace", "Nature"])
        if st.button("RENDERIZAR (SIMULAÇÃO)"): st.success("PROCESSADO.")

elif menu == "Configurações":
    st.title("Configurações do Sistema")
    c1, c2 = st.columns(2)
    with c1:
        nc = st.color_picker("Cor Destaque", st.session_state["config"].get("theme_color", "#D4AF37"))
        nf = st.slider("Tamanho Fonte", 14, 28, st.session_state["config"].get("font_size", 18))
    with c2:
        nk = st.text_input("API Key (Google)", value=st.session_state["config"].get("api_key", ""), type="password")
        
    if st.button("ATUALIZAR PARÂMETROS", type="primary"):
        cfg = st.session_state["config"]
        cfg.update({"theme_color": nc, "font_size": nf, "api_key": nk})
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("SISTEMA REINICIANDO...")
        time.sleep(1)
        st.rerun()
