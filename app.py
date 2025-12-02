import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import random
import math
import calendar
import shutil
from datetime import datetime, timedelta
from io import BytesIO
from collections import Counter

# ==============================================================================
# 0. KERNEL DE INSTALAÇÃO & INTEGRIDADE
# ==============================================================================
def system_check():
    required = ["google-generativeai", "duckduckgo-search", "streamlit-lottie", "fpdf", "Pillow"]
    install_needed = False
    for lib in required:
        try:
            module_name = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
            __import__(module_name.replace("-", "_"))
        except ImportError:
            install_needed = True
            break
    if install_needed:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + required)
        st.rerun()

system_check()

import google.generativeai as genai
from duckduckgo_search import DDGS
from streamlit_lottie import st_lottie
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

# ==============================================================================
# 1. CONFIGURAÇÃO DE SISTEMA & DIRETÓRIOS
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

PASTA_RAIZ = "Dados_Pregador_V16"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_MIDIA = os.path.join(PASTA_RAIZ, "Assets_Midia")
PASTA_USER = os.path.join(PASTA_RAIZ, "User_Profile")

# Estrutura de arquivos
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json") # Novo Sistema de Gamificação
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")

for p in [PASTA_RAIZ, PASTA_SERMOES, PASTA_CARE, PASTA_SERIES, PASTA_MIDIA, PASTA_USER]:
    os.makedirs(p, exist_ok=True)

# ==============================================================================
# 2. NOVAS ENGINES (EVOLUÇÃO DO CÓDIGO)
# ==============================================================================

class LeviteGamification:
    """
    SISTEMA DE RECOMPENSA & ASSIDUIDADE
    Gerencia XP, Níveis, Streaks (Dias consecutivos) e Conquistas.
    """
    BADGES = {
        "novico": {"nome": "Noviço", "desc": "Primeiro acesso ao sistema.", "icon": "🌱"},
        "escriba": {"nome": "Escriba Fiel", "desc": "Escreveu 5 sermões.", "icon": "📜"},
        "guardiao": {"nome": "Guardião", "desc": "7 dias de ofensiva (acesso consecutivo).", "icon": "🛡️"},
        "teologo": {"nome": "Mestre da Palavra", "desc": "Nível 10 alcançado.", "icon": "🎓"},
        "profeta": {"nome": "Voz Profética", "desc": "Usou a IA para discernimento 50 vezes.", "icon": "🦁"}
    }

    @staticmethod
    def carregar_stats():
        if not os.path.exists(DB_STATS):
            return {
                "xp": 0, "nivel": 1, 
                "sermoes_criados": 0, 
                "ultimo_login": "", 
                "streak_dias": 0,
                "badges": ["novico"],
                "uso_ia": 0
            }
        try:
            with open(DB_STATS, 'r') as f: return json.load(f)
        except: return LeviteGamification.carregar_stats() # Fallback

    @staticmethod
    def salvar_stats(dados):
        with open(DB_STATS, 'w') as f: json.dump(dados, f, indent=4)

    @staticmethod
    def processar_login():
        stats = LeviteGamification.carregar_stats()
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        if stats["ultimo_login"] != hoje:
            # Lógica de Streak
            if stats["ultimo_login"]:
                last = datetime.strptime(stats["ultimo_login"], "%Y-%m-%d")
                diff = (datetime.now() - last).days
                if diff == 1:
                    stats["streak_dias"] += 1
                elif diff > 1:
                    stats["streak_dias"] = 1 # Resetou :(
            else:
                stats["streak_dias"] = 1
                
            stats["ultimo_login"] = hoje
            stats["xp"] += 10 # XP Diário
            
            # Verificar Badge de Streak
            if stats["streak_dias"] >= 7 and "guardiao" not in stats["badges"]:
                stats["badges"].append("guardiao")
                st.toast("NOVA CONQUISTA: Guardião (7 dias)!", icon="🛡️")
            
            LeviteGamification.salvar_stats(stats)
        return stats

    @staticmethod
    def adicionar_xp(qtd, motivo="Ação"):
        stats = LeviteGamification.carregar_stats()
        stats["xp"] += qtd
        
        # Lógica de Nível (Ex: Nível = raiz quadrada do XP * 0.1)
        novo_nivel = int(math.sqrt(stats["xp"]) * 0.2) + 1
        if novo_nivel > stats["nivel"]:
            stats["nivel"] = novo_nivel
            st.toast(f"SUBIU DE NÍVEL! Agora você é Nível {novo_nivel}", icon="🆙")
            
        LeviteGamification.salvar_stats(stats)

