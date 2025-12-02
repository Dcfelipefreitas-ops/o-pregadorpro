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
# 0. KERNEL DE INSTALAÇÃO & INTEGRIDADE (AUTO-REPAIR)
# ==============================================================================
def system_check():
    """Garante que as dependências críticas estejam instaladas."""
    required = ["google-generativeai", "streamlit-lottie", "Pillow"]
    
    install_needed = False
    for lib in required:
        try:
            # Tratamento para nomes de importação diferentes do pip
            module_name = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
            __import__(module_name.replace("-", "_"))
        except ImportError:
            install_needed = True
            break
            
    if install_needed:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + required)
        st.rerun()

system_check()

# Importações após verificação
import google.generativeai as genai
from PIL import Image, ImageOps

# ==============================================================================
# 1. CONFIGURAÇÃO DE SISTEMA & DIRETÓRIOS
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

# Definição de Caminhos
PASTA_RAIZ = "Dados_Pregador_V16"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
PASTA_SERIES = os.path.join(PASTA_RAIZ, "Series_Database")
PASTA_MIDIA = os.path.join(PASTA_RAIZ, "Assets_Midia")
PASTA_USER = os.path.join(PASTA_RAIZ, "User_Profile")

# Arquivos JSON (Bancos de Dados)
DB_SERIES = os.path.join(PASTA_SERIES, "planejamento_series.json")
DB_STATS = os.path.join(PASTA_USER, "levite_stats.json")
DB_CONFIG = os.path.join(PASTA_USER, "system_config.json")

# Criação da Infraestrutura
for p in [PASTA_RAIZ, PASTA_SERMOES, PASTA_CARE, PASTA_SERIES, PASTA_MIDIA, PASTA_USER]:
    os.makedirs(p, exist_ok=True)

# ==============================================================================
# 2. ENGINES AVANÇADAS (LÓGICA DO SISTEMA)
# ==============================================================================

