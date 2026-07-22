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
# 02. ESTÉTICA CELESTIAL E ESTILOS (CSS CORRIGIDO)
# ==============================================================================
st.set_page_config(page_title=APP_TITLE, page_icon="✝️", layout="wide")

# O erro "invalid decimal literal" foi corrigido garantindo que o CSS esteja dentro das aspas abaixo
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
    
    /* Interface estilo Software Desktop para o Gabinete */
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
# 04. LOGIN PERSISTENTE
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "current_page" not in st.session_state: 
    st.session_state["current_page"] = "MENU"

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
    menu = ["📊 Painel Geral", "📖 Gabinete de Hermenêutica", "📚 Biblioteca Digital", "✍️ Estudos", "🧭 Aconselhamento Pastoral", "💬 SOS Direto"]
    choice = st.radio("Escolha o Módulo:", menu)
    
    if st.session_state["role"] == "ADMIN":
        st.divider()
        if st.checkbox("⚙️ SECRETARIA ADMIN"): choice = "MODO_ADMIN"
    if st.button("SAIR"):
        st.session_state["logged_in"] = False; st.rerun()

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
            f_up = st.file_uploader("Selecione o arquivo (PDF/DOC)", type=["pdf","docx"]) if "PC" in fonte else None
            txt_in = st.text_area("Texto Manual") if "Manual" in fonte else ""
            if st.form_submit_button("🚀 PUBLICAR PARA TODOS"):
                bibli = _read_json(PATH_LIVROS, default=[])
                nid = str(uuid.uuid4())[:8]; fp = ""
                if f_up:
                    fp = os.path.join(ACERVO_DIR, f"{nid}_{f_up.name}")
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
    st.title("📚 Biblioteca Digital")
    acervo = _read_json(PATH_LIVROS, default=[])
    if not acervo: st.info("Nada publicado ainda.")
    else:
        for b in acervo:
            with st.container():
                st.markdown(f"<div class='ministerial-card'><h3>{b['titulo']}</h3><small>{b['data']}</small></div>", unsafe_allow_html=True)
                if "PC" in b['tipo'] and b['path'] and os.path.exists(b['path']):
                    with open(b['path'], "rb") as f:
                        st.download_button(f"📥 Baixar: {b['nome']}", f, file_name=b['nome'], key=b['id'])
                else:
                    with st.expander("📖 Ler on-line"): st.markdown(b['texto'])
                st.divider()

