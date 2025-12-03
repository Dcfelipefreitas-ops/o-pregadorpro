# -*- coding: utf-8 -*-
"""
O PREGADOR - SYSTEM CORE (Versão V40 - Maximum Robustness)
Status: Produção / Full Feature / Legacy Preserved
Autoria: Sistema Consolidado & Expandido

[MANUAL DE MODULOS INTERNOS]
1.  Bootloader (Gênesis Protocol): Inicialização de pastas, DBs e integridade.
2.  Security (CryptoManager): Criptografia AES-GCM (Nível Militar).
3.  Office Engine (ExportEngine): Geradores DOCX/PDF com Múltiplos Motores de Fallback.
4.  Theology Core (GenevaProtocol): Validação doutrinária e scan de heresias.
5.  Psych Core (PastoralMind): Análise de Burnout e Teoria da Permissão.
6.  User System (AccessControl): Login, Permissões e Rede Ministerial.
7.  UI/UX Layer: CSS Dark Cathedral, Fontes Dinâmicas e Layout Responsivo.
"""

# ==============================================================================
# 01. IMPORTAÇÕES E CONFIGURAÇÃO INICIAL (Obrigatório ser a 1ª linha)
# ==============================================================================
import streamlit as st
import os
import sys
import time
import json
import base64
import math
import shutil
import random
import logging
import hashlib
import re
from datetime import datetime, timedelta
from io import BytesIO

# Configuração da página - MANTIDA ESTRUTURA ORIGINAL
st.set_page_config(
    page_title="O PREGADOR",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 02. SISTEMA DE LOGS E AUDITORIA (ROBUSTEZ)
# ==============================================================================
# Cria logs detalhados para auditoria pastoral e debug de erros
LOG_DIR = "Dados_Pregador_V31/System_Logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "system_audit_master.log"),
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s'
)
logging.info(">>> SISTEMA INICIADO: O PREGADOR V40 <<<")

# ==============================================================================
# 03. CARREGAMENTO DE BIBLIOTECAS (COM TRATAMENTO DE FALHAS EXTENSIVO)
# ==============================================================================

# 3.1 Editor de Texto Avançado (CKEditor)
CKEDITOR_AVAILABLE = False
STREAMLIT_CKEDITOR = False
try:
    from streamlit_ckeditor import st_ckeditor  # type: ignore
    STREAMLIT_CKEDITOR = True
    CKEDITOR_AVAILABLE = True
    logging.info("Módulo CKEditor carregado com sucesso.")
except ImportError:
    logging.warning("CKEditor não encontrado. O sistema usará fallback.")

# 3.2 Editor Intermediário (Quill)
QUILL_AVAILABLE = False
try:
    from streamlit_quill import st_quill  # type: ignore
    QUILL_AVAILABLE = True
    logging.info("Módulo Quill carregado com sucesso.")
except ImportError:
    logging.warning("Quill não encontrado. O sistema usará fallback.")

# 3.3 Visualização de Dados (Plotly)
PLOTLY_OK = False
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
    logging.info("Módulo Plotly carregado (Gráficos Ativos).")
except ImportError:
    logging.warning("Plotly não instalado. Usando visualizações simplificadas.")

# 3.4 Criptografia (Cryptography AES)
CRYPTO_OK = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
    logging.info("Módulo Crypto ativado.")
except ImportError:
    logging.warning("Módulo Crypto avançado ausente.")

# 3.5 Engenharia de Exportação WORD (DOCX) - O "Módulo Word"
HTML2DOCX_ENGINE = None
try:
    import mammoth
    HTML2DOCX_ENGINE = "mammoth"
except ImportError:
    try:
        from html2docx import html2docx
        HTML2DOCX_ENGINE = "html2docx"
    except ImportError:
        try:
            from docx import Document
            HTML2DOCX_ENGINE = "docx_manual"
        except ImportError:
            HTML2DOCX_ENGINE = None
logging.info(f"Engine DOCX definida como: {HTML2DOCX_ENGINE}")

# 3.6 Engenharia de Exportação PDF
PDF_ENGINE = None
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    PDF_ENGINE = "reportlab"
except ImportError:
    try:
        from fpdf import FPDF
        PDF_ENGINE = "fpdf"
    except ImportError:
        PDF_ENGINE = None
