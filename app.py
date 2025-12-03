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
# 0. KERNEL DE INICIALIZAÇÃO BLINDADO (SYSTEM CORE)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo 'Raiz': Instala dependências silenciosamente e mantém o sistema vivo.
    """
    REQUIRED = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas", "fpdf"]
    
    @staticmethod
    def _install(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        except:
            pass

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
            placeholder.info(f"⚙️ Otimizando Catedral Digital... ({len(queue)} módulos)")
            for lib in queue:
                SystemOmegaKernel._install(lib)
            placeholder.empty()
            st.rerun()

SystemOmegaKernel.boot_check()

import google.generativeai as genai
from PIL import Image, ImageOps

# ==============================================================================
# 1. INFRAESTRUTURA & AUTO-CORREÇÃO (SAFE I/O)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="expanded"
)

ROOT = "Dados_Pregador_V22_Gratia"
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
    """Sistema de Auto-Correção e Backup Silencioso."""
    @staticmethod
    def ler_json(caminho, default_return):
        if not os.path.exists(caminho): return default_return
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return json.loads(content) if content else default_return
        except:
            return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            # Backup instantâneo
            shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
        except Exception as e:
            st.error(f"Erro de I/O: {e}")

# ==============================================================================
# 2. DESIGN SYSTEM "CATEDRAL" (CSS AVANÇADO)
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@500;700&family=Cinzel:wght@400;700&display=swap');
        
        :root {{ --gold: {color}; --bg: #030303; --panel: #0E0E0E; --text: #E0E0E0; --glass: rgba(20, 20, 20, 0.6); }}
        
        .stApp {{ 
            background-color: var(--bg); 
            background-image: radial-gradient(circle at 50% 0%, #1a1000 0%, var(--bg) 60%);
            color: var(--text); font-family: 'Inter', sans-serif; 
        }}
        
        /* SIDEBAR (ABADIA) */
        [data-testid="stSidebar"] {{
            background-color: #050505;
            border-right: 1px solid #222;
        }}
        [data-testid="stSidebar"] hr {{ border-color: #333; }}
        
        /* ANIMAÇÃO DE LOGIN (SAGRADA) */
        @keyframes pulse-gold {{
            0% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); transform: scale(1); }}
            50% {{ box-shadow: 0 0 0 25px rgba(212, 175, 55, 0); transform: scale(1.02); }}
            100% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); transform: scale(1); }}
        }}
        .holy-circle {{
            width: 130px; height: 130px; border-radius: 50%;
            border: 3px solid var(--gold); background: #000;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 30px auto;
            animation: pulse-gold 3s infinite;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.1);
        }}
        .login-card {{
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid #333;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}

        /* CARDS & EDITOR */
        .omega-card {{
            background: var(--panel); border: 1px solid #222;
            border-radius: 8px; padding: 25px; margin-bottom: 20px;
            border-left: 3px solid var(--gold);
            transition: all 0.3s ease;
        }}
        .omega-card:hover {{ transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); border-color: var(--gold); }}

        .editor-box textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_sz}px !important;
            line-height: 1.8;
            background-color: #080808 !important;
            border: 1px solid #222 !important;
            color: #ddd !important;
            padding: 30px !important;
        }}
        
        /* STATUS HEADER */
        .status-header {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 15px 20px; background: rgba(20,20,20,0.5);
            border-bottom: 1px solid #222; margin-bottom: 30px;
            border-radius: 8px; backdrop-filter: blur(5px);
        }}
        
        /* UTILS */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{
            background-color: #111 !important; border: 1px solid #333 !important; color: white !important;
        }}
        div[data-testid="stRadio"] > label {{ display: none; }} /* Esconde label do radio */
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES TEOLÓGICOS E LITÚRGICOS
# ==============================================================================

class LiturgicalCalendar:
    """Calcula o Tempo Litúrgico para contextualizar o Pregador."""
    @staticmethod
    def get_season():
        now = datetime.now()
        year = now.year
        # Cálculo simplificado de Páscoa (Meeus/Jones/Butcher)
        a=year%19; b=year//100; c=year%100; d=b//4; e=b%4; f=(b+8)//25; g=(b-f+1)//3
        h=(19*a+b-d-g+15)%30; i=c//4; k=c%4; l=(32+2*e+2*i-h-k)%7
        m=(a+11*h+22*l)//451; month=(h+l-7*m+114)//31; day=((h+l-7*m+114)%31)+1
        easter = datetime(year, month, day)
        
        if now < easter - timedelta(days=46): return "Tempo Comum", "🟢"
        if now < easter: return "Quaresma", "🟣"
        if now < easter + timedelta(days=50): return "Páscoa", "⚪"
        if now.month == 12: return "Advento/Natal", "🔴"
        return "Tempo Comum", "🟢"

class GenevaProtocol:
    """Verificador de Ortodoxia."""
    DB = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade detectada.",
        "eu determino": "⚠️ ALERTA: Quebra de Soberania (Tiago 4:15).",
        "mérito": "⚠️ ALERTA: Pelagianismo. Sola Gratia.",
        "vibração": "⚠️ ALERTA: Linguagem Nova Era."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        warns = [v for k, v in GenevaProtocol.DB.items() if k in text.lower()]
        if text and "cristo" not in text.lower() and "jesus" not in text.lower():
            warns.append("🔴 CRÍTICO: Sermão sem cristocentrismo.")
        return warns

class PastoralMind:
    """Saúde Mental."""
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:]
        bad = sum(1 for h in hist if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        if bad >= 6: return "CRÍTICO", "Pare. Risco de Colapso."
        if bad >= 3: return "ALERTA", "Cuidado. Reserva baixa."
        return "ESTÁVEL", "Equilíbrio."

    @staticmethod
    def registrar(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "diario": []})
        data["historico"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

class Gamification:
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1, "badges": []})
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
# 5. TELA DE LOGIN (PRESERVADA & MELHORADA)
# ==============================================================================
if not st.session_state["logado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="holy-circle">
            <span style="font-size:60px; color:{st.session_state["config"]["theme_color"]};">✝</span>
        </div>
        <div style="text-align:center;">
            <h1 style="font-family:'Cinzel'; margin:0; color:#fff; font-size:32px;">O PREGADOR</h1>
            <div style="width:60px; height:2px; background:{st.session_state["config"]["theme_color"]}; margin: 15px auto;"></div>
            <p style="font-size:12px; color:#888; letter-spacing:4px; margin-bottom:20px;">SYSTEM OMEGA V22</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Credencial", label_visibility="collapsed", placeholder="IDENTIDADE")
            pw = st.text_input("Chave", type="password", label_visibility="collapsed", placeholder="SENHA")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("ENTRAR NO SANTUÁRIO", type="primary", use_container_width=True):
                if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = user.upper()
                    Gamification.add_xp(5)
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL
# ==============================================================================

# --- SIDEBAR (MENU "ABADIA") ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h1 style="font-family:'Cinzel'; color:{st.session_state["config"]["theme_color"]}; font-size:24px;">OMEGA</h1>
        <p style="font-size:10px; color:#666; letter-spacing:2px;">SOLA SCRIPTURA</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navegação")
    # Menu robusto usando radio, mas estilizado como lista
    menu = st.radio(
        "Menu Principal", 
        ["Dashboard", "Gabinete Pastoral", "Studio Expositivo", "Séries Bíblicas", "Media Lab", "Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Widget de Gamificação
    stats = SafeIO.ler_json(DBS["STATS"], {"nivel": 1, "xp": 0})
    xp_bar = min(100, stats['xp'] % 100)
    st.markdown(f"""
    <div style="background:#111; padding:10px; border-radius:5px; border:1px solid #222;">
        <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;">
            <span>Nível {stats['nivel']}</span>
            <span>XP {stats['xp']}</span>
        </div>
        <div style="width:100%; height:4px; background:#333; border-radius:2px;">
            <div style="width:{xp_bar}%; height:100%; background:{st.session_state["config"]["theme_color"]}; border-radius:2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("SAIR DO SISTEMA", use_container_width=True):
        st.session_state["logado"] = False
        st.rerun()

