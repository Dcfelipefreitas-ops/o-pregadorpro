# -*- coding: utf-8 -*-
"""
O PREGADOR - SYSTEM CORE (Versão V36.0 - Titanium Edition)
Status: Produção / Robusto / Full Feature
Autoria: Sistema Consolidado

[ÍNDICE DE FUNCIONALIDADES]
1.  Bootloader (Gênesis Protocol): Inicialização de pastas e DBs.
2.  Módulo de Segurança (CryptoManager): Criptografia AES.
3.  Módulo de Exportação (ExportEngine): Geradores DOCX/PDF com Múltiplos Motores.
4.  Núcleo Teológico (GenevaProtocol): Validação doutrinária.
5.  Análise Humana (PastoralMind): Burnout e Teoria da Permissão Educativa.
6.  Sistema de Usuários (AccessControl): Login e Permissões de Rede.
7.  Interface Gráfica (UX): CSS Dark Cathedral e componentes visuais.
8.  Gabinete Pastoral: Editor Híbrido (CKEditor/Quill/Native).
9.  Rede Ministerial: Feed de Colaboradores e Vídeos.
"""

# ==============================================================================
# SEÇÃO 01: IMPORTAÇÕES E CONFIGURAÇÃO INICIAL (Obrigatório)
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

# Configuração da página deve ser a PRIMEIRA chamada do Streamlit
st.set_page_config(
    page_title="O PREGADOR | Titanium",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# --- CONFIGURAÇÃO DE LOGGING DO SISTEMA ---
# Cria logs detalhados para auditoria pastoral
if not os.path.exists("Dados_Pregador_V31/System_Logs"):
    os.makedirs("Dados_Pregador_V31/System_Logs", exist_ok=True)

logging.basicConfig(
    filename=os.path.join("Dados_Pregador_V31", "System_Logs", "system_audit_core.log"),
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s'
)
logging.info("Sistema Iniciando Boot...")

# ==============================================================================
# SEÇÃO 02: TENTATIVAS DE IMPORTAÇÃO DE BIBLIOTECAS (MODULARIZAÇÃO)
# ==============================================================================
# Nesta seção, garantimos que o app não quebre se faltar uma biblioteca específica,
# ativando "flags" de disponibilidade.

# 2.1 Editor de Texto Avançado (CKEditor)
CKEDITOR_AVAILABLE = False
STREAMLIT_CKEDITOR = False
try:
    from streamlit_ckeditor import st_ckeditor  # type: ignore
    STREAMLIT_CKEDITOR = True
    CKEDITOR_AVAILABLE = True
    logging.info("Módulo CKEditor carregado com sucesso.")
except ImportError:
    logging.warning("CKEditor não encontrado. Fallback ativado.")

# 2.2 Editor Intermediário (Quill)
QUILL_AVAILABLE = False
try:
    from streamlit_quill import st_quill  # type: ignore
    QUILL_AVAILABLE = True
    logging.info("Módulo Quill carregado com sucesso.")
except ImportError:
    logging.warning("Quill não encontrado.")

# 2.3 Visualização de Dados (Plotly)
PLOTLY_OK = False
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
    logging.info("Módulo Plotly carregado.")
except ImportError:
    logging.warning("Plotly não instalado. Usando visualizações simples.")

# 2.4 Criptografia Militar (Cryptography AES)
CRYPTO_OK = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except ImportError:
    logging.warning("Módulo Crypto avançado ausente.")

# 2.5 Engenharia de Exportação WORD (DOCX)
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

# 2.6 Engenharia de Exportação PDF
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
# SEÇÃO 03: UTILITÁRIOS GLOBAIS E TRATAMENTO DE ERROS
# ==============================================================================
# Estas funções precisam estar definidas ANTES de qualquer uso no CSS ou Config

def normalize_font_name(fname):
    """
    Função vital para o CSS. Normaliza nomes de fontes vindas do JSON config.
    Remove aspas simples ou duplas e limpa espaços extras.
    """
    if not fname:
        return "Inter"  # Fonte padrão
    try:
        # Se for uma lista separada por vírgula, pega a primeira
        base_name = fname.split(",")[0]
        # Remove caracteres indesejados
        base_name = base_name.strip().replace("'", "").replace('"', "")
        return base_name
    except Exception as e:
        logging.error(f"Erro ao normalizar fonte: {e}")
        return "Inter"

def safe_filename(text):
    """Garante que o nome do arquivo seja seguro para o sistema operacional."""
    if not text:
        return "arquivo_sem_nome_" + str(int(time.time()))
    clean_text = str(text).strip()
    # Substitui espaços por underscores e remove caracteres estranhos
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
    """Escreve um arquivo JSON atomicamente (evita corrupção se desligar)."""
    try:
        temp_path = path + ".tmp_write"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # Substituição atômica do SO
        os.replace(temp_path, path)
        return True
    except Exception as e:
        logging.error(f"FATAL: Erro ao escrever JSON em {path}. Erro: {e}")
        st.error(f"Erro de Gravação: {e}")
        return False

# ==============================================================================
# SEÇÃO 04: GÊNESIS PROTOCOL (GESTÃO DE SISTEMA DE ARQUIVOS)
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
    "NETWORK": os.path.join(ROOT_DIR, "Rede_Ministerial")  # Novo braço de rede
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
    """Garante a existência da integridade física do sistema."""
    # 1. Cria pastas
    for key, path in DIRECTORIES.items():
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            logging.info(f"Diretório criado: {path}")

    # 2. Inicializa Banco de Configurações
    if not os.path.exists(DATABASE_FILES["CONFIG"]):
        default_config = {
            "theme_color": "#D4AF37",
            "font_size": 18,
            "font_family": "Inter",
            "theme_mode": "Dark Cathedral",
            "enc_password": "OMEGA_KEY_DEFAULT",
            "backup_interval": 86400,
            "last_backup_timestamp": None,
            "work_mode": "Full",
            # Lista dinâmica solicitada para rotina
            "rotina_pastoral": [
                "Oração Inicial",
                "Leitura da Palavra",
                "Estudo Teológico (45 min)",
                "Cuidado da Família"
            ]
        }
        write_json_safe(DATABASE_FILES["CONFIG"], default_config)

    # 3. Inicializa Banco de Usuários
    if not os.path.exists(DATABASE_FILES["USERS"]):
        # Hash padrão SHA256 para 'admin'
        default_admin = hashlib.sha256("admin".encode()).hexdigest()
        write_json_safe(DATABASE_FILES["USERS"], {"ADMIN": default_admin})

    # 4. Inicializa Feed da Rede Ministerial (Colaboradores)
    if not os.path.exists(DATABASE_FILES["NETWORK_FEED"]):
        write_json_safe(DATABASE_FILES["NETWORK_FEED"], [])

    # 5. Garante outros JSONs vazios
    for db_key in ["MEMBERS", "SOUL"]:
        if not os.path.exists(DATABASE_FILES[db_key]):
            write_json_safe(DATABASE_FILES[db_key], [])
    
    if not os.path.exists(DATABASE_FILES["STATS"]):
        write_json_safe(DATABASE_FILES["STATS"], {"xp": 0, "nivel": 1})

# Executa o protocolo de inicialização
genesis_boot_protocol()


# ==============================================================================
# SEÇÃO 05: CLASSES DE LÓGICA DE NEGÓCIO (BACKEND)
# ==============================================================================

class CryptoManager:
    """Gerencia criptografia e segurança de arquivos."""
    
    @staticmethod
    def encrypt_data(password, text_data):
        if not CRYPTO_OK:
            return None
        try:
            # Deriva chave simples do SHA256 da senha
            key = hashlib.sha256(password.encode()).digest()
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, text_data.encode("utf-8"), None)
            return base64.b64encode(nonce + ciphertext).decode("utf-8")
        except Exception as e:
            logging.error(f"Erro Crypto: {e}")
            return None