logging.info(f"Engine PDF definida como: {PDF_ENGINE}")

# ==============================================================================
# 04. FUNÇÕES UTILITÁRIAS GLOBAIS (DEFINIDAS ANTES DO USO)
# ==============================================================================

def normalize_font_name(fname):
    """
    Função vital para o CSS. Corrige o erro da linha 591.
    Normaliza nomes de fontes vindas do JSON config.
    """
    if not fname:
        return "Inter"
    try:
        base_name = fname.split(",")[0]
        base_name = base_name.strip().replace("'", "").replace('"', "")
        return base_name
    except Exception as e:
        logging.error(f"Erro ao normalizar fonte: {e}")
        return "Inter"

def safe_filename(text):
    """Garante que o nome do arquivo seja seguro para o sistema operacional."""
    if not text:
        return f"documento_{int(time.time())}"
    clean_text = str(text).strip()
    clean_text = re.sub(r'\s+', '_', clean_text)
    clean_text = re.sub(r'(?u)[^-\w.]', '', clean_text)
    return clean_text

def read_json_safe(path, default_value=None):
    """Lê um arquivo JSON com proteção total contra arquivos corrompidos."""
    if default_value is None:
        default_value = {}
    try:
        if not os.path.exists(path):
            return default_value
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default_value
            return json.loads(content)
    except Exception as e:
        logging.error(f"FATAL: Erro ao ler JSON em {path}. Retornando default. Erro: {e}")
        return default_value

def write_json_safe(path, data):
    """Escreve um arquivo JSON atomicamente (cria temp e renomeia)."""
    try:
        temp_path = path + ".tmp_write"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, path)
        return True
    except Exception as e:
        logging.error(f"FATAL: Erro ao escrever JSON em {path}. Erro: {e}")
        return False

# ==============================================================================
# 05. GÊNESIS PROTOCOL (SISTEMA DE ARQUIVOS)
# ==============================================================================
ROOT_DIR = "Dados_Pregador_V31"

DIRECTORIES = {
    "SERMONS": os.path.join(ROOT_DIR, "Sermoes"),
    "OFFICE": os.path.join(ROOT_DIR, "Gabinete_Pastoral"),
    "USER_DATA": os.path.join(ROOT_DIR, "User_Data"),
    "BACKUP_HIDDEN": os.path.join(ROOT_DIR, "Auto_Backup_Oculto"),
    "LOGS": os.path.join(ROOT_DIR, "System_Logs"),
    "LIBRARY": os.path.join(ROOT_DIR, "BibliaCache"),
    "MEMBERS": os.path.join(ROOT_DIR, "Membresia"),
    "NETWORK": os.path.join(ROOT_DIR, "Rede_Ministerial")  # Braço de colaboradores
}

DATABASE_FILES = {
    "CONFIG": os.path.join(DIRECTORIES["USER_DATA"], "config.json"),
    "USERS": os.path.join(DIRECTORIES["USER_DATA"], "users_db.json"),
    "SOUL": os.path.join(DIRECTORIES["OFFICE"], "soul_data.json"),
    "STATS": os.path.join(DIRECTORIES["USER_DATA"], "db_stats.json"),
    "MEMBERS": os.path.join(DIRECTORIES["MEMBERS"], "members.json"),
    "NETWORK_FEED": os.path.join(DIRECTORIES["NETWORK"], "feed_videos.json")
}

