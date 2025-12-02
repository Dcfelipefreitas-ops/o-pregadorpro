import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import random
import calendar
import re
from datetime import datetime, timedelta
from io import BytesIO
from collections import Counter

# ==============================================================================
# MÓDULO 0: KERNEL DE INSTALAÇÃO & DEPENDÊNCIAS
# ==============================================================================
def verify_integrity_and_install():
    """Verifica e instala dependências vitais do sistema sem travar."""
    required_libs = [
        "google-generativeai", "duckduckgo-search", 
        "streamlit-lottie", "fpdf", "Pillow"
    ]
    
    install_queue = []
    for lib in required_libs:
        import_name = lib.replace("-", "_").replace("google_generativeai", "google.generativeai").replace("Pillow", "PIL")
        try:
            __import__(import_name)
        except ImportError:
            install_queue.append(lib)
    
    if install_queue:
        # Modo silencioso de instalação
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + install_queue)
        st.rerun()

verify_integrity_and_install()

# Importações Pós-Verificação
import google.generativeai as genai
from duckduckgo_search import DDGS
from streamlit_lottie import st_lottie
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

# ==============================================================================
# MÓDULO 1: CONFIGURAÇÃO DE SISTEMA E ARQUIVOS
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | System Omega", 
    layout="wide", 
    page_icon="✝️", 
    initial_sidebar_state="collapsed"
)

# Definição de Arquitetura de Pastas (Banco de Dados Local)
PASTAS_SISTEMA = {
    "root": "Dados_Pregador",
    "sermoes": "Dados_Pregador/Sermoes",
    "care": "Dados_Pregador/PastoralCare",
    "series": "Dados_Pregador/Series",
    "assets": "Dados_Pregador/Assets",
    "logs": "Dados_Pregador/Logs"
}

for _, path in PASTAS_SISTEMA.items():
    os.makedirs(path, exist_ok=True)

# Caminhos de Arquivos Persistentes
DB_ORACOES = os.path.join(PASTAS_SISTEMA["care"], "oracoes_db.json")
DB_CALENDARIO = os.path.join(PASTAS_SISTEMA["root"], "agenda_liturgica.json")
DB_LOGS = os.path.join(PASTAS_SISTEMA["logs"], "access_log.txt")

# ==============================================================================
# MÓDULO 2: CLASSES DE LÓGICA AVANÇADA (BACKEND)
# ==============================================================================

class LiturgicalEngine:
    """Gerencia lógica de calendário, datas de culto e séries."""
    
    @staticmethod
    def get_proximo_domingo():
        hoje = datetime.now()
        dias_ate_domingo = (6 - hoje.weekday()) % 7
        if dias_ate_domingo == 0: dias_ate_domingo = 7 # Próximo, não hoje
        return hoje + timedelta(days=dias_ate_domingo)

    @staticmethod
    def salvar_evento(titulo, data, tipo="Culto"):
        eventos = []
        if os.path.exists(DB_CALENDARIO):
            with open(DB_CALENDARIO, 'r') as f:
                try: eventos = json.load(f)
                except: pass
        eventos.append({"titulo": titulo, "data": str(data), "tipo": tipo})
        with open(DB_CALENDARIO, 'w') as f:
            json.dump(eventos, f)

    @staticmethod
    def ler_agenda():
        if os.path.exists(DB_CALENDARIO):
            with open(DB_CALENDARIO, 'r') as f: return json.load(f)
        return []

class BibleAnalytics:
    """Ferramentas de análise textual para sermões."""
    
    @staticmethod
    def contar_palavras_frequentes(texto):
        if not texto: return []
        # Limpeza básica regex
        palavras = re.findall(r'\w+', texto.lower())
        stopwords = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'tem', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está']
        palavras_uteis = [p for p in palavras if p not in stopwords and len(p) > 2]
        return Counter(palavras_uteis).most_common(5)

    @staticmethod
    def tempo_leitura_estimado(texto):
        palavras = len(texto.split())
        # Média de fala: 130 palavras por minuto
        minutos = words = palavras // 130
        return max(1, minutos)