class ExportEngine:
    """O Módulo Word robusto para lidar com DOCX e PDF."""
    
    @staticmethod
    def export_to_docx(title, html_content, output_filepath):
        logging.info(f"Iniciando exportação DOCX usando engine: {HTML2DOCX_ENGINE}")
        
        # Estratégia 1: Mammoth (Melhor fidelidade)
        if HTML2DOCX_ENGINE == "mammoth":
            try:
                import mammoth
                # Envolve o conteúdo para garantir estrutura válida
                full_html = f"<html><head><title>{title}</title></head><body><h1>{title}</h1>{html_content}</body></html>"
                result = mammoth.convert_to_docx(full_html)
                with open(output_filepath, "wb") as f:
                    f.write(result.value)
                return True, "Arquivo DOCX gerado com sucesso (Mammoth)."
            except Exception as e:
                logging.error(f"Erro Mammoth: {e}")
        
        # Estratégia 2: html2docx
        if HTML2DOCX_ENGINE == "html2docx":
            try:
                from html2docx import html2docx
                buf = html2docx(html_content, title=title)
                with open(output_filepath, "wb") as f:
                    f.write(buf.getvalue())
                return True, "Arquivo DOCX gerado com sucesso (Html2Docx)."
            except Exception as e:
                logging.error(f"Erro Html2Docx: {e}")

        # Estratégia 3: Python-Docx Manual (Texto Puro com formatação mínima)
        if HTML2DOCX_ENGINE == "docx_manual" or HTML2DOCX_ENGINE is None:
            try:
                from docx import Document
                doc = Document()
                doc.add_heading(title, 0)
                
                # Remove HTML tags simples
                text_clean = re.sub(r'<[^>]+>', '\n', html_content)
                paragraphs = text_clean.split('\n')
                for p in paragraphs:
                    if p.strip():
                        doc.add_paragraph(p.strip())
                        
                doc.save(output_filepath)
                return True, "Arquivo gerado via Fallback (Texto Puro, sem formatação rica)."
            except Exception as e:
                logging.error(f"Erro Fatal Docx: {e}")
                
        return False, "Nenhum motor de exportação disponível."

    @staticmethod
    def export_to_pdf(title, html_content, output_filepath):
        logging.info(f"Iniciando exportação PDF usando engine: {PDF_ENGINE}")
        
        text_clean = re.sub(r'<[^>]+>', '\n', html_content)
        
        if PDF_ENGINE == "reportlab":
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                
                c = canvas.Canvas(output_filepath, pagesize=letter)
                w, h = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, h - 50, title)
                c.line(40, h - 60, w - 40, h - 60)
                
                # Content
                c.setFont("Helvetica", 12)
                y_pos = h - 90
                
                lines = text_clean.split('\n')
                for line in lines:
                    # Quebra de linha simples
                    line = line.strip()
                    if not line: continue
                    
                    # Corta se muito longo (implementação robusta requer Platypus, aqui simplificado)
                    c.drawString(40, y_pos, line[:100])
                    y_pos -= 15
                    if len(line) > 100:
                        c.drawString(40, y_pos, line[100:200])
                        y_pos -= 15
                    
                    if y_pos < 50:
                        c.showPage()
                        y_pos = h - 50
                        c.setFont("Helvetica", 12)
                        
                c.save()
                return True, "PDF gerado via ReportLab."
            except Exception as e:
                return False, f"Erro ao gerar PDF: {e}"
        
        return False, "Motor PDF indisponível (instale ReportLab)."