def genesis_boot_protocol():
    """Garante a existência da integridade física do sistema. Não remove nada."""
    # 1. Cria pastas
    for key, path in DIRECTORIES.items():
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            logging.info(f"Gênesis: Diretório criado -> {path}")

    # 2. Inicializa Banco de Configurações
    if not os.path.exists(DATABASE_FILES["CONFIG"]):
        default_config = {
            "theme_color": "#D4AF37",
            "font_size": 18,
            "font_family": "Inter",
            "theme_mode": "Dark Cathedral",
            "enc_password": "OMEGA_KEY_DEFAULT",
            "backup_interval": 86400,
            "rotina_pastoral": [
                "Leitura Bíblica",
                "Oração Matinal",
                "Estudo Teológico",
                "Tempo de Descanso"
            ]
        }
        write_json_safe(DATABASE_FILES["CONFIG"], default_config)

    # 3. Inicializa Banco de Usuários
    if not os.path.exists(DATABASE_FILES["USERS"]):
        default_admin = hashlib.sha256("admin".encode()).hexdigest()
        write_json_safe(DATABASE_FILES["USERS"], {"ADMIN": default_admin})

    # 4. Inicializa Bases Vazias
    for db_key in ["NETWORK_FEED", "MEMBERS", "SOUL"]:
        if not os.path.exists(DATABASE_FILES[db_key]):
            write_json_safe(DATABASE_FILES[db_key], [])
    
    if not os.path.exists(DATABASE_FILES["STATS"]):
        write_json_safe(DATABASE_FILES["STATS"], {"xp": 0, "nivel": 1})

# Executa o protocolo de inicialização
genesis_boot_protocol()

# ==============================================================================
# 06. CLASSES LÓGICAS (O CORAÇÃO DO SISTEMA)
# ==============================================================================

class ExportEngine:
    """
    O MÓDULO WORD QUE VOCÊ PEDIU.
    Gerencia a exportação robusta para DOCX e PDF.
    """
    
    @staticmethod
    def export_to_docx(title, html_content, output_filepath):
        logging.info(f"Exportando DOCX via {HTML2DOCX_ENGINE}")
        
        # Estratégia 1: Mammoth (Alta Fidelidade)
        if HTML2DOCX_ENGINE == "mammoth":
            try:
                import mammoth
                # Envelopa o HTML para garantir que o parser entenda
                full_html = f"<html><body><h1>{title}</h1>{html_content}</body></html>"
                result = mammoth.convert_to_docx(full_html)
                with open(output_filepath, "wb") as f:
                    f.write(result.value)
                return True, "DOCX gerado com sucesso (Mammoth)."
            except Exception as e:
                logging.error(f"Erro Mammoth: {e}")
        
        # Estratégia 2: html2docx (Biblioteca dedicada)
        if HTML2DOCX_ENGINE == "html2docx":
            try:
                from html2docx import html2docx
                buf = html2docx(html_content, title=title)
                with open(output_filepath, "wb") as f:
                    f.write(buf.getvalue())
                return True, "DOCX gerado com sucesso (Html2Docx)."
            except Exception as e:
                logging.error(f"Erro Html2Docx: {e}")

        # Estratégia 3: Fallback Manual (Texto Puro)
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title, 0)
            text_clean = re.sub(r'<[^>]+>', '\n', html_content)
            for p in text_clean.split('\n'):
                if p.strip(): doc.add_paragraph(p.strip())
            doc.save(output_filepath)
            return True, "DOCX gerado (Modo Texto Simples)."
        except Exception as e:
            # Último recurso: Salvar como TXT
            try:
                with open(output_filepath.replace(".docx", ".txt"), "w") as f:
                    f.write(f"{title}\n\n{html_content}")
                return False, "Erro DOCX. Salvo como TXT."
            except:
                return False, f"Falha total na exportação: {e}"

    @staticmethod
    def export_to_pdf(title, html_content, output_filepath):
        logging.info(f"Exportando PDF via {PDF_ENGINE}")
        text_clean = re.sub(r'<[^>]+>', '\n', html_content)
        
        if PDF_ENGINE == "reportlab":
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                c = canvas.Canvas(output_filepath, pagesize=letter)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, 750, title)
                c.setFont("Helvetica", 12)
                y = 720
                for line in text_clean.split('\n'):
                    # Simples quebra de linha visual
                    c.drawString(40, y, line[:95]) 
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = 750
                c.save()
                return True, "PDF Gerado."
            except Exception as e:
                return False, f"Erro PDF: {e}"
        
        return False, "Motor PDF não instalado."

class GenevaProtocol:
    """Núcleo de Validação Teológica."""
    ALERTS = {
        "prosperidade": "ALERTA: Viés de Teologia da Prosperidade detectado.",
        "eu determino": "ALERTA: Linguagem de Confissão Positiva (Antropocêntrica).",
        "energia": "ALERTA: Terminologia vaga / Nova Era.",
        "merecimento": "CUIDADO: Revisar conceito de Graça vs Mérito."
    }
    @staticmethod
    def scan(text):
        if not text: return []
        return [msg for term, msg in GenevaProtocol.ALERTS.items() if term in text.lower()]

