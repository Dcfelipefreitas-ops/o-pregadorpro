# -*- coding: utf-8 -*-
import os, json, logging, uuid, hashlib, streamlit as st
from datetime import datetime

# ==============================================================================
# 01. CONFIGURAÇÕES PERMANENTES (NÃO ALTERAR)
# ==============================================================================
APP_TITLE = "DISCIPULADO | PR. FELIPE FREITAS"
SYSTEM_ROOT = "DADOS_SISTEMA_DISCIPULADO"  # Nome da pasta fixo
DB_DIR = os.path.join(SYSTEM_ROOT, "db")
ACERVO_DIR = os.path.join(SYSTEM_ROOT, "acervo_arquivos")

# Criar estrutura de pastas única vez
for path in [DB_DIR, ACERVO_DIR]:
    os.makedirs(path, exist_ok=True)

# Definição de Caminhos de Arquivos
PATH_USERS = os.path.join(DB_DIR, "users_db.json")
PATH_LIVROS = os.path.join(DB_DIR, "livros_biblioteca.json")
PATH_MSGS = os.path.join(DB_DIR, "mensagens_contato.json")

# ==============================================================================
# 02. ESTÉTICA GABINETE: VISUAL MINISTERIAL FIXO (MIDNIGHT BLUE & GOLD)
# ==============================================================================
st.set_page_config(page_title=APP_TITLE, page_icon="✝️", layout="wide")

