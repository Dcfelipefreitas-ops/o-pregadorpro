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
from collections import Counter
from io import BytesIO

# ==============================================================================
# 0. KERNEL DE INICIALIZAÇÃO E AUTO-REPARO (SYSTEM CORE)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo de inicialização do Sistema O Pregador.
    Gerencia integridade, assets visuais e configuração de ambiente.
    """
    REQUIRED_LIBS = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas", "fpdf"]
    
    @staticmethod
    def _install_quietly(package):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        except Exception as e:
            print(f"Erro de kernel ao instalar {package}: {e}")

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
                st.markdown("### ⚙️ INICIANDO PROTOCOLO OMEGA...")
                st.markdown(f"Restaurando módulos neurais... ({len(install_queue)} pacotes)")
                st.progress(0)
                for idx, lib in enumerate(install_queue):
                    SystemOmegaKernel._install_quietly(lib)
                    st.progress((idx + 1) / len(install_queue))
            placeholder.empty()
            st.rerun()

# Executa Verificação
SystemOmegaKernel.integrity_check()

import google.generativeai as genai
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

# ==============================================================================
# 1. CONFIGURAÇÃO E INFRAESTRUTURA
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR ", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

# Caminhos Absolutos (Estrutura Completa)
PASTA_RAIZ = "Dados_Pregador_Ultimate_V20"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes_Expositivos")
PASTA_CARE = os.path.join(PASTA_RAIZ, "Gabinete_Pastoral")
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_MIDIA = os.path.join(PASTA_RAIZ, "Assets_Midia")
PASTA_USER = os.path.join(PASTA_RAIZ, "Perfil_Pastor")
PASTA_LOGS = os.path.join(PASTA_RAIZ, "System_Logs")

# Bancos de Dados JSON
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json")
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")
DB_SOUL = os.path.join(PASTA_CARE, "saude_mental_pastoral.json")

# Criação da Infraestrutura
for p in [PASTA_RAIZ, PASTA_SERMOES, PASTA_CARE, PASTA_SERIES, PASTA_MIDIA, PASTA_USER, PASTA_LOGS]:
    os.makedirs(p, exist_ok=True)

# ==============================================================================
# 2. DESIGN SYSTEM OMEGA (ESTILO SOLICITADO PRESERVADO)
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
            --success: #32D74B;
            --danger: #FF453A;
        }}
        
        .stApp {{ background-color: var(--bg-deep); color: var(--text-main); font-family: 'Inter', sans-serif; }}
        header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
        .block-container {{ padding-top: 80px !important; max-width: 1200px !important; }}

        /* NAVBAR FLUTUANTE (APPLE STYLE) */
        .omega-nav {{
            position: fixed; top: 0; left: 0; width: 100%; height: 60px;
            background: rgba(5, 5, 5, 0.95); backdrop-filter: blur(15px);
            border-bottom: 1px solid var(--border); z-index: 9999;
            display: flex; align-items: center; justify-content: space-between; padding: 0 30px;
        }}

        /* --- ANIMAÇÃO DE LOGIN (RESTAURADA E PROTEGIDA) --- */
        @keyframes pulse-gold {{
            0% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); transform: scale(1); }}
            50% {{ box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); transform: scale(1.05); }}
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
            transition: transform 0.2s;
        }}
        .omega-card:hover {{ border-color: #333; transform: translateY(-2px); }}

        .editor-box textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_size}px !important;
            line-height: 1.8 !important;
            background-color: #050505 !important;
            border: 1px solid #222 !important;
            color: #ddd !important;
            padding: 20px !important;
        }}
        
        /* UTILS */
        .stTextInput input, .stSelectbox div {{
            background-color: #111 !important; border: 1px solid #333 !important; color: white !important;
        }}
        
        /* ALERTAS TEOLÓGICOS */
        .theology-alert {{ border-left: 3px solid var(--danger); background: #1a0505; padding: 10px; font-size: 13px; margin-top:5px; }}
        .theology-safe {{ border-left: 3px solid var(--success); background: #051a05; padding: 10px; font-size: 13px; }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. ICONOGRAFIA (SVG SYSTEM)
# ==============================================================================
class OmegaIcons:
    @staticmethod
    def get_icon(name, color="#D4AF37"):
        icons = {
            "home": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>''',
            "edit": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>''',
            "heart": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>''',
            "media": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>''',
            "books": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>''',
            "settings": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>''',
            "cross": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 8h8"/></svg>'''
        }
        return f'data:image/svg+xml;base64,{base64.b64encode(icons.get(name, "").encode()).decode()}'

# ==============================================================================
# 4. ENGINES AVANÇADAS (TODOS OS MOTORES REUNIDOS E CORRIGIDOS)
# ==============================================================================

class LiturgicalEngine:
    """Motor Matemático Litúrgico."""
    @staticmethod
    def calcular_pascoa(ano):
        a = ano % 19
        b = ano // 100
        c = ano % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mes = (h + l - 7 * m + 114) // 31
        dia = ((h + l - 7 * m + 114) % 31) + 1
        return datetime(ano, mes, dia)

    @staticmethod
    def get_calendario():
        hoje = datetime.now()
        pascoa = LiturgicalEngine.calcular_pascoa(hoje.year)
        datas = {
            "Páscoa": pascoa,
            "Pentecostes": pascoa + timedelta(days=49),
            "Natal": datetime(hoje.year, 12, 25)
        }
        return datas

class ReformedTheologyEngine:
    """Protocolo Genebra: Verificação de Ortodoxia."""
    HERESY_DB = {
        "prosperidade": "⚠️ Alerta: Teologia da Prosperidade. O Evangelho não é garantia financeira.",
        "eu determino": "⚠️ Alerta: Soberania de Deus comprometida. Use 'Se Deus quiser'.",
        "mérito": "⚠️ Alerta: Risco de Pelagianismo. Salvação é Sola Gratia.",
        "força do pensamento": "⚠️ Alerta: Sincretismo. O poder vem do Espírito, não da mente.",
        "exigir": "⚠️ Alerta: Deus não é nosso servo."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        alerts = []
        text_lower = text.lower()
        for term, warning in ReformedTheologyEngine.HERESY_DB.items():
            if term in text_lower: alerts.append(warning)
        if "jesus" not in text_lower and "cristo" not in text_lower and "senhor" not in text_lower:
            alerts.append("🔴 Crítico: Sermão sem cristocentrismo aparente.")
        return alerts

class PastoralPsychologyEngine:
    """Motor de Saúde Mental e Cuidado da Alma."""
    @staticmethod
    def diagnosticar(humor):
        analises = {
            "Ira 😠": {"texto": "Efésios 4:26", "conselho": "A ira do homem não produz justiça.", "risco": 2},
            "Cansaço 🌖": {"texto": "1 Reis 19:5", "conselho": "Elias precisou dormir. Descanse.", "risco": 3},
            "Ansiedade 🌪️": {"texto": "1 Pedro 5:7", "conselho": "Lance sobre Ele a ansiedade.", "risco": 2},
            "Soberba 👑": {"texto": "Provérbios 16:18", "conselho": "A soberba precede a queda.", "risco": 1},
            "Tristeza 😢": {"texto": "Salmos 42", "conselho": "Ponha a esperança em Deus.", "risco": 2},
            "Plenitude 🕊️": {"texto": "Salmos 23", "conselho": "O Senhor é o teu pastor.", "risco": 0}
        }
        return analises.get(humor, {"texto": "Filipenses 4:4", "conselho": "Alegrai-vos.", "risco": 0})

    @staticmethod
    def terapia_cognitiva_biblica(pensamento):
        distorcoes = {
            "salvador": {"gatilho": ["tenho que salvar", "culpa"], "cura": "Você é servo, não Salvador. (Salmos 127:1)"},
            "perfeccionismo": {"gatilho": ["erro", "falhei", "ruim"], "cura": "A graça te basta. (2 Coríntios 12:9)"},
            "solidão": {"gatilho": ["sozinho", "ninguém"], "cura": "Deus reservou 7 mil que não se dobraram. (1 Reis 19)"}
        }
        for k, v in distorcoes.items():
            if any(t in pensamento.lower() for t in v["gatilho"]): return v
        return {"cura": "Entregue o fardo a Cristo. (Mateus 11:28)"}

    @staticmethod
    def monitorar_burnout():
        if not os.path.exists(DB_SOUL): return "Estável"
        try:
            with open(DB_SOUL, 'r') as f: 
                data = json.load(f)
                historico = data.get("historico_humor", [])[-10:]
                risco_total = sum(1 for h in historico if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️"])
                if risco_total >= 6: return "CRÍTICO"
                if risco_total >= 3: return "ALERTA"
                return "ESTÁVEL"
        except: return "Estável"

class LeviteGamification:
    """Gamificação e Assiduidade (CORRIGIDO PARA EVITAR ERRO DE SINTAXE)."""
    @staticmethod
    def add_xp(amount):
        stats = {"xp": 0, "nivel": 1, "badges": []}
        
        # Correção: O 'try' agora envolve o bloco indentado corretamente
        if os.path.exists(DB_STATS):
            try: 
                with open(DB_STATS, 'r') as f: 
                    stats = json.load(f)
            except: 
                pass
        
        stats['xp'] += amount
        stats['nivel'] = int(math.sqrt(stats['xp']) * 0.2) + 1
        
        # Badge Logic
        if stats['xp'] > 100 and "escriba" not in stats.get('badges', []): 
            stats.setdefault('badges', []).append("escriba")
        
        try:
            with open(DB_STATS, 'w') as f: 
                json.dump(stats, f)
        except:
            pass

class SermonSeriesManager:
    @staticmethod
    def carregar():
        if os.path.exists(DB_SERIES):
            try: 
                with open(DB_SERIES, 'r') as f: 
                    return json.load(f)
            except: 
                pass
        return {}
    
    @staticmethod
    def salvar(data):
        try:
            with open(DB_SERIES, 'w') as f: 
                json.dump(data, f)
        except:
            pass

class ConfigManager:
    @staticmethod
    def get_config():
        defaults = {"font_size": 18, "theme_color": "#D4AF37", "ai_temp": 0.7}
        if os.path.exists(DB_CONFIG):
            try: 
                with open(DB_CONFIG, 'r') as f: 
                    return {**defaults, **json.load(f)}
            except: 
                pass
        return defaults
    
    @staticmethod
    def save_config(cfg):
        try:
            with open(DB_CONFIG, 'w') as f: 
                json.dump(cfg, f)
        except:
            pass

# ==============================================================================
# 5. GESTÃO DE ESTADO (SESSION)
# ==============================================================================
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Dashboard"], 
    "texto_ativo": "", "titulo_ativo": "", "api_key": "", "humor": "Neutro",
    "user_avatar": None, "user_name": "Pastor",
    "config": ConfigManager.get_config()
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

inject_css(st.session_state['config']['theme_color'], st.session_state['config']['font_size'])

# ==============================================================================
# 6. COMPONENTES DE UI
# ==============================================================================
def render_navbar():
    with st.container():
        c_brand, c_nav, c_user = st.columns([1.5, 3.5, 1.2])
        
        with c_brand:
            st.markdown(f'''
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{OmegaIcons.get_icon("cross", st.session_state["config"]["theme_color"])}" width="24"/>
                <span style="font-family:Cinzel; font-weight:700; color:{st.session_state["config"]["theme_color"]}; font-size:18px;">SYSTEM OMEGA</span>
            </div>
            ''', unsafe_allow_html=True)
            
        with c_nav:
            cols = st.columns(6)
            menu = [("Dashboard", "home"), ("Gabinete", "heart"), ("Studio", "edit"), ("Séries", "books"), ("Media", "media"), ("Config", "settings")]
            for i, (p, ico) in enumerate(menu):
                if cols[i].button(p, key=f"nav_{p}"): # Simplificado para caber
                    st.session_state['page_stack'].append(p)
                    st.rerun()

        with c_user:
            # Monitor de Saúde na Navbar
            status_burnout = PastoralPsychologyEngine.monitorar_burnout()
            cor = "#32D74B" if status_burnout == "ESTÁVEL" else "#FF453A"
            st.markdown(f'''<div style="text-align:right; font-size:11px;">Vitalidade: <span style="color:{cor}">{status_burnout}</span></div>''', unsafe_allow_html=True)

# ==============================================================================
# 7. TELA DE LOGIN (PROTEGIDA)
# ==============================================================================
if not st.session_state['logado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 0.8, 1])
    
    with c2:
        # AQUI ESTÁ O DESIGN ORIGINAL RESTAURADO
        st.markdown("""
        <div class="holy-circle">
            <span style="font-size:50px; color:#d4af37;">✝</span>
        </div>
        <div style="text-align:center;">
            <h2 style="font-family:'Cinzel'; letter-spacing:4px; font-weight:700; margin:0; color:#fff">O PREGADOR</h2>
            <div style="width:60px; height:2px; background:#D4AF37; margin: 15px auto;"></div>
            <p style="font-size:11px; color:#666; letter-spacing:2px; text-transform:uppercase;">Sola Scriptura • Sola Gratia</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("omega_gate"):
            user = st.text_input("Credencial", label_visibility="collapsed", placeholder="IDENTIFICAÇÃO")
            pw = st.text_input("Chave", type="password", label_visibility="collapsed", placeholder="SENHA")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("INICIAR SISTEMA", type="primary", use_container_width=True):
                if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = user
                    LeviteGamification.add_xp(5)
                    st.rerun()
                else:
                    st.error("Credenciais não reconhecidas.")
    st.stop()

