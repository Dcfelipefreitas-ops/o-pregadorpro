import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time

# --- Configuração da página ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# --- Usuários simples (substituir por DB real no futuro) ---
USUARIOS = {
    "admin": "1234",
    "pastor1": "pregar",
    "convidado": "jesus",
}

def verificar_login():
    """Mostra a tela de login e controla `st.session_state`."""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("## 🔐 Acesso Restrito")
            st.markdown("### O Pregador")
            user = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            if st.button("Entrar"):
                if user in USUARIOS and USUARIOS[user] == senha:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = user
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        return False
    return True


# Se não logado, interrompe
if not verificar_login():
    st.stop()

USUARIO_ATUAL = st.session_state['usuario_atual']


# --- Helpers ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=6)
        return r.json()
    except Exception:
        return None

anim_book = load_lottieurl("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")


def consultar_gemini(prompt, chave):
    if not chave:
        return "⚠️ Coloque a chave API no menu (Google Generative AI)."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro ao chamar a API: {e}"


def buscar_web(texto, max_results=3):
    try:
        ddgs = DDGS()
        results = ddgs.text(texto, max_results=max_results)
        if not results:
            return "Nenhum resultado encontrado."
        lines = []
        for r in results:
            title = r.get('title') or r.get('body') or '(sem título)'
            body = r.get('body') or ''
            lines.append(f"• {title}: {body}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Erro na busca web: {e}"


# --- Diretórios por usuário ---
PASTA_RAIZ = "Banco_de_Sermoes"
PASTA_USUARIO = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)
os.makedirs(PASTA_USUARIO, exist_ok=True)


