import streamlit as st
import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime
from io import BytesIO

# --- 0. AUTO-INSTALAÇÃO DE DEPENDÊNCIAS (BLINDADA) ---
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- 1. CONFIGURAÇÃO DO SISTEMA ---
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# --- 2. GERENCIAMENTO DE ESTADO E PREFERÊNCIAS ---
PASTA_USER = "Banco_Sermoes"
os.makedirs(PASTA_USER, exist_ok=True)

# Cores e Temas Personalizáveis
TEMAS = {
    "Genesis Dark": {"bg": "#000000", "fg": "#e0e0e0", "acc": "#d4af37", "menu": "#1a1a1a"},
    "Apocalipse Red": {"bg": "#1a0505", "fg": "#ffcccc", "acc": "#ff4444", "menu": "#2e0b0b"},
    "Salmos Light": {"bg": "#f8f9fa", "fg": "#333333", "acc": "#2980b9", "menu": "#e9ecef"},
    "Cyber Gospel": {"bg": "#0b0c15", "fg": "#a0e9ff", "acc": "#00d2ff", "menu": "#151621"}
}

def load_user_prefs():
    if 'prefs' not in st.session_state:
        st.session_state['prefs'] = {"tema": "Genesis Dark", "user": "Pastor", "igreja": "Igreja Local", "biblia": "NVI", "avatar_url": ""}
    return st.session_state['prefs']

prefs = load_user_prefs()
cores = TEMAS[prefs['tema']]

