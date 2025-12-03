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
# 0. KERNEL DE INICIALIZAÇÃO E INTEGRIDADE (SYSTEM CORE)
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo de inicialização do Sistema O Pregador.
    Responsável por garantir que todas as bibliotecas teológicas e de sistema
    estejam presentes antes da execução da liturgia digital.
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
        """Verifica a integridade do ambiente de execução."""
        install_queue = []
        for lib in SystemOmegaKernel.REQUIRED_LIBS:
            try:
                # Mapeamento de imports vs nomes de pacotes no pip
                module_name = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(module_name.replace("-", "_"))
            except ImportError:
                install_queue.append(lib)
        
        if install_queue:
            placeholder = st.empty()
            with placeholder.container():
                st.markdown("### ⚙️ RESTAURANDO SISTEMA OMEGA")
                st.markdown(f"Atualizando bibliotecas vitais... ({len(install_queue)} pendentes)")
                st.progress(0)
                for idx, lib in enumerate(install_queue):
                    SystemOmegaKernel._install_quietly(lib)
                    st.progress((idx + 1) / len(install_queue))
            placeholder.empty()
            st.rerun()

# Executa Verificação de Integridade
SystemOmegaKernel.integrity_check()

# Importações Seguras
import google.generativeai as genai
import pandas as pd
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

# ==============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE E DIRETÓRIOS (V17 REFORMED)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

# Definição de Caminhos Absolutos
PASTA_RAIZ = "Dados_Pregador_V17_Reformed"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes_Expositivos")
PASTA_CARE = os.path.join(PASTA_RAIZ, "Gabinete_Pastoral")
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_MIDIA = os.path.join(PASTA_RAIZ, "Assets_Midia")
PASTA_USER = os.path.join(PASTA_RAIZ, "Perfil_Pastor")
PASTA_LOGS = os.path.join(PASTA_RAIZ, "System_Logs")

# Bancos de Dados JSON (Persistência)
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json")
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")
DB_SOUL = os.path.join(PASTA_CARE, "saude_mental_pastoral.json")

# Criação da Infraestrutura de Diretórios
for p in [PASTA_RAIZ, PASTA_SERMOES, PASTA_CARE, PASTA_SERIES, PASTA_MIDIA, PASTA_USER, PASTA_LOGS]:
    os.makedirs(p, exist_ok=True)