class SecurityLog:
    """Sistema de logs silencioso."""
    @staticmethod
    def log_access(user):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"LOGIN_SUCCESS | User: {user} | Time: {timestamp}\n"
        with open(DB_LOGS, "a") as f:
            f.write(entry)

# ==============================================================================
# MÓDULO 3: DESIGN SYSTEM (VISUAL + CSS CORRIGIDO)
# ==============================================================================
def carregar_estilo_visual():
    st.markdown(f"""
    <style>
    /* FONTS IMPORT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;900&family=Cinzel:wght@400;700&family=Merriweather:ital,wght@0,300;0,700;1,400&display=swap');
    
    /* VARIAVEIS DE TEMA - HIGH CONTRAST DARK */
    :root {{ 
        --bg-space: #050505; 
        --bg-panel: #111111;
        --border-subtle: #222;
        --gold-primary: #D4AF37;
        --gold-glow: rgba(212, 175, 55, 0.4);
        --text-main: #ECECEC;
        --danger: #FF4B4B;
    }}
    
    /* CONFIG GERAL */
    .stApp {{ background-color: var(--bg-space); color: var(--text-main); font-family: 'Inter', sans-serif; }}
    
    [data-testid="stSidebar"] {{ display: none !important; }}
    header, footer {{ display: none !important; }}
    
    /* --- BARRA DE NAVEGAÇÃO HORIZONTAL INTELIGENTE --- */
    .smart-nav {{
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background: rgba(10,10,12, 0.95); backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border-subtle);
        z-index: 99999; padding: 0 30px;
        display: flex; align-items: center; justify-content: space-between;
    }}
    
    /* BOTÕES DA NAV */
    div.stButton > button {{
        background: transparent; border: 1px solid transparent; color: #888;
        text-transform: uppercase; font-size: 12px; letter-spacing: 1px; font-weight: 600;
        transition: all 0.3s ease; margin: 0 4px; padding: 0.5rem 1rem;
    }}
    div.stButton > button:hover {{
        background: rgba(255,255,255,0.05); color: #FFF; border: 1px solid #333;
    }}
    div.stButton > button:focus {{ color: var(--gold-primary); }}

    /* BOTÕES DE AÇÃO (PRIMARY) */
    .primary-action button {{
        background: linear-gradient(135deg, #1f1f1f 0%, #111 100%) !important;
        border: 1px solid #444 !important; color: #fff !important;
    }}
    
    /* --- EFEITO BOLINHA PULSANTE (LOGIN) --- */
    @keyframes pulse-ring {{
        0% {{ transform: scale(0.8); opacity: 0.8; box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.7); }}
        70% {{ transform: scale(1); opacity: 1; box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); }}
        100% {{ transform: scale(0.8); opacity: 0.8; box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }}
    }}
    
    .login-circle-container {{
        position: relative; width: 120px; height: 120px; margin: 0 auto 30px auto;
        display: flex; align-items: center; justify-content: center;
        background: #000; border-radius: 50%;
        border: 2px solid var(--gold-primary);
        animation: pulse-ring 3s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
    }}
    
    .cross-symbol {{ font-size: 60px; color: var(--gold-primary); z-index: 2; }}

    /* --- EDITOR --- */
    .stTextArea textarea {{
        background-color: #080808 !important; border: 1px solid #222 !important;
        color: #e0e0e0 !important; font-family: 'Merriweather', serif;
        font-size: 19px !important; line-height: 1.8;
        padding: 40px; box-shadow: inset 0 0 20px #000;
        border-radius: 4px;
    }}
    
    /* --- AVATAR E UI ELEMENTS --- */
    .user-ball {{
        width: 35px; height: 35px; border-radius: 50%;
        border: 2px solid #333; background-size: cover; background-position: center;
        cursor: pointer; transition: transform 0.2s;
    }}
    .user-ball:hover {{ border-color: var(--gold-primary); transform: scale(1.1); }}

    /* ESPAÇAMENTO DO TOPO PARA CONTEÚDO */
    .block-container {{ padding-top: 80px !important; }}
    
    /* CONTAINERS GERAIS */
    .glass-panel {{
        background: #111; border: 1px solid #222; border-radius: 8px; padding: 25px;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 4: GESTÃO DE ESTADO (SESSION MANAGER)
# ==============================================================================
STATE_TEMPLATE = {
    "logado": False, "user": "", 
    "page_stack": ["Dashboard"], 
    "texto_ativo": "", 
    "titulo_ativo": "", 
    "slides": [], 
    "api_key": "", 
    "theme_size": 18, 
    "stats_sermoes": 0,
    "historico_biblia": [], 
    "humor": "Neutro",
    "tocar_som": False,
    "user_avatar": None, 
    "user_name": "Pastor"
}

for k, v in STATE_TEMPLATE.items():
    if k not in st.session_state: st.session_state[k] = v

# Atualiza stats dinamicamente
st.session_state['stats_sermoes'] = len(os.listdir(PASTA_SERMOES))

# ==============================================================================
# MÓDULO 5: HELPERS GRÁFICOS (MEDIA ENGINE)
# ==============================================================================
def render_post_social(texto, imagem_bg=None, estilo="Classic"):
    """Motor de renderização gráfica usando Pillow"""
    W, H = 1080, 1080
    
    # 1. Background Layer
    if imagem_bg:
        img = Image.open(imagem_bg).convert("RGB")
        img = ImageOps.fit(img, (W, H))
        img = img.filter(ImageFilter.GaussianBlur(3))
        # Escurecer para contraste
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.4)
    else:
        # Fundo Procedural Elegante
        img = Image.new("RGB", (W, H), "#0f0f0f")
        draw = ImageDraw.Draw(img)
        # Borda Dourada
        draw.rectangle([20, 20, W-20, H-20], outline="#D4AF37", width=5)

    draw = ImageDraw.Draw(img)
    
    # 2. Text Layer
    # Carregamento seguro de fontes
    try:
        font_path = "arial.ttf" # Fallback windows
        font_main = ImageFont.truetype(font_path, 70)
        font_footer = ImageFont.truetype(font_path, 30)
    except:
        font_main = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Wrap Text Logic Simplificado
    margin = 100
    text_y = H / 2 - 100 # Approx center
    for line in texto.split("\n"):
        # Centralizar (Lógica simplificada pois Pillow puro requer textbbox)
        # Aqui desenhamos fixo esquerda com margem, profissional e limpo.
        draw.text((margin, text_y), line, font=font_main, fill="#FFFFFF")
        text_y += 85

    # 3. Branding Layer
    draw.text((W - 300, H - 100), "O PREGADOR APP", font=font_footer, fill="#D4AF37")
    
    # Output Buffer
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==============================================================================
# MÓDULO 6: INTEGRAÇÃO SENSORIAL (ÁUDIO & IA)
# ==============================================================================
def tocar_pad_angelical():
    sound_url = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=angelic-pad-15337.mp3"
    st.markdown(f"""
        <audio autoplay style="display:none;">
            <source src="{sound_url}" type="audio/mp3">
        </audio>
        <script>
            const audio = document.querySelector("audio");
            audio.volume = 0.4;
            setTimeout(() => {{ audio.pause(); }}, 5000);
        </script>
    """, unsafe_allow_html=True)

def cerebro_ia(prompt, key, context="teologo"):
    if not key: return "⚠️ IA Offline: Insira API Key nas Configurações."
    try:
        genai.configure(api_key=key)
        sys_msg = "Você é um assistente acadêmico cristão."
        
        if context == "emocional":
            sys_msg = f"O pastor sente: {st.session_state['humor']}. Responda como um 'Pastor de Pastores' (Mentor Sábio). Dê um conselho curto, empático e um texto bíblico balsâmico."
        elif context == "critico":
            sys_msg = "Analise o texto homileticamente. Está cristocêntrico? Está claro? O tom é agressivo ou amoroso?"

        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys_msg}\nInput: {prompt}").text
    except Exception as e: return f"Erro Neural: {e}"

# ==============================================================================
# MÓDULO 7: ROTEAMENTO & NAVEGAÇÃO
# ==============================================================================
def render_header_navbar():
    with st.container():
        # Grids: Logo | Espaço | Menu Buttons | Espaço | Perfil
        c_logo, c_sp1, c_menu1, c_menu2, c_menu3, c_menu4, c_sp2, c_pf = st.columns([1.5, 0.5, 1, 1, 1, 1, 3, 0.5])
        
        with c_logo:
            st.markdown(f'<span style="font-family:Cinzel; font-weight:700; color:#d4af37; font-size:18px;">✝ O PREGADOR</span>', unsafe_allow_html=True)
        
        if c_menu1.button("Dashboard"): navigate_to("Dashboard")
        if c_menu2.button("Sermões"): navigate_to("Studio")
        if c_menu3.button("Teologia"): navigate_to("Bible")
        if c_menu4.button("Mídia"): navigate_to("Media")
        
        with c_pf:
            # Avatar Lógico
            if st.session_state['user_avatar']:
                st.image(st.session_state['user_avatar'], width=35) # Simples mas funciona
            else:
                if st.button("👤", help="Perfil"): navigate_to("Settings")

def navigate_to(dest):
    st.session_state['page_stack'].append(dest)
    st.rerun()

def get_current_page():
    return st.session_state['page_stack'][-1]

# ==============================================================================
# MÓDULO 8: FLUXO DE LOGIN (CORRIGIDO C/ ANIMAÇÃO)
# ==============================================================================
if not st.session_state['logado']:
    carregar_estilo_visual() # Carrega CSS da animação
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 0.8, 1])
    
    with c2:
        # A Mágica do Círculo Pulsante Restaurada
        st.markdown("""
        <div class="login-circle-container">
            <span class="cross-symbol">✝</span>
        </div>
        <div style="text-align:center; animation: fadeIn 1s;">
            <h2 style="color:white; font-family:'Cinzel'; margin:0; letter-spacing:4px;">O PREGADOR</h2>
            <p style="color:#666; font-size:11px; margin-bottom:30px; letter-spacing:2px;">SECURITY ACCESS V14</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("gate_access"):
            u = st.text_input("ID", label_visibility="collapsed", placeholder="IDENTIDADE")
            p = st.text_input("KEY", type="password", label_visibility="collapsed", placeholder="SENHA")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("AUTENTICAR SISTEMA", type="primary", use_container_width=True):
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.session_state['tocar_som'] = True # Gatilho de som
                    SecurityLog.log_access(u) # Log seguro
                    st.rerun()
                else:
                    st.error("Credencial Rejeitada.")
    st.stop()

# Toca o som (apenas no primeiro reload pós-login)
if st.session_state.get('tocar_som'):
    tocar_pad_angelical()
    st.session_state['tocar_som'] = False

# ==============================================================================
# MÓDULO 9: APP EM EXECUÇÃO
# ==============================================================================
carregar_estilo_visual()
render_header_navbar()
page = get_current_page()

# >>> 🏠 DASHBOARD
if page == "Dashboard":
    
    st.markdown(f"## Shalom, {st.session_state['user_name']}.")
    
    # Widget de Estado Vital (Em cima)
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    col_feel, col_adv = st.columns([1.5, 2.5])
    
    with col_feel:
        st.caption("ESTADO ESPIRITUAL")
        opcoes = ["Fogo 🔥", "Paz 🕊️", "Cansaço 🌙", "Luta ⚔️", "Vazio 🏜️"]
        novo_h = st.selectbox("Status Atual", opcoes, index=0, label_visibility="collapsed")
        if novo_h != st.session_state['humor']: st.session_state['humor'] = novo_h
        
    with col_adv:
        if st.session_state['api_key']:
            if st.button("Receber palavra profética (Mentoria)", use_container_width=True):
                with st.spinner("Discernindo..."):
                    resp = cerebro_ia("", st.session_state['api_key'], "emocional")
                    st.success(resp)
        else:
            st.info("Conecte a IA nas Configurações para receber mentoria.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Atalhos e Agenda
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.subheader("Meus Sermões")
        serms = [f for f in os.listdir(PASTA_SERMOES) if f.endswith('.txt')]
        if serms:
            # Ordena por data mod
            serms.sort(key=lambda x: os.path.getmtime(os.path.join(PASTA_SERMOES, x)), reverse=True)
            for s in serms[:3]:
                # Listagem elegante
                cl1, cl2 = st.columns([0.1, 0.9])
                cl1.write("📄")
                if cl2.button(f"{s.replace('.txt','').upper()}", key=s):
                    # Load Logic
                    with open(os.path.join(PASTA_SERMOES, s), 'r', encoding='utf-8') as f:
                        st.session_state['texto_ativo'] = f.read()
                    st.session_state['titulo_ativo'] = s.replace('.txt','')
                    navigate_to("Studio")
        else:
            st.info("Nenhum manuscrito encontrado.")
            
    with c_right:
        st.subheader("Próximos Cultos")
        # Engine Litúrgica Calculando Datas
        prox_dom = LiturgicalEngine.get_proximo_domingo()
        st.markdown(f"""
        <div style="background:#222; padding:15px; border-radius:8px; border-left:3px solid #d4af37">
            <h3 style="margin:0; color:white">{prox_dom.day}</h3>
            <span style="font-size:12px; color:#888">{prox_dom.strftime('%B').upper()} - DOMINGO</span><br>
            Culto da Família
        </div>
        """, unsafe_allow_html=True)
        if st.button("➕ Novo Manuscrito", use_container_width=True, type="primary"):
            st.session_state['texto_ativo'] = ""
            st.session_state['titulo_ativo'] = ""
            navigate_to("Studio")


# >>> ✍️ STUDIO (SERMONS)
elif page == "Sermons":
    
    # 1. Configurações de Topo
    c_tit, c_btns = st.columns([3, 1])
    with c_tit:
        st.session_state['titulo_ativo'] = st.text_input("Tema", value=st.session_state['titulo_ativo'], placeholder="Título...", label_visibility="collapsed")
    with c_btns:
        if st.button("SALVAR", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"), 'w', encoding='utf-8') as f:
                    f.write(st.session_state['texto_ativo'])
                st.toast("Armazenado com sucesso.", icon="✅")

    # 2. Workspace
    c_ed, c_tools = st.columns([2.5, 1])
    
    with c_ed:
        # Ferramentas Rápidas (Toolbar WYSIWYG Mockup)
        t1, t2, t3, t4, t5 = st.columns(5)
        def inj(tx): st.session_state['texto_ativo'] += tx
        
        t1.button("H1", on_click=inj, args=("\n# ",), use_container_width=True)
        t2.button("**B**", on_click=inj, args=(" **negr** ",), use_container_width=True)
        t3.button("“Quotes”", on_click=inj, args=("\n> ",), use_container_width=True)
        t4.button("• Lista", on_click=inj, args=("\n- ",), use_container_width=True)
        # Mockup Speech-to-text
        t5.button("🎙️ Ditado", help="Speech-to-text placeholder", disabled=True, use_container_width=True)

        txt_main = st.text_area("editor", value=st.session_state['texto_ativo'], height=650, label_visibility="collapsed")
        st.session_state['texto_ativo'] = txt_main
        
        # Stats Rodapé Editor
        c_an, c_tim = st.columns(2)
        counts = BibleAnalytics.contar_palavras_frequentes(txt_main)
        tempo = BibleAnalytics.tempo_leitura_estimado(txt_main)
        c_an.caption(f"Palavras Frequentes: {', '.join([x[0] for x in counts])}")
        c_tim.caption(f"Tempo estimado de fala: {tempo} minutos")

    with c_tools:
        st.markdown("#### Slide Timeline")
        input_s = st.text_area("Criar Slide", height=100, placeholder="Cole aqui...")
        if st.button("Gerar Slide", use_container_width=True):
            if input_s: st.session_state['slides'].append({"conteudo": input_s})
        
        st.divider()
        if st.session_state['slides']:
            for i, slide in enumerate(st.session_state['slides']):
                st.markdown(f"""
                <div style="background:#0a0a0a; border-left:2px solid gold; padding:10px; font-size:12px; margin-bottom:5px;">
                    {i+1}. {slide['conteudo'][:40]}...
                </div>""", unsafe_allow_html=True)
        else:
            st.caption("Timeline vazia.")


# >>> 📚 BIBLE (TEOLOGIA)
elif page == "Theology":
    st.markdown("## Centro de Exegese")
    
    sr = st.text_input("Pesquisa Avançada (Texto ou Tema):", placeholder="Ex: Romanos 8:1")
    if sr and st.button("Pesquisar na Biblioteca Universal"):
        resp = cerebro_ia(sr, st.session_state['api_key'], "teologo")
        st.markdown(f'<div class="glass-panel">{resp}</div>', unsafe_allow_html=True)


# >>> 🎨 MEDIA LAB (SOCIAL)
elif page == "Media":
    st.markdown("## Media Lab")
    
    tabs = st.tabs(["Design Studio", "Social Planner (Novo)"])
    
    with tabs[0]: # Editor
        cl, cr = st.columns([2, 1])
        with cr:
            st.caption("Configurações")
            t_post = st.text_area("Texto", "Jesus salva.")
            bg_post = st.file_uploader("Fundo", type=['png','jpg'])
            if st.button("Renderizar Imagem", type="primary", use_container_width=True):
                # Usando nossa nova Engine
                img_data = render_post_social(t_post, bg_post)
                st.session_state['media_render'] = img_data
                st.success("Renderizado!")
        
        with cl:
            if 'media_render' in st.session_state and st.session_state['media_render']:
                st.image(st.session_state['media_render'], caption="Preview", width=400)
                st.download_button("Baixar PNG", st.session_state['media_render'], "post_pregador.png", "image/png")
            else:
                st.info("O Canvas de renderização aparecerá aqui.")

    with tabs[1]: # Planner Simples
        st.markdown("#### Agenda de Posts")
        dia = st.date_input("Data do Post")
        ideia = st.text_input("Ideia/Legenda")
        if st.button("Agendar (Simulação)"):
            st.toast(f"Agendado para {dia}")


# >>> ⚙️ CONFIG
elif page == "Settings":
    st.title("Settings")
    
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.subheader("Identidade Visual")
    name = st.text_input("Seu Nome / Título", value=st.session_state['user_name'])
    if name: st.session_state['user_name'] = name
    
    # Avatar Handler
    c1, c2 = st.columns(2)
    av_up = c1.file_uploader("Foto de Perfil", type=['png','jpg'])
    if av_up: st.session_state['user_avatar'] = Image.open(av_up)
    
    cam = c2.camera_input("Selfie Rápida")
    if cam: st.session_state['user_avatar'] = Image.open(cam)
    
    st.divider()
    
    st.subheader("Conexões (API)")
    k = st.text_input("Google AI Key", value=st.session_state['api_key'], type="password")
    if k: st.session_state['api_key'] = k
    
    st.divider()
    if st.button("Logout Seguro"):
        st.session_state['logado'] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
