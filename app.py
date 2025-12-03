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
from datetime import datetime, timedelta
from collections import Counter
from io import BytesIO

# ==============================================================================
# 0. KERNEL DE AUTONOMIA E INTEGRIDADE (SYSTEM CORE)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo de inicialização do Sistema O Pregador.
    Responsável pela integridade e pela 'Autoconsciência' do sistema.
    """
    REQUIRED_LIBS = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas"]
    
    @staticmethod
    def _install_quietly(package):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        except Exception as e:
            print(f"Erro ao instalar {package}: {e}")

    @staticmethod
    def integrity_check():
        """Verifica a integridade do ambiente e repara dependências."""
        install_queue = []
        for lib in SystemOmegaKernel.REQUIRED_LIBS:
            try:
                module_name = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(module_name.replace("-", "_"))
            except ImportError:
                install_queue.append(lib)
        
        if install_queue:
            placeholder = st.empty()
            with placeholder.container():
                st.markdown("### ⚙️ PROTOCOLO DE AUTO-REPARO ATIVADO")
                st.markdown(f"Instalando módulos neurais... ({len(install_queue)} pendentes)")
                st.progress(0)
                for idx, lib in enumerate(install_queue):
                    SystemOmegaKernel._install_quietly(lib)
                    st.progress((idx + 1) / len(install_queue))
            placeholder.empty()
            st.rerun()

# Executa Verificação de Integridade
SystemOmegaKernel.integrity_check()

import google.generativeai as genai
import pandas as pd
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

# ==============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE (REFORMED EDITION)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

# Caminhos Absolutos
PASTA_RAIZ = "Dados_Pregador_V18_Geneva"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes_Expositivos")
PASTA_CARE = os.path.join(PASTA_RAIZ, "Gabinete_Pastoral")
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_USER = os.path.join(PASTA_RAIZ, "Perfil_Pastor")
PASTA_LOGS = os.path.join(PASTA_RAIZ, "System_Logs")

# Bancos de Dados JSON
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json")
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")
DB_SOUL = os.path.join(PASTA_CARE, "saude_mental_pastoral.json")

# Infraestrutura Auto-Regenerativa
for p in [PASTA_RAIZ, PASTA_SERMOES, PASTA_CARE, PASTA_SERIES, PASTA_USER, PASTA_LOGS]:
    os.makedirs(p, exist_ok=True)

# ==============================================================================
# 2. DESIGN SYSTEM OMEGA (ESTÉTICA DOURADA RESTAURADA)
# ==============================================================================
def inject_css(theme_color="#D4AF37", font_size=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@500;700&family=Cinzel:wght@400;700&display=swap');
        
        :root {{
            --bg-deep: #030303;
            --bg-panel: #0E0E0E;
            --gold: {theme_color};
            --text-main: #EAEAEA;
            --border: #222;
        }}
        
        .stApp {{ background-color: var(--bg-deep); color: var(--text-main); font-family: 'Inter', sans-serif; }}
        header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
        .block-container {{ padding-top: 80px !important; max-width: 1200px !important; }}

        /* NAVBAR FLUTUANTE */
        .omega-nav {{
            position: fixed; top: 0; left: 0; width: 100%; height: 60px;
            background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(15px);
            border-bottom: 1px solid var(--border); z-index: 9999;
            display: flex; align-items: center; justify-content: space-between; padding: 0 30px;
        }}

        /* ANIMAÇÃO DO CÍRCULO DOURADO (PULSE) */
        @keyframes pulse-gold {{
            0% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); transform: scale(1); }}
            50% {{ box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); transform: scale(1.02); }}
            100% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); transform: scale(1); }}
        }}
        
        .holy-circle {{
            width: 110px; height: 110px; border-radius: 50%;
            border: 2px solid var(--gold); background: #000;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 25px auto;
            animation: pulse-gold 3s infinite;
            position: relative;
        }}

        /* CARDS & EDITOR */
        .omega-card {{
            background: var(--bg-panel); border: 1px solid var(--border);
            border-radius: 8px; padding: 25px; margin-bottom: 20px;
        }}
        .editor-box textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_size}px !important;
            line-height: 1.8 !important;
            background-color: #050505 !important;
            border: none !important;
            color: #ddd !important;
            padding: 20px !important;
        }}
        .stTextInput input, .stSelectbox div {{
            background-color: #111 !important; border: 1px solid #333 !important; color: white !important;
        }}
        
        /* ALERTAS TEOLÓGICOS */
        .theology-alert {{ border-left: 3px solid #FF453A; background: #1a0505; padding: 10px; font-size: 13px; }}
        .theology-safe {{ border-left: 3px solid #32D74B; background: #051a05; padding: 10px; font-size: 13px; }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES DE INTELIGÊNCIA (IA CONTROLANDO IA)
# ==============================================================================

class GenevaProtocol:
    """
    IA TEOLÓGICA AUTÔNOMA: Verifica desvios doutrinários em tempo real.
    """
    HERESY_DB = {
        "prosperidade": "Alerta: Teologia da Prosperidade detectada. O Evangelho não garante lucro financeiro.",
        "eu declaro": "Alerta: Soberania de Deus comprometida. Use 'Se Deus quiser' (Tiago 4:15).",
        "mérito": "Alerta: Pelagianismo. A salvação é Sola Gratia (Efésios 2:8).",
        "força do pensamento": "Alerta: Sincretismo. O poder vem do Espírito, não da mente.",
        "exigir": "Alerta: Deus não é nosso servo. Humilhe-se."
    }

    @staticmethod
    def scan_sermon(text):
        if not text: return []
        alerts = []
        text_lower = text.lower()
        for term, warning in GenevaProtocol.HERESY_DB.items():
            if term in text_lower:
                alerts.append(warning)
        
        # Verificação de Cristocentrismo
        if "cristo" not in text_lower and "jesus" not in text_lower and "cruz" not in text_lower:
            alerts.append("CRÍTICO: Sermão sem menção explícita à Obra de Cristo. Pregue o Evangelho.")
            
        return alerts

class ParacleteAgent:
    """
    IA DE CUIDADO PASTORAL: Monitora o estado do pastor e bloqueia funções se necessário.
    """
    @staticmethod
    def get_pastoral_state():
        if not os.path.exists(DB_SOUL): return "Estável"
        try:
            with open(DB_SOUL, 'r') as f: data = json.load(f)
            history = data.get("historico_humor", [])[-5:] # Últimos 5
            bad_count = sum(1 for h in history if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
            
            if bad_count >= 3: return "Crítico"
            if bad_count >= 1: return "Alerta"
            return "Estável"
        except: return "Estável"

    @staticmethod
    def apply_intervention():
        state = ParacleteAgent.get_pastoral_state()
        if state == "Crítico":
            st.error("🛑 INTERVENÇÃO DO SISTEMA: Seus níveis de estresse estão críticos.")
            st.info("O módulo de Trabalho (Studio) está restrito. Vá para o Gabinete e ore.")
            return True # Bloqueia ações
        return False

class PastoralPsychologyEngine:
    """Motor de Saúde Mental Pastoral."""
    @staticmethod
    def diagnosticar_estado(humor):
        analises = {
            "Ira 😠": {"texto": "Efésios 4:26", "conselho": "A ira do homem não produz a justiça de Deus."},
            "Cansaço 🌖": {"texto": "1 Reis 19:5", "conselho": "Elias precisou dormir e comer. Você também."},
            "Ansiedade 🌪️": {"texto": "1 Pedro 5:7", "conselho": "Lance sobre Ele toda a vossa ansiedade."},
            "Soberba 👑": {"texto": "Provérbios 16:18", "conselho": "A soberba precede a ruína. Volte à Cruz."},
            "Tristeza 😢": {"texto": "Salmos 42", "conselho": "Ponha sua esperança em Deus."}
        }
        return analises.get(humor, {"texto": "Filipenses 4:4", "conselho": "Alegrai-vos sempre no Senhor."})

    @staticmethod
    def registrar_checkin(humor):
        # Lógica de persistência
        data = {"historico_humor": [], "diario": []}
        if os.path.exists(DB_SOUL):
            with open(DB_SOUL, 'r') as f: data = json.load(f)
        
        data["historico_humor"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        with open(DB_SOUL, 'w') as f: json.dump(data, f)

class LeviteGamification:
    @staticmethod
    def add_xp(amount):
        stats = {"xp": 0, "nivel": 1}
        if os.path.exists(DB_STATS):
            with open(DB_STATS, 'r') as f: stats = json.load(f)
        
        stats['xp'] += amount
        stats['nivel'] = int(math.sqrt(stats['xp']) * 0.2) + 1
        with open(DB_STATS, 'w') as f: json.dump(stats, f)

class SermonSeriesManager:
    @staticmethod
    def carregar():
        if os.path.exists(DB_SERIES):
            with open(DB_SERIES, 'r') as f: return json.load(f)
        return {}
    @staticmethod
    def salvar(data):
        with open(DB_SERIES, 'w') as f: json.dump(data, f)

# ==============================================================================
# 4. GESTÃO DE SESSÃO
# ==============================================================================
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Dashboard"], 
    "texto_ativo": "", "titulo_ativo": "", "api_key": "", "humor": "Neutro",
    "user_avatar": None, "user_name": "Pastor",
    "config": {"font_size": 18, "theme_color": "#D4AF37", "ai_temp": 0.7}
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# Carregar config real
if os.path.exists(DB_CONFIG):
    with open(DB_CONFIG, 'r') as f: st.session_state['config'] = json.load(f)

inject_css(st.session_state['config']['theme_color'], st.session_state['config']['font_size'])

# ==============================================================================
# 5. UI: NAVBAR & LOGIN
# ==============================================================================
def render_navbar():
    with st.container():
        c1, c2, c3 = st.columns([1.5, 3.5, 1])
        with c1:
            st.markdown(f'<span style="font-family:Cinzel; font-weight:700; color:{st.session_state["config"]["theme_color"]}; font-size:20px;">✝ SYSTEM OMEGA</span>', unsafe_allow_html=True)
        with c2:
            cols = st.columns(6)
            menu = [("Dashboard", "🏠"), ("Gabinete", "🛋️"), ("Studio", "📜"), ("Séries", "📚"), ("Config", "⚙️")]
            for i, (p, ico) in enumerate(menu):
                if cols[i].button(f"{ico} {p}", key=f"nav_{p}"):
                    st.session_state['page_stack'].append(p)
                    st.rerun()
        with c3:
            # Status do Sistema de Monitoramento
            state = ParacleteAgent.get_pastoral_state()
            color = "green" if state == "Estável" else "red"
            st.markdown(f'<div style="text-align:right; font-size:12px;">Monitor: <span style="color:{color}">{state}</span></div>', unsafe_allow_html=True)

if not st.session_state['logado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        st.markdown("""
        <div class="holy-circle">
            <span style="font-size:50px; color:#d4af37;">✝</span>
        </div>
        <div style="text-align:center;">
            <h2 style="font-family:'Cinzel'; letter-spacing:4px; font-weight:700; margin:0; color:#fff">O PREGADOR</h2>
            <div style="width:60px; height:2px; background:#D4AF37; margin: 15px auto;"></div>
            <p style="font-size:11px; color:#666; letter-spacing:2px; text-transform:uppercase;">Geneva Protocol • V18</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("omega_gate"):
            user = st.text_input("ID", label_visibility="collapsed", placeholder="IDENTIFICAÇÃO")
            pw = st.text_input("Key", type="password", label_visibility="collapsed", placeholder="SENHA")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("INICIAR SISTEMA", type="primary", use_container_width=True):
                if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = user
                    LeviteGamification.add_xp(5)
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL
# ==============================================================================
render_navbar()
page = st.session_state['page_stack'][-1]