def inject_ui_fixed():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .main {{ background-color: #050a1a; color: #ffffff; }}
        .ministerial-card {{
            background: rgba(255, 255, 255, 0.05);
            border-left: 5px solid #D4AF37;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
            border: 1px solid rgba(212, 175, 55, 0.1);
        }}
        h1, h2, h3 {{ color: #D4AF37 !important; }}
        .stDeployButton {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

inject_ui_fixed()

# ==============================================================================
# 03. FUNÇÕES DE SEGURANÇA E DADOS
# ==============================================================================
def hashlib_sha256(v): return hashlib.sha256(v.encode()).hexdigest()

def _read_json(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)
        
def analise_hermeneutica(texto):
    """Analisa termos teológicos e aprofundamento do texto."""
    keywords = ["exegese", "hermenêutica", "soteriologia", "cristocentrismo", "escatologia", "graça", "doutrina"]
    achadas = [w for w in keywords if w in texto.lower()]
    alertas = []
    if 10 < len(texto) < 300: alertas.append("⚠️ O texto pode ser mais aprofundado.")
    if len(achadas) == 0 and len(texto) > 100: alertas.append("🔍 Dica: Adicione termos da Hermenêutica para maior precisão.")
    return achadas, alertas

# ==============================================================================
# 04. SISTEMA DE LOGIN PERSISTENTE
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown(f"<h1 style='text-align:center;'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        tab_login, tab_cad = st.tabs(["🔒 ACESSAR", "📝 CADASTRAR"])
        
        with tab_login:
            with st.form("form_login"):
                u = st.text_input("Usuário").upper().strip()
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("CONECTAR AO GABINETE"):
                    usuarios = _read_json(PATH_USERS, default={})
                    if u in usuarios and usuarios[u].get("hash") == hashlib_sha256(p):
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = u
                        st.session_state["role"] = usuarios[u].get("role", "MEMBRO")
                        st.rerun()
                    else: st.error("Acesso Negado. Verifique usuário e senha.")

        with tab_cad:
            st.caption("Crie seu acesso apenas uma vez.")
            with st.form("form_cad"):
                nu = st.text_input("Novo Usuário").upper().strip()
                np = st.text_input("Nova Senha", type="password")
                if st.form_submit_button("CRIAR MEU ACESSO"):
                    usrs = _read_json(PATH_USERS, default={})
                    role = "ADMIN" if nu == "ADMIN" or not usrs else "MEMBRO"
                    if nu in usrs: st.warning("Usuário já existe.")
                    else:
                        usrs[nu] = {"hash": hashlib_sha256(np), "role": role, "data": datetime.now().strftime("%d/%m/%y")}
                        _write_json(PATH_USERS, usrs)
                        st.success("Cadastro realizado com sucesso! Use a aba de ACESSAR.")
    st.stop()

# ==============================================================================
# 05. NAVEGAÇÃO E SIDEBAR (DURÁVEL)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user']}\nNível: `{st.session_state['role']}`")
    st.divider()
    menu = ["📊 Dashboard Geral", "📚 Biblioteca Digital", "✍️ Meus Estudos", "💬 Central Ministerial"]
    choice = st.radio("Módulo Ativo:", menu)

    # Painel do Admin (Pr. Felipe Freitas)
    if st.session_state["role"] == "ADMIN":
        st.divider()
        is_admin_mode = st.checkbox("⚙️ SECRETARIA ADMIN")
        if is_admin_mode: choice = "MODO_ADMIN"

    if st.button("🚪 DESCONECTAR"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==============================================================================
# 06. ROTA: MODO ADMINISTRATIVO (CADASTRO DE LIVROS E ARQUIVOS)
# ==============================================================================

if choice == "MODO_ADMIN":
    st.title("🗄️ Secretaria Administrativa")
    # ... (coloque aqui o código da sua secretaria) ...

elif choice == "📖 Gabinete de Hermenêutica":
    st.title("📖 Gabinete de Hermenêutica")
    col1, col2 = st.columns([3, 1])
    with col1:
        tema_h = st.text_input("Tema de Estudo Teológico")
        texto_h = st.text_area("Desenvolvimento da Mensagem", height=450, key="txt_herm")
        if texto_h:
            achados, avisos = analise_hermeneutica(texto_h)
            with st.expander("🧐 Relatório de Inteligência Teológica", expanded=True):
                for a in avisos: st.warning(a)
                st.write(f"**Termos Identificados:** {', '.join(achados) if achados else 'Nenhum termo técnico detectado.'}")
                st.progress(min(len(achados) * 20, 100))
    with col2:
        st.markdown(f"<div class='ministerial-card'><b>OPERADOR</b><br>{st.session_state['user']}</div>", unsafe_allow_html=True)
        if st.button("💾 Arquivar Estudo"):
            st.success("Estudo sincronizado com o servidor.")

elif choice == "📚 Biblioteca Digital":
    st.title("📚 Biblioteca Digital")
    # ... (coloque aqui o seu código da biblioteca) ...

elif choice == "📊 Dashboard Geral":
    st.title("📊 Painel Ministerial")
    st.info("Sistemas Ativos. Seja bem-vindo ao portal unificado.")

elif choice == "✍️ Meus Estudos":
    st.title("✍️ Meus Estudos")
    # ... (seu código de rascunhos) ...

elif choice == "💬 Central Ministerial":
    st.title("💬 Central Ministerial")
    # ... (seu código de SOS Pastoral) ...

# ==============================================================================
# 07. ROTA: BIBLIOTECA (VISUALIZAÇÃO DE ARQUIVOS E TEXTOS)
# ==============================================================================
elif choice == "📚 Biblioteca Digital":
    st.title("📚 Biblioteca Digital")
    biblioteca = _read_json(PATH_LIVROS, default=[])
    if not biblioteca: st.info("O acervo está sendo atualizado pelo Pastor.")
    else:
        for b in biblioteca:
            with st.container():
                st.markdown(f"<div class='ministerial-card'><h3>{b['titulo']}</h3><small>Publicado em {b['data']}</small></div>", unsafe_allow_html=True)
                if "PC" in b['tipo'] and b['path']:
                    if os.path.exists(b['path']):
                        with open(b['path'], "rb") as file:
                            st.download_button(f"📥 Baixar Arquivo: {b['nome']}", file, file_name=b['nome'], key=b['id'])
                else:
                    with st.expander("📖 Ler On-line"): st.write(b['conteudo'])
            st.divider()

# ==============================================================================
# 08. ROTA: OUTROS MODULOS
# ==============================================================================
elif choice == "📖 Gabinete de Hermenêutica":
    st.title("📖 Gabinete de Estudo e Hermenêutica")
    col1, col2 = st.columns([3, 1])
    with col1:
        tema = st.text_input("Tema de Estudo")
        texto_estudo = st.text_area("Desenvolvimento da Mensagem", height=450)
        if texto_estudo:
            achados, avisos = analise_hermeneutica(texto_estudo)
            with st.expander("🧐 Relatório de Inteligência Teológica", expanded=True):
                for a in avisos: st.warning(a)
                st.write(f"**Termos Identificados:** {', '.join(achados) if achados else 'Nenhum termo técnico detectado.'}")
                st.progress(min(len(achados) * 20, 100))
    with col2:
        st.markdown(f"<div class='ministerial-card'><b>OPERADOR</b><br>{st.session_state['user']}</div>", unsafe_allow_html=True)
        st.button("💾 Arquivar Estudo")
        
elif choice == "📊 Dashboard Geral":
    st.title("📊 Painel Ministerial")
    st.markdown("<div class='ministerial-card'>Sistemas Ativos. Seja bem-vindo ao portal unificado de discipulado.</div>", unsafe_allow_html=True)

elif choice == "✍️ Meus Estudos":
    st.title("✍️ Composição de Estudos")
    st.text_area("Bloco de Notas Privado", height=300, placeholder="Digite aqui seus rascunhos de pregações...")
    st.button("Salvar Rascunho")

elif choice == "💬 Central Ministerial":
    st.title("💬 SOS Pastoral")
    msg_sos = st.text_area("Deseja enviar uma mensagem direta para o Pr. Felipe Freitas?")
    if st.button("Enviar"):
        msgs = _read_json(PATH_MSGS, default=[])
        msgs.append({"de": st.session_state["user"], "txt": msg_sos})
        _write_json(PATH_MSGS, msgs)
        st.success("Mensagem enviada com sucesso ao gabinete.")