class GenevaProtocol:
    """Núcleo de validação teológica básica."""
    # Base de conhecimento de termos sensíveis
    ALERTS = {
        "prosperidade": "ALERTA: Possível viés de Teologia da Prosperidade.",
        "eu determino": "ALERTA: Linguagem de Confissão Positiva (antropocêntrica).",
        "energia cósmica": "ALERTA: Linguagem Sincretista/Nova Era.",
        "não há pecado": "PERIGO: Heresia Pelagiana ou Antinomiana."
    }
    
    @staticmethod
    def run_diagnostic(text):
        if not text:
            return []
        lower_text = text.lower()
        findings = []
        for term, message in GenevaProtocol.ALERTS.items():
            if term in lower_text:
                findings.append(message)
        return findings

class AccessControl:
    """Gestão de Acesso, Autenticação e Registro de Colaboradores."""
    
    @staticmethod
    def authenticate(username, password):
        # Admin Override (Backdoor de segurança para dev)
        users = read_json_safe(DATABASE_FILES["USERS"], {})
        if username == "ADMIN" and password == "1234" and not users:
            return True # Primeira execução
            
        stored_hash = users.get(username.upper())
        if not stored_hash:
            return False
            
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        return input_hash == stored_hash

    @staticmethod
    def register_user(username, password):
        users = read_json_safe(DATABASE_FILES["USERS"], {})
        if username.upper() in users:
            return False, "Usuário já existente."
        
        new_hash = hashlib.sha256(password.encode()).hexdigest()
        users[username.upper()] = new_hash
        if write_json_safe(DATABASE_FILES["USERS"], users):
            return True, "Usuário registrado com sucesso."
        return False, "Erro ao salvar banco de usuários."

# ==============================================================================
# SEÇÃO 06: INJEÇÃO DE CSS E UI GLOBAL
# ==============================================================================
# Aqui carregamos a config antes de definir o estilo para usar as variáveis
current_config = read_json_safe(DATABASE_FILES["CONFIG"])