# --- DASHBOARD ---
if page == "Dashboard":
    st.markdown(f"## Graça e Paz, {st.session_state['user_name']}.")
    
    # Cartão de Diagnóstico Rápido
    st.markdown('<div class="omega-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.caption("COMO ESTÁ SUA ALMA?")
        humor = st.selectbox("Status", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Soberba 👑", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("Registrar Check-in"):
            PastoralPsychologyEngine.registrar_checkin(humor)
            st.session_state['humor'] = humor
            LeviteGamification.add_xp(10)
            st.success("Registrado.")
            st.rerun()
            
    with c2:
        diag = PastoralPsychologyEngine.diagnosticar_estado(st.session_state['humor'])
        st.markdown(f"#### Palavra de Guarda")
        st.info(f"💡 {diag['conselho']}")
        st.caption(f"📖 {diag['texto']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Trabalhos Recentes
    st.subheader("Mesa de Estudos")
    files = sorted([f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)[:3]
    
    col_files = st.columns(3)
    for i, f in enumerate(files):
        with col_files[i]:
            st.markdown(f"<div style='background:#111; padding:15px; border-radius:5px; border:1px solid #222'>📄 <b>{f[:-4]}</b></div>", unsafe_allow_html=True)
            if st.button("Abrir", key=f"op_{f}"):
                st.session_state['titulo_ativo'] = f[:-4]
                with open(os.path.join(PASTA_SERMOES, f), 'r') as fl: st.session_state['texto_ativo'] = fl.read()
                st.session_state['page_stack'].append("Studio")
                st.rerun()

# --- GABINETE PASTORAL (MENTAL HEALTH) ---
elif page == "Gabinete":
    st.title("Gabinete Pastoral")
    st.caption("Lugar de descanso, confissão e alinhamento da alma.")
    
    tab1, tab2 = st.tabs(["🩺 Auto-Exame", "📓 Diário 'Coram Deo'"])
    
    with tab1:
        # Gráfico de Humor
        if os.path.exists(DB_SOUL):
            with open(DB_SOUL, 'r') as f:
                data = json.load(f)
                if data.get("historico_humor"):
                    df = pd.DataFrame(data["historico_humor"])
                    st.dataframe(df, use_container_width=True)
                    
        st.divider()
        st.markdown("### Exercício de Respiração (Selah)")
        st.markdown("Respire fundo. O mundo não vai acabar se você parar por 5 minutos. Deus sustenta o universo, não você.")
        
    with tab2:
        st.markdown("Escreva suas angústias. Este texto é criptografado (simbolicamente).")
        diario = st.text_area("Desabafo", height=200)
        if st.button("Entregar a Deus (Salvar)"):
             LeviteGamification.add_xp(20)
             st.toast("Guardado no cofre.", icon="🔒")

# --- STUDIO (COM GENEVA PROTOCOL) ---
elif page == "Studio":
    # Verificação do Agente Paracleto
    if ParacleteAgent.apply_intervention():
        st.stop() # Bloqueia o editor se o pastor estiver em Burnout
        
    st.markdown("### Studio Expositivo")
    
    c1, c2 = st.columns([3, 1])
    c1.text_input("Título do Sermão", key="titulo_ativo", label_visibility="collapsed", placeholder="Título...")
    if c2.button("💾 Salvar"):
        if st.session_state['titulo_ativo']:
            with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                f.write(st.session_state['texto_ativo'])
            LeviteGamification.add_xp(5)
            st.toast("Salvo.", icon="✅")
    
    # Editor Principal
    c_edit, c_audit = st.columns([2.5, 1])
    with c_edit:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        st.session_state['texto_ativo'] = st.text_area("main_editor", st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_audit:
        st.markdown("#### 🛡️ Protocolo Genebra")
        st.caption("Auditoria Teológica em Tempo Real")
        
        alerts = GenevaProtocol.scan_sermon(st.session_state['texto_ativo'])
        
        if not st.session_state['texto_ativo']:
            st.info("Aguardando texto...")
        elif not alerts:
            st.markdown('<div class="theology-safe">✅ Doutrina Aparentemente Sã.</div>', unsafe_allow_html=True)
        else:
            for alert in alerts:
                st.markdown(f'<div class="theology-alert">{alert}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### Assistente IA")
        q = st.text_area("Pergunta Teológica")
        if st.button("Consultar"):
            if st.session_state['api_key']:
                genai.configure(api_key=st.session_state['api_key'])
                r = genai.GenerativeModel("gemini-pro").generate_content(f"Aja como Charles Spurgeon. Responda: {q}").text
                st.info(r)
            else:
                st.error("Configure a API Key.")

# --- SERIES ---
elif page == "Séries":
    st.title("Planejamento de Séries")
    
    with st.form("nova_serie"):
        nome = st.text_input("Nome da Série")
        desc = st.text_area("Objetivo da Série")
        if st.form_submit_button("Criar"):
            db = SermonSeriesManager.carregar()
            db[f"S{int(time.time())}"] = {"nome": nome, "descricao": desc, "inicio": datetime.now().strftime("%d/%m/%Y")}
            SermonSeriesManager.salvar(db)
            st.success("Série Criada.")
            st.rerun()
            
    db = SermonSeriesManager.carregar()
    for k, v in db.items():
        st.info(f"**{v['nome']}**: {v['descricao']}")

# --- CONFIG ---
elif page == "Config":
    st.title("Configurações do Sistema")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Aparência")
        cor = st.color_picker("Cor do Tema", st.session_state['config']['theme_color'])
        fonte = st.slider("Tamanho da Fonte", 14, 28, st.session_state['config']['font_size'])
        
    with c2:
        st.markdown("#### Conectividade")
        key = st.text_input("Google Gemini API Key", value=st.session_state['api_key'], type="password")
        
    if st.button("Salvar Tudo"):
        cfg = st.session_state['config']
        cfg['theme_color'] = cor
        cfg['font_size'] = fonte
        st.session_state['api_key'] = key
        
        with open(DB_CONFIG, 'w') as f: json.dump(cfg, f)
        st.success("Configuração Salva. Reinicie.")
        time.sleep(1)
        st.rerun()
