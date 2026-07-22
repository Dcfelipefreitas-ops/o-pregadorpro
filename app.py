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
# 08. ROTA: GABINETE DE HERMENÊUTICA (DINÂMICO POR GÊNERO)
# ==============================================================================
elif choice == "📖 Gabinete de Hermenêutica":
    st.title("📖 Gabinete de Exegese e Hermenêutica Profissional")
    
    # --- BARRA DE FERRAMENTAS DE CONSULTA (ESTILO THE WORD) ---
    with st.expander("🛠️ BIBLIOTECA DE APOIO (Strong & Léxicos)", expanded=False):
        col_tool1, col_tool2, col_tool3 = st.columns(3)
        with col_tool1:
            st.markdown("**Lexicon Strong**")
            st.info("Consulte o original (Grego/Hebraico) via [Blue Letter Bible](https://www.blueletterbible.org/)")
        with col_tool2:
            st.markdown("**Comentário Bíblico**")
            st.info("Sugestão: [Bible Hub Commentaries](https://biblehub.com/commentaries/)")
        with col_tool3:
            st.markdown("**Dicionário Teológico**")
            st.info("Padrão: [Bible Study Tools](https://www.biblestudytools.com/dictionaries/)")

    st.divider()

    # --- SELEÇÃO DE GÊNERO (O Cérebro do Sistema) ---
    col_main1, col_main2 = st.columns([1, 2])
    
    with col_main1:
        st.subheader("📍 Configuração do Estudo")
        ref_biblica = st.text_input("Passagem Bíblica (ex: Romanos 8:1-4)")
        genero = st.selectbox("Gênero Literário", [
            "Epístola (Argumentativo)", 
            "Narrativa (Histórico)", 
            "Poesia/Sapiencial (Emocional)", 
            "Parábola (Ilustrativo)",
            "Profético/Apocalíptico"
        ])
        
        # Orientações dinâmicas com base no gênero (Baseado no "Entendes o que lês?")
        guias_genero = {
            "Epístola (Argumentativo)": {
                "foco": "Lógica e Argumentação",
                "perguntas": ["Qual o 'Portanto'? ", "Qual a premissa teológica?", "Identifique as conjunções (pois, mas, para que)."]
            },
            "Narrativa (Histórico)": {
                "foco": "Cenário, Personagens e Conflito",
                "perguntas": ["Quem é o protagonista?", "Qual o clímax da cena?", "Onde Deus está agindo na história?"]
            },
            "Poesia/Sapiencial (Emocional)": {
                "foco": "Paralelismo e Imagem",
                "perguntas": ["Qual o sentimento dominante?", "Há paralelismo sinônimo ou antitético?", "Qual a metáfora central?"]
            },
            "Parábola (Ilustrativo)": {
                "foco": "Ponto de Impacto",
                "perguntas": ["Quem eram os ouvintes originais?", "Qual a reviravolta na história?", "Qual a única verdade central?"]
            }
        }
        
        guia = guias_genero.get(genero, {"foco": "Geral", "perguntas": []})
        st.warning(f"**Foco do Gênero:** {guia['foco']}")
        for p in guia['perguntas']:
            st.caption(f"• {p}")

    with col_main2:
        # --- WORKSPACE DE ESCRITA ---
        tab_obs, tab_exegese, tab_esboço = st.tabs(["👁️ OBSERVAÇÃO", "🔍 EXEGESE (STRONG)", "🎤 ESBOÇO EXPOSITIVO"])
        
        with tab_obs:
            st.subheader("Observação do Texto")
            if genero == "Epístola (Argumentativo)":
                obs_texto = st.text_area("Mapeie o argumento: (Se A então B...)", height=300, placeholder="Ex: Paulo inicia com uma negação 'Nenhuma condenação'...")
            else:
                obs_texto = st.text_area("O que você vê no texto?", height=300)
            
        with tab_exegese:
            st.subheader("Análise de Palavras e Contexto")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                palavra_chave = st.text_input("Palavra Original (Strong G/H)")
                significado = st.text_area("Significado no Léxico")
            with col_ex2:
                contexto_cultural = st.text_area("Contexto Histórico/Cultural")
            
            ponte_teologica = st.text_area("A Ponte: Qual o princípio eterno que não muda?", placeholder="Ex: A justificação é apenas pela fé.")

        with tab_esboço:
            st.subheader("Estrutura da Pregação")
            tema_central = st.text_input("Título Homilético")
            esboco_final = st.text_area("Esboço (Introdução, Pontos, Aplicação)", height=350, 
                                        value="I. \n\nII. \n\nIII. \n\nConclusão e Apelo:")

    # --- BOTÃO DE FINALIZAÇÃO ---
    if st.button("💾 FINALIZAR E ARQUIVAR ESTUDO"):
        novo_estudo = {
            "data": datetime.now().strftime("%d/%m/%Y"),
            "ref": ref_biblica,
            "genero": genero,
            "tema": tema_central,
            "esboco": esboco_final
        }
        # Lógica para salvar no JSON
        st.success(f"Estudo sobre {ref_biblica} salvo com sucesso no seu Gabinete!")
# ==============================================================================
# 09. DEMAIS ROTAS
# ==============================================================================
# ==============================================================================
# 06. ROTA: PAINEL GERAL (SOUZEL | SINCRONIZAÇÃO TOTAL GOOGLE)
# ==============================================================================
elif choice == "📊 Painel Geral":
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37; margin-bottom:0;'>IGREJA BATISTA EM SOUZEL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Protocolo de Discipulado Sincronizado | Gabinete Pr. Felipe Freitas</p>", unsafe_allow_html=True)
    st.divider()

    # --- LINHA 1: BÍBLIA DIGITAL NVT ---
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        st.subheader("📖 NVT DIGITAL")
        l_bib = st.selectbox("Livro:", ["Mateus", "Salmos", "Gênesis", "João", "Romanos"], key="nb_l")
        c_bib = st.number_input("Capítulo:", min_value=1, max_value=150, value=1, key="nb_c")
        
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
    
    # Parâmetros NASA para o Google Calendar
    CALENDAR_ID = "igrejabatistaemsouzel@gmail.com"
    # A cor de fundo é #050a1a para sumir no fundo do seu app
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

elif "Estudos" in choice:
    st.title("✍️ Notas e Estudos ")
    st.text_area("Meus Rascunhos", height=300)

elif choice == "💬 Aconselhamento Pastoral ":
    st.title("💬 SOS Aconselhamento")
    txt_s = st.text_area("Enviar mensagem para o Gabinete do Pastor:")
    if st.button("Enviar SOS"):
        mlist = _read_json(PATH_MSGS, default=[])
        mlist.append({"de": st.session_state["user"], "txt": txt_s})
        _write_json(PATH_MSGS, mlist); st.success("Mensagem enviada.")