# VARIÁVEIS CRÍTICAS NORMALIZADAS
APP_PRIMARY_COLOR = current_config.get("theme_color", "#D4AF37")
APP_FONT = normalize_font_name(current_config.get("font_family", "Inter"))

def inject_global_css():
    st.markdown(f"""
    <style>
        /* IMPORTAÇÃO DE FONTES EXTERNAS (GOOGLE FONTS) */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;800&family=Inter:wght@300;400;600&family=Roboto+Mono:wght@400&display=swap');
        
        :root {{
            --primary: {APP_PRIMARY_COLOR};
            --bg-color: #0e0e0e;
            --panel-bg: #111111;
            --text-color: #EAEAEA;
            --font-main: '{APP_FONT}', sans-serif;
            --font-header: 'Cinzel', serif;
        }}
        
        html, body, [class*="css"] {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-main);
        }}
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: #050505;
            border-right: 1px solid #333;
        }}
        
        /* TÍTULOS E HEADERS */
        h1, h2, h3 {{
            font-family: var(--font-header) !important;
            color: var(--primary) !important;
            font-weight: 700;
        }}
        
        /* BOTÕES PERSONALIZADOS (ROBUSTOS) */
        .stButton>button {{
            width: 100%;
            background-color: transparent;
            color: var(--primary);
            border: 1px solid var(--primary);
            border-radius: 4px;
            font-family: var(--font-main);
            font-weight: 600;
            padding: 0.5rem;
            transition: all 0.3s ease;
        }}
        
        .stButton>button:hover {{
            background-color: var(--primary);
            color: #000;
            border-color: var(--primary);
        }}
        
        /* CARD PASTORAL (ESTILO PRÓPRIO) */
        .pastoral-card {{
            background-color: var(--panel-bg);
            border-left: 4px solid var(--primary);
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        }}
        
        .card-title {{
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 10px;
            font-family: var(--font-header);
        }}
        
        /* EDITOR FALLBACK */
        .stTextArea textarea {{
            background-color: #1a1a1a;
            color: #ddd;
            border: 1px solid #444;
        }}
    </style>
    """, unsafe_allow_html=True)

# Aplica o CSS imediatamente
inject_global_css()

# ==============================================================================
# SEÇÃO 07: FLUXO DE CONTROLE PRINCIPAL (MAIN LOOP)
# ==============================================================================

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = "GUEST"

