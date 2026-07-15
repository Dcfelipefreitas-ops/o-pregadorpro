# -*- coding: utf-8 -*-
import os, json, logging, uuid, hashlib, streamlit as st
from datetime import datetime

# ==============================================================================
# 01. CONFIGURAÇÕES GLOBAIS E PASTAS
# ==============================================================================
APP_TITLE = "DISCIPULADO | PR. FELIPE FREITAS"
SYSTEM_ROOT = "DADOS_SISTEMA_DISCIPULADO" 
DB_DIR = os.path.join(SYSTEM_ROOT, "db")
ACERVO_DIR = os.path.join(SYSTEM_ROOT, "acervo_arquivos")

for path in [DB_DIR, ACERVO_DIR]: 
    os.makedirs(path, exist_ok=True)

PATH_USERS = os.path.join(DB_DIR, "users_db.json")
PATH_LIVROS = os.path.join(DB_DIR, "livros_biblioteca.json")
PATH_MSGS = os.path.join(DB_DIR, "mensagens_contato.json")
PATH_ACONSELHAMENTO = os.path.join(DB_DIR, "prontuarios_aconselhamento.json")

# ==============================================================================
# 02. ESTÉTICA CELESTIAL (MIDNIGHT BLUE & GOLD)
# ==============================================================================
st.set_page_config(page_title=APP_TITLE, page_icon="✝️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #050a1a; color: #ffffff; }
    .ministerial-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #D4AF37;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 20px;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 03. MOTORES DE LÓGICA E HERMENÊUTICA
# ==============================================================================
def hashlib_sha256(v): return hashlib.sha256(v.encode()).hexdigest()

def _read_json(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def analise_hermeneutica(texto):
    keywords = ["exegese", "hermenêutica", "soteriologia", "cristocentrismo", "escatologia", "graça", "doutrina"]
    achadas = [w for w in keywords if w in texto.lower()]
    alertas = []
    if texto and 10 < len(texto) < 300: alertas.append("⚠️ O conteúdo pode ser mais aprofundado.")
    if texto and not achadas and len(texto) > 100: alertas.append("🔍 Adicione termos técnicos teológicos.")
    return achadas, alertas

# ==============================================================================
# 04. LOGIN PERSISTENTE
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown(f"<h1 style='text-align:center;'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        tab_login, tab_cad = st.tabs(["🔒 ACESSAR", "📝 REGISTRAR"])
        with tab_login:
            with st.form("f_log"):
                u = st.text_input("Usuário").upper().strip()
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR"):
                    users = _read_json(PATH_USERS, default={})
                    if u in users and users[u].get("hash") == hashlib_sha256(p):
                        st.session_state.update({"logged_in":True, "user":u, "role":users[u].get("role", "MEMBRO")})
                        st.rerun()
                    else: st.error("Dados incorretos.")
        with tab_cad:
            with st.form("f_cad"):
                nu = st.text_input("Nome").upper().strip()
                np = st.text_input("Senha", type="password")
                if st.form_submit_button("CADASTRAR"):
                    usrs = _read_json(PATH_USERS, default={})
                    role = "ADMIN" if nu == "ADMIN" or not usrs else "MEMBRO"
                    if nu in usrs: st.warning("Existe.")
                    else:
                        usrs[nu] = {"hash":hashlib_sha256(np), "role":role, "data":datetime.now().strftime("%d/%m/%y")}
                        _write_json(PATH_USERS, usrs); st.success("Pronto! Vá em ACESSAR.")
    st.stop()

# ==============================================================================
# 05. BARRA LATERAL (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user']}\nNível: `{st.session_state['role']}`")
    st.divider()
    menu = ["📊 Painel Geral", "📖 Gabinete de Hermenêutica", "📚 Biblioteca Digital", "✍️ Estudos", "💬 Central Ministerial"]
    choice = st.radio("Escolha o Módulo:", menu)
    
    if st.session_state["role"] == "ADMIN":
        st.divider()
        if st.checkbox("⚙️ SECRETARIA ADMIN"): choice = "MODO_ADMIN"
    if st.button("SAIR"):
        st.session_state["logged_in"] = False; st.rerun()

# ==============================================================================
# 06. ROTA: MODO ADMIN (ENVIO DE LIVROS)
# ==============================================================================
if choice == "MODO_ADMIN":
    st.title("🗄️ Secretaria Administrativa")
    t1, t2, t3 = st.tabs(["👥 Alunos", "📤 Publicar Livro", "📬 SOS Mensagens"])
    
    with t1:
        u_list = _read_json(PATH_USERS)
        for u, d in u_list.items():
            if isinstance(d, dict): st.write(f"🔹 **{u}** | {d.get('role')} | Adesão: {d.get('data')}")
            
    with t2:
        st.subheader("Subir Livros do PC ou Criar Texto")
        with st.form("pub_form"):
            titulo = st.text_input("Título do Material")
            fonte = st.radio("Fonte", ["Importar Arquivo do PC", "Texto Manual"])
            f_up = st.file_uploader("Selecione o arquivo (PDF/DOC)", type=["pdf","docx"]) if "PC" in fonte else None
            txt_in = st.text_area("Texto Manual") if "Manual" in fonte else ""
            if st.form_submit_button("🚀 PUBLICAR PARA TODOS"):
                bibli = _read_json(PATH_LIVROS, default=[])
                nid = str(uuid.uuid4())[:8]; fp = ""
                if f_up:
                    fp = os.path.join(ACERVO_DIR, f"{nid}_{f_up.name}")
                    with open(fp, "wb") as f: f.write(f_up.getbuffer())
                bibli.append({
                    "id": nid, "titulo": titulo, "tipo": fonte, "path": fp, 
                    "nome": f_up.name if f_up else "", "texto": txt_in, "data": datetime.now().strftime("%d/%m/%Y")
                })
                _write_json(PATH_LIVROS, bibli); st.success("Livro adicionado!")

    with t3:
        m_list = _read_json(PATH_MSGS, default=[])
        for msg in reversed(m_list): st.info(f"De {msg['de']}: {msg['txt']}")

# ==============================================================================
# 07. ROTA: BIBLIOTECA DIGITAL (MEMBROS BAIXAM/LEEM)
# ==============================================================================
elif choice == "📚 Biblioteca Digital":
    st.title("📚 Biblioteca Digital")
    acervo = _read_json(PATH_LIVROS, default=[])
    if not acervo: st.info("Nada publicado ainda.")
    else:
        for b in acervo:
            with st.container():
                st.markdown(f"<div class='ministerial-card'><h3>{b['titulo']}</h3><small>{b['data']}</small></div>", unsafe_allow_html=True)
                if "PC" in b['tipo'] and b['path'] and os.path.exists(b['path']):
                    with open(b['path'], "rb") as f:
                        st.download_button(f"📥 Baixar Arquivo: {b['nome']}", f, file_name=b['nome'], key=b['id'])
                else:
                    with st.expander("📖 Ler on-line"): st.markdown(b['texto'])
                st.divider()

# ==============================================================================
# 08. ROTA: GABINETE DE HERMENÊUTICA (NOVO)
# ==============================================================================
elif choice == "📖 Gabinete de Hermenêutica":
    st.title("📖 Gabinete de Hermenêutica")
    tema_h = st.text_input("Tema Central do Estudo")
    texto_h = st.text_area("Escreva seu Manuscrito", height=450)
    if texto_h:
        achados, avisos = analise_hermeneutica(texto_h)
        with st.expander("🧐 Análise Teológica do Sistema", expanded=True):
            for a in avisos: st.warning(a)
            st.write(f"**Termos Identificados:** {', '.join(achados) if achados else 'Aguardando termos técnicos...'}")
            st.progress(min(len(achados)*20, 100))
    st.button("💾 Sincronizar Estudo")
    # ==============================================================================
# ROTA: GABINETE DE ACONSELHAMENTO (PRONTUÁRIO COMPARTILHADO)
# ==============================================================================
elif choice == "🧭 Aconselhamento Pastoral":
    st.title("🧭 Gabinete de Aconselhamento")
    
    # 1. Carrega o Banco de Prontuários
    db_acon = _read_json(PATH_ACONSELHAMENTO, default=[])
    
    if st.session_state["role"] != "ADMIN":
        # --- VISÃO DO ALUNO/MEMBRO ---
        tab_pedido, tab_meu_plano = st.tabs(["🆕 Solicitar Aconselhamento", "📝 Meu Plano de Evolução"])
        
        with tab_pedido:
            st.subheader("Iniciar Processo de Cuidado")
            with st.form("solicitar_acon"):
                tema = st.selectbox("Sobre o que deseja conversar?", ["Batismo", "Casamento", "Filhos", "Dificuldades Financeiras", "Vida Espiritual", "Outros"])
                descricao = st.text_area("Descreva brevemente sua necessidade atual:")
                if st.form_submit_button("Enviar para o Pastor"):
                    novo_caso = {
                        "id": str(uuid.uuid4())[:8],
                        "aluno": st.session_state["user"],
                        "tema": tema,
                        "descricao_inicial": descricao,
                        "status": "Em Espera",
                        "prontuario": [], # Notas que o pastor vai escrever
                        "material_leitura": "", # Indicações do pastor
                        "data_inicio": datetime.now().strftime("%d/%m/%Y")
                    }
                    db_acon.append(novo_caso)
                    _write_json(PATH_ACONSELHAMENTO, db_acon)
                    st.success("Sua solicitação foi enviada. O Pastor Freitas entrará em contato em breve.")

        with tab_meu_plano:
            meus_casos = [c for c in db_acon if c['aluno'] == st.session_state['user']]
            if not meus_casos:
                st.info("Você ainda não possui planos de aconselhamento ativos.")
            for c in meus_casos:
                with st.container():
                    st.markdown(f"<div class='ministerial-card'><h4>{c['tema']} (Iniciado em {c['data_inicio']})</h4><p>Status: {c['status']}</p></div>", unsafe_allow_html=True)
                    if c['prontuario']:
                        st.subheader("🗒️ Evolução do Aconselhamento (Notas do Pastor)")
                        for nota in c['prontuario']:
                            st.info(f"**Data: {nota['data']}**\n\n{nota['conteudo']}")
                    if c['material_leitura']:
                        st.subheader("📚 Minha Jornada de Estudo")
                        st.success(c['material_leitura'])

    else:
        # --- VISÃO DO PASTOR (ADMIN) ---
        st.subheader("Painel de Gestão de Casos")
        if not db_acon:
            st.info("Não há solicitações de aconselhamento no momento.")
        else:
            for i, c in enumerate(db_acon):
                with st.expander(f"👤 {c['aluno']} - Tema: {c['tema']} ({c['status']})"):
                    st.write(f"**Descrição Inicial:** {c['descricao_inicial']}")
                    
                    st.divider()
                    st.subheader("Adicionar Nota ao Prontuário")
                    nova_nota = st.text_area("Evolução, Devocional ou Orientação", key=f"nota_{c['id']}")
                    material = st.text_area("Referências Bíblicas e Livros Recomendados", value=c['material_leitura'], key=f"mat_{c['id']}")
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("💾 Salvar Evolução", key=f"btn_{c['id']}"):
                        if nova_nota:
                            db_acon[i]['prontuario'].append({
                                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "conteudo": nova_nota
                            })
                        db_acon[i]['material_leitura'] = material
                        db_acon[i]['status'] = "Em Processo"
                        _write_json(PATH_ACONSELHAMENTO, db_acon)
                        st.success("Prontuário atualizado. O aluno já pode visualizar o novo material.")
                        st.rerun()
                    
                    if col_b2.button("✅ Encerrar Caso", key=f"finish_{c['id']}"):
                        db_acon[i]['status'] = "Concluído"
                        _write_json(PATH_ACONSELHAMENTO, db_acon)
                        st.rerun()

# ==============================================================================
# 09. DEMAIS ROTAS
# ==============================================================================
elif choice == "📊 Painel Geral":
    st.title("📊 Painel Geral")
    st.info("Operação ministerial nominal. Bem-vindo.")

elif "Estudos" in choice:
    st.title("✍️ Notas e Estudos Privados")
    st.text_area("Meus Rascunhos", height=300)

elif choice == "💬 Aconselhamento Pastoral ":
    st.title("💬 SOS Aconselhamento")
    txt_s = st.text_area("Enviar mensagem para o Gabinete do Pastor:")
    if st.button("Enviar SOS"):
        mlist = _read_json(PATH_MSGS, default=[])
        mlist.append({"de": st.session_state["user"], "txt": txt_s})
        _write_json(PATH_MSGS, mlist); st.success("Mensagem enviada.")