class ShepherdEngine:
    """
    MOTOR DE CUIDADO PASTORAL & TEOLOGIA
    Analisa o estado do pregador e sugere caminhos saudáveis.
    """
    @staticmethod
    def analisar_caminho_pregacao(humor, api_key):
        """Retorna conselhos baseados no estado emocional para evitar pregação nociva."""
        conselhos = {
            "Ira 😠": {
                "perigo": "Pregar com raiva pode ferir as ovelhas em vez de curá-las.",
                "texto_cura": "Tiago 1:19-20 - 'A ira do homem não produz a justiça de Deus'.",
                "direcao": "Foque na Graça e não no Juízo hoje."
            },
            "Cansaço 🌖": {
                "perigo": "O esgotamento pode levar a uma teologia vazia e mecânica.",
                "texto_cura": "1 Reis 19:5-8 - Deus deu comida e sono a Elias antes de dar ordens.",
                "direcao": "Pregue sobre o Descanso de Deus ou a Suficiência de Cristo."
            },
            "Soberba 👑": {
                "perigo": "O púlpito não é pedestal.",
                "texto_cura": "Filipenses 2:3 - 'Considerem os outros superiores a si mesmos'.",
                "direcao": "Volte à Cruz. Pregue sobre o serviço e a humildade."
            },
            "Tristeza 😢": {
                "perigo": "Projetar sua dor na congregação sem filtro.",
                "texto_cura": "Salmos 42 - 'Por que estás abatida, ó minha alma?'.",
                "direcao": "Use sua dor como ponte para a empatia, não como lamento sem fim."
            }
        }
        
        base = conselhos.get(humor)
        if not base:
            return None # Retorno neutro
            
        # Se tiver API, enriquece
        if api_key and base:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel("gemini-pro")
                p = f"O pastor está sentindo {humor}. O perigo teológico é: {base['perigo']}. Gere uma oração curta de 2 linhas para ele fazer antes de subir ao púlpito."
                base['oracao_ia'] = m.generate_content(p).text
            except:
                base['oracao_ia'] = "Senhor, sonda meu coração."
                
        return base

# Classes Anteriores Mantidas (LiturgicalEngine, HomileticAnalytics, etc.)
class LiturgicalEngine:
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
    def get_calendario_cristao():
        hoje = datetime.now()
        ano = hoje.year
        pascoa = LiturgicalEngine.calcular_pascoa(ano)
        datas = {
            "Cinzas": pascoa - timedelta(days=46),
            "Páscoa": pascoa,
            "Pentecostes": pascoa + timedelta(days=49),
            "Advento": datetime(ano, 12, 25) - timedelta(days=(datetime(ano, 12, 25).weekday() + 22)),
            "Natal": datetime(ano, 12, 25)
        }
        cor = "#2ECC71" 
        tempo = "Tempo Comum"
        if datas["Cinzas"] <= hoje < datas["Páscoa"]:
            cor = "#8E44AD"; tempo = "Quaresma"
        elif datas["Páscoa"] <= hoje < datas["Pentecostes"]:
            cor = "#F1C40F"; tempo = "Páscoa"
        elif datas["Advento"] <= hoje < datas["Natal"]:
            cor = "#8E44AD"; tempo = "Advento"
        return {"datas": datas, "cor_atual": cor, "tempo_atual": tempo}

class HomileticAnalytics:
    @staticmethod
    def analisar_densidade(texto):
        if not texto: return {"tempo": 0, "top_words": []}
        palavras = texto.lower().split()
        n_palavras = len(palavras)
        tempo_min = math.ceil(n_palavras / 130)
        return {"palavras_total": n_palavras, "tempo_estimado": tempo_min}