# ==============================================================================
# 8. APLICAÇÃO PRINCIPAL (MAIN APP)
# ==============================================================================
render_navbar()
page = st.session_state['page_stack'][-1]

# --- DASHBOARD ---
if page == "Dashboard":
    st.markdown(f"## Graça e Paz, {st.session_state['user_name']}.")
    
    # 1. Vitality Monitor & Check-in
    st.markdown('<div class="omega-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.caption("CHECK-IN ESPIRITUAL")
        humor = st.selectbox("Status", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Soberba 👑", "Ansiedade 🌪️"], label_visibility="collapsed")
        if st.button("Registrar Estado"):
            # Salvar no JSON com proteção
            db = {"historico_humor": []}
            if os.path.exists(DB_SOUL):
                try:
                    with open(DB_SOUL, 'r') as f: db = json.load(f)
                except: pass
            
            db.setdefault("historico_humor", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
            
            try:
                with open(DB_SOUL, 'w') as f: json.dump(db, f)
            except: pass
            
            st.session_state['humor'] = humor
            LeviteGamification.add_xp(10)
            st.success("Registrado.")
            st.rerun()

    with c2:
        diag = PastoralPsychologyEngine.diagnosticar(st.session_state['humor'])
        st.markdown(f"#### Diagnóstico Pastoral")
        st.warning(f"💡 {diag['conselho']}")
        st.caption(f"📖 Texto de Refúgio: {diag['texto']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Liturgia e Arquivos
    c_lit, c_files = st.columns([1, 2])
    with c_lit:
        st.markdown("#### Calendário Cristão")
        cal = LiturgicalEngine.get_calendario()
        st.write(f"**Páscoa:** {cal['Páscoa'].strftime('%d/%m')}")
        st.write(f"**Pentecostes:** {cal['Pentecostes'].strftime('%d/%m')}")
        
    with c_files:
        st.markdown("#### Mesa de Estudos")
        files = sorted([f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)[:3]
        for f in files:
            with st.container():
                c_a, c_b = st.columns([4, 1])
                c_a.markdown(f"<div style='background:#111; padding:10px; border-radius:5px;'>📄 {f[:-4]}</div>", unsafe_allow_html=True)
                if c_b.button("Abrir", key=f"d_{f}"):
                    st.session_state['titulo_ativo'] = f[:-4]
                    with open(os.path.join(PASTA_SERMOES, f), 'r') as fl: st.session_state['texto_ativo'] = fl.read()
                    st.session_state['page_stack'].append("Studio")
                    st.rerun()

# --- GABINETE (SANTUÁRIO) ---
elif page == "Gabinete":
    st.title("Gabinete Pastoral (Santuário)")
    st.caption("Cuidado da alma e Terapia Cognitiva Bíblica.")
    
    tab1, tab2, tab3 = st.tabs(["🩺 Vitalidade", "💊 Terapia", "📓 Diário"])
    
    with tab1:
        st.subheader("Monitor de Burnout")
        status = PastoralPsychologyEngine.monitorar_burnout()
        st.metric("Risco de Esgotamento", status)
        if status == "CRÍTICO":
            st.error("⚠️ PARE TUDO. Seu ministério está em perigo. Busque descanso imediatamente.")
            
        if os.path.exists(DB_SOUL):
            try:
                with open(DB_SOUL, 'r') as f:
                    d = json.load(f)
                    if d.get("historico_humor"):
                        st.dataframe(pd.DataFrame(d["historico_humor"]), use_container_width=True)
            except: pass

    with tab2:
        st.subheader("Identificador de Mentiras")
        pensamento = st.text_input("Que mentira está te afligindo? (Ex: Tenho que salvar a todos)")
        if pensamento:
            res = PastoralPsychologyEngine.terapia_cognitiva_biblica(pensamento)
            st.info(f"**Verdade Bíblica:** {res['cura']}")
            
    with tab3:
        st.subheader("Diário 'Coram Deo'")
        st.text_area("Escreva para Deus (Criptografado)", height=200)
        if st.button("Guardar"):
            LeviteGamification.add_xp(15)
            st.toast("Guardado no cofre.", icon="🔒")

# --- STUDIO (EDITOR) ---
elif page == "Studio":
    # Bloqueio de Segurança (Paracleto Agent)
    if PastoralPsychologyEngine.monitorar_burnout() == "CRÍTICO":
        st.error("🛑 ACESSO NEGADO PELO PROTOCOLO DE SAÚDE.")
        st.warning("O sistema detectou risco severo de burnout. O módulo de trabalho está bloqueado.")
        st.stop()

    st.markdown("### Studio Expositivo")
    
    c1, c2 = st.columns([3, 1])
    c1.text_input("Título", key="titulo_ativo", label_visibility="collapsed", placeholder="Título do Sermão...")
    if c2.button("💾 Salvar"):
        if st.session_state['titulo_ativo']:
            with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                f.write(st.session_state['texto_ativo'])
            LeviteGamification.add_xp(5)
            st.toast("Salvo.", icon="✅")

    c_edit, c_audit = st.columns([2.5, 1])
    with c_edit:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        st.session_state['texto_ativo'] = st.text_area("main_editor", st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_audit:
        st.markdown("#### 🛡️ Protocolo Genebra")
        alerts = ReformedTheologyEngine.scan(st.session_state['texto_ativo'])
        if not alerts:
            st.markdown('<div class="theology-safe">✅ Doutrina Sã.</div>', unsafe_allow_html=True)
        else:
            for a in alerts: st.markdown(f'<div class="theology-alert">{a}</div>', unsafe_allow_html=True)
            
        st.divider()
        st.markdown("#### IA Teológica")
        q = st.text_area("Consultar")
        if st.button("Pesquisar"):
            if st.session_state['api_key']:
                try:
                    genai.configure(api_key=st.session_state['api_key'])
                    r = genai.GenerativeModel("gemini-pro").generate_content(f"Aja como Calvino. Responda: {q}").text
                    st.info(r)
                except Exception as e:
                    st.error(f"Erro IA: {e}")

# --- SÉRIES ---
elif page == "Séries":
    st.title("Planejamento de Séries")
    with st.form("new_serie"):
        n = st.text_input("Nome")
        d = st.text_area("Escopo")
        if st.form_submit_button("Criar"):
            db = SermonSeriesManager.carregar()
            db[f"S{int(time.time())}"] = {"nome": n, "descricao": d}
            SermonSeriesManager.salvar(db)
            st.success("Criado.")
            st.rerun()
    
    db = SermonSeriesManager.carregar()
    for k, v in db.items(): st.info(f"**{v['nome']}**: {v['descricao']}")

# --- MEDIA (RESTAURADO) ---
elif page == "Media":
    st.title("Media Lab & Agendador")
    st.caption("Gere artes e agende posts.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="omega-card" style="height:300px; display:flex; align-items:center; justify-content:center; border:1px dashed #444;">PREVIEW DA ARTE</div>', unsafe_allow_html=True)
    with c2:
        txt_art = st.text_input("Texto da Arte")
        if st.button("Gerar Imagem (Simulador)"):
            st.success("Imagem enviada para fila de renderização.")
            
        st.divider()
        data_post = st.date_input("Agendar Para")
        if st.button("Agendar Post"):
            st.toast(f"Agendado para {data_post}")

# --- CONFIG ---
elif page == "Config":
    st.title("Configurações")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Aparência")
        c = st.color_picker("Cor Tema", st.session_state['config']['theme_color'])
        s = st.slider("Fonte", 14, 28, st.session_state['config']['font_size'])
        cam = st.camera_input("Foto ID")
        if cam:
            try:
                img = Image.open(cam)
                img = ImageOps.grayscale(img)
                img.save(os.path.join(PASTA_USER, "avatar.png"))
                st.success("ID Atualizado.")
            except: pass
            
    with c2:
        st.markdown("#### Sistema")
        k = st.text_input("API Key", value=st.session_state['api_key'], type="password")
        if st.button("Salvar Tudo"):
            cfg = st.session_state['config']
            cfg['theme_color'] = c
            cfg['font_size'] = s
            st.session_state['api_key'] = k
            ConfigManager.save_config(cfg)
            st.rerun()
        
        st.divider()
        if st.button("Fazer Backup Completo (.zip)"):
            shutil.make_archive("backup_omega", 'zip', PASTA_RAIZ)
            with open("backup_omega.zip", "rb") as f:
                st.download_button("Baixar Backup", f, "backup_omega.zip")
