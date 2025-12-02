import streamlit as st
import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime
from io import BytesIO
import SwiftUI

struct ContentView: View {
    var body: some View {
        // 1. Envolva sua visualização em um NavigationStack
        NavigationStack {
            List(0..<10) { item in
                NavigationLink("Item \(item)", destination: DetailView())
            }
            // 2. Adicione o título do cabeçalho com navigationTitle
            .navigationTitle("Meu App")
            
            // 3. (Opcional) Para um título grande padrão do iOS
            .navigationBarTitleDisplayMode(.automatic) 
        }
    }
}

struct DetailView: View {
    var body: some View {
        Text("Detalhe do Item")
            .navigationTitle("Detalhe")
    }
}

# --- 0. AUTO-INSTALAÇÃO DE DEPENDÊNCIAS ---
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

# --- 1. CONFIGURAÇÃO DO SISTEMA (APP) ---
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "APPLE DARK" & LOGOS HEADER ---
# Este CSS define o cabeçalho fixo, a fonte moderna e o visual "limpo".
st.markdown("""
    <style>
    /* IMPORTANDO FONTES MODERNAS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Merriweather:ital,wght@0,300;0,700;1,400&display=swap');

    :root {
        --bg-color: #0d0d0d;
        --panel-color: #1c1c1e;
        --border-color: #2c2c2e;
        --accent-color: #0A84FF;
        --text-color: #f5f5f7;
    }

    /* GLOBAL */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* REMOVE HEADER PADRÃO */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* CABEÇALHO FIXO "LOGOS STYLE" */
    .logos-header {
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 60px;
        background: rgba(28, 28, 30, 0.85); /* Vidro Escuro */
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-color);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .logo-area { font-weight: 700; font-size: 18px; color: #FFF; letter-spacing: 1px; display: flex; align-items: center; gap: 10px; }
    .gold-cross { color: #d4af37; font-size: 22px; }

    /* Espaçamento para o conteúdo não ficar embaixo do header fixo */
    .block-container {
        padding-top: 80px !important;
    }

    /* BOTÕES TIPO APPLE */
    div.stButton > button {
        background-color: #2c2c2e;
        color: white;
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        padding: 6px 15px;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: var(--accent-color);
        border-color: var(--accent-color);
        transform: scale(1.02);
    }

    /* ÁREA DE TEXTO ESTILO "THE WORD" */
    .stTextArea textarea {
        background-color: #151516 !important;
        border: 1px solid #333 !important;
        color: #ddd !important;
        font-family: 'Merriweather', serif; /* Fonte para leitura confortável */
        line-height: 1.8;
        font-size: 18px !important;
        border-radius: 8px;
    }
    
    /* MODAIS/CARDS */
    div[data-testid="stExpander"] {
        background-color: var(--panel-color);
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }
    </style>
    
    <!-- ELEMENTO HTML DO CABEÇALHO -->
    <div class="logos-header">
        <div class="logo-area">
            <span class="gold-cross">✝</span> O PREGADOR
            <span style="font-size:10px; color:#666; margin-top:5px; margin-left:5px">SYSTEM 4.0</span>
        </div>
        <div style="font-size: 13px; color: #888;">
            Central de Pregação Integrada
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. GESTÃO DE DADOS ---
PASTA_USER = "Banco_Sermoes"
os.makedirs(PASTA_USER, exist_ok=True)

if 'slides' not in st.session_state: st.session_state['slides'] = []
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""
if 'api_key' not in st.session_state: st.session_state['api_key'] = ""
if 'aba_atual' not in st.session_state: st.session_state['aba_atual'] = "Central"
if 'humor' not in st.session_state: st.session_state['humor'] = "Normal"

# --- 4. CÉREBRO (IA) COM EMPATIA ---
def assistente_ia(prompt, key, contexto="teologico"):
    if not key: return "⚠️ Conecte sua Chave nas Configurações."
    try:
        genai.configure(api_key=key)
        
        # 🧠 INTEGRAÇÃO EMOCIONAL
        humor_atual = st.session_state['humor']
        
        personalidade = "Você é um assistente teológico acadêmico."
        
        if contexto == "ajuda_emocional":
            if humor_atual in ["Esgotado (Burnout)", "Tristeza Profunda", "Ansioso"]:
                personalidade = """
                ATENÇÃO MÁXIMA: O usuário (pastor) está relatando sofrimento emocional (Burnout/Tristeza).
                Aja como um 'Pastor de Pastores', terapeuta cristão sábio e acolhedor.
                1. NÃO dê ordens. Valide a dor dele. (Ex: "Eu sinto muito, pastor. O peso é grande mesmo.")
                2. Use o exemplo de Elias (1 Reis 19) ou Jesus no Getsêmani: até gigantes cansam.
                3. Sugira descanso físico e busca por ajuda profissional (psicólogo/médico) com delicadeza.
                4. Termine com uma oração curta escrita em itálico.
                """
            else:
                personalidade = "Você é um mentor puritano encorajador. Dê conselhos bíblicos de ânimo."
        
        elif contexto == "chat":
             personalidade = f"Você é o assistente do software O Pregador. O usuário está se sentindo: {humor_atual}. Ajuste seu tom para ser empático a esse sentimento."

        model = genai.GenerativeModel("gemini-pro")
        return model.generate_content(f"{personalidade}\n\nPERGUNTA/TEXTO: {prompt}").text
    except Exception as e: return f"Erro de Conexão: {e}"

def gerar_imagem_social(texto, img_upload=None, cor_hex="#FFFFFF"):
    W, H = 1080, 1080
    bg_color = (20, 20, 20)
    
    if img_upload:
        try:
            img = Image.open(img_upload).convert("RGB").resize((W, H))
            img = img.filter(ImageFilter.GaussianBlur(4)) # Blur estiloso estilo Apple
        except: img = Image.new('RGB', (W, H), color=bg_color)
    else:
        img = Image.new('RGB', (W, H), color=bg_color)
        
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", 60)
    except: font = ImageFont.load_default()
    
    # Texto Centralizado
    linhas = texto.split('\n')
    total_h = len(linhas) * 70
    y_text = (H - total_h) / 2
    
    for linha in linhas:
        draw.text((100, y_text), linha, font=font, fill=cor_hex)
        y_text += 80
        
    draw.text((W-350, H-100), "O PREGADOR", fill="#d4af37", font=font)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- 5. INTERFACE (FRONT-END) ---

# MENU DE NAVEGAÇÃO "ATALHOS NO TOPO" (Simulado abaixo do header fixo)
def navegacao_topo():
    c1, c2, c3, c4, c5 = st.columns(5)
    modulo = None
    if c1.button("🏠 CENTRAL", use_container_width=True): modulo = "Central"
    if c2.button("✍️ STUDIO", use_container_width=True): modulo = "Studio"
    if c3.button("🎨 SOCIAL", use_container_width=True): modulo = "Social"
    if c4.button("🖥️ SLIDES", use_container_width=True): modulo = "Slides"
    if c5.button("⚙️ CONFIG", use_container_width=True): modulo = "Config"
    
    if modulo: 
        st.session_state['aba_atual'] = modulo
        st.rerun()

# --- SIDEBAR (PERFIL & CHAT INTEGRADO) ---
with st.sidebar:
    st.caption("CONTA")
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.write("Pr. Usuário")
    
    st.divider()
    
    # --- NOVO: SELETOR DE HUMOR ---
    st.caption("❤️ TERMÔMETRO EMOCIONAL")
    humor_ops = ["Bem / Normal", "Abençoado 🙏", "Cansado 😓", "Ansioso 😰", "Esgotado (Burnout) 🔴", "Tristeza Profunda 🌑"]
    st.session_state['humor'] = st.selectbox("Como você está?", humor_ops)
    
    if st.session_state['humor'] in ["Esgotado (Burnout) 🔴", "Tristeza Profunda 🌑", "Ansioso 😰"]:
        st.warning("⚠️ O Modo 'Cuidado Pastoral' foi ativado no Chat. Estamos aqui por você.")
    
    st.divider()
    
    # --- CHATBOT INTEGRADO ---
    with st.expander("💬 Chat Assistente", expanded=True):
        api_key = st.text_input("API Key (Google)", type="password", value=st.session_state['api_key'])
        st.session_state['api_key'] = api_key
        
        p_chat = st.text_input("Converse comigo:", placeholder="Preciso de ajuda...")
        if p_chat and api_key:
            # Envia contexto emocional para a IA
            res_chat = assistente_ia(p_chat, api_key, contexto="chat")
            st.markdown(f"**Assistente:** {res_chat}")


# --- ROTEAMENTO DE PÁGINAS ---

# 1. PÁGINA CENTRAL (DASHBOARD)
if st.session_state['aba_atual'] == "Central":
    navegacao_topo()
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_dash1, col_dash2 = st.columns([2, 1])
    
    with col_dash1:
        st.subheader("💡 Direção para Hoje")
        # IA PROATIVA BASEADA NO HUMOR
        if api_key:
            if st.button("Receber Palavra do Dia (Personalizada)"):
                with st.spinner("O Espírito sopra onde quer..."):
                    msg = assistente_ia("Dê-me uma palavra para hoje.", api_key, contexto="ajuda_emocional")
                    st.success(msg)
        else:
            st.info("Insira sua chave no menu lateral para ativar a inteligência pastoral.")
            
        st.markdown("---")
        st.markdown("### 📂 Acesso Rápido")
        files = os.listdir(PASTA_USER)
        if files:
            for f in files[:5]:
                if f.endswith(".txt"):
                    st.markdown(f"📄 {f.replace('.txt','')}")
        else:
            st.caption("Nenhum sermão encontrado.")

    with col_dash2:
        st.markdown("""
        <div style="background:#1c1c1e; padding:20px; border-radius:15px; border:1px solid #333; text-align:center;">
            <h1 style="color:#0A84FF; font-size:40px;">Studio</h1>
            <p>O Pregador</p>
        </div>
        """, unsafe_allow_html=True)

# 2. STUDIO (EDITOR + SLIDES LATERAL)
elif st.session_state['aba_atual'] == "Studio":
    navegacao_topo()
    st.markdown("<br>", unsafe_allow_html=True)

    # Toolbar de Arquivo
    c_file, c_name, c_act = st.columns([2, 3, 2])
    with c_file:
        arquivo_aberto = st.selectbox("Abrir:", ["+ Novo"] + os.listdir(PASTA_USER))
        
        # Carregamento automático ao mudar seleção
        if 'last_load' not in st.session_state: st.session_state['last_load'] = ""
        if arquivo_aberto != st.session_state['last_load']:
            st.session_state['last_load'] = arquivo_aberto
            if arquivo_aberto != "+ Novo":
                try:
                    with open(os.path.join(PASTA_USER, arquivo_aberto), 'r', encoding='utf-8') as f:
                        st.session_state['texto_ativo'] = f.read()
                    # Tenta carregar slides
                    slide_path = os.path.join(PASTA_USER, arquivo_aberto.replace('.txt', '_slides.json'))
                    if os.path.exists(slide_path):
                        with open(slide_path, 'r', encoding='utf-8') as f: st.session_state['slides'] = json.load(f)
                    st.session_state['titulo_ativo'] = arquivo_aberto.replace(".txt", "")
                except: pass
            else:
                st.session_state['titulo_ativo'] = ""
                st.session_state['texto_ativo'] = ""

    with c_name:
        titulo = st.text_input("Título", value=st.session_state['titulo_ativo'], label_visibility="collapsed", placeholder="Título da Mensagem...")
    
    with c_act:
        if st.button("💾 SALVAR TUDO", type="primary", use_container_width=True):
            if titulo:
                # Salvar TXT
                with open(os.path.join(PASTA_USER, f"{titulo}.txt"), 'w', encoding='utf-8') as f:
                    f.write(st.session_state['texto_ativo'])
                # Salvar Slides JSON
                with open(os.path.join(PASTA_USER, f"{titulo}_slides.json"), 'w', encoding='utf-8') as f:
                    json.dump(st.session_state['slides'], f)
                st.toast("Projeto salvo com sucesso!", icon="✅")

    # ÁREA DE TRABALHO DIVIDIDA
    c_txt, c_ppt = st.columns([1.5, 1])
    
    # COLUNA ESQUERDA: EDITOR DE TEXTO
    with c_txt:
        st.caption("MANUSCRITO")
        
        # Barra de Edição Rápida
        btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
        def ins(t): st.session_state['texto_ativo'] += t
        
        btn_c1.button("**B**", help="Negrito", on_click=ins, args=(" **texto** ",))
        btn_c2.button("*I*", help="Itálico", on_click=ins, args=(" *texto* ",))
        btn_c3.button("H1", help="Título", on_click=ins, args=("\n# ",))
        btn_c4.button("Vers.", help="Inserir Versículo (Exemplo)", on_click=ins, args=("\n> Jo 3:16\n",))
        
        txt_in = st.text_area("", value=st.session_state['texto_ativo'], height=600, key="main_editor", label_visibility="collapsed")
        st.session_state['texto_ativo'] = txt_in # Sync
        
        st.caption(f"Caracteres: {len(txt_in)}")

    # COLUNA DIREITA: GERENCIADOR DE SLIDES (ARRASTAR IDEAL)
    with c_ppt:
        st.caption("GERENCIADOR DE SLIDES")
        st.info("💡 Copie texto do lado esquerdo e cole aqui para criar slide.")
        
        # Adicionar novo slide
        novo_conteudo = st.text_area("Texto para o Slide:", height=100)
        col_btn_add, col_btn_clear = st.columns([3, 1])
        if col_btn_add.button("⬇️ Adicionar como Slide"):
            if novo_conteudo:
                st.session_state['slides'].append({"texto": novo_conteudo, "img": None})
                st.toast("Slide Adicionado!")
        
        st.divider()
        
        # Lista de Slides
        if st.session_state['slides']:
            for i, slide in enumerate(st.session_state['slides']):
                with st.expander(f"Slide {i+1}: {slide['texto'][:20]}..."):
                    st.write(slide['texto'])
                    if st.button(f"Remover {i+1}", key=f"del_{i}"):
                        st.session_state['slides'].pop(i)
                        st.rerun()
        else:
            st.caption("Nenhum slide criado.")

# 3. SOCIAL STUDIO
elif st.session_state['aba_atual'] == "Social":
    navegacao_topo()
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("Criador de Posts")
    
    col_social_1, col_social_2 = st.columns([1, 1.5])
    
    with col_social_1:
        s_txt = st.text_area("Frase do Card:", "Tudo posso naquele que me fortalece.\nFilipenses 4:13")
        s_file = st.file_uploader("Fundo (Opcional):", type=['png','jpg'])
        s_cor = st.color_picker("Cor da Fonte:", "#ffffff")
        
        if st.button("Gerar Imagem"):
            st.session_state['img_gerada'] = gerar_imagem_social(s_txt, s_file, s_cor)
            
    with col_social_2:
        if 'img_gerada' in st.session_state:
            st.image(st.session_state['img_gerada'], use_column_width=True)
            st.download_button("Baixar PNG", st.session_state['img_gerada'], "card_pregador.png", "image/png")

# 4. SLIDES / APRESENTAÇÃO
elif st.session_state['aba_atual'] == "Slides":
    navegacao_topo()
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state['slides']:
        st.warning("Crie slides no Studio primeiro.")
    else:
        # VISÃO DE OPERADOR
        if 'idx_slide' not in st.session_state: st.session_state['idx_slide'] = 0
        
        current = st.session_state['slides'][st.session_state['idx_slide']]
        
        col_prev, col_main, col_next = st.columns([1, 6, 1])
        
        with col_prev:
            if st.button("◀", use_container_width=True):
                st.session_state['idx_slide'] = max(0, st.session_state['idx_slide']-1)
                st.rerun()
        
        with col_main:
            # RENDERIZA O SLIDE ESTILO PROJETOR
            html_content = current['texto'].replace('\n', '<br>')
            st.markdown(f"""
            <div style="
                width:100%; height: 60vh; background: black; color: white;
                display:flex; justify-content:center; align-items:center;
                text-align:center; font-size:40px; font-weight:bold;
                border: 4px solid #333; border-radius:10px;
                text-shadow: 2px 2px 4px #000;
            ">
                {html_content}
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Slide {st.session_state['idx_slide']+1} / {len(st.session_state['slides'])}")

        with col_next:
            if st.button("▶", use_container_width=True):
                st.session_state['idx_slide'] = min(len(st.session_state['slides'])-1, st.session_state['idx_slide']+1)
                st.rerun()

# 5. CONFIG
elif st.session_state['aba_atual'] == "Config":
    navegacao_topo()
    st.title("Preferências")
    st.info("Configurações do Sistema 4.0")
    st.text_input("Seu Nome")
    st.text_input("Nome da Igreja")
    if st.button("Salvar"): st.toast("Salvo")
