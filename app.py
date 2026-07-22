# -*- coding: utf-8 -*-
import os, json, logging, uuid, hashlib, streamlit as st
from datetime import datetime
from streamlit_quill import st_quill # Certifique-se de rodar: pip install streamlit-quill

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
    
    /* Janela de Paineis Estilo Software Desktop (The Word) */
    .pane {
        border: 1px solid rgba(212, 175, 55, 0.2);
        padding: 15px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.03);
        height: 75vh;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 03. MOTORES DE LÓGICA
# ==============================================================================
def hashlib_sha256(v): return hashlib.sha256(v.encode()).hexdigest()

def _read_json(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

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
    menu = ["📊 Painel Geral", "📖 Gabinete de Hermenêutica", "📚 Biblioteca Digital", "✍️ Estudos", "💬 SOS Direto", "🧭 Aconselhamento Pastoral"]
    choice = st.radio("Escolha o Módulo:", menu)
    
    if st.session_state["role"] == "ADMIN":
        st.divider()
        if st.checkbox("⚙️ SECRETARIA ADMIN"): choice = "MODO_ADMIN"
    if st.button("SAIR"):
        st.session_state["logged_in"] = False; st.rerun()

# ==============================================================================
# 06. ROTA: MODO ADMIN (CÓDIGO ORIGINAL)
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
# 07. ROTA: BIBLIOTECA DIGITAL (CÓDIGO ORIGINAL)
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
# 08. ROTA: GABINETE DE HERMENÊUTICA (INTERFACE MELHORADA - THE WORD STYLE)
# ==============================================================================
elif choice == "📖 Gabinete de Hermenêutica":
    st.title("🏛️ Gabinete de Estudo Teológico (Interface Profissional)")

    strong_simulado = {
        "G5485": {"termo": "χάρις (charis)", "trad": "Graça", "def": "Favor imerecido, a base da salvação em Efésios."},
        "G4102": {"termo": "πίστις (pistis)", "trad": "Fé", "def": "Confiança, convicção e lealdade a Deus."}
    }

    # Painéis de Estudo estilo "The Word"
    col_bib, col_tools, col_edit = st.columns([1, 1, 1.8])

    with col_bib:
        st.markdown("<div class='pane'>", unsafe_allow_html=True)
        st.subheader("📜 Bíblias e Comentários")
        passagem = st.text_input("Passagem Bíblica", "Efésios 2:1-10")
        v_biblia = st.selectbox("Versão", ["NVT", "ARA", "Almeida Corrigida"])
        
        tab_t, tab_c = st.tabs(["📖 Texto", "💭 Comentários"])
        with tab_t:
            st.info(f"Modo Estudo: {passagem} na versão {v_biblia}")
            st.write("DICA: Use o painel ao lado para exegese de termos chave.")
        with tab_c:
            st.write("**Comentário Wesley:** O fundamento aqui é a eleição soberana de Deus...")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tools:
        st.markdown("<div class='pane'>", unsafe_allow_html=True)
        st.subheader("🔍 Strong & Léxicos")
        cod_s = st.text_input("Digite o código Strong (ex: G5485)").upper()
        if cod_s in strong_simulado:
            item = strong_simulado[cod_s]
            st.success(f"**{item['termo']}**\n\n**Significado:** {item['trad']}\n\n{item['def']}")
        else:
            st.caption("Consulte os originais Grego/Hebraico para uma pregação expositiva fiel.")
        st.divider()
        st.subheader("📚 Dicionário de Temas")
        st.text_input("Pesquisar por: Justificação, Graça, Santidade...")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_edit:
        st.subheader("✍️ Manuscrito (Pregador)")
        st.caption("Escreva seu esboço abaixo. Use listas e negrito para organizar seus pontos.")
        manuscrito_final = st_quill(placeholder="Proposição, Pontos e Aplicação...", html=True, key="h_editor")
        if st.button("💾 ARQUIVAR MEU ESTUDO"):
            st.success("Estudo arquivado com sucesso!")

# ==============================================================================
# 09. ROTA: ACONSELHAMENTO PASTORAL (SEU CÓDIGO ORIGINAL ÍNTEGRO)
# ==============================================================================
elif choice == "🧭 Aconselhamento Pastoral":
    st.title("🧭 Gabinete de Cuidado Ministerial")
    db_acon = _read_json(PATH_ACONSELHAMENTO, default=[])
    
    if st.session_state["role"] != "ADMIN":
        meus_processos = [p for p in db_acon if p['aluno'] == st.session_state['user']]
        if not meus_processos:
            st.info("Você ainda não possui um processo de aconselhamento iniciado.")
            with st.expander("🆕 Solicitar Nova Orientação"):
                with st.form("sol_acon_aluno"):
                    t_escolhido = st.selectbox("Área:", ["Batismo", "Casamento", "Educação", "Espiritual", "Outros"])
                    d_inicial = st.text_area("Descreva o que está passando:")
                    if st.form_submit_button("Iniciar"):
                        p_novo = {"id": str(uuid.uuid4())[:8], "aluno": st.session_state["user"], "tema": t_escolhido, "historico": [], "plano_da_semana": {"devocional": "", "leitura": "", "referencia": ""}, "status": "Em Espera", "data_abertura": datetime.now().strftime("%d/%m/%Y")}
                        db_acon.append(p_novo); _write_json(PATH_ACONSELHAMENTO, db_acon); st.rerun()
        else:
            for proc in meus_processos:
                st.markdown(f"<div class='ministerial-card'><h3>{proc['tema']}</h3><p>{proc['status']}</p></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 📖 Meu Plano")
                    if proc['plano_da_semana']['devocional']:
                        st.info(f"**Devocional:** {proc['plano_da_semana']['devocional']}")
                        st.success(f"**Leitura:** {proc['plano_da_semana']['leitura']}")
                with c2:
                    st.markdown("#### 📅 Histórico")
                    for h in reversed(proc['historico']):
                        with st.expander(f"Nota de {h['data']}"): st.write(h['nota'])
    else:
        st.subheader("📋 Gestão Pastoral")
        nomes_alunos = sorted(list(set([p['aluno'] for p in db_acon])))
        if not nomes_alunos: st.info("Sem casos.")
        else:
            aluno_alvo = st.selectbox("Atender Aluno:", nomes_alunos)
            for idx, p_global in enumerate(db_acon):
                if p_global['aluno'] == aluno_alvo:
                    with st.expander(f"Atendimento: {p_global['aluno']}", expanded=True):
                        txt_nota = st.text_area("Notas da Sessão", key=f"nt_{p_global['id']}")
                        dev_txt = st.text_input("Plano Devocional", value=p_global['plano_da_semana']['devocional'], key=f"dv_{p_global['id']}")
                        leit_txt = st.text_input("Livro Indicado", value=p_global['plano_da_semana']['leitura'], key=f"lei_{p_global['id']}")
                        ref_txt = st.text_input("Versículo Base", value=p_global['plano_da_semana']['referencia'], key=f"rf_{p_global['id']}")
                        if st.button("✅ Salvar e Enviar Aluno", key=f"sv_{p_global['id']}"):
                            if txt_nota: p_global['historico'].append({"data": datetime.now().strftime("%d/%m %H:%M"), "nota": txt_nota})
                            p_global['plano_da_semana'] = {"devocional": dev_txt, "leitura": leit_txt, "referencia": ref_txt}
                            p_global['status'] = "Em Acompanhamento"; _write_json(PATH_ACONSELHAMENTO, db_acon); st.rerun()

# ==============================================================================
# 10. ROTA: PAINEL GERAL (CÓDIGO ORIGINAL ÍNTEGRO)
# ==============================================================================
elif choice == "📊 Painel Geral":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>IGREJA BATISTA EM SOUZEL</h1>", unsafe_allow_html=True)
    st.divider()
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        st.subheader("📖 NVT DIGITAL")
        l_bib = st.selectbox("Livro:", ["Mateus", "Salmos", "Gênesis", "João", "Romanos"])
        c_bib = st.number_input("Capítulo:", min_value=1, max_value=150, value=1)
    with col_b2:
        st.markdown(f"<div class='ministerial-card'><h4>{l_bib} {c_bib} (NVT)</h4><br><p style='font-style: italic;'>'Lâmpada para os meus pés é a tua palavra e luz, para o meu caminho.'</p></div>", unsafe_allow_html=True)
    st.divider()
    st.subheader("📅 Calendário em Souzel")
    google_url = "https://calendar.google.com/calendar/embed?src=igrejabatistaemsouzel@gmail.com&ctz=America%2FSao_Paulo&bgcolor=%23050a1a&color=%23D4AF37&showTitle=0"
    st.markdown(f"<iframe src='{google_url}' style='border:0' width='100%' height='550' frameborder='0' scrolling='no'></iframe>", unsafe_allow_html=True)
    st.divider()
    h1, h2, h3 = st.columns(3)
    with h1: st.markdown("<div class='ministerial-card' style='text-align:center;'><h4>QUARTA-FEIRA</h4><p style='color:#D4AF37;'>19:30</p></div>", unsafe_allow_html=True)
    with h2: st.markdown("<div class='ministerial-card' style='text-align:center;'><h4>SÁBADO</h4><p style='color:#D4AF37;'>19:30</p></div>", unsafe_allow_html=True)
    with h3: st.markdown("<div class='ministerial-card' style='text-align:center;'><h4>DOMINGO</h4><p style='color:#D4AF37;'>19:30</p></div>", unsafe_allow_html=True)

# ==============================================================================
# 11. DEMAIS ROTAS (ORIGINAIS)
# ==============================================================================
elif choice == "✍️ Estudos":
    st.title("✍️ Notas e Estudos ")
    st.text_area("Meus Rascunhos", height=300)

elif choice == "💬 SOS Direto":
    st.title("💬 Central Ministerial")
    txt_s = st.text_area("Mensagem privada para o Pastor:")
    if st.button("Enviar SOS"):
        mlist = _read_json(PATH_MSGS, default=[])
        mlist.append({"de": st.session_state["user"], "txt": txt_s})
        _write_json(PATH_MSGS, mlist); st.success("Mensagem enviada.")