# ==============================================================================
# 2. DESIGN SYSTEM OMEGA (CSS RESTAURADO & APRIMORADO)
# ==============================================================================
def inject_css(theme_color="#D4AF37", font_size=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@500;700&family=Cinzel:wght@400;700&display=swap');
        
        :root {{
            --bg-deep: #030303;
            --bg-panel: #0E0E0E;
            --gold: {theme_color};
            --gold-dim: #8a7324;
            --text-main: #EAEAEA;
            --border: #222;
        }}
        
        .stApp {{ background-color: var(--bg-deep); color: var(--text-main); font-family: 'Inter', sans-serif; }}
        
        /* Ocultar Elementos Padrão */
        header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
        .block-container {{ padding-top: 80px !important; max-width: 1200px !important; }}

        /* --- NAVBAR FLUTUANTE (ESTILO APPLE/OMEGA) --- */
        .omega-nav {{
            position: fixed; top: 0; left: 0; width: 100%; height: 60px;
            background: rgba(14, 14, 14, 0.9); backdrop-filter: blur(15px);
            border-bottom: 1px solid var(--border); z-index: 9999;
            display: flex; align-items: center; justify-content: space-between; padding: 0 30px;
        }}

        /* --- ANIMAÇÃO DE LOGIN (RESTAURADA) --- */
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
        
        /* --- CARDS & PANELS --- */
        .omega-card {{
            background: var(--bg-panel); border: 1px solid var(--border);
            border-radius: 8px; padding: 25px; margin-bottom: 20px;
            transition: transform 0.2s;
        }}
        .omega-card:hover {{ border-color: #333; }}

        /* --- TYPOGRAPHY & EDITOR --- */
        .editor-box textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_size}px !important;
            line-height: 1.8 !important;
            background-color: #050505 !important;
            border: 1px solid #222 !important;
            color: #ddd !important;
            padding: 20px !important;
        }}
        
        /* --- UTILS --- */
        .stTextInput input, .stSelectbox div {{
            background-color: #111 !important; border: 1px solid #333 !important; color: white !important;
        }}
        .badge-icon {{ font-size: 20px; margin-right: 5px; }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES TEOLÓGICOS E PSICOLÓGICOS (LÓGICA EXPANDIDA)
# ==============================================================================

class ReformedTheologyEngine:
    """
    Motor de Análise Teológica Reformada (Genebra).
    Analisa textos para garantir alinhamento com os 5 Solas e a Confissão de Fé.
    """
    
    PALAVRAS_CHAVE_ALERTA = {
        "prosperidade": "Cuidado com a Teologia da Glória. Foque na Teologia da Cruz.",
        "eu determino": "Lembre-se da Soberania de Deus. Nós rogamos, Ele determina.",
        "mérito": "Sola Gratia. Não há mérito humano na salvação.",
        "livre arbítrio": "Considere a Depravação Total e a Eleição Incondicional (Romanos 9).",
        "vitória financeira": "O Evangelho não garante riquezas terrenas."
    }
    
    CATECISMO_HEIDELBERG_REF = {
        "consolo": "Qual é o seu único consolo na vida e na morte? Que não pertenço a mim mesmo...",
        "lei": "A Lei serve para nos mostrar nosso pecado e miséria.",
        "gratidao": "Boas obras são fruto da gratidão, não causa da salvação."
    }

    @staticmethod
    def analisar_ortodoxia(texto):
        """Varre o texto em busca de desvios doutrinários comuns."""
        alertas = []
        texto_lower = texto.lower()
        
        for termo, aviso in ReformedTheologyEngine.PALAVRAS_CHAVE_ALERTA.items():
            if termo in texto_lower:
                alertas.append(f"⚠️ **Termo '{termo}':** {aviso}")
                
        # Análise de Centralidade de Cristo
        if "jesus" not in texto_lower and "cristo" not in texto_lower and "senhor" not in texto_lower:
            alertas.append("🔴 **Alerta Crítico:** O texto parece não mencionar explicitamente a Cristo. Pregue Cristo, e este crucificado.")
            
        return alertas if alertas else ["✅ O texto parece teologicamente seguro e centrado."]

class PastoralPsychologyEngine:
    """
    Motor de Saúde Mental Pastoral (Cuidado da Alma).
    Baseado em princípios noutéticos e psicologia cognitiva cristã.
    """
    
    @staticmethod
    def carregar_dados():
        if not os.path.exists(DB_SOUL):
            dados_iniciais = {"historico_humor": [], "diario": [], "metricas": {"cansaco": 0, "alegria": 0}}
            try:
                with open(DB_SOUL, 'w') as f:
                    json.dump(dados_iniciais, f)
            except:
                pass
            return dados_iniciais
            
        try:
            with open(DB_SOUL, 'r') as f:
                return json.load(f)
        except Exception:
            return {"historico_humor": [], "diario": []}

    @staticmethod
    def salvar_dados(dados):
        try:
            with open(DB_SOUL, 'w') as f:
                json.dump(dados, f, indent=4)
        except Exception as e:
            st.error(f"Erro ao salvar dados da alma: {e}")

    @staticmethod
    def diagnosticar_estado(humor_atual):
        """
        Retorna uma análise baseada no humor atual e no histórico.
        """
        analises = {
            "Ira 😠": {
                "diagnostico": "Coração Inflamado",
                "texto_biblico": "Efésios 4:26 - 'Irai-vos, e não pequeis; não se ponha o sol sobre a vossa ira'.",
                "acao_sugerida": "Ore pelos que te ofenderam antes de escrever o sermão. A ira do homem não produz a justiça de Deus."
            },
            "Cansaço 🌖": {
                "diagnostico": "Esgotamento Ministerial (Elias)",
                "texto_biblico": "Marcos 6:31 - 'Vinde vós, aqui à parte, a um lugar deserto, e repousai um pouco'.",
                "acao_sugerida": "Não tente ser o Messias hoje. Apenas seja o jumento que O carrega. Descanse."
            },
            "Ansiedade 🌪️": {
                "diagnostico": "Fardo do Futuro",
                "texto_biblico": "Mateus 6:34 - 'Não vos inquieteis pelo dia de amanhã'.",
                "acao_sugerida": "Escreva 3 coisas que estão sob controle de Deus e fora do seu. Entregue."
            },
            "Soberba 👑": {
                "diagnostico": "Perigo de Queda",
                "texto_biblico": "1 Coríntios 10:12 - 'Aquele que pensa estar em pé, cuide para que não caia'.",
                "acao_sugerida": "Lembre-se de onde Deus te tirou. Humilhe-se sob a potente mão de Deus."
            },
            "Tristeza 😢": {
                "diagnostico": "Vale de Baca",
                "texto_biblico": "Salmos 42:5 - 'Por que estás abatida, ó minha alma? Espera em Deus'.",
                "acao_sugerida": "A tristeza é um hóspede, não o dono da casa. Leia um Salmo de lamento."
            }
        }
        return analises.get(humor_atual, {
            "diagnostico": "Estado Estável",
            "texto_biblico": "Filipenses 4:7",
            "acao_sugerida": "Prossiga para o alvo com gratidão."
        })

    @staticmethod
    def registrar_checkin(humor):
        db = PastoralPsychologyEngine.carregar_dados()
        entrada = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "humor": humor
        }
        db["historico_humor"].append(entrada)
        
        # Análise de Tendência de Burnout
        ultimos_10 = db["historico_humor"][-10:]
        contagem_negativa = sum(1 for x in ultimos_10 if x['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        
        alerta_burnout = False
        if len(ultimos_10) >= 5 and contagem_negativa >= 7:
            alerta_burnout = True
            
        PastoralPsychologyEngine.salvar_dados(db)
        return alerta_burnout

class LeviteGamification:
    """Sistema de Recompensa e Assiduidade."""
    BADGES = {
        "novico": {"nome": "Noviço", "icon": "🌱"},
        "reformador": {"nome": "Reformador", "icon": "🔨"}, # 50 sermões
        "teologo": {"nome": "Teólogo", "icon": "📚"},
        "pastor": {"nome": "Pastor de Almas", "icon": "🐑"},
        "guardiao": {"nome": "Guardião da Doutrina", "icon": "🛡️"}
    }

    @staticmethod
    def carregar_stats():
        if os.path.exists(DB_STATS):
            try: 
                with open(DB_STATS, 'r') as f: return json.load(f)
            except: pass
        return {"xp": 0, "nivel": 1, "badges": ["novico"], "streak": 0, "last_login": ""}

    @staticmethod
    def salvar_stats(stats):
        with open(DB_STATS, 'w') as f: json.dump(stats, f)

    @staticmethod
    def add_xp(amount):
        stats = LeviteGamification.carregar_stats()
        stats['xp'] += amount
        # Lógica de Nível (Raiz Quadrada)
        stats['nivel'] = int(math.sqrt(stats['xp']) * 0.2) + 1
        LeviteGamification.salvar_stats(stats)

class ConfigManager:
    @staticmethod
    def get_config():
        defaults = {"font_size": 18, "theme_color": "#D4AF37", "ai_temp": 0.7}
        try:
            if os.path.exists(DB_CONFIG):
                with open(DB_CONFIG, 'r') as f:
                    return {**defaults, **json.load(f)}
        except: pass
        return defaults

    @staticmethod
    def save_config(cfg):
        try:
            with open(DB_CONFIG, 'w') as f:
                json.dump(cfg, f)
        except Exception as e:
            st.error(f"Erro ao salvar config: {e}")

class SermonSeriesManager:
    @staticmethod
    def carregar():
        try:
            if os.path.exists(DB_SERIES):
                with open(DB_SERIES, 'r') as f: return json.load(f)
        except: return {}
        return {}

    @staticmethod
    def criar(nome, desc):
        db = SermonSeriesManager.carregar()
        db[f"S{int(time.time())}"] = {"nome": nome, "descricao": desc, "inicio": datetime.now().strftime("%d/%m/%Y")}
        with open(DB_SERIES, 'w') as f: json.dump(db, f)

# ==============================================================================
# 4. GESTÃO DE SESSÃO (SESSION STATE)
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
# 5. UI COMPONENTS: NAVBAR & HEADER
# ==============================================================================
def render_navbar():
    with st.container():
        # Layout em colunas invisíveis
        c1, c2, c3 = st.columns([1.5, 3.5, 1])
        
        with c1:
            st.markdown(f'<span style="font-family:Cinzel; font-weight:700; color:{st.session_state["config"]["theme_color"]}; font-size:20px;">✝ SYSTEM OMEGA</span>', unsafe_allow_html=True)
            
        with c2:
            # Menu Horizontal
            cols = st.columns(6)
            menu_items = [
                ("Dashboard", "🏠"), 
                ("Gabinete", "🛋️"), # Novo Módulo Saúde Mental
                ("Studio", "📜"), 
                ("Séries", "📚"), 
                ("Config", "⚙️")
            ]
            for i, (page, icon) in enumerate(menu_items):
                if cols[i].button(f"{icon} {page}", key=f"nav_{page}"):
                    st.session_state['page_stack'].append(page)
                    st.rerun()
                    
        with c3:
            stats = LeviteGamification.carregar_stats()
            st.markdown(f"""
            <div style="text-align:right; font-size:12px; color:#888;">
                <b>LVL {stats['nivel']}</b> | Reformado
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 6. TELA DE LOGIN (RESTAURADA - CÍRCULO PULSANTE DOURADO)
# ==============================================================================
if not st.session_state['logado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 0.8, 1])
    
    with c2:
        # AQUI ESTÁ A RESTAURAÇÃO DO DESIGN SOLICITADO
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
            user = st.text_input("Identidade", label_visibility="collapsed", placeholder="IDENTIFICAÇÃO")
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
# 7. APLICAÇÃO PRINCIPAL (MAIN APP)
# ==============================================================================
render_navbar()
page = st.session_state['page_stack'][-1] if st.session_state['page_stack'] else "Dashboard"

# >>>