class SermonSeriesManager:
    @staticmethod
    def carregar_series():
        if os.path.exists(DB_SERIES):
            try: with open(DB_SERIES, 'r') as f: return json.load(f)
            except: return {}
        return {}
    @staticmethod
    def salvar_series(data):
        with open(DB_SERIES, 'w') as f: json.dump(data, f, indent=4)
    @staticmethod
    def criar_serie(nome, descricao):
        db = SermonSeriesManager.carregar_series()
        id_serie = f"S{int(time.time())}"
        db[id_serie] = {"nome": nome, "descricao": descricao, "data_inicio": datetime.now().strftime("%d/%m/%Y")}
        SermonSeriesManager.salvar_series(db)
        # XP Reward
        LeviteGamification.adicionar_xp(50, "Nova Série Criada")

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

# ==============================================================================
# 3. GESTÃO DE ESTADO (SESSION STATE)
# ==============================================================================
DEFAULTS = {
    "logado": False, "user": "", "page_stack": ["Dashboard"], 
    "texto_ativo": "", "titulo_ativo": "", "slides": [], 
    "api_key": "", "humor": "Neutro",
    "user_avatar": None, "user_name": "Pastor",
    "config": ConfigManager.get_config()
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# Processar Login Silencioso (Gamificação)
if st.session_state['logado']:
    st.session_state['user_stats'] = LeviteGamification.processar_login()

# ==============================================================================
# 4. FRONT-END: DESIGN SYSTEM OMEGA EVOLVED
# ==============================================================================
def carregar_interface():
    # Fonte e Cores Dinâmicas baseadas na config
    font_sz = st.session_state['config']['font_size']
    gold = st.session_state['config']['theme_color']
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@600&family=Playfair+Display:wght@700&display=swap');
    
    :root {{ --bg: #050505; --panel: #111; --gold: {gold}; --border: #222; --text: #E0E0E0; }}
    
    .stApp {{ background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }}
    
    /* REMOVENDO CABEÇALHOS PADRÃO E PADDING EXCESSIVO */
    header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
    .block-container {{ padding-top: 60px !important; padding-bottom: 20px !important; max-width: 95% !important; }}
    
    /* NAVBAR */
    .omega-nav {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 20px; background: rgba(10,10,10,0.9); border-bottom: 1px solid var(--border);
        position: fixed; top: 0; left: 0; width: 100%; z-index: 999; backdrop-filter: blur(10px);
    }}
    
    /* CARDS */
    .omega-card {{
        background: var(--panel); border: 1px solid var(--border);
        border-radius: 6px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* BOTÕES */
    .stButton button {{
        background: #1a1a1a; border: 1px solid #333; color: #ccc;
        border-radius: 4px; transition: 0.3s;
    }}
    .stButton button:hover {{ border-color: var(--gold); color: var(--gold); }}
    div[data-testid="stFormSubmitButton"] button {{ background: var(--gold); color: #000; font-weight: bold; border: none; }}
    
    /* EDITOR */
    .editor-box textarea {{
        font-family: 'Playfair Display', serif !important; 
        font-size: {font_sz}px !important; line-height: 1.6;
        background: #080808 !important; border: 1px solid #222 !important; color: #ccc !important;
    }}
    
    /* GAMIFICAÇÃO & STATUS */
    .xp-bar {{ height: 4px; background: #333; width: 100%; border-radius: 2px; margin-top: 5px; }}
    .xp-fill {{ height: 100%; background: var(--gold); border-radius: 2px; }}
    .badge-icon {{ font-size: 24px; padding: 5px; background: #1a1a1a; border-radius: 50%; margin-right: 5px; border: 1px solid #333; }}
    
    </style>
    """, unsafe_allow_html=True)

def render_navbar():
    with st.container():
        c1, c2, c3 = st.columns([1.5, 3.5, 1])
        with c1:
            st.markdown(f'<span style="font-family:Cinzel; font-size:20px; color:{st.session_state["config"]["theme_color"]}">✝ OMEGA V16</span>', unsafe_allow_html=True)
        with c2:
            # Menu Horizontal
            cols = st.columns(6)
            btns = [("Dashboard", "🏠"), ("Studio", "✒️"), ("Media", "🎨"), ("Series", "📚"), ("Config", "⚙️")]
            for i, (page, icon) in enumerate(btns):
                if cols[i].button(f"{icon} {page}", key=f"nav_{page}"): navegue(page)
        with c3:
            # Stats Display
            stats = st.session_state.get('user_stats', {"nivel": 1, "xp": 0})
            st.markdown(f"""
            <div style="text-align:right; font-size:12px;">
                <b>LVL {stats['nivel']}</b> | 🔥 {stats.get('streak_dias', 0)} dias<br>
                <div class="xp-bar"><div class="xp-fill" style="width:{(stats['xp']%100)}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

def navegue(destino):
    st.session_state['page_stack'].append(destino)
    st.rerun()

# ==============================================================================
# 5. LÓGICA DE LOGIN
# ==============================================================================
if not st.session_state['logado']:
    carregar_interface()
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="width:80px; height:80px; background:#000; border:2px solid {st.session_state['config']['theme_color']}; border-radius:50%; margin:0 auto; display:flex; align-items:center; justify-content:center; font-size:40px;">✝</div>
            <h2 style="font-family:Cinzel; margin-top:15px;">PREGADOR OS</h2>
            <p style="color:#666; font-size:12px;">SYSTEM OMEGA EVOLUTION</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_gate"):
            u = st.text_input("Credencial", placeholder="Usuário")
            p = st.text_input("Chave", type="password", placeholder="Senha")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL
# ==============================================================================
carregar_interface()
render_navbar()
page = st.session_state['page_stack'][-1]
stats = st.session_state.get('user_stats', {})

# ------------------------------------------------------------------------------
# PÁGINA: DASHBOARD (COM "CARE ENGINE" e GAMIFICAÇÃO)
# ------------------------------------------------------------------------------
if page == "Dashboard":
    # 1. Cabeçalho de Boas Vindas com Gamificação
    st.markdown(f"### Olá, {st.session_state['user_name']}.")
    
    # Exibir Badges
    if "badges" in stats:
        badges_html = ""
        for b_id in stats["badges"]:
            b_info = LeviteGamification.BADGES.get(b_id, {"icon": "❓", "nome": "Unknown"})
            badges_html += f'<span title="{b_info["nome"]}" class="badge-icon">{b_info["icon"]}</span>'
        st.markdown(f"<div style='margin-bottom:20px'>{badges_html}</div>", unsafe_allow_html=True)

    # 2. SHEPHERD ENGINE (Cuidado Emocional)
    st.markdown('<div class="omega-card" style="border-left: 4px solid #D4AF37;">', unsafe_allow_html=True)
    c_feel, c_adv = st.columns([1, 2])
    
    with c_feel:
        st.markdown("**Check-in Espiritual**")
        humor_options = ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Soberba 👑", "Guerra Espiritual ⚔️"]
        novo_humor = st.selectbox("Como está seu coração antes de servir?", humor_options, index=0 if st.session_state['humor'] == "Neutro" else 0)
        
        if novo_humor != st.session_state['humor']:
            st.session_state['humor'] = novo_humor
            LeviteGamification.adicionar_xp(5, "Check-in Emocional") # Recompensa por honestidade
    
    with c_adv:
        # Análise do Shepherd Engine
        conselho = ShepherdEngine.analisar_caminho_pregacao(st.session_state['humor'], st.session_state['api_key'])
        
        if conselho:
            st.markdown(f"#### 🛡️ Guardião do Coração: {st.session_state['humor']}")
            st.warning(f"**Atenção:** {conselho['perigo']}")
            st.info(f"**Texto de Cura:** {conselho['texto_cura']}")
            st.markdown(f"**Direção Sugerida:** {conselho['direcao']}")
            if 'oracao_ia' in conselho:
                st.caption(f"Suggestion de Oração: *{conselho['oracao_ia']}*")
        else:
            cal = LiturgicalEngine.get_calendario_cristao()
            st.markdown(f"#### Tempo Litúrgico: <span style='color:{cal['cor_atual']}'>{cal['tempo_atual']}</span>", unsafe_allow_html=True)
            st.write(f"Prepare seu coração para o próximo domingo ({LiturgicalEngine.get_calendario_cristao()['datas']['Páscoa'].year}).")

    st.markdown('</div>', unsafe_allow_html=True)

    # 3. ÁREA DE TRABALHO
    c_proj, c_stats = st.columns([2, 1])
    
    with c_proj:
        st.subheader("Projetos Recentes")
        files = sorted([f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)[:3]
        
        if files:
            for f in files:
                with st.container():
                    st.markdown(f"""
                    <div style="background:#151515; padding:10px; border-radius:4px; margin-bottom:5px; display:flex; justify-content:space-between; align-items:center; border:1px solid #222;">
                        <span>📄 <b>{f.replace('.txt','')}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Abrir Editor", key=f"btn_{f}"):
                        st.session_state['titulo_ativo'] = f.replace(".txt","")
                        with open(os.path.join(PASTA_SERMOES, f), 'r') as fl: st.session_state['texto_ativo'] = fl.read()
                        navegue("Studio")
        else:
            st.info("Nenhum sermão recente. Comece algo novo.")
            if st.button("Criar Primeiro Sermão"):
                st.session_state['texto_ativo'] = ""
                st.session_state['titulo_ativo'] = ""
                navegue("Studio")

    with c_stats:
        st.subheader("Assiduidade")
        st.metric("Dias Consecutivos (Streak)", f"{stats.get('streak_dias', 0)} 🔥")
        st.metric("Total de Sermões", len(os.listdir(PASTA_SERMOES)))
        st.progress(stats.get('xp', 0) % 100 / 100)
        st.caption(f"XP para próximo nível: {100 - (stats.get('xp',0)%100)}")

# ------------------------------------------------------------------------------
# PÁGINA: STUDIO (EDITOR)
# ------------------------------------------------------------------------------
elif page == "Studio":
    st.markdown("### Studio Homilético")
    
    # Barra de Ferramentas Superior
    t1, t2, t3 = st.columns([3, 1, 1])
    with t1:
        st.session_state['titulo_ativo'] = st.text_input("Título da Mensagem", value=st.session_state['titulo_ativo'], label_visibility="collapsed", placeholder="Título...")
    with t2:
        if st.button("💾 SALVAR"):
            if st.session_state['titulo_ativo']:
                caminho = os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt")
                with open(caminho, 'w') as f: f.write(st.session_state['texto_ativo'])
                
                # Gamificação: Ganha XP por escrever
                if len(st.session_state['texto_ativo']) > 500:
                    LeviteGamification.adicionar_xp(2, "Edição de Sermão")
                st.toast("Salvo!", icon="✅")
            else:
                st.error("Defina um título.")
    with t3:
        if st.button("Sair"): navegue("Dashboard")

    c_editor, c_tools = st.columns([3, 1])
    
    with c_editor:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        txt = st.text_area("editor", value=st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.session_state['texto_ativo'] = txt
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Dados em Tempo Real
        meta = HomileticAnalytics.analisar_densidade(txt)
        st.caption(f"Palavras: {meta['palavras_total']} | Tempo Estimado: ~{meta['tempo_estimado']} min")

    with c_tools:
        st.markdown("#### Assistente")
        with st.expander("📖 Bíblia Rápida"):
            ref = st.text_input("Ref (ex: Jo 3:16)")
            if st.button("Buscar"):
                st.info("Funcionalidade Offline: Implementar JSON bíblico aqui.")
        
        with st.expander("🤖 IA Teológica"):
            p_ia = st.text_area("Pergunta à IA")
            if st.button("Consultar IA"):
                if st.session_state['api_key']:
                    try:
                        genai.configure(api_key=st.session_state['api_key'])
                        res = genai.GenerativeModel("gemini-pro").generate_content(f"Contexto Teológico Cristão: {p_ia}").text
                        st.session_state['ia_res'] = res
                        LeviteGamification.adicionar_xp(5, "Uso de IA")
                    except Exception as e:
                        st.error(f"Erro IA: {e}")
                else:
                    st.warning("Configure a API Key.")
            if 'ia_res' in st.session_state:
                st.info(st.session_state['ia_res'])

# ------------------------------------------------------------------------------
# PÁGINA: SÉRIES
# ------------------------------------------------------------------------------
elif page == "Series":
    st.title("Planejamento de Séries")
    aba1, aba2 = st.tabs(["📚 Minhas Séries", "➕ Nova Série"])
    
    with aba1:
        series = SermonSeriesManager.carregar_series()
        if not series: st.warning("Nenhuma série encontrada.")
        for sid, s in series.items():
            st.markdown(f"""
            <div class="omega-card">
                <h3>{s['nome']}</h3>
                <p>{s['descricao']}</p>
                <small style="color:#666">Início: {s['data_inicio']}</small>
            </div>
            """, unsafe_allow_html=True)
            
    with aba2:
        with st.form("form_serie"):
            nome = st.text_input("Nome da Série")
            desc = st.text_area("Objetivo / Resumo")
            if st.form_submit_button("Criar Série"):
                SermonSeriesManager.criar_serie(nome, desc)
                st.success("Série criada com sucesso!")
                st.rerun()

# ------------------------------------------------------------------------------
# PÁGINA: MEDIA (Stub)
# ------------------------------------------------------------------------------
elif page == "Media":
    st.title("Media Lab")
    st.info("O módulo de geração de imagens via IA será expandido na v17. Atualmente use o Studio para roteiros.")

# ------------------------------------------------------------------------------
# PÁGINA: CONFIGURAÇÕES (REFATORADA)
# ------------------------------------------------------------------------------
elif page == "Config":
    st.title("Configurações do Sistema")
    
    tab_pf, tab_sys = st.tabs(["👤 Perfil & Identidade", "⚙️ Sistema"])
    
    with tab_pf:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("#### Crachá Ministerial")
            img_file = st.camera_input("Capturar Foto ID")
            
            if img_file:
                # Processamento de Imagem (PIL) - Efeito "Noir"
                img = Image.open(img_file)
                img = ImageOps.grayscale(img)
                img = ImageOps.posterize(img, 2)
                st.image(img, caption="Preview Estilizado", width=150)
                # Salvar
                path_img = os.path.join(PASTA_USER, "avatar.png")
                img.save(path_img)
                st.session_state['user_avatar'] = path_img
                st.success("Identidade Atualizada!")
                
        with c2:
            st.markdown("#### Dados Pessoais")
            novo_nome = st.text_input("Nome de Exibição", value=st.session_state['user_name'])
            if st.button("Salvar Nome"):
                st.session_state['user_name'] = novo_nome
                st.rerun()
                
    with tab_sys:
        st.markdown("#### Preferências")
        cfg = st.session_state['config']
        
        n_font = st.slider("Tamanho da Fonte (Editor)", 12, 32, cfg['font_size'])
        n_color = st.color_picker("Cor de Destaque (Tema)", cfg['theme_color'])
        n_api = st.text_input("Google Gemini API Key", value=st.session_state['api_key'], type="password")
        
        if st.button("Aplicar Configurações"):
            cfg['font_size'] = n_font
            cfg['theme_color'] = n_color
            st.session_state['api_key'] = n_api
            ConfigManager.save_config(cfg)
            st.success("Configurações salvas! Recarregue a página se necessário.")
            time.sleep(1)
            st.rerun()
            
        st.divider()
        st.markdown("#### Manutenção")
        if st.button("Fazer Backup dos Dados (.zip)"):
            shutil.make_archive("backup_pregador", 'zip', PASTA_RAIZ)
            with open("backup_pregador.zip", "rb") as f:
                st.download_button("Baixar Backup", f, "backup_pregador.zip")

        if st.button("Sair (Logout)", type="primary"):
            st.session_state['logado'] = False
            st.rerun()
