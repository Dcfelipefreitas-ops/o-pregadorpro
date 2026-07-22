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
# 02. ESTÉTICA CELESTIAL E ESTILOS
# ==============================================================================
st.markdown("""
<style>
    /* Importação de fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600&family=Inter:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'SF Pro Display', 'Inter', sans-serif; 
        background-color: #000000; 
    }

    /* Fundo em degradê profundo estilo Apple Dark */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #000000);
    }

    /* Card Ministerial - Efeito Vidro (Glassmorphism) */
    .ministerial-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 22px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .ministerial-card:hover {
        transform: scale(1.02);
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(212, 175, 55, 0.4);
        box-shadow: 0 15px 40px rgba(212, 175, 55, 0.1);
    }

    /* Títulos em Destaque Nobre */
    h1, h2, h3 { 
        color: #D4AF37 !important; 
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* Painel de Trabalho (Gabinete) em Relevo Profundo */
    .pane {
        background: linear-gradient(145deg, #0f0f15, #050508);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 28px;
        padding: 20px;
        height: 78vh;
        overflow-y: auto;
        box-shadow: inset 4px 4px 10px rgba(0,0,0,0.8), 
                    inset -2px -2px 10px rgba(255,255,255,0.02),
                    0 10px 30px rgba(0,0,0,0.6);
    }

    /* Customização da Barra de Rolagem do Painel */
    .pane::-webkit-scrollbar { width: 6px; }
    .pane::-webkit-scrollbar-thumb { background: #D4AF37; border-radius: 10px; }

    /* Botões estilo Neumorfismo (Relevo Apple) */
    div.stButton > button {
        background: #121212;
        color: #D4AF37;
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 14px;
        padding: 12px 20px;
        font-weight: 600;
        box-shadow: 6px 6px 12px #000000, 
                   -2px -2px 8px rgba(255,255,255,0.05);
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div.stButton > button:hover {
        color: #ffffff;
        border-color: #D4AF37;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
        transform: translateY(-2px);
    }

    /* Estilo para Widgets de Entrada (Inputs) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* Esconder Elementos desnecessários do Streamlit */
    .stDeployButton, #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
# ==============================================================================
# 03. MOTORES DE LÓGICA E AUXILIARES
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
# 04. LOGIN PERSISTENTE E INICIALIZAÇÃO DE ESTADO
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "current_page" not in st.session_state: st.session_state["current_page"] = "MENU"

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
    menu = ["🏠 Início", "📊 Painel Geral", "📖 Gabinete de Hermenêutica", "📚 Biblioteca Digital", "✍️ Estudos", "🧭 Aconselhamento Pastoral", "💬 SOS Direto"]
    choice = st.radio("Escolha o Módulo:", menu)
    
    if st.session_state["role"] == "ADMIN":
        st.divider()
        if st.checkbox("⚙️ SECRETARIA ADMIN"): choice = "MODO_ADMIN"
    if st.button("SAIR"):
        st.session_state["logged_in"] = False; st.rerun()

# --- Sincronizar escolha da barra lateral com o estado da página ---
if choice == "📊 Painel Geral": st.session_state["current_page"] = "PAINEL"
elif choice == "🏠 Início": st.session_state["current_page"] = "MENU"

# ==============================================================================
# 06. ROTA: MODO ADMIN (GESTÃO DE LIVROS E MENSAGENS)
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
            f_up = st.file_uploader("Selecione o arquivo", type=["pdf","docx"]) if "PC" in fonte else None
            txt_in = st.text_area("Texto Manual") if "Manual" in fonte else ""
            if st.form_submit_button("🚀 PUBLICAR PARA TODOS"):
                bibli = _read_json(PATH_LIVROS, default=[])
                nid = str(uuid.uuid4())[:8]
                fp = os.path.join(ACERVO_DIR, f"{nid}_{f_up.name}") if f_up else ""
                if f_up:
                    with open(fp, "wb") as f: f.write(f_up.getbuffer())
                bibli.append({"id": nid, "titulo": titulo, "tipo": fonte, "path": fp, "nome": f_up.name if f_up else "", "texto": txt_in, "data": datetime.now().strftime("%d/%m/%Y")})
                _write_json(PATH_LIVROS, bibli); st.success("Livro adicionado!")
    with t3:
        m_list = _read_json(PATH_MSGS, default=[])
        for msg in reversed(m_list): st.info(f"De {msg['de']}: {msg['txt']}")

# ==============================================================================
# 07. ROTA: BIBLIOTECA DIGITAL
# ==============================================================================
elif choice == "📚 Biblioteca Digital":
    st.markdown("<h1 style='text-align:center;'>📚 Biblioteca Digital</h1>", unsafe_allow_html=True)
    
    # Criamos duas abas: O que você subiu e sugestões externas
    tab_local, tab_global = st.tabs(["📂 Meus Arquivos", "🌐 Livraria Cristã (Domínio Público)"])

    with tab_local:
        acervo = _read_json(PATH_LIVROS, default=[])
        if not acervo:
            st.info("Seu acervo pessoal está vazio. Vá em 'SECRETARIA' para subir seus arquivos PDF ou DOCX.")
        else:
            # Busca simples no acervo local
            busca = st.text_input("🔍 Pesquisar em meus livros:", placeholder="Título ou autor...")
            for b in acervo:
                if busca.lower() in b['titulo'].lower():
                    with st.container():
                        st.markdown(f"""
                            <div class='ministerial-card'>
                                <h3 style='margin:0;'>{b['titulo']}</h3>
                                <small>Postado em: {b['data']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                        if "PC" in b['tipo'] and b['path'] and os.path.exists(b['path']):
                            with open(b['path'], "rb") as f:
                                st.download_button(f"📥 Baixar Arquivo", f, file_name=b['nome'], key=f"dl_{b['id']}")
                        else:
                            with st.expander("📖 Ler On-line"):
                                st.markdown(b['texto'])

    with tab_global:
        st.markdown("### 🏛️ Clássicos de Domínio Público")
        st.caption("Acesso direto a obras fundamentais da teologia (Links externos seguros)")
        
        # Lista Curada de Grandes Obras Gratuitas (Exemplos Reais)
        biblioteca_externa = [
            {"titulo": "O Peregrino (John Bunyan)", "link": "https://www.monergismo.com/textos/literatura/o-peregrino_bunyan.pdf"},
            {"titulo": "Institutas da Religião Cristã (João Calvino)", "link": "https://www.monergismo.com/textos/livros/institutas_calvino.pdf"},
            {"titulo": "Confissões (Santo Agostinho)", "link": "https://www.monergismo.com/textos/agostinho/confissoes_agostinho.pdf"},
            {"titulo": "Sermões de C.H. Spurgeon", "link": "https://www.projetospurgeon.com.br/"},
            {"titulo": "Dicionário Bíblico Smith", "link": "https://www.biblestudytools.com/dictionaries/smiths-bible-dictionary/"}
        ]

        # Exibição em formato Apple Relevo
        cols_glob = st.columns(2)
        for i, livro in enumerate(biblioteca_externa):
            target_col = cols_glob[i % 2]
            with target_col:
                st.markdown(f"""
                    <div class='ministerial-card'>
                        <h4 style='color:#D4AF37; margin:0;'>{livro['titulo']}</h4>
                        <p style='font-size:0.8rem; color:gray;'>Fonte: Repositórios Oficiais</p>
                    </div>
                """, unsafe_allow_html=True)
                st.link_button(f"🔗 Abrir Obra Completa", livro['link'])

        st.divider()
        st.subheader("🔍 Portais Recomendados")
        st.markdown("""
        *   **[Monergismo](https://www.monergismo.com/):** Maior acervo de artigos e livros reformados em português.
        *   **[Projeto Spurgeon](https://www.projetospurgeon.com.br/):** Centenas de sermões expositivos grátis.
        *   **[CCEL](https://ccel.org/):** Biblioteca Ethereal de Clássicos Cristãos (Internacional).
        """)

# ==============================================================================
# 08. ROTA: GABINETE DE HERMENÊUTICA
# ==============================================================================
elif choice == "📖 Gabinete de Hermenêutica":
    st.title("🏛️ Gabinete de Estudo Teológico Profissional")
    arquivos_db = [f for f in os.listdir(DB_DIR) if f.endswith('.json')]
    recursos_novos = {}
    for arq in arquivos_db:
        dados = _read_json(os.path.join(DB_DIR, arq))
        if isinstance(dados, dict) and "title" in dados:
            recursos_novos[dados["title"]] = dados
    col_bib, col_tools, col_edit = st.columns([1, 1, 1.8])
    with col_bib:
        st.markdown("<div class='pane'>", unsafe_allow_html=True)
        st.subheader("📜 Bíblias e Fontes")
        tab_t, tab_rec = st.tabs(["📖 Texto", "📚 Manuscritos"])
        with tab_t:
            st.selectbox("Versão", ["NVT", "ARA", "ARC"], key="bib_sel")
            st.text_input("Referência", "Efésios 2:8", key="bib_ref")
        with tab_rec:
            if recursos_novos:
                sel_m = st.selectbox("Escolha um Material:", list(recursos_novos.keys()))
                st.write(recursos_novos[sel_m].get('description', '').replace('<br>', '\n'))
        st.markdown("</div>", unsafe_allow_html=True)
    with col_tools:
        st.markdown("<div class='pane'>", unsafe_allow_html=True)
        st.subheader("🔍 Strong & Léxicos")
        cod_s = st.text_input("Código Strong (ex: G5485)").upper()
        if cod_s == "G5485": st.success("**χάρις (charis)** - Graça")
        st.divider()
        st.text_input("Pesquisar termo no dicionário...")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_edit:
        st.subheader("✍️ Editor do Estudo Expositivo")
        manuscrito = st_quill(placeholder="Estruture sua pregação...", html=True, key="quill_h")
        if st.button("💾 ARQUIVAR ESTUDO"): st.success("Estudo arquivado!")

# ==============================================================================
# 09. ROTA: ACONSELHAMENTO PASTORAL
# ==============================================================================
elif choice == "🧭 Aconselhamento Pastoral":
    st.title("🧭 Gabinete de Cuidado Ministerial")
    db_acon = _read_json(PATH_ACONSELHAMENTO, default=[])
    if st.session_state["role"] != "ADMIN":
        meus_processos = [p for p in db_acon if p['aluno'] == st.session_state['user']]
        if not meus_processos:
            st.info("Você ainda não possui um processo iniciado.")
            with st.form("sol_acon_aluno"):
                t_escolhido = st.selectbox("Área:", ["Batismo", "Casamento", "Educação", "Crises", "Outros"])
                d_inicial = st.text_area("Descreva o que está passando:")
                if st.form_submit_button("Iniciar Processo"):
                    p_novo = {"id": str(uuid.uuid4())[:8], "aluno": st.session_state["user"], "tema": t_escolhido, "historico": [], "plano_da_semana": {"devocional": "", "leitura": "", "referencia": ""}, "status": "Em Espera", "data_abertura": datetime.now().strftime("%d/%m/%Y")}
                    db_acon.append(p_novo); _write_json(PATH_ACONSELHAMENTO, db_acon); st.rerun()
        else:
            for proc in meus_processos:
                st.markdown(f"<div class='ministerial-card'><h3>{proc['tema']}</h3><small>{proc['status']}</small></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"**Devocional:** {proc['plano_da_semana']['devocional']}")
                    st.success(f"**Leitura:** {proc['plano_da_semana']['leitura']}")
                with c2:
                    for h in reversed(proc['historico']): st.write(f"- {h['data']}: {h['nota']}")
    else:
        st.subheader("📋 Gestão Pastoral")
        alunos_p = sorted(list(set([p['aluno'] for p in db_acon])))
        if alunos_p:
            aluno_alvo = st.selectbox("Atender Aluno:", alunos_p)
            for idx, p in enumerate(db_acon):
                if p['aluno'] == aluno_alvo:
                    with st.expander(f"Caso de {p['aluno']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1: nota_p = st.text_area("Nota Prontuário", key=f"nota_{idx}")
                        with col2:
                            dev = st.text_input("Devocional", value=p['plano_da_semana']['devocional'], key=f"dev_{idx}")
                            lei = st.text_input("Leitura", value=p['plano_da_semana']['leitura'], key=f"lei_{idx}")
                        if st.button("✅ Salvar Atendimento", key=f"btn_{idx}"):
                            if nota_p: p['historico'].append({"data": datetime.now().strftime("%d/%m %H:%M"), "nota": nota_p})
                            p['plano_da_semana'] = {"devocional": dev, "leitura": lei, "referencia": ""}
                            p['status'] = "Em Acompanhamento"; _write_json(PATH_ACONSELHAMENTO, db_acon); st.rerun()

# ==============================================================================
# 10. ROTA: PAINEL GERAL (FULL SCREEN)
# ==============================================================================
elif st.session_state.get("current_page") == "PAINEL" or choice == "📊 Painel Geral":
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state["current_page"] = "MENU"
        st.rerun()

    st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-bottom:0;'>IGREJA BATISTA EM SOUZEL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Protocolo de Discipulado Sincronizado | Gabinete Pr. Felipe Freitas</p>", unsafe_allow_html=True)
    st.divider()

    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        st.subheader("📖 NVT DIGITAL")
        l_bib = st.selectbox("Livro:", ["Mateus", "Salmos", "Gênesis", "João", "Romanos"], key="nvt_l")
        c_bib = st.number_input("Capítulo:", min_value=1, max_value=150, value=1, key="nvt_c")
    with col_b2:
        st.markdown(f"<div class='ministerial-card' style='height: 200px; overflow-y: auto; padding: 25px;'><h4>{l_bib} {c_bib} (NVT)</h4><p>'Lâmpada para os meus pés é a tua palavra...'</p></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📅 Calendário de Eventos")
    google_url = "https://calendar.google.com/calendar/embed?src=igrejabatistaemsouzel@gmail.com&ctz=America%2FSao_Paulo&bgcolor=%23050a1a&color=%23D4AF37&showTitle=0"
    st.markdown(f"<iframe src='{google_url}' style='border:0' width='100%' height='550' frameborder='0'></iframe>", unsafe_allow_html=True)

    st.divider()
    st.subheader("🏛️ Celebrações de Souzel")
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1: st.markdown("<div class='ministerial-card' style='text-align:center;'><h4>QUARTA-FEIRA</h4><p style='color:#D4AF37;'>19:30</p></div>", unsafe_allow_html=True)
    with h_col2: st.markdown("<div class='ministerial-card' style='text-align:center;'><h4>SÁBADO (EBD)</h4><p style='color:#D4AF37;'>19:30</p></div>", unsafe_allow_html=True)
    with h_col3: st.markdown("<div class='ministerial-card' style='text-align:center;'><h4>DOMINGO</h4><p style='color:#D4AF37;'>19:30</p></div>", unsafe_allow_html=True)

# ==============================================================================
# 11. DEMAIS ROTAS
# ==============================================================================
elif choice == "✍️ Estudos":
    st.title("✍️ Notas e Estudos ")
    st.text_area("Meus Rascunhos", height=300)

elif choice == "💬 SOS Direto":
    st.title("💬 SOS Ministerial")
    txt_s = st.text_area("Mensagem direta ao Gabinete:")
    if st.button("Enviar SOS"):
        m_l = _read_json(PATH_MSGS, default=[])
        m_l.append({"de": st.session_state["user"], "txt": txt_s})
        _write_json(PATH_MSGS, m_l); st.success("Enviado com sucesso.")

elif choice == "🏠 Início" or st.session_state["current_page"] == "MENU":
    st.markdown("<h2 style='text-align:center;'>Bem-vindo ao Gabinete Ministerial</h2>", unsafe_allow_html=True)
    st.info("Utilize a barra lateral para navegar pelos módulos.")
