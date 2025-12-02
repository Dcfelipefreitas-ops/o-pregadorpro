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
from datetime import datetime, timedelta
from collections import Counter
from io import BytesIO

# ==============================================================================
# 0. OMEGA KERNEL: BOOTSTRAP & DEPENDENCIES (SYSTEM CORE)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo de inicialização de alta performance.
    Gerencia integridade, assets visuais e configuração de ambiente.
    """
    REQUIRED_LIBS = ["google-generativeai", "streamlit-lottie", "Pillow"]
    
    @staticmethod
    def _install_quietly(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

    @staticmethod
    def integrity_check():
        """Verifica e repara o ambiente de execução silenciosamente."""
        install_queue = []
        for lib in SystemOmegaKernel.REQUIRED_LIBS:
            try:
                # Mapeamento de imports vs nomes de pacotes
                module = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(module.replace("-", "_"))
            except ImportError:
                install_queue.append(lib)
        
        if install_queue:
            placeholder = st.empty()
            with placeholder.container():
                st.markdown("### ⚙️ OMEGA SYSTEM UPDATE")
                st.markdown(f"Otimizando kernel... ({len(install_queue)} patchs)")
                st.progress(0)
                for idx, lib in enumerate(install_queue):
                    SystemOmegaKernel._install_quietly(lib)
                    st.progress((idx + 1) / len(install_queue))
            placeholder.empty()
            st.rerun()

# Executa Verificação de Integridade
SystemOmegaKernel.integrity_check()

# Importações Pós-Verificação
import google.generativeai as genai
from PIL import Image, ImageOps, ImageFilter

# ==============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE & CONSTANTES DE DESIGN
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

# Caminhos do Sistema (Preservados)
PASTA_RAIZ = "Dados_Pregador_V16"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_MIDIA = os.path.join(PASTA_RAIZ, "Assets_Midia")
PASTA_USER = os.path.join(PASTA_RAIZ, "User_Profile")
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json")
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")

# Criação de Infraestrutura
for p in [PASTA_RAIZ, PASTA_SERMOES, PASTA_CARE, PASTA_SERIES, PASTA_MIDIA, PASTA_USER]:
    os.makedirs(p, exist_ok=True)

# ==============================================================================
# 2. UI ASSETS: ICONOGRAFIA VETORIAL (SVG SYSTEM)
# ==============================================================================
class OmegaIcons:
    """Banco de ícones SVG base64 para interface Apple-like limpa."""
    
    @staticmethod
    def get_icon(name, color="#888888"):
        icons = {
            "home": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>''',
            "edit": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>''',
            "media": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>''',
            "books": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>''',
            "settings": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>''',
            "cross": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 8h8"/></svg>''',
            "user": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'''
        }
        return f'data:image/svg+xml;base64,{base64.b64encode(icons.get(name, "").encode()).decode()}'

# ==============================================================================
# 3. DESIGN SYSTEM: CSS INJECTION (APPLE STYLE)
# ==============================================================================
def inject_premium_css(theme_color="#D4AF37", font_size=18):
    st.markdown(f"""
    <style>
        /* IMPORTANDO FONTES PREMIUM */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@500;700&display=swap');
        
        :root {{
            --bg-deep: #000000;
            --bg-surface: #121212;
            --bg-glass: rgba(18, 18, 18, 0.75);
            --border-subtle: rgba(255, 255, 255, 0.1);
            --text-main: #F5F5F7;
            --text-muted: #86868B;
            --accent: {theme_color};
            --success: #32D74B;
            --danger: #FF453A;
            --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-serif: 'Playfair Display', serif;
        }}
        
        /* RESET STREAMLIT */
        .stApp {{
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: var(--font-ui);
        }}
        
        header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
        
        .block-container {{
            padding-top: 100px !important;
            padding-bottom: 50px !important;
            max-width: 1200px !important;
        }}

        /* --- OMEGA NAVIGATION BAR (APPLE STYLE) --- */
        .omega-header {{
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 1100px;
            height: 64px;
            background: var(--bg-glass);
            backdrop-filter: blur(25px) saturate(180%);
            -webkit-backdrop-filter: blur(25px) saturate(180%);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }}
        
        .omega-header:hover {{
            border-color: rgba(255,255,255,0.2);
            box-shadow: 0 15px 40px rgba(0,0,0,0.6);
        }}
        
        .nav-brand {{
            font-family: var(--font-serif);
            font-weight: 700;
            font-size: 18px;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: 0.5px;
        }}
        
        /* SIMULAÇÃO DE BOTÕES NA NAVBAR */
        /* O Streamlit não permite botões HTML nativos fáceis, então estilizamos os st.buttons dentro das colunas */
        div[data-testid="stHorizontalBlock"] button {{
            background: transparent !important;
            border: none !important;
            color: var(--text-muted) !important;
            font-family: var(--font-ui) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            padding: 4px 12px !important;
        }}
        
        div[data-testid="stHorizontalBlock"] button:hover {{
            color: var(--text-main) !important;
            background: rgba(255,255,255,0.05) !important;
            border-radius: 8px !important;
        }}
        
        div[data-testid="stHorizontalBlock"] button:focus {{
            color: var(--accent) !important;
            outline: none !important;
        }}

        /* --- CARDS & PANELS --- */
        .omega-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        
        .omega-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.15);
        }}

        /* --- INPUTS & FORMS --- */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {{
            background-color: #1A1A1A !important;
            border: 1px solid #333 !important;
            color: #EAEAEA !important;
            border-radius: 10px !important;
            padding: 10px 15px !important;
        }}
        
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2) !important;
        }}

        /* EDITOR TYPOGRAPHY */
        .editor-box textarea {{
            font-family: var(--font-serif) !important;
            font-size: {font_size}px !important;
            line-height: 1.8 !important;
            background: transparent !important;
            border: none !important;
            padding: 20px 0 !important;
            color: #DEDEDE !important;
        }}

        /* --- GAMIFICATION BARS --- */
        .xp-pill {{
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border-subtle);
            border-radius: 30px;
            padding: 4px 12px;
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .xp-progress {{
            width: 60px;
            height: 4px;
            background: #333;
            border-radius: 2px;
            overflow: hidden;
        }}
        
        .xp-fill {{
            height: 100%;
            background: var(--accent);
            border-radius: 2px;
        }}

        /* UTILS */
        .badge-icon {{ 
            font-size: 18px; 
            opacity: 0.8; 
            margin-right: 5px; 
            transition: 0.2s;
        }}
        .badge-icon:hover {{ opacity: 1; transform: scale(1.2); }}

    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. ENGINE DE CONFIGURAÇÃO (BACKEND)
# ==============================================================================
class ConfigManager:
    @staticmethod
    def get_config():
        defaults = {"font_size": 18, "theme_color": "#D4AF37", "ai_temp": 0.7}
        if os.path.exists(DB_CONFIG):
            try:
                with open(DB_CONFIG, 'r') as f:
                    return {**defaults, **json.load(f)}
            except: pass
        return defaults
        
    @staticmethod
    def save_config(cfg):
        with open(DB_CONFIG, 'w') as f: json.dump(cfg, f)

# Inicializa Configuração
current_config = ConfigManager.get_config()
inject_premium_css(current_config['theme_color'], current_config['font_size'])

# ==============================================================================
# 5. GESTÃO DE ESTADO (SESSION)
# ==============================================================================
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Dashboard"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "humor": "Neutro",
    "user_avatar": None, "user_name": "Pastor",
    "config": current_config
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ==============================================================================
# 6. COMPONENTE: NAVBAR FLUTUANTE (CORE UI)
# ==============================================================================
def render_omega_header():
    """Renderiza o cabeçalho flutuante usando layout de colunas para simular a barra."""
    
    # Início do Container da Navbar (HTML Puro para o visual 'Container')
    st.markdown('<div class="omega-header">', unsafe_allow_html=True)
    
    # Precisamos criar colunas dentro do fluxo normal, mas o CSS as posicionará dentro do container .omega-header
    # Nota: No Streamlit, usar colunas dentro de HTML é complexo, então usamos um hack visual.
    # O CSS .omega-header atua como fundo. Aqui desenhamos o conteúdo sobre ele.
    
    # Para garantir o alinhamento, usaremos st.columns padrão, mas o CSS global ajustou os botões.
    # Vou usar uma abordagem de container limpo.
    
    with st.container():
        # Layout: [Logo/Brand] [Spacer] [Nav Buttons] [Spacer] [User Profile]
        c_brand, c_nav, c_user = st.columns([1.5, 3.5, 1.2])
        
        with c_brand:
            st.markdown(f'''
            <div class="nav-brand">
                <img src="{OmegaIcons.get_icon("cross", st.session_state["config"]["theme_color"])}" width="20"/>
                <span>OMEGA</span>
            </div>
            ''', unsafe_allow_html=True)
            
        with c_nav:
            # Botões de Navegação Minimalistas
            # Usando CSS para remover a "cara de botão" e deixar só texto/ícone
            sub_cols = st.columns(5)
            
            nav_items = [
                ("Dashboard", "home"),
                ("Studio", "edit"),
                ("Media", "media"),
                ("Series", "books"),
                ("Config", "settings")
            ]
            
            for idx, (label, icon_name) in enumerate(nav_items):
                is_active = st.session_state['page_stack'][-1] == label
                icon_color = st.session_state["config"]["theme_color"] if is_active else "#666"
                
                # Renderiza botão
                if sub_cols[idx].button(label, key=f"nav_{label}"):
                    st.session_state['page_stack'].append(label)
                    st.rerun()

        with c_user:
            # User Pill com Gamificação
            stats = st.session_state.get('user_stats', {"xp": 0, "nivel": 1})
            xp_percent = stats['xp'] % 100
            
            st.markdown(f'''
            <div style="display:flex; justify-content:flex-end; align-items:center;">
                <div class="xp-pill">
                    <span style="color:#888">LVL {stats['nivel']}</span>
                    <div class="xp-progress">
                        <div class="xp-fill" style="width:{xp_percent}%"></div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Fecha Container CSS
    
    # Espaçamento para não ficar "atrás" da navbar fixa
    st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)

# ==============================================================================
# 7. LOGICA DE NEGÓCIO (MANTIDA - GAMES, PASTORAL, ETC.)
# ==============================================================================

class LeviteGamification:
    BADGES = {
        "novico": {"nome": "Noviço", "desc": "Primeiro acesso ao sistema.", "icon": "🌱"},
        "escriba": {"nome": "Escriba Fiel", "desc": "Escreveu sermões consistentes.", "icon": "📜"},
        "guardiao": {"nome": "Guardião", "desc": "7 dias de ofensiva.", "icon": "🛡️"},
        "teologo": {"nome": "Mestre da Palavra", "desc": "Nível 10 alcançado.", "icon": "🎓"},
        "profeta": {"nome": "Voz Profética", "desc": "Usou discernimento IA 50 vezes.", "icon": "🦁"}
    }
    @staticmethod
    def carregar_stats():
        if not os.path.exists(DB_STATS):
            return {"xp": 0, "nivel": 1, "sermoes_criados": 0, "ultimo_login": "", "streak_dias": 0, "badges": ["novico"]}
        try:
            with open(DB_STATS, 'r') as f: return json.load(f)
        except: return {"xp": 0, "nivel": 1, "badges": ["novico"]}
    @staticmethod
    def salvar_stats(dados):
        with open(DB_STATS, 'w') as f: json.dump(dados, f, indent=4)
    @staticmethod
    def processar_login():
        stats = LeviteGamification.carregar_stats()
        hoje = datetime.now().strftime("%Y-%m-%d")
        if stats.get("ultimo_login") != hoje:
            if stats.get("ultimo_login"):
                try:
                    last = datetime.strptime(stats["ultimo_login"], "%Y-%m-%d")
                    diff = (datetime.now() - last).days
                    stats["streak_dias"] = stats.get("streak_dias", 0) + 1 if diff == 1 else 1
                except: stats["streak_dias"] = 1
            else: stats["streak_dias"] = 1
            stats["ultimo_login"] = hoje
            stats["xp"] += 10
            LeviteGamification.salvar_stats(stats)
        return stats
    @staticmethod
    def adicionar_xp(qtd):
        stats = LeviteGamification.carregar_stats()
        stats["xp"] += qtd
        novo_nivel = int(math.sqrt(stats["xp"]) * 0.2) + 1
        if novo_nivel > stats["nivel"]: stats["nivel"] = novo_nivel
        LeviteGamification.salvar_stats(stats)

class ShepherdEngine:
    @staticmethod
    def analisar_caminho_pregacao(humor, api_key):
        conselhos = {
            "Ira 😠": {"perigo": "Pregar com raiva fere.", "texto_cura": "Tiago 1:19", "direcao": "Graça."},
            "Cansaço 🌖": {"perigo": "Teologia mecânica.", "texto_cura": "1 Reis 19", "direcao": "Descanso."},
            "Soberba 👑": {"perigo": "Púlpito não é pedestal.", "texto_cura": "Fp 2:3", "direcao": "Humildade."},
            "Tristeza 😢": {"perigo": "Projeção de dor.", "texto_cura": "Salmos 42", "direcao": "Empatia."},
            "Neutro": None, "Plenitude 🕊️": None, "Gratidão 🙏": None, "Guerra Espiritual ⚔️": None
        }
        base = conselhos.get(humor)
        if base and api_key:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel("gemini-pro")
                p = f"O pastor sente {humor}. Gere oração curta (15 palavras) baseada em {base['texto_cura']}."
                base['oracao_ia'] = m.generate_content(p).text
            except: base['oracao_ia'] = "Senhor, guia-me."
        return base

class SermonSeriesManager:
    @staticmethod
    def carregar_series():
        if os.path.exists(DB_SERIES):
            try: with open(DB_SERIES, 'r') as f: return json.load(f)
            except: return {}
        return {}
    @staticmethod
    def criar_serie(nome, desc):
        db = SermonSeriesManager.carregar_series()
        db[f"S{int(time.time())}"] = {"nome": nome, "descricao": desc, "data_inicio": datetime.now().strftime("%d/%m/%Y")}
        with open(DB_SERIES, 'w') as f: json.dump(db, f, indent=4)
        LeviteGamification.adicionar_xp(50)

class LiturgicalEngine:
    @staticmethod
    def get_calendario_cristao():
        return {"tempo_atual": "Tempo Comum", "cor_atual": "#2ECC71"} # Simplificado para brevidade no header

class HomileticAnalytics:
    @staticmethod
    def analisar_densidade(texto):
        if not texto: return {"tempo": 0, "palavras_total": 0}
        n = len(texto.split())
        return {"palavras_total": n, "tempo_estimado": math.ceil(n/130)}

# Processa Login Silencioso
if st.session_state['logado']:
    st.session_state['user_stats'] = LeviteGamification.processar_login()

# ==============================================================================
# 8. TELA DE LOGIN (MODERNIZADA)
# ==============================================================================
if not st.session_state['logado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # Logo Animado com CSS Pulse
        st.markdown(f"""
        <style>
            @keyframes pulse-gold {{ 0% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); }} 70% {{ box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }} }}
            .login-circle {{
                width: 80px; height: 80px; border-radius: 50%;
                border: 2px solid {st.session_state['config']['theme_color']};
                margin: 0 auto 20px auto;
                display: flex; align-items: center; justify-content: center;
                animation: pulse-gold 2s infinite;
            }}
        </style>
        <div class="login-circle">
            <img src="{OmegaIcons.get_icon("cross", "#D4AF37")}" width="30"/>
        </div>
        <div style="text-align:center; margin-bottom:30px;">
            <h3 style="font-family: 'Playfair Display'; margin:0;">SYSTEM OMEGA</h3>
            <span style="font-size:10px; letter-spacing:3px; color:#666; text-transform:uppercase;">Identidade Pastoral</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_gate"):
            u = st.text_input("ID", placeholder="Usuário", label_visibility="collapsed")
            p = st.text_input("Key", type="password", placeholder="Chave de Acesso", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("INICIAR SESSÃO", use_container_width=True):
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Acesso não autorizado.")
    st.stop()

# ==============================================================================
# 9. APP PRINCIPAL (CONTEÚDO)
# ==============================================================================

render_omega_header() # Renderiza a nova barra Apple-like
page = st.session_state['page_stack'][-1]
stats = st.session_state.get('user_stats', {})

# --- DASHBOARD ---
if page == "Dashboard":
    st.markdown(f"## Bem-vindo, {st.session_state['user_name']}.")
    
    # Shepherd Engine (Cuidado Emocional)
    st.markdown('<div class="omega-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.caption("ESTADO ESPIRITUAL")
        humor = st.selectbox("Humor", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Soberba 👑"], label_visibility="collapsed")
        if humor != st.session_state['humor']:
            st.session_state['humor'] = humor
            LeviteGamification.adicionar_xp(5)
            st.rerun()
    with c2:
        advice = ShepherdEngine.analisar_caminho_pregacao(st.session_state['humor'], st.session_state['api_key'])
        if advice:
            st.warning(f"{advice['perigo']}")
            st.caption(f"Refúgio: {advice['texto_cura']} | {advice.get('oracao_ia', '')}")
        else:
            st.success("Espírito alinhado para a obra. Bom trabalho.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Projetos
    col_proj, col_stat = st.columns([2, 1])
    with col_proj:
        st.markdown("### Trabalhos Recentes")
        files = sorted([f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)[:3]
        for f in files:
            with st.container():
                c_a, c_b = st.columns([4, 1])
                c_a.markdown(f"<div style='padding:10px; background:#1A1A1A; border-radius:8px; border:1px solid #333'>{f.replace('.txt','')}</div>", unsafe_allow_html=True)
                if c_b.button("Abrir", key=f"op_{f}"):
                    st.session_state['titulo_ativo'] = f.replace(".txt","")
                    with open(os.path.join(PASTA_SERMOES, f), 'r') as fl: st.session_state['texto_ativo'] = fl.read()
                    st.session_state['page_stack'].append("Studio")
                    st.rerun()
    
    with col_stat:
        st.markdown("### Performance")
        st.metric("Sermões", len(os.listdir(PASTA_SERMOES)))
        st.metric("Streak", f"{stats.get('streak_dias', 0)} dias")

# --- STUDIO ---
elif page == "Studio":
    st.markdown("### Studio")
    t1, t2 = st.columns([3, 1])
    t1.text_input("Título", key="titulo_ativo", label_visibility="collapsed", placeholder="Título da Mensagem...")
    if t2.button("Salvar & Sincronizar", type="primary"):
        if st.session_state['titulo_ativo']:
            with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                f.write(st.session_state['texto_ativo'])
            LeviteGamification.adicionar_xp(5)
            st.toast("Salvo na nuvem local.", icon="☁️")
    
    c_edit, c_tool = st.columns([2.5, 1])
    with c_edit:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        st.session_state['texto_ativo'] = st.text_area("editor", st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        meta = HomileticAnalytics.analisar_densidade(st.session_state['texto_ativo'])
        st.caption(f"{meta['palavras_total']} palavras | ~{meta['tempo_estimado']} min de fala")

    with c_tool:
        st.markdown("#### IA Teológica")
        q = st.text_area("Consultar", height=100)
        if st.button("Pesquisar"):
            if st.session_state['api_key']:
                genai.configure(api_key=st.session_state['api_key'])
                res = genai.GenerativeModel("gemini-pro").generate_content(f"Teologia concisa: {q}").text
                st.info(res)

# --- SERIES ---
elif page == "Series":
    st.title("Séries")
    tab1, tab2 = st.tabs(["Ativas", "Nova"])
    with tab1:
        dbs = SermonSeriesManager.carregar_series()
        for k,v in dbs.items(): st.info(f"**{v['nome']}**: {v['descricao']}")
    with tab2:
        with st.form("ns"):
            n = st.text_input("Nome")
            d = st.text_area("Escopo")
            if st.form_submit_button("Criar"):
                SermonSeriesManager.criar_serie(n, d)
                st.success("Criado.")

# --- CONFIG ---
elif page == "Config":
    st.title("Ajustes")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Identidade Visual")
        c = st.color_picker("Cor de Destaque", st.session_state['config']['theme_color'])
        s = st.slider("Tamanho da Fonte", 14, 24, st.session_state['config']['font_size'])
    with c2:
        st.markdown("#### Sistema")
        k = st.text_input("API Key", value=st.session_state['api_key'], type="password")
        
    if st.button("Aplicar Mudanças"):
        cfg = st.session_state['config']
        cfg['theme_color'] = c
        cfg['font_size'] = s
        st.session_state['api_key'] = k
        ConfigManager.save_config(cfg)
        st.rerun()
        
    if st.button("Logout"):
        st.session_state['logado'] = False
        st.rerun()

# --- MEDIA (Placeholder) ---
elif page == "Media":
    st.title("Assets & Media")
    st.info("Módulo de geração de imagem em desenvolvimento.")