# ==============================================================================
# 08. ROTA: GABINETE DE HERMENÊUTICA (PAINÉIS TIPO THE WORD)
# ==============================================================================
elif choice == "📖 Gabinete de Hermenêutica":
    st.title("🏛️ Gabinete de Estudo Teológico Profissional")
    
    # Carregando arquivos históricos JSON se existirem
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
            st.info("Aqui será exibido o texto bíblico sincronizado.")
        with tab_rec:
            if recursos_novos:
                sel_m = st.selectbox("Escolha um Material:", list(recursos_novos.keys()))
                info_m = recursos_novos[sel_m]
                st.markdown(f"**Título:** {info_m.get('title_vernacular', '')}")
                st.write(info_m.get('description', '').replace('<br>', '\n'))
            else:
                st.info("Arraste seus arquivos JSON históricos para a pasta db.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tools:
        st.markdown("<div class='pane'>", unsafe_allow_html=True)
        st.subheader("🔍 Strong & Léxicos")
        cod_s = st.text_input("Código Strong (ex: G5485)").upper()
        if cod_s == "G5485": st.success("**χάρις (charis)** - Graça")
        st.divider()
        st.subheader("📚 Dicionário")
        st.text_input("Pesquisar termo...")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_edit:
        st.subheader("✍️ Editor do Estudo Expositivo")
        # Editor Rico (Negrito, Itálico, Listas, etc)
        manuscrito = st_quill(placeholder="Estruture sua pregação...", html=True, key="quill_h")
        if st.button("💾 ARQUIVAR ESTUDO"):
            st.success("Estudo arquivado com sucesso!")

# ==============================================================================
# 09. ROTA: ACONSELHAMENTO PASTORAL (ALUNO E PASTOR COMPLETOS)
# ==============================================================================
elif choice == "🧭 Aconselhamento Pastoral":
    st.title("🧭 Gabinete de Cuidado Ministerial")
    db_acon = _read_json(PATH_ACONSELHAMENTO, default=[])
    
    if st.session_state["role"] != "ADMIN":
        # --- VISÃO DO ALUNO ---
        meus_processos = [p for p in db_acon if p['aluno'] == st.session_state['user']]
        if not meus_processos:
            st.info("Você ainda não possui um processo de aconselhamento iniciado.")
            with st.expander("🆕 Solicitar Nova Orientação"):
                with st.form("sol_acon_aluno"):
                    t_escolhido = st.selectbox("Sobre qual área deseja orientação?", ["Batismo", "Casamento", "Educação", "Crises", "Outros"])
                    d_inicial = st.text_area("Descreva o que está passando:")
                    if st.form_submit_button("Iniciar Processo"):
                        p_novo = {"id": str(uuid.uuid4())[:8], "aluno": st.session_state["user"], "tema": t_escolhido, "historico": [], "plano_da_semana": {"devocional": "", "leitura": "", "referencia": ""}, "status": "Em Espera", "data_abertura": datetime.now().strftime("%d/%m/%Y")}
                        db_acon.append(p_novo); _write_json(PATH_ACONSELHAMENTO, db_acon); st.rerun()
        else:
            for proc in meus_processos:
                st.markdown(f"<div class='ministerial-card'><h3>PROCESSO: {proc['tema']}</h3><small>Início: {proc['data_abertura']} | Status: {proc['status']}</small></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 📖 Meu Plano de Estudo")
                    if proc['plano_da_semana']['devocional']:
                        st.info(f"**Devocional:** {proc['plano_da_semana']['devocional']}")
                        st.success(f"**Leitura:** {proc['plano_da_semana']['leitura']}")
                with c2:
                    st.markdown("#### 📅 Evolução")
                    for h in reversed(proc['historico']):
                        with st.expander(f"Nota de {h['data']}"): st.write(h['nota'])
    else:
        # --- VISÃO DO PASTOR (GESTOR) ---
        st.subheader("📋 Gestão de Prontuários Pastoriais")
        if not db_acon: st.info("Nenhuma solicitação ativa.")
        else:
            nomes_alunos = sorted(list(set([p['aluno'] for p in db_acon])))
            aluno_alvo = st.selectbox("Selecione o Aluno para Atender:", nomes_alunos)
            for idx, p_global in enumerate(db_acon):
                if p_global['aluno'] == aluno_alvo:
                    with st.expander(f"Atenção a: {p_global['aluno']}", expanded=True):
                        col_adm1, col_adm2 = st.columns(2)
                        with col_adm1:
                            txt_nota = st.text_area("Notas da Conversa", key=f"nt_{p_global['id']}")
                        with col_adm2:
                            dev_txt = st.text_input("Tema Devocional", value=p_global['plano_da_semana']['devocional'], key=f"dv_{p_global['id']}")
                            leit_txt = st.text_input("Indicação Leitura", value=p_global['plano_da_semana']['leitura'], key=f"lei_{p_global['id']}")
                            ref_txt = st.text_input("Referência Bíblica", value=p_global['plano_da_semana']['referencia'], key=f"rf_{p_global['id']}")
                        if st.button("✅ Atualizar e Enviar", key=f"sv_{p_global['id']}"):
                            if txt_nota: p_global['historico'].append({"data": datetime.now().strftime("%d/%m %H:%M"), "nota": txt_nota})
                            p_global['plano_da_semana'] = {"devocional": dev_txt, "leitura": leit_txt, "referencia": ref_txt}
                            p_global['status'] = "Em Acompanhamento"; _write_json(PATH_ACONSELHAMENTO, db_acon); st.rerun()

# ==============================================================================
# MÓDULO: PAINEL GERAL (RESTAURAÇÃO COMPLETA - TELA CHEIA)
# ==============================================================================
    

elif st.session_state.get("current_page") == "PAINEL" or choice == "📊 Painel Geral":
    
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state["current_page"] = "MENU"
        st.rerun()

    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>IGREJA BATISTA EM SOUZEL</h1>", unsafe_allow_html=True)
    if st.button("⬅️ VOLTAR AO MENU"):
        st.session_state["current_page"] = "MENU"
        st.rerun()

    st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-bottom:0;'>IGREJA BATISTA EM SOUZEL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Protocolo de Discipulado Sincronizado | Gabinete Pr. Felipe Freitas</p>", unsafe_allow_html=True)
    st.divider()

    # --- LINHA 1: BÍBLIA DIGITAL NVT ---
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        st.subheader("📖 NVT DIGITAL")
        l_bib = st.selectbox("Livro:", ["Mateus", "Salmos", "Gênesis", "João", "Romanos"], key="nvt_l")
        c_bib = st.number_input("Capítulo:", min_value=1, max_value=150, value=1, key="nvt_c")
        
    with col_b2:
        st.markdown(f"""
            <div class='ministerial-card' style='height: 200px; overflow-y: auto; padding: 25px;'>
                <h4 style='margin:0; color:#D4AF37;'>{l_bib} {c_bib} (NVT)</h4><br>
                <p style='font-style: italic; color:#E2E8F0; font-size:1.1rem;'>
                "Lâmpada para os meus pés é a tua palavra e luz, para o meu caminho."
                </p>
                <small style='color: gray;'>Acesse o Gabinete de Hermenêutica para análises exegéticas.</small>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- LINHA 2: AGENDA GOOGLE DA IGREJA EM SOUZEL ---
    st.subheader("📅 Calendário de Eventos em Souzel")
    
    CALENDAR_ID = "igrejabatistaemsouzel@gmail.com"
    # Ajuste de cores para o calendário sumir no fundo dark do app
    google_url = f"https://calendar.google.com/calendar/embed?src={CALENDAR_ID}&ctz=America%2FSao_Paulo&bgcolor=%23050a1a&color=%23D4AF37&showTitle=0&showNav=1&showDate=1&showPrint=0&showTabs=0&showCalendars=0&showTz=0"

    st.markdown(f"""
        <div style='border: 1px solid rgba(212,175,55,0.3); border-radius: 12px; overflow: hidden;'>
            <iframe src="{google_url}" style="border:0" width="100%" height="550" frameborder="0" scrolling="no"></iframe>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- LINHA 3: HORÁRIOS FIXOS INSTITUCIONAIS ---
    st.subheader("🏛️ Celebrações de Souzel (Horários Fixos)")
    h_col1, h_col2, h_col3 = st.columns(3)
    
    with h_col1:
        st.markdown("""
            <div class='ministerial-card' style='text-align:center;'>
                <h4 style='margin:0;'>QUARTA-FEIRA</h4>
                <p style='color:#D4AF37; font-size: 1.5rem; font-family: monospace;'>19:30</p>
                <small style='color:gray;'>ENSINO E ORAÇÃO</small>
            </div>
        """, unsafe_allow_html=True)
        
    with h_col2:
        st.markdown("""
            <div class='ministerial-card' style='text-align:center;'>
                <h4 style='margin:0;'>SÁBADO (EBD)</h4>
                <p style='color:#D4AF37; font-size: 1.5rem; font-family: monospace;'>19:30</p>
                <small style='color:gray;'>DISCIPULADO AVANÇADO</small>
            </div>
        """, unsafe_allow_html=True)
        
    with h_col3:
        st.markdown("""
            <div class='ministerial-card' style='text-align:center;'>
                <h4 style='margin:0;'>DOMINGO</h4>
                <p style='color:#D4AF37; font-size: 1.5rem; font-family: monospace;'>19:30</p>
                <small style='color:gray;'>CULTO DA FAMÍLIA</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<center style='margin-top:20px; color:#333;'><small>SYNC COMPLETED: PROTOCOL SOUZEL ACTIVE</small></center>", unsafe_allow_html=True)
# ==============================================================================
# 11. DEMAIS ROTAS (ESTUDOS E SOS)
# ==============================================================================
elif "Estudos" in choice:
    st.title("✍️ Notas e Estudos ")
    st.text_area("Meus Rascunhos", height=300)

elif choice == "💬 SOS Direto":
    st.title("💬 SOS Ministerial")
    txt_s = st.text_area("Mensagem direta ao Gabinete:")
    if st.button("Enviar"):
        m_l = _read_json(PATH_MSGS, default=[])
        m_l.append({"de": st.session_state["user"], "txt": txt_s})
        _write_json(PATH_MSGS, m_l); st.success("Enviado com sucesso.")
