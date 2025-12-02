import streamlit as st
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from duckduckgo_search import DDGS
import requests
from streamlit_lottie import st_lottie
from fpdf import FPDF

# --- 1. INSTALAÇÃO BLINDADA ---
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
    st.rerun()

# --- 2. CONFIGURAÇÃO VISUAL INICIAL ---
st.set_page_config(
    page_title="O PREGADOR", 
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# --- 3. GESTÃO DE PREFERÊNCIAS DO USUÁRIO (JSON LOCAL) ---
def carregar_preferencias(usuario):
    arquivo_pref = f"prefs_{usuario}.json"
    if os.path.exists(arquivo_pref):
        with open(arquivo_pref, 'r') as f: return json.load(f)
    return {
        "tema": "Dark Theology",
        "biblia": "NVI (Nova Versão Internacional)",
        "igreja": "Minha Igreja",
        "nome_pastor": usuario.capitalize()
    }

def salvar_preferencias(usuario, dados):
    with open(f"prefs_{usuario}.json", 'w') as f: json.dump(dados, f)

# --- 4. TEMAS E ESTILOS CSS (Visual Futurista e Personalizável) ---
TEMAS = {
    "Dark Theology": {"bg": "#121212", "txt": "#E0E0E0", "destaque": "#d4af37", "card": "#1E1E1E"},
    "Luz Divina":    {"bg": "#f0f2f6", "txt": "#262730", "destaque": "#2980b9", "card": "#ffffff"},
    "Papiro Antigo": {"bg": "#fdf6e3", "txt": "#586e75", "destaque": "#b58900", "card": "#eee8d5"},
    "Midnight Blue": {"bg": "#0f172a", "txt": "#94a3b8", "destaque": "#38bdf8", "card": "#1e293b"},
}

def aplicar_estilo(tema_nome):
    t = TEMAS.get(tema_nome, TEMAS["Dark Theology"])
    st.markdown(f"""
    <style>
    /* ANIMAÇÃO FUTURISTA NO FUNDO (Tela Login) */
    @keyframes gradient {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}
    .stApp {{
        background-color: {t['bg']};
    }}
    
    /* Remove elementos padrão */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}

    /* Inputs Modernos */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {{
        background-color: {t['card']} !important;
        border: 1px solid {t['destaque']}40 !important; /* Transparência no boarda */
        color: {t['txt']} !important;
        border-radius: 8px;
    }}
    
    /* Área de Texto Estilo WORD */
    .stTextArea textarea {{
        font-family: 'Georgia', serif; 
        font-size: 19px !important;
        line-height: 1.8;
        padding: 40px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    /* Títulos e Headers */
    h1, h2, h3, h4 {{ color: {t['destaque']} !important; }}
    p, label, span {{ color: {t['txt']} !important; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {t['bg']};
        border-right: 1px solid {t['card']};
    }}
    
    /* Botões */
    div.stButton > button {{
        background: linear-gradient(145deg, {t['card']}, {t['bg']});
        color: {t['txt']};
        border: 1px solid {t['destaque']};
    }}
    
    /* Slides Apresentação */
    .slide-card {{
        background-color: {t['card']};
        color: {t['txt']};
        padding: 60px;
        border-radius: 15px;
        border: 2px solid {t['destaque']};
        min-height: 60vh;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. HELPERS ---
LOTTIE_URLS = {
    "cross": "https://lottie.host/80f76906-8d19-484c-b715-4f466b0a2c0c/EpxKCVG6xZ.json", # Cruz Atual
    "study": "https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json",
}

USUARIOS = {"admin": "1234", "pr": "123"}

def load_lottie_safe(url):
    try:
        r = requests.get(url, timeout=1.5)
        if r.status_code == 200: return r.json()
    except: pass
    return None

def consultar_cerebro(prompt, chave, modo="teologo"):
    if not chave: return "⚠️ Conecte a Chave Mestra no Menu Lateral."
    try:
        genai.configure(api_key=chave)
        # Personas Aprimoradas
        system_msg = "Você é um assistente teológico acadêmico."
        if modo == "puritano":
            system_msg = "Você é um pastor puritano experiente e sábio (como Spurgeon ou John Edwards). Fale com autoridade, amor pastoral e use teologia profunda. Dê conselhos práticos e encorajadores."
        elif modo == "ilustrador":
            system_msg = "Você é um mestre em Storytelling para sermões."
            
        model = genai.GenerativeModel('gemini-pro')
        full = f"{system_msg}\nCONTEXTO: {prompt}"
        
        with st.spinner("Meditando na resposta..."):
            return model.generate_content(full).text
    except Exception as e: return f"Silêncio no céu (Erro): {e}"

def gerar_pdf(titulo, texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', 16)
    clean_title = titulo.encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(0, 10, clean_title, 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Times", size=12)
    clean_text = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. TELA DE LOGIN FUTURISTA ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    # Fundo animado via CSS
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        height: 100vh;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Cruz moderna (Lottie ou SVG simulado se falhar)
        anim_cross = load_lottie_safe(LOTTIE_URLS["cross"])
        if anim_cross:
            st_lottie(anim_cross, height=150, key="login_anim")
        else:
            st.markdown("<h1 style='text-align:center; font-size: 80px;'>✝️</h1>", unsafe_allow_html=True)
            
        st.markdown("<h1 style='text-align: center; font-family: sans-serif; letter-spacing: 5px; color: #FFF;'>O PREGADOR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #AAA; letter-spacing: 2px;'>SYSTEM 3.0</p>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            u = st.text_input("Identificação")
            s = st.text_input("Chave de Acesso", type="password")
            if st.form_submit_button("CONECTAR", type="primary", use_container_width=True):
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
    st.stop()

# --- 7. CARREGAMENTO DO USUÁRIO & ESTILO ---
USER = st.session_state['user']
prefs = carregar_preferencias(USER)

# Aplica o tema escolhido pelo usuário
aplicar_estilo(prefs.get("tema", "Dark Theology"))

# Pastas e Diretórios
PASTA_USER = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA_USER, exist_ok=True)

# Variaveis de Estado Globais
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""
if 'slide_atual' not in st.session_state: st.session_state['slide_atual'] = 0
if 'humor_hoje' not in st.session_state: st.session_state['humor_hoje'] = "Neutro"

# === MENU LATERAL (PERSONALIZAÇÃO) ===
with st.sidebar:
    st.markdown(f"## {prefs['nome_pastor']}")
    st.caption(prefs['igreja'])
    
    # Navegação
    menu = st.radio("Navegação", ["🏠 Central Pastoral", "✍️ Studio Editor", "📚 Laboratório", "🕶️ Apresentação"])
    
    st.divider()
    
    # Área de Configurações
    with st.expander("⚙️ Configurações & Personalização"):
        st.caption("Ajustes do Sistema")
        novo_tema = st.selectbox("Tema Visual", list(TEMAS.keys()), index=list(TEMAS.keys()).index(prefs.get("tema", "Dark Theology")))
        nova_biblia = st.selectbox("Bíblia Preferida", ["NVI (Nova Versão Internacional)", "ACF (Almeida Corrigida)", "NAA (Nova Almeida)", "KJA (King James)"], index=0)
        
        # Atualização de perfil
        st.caption("Seus Dados")
        novo_nome = st.text_input("Seu Nome/Título", value=prefs['nome_pastor'])
        nova_igreja = st.text_input("Sua Igreja", value=prefs['igreja'])
        
        if st.button("💾 Salvar Perfil"):
            prefs['tema'] = novo_tema
            prefs['biblia'] = nova_biblia
            prefs['nome_pastor'] = novo_nome
            prefs['igreja'] = nova_igreja
            salvar_preferencias(USER, prefs)
            st.success("Salvo! Recarregando...")
            time.sleep(1)
            st.rerun()

    # Cronômetro
    if 'cron_on' not in st.session_state: st.session_state['cron_on'] = None
    if st.button("⏱️ Cronômetro de Ensaio"):
        st.session_state['cron_on'] = time.time() if not st.session_state['cron_on'] else None
    
    if st.session_state['cron_on']:
        t = int(time.time() - st.session_state['cron_on'])
        st.metric("Tempo", f"{t//60:02}:{t%60:02}")

    with st.expander("🔑 Chave IA"):
        api_key = st.text_input("Google API Key", type="password")

    st.divider()
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

# === CONTEÚDO PRINCIPAL ===

# 🏠 CENTRAL PASTORAL
if menu == "🏠 Central Pastoral":
    st.title("Central Pastoral")
    st.markdown(f"*{datetime.now().strftime('%A, %d de %B')} | Bíblia ativa: {prefs['biblia']}*")
    
    c1, c2 = st.columns([1.8, 1])
    
    with c1:
        # Mood Tracker (Emoções)
        st.markdown("#### Como está seu coração hoje, pastor?")
        emocoes = {"🙏 Grato": "gratidão", "😃 Animado": "alegria", "😔 Cansado": "cansaço", "😰 Ansioso": "ansiedade", "🔥 Zeloso": "fogo"}
        col_emos = st.columns(len(emocoes))
        
        for idx, (emoji, sentimento) in enumerate(emocoes.items()):
            if col_emos[idx].button(emoji, use_container_width=True):
                st.session_state['humor_hoje'] = sentimento
                st.session_state['devocional'] = None # Força regenerar devocional
                st.toast(f"Registrado: {emoji}")

        # Palavra do Dia com Viés Puritano e Pessoal
        st.markdown("---")
        st.markdown(f"### 🕯️ Conselho Pastoral ({st.session_state['humor_hoje'].capitalize()})")
        
        if api_key:
            if not st.session_state.get('devocional'):
                humor = st.session_state['humor_hoje']
                biblia = prefs['biblia']
                prompt = f"""
                O usuário é um pastor e hoje está se sentindo: {humor}.
                Aja como um mentor puritano sábio (tom pastoral, sério, mas encorajador e cheio de graça).
                1. Dê um conselho teológico profundo, mas aplicável.
                2. Dê um incentivo ministerial para continuar a obra.
                3. Cite um versículo chave na versão {biblia}.
                Mantenha um tom atual, conectado com os desafios da modernidade, mas com raízes antigas.
                """
                st.session_state['devocional'] = consultar_cerebro(prompt, api_key, "puritano")
            
            st.info(st.session_state['devocional'])
        else:
            st.warning("Insira sua chave API no menu para receber seu alimento diário.")

    with c2:
        # Cartão de Informações
        st.markdown(f"""
        <div style="background:{TEMAS.get(prefs['tema'], TEMAS['Dark Theology'])['card']}; padding:20px; border-radius:10px; border-left:5px solid #d4af37">
            <h4>📊 Resumo</h4>
            <p>Sermões Criados: {len(os.listdir(PASTA_USER))}</p>
            <p>Pastas: {len([d for d in os.listdir(PASTA_USER) if os.path.isdir(os.path.join(PASTA_USER, d))])}</p>
            <p>Humor Atual: {st.session_state['humor_hoje']}</p>
        </div>
        """, unsafe_allow_html=True)
        try: st_lottie(requests.get(LOTTIE_URLS['study']).json(), height=180)
        except: pass

# ✍️ STUDIO EDITOR (WORD STYLE)
elif menu == "✍️ Studio Editor":
    # 1. SISTEMA DE ARQUIVOS (PASTAS)
    c_pasta, c_arq, c_opcoes = st.columns([1, 2, 1])
    
    with c_pasta:
        # Criar/Selecionar Pasta
        subpastas = [d for d in os.listdir(PASTA_USER) if os.path.isdir(os.path.join(PASTA_USER, d))]
        pasta_sel = st.selectbox("📂 Pasta:", ["Geral"] + subpastas)
        
        if pasta_sel == "Geral":
            caminho_atual = PASTA_USER
        else:
            caminho_atual = os.path.join(PASTA_USER, pasta_sel)

    with c_arq:
        arquivos = [f for f in os.listdir(caminho_atual) if f.endswith('.txt')]
        escolha = st.selectbox("📄 Arquivo:", ["+ Novo"] + arquivos, label_visibility="visible")

    with c_opcoes:
        if st.button("📁 Nova Pasta"):
            st.session_state['criando_pasta'] = True
    
    if st.session_state.get('criando_pasta'):
        nome_pasta = st.text_input("Nome da Pasta:")
        if st.button("Criar"):
            if nome_pasta: os.makedirs(os.path.join(PASTA_USER, nome_pasta), exist_ok=True); st.rerun()

    # Lógica de Carregamento
    if 'last_open' not in st.session_state: st.session_state['last_open'] = ""
    file_id = f"{pasta_sel}/{escolha}" # ID unico
    
    if file_id != st.session_state['last_open']:
        st.session_state['last_open'] = file_id
        if escolha != "+ Novo":
            st.session_state['titulo_ativo'] = escolha.replace(".txt", "")
            try:
                with open(os.path.join(caminho_atual, escolha), 'r', encoding='utf-8') as f:
                    st.session_state['texto_ativo'] = f.read()
            except: pass
        else:
            st.session_state['titulo_ativo'] = ""
            st.session_state['texto_ativo'] = ""

    # 2. EDITOR "WORD" (Barra de Ferramentas e Tela Cheia)
    
    st.divider()
    
    # Barra de Ferramentas
    c_tit, c_toolbar = st.columns([3, 2])
    with c_tit:
        st.text_input("Título do Sermão", key="titulo_ativo", placeholder="Digite o tema...")
    
    with c_toolbar:
        st.markdown("**Ferramentas:**")
        bt1, bt2, bt3, bt4 = st.columns(4)
        def inserir(t): st.session_state['texto_ativo'] += t
        
        bt1.button("H1", on_click=inserir, args=("\n# ",), help="Título Grande")
        bt2.button("Negrito", on_click=inserir, args=(" **texto** ",), help="Negrito")
        bt3.button("Intro", on_click=inserir, args=("\n# INTRODUÇÃO\n\n",))
        bt4.button("Fim", on_click=inserir, args=("\n# CONCLUSÃO\n\n",))

    # EDITOR VISUAL (Wide Area)
    st.text_area("Desenvolvimento (Ortografia ativa no navegador)", key="texto_ativo", height=600)
    
    # Rodapé do Editor
    col_salvar, col_dl, col_stats = st.columns([1,1,1])
    with col_salvar:
        if st.button("💾 Salvar na Nuvem (Local)", type="primary", use_container_width=True):
            if st.session_state['titulo_ativo']:
                caminho_final = os.path.join(caminho_atual, f"{st.session_state['titulo_ativo']}.txt")
                with open(caminho_final, 'w', encoding='utf-8') as f: f.write(st.session_state['texto_ativo'])
                st.toast(f"Salvo em '{pasta_sel}'!", icon="☁️")

    with col_dl:
        if st.session_state['titulo_ativo']:
            pdf_bytes = gerar_pdf(st.session_state['titulo_ativo'], st.session_state['texto_ativo'])
            st.download_button("📥 Baixar no PC (PDF)", pdf_bytes, f"{st.session_state['titulo_ativo']}.pdf", "application/pdf", use_container_width=True)

    with col_stats:
        contagem = len(st.session_state['texto_ativo'].split())
        st.caption(f"Palavras: {contagem} | Estimativa de Fala: ~{contagem//130} min")


# 📚 LABORATÓRIO (Exegese + Auxílios)
elif menu == "📚 Laboratório":
    st.header("Laboratório Teológico")
    tabs = st.tabs(["🔎 Exegese Profunda", "🎨 Fábrica de Ilustrações", "🧠 Assistente IA"])
    
    with tabs[0]:
        vers = st.text_input("Passagem:", placeholder="Jo 3:16")
        if st.button("Dissecar Texto"):
            resp = consultar_cerebro(f"Faça uma análise profunda de {vers} considerando o original (grego/hebraico), morfologia e contexto histórico.", api_key)
            st.markdown(resp)

    with tabs[1]:
        st.caption("Crie analogias perfeitas")
        tema = st.text_input("Tema:", placeholder="Graça, Pecado...")
        tipo = st.selectbox("Estilo", ["Vida Real", "Científico", "Histórico"])
        if st.button("Gerar História"):
            resp = consultar_cerebro(f"Crie uma ilustração curta sobre {tema} estilo {tipo}.", api_key, "ilustrador")
            st.info(resp)


# 🕶️ APRESENTAÇÃO (POWER POINT STYLE)
elif menu == "🕶️ Apresentação":
    if not st.session_state['texto_ativo']:
        st.warning("Abra um texto no Studio primeiro.")
    else:
        # Prepara Slides
        slides = [s.strip() for s in st.session_state['texto_ativo'].split('\n\n') if s.strip()]
        if slides:
            # Controle de Slides
            cols = st.columns([1, 6, 1])
            if cols[0].button("◀", use_container_width=True): 
                st.session_state['slide_atual'] = max(0, st.session_state['slide_atual']-1)
            
            with cols[1]:
                pg = st.session_state['slide_atual'] + 1
                ttl = len(slides)
                st.progress(pg/ttl)
                st.caption(f"Slide {pg}/{ttl}")

            if cols[2].button("▶", use_container_width=True): 
                st.session_state['slide_atual'] = min(len(slides)-1, st.session_state['slide_atual']+1)

            # O SLIDE EM SI
            conteudo = slides[st.session_state['slide_atual']]
            conteudo_html = conteudo.replace('\n', '<br>')
            # Renderiza cartão grande estilo PPT
            st.markdown(f"""
            <div class="slide-card">
                <div style="font-size: 38px; line-height: 1.5; font-weight: bold;">
                {conteudo_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Texto muito curto para gerar slides.")