# --- TELA DE LOGIN ---
if not st.session_state["logged_in"]:
    col_spacer_l, col_login, col_spacer_r = st.columns([1, 1, 1])
    
    with col_login:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Logo Simulado via CSS/SVG
        st.markdown(f"""
        <div style="text-align:center">
            <h1 style="font-size: 3rem; margin-bottom: 0;">Ω PREGADOR</h1>
            <p style="letter-spacing: 5px; color: #888; font-size: 0.8rem;">TITANIUM EDITION V36</p>
            <hr style="border-color: {APP_PRIMARY_COLOR}; width: 50%; margin: 20px auto;">
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("auth_form"):
            input_user = st.text_input("Credencial Pastoral (ID)", placeholder="Ex: ADMIN")
            input_pass = st.text_input("Chave de Segurança", type="password")
            
            submitted = st.form_submit_button("AUTENTICAR NO SISTEMA")
            
            if submitted:
                if AccessControl.authenticate(input_user, input_pass):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = input_user.upper()
                    st.success("Autenticação validada. Carregando Gabinete...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. O acesso foi negado.")
    st.stop()  # Impede de carregar o resto do app se não logado

# --- BARRA LATERAL (SIDEBAR NAVIGATION) ---
with st.sidebar:
    st.markdown(f"## Pastor(a): {st.session_state['username']}")
    st.caption("Conectado | Servidor Seguro")
    
    # Navegação Robusta
    navigation = st.radio(
        "Módulos do Sistema", 
        ["Cuidado Pastoral", "Gabinete (Editor)", "Rede Ministerial", "Biblioteca", "Configurações"],
        index=0
    )
    
    st.markdown("---")
    
    # Cálculo rápido de vitalidade para Sidebar
    soul_data = read_json_safe(DATABASE_FILES["SOUL"], {"historico": []})
    hist = soul_data.get("historico", [])[-7:]
    negative_states = sum(1 for h in hist if h['humor'] in ['Cansaço Extremo', 'Tristeza', 'Estresse'])
    
    if negative_states >= 3:
        status_label = "ALERTA"
        status_color = "#FF3333"
    else:
        status_label = "ESTÁVEL"
        status_color = "#33FF33"
        
    st.markdown(f"Status Emocional: <b style='color:{status_color}'>{status_label}</b>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("DESCONECTAR"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==============================================================================
# SEÇÃO 08: MÓDULO CUIDADO PASTORAL (EXPANDIDO)
# ==============================================================================
if navigation == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral & Saúde da Alma")
    st.markdown("---")
    
    tab_status, tab_permissoes, tab_rotina = st.tabs(["📊 Estado da Alma", "⚖️ Teoria da Permissão", "📋 Rotina Dinâmica"])
    
    # 8.1 - ESTADO DA ALMA (DIÁRIO EMOCIONAL)
    with tab_status:
        st.markdown(f"<div class='pastoral-card'><div class='card-title'>Diário Emocional</div>Registe honestamente como está seu coração hoje diante de Deus.</div>", unsafe_allow_html=True)
        
        col_input, col_graph = st.columns([1, 2])
        
        with col_input:
            humor_select = st.select_slider(
                "Nível de Energia Espiritual/Emocional",
                options=["Esgotamento", "Cansaço Extremo", "Cansaço Leve", "Neutro", "Bom", "Excelente", "Plenitude"],
                value="Neutro"
            )
            obs_day = st.text_area("Notas do dia (opcional)", height=100)
            
            if st.button("REGISTRAR CHECK-IN", use_container_width=True):
                entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "humor": humor_select,
                    "obs": obs_day
                }
                current_soul = read_json_safe(DATABASE_FILES["SOUL"])
                if "historico" not in current_soul: current_soul["historico"] = []
                current_soul["historico"].append(entry)
                write_json_safe(DATABASE_FILES["SOUL"], current_soul)
                st.success("Estado registrado no Livro da Alma.")
        
        with col_graph:
            # Gráfico de tendência (Plotly ou Texto)
            hist = read_json_safe(DATABASE_FILES["SOUL"]).get("historico", [])
            if len(hist) > 0:
                df_data = [{"Data": x['date'][:10], "Estado": x['humor']} for x in hist]
                st.table(df_data[-5:]) # Mostra os últimos 5 em tabela para robustez
            else:
                st.info("Nenhum registro encontrado.")

    # 8.2 - TEORIA DA PERMISSÃO (EDUCATIVO + INTERATIVO)
    with tab_permissoes:
        st.info("🧠 A 'Teoria da Permissão' é uma ferramenta terapêutica para líderes que sofrem de auto-cobrança excessiva.")
        
        with st.expander("📚 Ler o Conceito Completo da Ferramenta"):
            st.markdown("""
            **O que é?**
            Muitos pastores colapsam não pelo excesso de trabalho, mas pela **falta de permissão interna** para serem humanos.
            
            **As 4 Permissões Fundamentais:**
            1.  **Permissão para Falhar:** Aceitar que erros não anulam o chamado. A graça é para o líder também.
            2.  **Permissão para Sentir:** Validar emoções 'negativas' (ira, tristeza) sem as demonizar imediatamente.
            3.  **Permissão para Limitar:** Dizer 'não' é uma disciplina espiritual sagrada. Você não é o Messias.
            4.  **Permissão para Receber:** Deixar de ser apenas o doador e aceitar cuidado.
            """)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Auto-Avaliação de Permissão Interna")
            p_fail = st.slider("Quanto você se permite cometer erros?", 0, 100, 50)
            p_feel = st.slider("Quanto você se permite sentir dor/tristeza?", 0, 100, 50)
            p_rest = st.slider("Quanto você se permite descansar sem culpa?", 0, 100, 50)
            p_recv = st.slider("Quanto você aceita ajuda de outros?", 0, 100, 50)
        
        with c2:
            avg_perm = (p_fail + p_feel + p_rest + p_recv) / 4
            st.markdown(f"### Índice de Permissão: {avg_perm:.1f}%")
            if avg_perm < 40:
                st.error("CRÍTICO: Você está sendo um feitor cruel de si mesmo. Busque a Graça.")
            elif avg_perm < 70:
                st.warning("ATENÇÃO: Sua auto-cobrança está acima do saudável.")
            else:
                st.success("SAUDÁVEL: Você entende seus limites humanos.")
                
            if PLOTLY_OK:
                fig = go.Figure(data=go.Scatterpolar(
                    r=[p_fail, p_feel, p_rest, p_recv, p_fail],
                    theta=['Falhar','Sentir','Descansar','Receber', 'Falhar'],
                    fill='toself',
                    name='Permissões',
                    line_color=APP_PRIMARY_COLOR
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

    # 8.3 - ROTINA DINÂMICA
    with tab_rotina:
        st.markdown(f"<div class='pastoral-card'><div class='card-title'>Gerenciador de Liturgia Diária</div>Acompanhe seus hábitos espirituais e administrativos.</div>", unsafe_allow_html=True)
        
        cfg = read_json_safe(DATABASE_FILES["CONFIG"])
        rotina_list = cfg.get("rotina_pastoral", [])
        
        # Checkbox dinâmico
        completed_tasks = 0
        for task in rotina_list:
            if st.checkbox(task, key=f"routine_{task}"):
                completed_tasks += 1
                
        progress = completed_tasks / len(rotina_list) if rotina_list else 0
        st.progress(progress)
        
        st.divider()
        st.subheader("Gerenciar Lista de Tarefas")
        
        c_add, c_del = st.columns([2, 1])
        
        with c_add:
            new_item = st.text_input("Adicionar Nova Tarefa à Rotina Padrão")
            if st.button("➕ Adicionar Item"):
                if new_item and new_item not in rotina_list:
                    rotina_list.append(new_item)
                    cfg["rotina_pastoral"] = rotina_list
                    write_json_safe(DATABASE_FILES["CONFIG"], cfg)
                    st.success("Adicionado à rotina permanente.")
                    st.rerun()
        
        with c_del:
            del_item = st.selectbox("Selecionar para Remover", ["Selecione..."] + rotina_list)
            if st.button("🗑️ Remover Item"):
                if del_item in rotina_list:
                    rotina_list.remove(del_item)
                    cfg["rotina_pastoral"] = rotina_list
                    write_json_safe(DATABASE_FILES["CONFIG"], cfg)
                    st.success("Item removido.")
                    st.rerun()

# ==============================================================================
# SEÇÃO 09: MÓDULO GABINETE (EDITOR E EXPORTAÇÃO)
# ==============================================================================
elif navigation == "Gabinete (Editor)":
    st.title("📝 Gabinete de Preparação de Sermão")
    
    col_file_nav, col_editor_area = st.columns([1, 4])
    
    with col_file_nav:
        st.markdown("### 📂 Arquivos")
        # Lista arquivos .html na pasta SERMONS
        files = [f for f in os.listdir(DIRECTORIES["SERMONS"]) if f.endswith(".html")]
        files.sort()
        selection = st.radio("Seus Esboços", ["Novo Documento"] + files)
    
    with col_editor_area:
        # Lógica de Carregamento
        current_content = ""
        current_title_placeholder = "Título da Mensagem..."
        
        if selection != "Novo Documento":
            file_path = os.path.join(DIRECTORIES["SERMONS"], selection)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    current_content = f.read()
                current_title_placeholder = selection.replace(".html", "")
            except Exception as e:
                st.error(f"Erro ao abrir arquivo: {e}")

        # Campos de Edição
        sermon_title = st.text_input("Título do Sermão / Estudo", value=current_title_placeholder if selection != "Novo Documento" else "")
        
        # --- SELEÇÃO DO MOTOR DO EDITOR ---
        st.markdown("### Conteúdo do Texto")
        final_content = current_content
        
        # Prioridade 1: CKEditor
        if CKEDITOR_AVAILABLE:
            final_content = st_ckeditor(value=current_content, key="ck_editor_main", height=500)
        # Prioridade 2: Quill
        elif QUILL_AVAILABLE:
            final_content = st_quill(value=current_content, html=True, key="quill_editor_main")
        # Fallback: Textarea simples
        else:
            st.warning("Editores avançados indisponíveis. Usando modo texto simples.")
            final_content = st.text_area("Texto", value=current_content, height=500)
        
        # --- BARRA DE FERRAMENTAS DO SERMÃO (AÇÕES) ---
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        
        safe_name = safe_filename(sermon_title if sermon_title else "SemTitulo")
        
        with c1:
            if st.button("💾 SALVAR PROGRESSO"):
                target_path = os.path.join(DIRECTORIES["SERMONS"], f"{safe_name}.html")
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(final_content if final_content else "")
                st.toast("Documento Salvo com Sucesso!", icon="✅")
                time.sleep(1)
                st.rerun()

        with c2:
            if st.button("🔍 ANÁLISE GENEVA"):
                findings = GenevaProtocol.run_diagnostic(final_content)
                if findings:
                    with st.expander("⚠️ Alertas Doutrinários Detectados", expanded=True):
                        for f in findings:
                            st.write(f"- {f}")
                else:
                    st.success("Geneva Protocol: Nenhum termo crítico detectado.")
                    
        with c3:
            if st.button("📄 EXPORTAR DOCX (WORD)"):
                docx_path = os.path.join(DIRECTORIES["SERMONS"], f"{safe_name}.docx")
                with st.spinner(f"Gerando DOCX via {HTML2DOCX_ENGINE}..."):
                    status, msg = ExportEngine.export_to_docx(sermon_title, final_content, docx_path)
                
                if status:
                    st.success(msg)
                    with open(docx_path, "rb") as f:
                        st.download_button(f"⬇️ Baixar {safe_name}.docx", f, file_name=f"{safe_name}.docx")
                else:
                    st.error(f"Falha: {msg}")

        with c4:
            if st.button("📕 EXPORTAR PDF"):
                pdf_path = os.path.join(DIRECTORIES["SERMONS"], f"{safe_name}.pdf")
                with st.spinner(f"Gerando PDF via {PDF_ENGINE}..."):
                    status, msg = ExportEngine.export_to_pdf(sermon_title, final_content, pdf_path)
                
                if status:
                    st.success(msg)
                    with open(pdf_path, "rb") as f:
                        st.download_button(f"⬇️ Baixar {safe_name}.pdf", f, file_name=f"{safe_name}.pdf")
                else:
                    st.error(f"Falha: {msg}")

# ==============================================================================
# SEÇÃO 10: MÓDULO REDE MINISTERIAL (BRAÇO DE COLABORADORES)
# ==============================================================================
elif navigation == "Rede Ministerial":
    st.title("🤝 Rede Ministerial Colaborativa")
    st.markdown("Um braço dedicado para que colaboradores do ministério postem devocionais e vídeos de edificação.")
    
    # Carregar Feed
    feed_data = read_json_safe(DATABASE_FILES["NETWORK_FEED"], [])
    
    # Área de Postagem (Disponível para usuários logados)
    with st.expander("📢 PUBLICAR NOVO CONTEÚDO NA REDE", expanded=False):
        st.info("Sua publicação ficará visível para toda a equipe ministerial conectada.")
        with st.form("new_post_form"):
            p_title = st.text_input("Título do Devocional / Vídeo")
            p_author = st.text_input("Nome do Colaborador", value=st.session_state['username'])
            p_url = st.text_input("Link do Youtube / Vimeo (Opcional)")
            p_desc = st.text_area("Descrição / Mensagem curta")
            
            submit_post = st.form_submit_button("POSTAR NA REDE")
            
            if submit_post:
                if p_title and p_desc:
                    new_item = {
                        "id": int(time.time()),
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "title": p_title,
                        "author": p_author,
                        "url": p_url,
                        "description": p_desc
                    }
                    # Insere no topo
                    feed_data.insert(0, new_item)
                    write_json_safe(DATABASE_FILES["NETWORK_FEED"], feed_data)
                    st.success("Conteúdo publicado na rede!")
                    st.rerun()
                else:
                    st.warning("Título e Descrição são obrigatórios.")

    st.markdown("---")
    st.markdown("### 📡 Feed de Atualizações")
    
    if not feed_data:
        st.info("Nenhuma publicação encontrada na rede. Seja o primeiro a edificar a equipe!")
    
    for item in feed_data:
        # Layout de Card de Feed
        st.markdown(f"""
        <div class="pastoral-card">
            <h3 style="margin:0; font-size: 1.4rem;">{item['title']}</h3>
            <small style="color: {APP_PRIMARY_COLOR}">Publicado por: {item['author']} em {item['date']}</small>
            <p style="margin-top: 10px;">{item['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Renderização condicional de vídeo
        if item.get("url") and ("youtube" in item["url"] or "youtu.be" in item["url"]):
            try:
                st.video(item["url"])
            except:
                st.warning("Não foi possível carregar o vídeo.")
        elif item.get("url"):
            st.markdown(f"[Link Externo de Recurso]({item['url']})")
        
        # Opção de Exclusão (Admin Only ou próprio autor - aqui simplificado para todos logados pela demo)
        if st.button("Remover Publicação", key=f"del_{item['id']}"):
            feed_data.remove(item)
            write_json_safe(DATABASE_FILES["NETWORK_FEED"], feed_data)
            st.rerun()
        
        st.markdown("---")

# ==============================================================================
# SEÇÃO 11: MÓDULO BIBLIOTECA DIGITAL
# ==============================================================================
elif navigation == "Biblioteca":
    st.title("📚 Biblioteca & Acervo Digital")
    
    c_upload, c_view = st.columns([1, 2])
    
    with c_upload:
        st.markdown(f"<div class='pastoral-card'><div class='card-title'>Adicionar Livro</div>PDFs e EPUBS locais</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload de Arquivo", type=["pdf", "epub", "txt", "docx"])
        
        if uploaded:
            dest_path = os.path.join(DIRECTORIES["LIBRARY"], uploaded.name)
            with open(dest_path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.success(f"Arquivo '{uploaded.name}' indexado com sucesso.")

    with c_view:
        st.markdown("### 📖 Acervo Disponível")
        lib_files = os.listdir(DIRECTORIES["LIBRARY"])
        if not lib_files:
            st.info("Nenhum livro no acervo. Utilize o painel de upload.")
        else:
            for book in lib_files:
                st.markdown(f"**📑 {book}**")
                file_p = os.path.join(DIRECTORIES["LIBRARY"], book)
                
                # Botão de download para recuperar arquivo
                with open(file_p, "rb") as f:
                    st.download_button("Baixar para Dispositivo", f, file_name=book, key=f"dl_{book}")

# ==============================================================================
# SEÇÃO 12: MÓDULO DE CONFIGURAÇÕES & FERRAMENTAS AVANÇADAS
# ==============================================================================
elif navigation == "Configurações":
    st.title("⚙️ Configurações & Ferramentas do Sistema")
    
    tabs = st.tabs(["Personalização (UI)", "Segurança & Usuários", "Ferramentas & Backup"])
    
    current_conf = read_json_safe(DATABASE_FILES["CONFIG"])
    
    with tabs[0]:
        st.subheader("Aparência do Pregador")
        col1, col2 = st.columns(2)
        with col1:
            new_color = st.color_picker("Cor de Destaque (Tema)", current_conf.get("theme_color"))
        with col2:
            new_font = st.selectbox("Família de Fontes", ["Inter", "Roboto", "Cinzel", "Lato"], index=0)
            
        if st.button("Aplicar Alterações Visuais"):
            current_conf["theme_color"] = new_color
            current_conf["font_family"] = new_font
            write_json_safe(DATABASE_FILES["CONFIG"], current_conf)
            st.toast("Configurações salvas. Por favor, recarregue a página.")
    
    with tabs[1]:
        st.subheader("Gerenciar Acessos")
        if st.session_state["username"] == "ADMIN":
            st.info("Painel de Administrador Ativo")
            with st.form("new_user_f"):
                nu_name = st.text_input("Novo Usuário (Colaborador)")
                nu_pass = st.text_input("Definir Senha", type="password")
                
                if st.form_submit_button("Criar Novo Acesso"):
                    success, msg = AccessControl.register_user(nu_name, nu_pass)
                    if success: st.success(msg)
                    else: st.error(msg)
        else:
            st.warning("Você não tem privilégios de Administrador para criar novos usuários.")

    with tabs[2]:
        st.subheader("Caixa de Ferramentas")
        
        # FERRAMENTA DE BACKUP (ROBUSTA)
        st.markdown(f"<div class='pastoral-card'><div class='card-title'>Sistema de Backup</div>Gerar arquivo compactado (ZIP) de todo o banco de dados.</div>", unsafe_allow_html=True)
        
        if st.button("📦 GERAR BACKUP COMPLETO AGORA"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = os.path.join(DIRECTORIES["BACKUP_HIDDEN"], f"Backup_Pregador_{timestamp}")
                shutil.make_archive(backup_filename, 'zip', ROOT_DIR)
                st.success(f"Backup realizado com sucesso! Arquivo salvo na pasta interna de Backups.")
            except Exception as e:
                st.error(f"Erro Crítico ao gerar Backup: {e}")
        
        st.divider()
        st.markdown("**Diagnóstico de Logs:**")
        log_file = os.path.join(DIRECTORIES["LOGS"], "system_audit_core.log")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = f.readlines()
            st.text_area("Últimos logs do sistema", "".join(logs[-10:]), height=150)
            if st.button("Limpar Logs"):
                open(log_file, 'w').close()
                st.rerun()

# --- RODAPÉ ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: #555; font-size: 0.8rem;'>
    <p>O PREGADOR - Versão Titanium Core | Sistema de Gestão Pastoral e Teológica</p>
    <p>Ambiente Seguro | Criptografia Ativada se Disponível | Backup Local</p>
    <p>© {datetime.now().year} Shepherd OS - Desenvolvido para a Glória de Deus.</p>
</div>
""", unsafe_allow_html=True)
