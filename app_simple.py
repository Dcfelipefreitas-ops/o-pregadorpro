import streamlit as st
import os

# imports opcionais
try:
    from duckduckgo_search import DDGS
except Exception:
    DDGS = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

# --- 1. CONFIGURAÇÃO VISUAL (ESTILO DESKTOP/THEWORD) ---
st.set_page_config(page_title="O Pregador - Simples", layout="wide", page_icon="✝️")

# CSS simples
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {background-color: #2b2b2b; border-right: 1px solid #444;}
    .stTextArea textarea {font-family: 'Georgia', serif; font-size: 18px !important; line-height: 1.6 !important; background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #444;}
    .stButton button {border-radius: 4px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# Pastas
PASTA_RAIZ = "Meus_Estudos"
CATEGORIAS = ["01. Rascunhos", "02. Antigo Testamento", "03. Novo Testamento", "04. Séries e Temas"]

os.makedirs(PASTA_RAIZ, exist_ok=True)
for cat in CATEGORIAS:
    os.makedirs(os.path.join(PASTA_RAIZ, cat), exist_ok=True)

# funções simples

def consultar_gemini(prompt, chave, contexto):
    if not chave:
        return "⚠️ Configure a Chave API no menu lateral."
    if genai is None:
        return "⚠️ Biblioteca `google.generativeai` não está instalada."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(f"Contexto: {contexto}\n\nPedido: {prompt}").text
    except Exception as e:
        return f"Erro: {e}"


def busca_web(termo):
    if DDGS is None:
        return "DuckDuckGo search library not available. Instale `duckduckgo_search`."
    try:
        res = DDGS().text(termo, max_results=3)
        return "\n".join([f"📎 {r.get('title','(sem título)')}: {r.get('body','')}" for r in res]) if res else "Nada achado."
    except Exception:
        return "Erro na busca."

# Interface
with st.sidebar:
    st.markdown("### ✝️ O Pregador - Simples")
    with st.expander("⚙️ Configurar Chave Google"):
        api_key = st.text_input("API Key", type="password")
    st.markdown("---")
    st.caption("BIBLIOTECA (Árvore)")
    pasta_selecionada = st.selectbox("📂 Pasta:", CATEGORIAS)
    caminho_pasta = os.path.join(PASTA_RAIZ, pasta_selecionada)
    arquivos = [f for f in os.listdir(caminho_pasta) if f.endswith(".txt")]
    arquivo_atual = st.radio("📄 Sermões:", ["+ Criar Novo"] + arquivos)
    st.markdown("---")
    st.info(f"Total na pasta: {len(arquivos)}")

col_editor, col_tools = st.columns([3, 1.2])

with col_editor:
    titulo_padrao = ""
    conteudo_padrao = ""
    if arquivo_atual != "+ Criar Novo":
        titulo_padrao = arquivo_atual.replace('.txt','')
        path_atual = os.path.join(caminho_pasta, arquivo_atual)
        try:
            with open(path_atual, 'r', encoding='utf-8') as f:
                conteudo_padrao = f.read()
        except Exception:
            conteudo_padrao = ''

    c1, c2 = st.columns([3,1])
    with c1:
        novo_titulo = st.text_input("Título da Mensagem", value=titulo_padrao, placeholder="Ex: O Poder da Oração")
    with c2:
        st.write("")
        st.write("")
        if st.button("💾 GRAVAR", type='primary'):
            if novo_titulo:
                caminho_final = os.path.join(caminho_pasta, f"{novo_titulo}.txt")
                texto_salvar = st.session_state.get('editor_text', conteudo_padrao)
                try:
                    with open(caminho_final, 'w', encoding='utf-8') as f:
                        f.write(texto_salvar)
                    st.success(f"Salvo em: {pasta_selecionada} ✅")
                except Exception as e:
                    st.error(f"Falha ao salvar: {e}")

    texto = st.text_area("Papel de Rascunho", value=conteudo_padrao, height=700, key='editor_text')
    if novo_titulo and texto != conteudo_padrao:
        caminho_final = os.path.join(caminho_pasta, f"{novo_titulo}.txt")
        with open(caminho_final, 'w', encoding='utf-8') as f:
            f.write(texto)

with col_tools:
    st.markdown("### Ferramentas")
    aba_busca, aba_ia, aba_biblia = st.tabs(["🔍", "🤖", "📖"])

    with aba_busca:
        st.caption("Pesquisa Web")
        q = st.text_input("Termo:")
        if st.button("Buscar"):
            res = busca_web(q)
            st.info(res)
            st.session_state['cache'] = res

    with aba_ia:
        st.caption("Assistente Inteligente")
        modo = st.selectbox("Modo:", ["Sugerir Esboço", "Exegese do Texto", "Ilustrar"])
        if st.button("Processar IA"):
            ctx = st.session_state.get('cache','')
            prompt = f"Modo: {modo}. Texto do pregador: {st.session_state.get('editor_text','')}"
            resp = consultar_gemini(prompt, api_key, ctx)
            st.write(resp)

    with aba_biblia:
        st.caption("Bíblia Online")
        livro = st.text_input("Ref (ex: Sl 23)")
        if livro:
            st.markdown(f"[Abrir {livro}](https://www.bibliaonline.com.br/acf/busca?q={livro})")
