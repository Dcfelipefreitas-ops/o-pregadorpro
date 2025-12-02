import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. CONFIGURAÇÃO E CONSTANTES ---
st.set_page_config(page_title="O Pregador Pro", layout="wide", page_icon="✝️")

# Cores e Estilos
COR_PRINCIPAL = "#4CAF50"
COR_FUNDO_EDITOR = "#1e1e1e"

# Animações Lottie
LOTTIE_URLS = {
    "book": "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json",
    "idea": "https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json",
    "pdf": "https://lottie.host/b0429a39-a9e9-4089-8d5c-1970b551e18e/5e171b3b1f.json"
}

# Usuários (Simulação de DB)
USUARIOS = {
    "admin": "1234",
    "pr": "123"
}

# --- 2. FUNÇÕES UTILITÁRIAS ---

def load_lottieurl(url):
    try: return requests.get(url).json()
    except: return None

def consultar_gemini(prompt, chave):
    if not chave: return "⚠️ Configure sua API Key no menu lateral."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        with st.spinner("Consultando a sabedoria digital..."):
            return model.generate_content(prompt).text
    except Exception as e: return f"Erro na IA: {e}"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'O Pregador - Esboço', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_pdf(titulo, texto):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título do Sermão
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, titulo.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'L')
    pdf.ln(5)
    
    # Corpo
    pdf.set_font("Arial", size=12)
    # FPDF tem problemas com caracteres especiais diretos, encode basico
    safe_text = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ESTILIZAÇÃO CSS AVANÇADA ---
