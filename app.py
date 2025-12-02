import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import random
from datetime import datetime
from io import BytesIO

# --- 0. ENGINE KERNEL: INSTALAÇÃO E DEPENDÊNCIAS ---
def install_packages():
    required = ["google-generativeai", "duckduckgo-search", "streamlit-lottie", "fpdf", "Pillow"]
    for package in required:
        try:
            __import__(package.replace("-", "_").replace("google_generativeai", "google.generativeai").replace("Pillow", "PIL"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            st.rerun()

install_packages()

import google.generativeai as genai
from duckduckgo_search import DDGS
from streamlit_lottie import st_lottie
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

# --- 1. CONFIGURAÇÃO DE SISTEMA ---
st.set_page_config(page_title="O PREGADOR", layout="wide", page_icon="✝️", initial_sidebar_state="collapsed")

# SISTEMA DE ARQUIVOS
PASTA_RAIZ = "Dados_Pregador"
PASTA_SERMOES = os.path.join(PASTA_RAIZ, "Sermoes")
PASTA_CARE = os.path.join(PASTA_RAIZ, "PastoralCare")
DB_ORACOES = os.path.join(PASTA_CARE, "oracoes.json") # Nova Base de Dados

os.makedirs(PASTA_SERMOES, exist_ok=True)
os.makedirs(PASTA_CARE, exist_ok=True)

# GESTÃO DE ESTADO (SESSION STATE MANAGER)
DEFAULTS = {
    "logado": False, 
    "user": "", 
    "page_stack": ["Dashboard"], 
    "texto_ativo": "", 
    "titulo_ativo": "", 
    "slides": [], 
    "api_key": "", 
    "theme_size": 18, 
    "stats_sermoes": len(os.listdir(PASTA_SERMOES)),
    "historico_biblia": [], 
    "humor": "Neutro",
    "tocar_som": False,
    "user_avatar": None, 
    "user_name": "Pastor",
    "imagem_gerada_bytes": None # Buffer para Media Lab
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 2. SUBSISTEMAS AVANÇADOS (FUNÇÕES COMPLEXAS) ---

# [NOVO] GERADOR PDF
class SermonPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'O Pregador - Manuscrito Pastoral', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def exportar_pdf(titulo, texto):
    pdf = SermonPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    # Título
    pdf.set_font("Times", 'B', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, titulo.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)
    # Corpo
    pdf.set_font("Times", size=14) # Letra grande para púlpito
    clean_txt = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_txt)
    return pdf.output(dest='S').encode('latin-1')

# [NOVO] ENGINE GRÁFICA (ADOBE STYLE)
def renderizar_midia_social(texto, fundo_upload=None, cor_texto="white", estilo="Clean"):
    # Configuração Base
    W, H = 1080, 1350 # Formato Portrait (Instagram)
    
    # 1. Tratamento do Fundo
    if fundo_upload:
        base_img = Image.open(fundo_upload).convert("RGB")
        base_img = ImageOps.fit(base_img, (W, H), method=Image.Resampling.LANCZOS)
        # Filtro de Escurecimento para leitura
        enhancer = ImageEnhance.Brightness(base_img)
        base_img = enhancer.enhance(0.4) # 40% brilho
        # Blur artístico
        base_img = base_img.filter(ImageFilter.GaussianBlur(3))
    else:
        # Fundo Gradiente Procedural
        base_img = Image.new('RGB', (W, H), "#111")
        draw_grad = ImageDraw.Draw(base_img)
        for i in range(H):
            r, g, b = 20, 20, 30
            ratio = i / H
            nr = int(r * (1 - ratio))
            ng = int(g * (1 - ratio))
            nb = int(b + (100 * ratio))
            draw_grad.line([(0, i), (W, i)], fill=(nr, ng, nb))

    draw = ImageDraw.Draw(base_img)
    
    # 2. Tipografia Dinâmica
    try:
        # Tenta carregar fonte do sistema ou fallback
        if estilo == "Cinematica":
            font_size = 70
            font = ImageFont.truetype("arialbd.ttf", font_size) # Bold
        else:
            font_size = 60
            font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
        font_size = 40 # Ajuste fallback

    # 3. Quebra de Linha e Centralização (Word Wrap Manual)
    margin = 100
    max_width = W - (margin * 2)
    
    lines = []
    words = texto.split(' ')
    current_line = []
    
    # Lógica de wrap para pillow
    for word in words:
        current_line.append(word)
        # Verifica tamanho (simulado pelo length * const para velocidade ou bbox real)
        line_str = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        if (bbox[2] - bbox[0]) > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    # 4. Renderização do Texto
    total_height = len(lines) * (font_size + 20)
    start_y = (H - total_height) / 2
    
    for line in lines:
        # Sombra suave
        draw.text((margin + 3, start_y + 3), line, font=font, fill="#000000")
        # Texto principal
        draw.text((margin, start_y), line, font=font, fill=cor_texto)
        start_y += (font_size + 20)

    # 5. Assinatura / Marca D'agua
    try:
        small_font = ImageFont.truetype("arial.ttf", 30)
    except: small_font = ImageFont.load_default()
    
    draw.text((W/2 - 100, H - 150), "O PREGADOR", font=small_font, fill="#D4AF37") # Gold
    
    # 6. Exportação
    buf = BytesIO()
    base_img.save(buf, format="PNG", quality=95)
    return buf.getvalue()

# [NOVO] BANCO DE DADOS DE ORAÇÃO (JSON)
def gerenciar_oracoes(acao, dados=None, idx=None):
    # Carrega
    lista = []
    if os.path.exists(DB_ORACOES):
        with open(DB_ORACOES, 'r') as f: lista = json.load(f)
    
    if acao == "adicionar":
        dados['data'] = datetime.now().strftime("%d/%m %H:%M")
        lista.insert(0, dados) # Adiciona no topo
    elif acao == "remover":
        if idx < len(lista): lista.pop(idx)
        
    # Salva
    with open(DB_ORACOES, 'w') as f: json.dump(lista, f)
    return lista

# --- 3. HELPER GERAIS ---
def img_to_base64(img_bytes):
    encoded = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{encoded}"

def play_heaven_sound():
    sound_url = "https://cdn.pixabay.com/download/audio/2023/09/20/audio_5b98096575.mp3?filename=angelic-ambient-169586.mp3"
    st.markdown(f"""<audio autoplay style="display:none;"><source src="{sound_url}" type="audio/mp3"></audio>
    <script>var a=document.querySelector("audio");a.volume=0.3;setTimeout(function(){{a.pause();}},6500);</script>""", unsafe_allow_html=True)

def cerebro_pregador(prompt, key, context="teologico"):
    if not key: return "⚠️ Desconectado. Configure a API Key."
    try:
        genai.configure(api_key=key)
        sys = "Você é um assistente teológico de precisão acadêmica."
        if context == "emocional": sys = f"O pastor sente: {st.session_state['humor']}. Responda com consolo bíblico, sabedoria de Spurgeon e graça."
        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys}\nConsulta: {prompt}").text
    except Exception as e: return f"Falha na comunicação: {e}"

# --- 4. DESIGN SYSTEM (QUANTUM UI) ---
def carregar_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400&family=Cinzel:wght@400;700&display=swap');
    
    /* RESET GLOBAL */
    [data-testid="stSidebar"] {{ display: none; }}
    header, footer {{ display: none !important; }}
    .block-container {{ padding-top: 70px !important; padding-bottom: 20px !important; }}
    
    :root {{ --bg-deep: #080808; --panel: #111111; --gold: #D4AF37; --text: #EAEAEA; --border: #333; --blue-neon: #007AFF; }}
    
    .stApp {{ 
        background-color: var(--bg-deep); 
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }}

    /* BARRA HORIZONTAL (NAV) */
    .top-nav-container {{
        background: rgba(12, 12, 12, 0.95); backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border); padding: 0 30px; height: 60px;
        position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
        display: flex; align-items: center; gap: 20px;
    }}
    
    /* BOTÕES TAB NAVEGAÇÃO */
    div.stButton > button {{
        background: transparent; border: 1px solid transparent; color: #888; 
        font-size: 13px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;
        transition: 0.3s; margin: 0 2px;
    }}
    div.stButton > button:hover {{ color: white; background: #222; border-radius: 4px; border: 1px solid #333; }}
    div.stButton > button:focus {{ color: var(--gold); border-bottom: 2px solid var(--gold); }}

    /* LOGO CINZEL */
    .logo-txt {{ font-family: 'Cinzel', serif; font-weight:700; color: var(--gold); font-size:18px; }}

    /* CONTAINERS FLUTUANTES (CARDS) */
    .float-card {{
        background: #111; border: 1px solid #222; border-radius: 12px; padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: 0.3s;
    }}
    .float-card:hover {{ border-color: #444; }}

    /* INPUTS MINIMALISTAS */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        background: #090909 !important; border: 1px solid #2a2a2a !important; 
        color: #ddd !important; border-radius: 6px;
    }}
    .stTextArea textarea:focus {{ border-color: var(--gold) !important; }}

    /* EDITOR DE PÚLPITO */
    .pulpit-editor textarea {{
        font-family: 'Georgia', serif; font-size: 20px !important; line-height: 1.8; padding: 40px;
    }}

    /* BOTÃO PRINCIPAL (CTA) */
    .primary-btn button {{
        background: linear-gradient(135deg, #D4AF37 0%, #AA8A2E 100%) !important;
        color: black !important; font-weight: bold !important; border: none !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }}
    
    /* AVATAR BALL */
    .user-avatar {{
        width: 35px; height: 35px; border-radius: 50%; border: 1px solid var(--border);
        background-size: cover; background-position: center; display: inline-block;
        vertical-align: middle;
    }}
    </style>
    """, unsafe_allow_html=True)

carregar_css()

# --- 5. LOGICA DE NAVEGAÇÃO ---
def navbar():
    with st.container():
        # Cria a barra usando colunas para posicionamento
        c1, c2, c3, c4, c5, c6, c7, c_pf = st.columns([1.5, 1, 1, 1, 1, 1, 3, 0.6])
        
        with c1:
            st.markdown(f'<span class="logo-txt">✝ PREGADOR <small style="font-size:9px; opacity:0.5">XIII</small></span>', unsafe_allow_html=True)
        
        # Tabs de Navegação
        if c2.button("Início"): nav_to("Dashboard")
        if c3.button("Sermão"): nav_to("Sermons")
        if c4.button("Criativo"): nav_to("Media")
        if c5.button("Bíblia"): nav_to("Theology")
        if c6.button("Projetor"): nav_to("Projector")
        
        # Área Perfil (Settings)
        with c_pf:
            # Avatar Hack: Usamos st.image pequeno se houver, ou botao
            if st.session_state['user_avatar']:
                st.image(st.session_state['user_avatar'], width=35)
                # Hack visual, abaixo tem botão invisivel na pratica cobrindo ou do lado
            
            if st.button("⚙️"): nav_to("Settings")

def nav_to(page):
    st.session_state['page_stack'].append(page)
    st.rerun()

def get_page(): return st.session_state['page_stack'][-1]

# --- 6. GATEKEEPER (LOGIN ATMOSFÉRICO) ---
if not st.session_state['logado']:
    # Visual Fullscreen Centralizado
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    cl, cm, cr = st.columns([1, 0.7, 1])
    with cm:
        st.markdown("""
        <div style="text-align:center; animation: fadeIn 2s;">
            <div style="font-size:60px; color:#d4af37; text-shadow:0 0 30px rgba(212,175,55,0.4);">✝</div>
            <h2 style="font-family:'Cinzel'; letter-spacing:6px; margin:0; color:white;">O PREGADOR</h2>
            <div style="height:1px; width:50px; background:#444; margin:15px auto;"></div>
            <p style="font-size:11px; color:#666; letter-spacing:2px;">SECURITY GATE V13</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("gate"):
            u = st.text_input("Credencial", label_visibility="collapsed", placeholder="IDENTIDADE")
            p = st.text_input("Chave", type="password", label_visibility="collapsed", placeholder="SENHA")
            
            # Espaçador
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Botão
            sub = st.form_submit_button("CONECTAR SISTEMA", type="primary", use_container_width=True)
            
            if sub:
                if (u == "admin" and p == "1234") or (u == "pr" and p == "123"):
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.session_state['tocar_som'] = True
                    st.rerun()
                else:
                    st.error("Acesso Negado. Identidade desconhecida.")
    st.stop()

# Toca som apenas 1 vez ao entrar
if st.session_state['tocar_som']:
    play_heaven_sound()
    st.session_state['tocar_som'] = False

# --- 7. NÚCLEO DO SISTEMA (PÁGINAS) ---
navbar()
st.markdown("<br>", unsafe_allow_html=True)
pagina = get_page()

# ================================
# 🏠 DASHBOARD: CUIDADO INTEGRAL
# ================================
if pagina == "Dashboard":
    
    st.markdown(f"### Olá, {st.session_state['user_name']}.")
    
    # 1. MOOD & MENTORIA
    st.markdown('<div class="float-card">', unsafe_allow_html=True)
    c_feel, c_mentoria = st.columns([1.5, 2])
    
    with c_feel:
        st.caption("TERMÔMETRO ESPIRITUAL")
        humor_list = ["Em Paz 🕊️", "Grato 🙏", "Cansado 🕸️", "Batalha ⚔️", "Deserto 🏜️"]
        h_sel = st.radio("Como está seu espírito?", humor_list, horizontal=True, label_visibility="collapsed")
        
        if h_sel != st.session_state['humor']:
            st.session_state['humor'] = h_sel # Salva
            
    with c_mentoria:
        st.caption("MENTORIA DIGITAL")
        if st.button("Receber palavra de alinhamento", use_container_width=True):
            if st.session_state['api_key']:
                with st.spinner("Conectando..."):
                    resp = cerebro_pregador("", st.session_state['api_key'], "emocional")
                    st.success(resp)
            else: st.warning("Conecte a IA nas Configurações.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. PAINEL DE ORAÇÃO & ARQUIVOS
    col_a, col_b = st.columns([1, 1.2])
    
    with col_a:
        st.markdown("#### 📁 Recentes")
        sermoes = [f.replace('.txt','') for f in os.listdir(PASTA_SERMOES) if f.endswith(".txt")]
        if sermoes:
            for s in sermoes[:3]: # Top 3
                if st.button(f"📄 {s}", key=f"d_{s}"):
                    st.session_state['titulo_ativo'] = s
                    # Carregar texto
                    with open(os.path.join(PASTA_SERMOES, f"{s}.txt"),'r') as f: st.session_state['texto_ativo'] = f.read()
                    nav_to("Sermons")
        else: st.info("Biblioteca vazia.")
        
        if st.button("➕ Novo Projeto", type="primary"):
            st.session_state['texto_ativo'] = ""
            st.session_state['titulo_ativo'] = ""
            nav_to("Sermons")

    with col_b:
        st.markdown("#### 🙏 Mural de Oração (Novo)")
        # Adicionar Pedido
        novo_pedido = st.text_input("Adicionar motivo:", placeholder="Ex: Cura da irmã Maria", label_visibility="collapsed")
        if st.button("Registrar Oração"):
            if novo_pedido: gerenciar_oracoes("adicionar", {"motivo": novo_pedido})
        
        # Listar Orações
        oracoes = gerenciar_oracoes("listar")
        if oracoes:
            for idx, item in enumerate(oracoes[:4]): # Mostra 4 ultimas
                c_txt, c_del = st.columns([4, 1])
                c_txt.caption(f"{item['data']} - {item['motivo']}")
                if c_del.button("❌", key=f"o_{idx}"):
                    gerenciar_oracoes("remover", idx=idx)
                    st.rerun()
        else:
            st.caption("Nenhum pedido ativo.")


# ================================
# ✍️ SERMONS: STUDIO ZEN
# ================================
elif pagina == "Sermons":
    
    # Barra de Ferramentas Fixa (Header do Editor)
    tb1, tb2 = st.columns([3, 1])
    with tb1:
        st.session_state['titulo_ativo'] = st.text_input("Titulo", value=st.session_state['titulo_ativo'], placeholder="Título da Mensagem...", label_visibility="collapsed")
    with tb2:
        c_sv, c_pdf = st.columns(2)
        if c_sv.button("SALVAR"):
            if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_SERMOES, f"{st.session_state['titulo_ativo']}.txt"),'w') as f: f.write(st.session_state['texto_ativo'])
                st.toast("Manuscrito salvo!", icon="💾")
        
        if c_pdf.button("PDF"):
            if st.session_state['texto_ativo']:
                pdf_bytes = exportar_pdf(st.session_state['titulo_ativo'], st.session_state['texto_ativo'])
                st.download_button("Baixar", pdf_bytes, f"{st.session_state['titulo_ativo']}.pdf", "application/pdf")

    # Layout de Edição (Timeline à Direita)
    c_txt, c_sl = st.columns([2.5, 1])
    
    with c_txt:
        # Área de Texto Estilo "Púlpito"
        st.markdown('<div class="pulpit-editor">', unsafe_allow_html=True)
        t_val = st.text_area("body", value=st.session_state['texto_ativo'], height=700, label_visibility="collapsed")
        st.session_state['texto_ativo'] = t_val
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ferramenta IA: Analisar Tom (NOVIDADE)
        if st.button("🔍 Analisar Tom do Sermão (IA)"):
            if st.session_state['api_key'] and t_val:
                resp = cerebro_pregador(f"Analise o tom deste sermão. É muito duro? Muito teológico? Sugira melhorias emocionais.\nTexto: {t_val[:2000]}...", st.session_state['api_key'])
                st.info(resp)

    with c_sl:
        st.markdown("**Timeline (Slides)**")
        st.info("💡 Arraste conteúdo:")
        
        add_s = st.text_area("Conteúdo do Slide", height=100)
        if st.button("Gerar Bloco Visual"):
            if add_s: st.session_state['slides'].append({"conteudo": add_s})
        
        st.divider()
        if st.session_state['slides']:
            for i, s in enumerate(st.session_state['slides']):
                st.markdown(f"<div style='border-left:3px solid var(--gold); padding:10px; background:#111; margin-bottom:5px; font-size:12px;'>#{i+1} {s['conteudo'][:40]}...</div>", unsafe_allow_html=True)
        else: st.caption("Vazio.")


# ================================
# 🎨 MEDIA LAB (REAL RENDER)
# ================================
elif pagina == "Media":
    st.markdown("### 🎨 Media Lab (Instagram/Social)")
    
    c_canvas, c_controls = st.columns([1.5, 1])
    
    with c_controls:
        st.markdown('<div class="float-card">', unsafe_allow_html=True)
        st.caption("CONFIGURADOR")
        
        txt_post = st.text_area("Texto do Post", "Tudo é possível ao que crê.\nMarcos 9:23")
        estilo = st.selectbox("Estilo", ["Clean", "Cinematica"])
        cor = st.color_picker("Cor Texto", "#ffffff")
        fundo = st.file_uploader("Fundo (Img)", type=['jpg','png'])
        
        if st.button("RENDERIZAR (GPU SIMULADA)", type="primary"):
            # Chama a função real de Pillow criada lá em cima
            with st.spinner("Processando pixels..."):
                img_data = renderizar_midia_social(txt_post, fundo, cor, estilo)
                st.session_state['imagem_gerada_bytes'] = img_data
                st.success("Render Completo.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_canvas:
        if st.session_state['imagem_gerada_bytes']:
            st.image(st.session_state['imagem_gerada_bytes'], caption="Preview HD", width=400)
            st.download_button("⬇️ Baixar PNG Final", st.session_state['imagem_gerada_bytes'], "pregador_media.png", "image/png")
        else:
            st.markdown("""
            <div style="width:400px; height:500px; border:2px dashed #333; display:flex; align-items:center; justify-content:center; color:#555; background:#080808">
                CANVAS DE PREVIEW
            </div>
            """, unsafe_allow_html=True)


# ================================
# 📚 THEOLOGY (BIBLE + EXEGESE)
# ================================
elif pagina == "Theology":
    st.markdown("### Centro de Pesquisa")
    
    search = st.text_input("Consulta Bíblica / Teológica", placeholder="Ex: A graça em Romanos ou Grego de João 3:16")
    
    if st.button("Pesquisar na Biblioteca Universal"):
        resp = cerebro_pregador(search, st.session_state['api_key'])
        st.markdown(f'<div class="float-card">{resp}</div>', unsafe_allow_html=True)


# ================================
# 📽️ PROJECTOR (FULLSCREEN)
# ================================
elif pagina == "Projector":
    if not st.session_state['slides']:
        st.warning("Sem slides na linha do tempo.")
    else:
        if 'slide_idx' not in st.session_state: st.session_state['slide_idx'] = 0
        
        # Controles
        idx = st.session_state['slide_idx']
        slides = st.session_state['slides']
        
        c_back, c_status, c_fwd = st.columns([1, 4, 1])
        if c_back.button("◀ ANTERIOR"): 
            st.session_state['slide_idx'] = max(0, idx - 1)
            st.rerun()
        
        with c_status:
            st.progress((idx + 1) / len(slides))
            st.caption(f"Slide {idx + 1} de {len(slides)}")
            
        if c_fwd.button("PRÓXIMO ▶"):
            st.session_state['slide_idx'] = min(len(slides) - 1, idx + 1)
            st.rerun()
            
        # O Slide em Si (Simulação Telão)
        conteudo = slides[st.session_state['slide_idx']]['conteudo'].replace('\n', '<br>')
        st.markdown(f"""
        <div style="
            position: fixed; top: 180px; left: 5%; width: 90%; height: 60vh;
            background: black; color: white; display: flex; align-items: center; justify-content: center;
            font-family: Arial; font-size: 50px; font-weight: bold; text-align: center;
            border: 10px solid #111; border-radius: 20px; box-shadow: 0 0 50px rgba(0,0,0,0.8);
            z-index: 100;">
            {conteudo}
        </div>
        """, unsafe_allow_html=True)


# ================================
# ⚙️ SETTINGS
# ================================
elif pagina == "Settings":
    st.title("Configurações do Sistema")
    
    st.markdown('<div class="float-card">', unsafe_allow_html=True)
    st.subheader("Identidade")
    n = st.text_input("Seu Nome", value=st.session_state['user_name'])
    if n: st.session_state['user_name'] = n
    
    c_up, c_cm = st.columns(2)
    # Upload Foto
    up_ph = c_up.file_uploader("Upload Foto Perfil", type=['jpg','png'])
    if up_ph: st.session_state['user_avatar'] = Image.open(up_ph)
    
    # Cam
    cam_ph = c_cm.camera_input("Tirar Foto Agora")
    if cam_ph: st.session_state['user_avatar'] = Image.open(cam_ph)
    
    st.divider()
    st.subheader("Chave Mestra (IA)")
    api = st.text_input("Google API Key", value=st.session_state['api_key'], type="password")
    if api: st.session_state['api_key'] = api
    
    st.divider()
    if st.button("SAIR DO SISTEMA"):
        st.session_state['logado'] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
