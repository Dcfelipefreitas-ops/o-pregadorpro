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

# --- INSTALAÇÃO SEGURA (GARANTIA PARA NUVEM) ---
try:
    import google.generativeai as genai
except ImportError:
    # st.warning("Configurando ambiente... (Isso acontece apenas uma vez)")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
    st.rerun()

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(
    page_title="O Pregador", 
    layout="wide", 
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# Cores e Estilos (Visual mais "Premium")
COR_PRINCIPAL = "#4CAF50"
COR_FUNDO_EDITOR = "#1A1A1D" # Um tom mais profundo e agradável

st.markdown(f"""
    <style>
    /* Remover cabeçalho padrão do Streamlit */
    header {{visibility: hidden;}}
    
    /* Fundo da Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #121212;
        border-right: 1px solid #333;
    }}
    
    /* Área do Editor (Estilo Papel Escuro) */
    .stTextArea textarea {{
        background-color: {COR_FUNDO_EDITOR};
        color: #E0E0E0;
        font-family: 'Georgia', serif; /* Fonte clássica de leitura */
        font-size: 19px !important;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid #333;
        padding: 25px;
        box-shadow: inset 0 0 10px #000;
    }}
    
    /* Cartões Bonitos (Glassmorphism) */
    .metric-card {{
        background: linear-gradient(145deg, #262730, #1e1e24);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid {COR_PRINCIPAL};
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Botões */
    div.stButton > button:first-child {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURAÇÕES E CONSTANTES ---
LOTTIE_URLS = {
    "book": "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json",
    "idea": "https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json",
}

USUARIOS = {
    "admin": "1234",
    "pr": "123"
}

# --- 3. FUNÇÕES AUXILIARES ---

def load_lottieurl(url):
    try: return requests.get(url, timeout=3).json()
    except: return None

def consultar_gemini(prompt, chave):
    if not chave: return "⚠️ Para usar a IA, insira a chave no menu lateral."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        with st.spinner("Meditando na resposta..."):
            return model.generate_content(prompt).text
    except Exception as e: return f"A IA não conseguiu responder agora. (Erro: {str(e)})"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'O Pregador', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_pdf(titulo, texto):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, titulo.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    # Ajuste para evitar caracteres estranhos no PDF
    safe_text = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.write("")
        st.write("")
        anim = load_lottieurl(LOTTIE_URLS["book"])
        if anim: st_lottie(anim, height=120)
        else: st.title("✝️")
        
        st.markdown("<h2 style='text-align: center;'>O Pregador</h2>", unsafe_allow_html=True)
        
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Púlpito", type="primary", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == s:
                st.session_state['logado'] = True
                st.session_state['user'] = u
                st.rerun()
            else:
                st.error("Acesso negado.")
    st.stop()

# --- 5. APLICAÇÃO PRINCIPAL ---
USER = st.session_state['user']
PASTA_USER = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA_USER, exist_ok=True)

# BARRA LATERAL
with st.sidebar:
    anim_menu = load_lottieurl(LOTTIE_URLS["book"])
    if anim_menu: st_lottie(anim_menu, height=70, key="sidebar_anim")
    
    st.markdown(f"Olá, **{USER.capitalize()}**")
    
    # Navegação
    menu = st.radio("Ir para:", ["🏠 Início", "✍️ Editor de Sermões"], label_visibility="collapsed")
    
    st.divider()
    
    # CRONÔMETRO DE PÚLPITO (NOVIDADE)
    st.markdown("⏱️ **Cronômetro**")
    if 'inicio_crono' not in st.session_state: st.session_state['inicio_crono'] = None
    
    if st.button("Iniciar / Zerar"):
        st.session_state['inicio_crono'] = time.time()
        
    if st.session_state['inicio_crono']:
        tempo = int(time.time() - st.session_state['inicio_crono'])
        minutos = tempo // 60
        segundos = tempo % 60
        st.markdown(f"<h3 style='text-align:center; color:#4CAF50;'>{minutos:02}:{segundos:02}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; color:#555;'>00:00</h3>", unsafe_allow_html=True)
        
    st.divider()
    
    # Config API
    with st.expander("⚙️ Configurar IA"):
        api_key = st.text_input("Chave Google API", type="password")
    
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

# --- CONTEÚDO DAS PÁGINAS ---

# > TELA INICIAL
if menu == "🏠 Início":
    st.title(f"Paz seja convosco, {USER.capitalize()}.")
    st.caption(datetime.now().strftime('%d de %B de %Y'))
    
    c1, c2 = st.columns([1.8, 1])
    
    with c1:
        st.markdown("### Palavra do Dia")
        if api_key:
            if 'verso' not in st.session_state:
                st.session_state['verso'] = consultar_gemini("Dê-me um versículo curto e encorajador para hoje (Versão NVI). Sem explicações.", api_key)
            st.info(f"💡 {st.session_state['verso']}")
        else:
            st.warning("Insira sua chave da API para receber inspirações diárias.")
            
        st.markdown("---")
        st.markdown("### Seus Estudos Recentes")
        files = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]
        if files:
            for f in files[:3]:
                st.markdown(f"📄 **{f.replace('.txt', '')}**")
        else:
            st.markdown("Nenhum estudo encontrado. Que tal criar o primeiro?")

    with c2:
        try: st_lottie(load_lottieurl(LOTTIE_URLS["idea"]), height=250)
        except: pass

# > TELA EDITOR
elif menu == "✍️ Editor de Sermões":
    
    # Seletor de Arquivos
    with st.sidebar:
        st.markdown("---")
        st.caption("MEUS SERMÕES")
        files = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]
        arquivo_sel = st.selectbox("Abrir:", ["+ Novo Estudo"] + files)

    # Lógica de Carregamento (State Management)
    if 'arquivo_atual' not in st.session_state: st.session_state['arquivo_atual'] = ""
    
    if st.session_state['arquivo_atual'] != arquivo_sel:
        st.session_state['arquivo_atual'] = arquivo_sel
        if arquivo_sel != "+ Novo Estudo":
            try:
                with open(os.path.join(PASTA_USER, arquivo_sel), 'r', encoding='utf-8') as f:
                    st.session_state['texto'] = f.read()
                st.session_state['titulo'] = arquivo_sel.replace('.txt', '')
            except: pass
        else:
            st.session_state['texto'] = ""
            st.session_state['titulo'] = ""
            
    if 'texto' not in st.session_state: st.session_state['texto'] = ""
    if 'titulo' not in st.session_state: st.session_state['titulo'] = ""

    # Callbacks de Inserção
    def add_txt(t): st.session_state['texto'] += t

    # Interface Editor
    col_e, col_t = st.columns([3, 1.2])
    
    with col_e:
        st.text_input("Tema da Mensagem", key="titulo", placeholder="Título do Sermão...")
        
        # Botão de Salvar Discreto
        if st.button("Salvar Trabalho", type="primary", use_container_width=True):
            if st.session_state['titulo']:
                with open(os.path.join(PASTA_USER, f"{st.session_state['titulo']}.txt"), 'w', encoding='utf-8') as f:
                    f.write(st.session_state['texto'])
                st.toast("Estudo salvo com sucesso!", icon="🕊️")
        
        # Atalhos
        st.markdown("<small>Inserção Rápida:</small>", unsafe_allow_html=True)
        b1, b2, b3, b4 = st.columns(4)
        b1.button("📌 Intro", on_click=add_txt, args=("\n\n# INTRODUÇÃO\n",))
        b2.button("I. Tópico", on_click=add_txt, args=("\n\n## I. TÓPICO\n",))
        b3.button("⚔️ Aplicação", on_click=add_txt, args=("\n> APLICAÇÃO:\n",))
        b4.button("🏁 Fim", on_click=add_txt, args=("\n\n# CONCLUSÃO\n",))
        
        # O Editor
        st.text_area("Desenvolvimento", key="texto", height=600, label_visibility="collapsed")

    with col_t:
        st.markdown("### Auxílios")
        aba1, aba2, aba3 = st.tabs(["🎨 Ilustrar", "🔍 Pesquisa", "📄 PDF"])
        
        with aba1:
            st.caption("Gerar Ilustração com IA")
            tema = st.text_input("Tema da ilustração")
            estilo = st.selectbox("Estilo", ["História Emocionante", "Fato Científico", "Analogia", "História Bíblica"])
            if st.button("Criar"):
                resp = consultar_gemini(f"Crie uma ilustração de sermão curta ({estilo}) sobre: {tema}", api_key)
                st.info(resp)
        
        with aba2:
            st.caption("Buscar na Web")
            q = st.text_input("O que procura?")
            if st.button("Buscar"):
                try:
                    res = DDGS().news(keywords=q, region="br-pt", max_results=3)
                    for r in res:
                        st.markdown(f"• [{r['title']}]({r['url']})")
                except: st.error("Sem resultados.")
                
        with aba3:
            st.caption("Gerar Arquivo para Impressão")
            if st.button("Baixar PDF"):
                if st.session_state['titulo']:
                    data = gerar_pdf(st.session_state['titulo'], st.session_state['texto'])
                    st.download_button("Download", data, f"{st.session_state['titulo']}.pdf", "application/pdf")
                else:
                    st.warning("Dê um título antes.")
