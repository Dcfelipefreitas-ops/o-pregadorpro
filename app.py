import streamlit as st
import os
import sys
import subprocess
import time
from datetime import datetime
from duckduckgo_search import DDGS
import requests
from streamlit_lottie import st_lottie
from fpdf import FPDF

# --- 1. INSTALAÇÃO BLINDADA (AUTO-REPAIR) ---
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
    st.rerun()

# --- 2. CONFIGURAÇÃO VISUAL (ESTILO "LOGOS DARK") ---
st.set_page_config(
    page_title="O Pregador | Studio", 
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# Paleta de Cores Inspirada em Softwares Profissionais
COR_DESTAQUE = "#d4af37" # Dourado Clássico
COR_FUNDO_EDITOR = "#1E1E1E" 
COR_SIDBAR = "#121212"

st.markdown(f"""
    <style>
    /* Remove itens nativos */
    header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    footer {{visibility: hidden;}}
    
    /* Sidebar Profissional */
    [data-testid="stSidebar"] {{
        background-color: {COR_SIDBAR};
        border-right: 1px solid #333;
    }}
    
    /* Editor "Focus Mode" */
    .stTextArea textarea {{
        background-color: {COR_FUNDO_EDITOR};
        color: #EAEAEA;
        font-family: 'Merriweather', serif; /* Fonte de Leitura */
        font-size: 20px !important;
        line-height: 1.7;
        padding: 30px;
        border: 1px solid #333;
        border-radius: 8px;
    }}
    
    /* Títulos e Headers */
    h1, h2, h3 {{ color: #F0F0F0; font-family: 'Helvetica Neue', sans-serif; letter-spacing: -0.5px; }}
    
    /* Botões Premium */
    div.stButton > button {{
        background-color: #2D2D2D; 
        color: white; 
        border: 1px solid #444;
        transition: 0.2s;
    }}
    div.stButton > button:hover {{
        border-color: {COR_DESTAQUE};
        color: {COR_DESTAQUE};
    }}
    
    /* Cards de Informação (Exegese) */
    .teologia-card {{
        background-color: #25262B;
        padding: 15px;
        border-left: 3px solid {COR_DESTAQUE};
        border-radius: 5px;
        margin-bottom: 10px;
        font-size: 0.9em;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS E HELPERS ---
LOTTIE_URLS = {
    "book": "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json", # Bíblia
    "worship": "https://lottie.host/b0429a39-a9e9-4089-8d5c-1970b551e18e/5e171b3b1f.json", # Louvor/Notícia
}

USUARIOS = {"admin": "1234", "pr": "123"}

def load_lottieurl(url):
    try: return requests.get(url, timeout=2).json()
    except: return None

def consultar_cerebro(prompt, chave, model_type="theology"):
    """
    Função de IA aprimorada para agir como teólogo.
    """
    if not chave: return "⚠️ Ative a 'Chave Mestra' (API) no menu lateral para liberar a inteligência."
    try:
        genai.configure(api_key=chave)
        # Ajustamos o modelo mental da IA
        system_instruction = "Você é um assistente teológico acadêmico erudito, especialista em hebraico, grego, hermenêutica e homilética. Responda de forma estruturada para pastores."
        if model_type == "sermon":
            system_instruction = "Você é um pregador eloquente e criativo. Ajude a estruturar esboços."
        
        model = genai.GenerativeModel('gemini-pro')
        full_prompt = f"{system_instruction}\n\nTarefa: {prompt}"
        
        with st.spinner("Consultando biblioteca teológica..."):
            return model.generate_content(full_prompt).text
    except Exception as e: return f"Erro na conexão com a base de conhecimento: {e}"

def gerar_pdf(titulo, texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', 16)
    pdf.cell(0, 10, titulo.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Times", size=12)
    clean_text = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. TELA DE LOGIN (Sua base mantida e estilizada) ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.write("\n\n")
        anim = load_lottieurl(LOTTIE_URLS["book"])
        if anim: st_lottie(anim, height=120)
        else: st.markdown("<h1 style='text-align:center'>✝️</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: #CCC;'>O Pregador <span style='color:#d4af37; font-size:0.6em'>STUDIO</span></h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar no Púlpito", type="primary", use_container_width=True)
            
            if entrar:
                if u in USUARIOS and USUARIOS[u] == s:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
    st.stop()

# --- 5. APLICAÇÃO PRINCIPAL ---
USER = st.session_state['user']
PASTA_USER = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA_USER, exist_ok=True)

# === SIDEBAR (Ferramentas Rápidas) ===
with st.sidebar:
    st_lottie(load_lottieurl(LOTTIE_URLS["book"]), height=50, key="side_logo")
    st.markdown(f"Teólogo: **{USER.capitalize()}**")
    
    # Navegação Estilo Abas de Software
    nav = st.radio("Módulos:", ["🏠 Dashboard", "✍️ Studio de Pregação", "📚 Biblioteca & Exegese", "🕶️ Modo Púlpito"])
    
    st.divider()
    st.markdown("🛠️ **Acesso Mestre**")
    with st.expander("🔑 Chave API (Google)", expanded=False):
        api_key = st.text_input("Insira API Key", type="password")
        st.caption("Necessário para funções 'Logos' (IA).")
    
    # Rodapé do sidebar com cronômetro
    st.divider()
    if 'cron_start' not in st.session_state: st.session_state['cron_start'] = None
    if st.button("⏱️ Cronômetro"):
        st.session_state['cron_start'] = time.time() if not st.session_state['cron_start'] else None
    
    if st.session_state['cron_start']:
        elapsed = int(time.time() - st.session_state['cron_start'])
        m, s = divmod(elapsed, 60)
        st.metric("Tempo decorrido", f"{m:02}:{s:02}")
    
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

# === LÓGICA GERAL DE ESTADO ===
# Gerenciamento de arquivo aberto globalmente
if 'texto_ativo' not in st.session_state: st.session_state['texto_ativo'] = ""
if 'titulo_ativo' not in st.session_state: st.session_state['titulo_ativo'] = ""

# Carrega lista de arquivos
arquivos_db = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]

# === TELA 1: DASHBOARD ===
if nav == "🏠 Dashboard":
    st.title("Central de Controle")
    st.markdown(f"*Paz seja convosco. Preparando o alimento espiritual de hoje.*")
    
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("💡 Inspiração Diária")
        if api_key:
            if 'verso_hoje' not in st.session_state:
                prompt = "Aja como um devocional diário 'Spurgeon'. Traga um versículo e uma aplicação de 2 frases para um pastor."
                st.session_state['verso_hoje'] = consultar_cerebro(prompt, api_key)
            st.info(st.session_state['verso_hoje'])
        else:
            st.warning("Conecte a inteligência (API Key) para receber devocionais.")
            
        st.subheader("📂 Sermões Recentes")
        if arquivos_db:
            for arq in arquivos_db[:4]:
                st.markdown(f"- 📄 **{arq.replace('.txt','')}**")
        else:
            st.caption("Biblioteca vazia.")

    with col2:
        st.markdown("""
        <div class="teologia-card">
            <b>Status do Púlpito</b><br>
            Sermões na base: {0}<br>
            Versão: O Pregador v3.0 Pro
        </div>
        """.format(len(arquivos_db)), unsafe_allow_html=True)


# === TELA 2: STUDIO DE PREGAÇÃO (EDITOR) ===
elif nav == "✍️ Studio de Pregação":
    # Barra de Ferramentas Superior
    c_sel, c_save, c_act = st.columns([3, 1, 1])
    
    with c_sel:
        arquivo_escolhido = st.selectbox("Selecione ou Crie:", ["+ Novo Esboço"] + arquivos_db, label_visibility="collapsed")
        
        # Lógica de Carregamento
        if 'last_file' not in st.session_state: st.session_state['last_file'] = ""
        
        if arquivo_escolhido != st.session_state['last_file']:
            st.session_state['last_file'] = arquivo_escolhido
            if arquivo_escolhido != "+ Novo Esboço":
                st.session_state['titulo_ativo'] = arquivo_escolhido.replace('.txt', '')
                try:
                    with open(os.path.join(PASTA_USER, arquivo_escolhido), 'r', encoding='utf-8') as f:
                        st.session_state['texto_ativo'] = f.read()
                except: pass
            else:
                st.session_state['titulo_ativo'] = ""
                st.session_state['texto_ativo'] = ""
    
    with c_save:
        if st.button("💾 Salvar", use_container_width=True, type="primary"):
            if st.session_state['titulo_ativo']:
                with open(os.path.join(PASTA_USER, f"{st.session_state['titulo_ativo']}.txt"), 'w', encoding='utf-8') as f:
                    f.write(st.session_state['texto_ativo'])
                st.toast("Guardado no cofre.", icon="✅")

    # Layout do Editor
    col_editor, col_ai = st.columns([2.2, 1])
    
    with col_editor:
        st.text_input("Tema / Título", key="titulo_ativo", placeholder="Ex: A Graça Irresistível")
        
        # Editor com atalhos de estrutura
        def add(txt): st.session_state['texto_ativo'] += txt
        
        b1, b2, b3, b4 = st.columns(4)
        b1.button("📌 Intro", on_click=add, args=("\n\n# INTRODUÇÃO\nContexto do texto...\nPropósito da mensagem...\n",), use_container_width=True)
        b2.button("I. Ponto", on_click=add, args=("\n\n## I. TÍTULO DO TÓPICO\nExplicação...\nIlustração...\nAplicação...\n",), use_container_width=True)
        b3.button("⚔️ Aplicação", on_click=add, args=("\n> APLICAÇÃO PRÁTICA:\nO que Deus quer de nós hoje?\n",), use_container_width=True)
        b4.button("🏁 Conclusão", on_click=add, args=("\n\n# CONCLUSÃO\nResumo...\nApelo...\n",), use_container_width=True)
        
        st.text_area("Canvas de Escrita", key="texto_ativo", height=600, label_visibility="collapsed")
    
    # Barra Lateral Direita (Ferramentas Contextuais)
    with col_ai:
        st.markdown("### 🧩 Auxílios Homiléticos")
        aba_i, aba_bib = st.tabs(["💡 Criativo", "📖 Bíblia"])
        
        with aba_i:
            st.caption("Fábrica de Ilustrações")
            tema_ilus = st.text_input("Assunto:", placeholder="Ex: Fé na tempestade")
            estilo = st.selectbox("Tipo:", ["Metáfora da Natureza", "História Real", "Fato Científico", "Analogia Histórica"])
            if st.button("Gerar Ilustração"):
                resp = consultar_cerebro(f"Crie uma ilustração de sermão ({estilo}) sobre: {tema_ilus}", api_key, "sermon")
                st.info(resp)
                
        with aba_bib:
            st.caption("Referências Cruzadas")
            vers = st.text_input("Versículo Base:", placeholder="Rm 8:28")
            if st.button("Encontrar Conexões"):
                prompt = f"Aja como a Bíblia Thompson. Liste 3 versículos relacionados teologicamente a {vers} e explique a conexão."
                st.markdown(consultar_cerebro(prompt, api_key))


# === TELA 3: BIBLIOTECA & EXEGESE (O PODER DO LOGOS) ===
elif nav == "📚 Biblioteca & Exegese":
    st.header("🔬 Laboratório de Exegese")
    st.markdown("Aqui utilizamos inteligência para dissecare o texto original, similar a ferramentas avançadas.")
    
    col_input, col_res = st.columns([1, 2])
    
    with col_input:
        ref_estudo = st.text_input("Passagem para Análise:", placeholder="Ex: João 1:1, Salmos 23:4")
        st.markdown("**Nível de Análise:**")
        tipo_analise = st.radio("Profundidade:", ["Básico (Dicionário)", "Avançado (Hebraico/Grego + Análise Morfológica)", "Hermenêutico (Contexto Histórico/Cultural)"])
        
        analyze_btn = st.button("🔍 Realizar Exegese", type="primary")
        
        st.divider()
        st.caption("Dica: Use referências específicas para melhor resultado.")

    with col_res:
        if analyze_btn and ref_estudo:
            with st.container():
                st.markdown(f"### Resultado da Análise: {ref_estudo}")
                
                # Definição do Prompt complexo para simular o Logos
                prompt_exegese = ""
                if "Avançado" in tipo_analise:
                    prompt_exegese = f"""
                    Aja como um software de exegese bíblica (Bible Works/Logos). Analise o texto: {ref_estudo}.
                    
                    ESTRUTURA DE RESPOSTA OBRIGATÓRIA:
                    1. **Texto Original:** Coloque o texto em Grego (NT) ou Hebraico (AT).
                    2. **Transliteração:** Como se lê.
                    3. **Palavras-Chave (Word Study):** Selecione 2 palavras chave, dê o número de Strong, e o significado profundo (nuances, tenses verbais).
                    4. **Análise Gramatical:** Identifique tempos verbais importantes (Aoristo, Imperfeito, etc) e o que isso implica teologicamente.
                    """
                elif "Hermenêutico" in tipo_analise:
                    prompt_exegese = f"""
                    Faça uma análise histórico-cultural de: {ref_estudo}.
                    
                    1. **Quem escreveu e para quem?**
                    2. **O Cenário:** O que estava acontecendo política ou culturalmente?
                    3. **Costumes:** Existe algum costume judaico/romano no texto que não entendemos hoje?
                    4. **Aplicação Teológica:** Qual a verdade central imutável?
                    """
                else:
                    prompt_exegese = f"Explique {ref_estudo} versículo por versículo de forma didática e simples."
                
                resultado = consultar_cerebro(prompt_exegese, api_key)
                
                st.markdown("""<div style='background-color:#111; padding:20px; border-radius:10px; border:1px solid #333'>""", unsafe_allow_html=True)
                st.markdown(resultado)
                st.markdown("</div>", unsafe_allow_html=True)


# === TELA 4: MODO PÚLPITO (HOLYRICS STYLE) ===
elif nav == "🕶️ Modo Púlpito":
    # Foca na leitura sem distrações
    if not st.session_state['titulo_ativo']:
        st.warning("Abra um sermão no Studio primeiro para ativar o Modo Púlpito.")
    else:
        # Botões discretos de controle no topo
        col_c1, col_c2 = st.columns([8, 2])
        with col_c1:
            st.caption("Modo de Leitura Otimizado - Use F11 no navegador para Tela Cheia")
        with col_c2:
            font_size = st.slider("Tamanho Fonte", 18, 50, 28)

        # Conteúdo HTML puro para controle total do visual
        conteudo_html = st.session_state['texto_ativo'].replace("\n", "<br>")
        
        # Conversão simples de Markdown para HTML visual para pregação
        import markdown
        html_body = markdown.markdown(st.session_state['texto_ativo'])
        
        st.markdown(f"""
        <div style="
            background-color: black; 
            color: white; 
            padding: 50px; 
            border-radius: 15px; 
            font-family: 'Arial', sans-serif; 
            font-size: {font_size}px; 
            line-height: 1.6;
            min-height: 80vh;">
            <h1 style='color: #d4af37; border-bottom: 2px solid #333; padding-bottom:10px;'>{st.session_state['titulo_ativo']}</h1>
            <div style='margin-top:30px;'>
                {html_body}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Rodapé minimalista
st.sidebar.markdown("---")
st.sidebar.caption("O Pregador © 2024 • Powered by Streamlit & Gemini")