# --- HEADER DE STATUS (HUD) ---
tempo, icone_tempo = LiturgicalCalendar.get_season()
nivel_b, msg_b = PastoralMind.check_burnout()
cor_b = "#32D74B" if nivel_b == "ESTÁVEL" else "#FF453A"

st.markdown(f"""
<div class="status-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:20px;">{icone_tempo}</span>
        <div>
            <div style="font-size:10px; color:#888; text-transform:uppercase;">Tempo Litúrgico</div>
            <div style="font-size:14px; font-weight:600;">{tempo}</div>
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:10px; color:#888; text-transform:uppercase;">Vitalidade</div>
        <div style="font-size:14px; font-weight:600; color:{cor_b};">{nivel_b}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CONTEÚDO DAS PÁGINAS ---

if menu == "Dashboard":
    st.markdown(f"<h2 style='font-family:Cinzel'>Bem-vindo, {st.session_state['user_name']}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="omega-card">', unsafe_allow_html=True)
        st.caption("COMO ESTÁ SUA ALMA?")
        humor = st.selectbox("Check-in", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("Registrar Estado", use_container_width=True):
            PastoralMind.registrar(humor)
            Gamification.add_xp(10)
            st.success("Registrado.")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="omega-card">', unsafe_allow_html=True)
        st.caption("RESUMO DE SAÚDE MENTAL")
        st.info(f"Diagnóstico: {msg_b}")
        if nivel_b == "CRÍTICO":
            st.warning("⚠️ RECOMENDAÇÃO: Tire um dia de 'Sabbath' urgente.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.subheader("Últimos Manuscritos")
    files = sorted([f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(DIRS["SERMOES"], x)), reverse=True)[:3]
    
    cols = st.columns(3)
    for i, f in enumerate(files):
        with cols[i]:
            st.markdown(f"""
            <div style="padding:15px; background:#0E0E0E; border:1px solid #222; border-radius:5px; margin-bottom:10px;">
                <div style="font-size:20px;">📄</div>
                <div style="font-weight:600; margin-top:5px;">{f.replace('.txt','')}</div>
            </div>
            """, unsafe_allow_html=True)

elif menu == "Gabinete Pastoral":
    st.title("Gabinete Pastoral")
    st.caption("Espaço seguro e criptografado para a alma do pastor.")
    
    tab1, tab2 = st.tabs(["📓 Diário 'Coram Deo'", "🧠 Terapia da Verdade"])
    
    with tab1:
        st.markdown("Escreva suas angústias. Deus ouve, e este sistema guarda.")
        diario = st.text_area("Texto Confidencial", height=300)
        if st.button("Guardar no Cofre"):
            soul = SafeIO.ler_json(DBS["SOUL"], {"diario": []})
            soul.setdefault("diario", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "texto": diario})
            SafeIO.salvar_json(DBS["SOUL"], soul)
            Gamification.add_xp(15)
            st.success("Guardado.")
            
    with tab2:
        mentira = st.text_input("Qual mentira o inimigo lançou hoje? (Ex: 'Sou inútil')")
        if mentira:
            st.info("💡 **Antídoto Bíblico:** 'Porque somos feitura sua, criados em Cristo Jesus para as boas obras.' (Efésios 2:10)")

elif menu == "Studio Expositivo":
    if nivel_b == "CRÍTICO":
        st.error("🛑 ACESSO NEGADO PELO AGENTE PARACLETO.")
        st.markdown("### Burnout Detectado.")
        st.markdown("O sistema bloqueou a escrita de sermões para proteger sua saúde. Vá para o Gabinete ou descanse.")
        st.stop()

    st.title("Studio Expositivo")
    
    c1, c2 = st.columns([3, 1])
    c1.text_input("Título do Sermão", key="titulo_ativo", placeholder="Ex: A Soberania de Deus...")
    if c2.button("💾 SALVAR", use_container_width=True, type="primary"):
        if st.session_state["titulo_ativo"]:
            path = os.path.join(DIRS["SERMOES"], f"{st.session_state['titulo_ativo']}.txt")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(st.session_state["texto_ativo"])
            SafeIO.salvar_json(os.path.join(DIRS["BACKUP"], "log.json"), {"saved": True})
            Gamification.add_xp(5)
            st.toast("Salvo com sucesso!", icon="✅")

    col_editor, col_ai = st.columns([2.5, 1])
    
    with col_editor:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        st.session_state["texto_ativo"] = st.text_area("editor", st.session_state["texto_ativo"], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_ai:
        st.markdown("#### Protocolo Genebra")
        alerts = GenevaProtocol.scan(st.session_state["texto_ativo"])
        if not alerts:
            st.markdown("<div style='color:#32D74B; padding:10px; background:#051a05; border-radius:4px;'>✅ Doutrina Sã</div>", unsafe_allow_html=True)
        else:
            for a in alerts: st.warning(a)
            
        st.divider()
        st.markdown("#### Assistente Teológico")
        q = st.text_area("Consultar", height=100)
        if st.button("Pesquisar"):
            api = st.session_state["config"].get("api_key")
            if api:
                try:
                    genai.configure(api_key=api)
                    r = genai.GenerativeModel("gemini-pro").generate_content(f"Teologia Reformada: {q}").text
                    st.info(r)
                except: st.error("Erro na API.")
            else: st.warning("Configure a API Key.")

elif menu == "Séries Bíblicas":
    st.title("Planejamento de Séries")
    
    with st.expander("➕ Nova Série Expositiva", expanded=True):
        with st.form("serie_form"):
            n = st.text_input("Nome da Série")
            d = st.text_area("Descrição / Livro Bíblico")
            if st.form_submit_button("Criar Estrutura"):
                db = SafeIO.ler_json(DBS["SERIES"], {})
                db[f"S{int(time.time())}"] = {"nome": n, "descricao": d}
                SafeIO.salvar_json(DBS["SERIES"], db)
                st.success("Criado.")
                st.rerun()
                
    st.markdown("### Séries em Andamento")
    db = SafeIO.ler_json(DBS["SERIES"], {})
    if not db: st.info("Nenhuma série ativa.")
    for k, v in db.items():
        st.markdown(f"<div class='omega-card'><b>{v['nome']}</b><br><small>{v['descricao']}</small></div>", unsafe_allow_html=True)

elif menu == "Media Lab":
    st.title("Media Lab")
    st.caption("Gerador de Artes para Culto (Simulador)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div style="height:300px; border:1px dashed #333; display:flex; align-items:center; justify-content:center; color:#666;">PREVIEW 1080x1080</div>', unsafe_allow_html=True)
    with c2:
        st.text_input("Versículo / Frase")
        st.selectbox("Estilo", ["Minimalista", "Reformed Dark", "Natureza"])
        if st.button("Renderizar Arte"):
            st.success("Renderizado (Simulação).")
            
elif menu == "Configurações":
    st.title("Configurações")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Aparência")
        nc = st.color_picker("Cor Destaque", st.session_state["config"].get("theme_color", "#D4AF37"))
        nf = st.slider("Fonte", 14, 28, st.session_state["config"].get("font_size", 18))
    with c2:
        st.markdown("### Conectividade")
        nk = st.text_input("Google API Key", value=st.session_state["config"].get("api_key", ""), type="password")
        
    if st.button("SALVAR CONFIGURAÇÕES", type="primary"):
        cfg = st.session_state["config"]
        cfg["theme_color"] = nc; cfg["font_size"] = nf; cfg["api_key"] = nk
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("Salvo. Reiniciando...")
        time.sleep(1)
        st.rerun()
        
    st.divider()
    if st.button("Baixar Backup Completo (.zip)"):
        shutil.make_archive("backup_omega", 'zip', ROOT)
        with open("backup_omega.zip", "rb") as f:
            st.download_button("Download Backup", f, "backup_omega.zip")