# --- Estilo básico ---
st.markdown(
    """
    <style>
    .stTextArea textarea {font-family: 'Georgia', serif; font-size: 18px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Barra lateral ---
with st.sidebar:
    try:
        if anim_book:
            st_lottie(anim_book, height=70)
    except Exception:
        pass

    st.write(f"Olá, **{USUARIO_ATUAL.upper()}**")

    if st.button("Sair / Logout"):
        st.session_state['logado'] = False
        st.rerun()

    st.divider()
    with st.expander("🔐 Chave Google"):
        api_key = st.text_input("API Key", type="password")

    arquivos = [f for f in os.listdir(PASTA_USUARIO) if f.endswith('.txt')]
    arquivo_atual = st.radio("Meus Estudos:", ["+ Novo"] + arquivos)


# --- Área principal ---
col_editor, col_tools = st.columns([2.5, 1.5])

with col_editor:
    titulo_padrao = ""
    conteudo_padrao = ""
    if arquivo_atual != "+ Novo":
        titulo_padrao = arquivo_atual.replace('.txt', '')
        try:
            with open(os.path.join(PASTA_USUARIO, arquivo_atual), 'r', encoding='utf-8') as f:
                conteudo_padrao = f.read()
        except Exception:
            conteudo_padrao = ""

    novo_titulo = st.text_input("Título", value=titulo_padrao)
    texto = st.text_area("Esboço", value=conteudo_padrao, height=600)

    if st.button("💾 Salvar", type='primary'):
        if not novo_titulo:
            st.warning("Digite um título antes de salvar.")
        else:
            path = os.path.join(PASTA_USUARIO, f"{novo_titulo}.txt")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(texto)
            st.success("Salvo na sua conta!")


with col_tools:
    aba1, aba2 = st.tabs(["🔍 Web", "🤖 IA"]) 

    with aba1:
        q = st.text_input("Pesquisa:")
        if st.button("Buscar"):
            with st.spinner("Buscando na web..."):
                st.info(buscar_web(q))

    with aba2:
        if st.button("Analisar Texto"):
            prompt = f"Analise este esboço e gere sugestões práticas:\n\n{texto}"
            with st.spinner("Consultando IA..."):
                resp = consultar_gemini(prompt, api_key if 'api_key' in locals() else None)
                st.write(resp)


# Rodapé opcional
st.markdown("---")
st.caption("App local para esboços — conteúdo e integrações dependem de suas chaves e arquivos locais.")
import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time

# --- Configuração da página ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# --- Usuários simples (substituir por DB real no futuro) ---
USUARIOS = {
    "admin": "1234",
    "pastor1": "pregar",
    "convidado": "jesus",
}

def verificar_login():
    """Mostra a tela de login e controla `st.session_state`."""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("## 🔐 Acesso Restrito")
            st.markdown("### O Pregador")
            user = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            if st.button("Entrar"):
                if user in USUARIOS and USUARIOS[user] == senha:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = user
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        return False
    return True


# Se não logado, interrompe
if not verificar_login():
    st.stop()

USUARIO_ATUAL = st.session_state['usuario_atual']


# --- Helpers ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=6)
        return r.json()
    except Exception:
        return None

anim_book = load_lottieurl("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")


def consultar_gemini(prompt, chave):
    if not chave:
        return "⚠️ Coloque a chave API no menu (Google Generative AI)."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erro ao chamar a API: {e}"


def buscar_web(texto, max_results=3):
    try:
        ddgs = DDGS()
        results = ddgs.text(texto, max_results=max_results)
        if not results:
            return "Nenhum resultado encontrado."
        lines = []
        for r in results:
            title = r.get('title') or r.get('body') or '(sem título)'
            body = r.get('body') or ''
            lines.append(f"• {title}: {body}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Erro na busca web: {e}"


# --- Diretórios por usuário ---
PASTA_RAIZ = "Banco_de_Sermoes"
PASTA_USUARIO = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)
os.makedirs(PASTA_USUARIO, exist_ok=True)


# --- Estilo básico ---
st.markdown(
    """
    <style>
    .stTextArea textarea {font-family: 'Georgia', serif; font-size: 18px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Barra lateral ---
with st.sidebar:
    try:
        if anim_book:
            st_lottie(anim_book, height=70)
    except Exception:
        pass

    st.write(f"Olá, **{USUARIO_ATUAL.upper()}**")

    if st.button("Sair / Logout"):
        st.session_state['logado'] = False
        st.rerun()

    st.divider()
    with st.expander("🔐 Chave Google"):
        api_key = st.text_input("API Key", type="password")

    arquivos = [f for f in os.listdir(PASTA_USUARIO) if f.endswith('.txt')]
    arquivo_atual = st.radio("Meus Estudos:", ["+ Novo"] + arquivos)


# --- Área principal ---
col_editor, col_tools = st.columns([2.5, 1.5])

with col_editor:
    titulo_padrao = ""
    conteudo_padrao = ""
    if arquivo_atual != "+ Novo":
        titulo_padrao = arquivo_atual.replace('.txt', '')
        try:
            with open(os.path.join(PASTA_USUARIO, arquivo_atual), 'r', encoding='utf-8') as f:
                conteudo_padrao = f.read()
        except Exception:
            conteudo_padrao = ""

    novo_titulo = st.text_input("Título", value=titulo_padrao)
    texto = st.text_area("Esboço", value=conteudo_padrao, height=600)

    if st.button("💾 Salvar", type='primary'):
        if not novo_titulo:
            st.warning("Digite um título antes de salvar.")
        else:
            path = os.path.join(PASTA_USUARIO, f"{novo_titulo}.txt")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(texto)
            st.success("Salvo na sua conta!")


with col_tools:
    aba1, aba2 = st.tabs(["🔍 Web", "🤖 IA"])

    with aba1:
        q = st.text_input("Pesquisa:")
        if st.button("Buscar"):
            with st.spinner("Buscando na web..."):
                st.info(buscar_web(q))

    with aba2:
        if st.button("Analisar Texto"):
            prompt = f"Analise este esboço e gere sugestões práticas:\n\n{texto}"
            with st.spinner("Consultando IA..."):
                resp = consultar_gemini(prompt, api_key if 'api_key' in locals() else None)
                st.write(resp)


# Rodapé opcional
st.markdown("---")
st.caption("App local para esboços — conteúdo e integrações dependem de suas chaves e arquivos locais.")

import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="✝️")

# --- 2. SISTEMA DE LOGIN (SEGURANÇA) ---
# Aqui você define os usuários e senhas. 
# No futuro, isso pode vir de um banco de dados real.
USUARIOS = {
    "admin": "1234",      # Usuário mestre
    "pastor1": "pregar",  # Teste
    "convidado": "jesus"  # Teste
}

def verificar_login():
    """Cria a tela de bloqueio"""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

    if not st.session_state['logado']:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("## 🔐 Acesso Restrito")
            st.markdown("### O Pregador")
            user = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            
            if st.button("Entrar"):
                if user in USUARIOS and USUARIOS[user] == senha:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = user
                    st.rerun() # Recarrega a página
                else:
                    st.error("Usuário ou senha incorretos.")
        return False # Não deixa o resto do app rodar
    return True # Deixa rodar

# Se não estiver logado, para tudo aqui.
if not verificar_login():
    st.stop()

# --- DAQUI PRA BAIXO, SÓ RODA SE TIVER LOGADO ---

# Pega o nome do pastor logado
USUARIO_ATUAL = st.session_state['usuario_atual']

# --- 3. ANIMAÇÕES ---
def load_lottieurl(url):
    try: return requests.get(url).json()
    except: return None

anim_book = load_lottieurl("https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json")

# --- 4. SISTEMA DE ARQUIVOS (SEPARADO POR USUÁRIO) ---
# Cria uma pasta principal e uma subpasta para CADA usuário
PASTA_RAIZ = "Banco_de_Sermoes"
PASTA_USUARIO = os.path.join(PASTA_RAIZ, USUARIO_ATUAL)

if not os.path.exists(PASTA_USUARIO):
    os.makedirs(PASTA_USUARIO)

# --- 5. FUNÇÕES ---
def consultar_gemini(prompt, chave):
    if not chave: return "⚠️ Coloque a chave API no menu."
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content(prompt).text
    except Exception as e: return f"Erro: {e}"

def buscar_web(texto):
    try:
        res = DDGS().text(texto, max_results=3)
        return "\n".join([f"📎 {r.get('title','(sem título)')}: {r.get('body','')}" for r in res]) if res else "Nada."
    except: return "Erro busca."

# --- 6. INTERFACE DO APP ---

# CSS
st.markdown("""
    <style>
    .stTextArea textarea {font-family: 'Georgia', serif; font-size: 18px;}
    </style>
    """, unsafe_allow_html=True)

# BARRA LATERAL
with st.sidebar:
    try:
        st_lottie(anim_book, height=50)
    except Exception:
        pass
    st.write(f"Olá, **{USUARIO_ATUAL.upper()}**")
    
    if st.button("Sair / Logout"):
        st.session_state['logado'] = False
        st.rerun()
        
    st.divider()
    with st.expander("🔐 Chave Google"):
        api_key = st.text_input("API Key", type="password")
    
    # Lista APENAS arquivos deste usuário
    arquivos = [f for f in os.listdir(PASTA_USUARIO) if f.endswith(".txt")]
    arquivo_atual = st.radio("Meus Estudos:", ["+ Novo"] + arquivos)

# ÁREA PRINCIPAL
col_editor, col_tools = st.columns([2.5, 1.5])

with col_editor:
    titulo_padrao = ""
    conteudo_padrao = ""
    if arquivo_atual != "+ Novo":
        titulo_padrao = arquivo_atual.replace(".txt", "")
        try:
            with open(os.path.join(PASTA_USUARIO, arquivo_atual), "r", encoding="utf-8") as f: conteudo_padrao = f.read()
        except: pass

    novo_titulo = st.text_input("Título", value=titulo_padrao)
    texto = st.text_area("Esboço", value=conteudo_padrao, height=600)
    
    if st.button("💾 Salvar", type="primary"):
        if novo_titulo:
            # Salva na pasta do usuário específico
            with open(os.path.join(PASTA_USUARIO, f"{novo_titulo}.txt"), "w", encoding="utf-8") as f: f.write(texto)
            st.success("Salvo na sua conta!")

with col_tools:
    aba1, aba2 = st.tabs(["🔍 Web", "🤖 IA"])
    with aba1:
        q = st.text_input("Pesquisa:")
        if st.button("Buscar"):
            st.info(buscar_web(q))
    with aba2:
        if st.button("Analisar Texto"):
            resp = consultar_gemini(f"Analise: {texto}", api_key)
            st.write(resp)
import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import requests
from streamlit_lottie import st_lottie
import time

# --- 1. CONFIGURAÇÃO E VISUAL ---
st.set_page_config(page_title="O Pregador Pro", layout="wide", page_icon="✝️")

# Animações
LOTTIE_BOOK = "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json"
                        else:
                            st.warning("Nenhuma notícia relevante encontrada hoje.")

    st.markdown("---")
    st.subheader("📂 Meus Sermões")

    # Lista de arquivos
    arquivos = [f for f in os.listdir("estudos") if f.endswith(".txt")]
    arquivo_atual = st.radio("Selecione para editar:", ["+ Novo Estudo"] + arquivos)


# Colunas Principais: Editor (Maior) | Ferramentas (Menor)
col_editor, col_tools = st.columns([3, 1.2])


# --- ÁREA DE ESCRITA (CENTRO) ---
with col_editor:
    # Se o usuário escolheu mover o cabide para o topo do editor, renderiza aqui
    if st.session_state.get("hanger_pos", "") == "Topo do editor":
        size_map = {"Pequeno (40px)": 40, "Médio (64px)": 64, "Grande (88px)": 88}
        svg_size = size_map.get(st.session_state.get("hanger_size", "Médio (64px)"), 64)
        svg_top = f"""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
  <div style="flex:1">
    <h1 style="margin:0;">✝️ O Pregador</h1>
    <div style="color:#555; font-size:13px; margin-top:4px;">v1.0 - Modo Estudo</div>
  </div>
  <div>
    <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="width:{svg_size}px; height:{svg_size}px;" class="hanger-metal hanger-glow">
      <defs>
        import streamlit as st
        from duckduckgo_search import DDGS
        import google.generativeai as genai
        import os
        import requests
        from streamlit_lottie import st_lottie
        import time

        # --- 1. CONFIGURAÇÃO E VISUAL ---
        st.set_page_config(page_title="O Pregador Pro", layout="wide", page_icon="✝️")

        # Animações
        LOTTIE_BOOK = "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json"
        LOTTIE_NEWS = "https://lottie.host/b0429a39-a9e9-4089-8d5c-1970b551e18e/5e171b3b1f.json" 
        LOTTIE_AI = "https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json"

        def load_lottieurl(url):
            try: return requests.get(url).json()
            except: return None

        anim_book = load_lottieurl(LOTTIE_BOOK)
        anim_news = load_lottieurl(LOTTIE_NEWS)
        anim_ai = load_lottieurl(LOTTIE_AI)

        # Estilo "TheWord" Dark
        st.markdown("""
            <style>
            .block-container {padding-top: 1rem;}
            header, footer {visibility: hidden;} # type: ignore
            [data-testid="stSidebar"] {background-color: #262730; border-right: 1px solid #444;}
    
            /* Área de Texto */
            .stTextArea textarea {
                font-family: 'Georgia', serif; 
                font-size: 19px !important;
                background-color: #1a1b21; 
                color: #e0e0e0;
                border: 1px solid #333;
            }
    
            /* Caixas de Informação */
            .info-box {
                background-color: #2d2f36;
                padding: 15px;
                border-radius: 10px;
                border-left: 5px solid #4CAF50;
                margin-bottom: 10px;
            }
            </style>
            """, unsafe_allow_html=True)

        # --- 2. INTELIGÊNCIA ---
        def consultar_gemini(prompt, chave):
            if not chave: return "⚠️ Coloque a chave API no menu."
            try:
                genai.configure(api_key=chave)
                model = genai.GenerativeModel('gemini-pro')
                return model.generate_content(prompt).text
            except Exception as e: return f"Erro: {e}"

        def buscar_noticias(tema):
            """Busca notícias recentes no Brasil sobre o tema"""
            try:
                # Busca notícias no Brasil (pt-br)
                results = DDGS().news(keywords=tema, region="br-pt", max_results=3)
                if not results: return None
                return results
            except: return None

        # --- 3. INTERFACE ---
        PASTA_RAIZ = "Meus_Estudos"
        if not os.path.exists(PASTA_RAIZ): os.makedirs(PASTA_RAIZ)

        # BARRA LATERAL
        with st.sidebar:
            st_lottie(anim_book, height=60, key="logo")
            st.markdown("### O Pregador")
            with st.expander("🔐 Chave Google"):
                api_key = st.text_input("API Key", type="password")
    
            st.divider()
            arquivos = [f for f in os.listdir(PASTA_RAIZ) if f.endswith(".txt")]
            arquivo_atual = st.radio("Meus Sermões:", ["+ Novo"] + arquivos)

        # ÁREA PRINCIPAL
        col_editor, col_tools = st.columns([2.5, 1.5])

        # ESQUERDA: EDITOR
        with col_editor:
            titulo_padrao = ""
            conteudo_padrao = ""
            if arquivo_atual != "+ Novo":
                titulo_padrao = arquivo_atual.replace(".txt", "")
                try:
                    with open(os.path.join(PASTA_RAIZ, arquivo_atual), "r") as f: conteudo_padrao = f.read()
                except: pass

            novo_titulo = st.text_input("Título", value=titulo_padrao, placeholder="Título...")
            texto = st.text_area("Esboço", value=conteudo_padrao, height=700, label_visibility="collapsed")
    
            if st.button("💾 Salvar", type="primary", use_container_width=True):
                if novo_titulo:
                    with open(os.path.join(PASTA_RAIZ, f"{novo_titulo}.txt"), "w") as f: f.write(texto)
                    try:
                        st.toast("Salvo!", icon="✅")
                    except Exception:
                        st.success("Salvo!")

        # DIREITA: FERRAMENTAS AVANÇADAS
        with col_tools:
            aba_biblia, aba_contexto, aba_atual = st.tabs(["📖 Bíblia", "🏛️ Contexto", "📰 Notícias"])
    
            # --- ABA 1: BÍBLIA COMPARATIVA ---
            with aba_biblia:
                st.caption("Comparar Versões (Integrado)")
                ref = st.text_input("Referência (ex: Romanos 12:2)")
                col_v1, col_v2 = st.columns(2)
                v1 = col_v1.selectbox("Ver. 1", ["Almeida (ARC)", "NVI", "King James"])
                v2 = col_v2.selectbox("Ver. 2", ["Linguagem de Hoje", "Grego/Hebraico", "A Mensagem"])
        
                if st.button("Comparar Textos"):
                    with st.status("Buscando textos...", expanded=True):
                        prompt = f"""
                        Aja como uma Bíblia Digital.
                        Traga o texto de: {ref}.
                
                        FORMATO DE RESPOSTA (Use Markdown):
                        ### {v1}
                        (Texto fiel na versão {v1})
                
                        ### {v2}
                        (Texto fiel na versão {v2})
                
                        Destaque em negrito as principais diferenças de palavras entre as duas.
                        """
                        resp = consultar_gemini(prompt, api_key)
                        st.markdown(resp)

            import streamlit as st
            from duckduckgo_search import DDGS
            import google.generativeai as genai
            import os
            import requests
            from streamlit_lottie import st_lottie
            import time

            # --- 1. CONFIGURAÇÃO E VISUAL ---
            st.set_page_config(page_title="O Pregador Pro", layout="wide", page_icon="✝️")

            # Animações
            LOTTIE_BOOK = "https://lottie.host/5a666e37-d2c4-4a47-98d9-247544062a4d/lB6y7y6a1W.json"
            LOTTIE_NEWS = "https://lottie.host/b0429a39-a9e9-4089-8d5c-1970b551e18e/5e171b3b1f.json" 
            LOTTIE_AI = "https://lottie.host/93310461-1250-482f-87d9-482a46696d5b/6u0v8v5j2a.json"

            def load_lottieurl(url):
                try: return requests.get(url).json()
                except: return None

            anim_book = load_lottieurl(LOTTIE_BOOK)
            anim_news = load_lottieurl(LOTTIE_NEWS)
            anim_ai = load_lottieurl(LOTTIE_AI)

            # Estilo "TheWord" Dark
            st.markdown("""
                <style>
                .block-container {padding-top: 1rem;}
                header, footer {visibility: hidden;}
                [data-testid="stSidebar"] {background-color: #262730; border-right: 1px solid #444;}
    
                /* Área de Texto */
                .stTextArea textarea {
                    font-family: 'Georgia', serif; 
                    font-size: 19px !important;
                    background-color: #1a1b21; 
                    color: #e0e0e0;
                    border: 1px solid #333;
                }
    
                /* Caixas de Informação */
                .info-box {
                    background-color: #2d2f36;
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 5px solid #4CAF50;
                    margin-bottom: 10px;
                }
                </style>
                """, unsafe_allow_html=True)

            # --- 2. INTELIGÊNCIA ---
            def consultar_gemini(prompt, chave):
                if not chave: return "⚠️ Coloque a chave API no menu."
                try:
                    genai.configure(api_key=chave)
                    model = genai.GenerativeModel('gemini-pro')
                    return model.generate_content(prompt).text
                except Exception as e: return f"Erro: {e}"

            def buscar_noticias(tema):
                """Busca notícias recentes no Brasil sobre o tema"""
                try:
                    # Busca notícias no Brasil (pt-br)
                    results = DDGS().news(keywords=tema, region="br-pt", max_results=3)
                    if not results: return None
                    return results
                except: return None

            # --- 3. INTERFACE ---
            PASTA_RAIZ = "Meus_Estudos"
            if not os.path.exists(PASTA_RAIZ): os.makedirs(PASTA_RAIZ)

            # BARRA LATERAL
            with st.sidebar:
                st_lottie(anim_book, height=60, key="logo")
                st.markdown("### O Pregador")
                with st.expander("🔐 Chave Google"):
                    api_key = st.text_input("API Key", type="password")
    
                st.divider()
                arquivos = [f for f in os.listdir(PASTA_RAIZ) if f.endswith(".txt")]
                arquivo_atual = st.radio("Meus Sermões:", ["+ Novo"] + arquivos)

            # ÁREA PRINCIPAL
            col_editor, col_tools = st.columns([2.5, 1.5])

            # ESQUERDA: EDITOR
            with col_editor:
                titulo_padrao = ""
                conteudo_padrao = ""
                if arquivo_atual != "+ Novo":
                    titulo_padrao = arquivo_atual.replace(".txt", "")
                    try:
                        with open(os.path.join(PASTA_RAIZ, arquivo_atual), "r") as f: conteudo_padrao = f.read()
                    except: pass

                novo_titulo = st.text_input("Título", value=titulo_padrao, placeholder="Título...")
                texto = st.text_area("Esboço", value=conteudo_padrao, height=700, label_visibility="collapsed")
    
                if st.button("💾 Salvar", type="primary", use_container_width=True):
                    if novo_titulo:
                        with open(os.path.join(PASTA_RAIZ, f"{novo_titulo}.txt"), "w") as f: f.write(texto)
                        try:
                            st.toast("Salvo!", icon="✅")
                        except Exception:
                            st.success("Salvo!")

            # DIREITA: FERRAMENTAS AVANÇADAS
            with col_tools:
                aba_biblia, aba_contexto, aba_atual = st.tabs(["📖 Bíblia", "🏛️ Contexto", "📰 Notícias"])
    
                # --- ABA 1: BÍBLIA COMPARATIVA ---
                with aba_biblia:
                    st.caption("Comparar Versões (Integrado)")
                    ref = st.text_input("Referência (ex: Romanos 12:2)")
                    col_v1, col_v2 = st.columns(2)
                    v1 = col_v1.selectbox("Ver. 1", ["Almeida (ARC)", "NVI", "King James"])
                    v2 = col_v2.selectbox("Ver. 2", ["Linguagem de Hoje", "Grego/Hebraico", "A Mensagem"])
        
                    if st.button("Comparar Textos"):
                        with st.status("Buscando textos...", expanded=True):
                            prompt = f"""
                            Aja como uma Bíblia Digital.
                            Traga o texto de: {ref}.
                
                            FORMATO DE RESPOSTA (Use Markdown):
                            ### {v1}
                            (Texto fiel na versão {v1})
                
                            ### {v2}
                            (Texto fiel na versão {v2})
                
                            Destaque em negrito as principais diferenças de palavras entre as duas.
                            """
                            resp = consultar_gemini(prompt, api_key)
                            st.markdown(resp)

                # --- ABA 2: RAIO-X DO TEXTO (HISTÓRIA) ---
                with aba_contexto:
                    st.caption("Contexto Histórico e Original")
                    st.info("O App vai analisar o versículo ou seu esboço.")
        
                    if st.button("🔎 Analisar Profundamente"):
                        if not api_key: st.error("Precisa da Chave Google.")
                        else:
                            with st.status("Consultando enciclopédias...", expanded=True):
                                try:
                                    st_lottie(anim_ai, height=80)
                                except: pass
                                prompt_historia = f"""
                                Faça uma análise exegética e histórica de: {ref if ref else "deste esboço: " + texto[:200]}.
                    
                                TÓPICOS OBRIGATÓRIOS:
                                1. 🏛️ **Contexto Histórico:** Quem escreveu, para quem e o que estava acontecendo na época?
                                2. 🔑 **Palavras-Chave:** Analise 2 palavras fortes no original (Grego ou Hebraico) e seu significado.
                                3. 💡 **Curiosidade:** Um fato cultural da época que muda o entendimento.
                                """
                                analise = consultar_gemini(prompt_historia, api_key)
                                st.markdown(analise)

                # --- ABA 3: NOTÍCIAS E ATUALIDADES ---
                with aba_atual:
                    st.caption("Conectar com o Hoje")
                    st.write("Encontra fatos atuais que combinam com sua mensagem.")
        
                    tema_busca = st.text_input("Qual o tema central?", placeholder="Ex: Corrupção, Ansiedade, Guerra")
        
                    if st.button("Buscar Notícias Atuais"):
                        if not tema_busca: st.warning("Digite um tema acima.")
                        else:
                            # 1. Busca no DuckDuckGo
                            with st.status("Lendo jornais...", expanded=True):
                                try:
                                    st_lottie(anim_news, height=80)
                                except: pass
                                noticias = buscar_noticias(tema_busca)
                    
                                if noticias:
                                    st.success("Notícias encontradas!")
                                    texto_noticias = ""
                                    for n in noticias:
                                        st.markdown(f"""
                                        <div class="info-box">
                                            <b>📰 {n['title']}</b><br>
                                            <span style="font-size:12px">{n.get('date','')} - {n.get('source','')}</span><br>
                                            <a href="{n.get('url','')}" target="_blank">Ler notícia original</a>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        texto_noticias += f"- {n.get('title','(sem título)')} ({n.get('source','')})\n"
                        
                                    # 2. IA Faz a Ponte
                                    st.write("---")
                                    st.write("🤖 **Sugestão do Pregador:**")
                                    ponte = consultar_gemini(f"""
                                    Tenho um sermão sobre '{tema_busca}'.
                                    Aqui estão notícias de hoje:
                                    {texto_noticias}
                        
                                    Como posso usar uma dessas notícias para introduzir ou ilustrar meu sermão?
                                    Crie uma 'Ponte de Ligação' curta e impactante.
                                    """, api_key)
                                    st.write(ponte)
                                else:
                                    st.warning("Nenhuma notícia relevante encontrada hoje.")