class LeviteGamification:
    """
    SISTEMA DE GAMIFICAÇÃO & ASSIDUIDADE
    Gerencia XP, Níveis, Streaks (Dias consecutivos) e Insígnias.
    """
    BADGES = {
        "novico": {"nome": "Noviço", "desc": "Primeiro acesso ao sistema.", "icon": "🌱"},
        "escriba": {"nome": "Escriba Fiel", "desc": "Escreveu sermões consistentes.", "icon": "📜"},
        "guardiao": {"nome": "Guardião", "desc": "7 dias de ofensiva (acesso consecutivo).", "icon": "🛡️"},
        "teologo": {"nome": "Mestre da Palavra", "desc": "Nível 10 alcançado.", "icon": "🎓"},
        "profeta": {"nome": "Voz Profética", "desc": "Usou discernimento IA 50 vezes.", "icon": "🦁"}
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
            with open(DB_STATS, 'r') as f:
                return json.load(f)
        except:
            return {
                "xp": 0, "nivel": 1, 
                "sermoes_criados": 0, 
                "ultimo_login": "", 
                "streak_dias": 0,
                "badges": ["novico"]
            }

    @staticmethod
    def salvar_stats(dados):
        with open(DB_STATS, 'w') as f:
            json.dump(dados, f, indent=4)

    @staticmethod
    def processar_login():
        stats = LeviteGamification.carregar_stats()
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        if stats["ultimo_login"] != hoje:
            # Lógica de Streak (Ofensiva Diária)
            if stats["ultimo_login"]:
                try:
                    last = datetime.strptime(stats["ultimo_login"], "%Y-%m-%d")
                    diff = (datetime.now() - last).days
                    if diff == 1:
                        stats["streak_dias"] += 1
                    elif diff > 1:
                        stats["streak_dias"] = 1 # Resetou :(
                except:
                    stats["streak_dias"] = 1
            else:
                stats["streak_dias"] = 1
                
            stats["ultimo_login"] = hoje
            stats["xp"] += 10 # XP Diário por Login
            
            # Verificar Conquista de Streak
            if stats["streak_dias"] >= 7 and "guardiao" not in stats["badges"]:
                stats["badges"].append("guardiao")
                
            LeviteGamification.salvar_stats(stats)
        return stats

    @staticmethod
    def adicionar_xp(qtd, motivo="Ação"):
        stats = LeviteGamification.carregar_stats()
        stats["xp"] += qtd
        
        # Cálculo de Nível: Raiz quadrada do XP * fator 0.2
        novo_nivel = int(math.sqrt(stats["xp"]) * 0.2) + 1
        
        if novo_nivel > stats["nivel"]:
            stats["nivel"] = novo_nivel
            # Em um app real, aqui lançaríamos um balão de comemoração
            
        LeviteGamification.salvar_stats(stats)

class ShepherdEngine:
    """
    MOTOR DE CUIDADO PASTORAL
    Analisa o estado emocional do usuário e sugere teologia de suporte.
    """
    @staticmethod
    def analisar_caminho_pregacao(humor, api_key):
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
        
        # Enriquecimento com IA (se disponível)
        if base and api_key:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel("gemini-pro")
                p = f"O pastor está sentindo {humor}. Gere uma oração curta (max 20 palavras) de fortalecimento baseada em {base['texto_cura']}."
                base['oracao_ia'] = m.generate_content(p).text
            except:
                base['oracao_ia'] = "Senhor, restaura minhas forças para servir ao Teu povo."
                
        return base

class SermonSeriesManager:
    @staticmethod
    def carregar_series():
        if os.path.exists(DB_SERIES):
            try:
                with open(DB_SERIES, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    @staticmethod
    def salvar_series(data):
        with open(DB_SERIES, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def criar_serie(nome, descricao):
        db = SermonSeriesManager.carregar_series()
        id_serie = f"S{int(time.time())}"
        db[id_serie] = {
            "nome": nome, 
            "descricao": descricao, 
            "data_inicio": datetime.now().strftime("%d/%m/%Y")
        }
        SermonSeriesManager.salvar_series(db)
        LeviteGamification.adicionar_xp(50, "Criação de Série")

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
        with open(DB_CONFIG, 'w') as f:
            json.dump(cfg, f)

# Classes Utilitárias (Mantidas do original)
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
        pascoa = LiturgicalEngine.calcular_pascoa(hoje.year)
        datas = {
            "Cinzas": pascoa - timedelta(days=46),
            "Páscoa": pascoa,
            "Pentecostes": pascoa + timedelta(days=49),
            "Advento": datetime(hoje.year, 12, 25) - timedelta(days=(datetime(hoje.year, 12, 25).weekday() + 22)),
            "Natal": datetime(hoje.year, 12, 25)
        }
        cor = "#2ECC71" # Comum (Verde)
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
        if not texto: return {"tempo": 0, "palavras_total": 0}
        n_palavras = len(texto.split())
        tempo_min = math.ceil(n_palavras / 130)
        return {"palavras_total": n_palavras, "tempo_estimado": tempo_min}

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

if st.session_state['logado']:
    st.session_state['user_stats'] = LeviteGamification.processar_login()

# ==============================================================================
# 4. FRONT-END: DESIGN SYSTEM OMEGA EVOLVED
# ==============================================================================
def carregar_interface():
    font_sz = st.session_state['config']['font_size']
    gold = st.session_state['config']['theme_color']
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@600&family=Playfair+Display:wght@700&display=swap');
    
    :root {{ --bg: #050505; --panel: #0E0E0E; --gold: {gold}; --border: #222; --text: #E0E0E0; }}
    
    .stApp {{ background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }}
    
    /* REMOVENDO CABEÇALHOS PADRÃO */
    header, footer, [data-testid="stSidebar"] {{ display: none !important; }}
    .block-container {{ padding-top: 60px !important; padding-bottom: 30px !important; max-width: 95% !important; }}
    
    /* NAVBAR */
    .omega-nav {{
        position: fixed; top: 0; left: 0; width: 100%; height: 50px;
        background: rgba(10,10,10,0.95); border-bottom: 1px solid var(--border);
        z-index: 999; display: flex; align-items: center; justify-content: space-between;
        padding: 0 20px; backdrop-filter: blur(8px);
    }}
    
    /* CARDS */
    .omega-card {{
        background: var(--panel); border: 1px solid var(--border);
        border-radius: 8px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }}
    
    /* INPUTS & TEXTAREA */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {{
        background-color: #111 !important; border: 1px solid #333 !important; color: #eee !important;
    }}
    .editor-box textarea {{
        font-family: 'Playfair Display', serif !important; 
        font-size: {font_sz}px !important; line-height: 1.7;
        background: #080808 !important; border: none !important; padding: 30px;
    }}
    
    /* GAMIFICAÇÃO */
    .xp-container {{ width: 100%; background: #222; height: 6px; border-radius: 3px; margin-top: 5px; }}
    .xp-bar {{ height: 100%; background: var(--gold); border-radius: 3px; }}
    .badge {{ font-size: 20px; margin-right: 8px; cursor: help; }}
    
    </style>
    """, unsafe_allow_html=True)

def render_navbar():
    with st.container():
        c1, c2, c3 = st.columns([1.5, 3.5, 1])
        with c1:
            st.markdown(f'<span style="font-family:Cinzel; font-size:18px; color:{st.session_state["config"]["theme_color"]}">✝ OMEGA V16</span>', unsafe_allow_html=True)
        with c2:
            cols = st.columns(6)
            menu = [("Dashboard", "🏠"), ("Studio", "✒️"), ("Media", "🎨"), ("Series", "📚"), ("Config", "⚙️")]
            for i, (p, ico) in enumerate(menu):
                if cols[i].button(f"{ico} {p}", key=f"n_{p}"): navegue(p)
        with c3:
            stats = st.session_state.get('user_stats', {"nivel": 1, "xp": 0})
            perc = stats['xp'] % 100
            st.markdown(f"""
            <div style="text-align:right; font-size:11px; line-height:1.2">
                <b>LVL {stats['nivel']}</b> | 🔥 {stats.get('streak_dias', 0)}<br>
                <div class="xp-container"><div class="xp-bar" style="width:{perc}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

def navegue(destino):
    st.session_state['page_stack'].append(destino)
    st.rerun()

# ==============================================================================
# 5. TELA DE LOGIN
# ==============================================================================
if not st.session_state['logado']:
    carregar_interface()
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="width:70px; height:70px; border:2px solid {st.session_state['config']['theme_color']}; border-radius:50%; margin:0 auto; display:flex; align-items:center; justify-content:center; font-size:30px;">✝</div>
            <h2 style="font-family:Cinzel; margin-top:15px; color:#fff;">PREGADOR OS</h2>
            <p style="color:#666; font-size:12px; letter-spacing:2px;">SYSTEM OMEGA EVOLUTION</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Credencial", placeholder="Usuário")
            p = st.text_input("Chave", type="password", placeholder="Senha")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas.")
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL
# ==============================================================================
carregar_interface()
render_navbar()
page = st.session_state['page_stack'][-1]
stats = st.session_state.get('user_stats', {})

# ------------------------------------------------------------------------------
# PÁGINA: DASHBOARD
# ------------------------------------------------------------------------------
if page == "Dashboard":
    st.markdown(f"### Olá, {st.session_state['user_name']}.")
    
    # Área de Badges
    if "badges" in stats:
        b_html = "".join([f"<span class='badge' title='{LeviteGamification.BADGES[b]['nome']}'>{LeviteGamification.BADGES[b]['icon']}</span>" for b in stats["badges"] if b in LeviteGamification.BADGES])
        st.markdown(f"<div>{b_html}</div>", unsafe_allow_html=True)
    
    # 1. Shepherd Engine (Cuidado Emocional)
    st.markdown('<div class="omega-card" style="border-left: 4px solid #D4AF37;">', unsafe_allow_html=True)
    col_feel, col_advice = st.columns([1, 2])
    
    with col_feel:
        st.caption("COMO ESTÁ SEU ESPÍRITO?")
        opts = ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Soberba 👑", "Guerra Espiritual ⚔️"]
        idx = 0
        if st.session_state['humor'] in opts: idx = opts.index(st.session_state['humor'])
        
        novo = st.selectbox("Status Emocional", opts, index=idx, label_visibility="collapsed")
        
        if novo != st.session_state['humor']:
            st.session_state['humor'] = novo
            LeviteGamification.adicionar_xp(5, "Check-in Emocional")
            st.rerun()

    with col_advice:
        advice = ShepherdEngine.analisar_caminho_pregacao(st.session_state['humor'], st.session_state['api_key'])
        if advice:
            st.markdown(f"#### Direção Pastoral")
            st.warning(f"**Cuidado:** {advice['perigo']}")
            st.info(f"**Texto de Refúgio:** {advice['texto_cura']}")
            if 'oracao_ia' in advice:
                st.markdown(f"*Orando:* {advice['oracao_ia']}")
        else:
            cal = LiturgicalEngine.get_calendario_cristao()
            st.markdown(f"#### Tempo Litúrgico: <span style='color:{cal['cor_atual']}'>{cal['tempo_atual']}</span>", unsafe_allow_html=True)
            st.write("Seu coração está equilibrado. Bom momento para estudos profundos.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Projetos e Atalhos
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Mesa de Trabalho")
        files = sorted([f for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)[:3]
        
        if files:
            for f in files:
                with st.container():
                    st.markdown(f"<div style='background:#151515; padding:12px; border-radius:5px; margin-bottom:8px; border:1px solid #333;'>📄 <b>{f.replace('.txt','')}</b></div>", unsafe_allow_html=True)
                    if st.button("Editar", key=f"edit_{f}"):
                        st.session_state['titulo_ativo'] = f.replace(".txt","")
                        with open(os.path.join(PASTA_SERMOES, f), 'r') as fl: 
                            st.session_state['texto_ativo'] = fl.read()
                        navegue("Studio")
        else:
            st.info("Nenhum sermão encontrado.")
            if st.button("Criar Primeiro Estudo"):
                st.session_state['titulo_ativo'] = ""
                st.session_state['texto_ativo'] = ""
                navegue("Studio")

    with c2:
        st.subheader("Painel Levita")
        st.metric("Sermões no Acervo", len(os.listdir(PASTA_SERMOES)))
        st.metric("Dias Consecutivos", f"{stats.get('streak_dias',0)} 🔥")
        
        if st.session_state['user_avatar']:
            st.image(st.session_state['user_avatar'], caption="ID Ministerial", width=120)

# ------------------------------------------------------------------------------
# PÁGINA: STUDIO
# ------------------------------------------------------------------------------
elif page == "Studio":
    # Header
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1:
        st.session_state['titulo_ativo'] = st.text_input("Título", value=st.session_state['titulo_ativo'], placeholder="Título da Mensagem...", label_visibility="collapsed")
    with c2:
        if st.button("SALVAR", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                path = os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt")
                with open(path, 'w') as f:
                    f.write(st.session_state['texto_ativo'])
                LeviteGamification.adicionar_xp(2, "Editor")
                st.toast("Salvo com sucesso!", icon="💾")
            else:
                st.error("Digite um título.")
    with c3:
        if st.button("X"): navegue("Dashboard")

    # Área de Edição
    col_edit, col_tools = st.columns([3, 1])
    
    with col_edit:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        txt = st.text_area("main_editor", value=st.session_state['texto_ativo'], height=600, label_visibility="collapsed")
        st.session_state['texto_ativo'] = txt
        st.markdown('</div>', unsafe_allow_html=True)
        
        analytics = HomileticAnalytics.analisar_densidade(txt)
        st.caption(f"Palavras: {analytics['palavras_total']} | Tempo estimado: {analytics['tempo_estimado']} min")

    with col_tools:
        st.markdown("### Auxílio IA")
        prompt = st.text_area("Consultar Teologia", placeholder="Ex: Contexto histórico de Filipenses 4...")
        if st.button("Pesquisar"):
            if st.session_state['api_key']:
                with st.spinner("Analisando escrituras..."):
                    try:
                        genai.configure(api_key=st.session_state['api_key'])
                        model = genai.GenerativeModel("gemini-pro")
                        res = model.generate_content(f"Aja como um teólogo conservador erudito. Responda: {prompt}").text
                        st.session_state['ia_cache'] = res
                        LeviteGamification.adicionar_xp(10, "Estudo IA")
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.error("Configure a API Key em Config.")
        
        if 'ia_cache' in st.session_state:
            st.info(st.session_state['ia_cache'])

# ------------------------------------------------------------------------------
# PÁGINA: SÉRIES
# ------------------------------------------------------------------------------
elif page == "Series":
    st.title("Planejamento de Séries")
    t1, t2 = st.tabs(["Minhas Séries", "Nova Série"])
    
    with t1:
        db = SermonSeriesManager.carregar_series()
        if not db: st.info("Nenhuma série ativa.")
        for k, v in db.items():
            with st.expander(f"📚 {v['nome']} ({v['data_inicio']})"):
                st.write(v['descricao'])
                
    with t2:
        with st.form("new_series"):
            n = st.text_input("Nome da Série")
            d = st.text_area("Descrição / Tema Central")
            if st.form_submit_button("Criar Estrutura"):
                SermonSeriesManager.criar_serie(n, d)
                st.success("Série Criada!")
                st.rerun()

# ------------------------------------------------------------------------------
# PÁGINA: MEDIA
# ------------------------------------------------------------------------------
elif page == "Media":
    st.title("Media Lab")
    st.info("Módulo de criação de slides e artes sociais em desenvolvimento para V17.")

# ------------------------------------------------------------------------------
# PÁGINA: CONFIGURAÇÕES
# ------------------------------------------------------------------------------
elif page == "Config":
    st.title("Configurações")
    
    tab_pessoal, tab_sistema = st.tabs(["👤 Identidade", "⚙️ Sistema"])
    
    with tab_pessoal:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Crachá Digital (ID)")
            foto = st.camera_input("Tire uma foto para seu perfil")
            if foto:
                img = Image.open(foto)
                # Filtro Estiloso
                img = ImageOps.grayscale(img)
                img = ImageOps.posterize(img, 3)
                
                path = os.path.join(PASTA_USER, "avatar.png")
                img.save(path)
                st.session_state['user_avatar'] = path
                st.success("Foto atualizada com estilo!")
                st.image(img, width=150)
                
        with c2:
            st.markdown("#### Dados")
            nome = st.text_input("Nome de Tratamento", st.session_state['user_name'])
            if st.button("Atualizar Nome"):
                st.session_state['user_name'] = nome
                st.rerun()

    with tab_sistema:
        cfg = st.session_state['config']
        
        n_font = st.slider("Tamanho Fonte Editor", 14, 30, cfg['font_size'])
        n_cor = st.color_picker("Cor do Tema", cfg['theme_color'])
        n_api = st.text_input("Chave API Google (Gemini)", value=st.session_state['api_key'], type="password")
        
        if st.button("Salvar Configurações"):
            cfg['font_size'] = n_font
            cfg['theme_color'] = n_cor
            st.session_state['api_key'] = n_api
            ConfigManager.save_config(cfg)
            st.success("Salvo! Reiniciando interface...")
            time.sleep(1)
            st.rerun()
            
        st.divider()
        if st.button("Fazer Backup (.zip)"):
            shutil.make_archive("backup_pregador", 'zip', PASTA_RAIZ)
            with open("backup_pregador.zip", "rb") as f:
                st.download_button("Download Backup", f, "backup_pregador.zip")
                
        if st.button("SAIR DO SISTEMA", type="primary"):
            st.session_state['logado'] = False
            st.rerun()
