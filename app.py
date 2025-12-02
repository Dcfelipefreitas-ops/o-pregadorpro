import streamlit as st
import os
import requests
import tempfile
from gtts import gTTS
import PyPDF2

# --- 1. CONFIGURAÇÃO GERAL (V10 BUSINESS) ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🪵", initial_sidebar_state="expanded")

# --- 2. GESTÃO DE ESTADO (Para não resetar a cada clique) ---
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 70
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'anuncios_ativos' not in st.session_state: st.session_state['anuncios_ativos'] = ""

# Importações de IA (Segurança)
try:
    from duckduckgo_search import DDGS
    import google.generativeai as genai
    HAS_IA = True
except: HAS_IA = False

# --- 3. CSS EXCLUSIVO "WOODEN APPLE" ---
# Mistura o vidro da Apple com a textura de madeira do pregador
st.markdown(f"""
<style>
    /* FONTE */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* WALLPAPER DINÂMICO */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* MODAIS DE VIDRO */
    [data-testid="stSidebar"], .stTextArea textarea, div[data-testid="stExpander"] {{
        background: rgba(18, 18, 20, 0.85) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #f0f0f0 !important;
        border-radius: 12px;
    }}
    
    /* EDITOR DE TEXTO (Papel Profissional) */
    .stTextArea textarea {{
        font-family: 'Inter', sans-serif;
        font-size: 18px !important;
        line-height: 1.6;
        padding: 20px;
    }}
    .stTextArea textarea:focus {{
        border-color: #eab308 !important; /* Amarelo Ouro */
    }}
    
    /* BOTÕES COM TEXTURA SUAVE */
    .stButton button {{
        background-color: #262626;
        color: white;
        border: 1px solid #404040;
        border-radius: 8px;
        transition: 0.2s;
    }}
    .stButton button:hover {{
        background-color: #eab308;
        color: black;
        border-color: #eab308;
    }}
    
    /* LOGO DA MADEIRA NO CSS */
    .wooden-clip {{
        font-size: 50px;
        text-align: center;
        margin-bottom: -20px;
    }}
    
    /* ESPAÇO DE ANÚNCIO */
    .ad-card {{
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid gold;
        padding: 10px;
        border-radius: 8px;
        margin-top: 20px;
        text-align: center;
    }}
    .ad-card a {{ color: #eab308; font-weight: bold; text-decoration: none; }}
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE IA E NEGÓCIO ---

def conectar_ia(chave):
    if not chave: return None
    try:
        genai.configure(api_key=chave)
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

def corretor_pro(texto, modelo):
    """Corrige o texto mantendo o estilo pastoral"""
    if not modelo: return texto
    try:
        p = f"Atue como um editor de livros cristãos. Corrija gramática, pontuação e melhore a fluidez deste texto, mantendo a teologia correta:\n\n{texto}"
        return modelo.generate_content(p).text
    except: return texto

def gerar_anuncios(tema, modelo):
    """MONETIZAÇÃO: Gera links de afiliados baseados no sermão"""
    if not modelo or len(tema) < 5: return "Buscando parceiros..."
    try:
        p = f"Com base no tema '{tema}', sugira 2 títulos de livros cristãos reais para estudo aprofundado. Retorne apenas Título - Autor."
        return modelo.generate_content(p).text
    except: return ""

def modo_dev_codigo(pedido, modelo):
    """Gera código Python para o próprio app"""
    if not modelo: return "IA Offline."
    try:
        p = f"Gere apenas o código Python (Streamlit) para atender este pedido: {pedido}. Não explique, só mande o código."
        return modelo.generate_content(p).text
    except: return "Erro ao gerar."

def buscar_biblia(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref.replace(' ', '+')}?translation=almeida", timeout=2)
        if r.status_code == 200: return r.json()
    except: return None

# --- 5. TELA DE LOGIN ---
if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div class='wooden-clip'>🪵</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center'>O PREGADOR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color:#888'>Edição Business</p>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Login")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema", type="primary"):
                # Senha simples
                if u in ["admin", "pastor"] and s in ["1234", "pregar"]:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Negado")
    st.stop()

# --- 6. ÁREA DE TRABALHO ---
USER = st.session_state['user']
PASTA = os.path.join("Banco_Sermoes", USER)
if not os.path.exists(PASTA): os.makedirs(PASTA)

# -> BARRA LATERAL (MENU & ANÚNCIOS)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9384/9384192.png", width=60) # Imagem de Pregador de Roupa (Link público estável)
    st.markdown("### O PREGADOR")
    
    # 1. SETUP DE API (Essencial para IA)
    api_key = st.text_input("Chave Google IA (Senha)", type="password")
    if not api_key: api_key = st.secrets.get("GOOGLE_API_KEY", "")
    modelo = conectar_ia(api_key)
    
    tab1, tab2 = st.tabs(["ARQUIVOS", "CONFIG"])
    
    with tab1:
        # Lista de arquivos
        try: files = [f.replace(".txt","") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except: files = []
        sel = st.radio("Seus Projetos:", ["+ Novo"] + files, label_visibility="collapsed")
        
        if st.button("Sair"): st.session_state['logado']=False; st.rerun()

    with tab2:
        st.caption("Personalização Visual")
        novo_fundo = st.text_input("Link da Imagem Fundo:", value=st.session_state['bg_url'])
        if st.button("Mudar Fundo"):
            st.session_state['bg_url'] = novo_fundo
            st.rerun()
        
        tamanho = st.slider("Largura Editor", 50, 90, st.session_state['layout_split'])
        st.session_state['layout_split'] = tamanho

    # --- ÁREA DE MONETIZAÇÃO (ANÚNCIOS INTELIGENTES) ---
    st.divider()
    st.markdown("### ⭐ Loja do Pregador")
    # Mostra sugestões baseadas no que o pastor está escrevendo
    if st.session_state['anuncios_ativos']:
        st.info("📚 **Sugestão de Estudo:**")
        st.caption(st.session_state['anuncios_ativos'])
        st.markdown("[Comprar na Amazon >](https://amazon.com.br)", unsafe_allow_html=True)
    else:
        st.caption("Escreva um sermão para ver sugestões de livros...")

# -> LAYOUT DO EDITOR E FERRAMENTAS
proporcao = st.session_state['layout_split'] / 100
col_main, col_tools = st.columns([proporcao, 1 - proporcao])

# LOGICA CARREGAMENTO
texto_atual = ""
titulo_atual = ""
if sel != "+ Novo":
    titulo_atual = sel
    try:
        with open(os.path.join(PASTA, f"{sel}.txt"), "r") as f: texto_atual = f.read()
    except: pass

with col_main:
    # Cabeçalho
    c_h1, c_h2 = st.columns([4, 1])
    with c_h1:
        new_tit = st.text_input("Título", value=titulo_atual, placeholder="Título da Mensagem...", label_visibility="collapsed")
    with c_h2:
        if st.button("💾 SALVAR", use_container_width=True, type="primary"):
            if new_tit:
                with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(texto_atual)
                # Aciona IA para gerar anúncio monetizado
                anuncio = gerar_anuncios(new_tit, modelo)
                st.session_state['anuncios_ativos'] = anuncio
                st.toast("Salvo & Anúncios Atualizados!")
                st.rerun()

    # O PAPEL (EDITOR)
    texto_editado = st.text_area("Papel", value=texto_atual, height=750, label_visibility="collapsed")
    
    # Barra de Corretor Integrada
    c_corr1, c_corr2 = st.columns([1,3])
    with c_corr1:
        if st.button("✨ CORRIGIR ORTOGRAFIA"):
            if modelo:
                with st.spinner("Revisando..."):
                    corrigido = corretor_pro(texto_editado, modelo)
                    # Atualiza o arquivo automaticamente
                    with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(corrigido)
                    st.success("Texto melhorado! Recarregue.")
            else: st.warning("IA Offline.")
    with c_corr2:
        st.caption("Dica: Use `Win + H` para digitar com voz direto no navegador.")

with col_tools:
    st.markdown("#### 🛠 Ferramentas")
    aba1, aba2, aba3, aba_dev = st.tabs(["📖 BÍBLIA", "🗣 TRAD", "🌍 WEB", "👨‍💻 DEV"])
    
    with aba1: # Bíblia com Áudio
        ref = st.text_input("Verso (Jo 3 16)")
        if ref:
            dados = buscar_biblia(ref)
            if dados:
                txt_b = f"{dados['text']}"
                st.info(f"{dados['reference']}\n\n{txt_b}")
                
                c_a1, c_a2 = st.columns(2)
                if c_a1.button("Inserir"):
                    novo_t = texto_editado + f"\n\n**{dados['reference']}**\n{txt_b}"
                    with open(os.path.join(PASTA, f"{new_tit}.txt"), "w") as f: f.write(novo_t)
                    st.rerun()
                
                if c_a2.button("🔊 Ouvir"):
                    tts = gTTS(txt_b, lang='pt')
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name)

    with aba2: # Tradutor IA
        origem = st.text_area("Texto em Inglês/Grego:")
        if st.button("Traduzir"):
            if modelo: st.write(modelo.generate_content(f"Traduza para teologia PT-BR: {origem}").text)

    with aba3: # Web / Monetização
        termo = st.text_input("Pesquisar:")
        if st.button("Buscar"):
            try:
                res = DDGS().text(termo, max_results=3)
                for r in res:
                    st.markdown(f"**[{r['title']}]({r['href']})**")
            except: st.error("Erro busca")

    with aba_dev: # DEV MODE (Gerar códigos)
        st.warning("⚠️ Modo Criador")
        pedido = st.text_area("O que você quer adicionar ao código?")
        if st.button("Gerar Código"):
            st.code(modo_dev_codigo(pedido, modelo), language='python')
            st.info("Copie este código e peça para eu integrar se gostar.")
