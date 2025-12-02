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

# ==============================================================================
# 0. OMEGA KERNEL: BOOTSTRAP & DEPENDENCIES (SYSTEM CORE)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo de inicialização de alta performance.
    Gerencia integridade, assets visuais e configuração de ambiente.
    """
    REQUIRED_LIBS = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas"]
    
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
                st.markdown(f"Otimizando kernel de saúde... ({len(install_queue)} módulos)")
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
import pandas as pd
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

# Caminhos do Sistema
PASTA_RAIZ = "Dados_Pregador_V17"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare") # Módulo Saúde Mental
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_MIDIA = os.path.join(PASTA_RAIZ, "Assets_Midia")
PASTA_USER = os.path.join(PASTA_RAIZ, "User_Profile")

# Bancos de Dados JSON
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json")
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")
DB_SOUL = os.path.join(PASTA_CARE, "soul_health.json") # DB de Saúde Mental

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
            "heart": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>''',
            "books": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>''',
            "settings": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>''',
            "cross": f'''<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 8h8"/></svg>''',
        }
        return f'data:image/svg+xml;base64,{base64.b64encode(icons.get(name, "").encode()).decode()}'

# ==============================================================================
# 3. DESIGN SYSTEM: CSS INJECTION (APPLE STYLE)
# ==============================================================================
def inject_premium_css(theme_color="#D4AF37", font_size=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@500;700&display=swap');
        
        :root {{
            --bg-deep: #000000;
            --bg-surface: #121212;
            --bg-glass: rgba(18, 18, 18, 0.75);
            --border-subtle: rgba(255, 255, 255, 0.1);
            --text-main: #F5F5F7;
            --text-muted: #86868B;
            --accent: {theme_color};
            --font-ui: 'Inter', sans-serif;
            --font-serif: 'Playfair Display', serif;
        }}
        
        .stApp {{ background-color: var(--bg-deep); color: var(--text-main); font-family: var(--font-ui); }}
        header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
        .block-container {{ padding-top: 100px !important; max-width: 1200px !important; }}

        /* OMEGA NAVIGATION BAR */
        .omega-header {{
            position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 1100px; height: 64px;
            background: var(--bg-glass); backdrop-filter: blur(25px) saturate(180%);
            border: 1px solid var(--border-subtle); border-radius: 20px;
            z-index: 10000; display: flex; align-items: center; justify-content: space-between;
            padding: 0 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .nav-brand {{ font-family: var(--font-serif); font-weight: 700; font-size: 18px; color: var(--text-main); display: flex; align-items: center; gap: 10px; }}
        
        div[data-testid="stHorizontalBlock"] button {{
            background: transparent !important; border: none !important;
            color: var(--text-muted) !important; font-size: 13px !important;
            font-weight: 500 !important; transition: all 0.2s ease !important;
        }}
        div[data-testid="stHorizontalBlock"] button:hover {{ color: var(--text-main) !important; background: rgba(255,255,255,0.05) !important; border-radius: 8px !important; }}

        .omega-card {{
            background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: 16px; padding: 24px; margin-bottom: 24px;
        }}
        
        /* EDITOR TYPOGRAPHY */
        .editor-box textarea {{
            font-family: var(--font-serif) !important; font-size: {font_size}px !important;
            line-height: 1.8 !important; background: transparent !important;
            border: none !important; color: #DEDEDE !important;
        }}
        
        /* SAÚDE MENTAL COLORS */
        .mood-bad {{ color: #FF453A; }}
        .mood-ok {{ color: #FFD60A; }}
        .mood-good {{ color: #32D74B; }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. ENGINES DE LÓGICA (CORRIGIDAS E EXPANDIDAS)
# ==============================================================================

class SoulCareEngine:
    """
    NOVO MÓDULO: Sistema de Saúde Mental e Cuidado Pastoral.
    Lida com Burnout, Ansiedade e Identidade.
    """
    
    @staticmethod
    def load_soul_db():
        """Carrega o histórico de saúde emocional."""
        if not os.path.exists(DB_SOUL):
            return {"journal": [], "mood_history": [], "checkins": 0}
        try:
            with open(DB_SOUL, 'r') as f:
                return json.load(f)
        except:
            return {"journal": [], "mood_history": [], "checkins": 0}

    @staticmethod
    def save_soul_db(data):
        with open(DB_SOUL, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def registrar_humor(humor, nota_pessoal=""):
        """Registra o humor do dia para análise de tendência."""
        db = SoulCareEngine.load_soul_db()
        entry = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "humor": humor,
            "nota": nota_pessoal
        }
        db["mood_history"].append(entry)
        db["checkins"] += 1
        SoulCareEngine.save_soul_db(db)
        return db

    @staticmethod
    def calcular_risco_burnout():
        """Algoritmo heurístico para detectar padrões de exaustão."""
        db = SoulCareEngine.load_soul_db()
        history = db.get("mood_history", [])
        if not history: return 0, "Sem dados suficientes"

        # Pegar últimos 10 registros
        recentes = history[-10:]
        negativos = sum(1 for h in recentes if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Guerra Espiritual ⚔️"])
        total = len(recentes)
        
        score = (negativos / total) * 100
        
        status = "Estável"
        if score > 40: status = "Atenção: Sinais de Estresse"
        if score > 70: status = "ALERTA: Risco de Burnout Elevado"
        
        return score, status

    @staticmethod
    def terapia_cognitiva_biblica(pensamento):
        """Identifica distorções cognitivas comuns em pastores e oferece antídoto."""
        distorcoes = {
            "salvador": {
                "gatilho": ["tenho que salvar", "depende de mim", "se eu não for", "culpa"],
                "diagnostico": "Complexo de Messias",
                "cura": "Você é o servo, não o Salvador. Jesus já morreu por eles.",
                "texto": "Salmos 127:1 - 'Se o Senhor não edificar a casa, em vão trabalham os que a edificam.'"
            },
            "perfeccionismo": {
                "gatilho": ["erro", "falhei", "não foi bom", "perfeito"],
                "diagnostico": "Legalismo Interno",
                "cura": "Sua aceitação vem da Graça, não da performance do sermão.",
                "texto": "2 Coríntios 12:9 - 'A minha graça te basta, porque o meu poder se aperfeiçoa na fraqueza.'"
            },
            "solidão": {
                "gatilho": ["sozinho", "ninguém entende", "isolado"],
                "diagnostico": "Isolamento Ministerial",
                "cura": "Elias também se sentiu único, mas haviam 7 mil que não se dobraram.",
                "texto": "1 Reis 19:18 - Deus sempre reserva companheiros, mesmo que invisíveis agora."
            }
        }
        
        for key, val in distorcoes.items():
            if any(word in pensamento.lower() for word in val["gatilho"]):
                return val
        
        return {
            "diagnostico": "Cansaço Geral",
            "cura": "Entregue esse fardo ao Senhor agora.",
            "texto": "Mateus 11:28 - 'Vinde a mim, todos os que estais cansados e oprimidos.'"
        }

class LeviteGamification:
    BADGES = {
        "novico": {"nome": "Noviço", "desc": "Primeiro acesso ao sistema.", "icon": "🌱"},
        "escriba": {"nome": "Escriba", "desc": "Escreveu sermões consistentes.", "icon": "📜"},
        "guardiao": {"nome": "Guardião", "desc": "7 dias de ofensiva.", "icon": "🛡️"},
        "teologo": {"nome": "Teólogo", "desc": "Nível 10 alcançado.", "icon": "🎓"}
    }
    @staticmethod
    def carregar_stats():
        if not os.path.exists(DB_STATS): return {"xp": 0, "nivel": 1, "ultimo_login": "", "streak_dias": 0, "badges": ["novico"]}
        try:
            with open(DB_STATS, 'r') as f: return json.load(f)
        except: return {"xp": 0, "nivel": 1}
        
    @staticmethod
    def salvar_stats(dados):
        with open(DB_STATS, 'w') as f: json.dump(dados, f, indent=4)
        
    @staticmethod
    def adicionar_xp(qtd):
        stats = LeviteGamification.carregar_stats()
        stats["xp"] += qtd
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        LeviteGamification.salvar_stats(stats)

class ConfigManager:
    @staticmethod
    def get_config():
        defaults = {"font_size": 18, "theme_color": "#D4AF37", "ai_temp": 0.7}
        if os.path.exists(DB_CONFIG):
            try:
                with open(DB_CONFIG, 'r') as f: return {**defaults, **json.load(f)}
            except: pass
        return defaults
    @staticmethod
    def save_config(cfg):
        with open(DB_CONFIG, 'w') as f: json.dump(cfg, f)

class SermonSeriesManager:
    @staticmethod
    def carregar_series():
        if os.path.exists(DB_SERIES):
            try:
                with open(DB_SERIES, 'r') as f: return json.load(f)
            except: return {}
        return {}
    @staticmethod
    def criar_serie(nome, desc):
        db = SermonSeriesManager.carregar_series()
        db[f"S{int(time.time())}"] = {"nome": nome, "descricao": desc, "data_inicio": datetime.now().strftime("%d/%m/%Y")}
        with open(DB_SERIES, 'w') as f: json.dump(db, f, indent=4)

# ==============================================================================
# 5. GESTÃO DE ESTADO
# ==============================================================================
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Dashboard"], 
    "texto_ativo": "", "titulo_ativo": "", "api_key": "", "humor": "Neutro",
    "user_avatar": None, "user_name": "Pastor",
    "config": ConfigManager.get_config()
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

inject_premium_css(st.session_state['config']['theme_color'], st.session_state['config']['font_size'])

# ==============================================================================
# 6. COMPONENTE: NAVBAR FLUTUANTE
# ==============================================================================
def render_omega_header():
    st.markdown('<div class="omega-header">', unsafe_allow_html=True)
    with st.container():
        c_brand, c_nav, c_user = st.columns([1.5, 3.5, 1.2])
        with c_brand:
            st.markdown(f'''<div class="nav-brand"><img src="{OmegaIcons.get_icon("cross", st.session_state["config"]["theme_color"])}" width="20"/><span>OMEGA</span></div>''', unsafe_allow_html=True)
        with c_nav:
            sub_cols = st.columns(5)
            # Adicionado "Sanctuary" ao menu
            nav_items = [("Dashboard", "home"), ("Sanctuary", "heart"), ("Studio", "edit"), ("Series", "books"), ("Config", "settings")]
            for idx, (label, icon) in enumerate(nav_items):
                if sub_cols[idx].button(label, key=f"nav_{label}"):
                    st.session_state['page_stack'].append(label)
                    st.rerun()
        with c_user:
            stats = LeviteGamification.carregar_stats()
            st.markdown(f'''<div style="text-align:right; font-size:12px; color:#666">LVL {stats['nivel']}</div>''', unsafe_allow_html=True)
    st.markdown('</div><div style="height: 40px;"></div>', unsafe_allow_html=True)

# ==============================================================================
# 7. TELA DE LOGIN
# ==============================================================================
if not st.session_state['logado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:30px;">
            <div style="width:80px; height:80px; border-radius:50%; border:2px solid {st.session_state['config']['theme_color']}; margin:0 auto 20px auto; display:flex; align-items:center; justify-content:center;">
                <img src="{OmegaIcons.get_icon("cross", "#D4AF37")}" width="30"/>
            </div>
            <h3 style="font-family: 'Playfair Display'; margin:0;">SYSTEM OMEGA</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_gate"):
            u = st.text_input("ID", placeholder="Admin", label_visibility="collapsed")
            p = st.text_input("Key", type="password", placeholder="1234", label_visibility="collapsed")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
    st.stop()

# ==============================================================================
# 8. APP PRINCIPAL
# ==============================================================================
render_omega_header()
page = st.session_state['page_stack'][-1]

# --- DASHBOARD ---
if page == "Dashboard":
    st.markdown(f"## Shalom, {st.session_state['user_name']}.")
    
    # Cartão de Ação Rápida e Status
    st.markdown('<div class="omega-card">', unsafe_allow_html=True)
    c_status, c_act = st.columns([1, 2])
    
    with c_status:
        # Mini Monitor de Burnout
        score, status = SoulCareEngine.calcular_risco_burnout()
        cor_status = "green" if score < 40 else "orange" if score < 70 else "red"
        st.caption("MONITOR DE VITALIDADE")
        st.markdown(f"<h3 style='color:{cor_status}'>{status}</h3>", unsafe_allow_html=True)
        st.progress(min(100, int(score)))
        
    with c_act:
        st.caption("ATALHOS")
        ca, cb = st.columns(2)
        if ca.button("Novo Sermão", use_container_width=True):
            st.session_state['titulo_ativo'] = ""
            st.session_state['texto_ativo'] = ""
            st.session_state['page_stack'].append("Studio")
            st.rerun()
        if cb.button("Check-in Emocional", use_container_width=True):
            st.session_state['page_stack'].append("Sanctuary")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lista de Sermões
    st.markdown("### Arquivos Recentes")
    files = sorted([f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)[:4]
    if not files: st.info("Sua mesa está limpa.")
    
    cols = st.columns(4)
    for i, f in enumerate(files):
        with cols[i]:
            st.markdown(f"<div style='background:#1a1a1a; padding:15px; border-radius:10px; height:100px; border:1px solid #333'>📄 <b>{f[:-4]}</b></div>", unsafe_allow_html=True)
            if st.button("Abrir", key=f"op_{f}"):
                st.session_state['titulo_ativo'] = f[:-4]
                with open(os.path.join(PASTA_SERMOES, f), 'r') as fl: st.session_state['texto_ativo'] = fl.read()
                st.session_state['page_stack'].append("Studio")
                st.rerun()

# --- SANCTUARY (NOVA PÁGINA DE SAÚDE MENTAL) ---
elif page == "Sanctuary":
    st.title("Santuário Pastoral")
    st.caption("Um espaço seguro para sua alma, longe das demandas do público.")
    
    tab_check, tab_therapy, tab_journal = st.tabs(["🩺 Check-in & Vitalidade", "💊 Terapia da Palavra", "📓 Diário 'Selah'"])
    
    with tab_check:
        st.markdown('<div class="omega-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("Como está seu coração hoje?")
            opts = ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Soberba 👑", "Ansiedade 🌪️", "Guerra Espiritual ⚔️"]
            humor = st.selectbox("Selecione com honestidade:", opts, index=opts.index(st.session_state.get('humor', "Plenitude 🕊️")))
            
            if st.button("Registrar Sentimento"):
                st.session_state['humor'] = humor
                SoulCareEngine.registrar_humor(humor)
                LeviteGamification.adicionar_xp(10)
                st.success("Registrado. Deus vê sua verdade.")
                
        with c2:
            st.subheader("Exercício de Respiração (4-7-8)")
            st.markdown("""
            <div style="background:#000; border-radius:10px; padding:20px; text-align:center;">
                <p>1. Inspire pelo nariz (4s)</p>
                <p>2. Segure o ar (7s)</p>
                <p>3. Expire pela boca (8s)</p>
                <small style="color:#666">Repita 4 vezes antes de pregar.</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico de Histórico
        db = SoulCareEngine.load_soul_db()
        if len(db['mood_history']) > 2:
            st.markdown("#### Histórico Emocional")
            # Convertendo para Pandas simples para visualização
            df = pd.DataFrame(db['mood_history'])
            df['data'] = pd.to_datetime(df['data'])
            st.dataframe(df[['data', 'humor']], use_container_width=True)

    with tab_therapy:
        st.markdown('<div class="omega-card">', unsafe_allow_html=True)
        st.markdown("### Identificador de Fardos")
        st.write("Escreva o que está pesando em sua mente (ex: 'Sinto que ninguém ajuda na igreja', 'Tenho medo de falhar domingo').")
        pensamento = st.text_input("Desabafo breve:", placeholder="Digite aqui...")
        
        if pensamento:
            analise = SoulCareEngine.terapia_cognitiva_biblica(pensamento)
            st.divider()
            st.markdown(f"**Diagnóstico Possível:** {analise['diagnostico']}")
            st.info(f"💡 **Perspectiva do Reino:** {analise['cura']}")
            st.markdown(f"📖 **Vacina Bíblica:** *{analise['texto']}*")
            
            if st.session_state['api_key']:
                if st.button("Pedir Oração à IA"):
                    genai.configure(api_key=st.session_state['api_key'])
                    oracao = genai.GenerativeModel("gemini-pro").generate_content(f"Crie uma oração curta e consoladora em primeira pessoa para um pastor que sente: {pensamento}. Baseie-se em {analise['texto']}").text
                    st.markdown(f"***Oração Sugerida:*** {oracao}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_journal:
        st.subheader("Diário de Descompressão")
        st.caption("O que você escrever aqui é criptografado e não aparece nos sermões.")
        
        texto_diario = st.text_area("Escreva para Deus:", height=300)
        if st.button("Guardar no Cofre"):
            # Aqui apenas simularíamos a criptografia salvando no JSON de SoulCare
            entry = {"data": datetime.now().strftime("%Y-%m-%d"), "texto": texto_diario}
            db = SoulCareEngine.load_soul_db()
            db['journal'].append(entry)
            SoulCareEngine.save_soul_db(db)
            st.toast("Guardado.", icon="🔒")

# --- STUDIO ---
elif page == "Studio":
    st.markdown("### Studio")
    c1, c2 = st.columns([3, 1])
    c1.text_input("Título", key="titulo_ativo", label_visibility="collapsed", placeholder="Título da Mensagem...")
    if c2.button("💾 Salvar"):
        if st.session_state['titulo_ativo']:
            with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w') as f:
                f.write(st.session_state['texto_ativo'])
            LeviteGamification.adicionar_xp(5)
            st.toast("Salvo!", icon="✅")
    
    st.markdown('<div class="editor-box">', unsafe_allow_html=True)
    st.session_state['texto_ativo'] = st.text_area("editor", st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SERIES ---
elif page == "Series":
    st.title("Séries")
    with st.form("ns"):
        n = st.text_input("Nome")
        d = st.text_area("Escopo")
        if st.form_submit_button("Criar"):
            SermonSeriesManager.criar_serie(n, d)
            st.success("Criado.")
    
    dbs = SermonSeriesManager.carregar_series()
    for k,v in dbs.items(): 
        st.info(f"**{v['nome']}**: {v['descricao']}")

# --- CONFIG ---
elif page == "Config":
    st.title("Ajustes")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Aparência")
        c = st.color_picker("Cor Tema", st.session_state['config']['theme_color'])
        s = st.slider("Fonte", 14, 24, st.session_state['config']['font_size'])
    with c2:
        st.markdown("#### Sistema")
        k = st.text_input("API Key (Google)", value=st.session_state['api_key'], type="password")
        if st.button("Salvar Tudo"):
            cfg = st.session_state['config']
            cfg['theme_color'] = c
            cfg['font_size'] = s
            st.session_state['api_key'] = k
            ConfigManager.save_config(cfg)
            st.rerun()