st.markdown(f"""
    <style>
    /* Esconder cabeçalho padrão */
    header {{visibility: hidden;}}
    
    /* Sidebar refinada */
    [data-testid="stSidebar"] {{
        background-color: #111;
        border-right: 1px solid #333;
    }}
    
    /* Área do Editor */
    .stTextArea textarea {{
        background-color: {COR_FUNDO_EDITOR};
        color: #ddd;
        font-family: 'Merriweather', serif; /* Fonte mais confortável para leitura */
        font-size: 18px !important;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid #444;
        padding: 20px;
    }}
    
    /* Botões personalizados */
    div.stButton > button:first-child {{
        border-radius: 6px;
        font-weight: bold;
    }}
    
    /* Card de Estatísticas */
    .metric-card {{
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {COR_PRINCIPAL};
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SISTEMA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st_lottie(load_lottieurl(LOTTIE_URLS["book"]), height=150)
        st.title("Acesso ao Púlpito")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == s:
                st.session_state['logado'] = True
                st.session_state['user'] = u
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
    st.stop()

# --- 5. LÓGICA DO APP PRINCIPAL ---

# Configuração de Pastas
USER = st.session_state['user']
PASTA_USER = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA_USER, exist_ok=True)

# Menu Lateral
with st.sidebar:
    st_lottie(load_lottieurl(LOTTIE_URLS["book"]), height=60, key="menu_anim")
    st.markdown(f"### Olá, Pastor {USER.capitalize()}")
    
    menu = st.radio("Navegação", ["🏠 Início", "✍️ Editor de Sermões", "⚙️ Configurações"])
    
    st.markdown("---")
    with st.expander("🔑 Chave Google AI (Gemini)", expanded=False):
        api_key = st.text_input("Cole aqui sua API Key", type="password")
        if not api_key:
            st.caption("Necessário para recursos de IA.")
            
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()

# --- TELA 1: INÍCIO (DASHBOARD) ---
if menu == "🏠 Início":
    st.title(f"Bem-vindo ao Estudo, {USER.capitalize()}.")
    st.markdown(f"*{datetime.now().strftime('%A, %d de %B de %Y')}*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Versículo do Dia (Gerado se tiver chave, ou estático)
        st.markdown("### 📖 Versículo Inspirador")
        if api_key:
            if 'verso_dia' not in st.session_state:
                prompt = "Gere um versículo bíblico encorajador para um pastor hoje. Apenas o texto e a referência."
                st.session_state['verso_dia'] = consultar_gemini(prompt, api_key)
            st.info(st.session_state['verso_dia'])
        else:
            st.info("💡 'Toda a Escritura é divinamente inspirada...' (2 Timóteo 3:16) - Insira sua chave API para versículos diários.")

        # Atalhos Rápidos
        st.markdown("### Acesso Rápido")
        files = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]
        if files:
            last_file = files[0] # Pega o primeiro (pode melhorar a logica de data)
            st.markdown(f"""
            <div class='metric-card'>
                <h4>📄 Último Sermão Editado</h4>
                <p>{last_file.replace('.txt','')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write("Nenhum sermão criado ainda.")

    with col2:
        st_lottie(load_lottieurl(LOTTIE_URLS["idea"]), height=200)


# --- TELA 2: EDITOR POWER ---
elif menu == "✍️ Editor de Sermões":
    
    # Seleção de Arquivo na Sidebar (para não poluir o topo)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📂 Meus Arquivos")
        arquivos = [f for f in os.listdir(PASTA_USER) if f.endswith('.txt')]
        arquivo_sel = st.selectbox("Selecione:", ["+ Novo Sermão"] + arquivos)

    # Lógica de Carregamento
    titulo_val = ""
    texto_val = ""
    
    if arquivo_sel != "+ Novo Sermão":
        titulo_val = arquivo_sel.replace(".txt", "")
        try:
            with open(os.path.join(PASTA_USER, arquivo_sel), 'r', encoding='utf-8') as f:
                texto_val = f.read()
        except: pass

    # Layout do Editor
    c_edit, c_tools = st.columns([3, 1.5])
    
    with c_edit:
        # Cabeçalho do Editor
        col_tit, col_btn = st.columns([3, 1])
        with col_tit:
            novo_titulo = st.text_input("Título da Mensagem", value=titulo_val, placeholder="Ex: O Poder da Oração")
        with col_btn:
            st.write("") # Espaçamento
            if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                if novo_titulo:
                    with open(os.path.join(PASTA_USER, f"{novo_titulo}.txt"), 'w', encoding='utf-8') as f:
                        f.write(texto_val) # Nota: aqui pegaria o estado atual, mas Streamlit requer rerun. 
                        # Ajuste fino: O st.text_area abaixo atualiza a var, mas salvar precisa estar conectado.
                    st.toast("Sermão salvo com sucesso!", icon="✅")
        
        # Ferramentas de Inserção Rápida (Toolbar)
        st.markdown("**Estrutura Rápida:**")
        b1, b2, b3, b4 = st.columns(4)
        adicionar_texto = ""
        if b1.button("📌 Intro"): adicionar_texto = "\n\n# INTRODUÇÃO\n\n"
        if b2.button("I. Tópico"): adicionar_texto = "\n\n## I. TÍTULO DO TÓPICO\nTexto...\n"
        if b3.button("⚔️ Aplicação"): adicionar_texto = "\n> APLICAÇÃO PRÁTICA:\n"
        if b4.button("🏁 Conclusão"): adicionar_texto = "\n\n# CONCLUSÃO\n\n"

        # O Editor Principal
        # Truque: Se clicou no botão, adiciona ao texto. Se não, usa o carregado.
        if adicionar_texto:
            texto_val += adicionar_texto
            
        texto_final = st.text_area("Escreva sua mensagem aqui...", value=texto_val, height=650, key="editor_area")

        # Botão de Salvar Real (para pegar o texto atualizado do text_area)
        # O botão lá em cima é visual, este aqui garante a integridade se o usuário editou.
        if novo_titulo:
            with open(os.path.join(PASTA_USER, f"{novo_titulo}.txt"), 'w', encoding='utf-8') as f:
                f.write(texto_final)

    # Ferramentas Laterais (Abas)
    with c_tools:
        st.markdown("### 🧰 Caixa de Ferramentas")
        tab1, tab2, tab3, tab4 = st.tabs(["💡 Ilustrar", "🔍 Exegese", "📰 Atualidades", "📤 Exportar"])
        
        # ABA 1: ILUSTRAÇÕES
        with tab1:
            st.caption("Gerador de Ilustrações e Histórias")
            tema_ilus = st.text_input("Sobre o que é a ilustração?", placeholder="Ex: Fé em tempos difíceis")
            tipo_ilus = st.selectbox("Tipo:", ["História Real", "Metáfora da Natureza", "Curiosidade Científica", "Biografia Cristã"])
            
            if st.button("Gerar Ilustração"):
                prompt = f"Crie uma ilustração de sermão curta e impactante do tipo '{tipo_ilus}' sobre o tema: '{tema_ilus}'. Comece direto na história."
                res = consultar_gemini(prompt, api_key)
                st.info(res)
                st.caption("Copie e cole no editor.")

        # ABA 2: EXEGESE
        with tab2:
            st.caption("Análise Profunda do Texto")
            ref_exe = st.text_input("Versículo:", placeholder="Jo 3:16")
            if st.button("Analisar Original"):
                prompt = f"Faça uma análise exegética de {ref_exe}. Palavras chaves no grego/hebraico e contexto histórico."
                st.markdown(consultar_gemini(prompt, api_key))

        # ABA 3: NOTÍCIAS (DuckDuckGo)
        with tab3:
            st.caption("Conectando com o mundo hoje")
            busca = st.text_input("Assunto atual:")
            if st.button("Buscar Notícias"):
                try:
                    res = DDGS().news(keywords=busca, region="br-pt", max_results=3)
                    if res:
                        for r in res:
                            st.markdown(f"**{r['title']}**")
                            st.caption(f"{r['source']} - [Ler]({r['url']})")
                    else:
                        st.warning("Nada encontrado.")
                except:
                    st.error("Erro na busca.")

        # ABA 4: EXPORTAR E ÁUDIO
        with tab4:
            st.caption("Levar para o Púlpito")
            
            # PDF
            if novo_titulo and texto_final:
                if st.button("📄 Gerar PDF"):
                    pdf_bytes = gerar_pdf(novo_titulo, texto_final)
                    st.download_button(
                        label="⬇️ Baixar PDF para Impressão",
                        data=pdf_bytes,
                        file_name=f"{novo_titulo}.pdf",
                        mime='application/pdf'
                    )
            else:
                st.warning("Salve um título e texto primeiro.")
            
            st.divider()
            
            # Áudio (TTS Simples)
            st.markdown("**🎧 Ouvir Esboço (Ensaio)**")
            if st.button("Ler Texto"):
                # Usando recurso nativo do Streamlit/Browser ou gTTS se instalado
                # Aqui faremos uma simulação simples de leitura via componente de áudio se gTTS estivesse aqui
                # Mas para manter simples sem gTTS, avisamos:
                st.info("Recurso de leitura em voz alta requer biblioteca 'gTTS' instalada. (Código preparado para expansão).")


# --- TELA 3: CONFIGURAÇÕES (Placeholder) ---
elif menu == "⚙️ Configurações":
    st.title("Configurações")
    st.write("Aqui você poderá alterar tamanho da fonte, temas e gerenciar backups futuramente.")
    st.info("Versão 2.0 - Build: Stable")