# --- 3. ESTILIZAÇÃO AVANÇADA (UI DE DESKTOP) ---
st.markdown(f"""
    <style>
    /* Reset Geral */
    .stApp {{ background-color: {cores['bg']}; color: {cores['fg']}; }}
    
    /* MENU BAR ESTILO WINDOWS/LOGOS */
    .menubar {{
        display: flex; gap: 15px; padding: 10px 20px;
        background: {cores['menu']}; border-bottom: 2px solid {cores['acc']};
        font-family: 'Segoe UI', sans-serif; font-size: 14px;
        position: sticky; top: 0; z-index: 999;
    }}
    .menu-item {{ cursor: pointer; color: {cores['fg']}; font-weight: 500; padding: 5px 10px; border-radius: 4px; }}
    .menu-item:hover {{ background: {cores['acc']}; color: {cores['bg']}; }}

    /* JANELAS FLUTUANTES (EFEITO) */
    .workspace {{
        background: {cores['menu']}; border: 1px solid #333;
        border-radius: 8px; padding: 20px; margin-top: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    
    /* TEXT AREAS CUSTOMIZADOS */
    textarea {{
        background: {cores['bg']} !important; color: {cores['fg']} !important;
        border: 1px solid #444 !important; font-family: 'Merriweather', serif;
    }}
    
    /* BOTÕES */
    button {{ border: 1px solid {cores['acc']} !important; }}
    
    /* SEPARAÇÃO DE TELAS */
    .split-screen {{ display: flex; gap: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE IA & LÓGICA ---
def assistente_ia(prompt, key, personality="Teólogo"):
    if not key: return "⚠️ IA Offline: Insira a chave API nas Configurações."
    try:
        genai.configure(api_key=key)
        sys_msg = f"Você é o assistente do sistema 'O Pregador'. Personalidade: {personality}."
        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{sys_msg}\n{prompt}").text
    except Exception as e: return f"Erro na Matriz: {e}"

def gerar_imagem_social(texto, imagem_fundo=None, cor_texto="white"):
    # Cria uma base preta ou usa imagem enviada
    W, H = 1080, 1080
    if imagem_fundo:
        try:
            img = Image.open(imagem_fundo).resize((W, H))
            img = img.filter(ImageFilter.GaussianBlur(3)) # Desfoque leve para ler texto
        except:
            img = Image.new('RGB', (W, H), color=(20, 20, 20))
    else:
        img = Image.new('RGB', (W, H), color=(20, 20, 20))
    
    draw = ImageDraw.Draw(img)
    # Tenta usar fonte padrão ou fallback
    try: font = ImageFont.truetype("arial.ttf", 60)
    except: font = ImageFont.load_default()
    
    # Centraliza texto (Lógica simplificada)
    lines = texto.split('\n')
    y_text = H // 2 - (len(lines)*35)
    for line in lines:
        # Posição aproximada central (Pillow nativo requer cálculos complexos de bbox, simplificando)
        draw.text((100, y_text), line, font=font, fill=cor_texto)
        y_text += 70
        
    # Adiciona Logo
    draw.text((W-300, H-80), "O PREGADOR APP", fill=cores['acc'])
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- 5. COMPONENTES DO SISTEMA ---

# BARRA DE MENU SUPERIOR (HEADER)
def render_menu_bar():
    c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,5])
    with c1: st.markdown(f"<div class='menu-item'>📂 Arquivo</div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='menu-item'>🛠️ Editar</div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='menu-item'>👁️ Exibir</div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='menu-item'>⚙️ Config</div>", unsafe_allow_html=True)
    with c5: st.markdown(f"<div class='menu-item'>🆘 Ajuda</div>", unsafe_allow_html=True)
    with c6: st.caption(f"Logado como: {prefs['user']} | {datetime.now().strftime('%H:%M')}")

# ESTADOS GLOBAIS
if 'slides' not in st.session_state: st.session_state['slides'] = []
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""
if 'api_key' not in st.session_state: st.session_state['api_key'] = ""
if 'aba_atual' not in st.session_state: st.session_state['aba_atual'] = "Studio"

# --- SIDEBAR (ASSISTENTE E PERFIL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2965/2965300.png", width=50) # Logo genérico cruz
    st.markdown("## O PREGADOR")
    st.markdown("*Sistema Homilético v4.0*")
    
    st.markdown("---")
    menu_sel = st.radio("MÓDULOS", ["🏠 Central", "✍️ Studio (Split View)", "🎨 Social Studio", "🖥️ Apresentação", "🆘 Suporte"], 
                       index=["Central", "Studio", "Social", "Apres", "Suporte"].index(st.session_state['aba_atual'].split(" ")[0]) if st.session_state['aba_atual'].split(" ")[0] in ["Central", "Studio", "Social", "Apres", "Suporte"] else 0)
    
    # Assistente de Bolso (Sempre visível)
    st.divider()
    with st.expander("🤖 O Pregador Chat", expanded=True):
        st.session_state['api_key'] = st.text_input("Chave Google", type="password", value=st.session_state['api_key'])
        msg = st.text_input("Fale comigo, pastor:", placeholder="Ex: Ideia para introdução...")
        if msg and st.session_state['api_key']:
            st.info(assistente_ia(msg, st.session_state['api_key']))
    
    # Customização Rápida
    st.divider()
    tema_opt = st.selectbox("Tema Visual", list(TEMAS.keys()), index=list(TEMAS.keys()).index(prefs['tema']))
    if tema_opt != prefs['tema']:
        prefs['tema'] = tema_opt
        st.rerun()

# --- PÁGINA 1: CENTRAL (DASHBOARD) ---
if menu_sel == "🏠 Central":
    render_menu_bar()
    st.title(f"Bem-vindo, {prefs['user']}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 🕯️ Palavra Viva de Hoje")
        # IA gera devocional com base no humor (Mood Tracker)
        humor = st.selectbox("Como você se sente hoje?", ["Abençoado 🙏", "Cansado 😓", "Ansioso 🌪️", "Motivado 🔥"])
        if st.button("Receber Direção Espiritual") and st.session_state['api_key']:
            prompt = f"O pastor está se sentindo {humor}. Dê um conselho puritano breve e um versículo ({prefs['biblia']})."
            st.success(assistente_ia(prompt, st.session_state['api_key'], "Puritano"))
    
    with col2:
        st.markdown(f"""
        <div class="workspace" style="text-align:center">
            <h4>Seu Púlpito</h4>
            <h1>{len(os.listdir(PASTA_USER))}</h1>
            <p>Sermões Arquivados</p>
        </div>
        """, unsafe_allow_html=True)

# --- PÁGINA 2: STUDIO (SPLIT SCREEN - CORE) ---
elif menu_sel == "✍️ Studio (Split View)":
    render_menu_bar()
    
    # Ferramentas de Topo (Word Style)
    t_col1, t_col2, t_col3 = st.columns([2, 3, 2])
    with t_col1:
        arquivo_sel = st.selectbox("Arquivo", ["+ Novo"] + os.listdir(PASTA_USER))
    with t_col2:
        titulo = st.text_input("Título da Mensagem", value=st.session_state['titulo_ativo'], label_visibility="collapsed", placeholder="Título do Sermão...")
    with t_col3:
        if st.button("💾 Salvar Tudo", type="primary", use_container_width=True):
            if titulo:
                # Salva texto
                with open(os.path.join(PASTA_USER, f"{titulo}.txt"), 'w', encoding='utf-8') as f:
                    f.write(st.session_state['texto_ativo'])
                # Salva slides (JSON)
                with open(os.path.join(PASTA_USER, f"{titulo}_slides.json"), 'w', encoding='utf-8') as f:
                    json.dump(st.session_state['slides'], f)
                st.toast("Texto e Slides salvos no servidor!", icon="💾")

    # ÁREA DIVIDIDA: ESQUERDA (TEXTO) | DIREITA (SLIDES)
    col_text, col_slide = st.columns([1.2, 1])
    
    # --- COLUNA ESQUERDA: EDITOR WORD ---
    with col_text:
        st.markdown("#### 📜 Manuscrito")
        
        # Barra de ferramentas texto
        b1, b2, b3 = st.columns(3)
        def add_text(t): st.session_state['texto_ativo'] += t
        b1.button("Negrito", on_click=add_text, args=(" **text** ",))
        b2.button("Versículo", help="Insira referência") 
        b3.button("Intro/Fim", on_click=add_text, args=("\n# INTRODUÇÃO\n\n",))
        
        texto_input = st.text_area("Escreva aqui...", value=st.session_state['texto_ativo'], height=600, key="editor_main")
        # Sync manual para garantir estado
        st.session_state['texto_ativo'] = texto_input
        
        # Botão mágico de transferência
        st.markdown("---")
        add_selecao = st.text_area("Copie um trecho acima e cole aqui para transformar em slide:", height=100)
        if st.button("➡️ Criar Slide Deste Trecho"):
            if add_selecao:
                st.session_state['slides'].append({"conteudo": add_selecao, "imagem": None})
                st.toast("Slide criado!", icon="🎞️")

    # --- COLUNA DIREITA: PROJETOR SLIDE BUILDER ---
    with col_slide:
        st.markdown("#### 🎞️ Deck de Apresentação (Slides)")
        
        if not st.session_state['slides']:
            st.info("Nenhum slide ainda. Escreva à esquerda e envie para cá.")
        
        # Iterador de Slides
        for i, slide in enumerate(st.session_state['slides']):
            with st.expander(f"Slide {i+1}", expanded=False):
                nov_conteudo = st.text_area(f"Texto Slide {i+1}", slide['conteudo'])
                st.session_state['slides'][i]['conteudo'] = nov_conteudo
                
                # Upload imagem de fundo individual
                bg = st.file_uploader(f"Fundo Slide {i+1}", type=["png","jpg"], key=f"file_{i}")
                if bg: st.session_state['slides'][i]['imagem'] = bg # Nota: Em prod, salvaria o path
                
                if st.button(f"🗑️ Excluir Slide {i+1}"):
                    st.session_state['slides'].pop(i)
                    st.rerun()

        # Adicionar Manualmente
        if st.button("➕ Slide em Branco"):
            st.session_state['slides'].append({"conteudo": "Novo Texto", "imagem": None})
            st.rerun()
            
        # Preview Rápido
        if st.session_state['slides']:
            last = st.session_state['slides'][-1]
            st.markdown(f"""
            <div style="background: black; color: white; padding: 20px; text-align: center; border: 4px solid {cores['acc']}; border-radius: 10px;">
                <small>PREVIEW ÚLTIMO SLIDE</small><br><br>
                <h3>{last['conteudo']}</h3>
            </div>
            """, unsafe_allow_html=True)


# --- PÁGINA 3: SOCIAL STUDIO (NOVIDADE) ---
elif menu_sel == "🎨 Social Studio":
    st.title("Estúdio Criativo")
    st.markdown("Crie cards para Instagram/WhatsApp baseados em versículos.")
    
    col_img, col_prev = st.columns([1, 1.5])
    
    with col_img:
        txt_card = st.text_area("Texto da Imagem", "O Senhor é o meu pastor;\nnada me faltará.\nSalmos 23:1")
        bg_card = st.file_uploader("Imagem de Fundo (Opcional)", type=['jpg', 'png'])
        cor_txt = st.color_picker("Cor do Texto", "#FFFFFF")
        
        if st.button("✨ Gerar Arte"):
            img_bytes = gerar_imagem_social(txt_card, bg_card, cor_txt)
            st.session_state['last_img'] = img_bytes
    
    with col_prev:
        if 'last_img' in st.session_state:
            st.image(st.session_state['last_img'], caption="Pré-visualização", use_column_width=True)
            st.download_button("⬇️ Baixar Imagem PNG", st.session_state['last_img'], file_name="versiculo_social.png", mime="image/png")

# --- PÁGINA 4: APRESENTAÇÃO (SEGUNDA TELA) ---
elif menu_sel == "🖥️ Apresentação":
    st.markdown("## Modo Projeção")
    
    if not st.session_state['slides']:
        st.warning("Crie slides no Studio primeiro.")
    else:
        # Se usuário tiver 2 telas, ele abre o navegador nesta aba e joga pra lá
        col_list, col_screen = st.columns([1, 4])
        
        # Controle (Operador)
        with col_list:
            st.caption("Navegação")
            if 'slide_idx' not in st.session_state: st.session_state['slide_idx'] = 0
            
            for j, s in enumerate(st.session_state['slides']):
                if st.button(f"Slide {j+1}: {s['conteudo'][:10]}...", use_container_width=True):
                    st.session_state['slide_idx'] = j
        
        # Tela (Projeção)
        with col_screen:
            curr = st.session_state['slides'][st.session_state['slide_idx']]
            
            # CSS Para simular Fullscreen na div
            st.markdown(f"""
            <div style="
                width: 100%; height: 70vh; 
                background-color: black; 
                color: white; 
                display: flex; justify-content: center; align-items: center; 
                text-align: center;
                font-family: Arial, sans-serif;
                font-size: 50px;
                font-weight: bold;
                border: 2px solid white;
                text-shadow: 2px 2px 4px #000000;">
                {curr['conteudo'].replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            c_back, c_fwd = st.columns(2)
            if c_back.button("⬅️ Anterior"): 
                st.session_state['slide_idx'] = max(0, st.session_state['slide_idx'] - 1)
                st.rerun()
            if c_fwd.button("Próximo ➡️"):
                st.session_state['slide_idx'] = min(len(st.session_state['slides']) - 1, st.session_state['slide_idx'] + 1)
                st.rerun()

# --- PÁGINA 5: SUPORTE ---
elif menu_sel == "🆘 Suporte":
    st.title("Central de Ajuda")
    
    st.info("Para destacar janelas em duas telas: Abra o site em duas abas do navegador. Em uma, fique no 'Studio' (Notebook). Na outra, vá em 'Apresentação', clique em F11 (Tela Cheia) e arraste para o Projetor/Datashow.")
    
    with st.form("ticket"):
        st.write("Fale com o desenvolvedor:")
        nome = st.text_input("Seu Nome")
        msg = st.text_area("Descreva o problema ou sugestão")
        if st.form_submit_button("Enviar"):
            st.success("Mensagem enviada! O anjo da TI responderá em breve.")

# --- LOADERS INICIAIS (Setup de arquivos) ---
if arquivo_sel != "+ Novo":
    try:
        path_txt = os.path.join(PASTA_USER, arquivo_sel)
        if os.path.exists(path_txt):
            with open(path_txt, 'r', encoding='utf-8') as f:
                 if st.session_state['texto_ativo'] == "": st.session_state['texto_ativo'] = f.read()
        # Tenta carregar slides associados
        path_json = os.path.join(PASTA_USER, f"{arquivo_sel.replace('.txt', '')}_slides.json")
        if os.path.exists(path_json) and not st.session_state['slides']:
            with open(path_json, 'r', encoding='utf-8') as f:
                st.session_state['slides'] = json.load(f)
            st.session_state['titulo_ativo'] = arquivo_sel.replace(".txt", "")
    except: pass