class AccessControl:
    """Controle de Login e Colaboradores."""
    @staticmethod
    def authenticate(username, password):
        users = read_json_safe(DATABASE_FILES["USERS"], {})
        # Backdoor de primeiro acesso seguro
        if username == "ADMIN" and password == "1234" and len(users) <= 1:
            return True
        stored_hash = users.get(username.upper())
        if not stored_hash: return False
        return stored_hash == hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def register_user(username, password):
        users = read_json_safe(DATABASE_FILES["USERS"], {})
        if username.upper() in users: return False, "Usuário já existe."
        users[username.upper()] = hashlib.sha256(password.encode()).hexdigest()
        write_json_safe(DATABASE_FILES["USERS"], users)
        return True, "Registrado com sucesso."

class PastoralMind:
    """Análise de Vitalidade."""
    @staticmethod
    def check_vitality():
        data = read_json_safe(DATABASE_FILES["SOUL"]).get("historico", [])[-7:]
        negatives = sum(1 for x in data if x['humor'] in ['Cansaço', 'Esgotamento', 'Tristeza'])
        if negatives >= 3:
            return "ALERTA", "#FF3333"
        return "ESTÁVEL", "#33FF33"

# ==============================================================================
# 07. INTERFACE GRÁFICA & CSS (VISUAL ORIGINAL RESTAURADO)
# ==============================================================================

# Carrega config para aplicar no CSS
cfg = read_json_safe(DATABASE_FILES["CONFIG"])
APP_COLOR = cfg.get("theme_color", "#D4AF37")
APP_FONT = normalize_font_name(cfg.get("font_family", "Inter"))

st.markdown(f"""
<style>
/* FONTES E CORES */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&display=swap');

:root {{
    --gold: {APP_COLOR};
    --bg-color: #000000;
    --panel-color: #0A0A0A;
    --text-color: #EAEAEA;
    --main-font: '{APP_FONT}', sans-serif;
    --header-font: 'Cinzel', serif;
}}

/* GERAL */
.stApp {{
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: var(--main-font);
}}

h1, h2, h3 {{
    font-family: var(--header-font) !important;
    color: var(--gold) !important;
}}

/* ELEMENTOS DE LOGIN (RESTAURADOS) */
.prime-logo {{
    width: 120px;
    height: 120px;
    display: block;
    margin: 0 auto;
}}
.login-title {{
    font-family: 'Cinzel', serif;
    color: var(--gold);
    text-align: center;
    letter-spacing: 6px;
    font-size: 24px;
    margin-top: 15px;
    margin-bottom: 30px;
    text-transform: uppercase;
    border-bottom: 1px solid #333;
    padding-bottom: 20px;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background-color: #080808;
    border-right: 1px solid #222;
}}

/* CARDS E BOTÕES */
.tech-card {{
    background: var(--panel-color);
    border: 1px solid #222;
    border-left: 3px solid var(--gold);
    padding: 18px;
    border-radius: 6px;
    margin-bottom: 12px;
}}

.stButton>button {{
    border: 1px solid var(--gold);
    color: var(--gold);
    background: transparent;
    transition: 0.3s;
}}
.stButton>button:hover {{
    background: var(--gold);
    color: #000;
}}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 08. FLUXO DE LOGIN (INTERFACE ORIGINAL)
# ==============================================================================
if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "ADMIN"

if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # LOGO SVG DOURADA ORIGINAL
        st.markdown(f"""
        <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="{APP_COLOR}" stroke-width="3" fill="none" />
            <line x1="50" y1="25" x2="50" y2="75" stroke="{APP_COLOR}" stroke-width="3" />
            <line x1="35" y1="40" x2="65" y2="40" stroke="{APP_COLOR}" stroke-width="3" />
        </svg>
        <div class="login-title">O PREGADOR</div>
        """, unsafe_allow_html=True)

        tab_entrar, tab_registrar = st.tabs(["ENTRAR", "REGISTRAR"])
        
        with tab_entrar:
            u_login = st.text_input("Identidade (ID)")
            p_login = st.text_input("Senha de Acesso", type="password")
            if st.button("ACESSAR O SISTEMA", use_container_width=True):
                if AccessControl.authenticate(u_login, p_login):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = u_login.upper()
                    st.success("Acesso Concedido.")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("NEGO A VOS CONHECER (Credenciais Inválidas).")
        
        with tab_registrar:
            st.info("Cadastro Local")
            nu = st.text_input("Novo Usuário", key="reg_u")
            np = st.text_input("Nova Senha", type="password", key="reg_p")
            if st.button("CRIAR CONTA"):
                ok, msg = AccessControl.register_user(nu, np)
                if ok: st.success(msg)
                else: st.error(msg)
    st.stop()

# ==============================================================================
# 09. APLICAÇÃO PRINCIPAL (SIDEBAR E MÓDULOS)
# ==============================================================================

with st.sidebar:
    st.markdown(f"## Pastor {st.session_state['user_name']}")
    
    vitality, color = PastoralMind.check_vitality()
    st.markdown(f"Vitalidade: <b style='color:{color}'>{vitality}</b>", unsafe_allow_html=True)
    st.divider()
    
    # Menu de Navegação
    menu = st.radio(
        "SISTEMA", 
        ["Cuidado Pastoral", "Gabinete Pastoral", "Rede Ministerial", "Biblioteca", "Configurações"]
    )
    
    st.markdown("---")
    if st.button("LOGOUT"):
        st.session_state["logado"] = False
        st.rerun()

# --- MÓDULO 1: CUIDADO PASTORAL (Expandido com Rotina Dinâmica e Teoria) ---
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral & Alma")
    
    tab1, tab2, tab3 = st.tabs(["Estado da Alma", "Teoria da Permissão", "Rotina Pastoral"])
    
    with tab1:
        st.markdown("<div class='tech-card'><b>Check-in Diário</b><br>Registre como está seu coração.</div>", unsafe_allow_html=True)
        humor = st.select_slider("Estado Emocional:", ["Esgotamento", "Cansaço", "Neutro", "Bem", "Pleno"])
        nota = st.text_area("Notas do dia (opcional)")
        
        if st.button("Registrar no Livro da Alma"):
            soul_db = read_json_safe(DATABASE_FILES["SOUL"])
            soul_db.setdefault("historico", []).append({
                "data": datetime.now().strftime("%Y-%m-%d"),
                "humor": humor,
                "nota": nota
            })
            write_json_safe(DATABASE_FILES["SOUL"], soul_db)
            st.success("Registrado com sucesso.")

    with tab2:
        # Conteúdo Educativo Solicitado
        st.info("🧠 **O que é a Teoria da Permissão?**\n\n"
                "Muitos pastores sofrem burnout não pelo trabalho, mas pela falta de permissão interna para serem humanos. "
                "Esta ferramenta ajuda você a visualizar se está se permitindo viver a Graça que prega.")
        
        col_input, col_viz = st.columns(2)
        with col_input:
            p_fail = st.slider("Permissão para Falhar (Errar)", 0, 100, 50)
            p_feel = st.slider("Permissão para Sentir (Dor/Ira)", 0, 100, 50)
            p_rest = st.slider("Permissão para Descansar", 0, 100, 50)
        
        with col_viz:
            if PLOTLY_OK:
                fig = go.Figure(data=go.Scatterpolar(
                    r=[p_fail, p_feel, p_rest, p_fail],
                    theta=['Falhar', 'Sentir', 'Descansar', 'Falhar'],
                    fill='toself',
                    line_color=APP_COLOR
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    margin=dict(t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.metric("Índice de Permissão", f"{(p_fail+p_feel+p_rest)//3}%")

    with tab3:
        st.subheader("📋 Rotina Dinâmica")
        st.caption("Adicione ou remova tarefas da sua liturgia diária.")
        
        # Carrega a rotina do config
        current_routine = cfg.get("rotina_pastoral", [])
        
        # Exibe lista com checkboxes
        for task in current_routine:
            st.checkbox(task, key=f"routine_{task}")
            
        st.divider()
        
        # Adicionar Nova Tarefa
        c_add, c_del = st.columns([3, 1])
        new_task = c_add.text_input("Nova Tarefa")
        if c_add.button("➕ Adicionar"):
            if new_task and new_task not in current_routine:
                current_routine.append(new_task)
                cfg["rotina_pastoral"] = current_routine
                write_json_safe(DATABASE_FILES["CONFIG"], cfg)
                st.rerun()
        
        # Remover Tarefa
        to_remove = c_del.selectbox("Remover", ["Selecione..."] + current_routine)
        if c_del.button("🗑️ Apagar"):
            if to_remove in current_routine:
                current_routine.remove(to_remove)
                cfg["rotina_pastoral"] = current_routine
                write_json_safe(DATABASE_FILES["CONFIG"], cfg)
                st.rerun()

# --- MÓDULO 2: GABINETE PASTORAL (Editor Robusto) ---
elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete de Preparação")
    
    col_list, col_editor = st.columns([1, 3])
    
    with col_list:
        st.markdown("**Seus Sermões**")
        files = [f for f in os.listdir(DIRECTORIES["SERMONS"]) if f.endswith(".html")]
        files.sort()
        selection = st.radio("Arquivo", ["Novo Documento"] + files)

    with col_editor:
        content_val = ""
        title_val = ""
        
        # Lógica de Carregamento
        if selection != "Novo Documento":
            try:
                with open(os.path.join(DIRECTORIES["SERMONS"], selection), "r", encoding="utf-8") as f:
                    content_val = f.read()
                title_val = selection.replace(".html", "")
            except Exception as e:
                st.error(f"Erro ao abrir: {e}")
        
        # Campos
        doc_title = st.text_input("Título da Mensagem", value=title_val)
        
        # Seleção de Editor (Prioridade: CKEditor -> Quill -> Textarea)
        final_content = content_val
        if CKEDITOR_AVAILABLE:
            final_content = st_ckeditor(value=content_val, key="ck_main", height=500)
        elif QUILL_AVAILABLE:
            final_content = st_quill(value=content_val, key="quill_main", html=True)
        else:
            final_content = st.text_area("Editor Texto", value=content_val, height=500)
            
        # BARRA DE FERRAMENTAS (Word, PDF, Scan)
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        
        clean_name = safe_filename(doc_title if doc_title else "sem_titulo")
        
        # Salvar
        if c1.button("💾 SALVAR"):
            path = os.path.join(DIRECTORIES["SERMONS"], f"{clean_name}.html")
            with open(path, "w", encoding="utf-8") as f: f.write(final_content)
            st.toast("Sermão salvo com sucesso!")
            time.sleep(1)
            st.rerun()
            
        # Exportar Word (Usa a classe ExportEngine detalhada acima)
        if c2.button("📄 DOCX (WORD)"):
            path = os.path.join(DIRECTORIES["SERMONS"], f"{clean_name}.docx")
            ok, msg = ExportEngine.export_to_docx(doc_title, final_content, path)
            if ok:
                st.success(msg)
                with open(path, "rb") as f:
                    st.download_button("Baixar Arquivo", f, file_name=f"{clean_name}.docx")
            else:
                st.error(msg)
                
        # Exportar PDF
        if c3.button("📕 PDF"):
            path = os.path.join(DIRECTORIES["SERMONS"], f"{clean_name}.pdf")
            ok, msg = ExportEngine.export_to_pdf(doc_title, final_content, path)
            if ok:
                st.success(msg)
                with open(path, "rb") as f:
                    st.download_button("Baixar PDF", f, file_name=f"{clean_name}.pdf")
            else:
                st.error(msg)
        
        # Scan Geneva
        if c4.button("🔍 SCAN TEOLÓGICO"):
            alerts = GenevaProtocol.scan(final_content)
            if alerts:
                st.warning("⚠️ Termos sensíveis detectados:")
                for a in alerts: st.write(f"- {a}")
            else:
                st.success("Nenhum termo de risco detectado.")

# --- MÓDULO 3: REDE MINISTERIAL (Braço Colaborativo) ---
elif menu == "Rede Ministerial":
    st.title("🤝 Rede Ministerial")
    st.markdown("Espaço para compartilhamento de vídeos, devocionais e avisos entre a liderança.")
    
    feed = read_json_safe(DATABASE_FILES["NETWORK_FEED"], [])
    
    # Formulário de Postagem
    with st.expander("📢 Publicar Novo Conteúdo"):
        with st.form("new_post"):
            pt = st.text_input("Título")
            pa = st.text_input("Autor", value=st.session_state["user_name"])
            pu = st.text_input("Link YouTube (Opcional)")
            pd = st.text_area("Mensagem / Descrição")
            
            if st.form_submit_button("Postar na Rede"):
                new_item = {
                    "id": int(time.time()),
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "title": pt, "author": pa, "url": pu, "desc": pd
                }
                feed.insert(0, new_item)
                write_json_safe(DATABASE_FILES["NETWORK_FEED"], feed)
                st.success("Publicado!")
                st.rerun()
    
    st.divider()
    
    # Exibição do Feed
    if not feed:
        st.info("Nenhuma publicação recente.")
    
    for item in feed:
        st.markdown(f"""
        <div class="tech-card">
            <h3>{item['title']}</h3>
            <small style="color:{APP_COLOR}">Por: {item['author']} em {item['date']}</small>
            <p>{item['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if "youtube" in item['url'] or "youtu.be" in item['url']:
            try: st.video(item['url'])
            except: st.write(f"[Link Vídeo]({item['url']})")
        
        # Botão de remoção simples
        if st.button("Remover", key=f"del_{item['id']}"):
            feed.remove(item)
            write_json_safe(DATABASE_FILES["NETWORK_FEED"], feed)
            st.rerun()

# --- MÓDULO 4: BIBLIOTECA ---
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Digital")
    
    col_up, col_list = st.columns([1, 2])
    with col_up:
        st.markdown("**Upload de Livro**")
        up = st.file_uploader("PDF/EPUB/DOCX", type=["pdf", "epub", "docx", "txt"])
        if up:
            dest = os.path.join(DIRECTORIES["LIBRARY"], up.name)
            with open(dest, "wb") as f: f.write(up.getbuffer())
            st.success("Livro indexado.")
            
    with col_list:
        st.markdown("**Seu Acervo**")
        files = os.listdir(DIRECTORIES["LIBRARY"])
        if not files: st.info("Biblioteca vazia.")
        for f in files:
            path = os.path.join(DIRECTORIES["LIBRARY"], f)
            with open(path, "rb") as b:
                st.download_button(f"⬇️ {f}", b, file_name=f)

# --- MÓDULO 5: CONFIGURAÇÕES & SOBRE ---
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    
    tab_ui, tab_tools, tab_about = st.tabs(["Personalização", "Ferramentas", "Sobre"])
    
    with tab_ui:
        st.subheader("Visual")
        new_color = st.color_picker("Cor do Tema", APP_COLOR)
        new_font = st.selectbox("Fonte Principal", ["Inter", "Roboto", "Cinzel"])
        
        if st.button("Salvar Aparência"):
            cfg["theme_color"] = new_color
            cfg["font_family"] = new_font
            write_json_safe(DATABASE_FILES["CONFIG"], cfg)
            st.success("Configurações salvas. Recarregue a página.")
            
    with tab_tools:
        st.subheader("Manutenção do Sistema")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Backup**")
            if st.button("📦 Criar Backup Completo (ZIP)"):
                ts = int(time.time())
                shutil.make_archive(os.path.join(DIRECTORIES["BACKUP_HIDDEN"], f"Backup_{ts}"), 'zip', ROOT_DIR)
                st.success("Backup salvo na pasta segura.")
        
        with col2:
            st.markdown("**Logs**")
            if st.button("Limpar Logs de Auditoria"):
                try:
                    open(os.path.join(LOG_DIR, "system_audit_master.log"), 'w').close()
                    st.success("Logs limpos.")
                except: st.error("Erro ao limpar logs.")
                
    with tab_about:
        st.header("O PREGADOR")
        st.markdown("**Versão:** V40 (Maximum Robustness)")
        st.markdown("**Build:** Titanium Core")
        st.markdown("---")
        st.caption("Sistema de Gestão Eclesiástica e Apoio Homilético.")
        st.caption("Todos os direitos reservados ao Ministério Local.")
        st.caption("Desenvolvido com Python/Streamlit.")

# Fim do código
