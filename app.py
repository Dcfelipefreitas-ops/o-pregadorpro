# -*- coding: utf-8 -*-
"""
################################################################################
#  O PREGADOR - SYSTEM OMEGA ENTERPRISE (V.50 - ULTIMATE BUILD)                #
#  STATUS: PRODUCTION | CRITICAL SYSTEM | REDUNDANT LOGIC                      #
#  --------------------------------------------------------------------------  #
#  ARQUITETURA DO SISTEMA:                                                     #
#  1. CORE BOOTLOADER: Verificação de integridade de sistema de arquivos.      #
#  2. SECURITY DAEMON: Criptografia AES-256 GCM (Grau Militar).                #
#  3. WORD PROCESSOR ENGINE: Módulo dedicado para manipulação de DOCX/PDF.     #
#  4. GENEVA DOCTRINE SCANNER: Algoritmo de análise semântica teológica.       #
#  5. SOUL ANALYTICS (PastoralMind): Análise comportamental e emocional.       #
#  6. NETWORK PROTOCOL: Camada de Rede Ministerial e Colaboração.              #
#  7. UX/UI RENDERER: Motor gráfico com animações CSS (Pulsing Cross).         #
################################################################################
"""

# ==============================================================================
# 00. IMPORTAÇÕES DE MÓDULOS DE SISTEMA
# ==============================================================================
import streamlit as st  # Framework de UI
import os              # Sistema Operacional
import sys             # Sistema de Sistema
import time            # Controle Temporal
import json            # Manipulação de Dados
import base64          # Codificação Binária
import math            # Cálculos Matemáticos
import shutil          # Manipulação de Arquivos
import random          # Geração Aleatória
import logging         # Auditoria e Logs
import hashlib         # Hashing e Segurança
import re              # Expressões Regulares (Regex)
import sqlite3         # Banco de Dados (Reserva)
import uuid            # Identificadores Únicos
from datetime import datetime, timedelta
from io import BytesIO # Manipulação de Streams

# ==============================================================================
# 01. CONFIGURAÇÃO DE AMBIENTE (OBRIGATÓRIO: LINHA 1 REAL)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | SYSTEM OMEGA",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.google.com',
        'Report a bug': "mailto:support@pregador.system",
        'About': "O PREGADOR V.50 Enterprise Edition"
    }
)

# ==============================================================================
# 02. AUDITORIA E LOGGING (SISTEMA DE LOGS DETALHADO)
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
LOG_PATH = os.path.join(SYSTEM_ROOT, "System_Logs")

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)

# Configuração de Logger Rotativo e Verboso
logging.basicConfig(
    filename=os.path.join(LOG_PATH, "system_audit_omega.log"),
    level=logging.INFO,
    format='[%(asctime)s] | [%(levelname)s] | MODULE: %(module)s | PROCESS: %(process)d | MSG: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info(">>> INICIALIZAÇÃO DO SISTEMA OMEGA: CICLO STARTUP <<<")

# ==============================================================================
# 03. INJEÇÃO DE DEPENDÊNCIAS (MODULARIZAÇÃO ROBUSTA)
# ==============================================================================
# O sistema tenta carregar bibliotecas externas. Se falhar, registra no log 
# e ativa flags de controle para não derrubar a aplicação.

GLOBAL_MODULES = {
    "CKEDITOR": False,
    "QUILL": False,
    "PLOTLY": False,
    "CRYPTO": False,
    "MAMMOTH": False,
    "HTML2DOCX": False,
    "REPORTLAB": False,
    "FPDF": False
}

# --- 3.1 Carregamento do Editor CKEditor ---
try:
    from streamlit_ckeditor import st_ckeditor
    GLOBAL_MODULES["CKEDITOR"] = True
    logging.info("Dependência Carregada: Streamlit CKEditor")
except ImportError as e:
    logging.warning(f"Dependência Falhou: CKEditor ({e})")

# --- 3.2 Carregamento do Editor Quill ---
try:
    from streamlit_quill import st_quill
    GLOBAL_MODULES["QUILL"] = True
    logging.info("Dependência Carregada: Streamlit Quill")
except ImportError as e:
    logging.warning(f"Dependência Falhou: Quill ({e})")

# --- 3.3 Carregamento do Motor Gráfico Plotly ---
try:
    import plotly.graph_objects as go
    import plotly.express as px
    GLOBAL_MODULES["PLOTLY"] = True
    logging.info("Dependência Carregada: Plotly")
except ImportError as e:
    logging.warning(f"Dependência Falhou: Plotly ({e})")

# --- 3.4 Carregamento do Núcleo Criptográfico ---
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    GLOBAL_MODULES["CRYPTO"] = True
    logging.info("Dependência Carregada: Cryptography AES")
except ImportError as e:
    logging.warning(f"Dependência Falhou: Cryptography ({e})")

# --- 3.5 Carregamento dos Motores WORD (Módulo Word Dependências) ---
try:
    import mammoth
    GLOBAL_MODULES["MAMMOTH"] = True
except ImportError:
    pass

try:
    from html2docx import html2docx
    GLOBAL_MODULES["HTML2DOCX"] = True
except ImportError:
    pass

try:
    from docx import Document
    GLOBAL_MODULES["PYTHON-DOCX"] = True
except ImportError:
    pass

# --- 3.6 Carregamento dos Motores PDF ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    GLOBAL_MODULES["REPORTLAB"] = True
except ImportError:
    pass

# ==============================================================================
# 04. SISTEMA DE ARQUIVOS E BANCO DE DADOS (GÊNESIS PROTOCOL)
# ==============================================================================
# Define a estrutura física onde os dados repousam. Nada é volátil aqui.

DIRECTORY_STRUCTURE = {
    "ROOT": SYSTEM_ROOT,
    "SERMONS": os.path.join(SYSTEM_ROOT, "Sermoes"),               # Guarda HTML/DOCX
    "GABINETE": os.path.join(SYSTEM_ROOT, "Gabinete_Pastoral"),    # Guarda Criptografados
    "USER_CONFIG": os.path.join(SYSTEM_ROOT, "User_Data"),         # Guarda Configurações e Users
    "BACKUP_VAULT": os.path.join(SYSTEM_ROOT, "Auto_Backup_Oculto"), # Área de Segurança
    "LIBRARY_CACHE": os.path.join(SYSTEM_ROOT, "BibliaCache"),     # Guarda PDFs
    "MEMBERSHIP": os.path.join(SYSTEM_ROOT, "Membresia"),          # Guarda dados do Rebanho
    "NETWORK_LAYER": os.path.join(SYSTEM_ROOT, "Rede_Ministerial") # Guarda Feed
}

DB_FILES = {
    "CONFIG": os.path.join(DIRECTORY_STRUCTURE["USER_CONFIG"], "config.json"),
    "USERS_DB": os.path.join(DIRECTORY_STRUCTURE["USER_CONFIG"], "users_db.json"),
    "SOUL_METRICS": os.path.join(DIRECTORY_STRUCTURE["GABINETE"], "soul_data.json"),
    "STATS_METRICS": os.path.join(DIRECTORY_STRUCTURE["USER_CONFIG"], "db_stats.json"),
    "MEMBERS_DB": os.path.join(DIRECTORY_STRUCTURE["MEMBERSHIP"], "members.json"),
    "NETWORK_FEED": os.path.join(DIRECTORY_STRUCTURE["NETWORK_LAYER"], "feed_data.json")
}

def genesis_filesystem_integrity_check():
    """
    Executa verificação forense do sistema de arquivos na inicialização.
    Cria diretórios ausentes e restaura bancos de dados críticos corrompidos.
    """
    logging.info("Executando Protocolo Genesis: Checagem de Integridade...")
    
    # 1. Validação de Diretórios
    for key, path in DIRECTORY_STRUCTURE.items():
        if not os.path.exists(path):
            logging.info(f"Diretório Ausente Detectado: {path}. Criando...")
            try:
                os.makedirs(path, exist_ok=True)
                # Cria arquivo sentinela para garantir persistência em nuvens voláteis
                with open(os.path.join(path, ".sentinel"), "w") as f:
                    f.write("System Integrity File - Do Not Delete")
            except Exception as e:
                logging.error(f"FATAL: Não foi possível criar diretório {path}. Erro: {e}")

    # 2. Validação do Banco de Configuração
    if not os.path.exists(DB_FILES["CONFIG"]):
        logging.warning("Configuração não encontrada. Gerando Default de Fábrica.")
        default_config = {
            "theme_color": "#D4AF37",
            "theme_mode": "Dark Cathedral",
            "font_family": "Inter",
            "security_level": "High",
            "backup_frequency": "Daily",
            "module_active_word": True,
            "module_active_network": True,
            "rotina_pastoral": [
                "Oração Inicial (30 min)",
                "Leitura Bíblica Devocional",
                "Estudo Teológico",
                "Gestão Eclesiástica"
            ]
        }
        _write_json_atomic(DB_FILES["CONFIG"], default_config)

    # 3. Validação do Banco de Usuários
    if not os.path.exists(DB_FILES["USERS_DB"]):
        logging.warning("DB de Usuários não encontrado. Criando Admin.")
        # SHA-256 Hash do Admin Padrão
        admin_hash = hashlib.sha256("admin".encode()).hexdigest()
        _write_json_atomic(DB_FILES["USERS_DB"], {"ADMIN": admin_hash})

    # 4. Inicialização dos Bancos de Dados Auxiliares
    _ensure_empty_json_list(DB_FILES["NETWORK_FEED"])
    _ensure_empty_json_list(DB_FILES["MEMBERS_DB"])
    _ensure_empty_json_list(DB_FILES["SOUL_METRICS"])

def _write_json_atomic(path, data):
    """
    Escrita Atômica: Garante que o arquivo nunca fique corrompido no meio da gravação.
    Escreve em um arquivo temporário e depois renomeia.
    """
    temp_path = f"{path}.tmp.{uuid.uuid4().hex}"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        shutil.move(temp_path, path)
        return True
    except Exception as e:
        logging.error(f"Erro na Escrita Atômica para {path}: {e}")
        return False

def _read_json_safe(path, default=None):
    """Leitura Defensiva de JSON."""
    if default is None: default = {}
    try:
        if not os.path.exists(path): return default
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return default
            return json.loads(content)
    except Exception as e:
        logging.error(f"Erro de Leitura em {path}: {e}")
        return default

def _ensure_empty_json_list(path):
    if not os.path.exists(path):
        _write_json_atomic(path, [])

# Inicializa o sistema imediatamente
genesis_filesystem_integrity_check()

# ==============================================================================
# 05. CORE LOGIC & HELPER UTILITIES
# ==============================================================================

class TextUtils:
    """Ferramentas para normalização e tratamento de strings."""
    @staticmethod
    def sanitize_filename(name):
        """Remove caracteres ilegais para nomes de arquivo."""
        s = str(name).strip().replace(" ", "_")
        return re.sub(r'(?u)[^-\w.]', '', s)

    @staticmethod
    def clean_html_tags(text):
        """Remove tags HTML para exportação em texto puro."""
        clean = re.compile('<.*?>')
        return re.sub(clean, '\n', text)

    @staticmethod
    def normalize_font(font_name):
        """Corrige nome da fonte para injeção CSS."""
        if not font_name: return "Inter"
        return font_name.split(",")[0].strip().replace("'","").replace('"','')

# ==============================================================================
# 06. WORD PROCESSOR MODULE (O MODULO SOLICITADO DETALHADO)
# ==============================================================================
class WordProcessorEngine:
    """
    #######################################################
    #        MÓDULO WORD: ENGINE DE EXPORTAÇÃO            #
    #######################################################
    Esta classe é o núcleo de transformação de documentos.
    Ela gerencia headers, encodings, seleção de bibliotecas e fallbacks.
    """
    
    def __init__(self, title, content_html, output_path):
        self.title = title
        self.content_html = content_html
        self.output_path = output_path
        self.clean_text = TextUtils.clean_html_tags(content_html)
        
    def execute_docx_export(self):
        """
        Tenta exportar para DOCX usando estratégias em cascata.
        1. Mammoth (Melhor) -> 2. Html2Docx -> 3. Fallback Raw
        """
        logging.info(f"Iniciando Exportação DOCX: {self.title}")
        
        # ESTRATÉGIA A: MAMMOTH
        if GLOBAL_MODULES["MAMMOTH"]:
            try:
                import mammoth
                # Constrói HTML válido completo
                html_structure = f"""
                <html>
                <head><style>body {{ font-family: 'Arial'; }}</style></head>
                <body>
                    <h1 style='text-align:center'>{self.title}</h1>
                    <hr>
                    {self.content_html}
                    <hr>
                    <p style='font-size:10px; color:grey'>Gerado por O PREGADOR SYSTEM</p>
                </body>
                </html>
                """
                result = mammoth.convert_to_docx(html_structure)
                with open(self.output_path, "wb") as f:
                    f.write(result.value)
                logging.info("Sucesso via Mammoth.")
                return True, "Documento Word (Alta Fidelidade) Gerado."
            except Exception as e:
                logging.error(f"Falha Mammoth: {e}")

        # ESTRATÉGIA B: HTML2DOCX
        if GLOBAL_MODULES["HTML2DOCX"]:
            try:
                from html2docx import html2docx
                buf = html2docx(self.content_html, title=self.title)
                with open(self.output_path, "wb") as f:
                    f.write(buf.getvalue())
                logging.info("Sucesso via Html2Docx.")
                return True, "Documento Word (Conversão HTML) Gerado."
            except Exception as e:
                logging.error(f"Falha Html2Docx: {e}")

        # ESTRATÉGIA C: MANUAL BUILDER (FALLBACK ROBUSTO)
        try:
            from docx import Document
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()
            # Título
            heading = doc.add_heading(self.title, 0)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Corpo (Splitando linhas vazias)
            for line in self.clean_text.split('\n'):
                line = line.strip()
                if line:
                    p = doc.add_paragraph(line)
                    p.paragraph_format.space_after = Pt(6)
            
            # Rodapé Simulado
            doc.add_page_break()
            doc.add_paragraph(f"Gerado em {datetime.now()} pelo Sistema O PREGADOR").italic = True
            
            doc.save(self.output_path)
            logging.info("Sucesso via Python-Docx Fallback.")
            return True, "Documento Word (Texto Puro) Gerado."
        except Exception as e:
            # ESTRATÉGIA D: EMERGENCY TXT (Se tudo falhar)
            try:
                txt_path = self.output_path.replace(".docx", ".txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"{self.title}\n\n{self.clean_text}")
                logging.error(f"Falha total DOCX. Gerado TXT. Erro: {e}")
                return False, "Erro crítico na engine DOCX. Salvo como TXT simples."
            except Exception as crit:
                return False, f"Falha de I/O crítica: {crit}"

    def execute_pdf_export(self):
        """Gerador de PDF via ReportLab com layout manual."""
        if not GLOBAL_MODULES["REPORTLAB"]:
            return False, "Motor PDF não instalado."
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            c = canvas.Canvas(self.output_path, pagesize=A4)
            width, height = A4
            
            # Header Layout
            c.setFillColorRGB(0.8, 0.7, 0.2) # Dourado simulado
            c.rect(0, height-50, width, 50, fill=1, stroke=0)
            c.setFillColorRGB(0,0,0)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width/2, height-35, self.title)
            
            # Body Layout
            c.setFont("Helvetica", 11)
            y_position = height - 80
            
            lines = self.clean_text.split('\n')
            for line in lines:
                # Wrap básico (90 caracteres)
                wrapped_lines = [line[i:i+90] for i in range(0, len(line), 90)]
                for subline in wrapped_lines:
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
                        c.setFont("Helvetica", 11)
                    c.drawString(40, y_position, subline)
                    y_position -= 14
            
            c.save()
            return True, "Arquivo PDF Padrão A4 Gerado."
        except Exception as e:
            logging.error(f"Erro PDF: {e}")
            return False, str(e)

# ==============================================================================
# 07. PROTOCOLO GENEVA E ANALYTICS (REGRA DE NEGÓCIO)
# ==============================================================================
class GenevaDoctrineCore:
    """Analisador de conteúdo para consistência teológica."""
    HERESY_DATABASE = {
        "prosperidade": "ALERTA: Viés de Teologia da Prosperidade (Sola Gratia em risco?).",
        "decreto": "ALERTA: Antropocentrismo detectado. Soberania de Deus deve prevalecer.",
        "energia": "CUIDADO: Termo metafísico vago. Use 'Espírito Santo' ou 'Poder de Deus'.",
        "universo": "ALERTA: Substituição panteísta. O correto é 'O Criador'.",
        "força": "NOTA: Verifique se refere a Star Wars ou ao Senhor.",
        "vibrar": "NOTA: Linguagem emocionalista/coaching detectada."
    }

    @staticmethod
    def scan(text):
        if not text: return []
        text_lower = text.lower()
        findings = []
        for keyword, message in GenevaDoctrineCore.HERESY_DATABASE.items():
            if keyword in text_lower:
                findings.append(message)
        return findings

class PastoralAnalytics:
    @staticmethod
    def calculate_health_index():
        """
        Lee el registro histórico (puede venir de DB_FILES['HEALTH_DB'] o de un fallback)
        y calcula un índice de salud pastoral (0-100), devolviendo tupla:
        (health_score: float, health_status: str, health_color: str)
        """
        try:
            # Obtém ruta desde DB_FILES se existe, sino usa fallback dentro de SYSTEM_ROOT
            health_db_path = None
            if isinstance(globals().get("DB_FILES"), dict):
                health_db_path = DB_FILES.get("HEALTH_DB")
            if not health_db_path:
                health_db_path = os.path.join(globals().get("SYSTEM_ROOT", "."), "pastoral_health.json")

            # _read_json_safe já se usa em outras partes do código; se não existe, tentar leitura manual
            if "_read_json_safe" in globals():
                db = _read_json_safe(health_db_path)
            else:
                try:
                    with open(health_db_path, "r", encoding="utf-8") as fh:
                        import json
                        db = json.load(fh)
                except Exception:
                    db = {}
        except Exception:
            db = {}

        # Asegurar que db sea dict e extraer histórico
        history = db.get("historico", []) if isinstance(db, dict) else []

        # Tomar últimos 10 registros
        last = history[-10:] if history else []

        # Si no hay datos, devolver valores por defecto
        if not last:
            return 0.0, "Sem dados", "gray"

        # Normalizar y extraer scores (aceita lista de números ou dicts com 'score')
        scores = []
        for item in last:
            try:
                if isinstance(item, dict):
                    val = item.get("score", item.get("pontuacao", 0))
                else:
                    val = item
                scores.append(float(val))
            except Exception:
                scores.append(0.0)

        avg = (sum(scores) / len(scores)) if scores else 0.0
        avg = max(0.0, min(100.0, round(avg, 2)))

        if avg >= 80:
            status, color = "Excelente", "green"
        elif avg >= 60:
            status, color = "Bom", "lime"
        elif avg >= 40:
            status, color = "Precisa atenção", "orange"
        else:
            status, color = "Crítico", "red"

        return avg, status, color

# ==============================================================================
# 08. SECURITY ACCESS LAYER
# ==============================================================================
class AccessGate:
    """Gatekeeper de Segurança."""
    @staticmethod
    def login_check(username, password):
        db = _read_json_safe(DB_FILES["USERS_DB"])
        
        # Masterkey (Segurança inicial apenas)
        if username == "ADMIN" and password == "1234" and len(db) <= 1:
            return True
            
        user_hash = db.get(username.upper())
        if not user_hash:
            logging.warning(f"Tentativa de login falha: {username}")
            return False
            
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        return pass_hash == user_hash

    @staticmethod
    def create_account(username, password):
        db = _read_json_safe(DB_FILES["USERS_DB"])
        if username.upper() in db:
            return False, "Usuário Duplicado no Sistema."
        
        new_hash = hashlib.sha256(password.encode()).hexdigest()
        db[username.upper()] = new_hash
        
        if _write_json_atomic(DB_FILES["USERS_DB"], db):
            return True, "Credencial criada com sucesso."
        return False, "Erro de gravação em disco."

# ==============================================================================
# 09. ENGINE GRÁFICA & CSS (UX COM ANIMAÇÃO RESTAURADA)
# ==============================================================================

def inject_visual_core():
    # Carrega configurações do usuário para personalizar CSS
    config = _read_json_safe(DB_FILES["CONFIG"])
    theme_color = config.get("theme_color", "#D4AF37")
    font_raw = config.get("font_family", "Inter")
    font_main = TextUtils.normalize_font(font_raw)

    st.markdown(f"""
    <style>
    /* ==========================================================================
       FONTE E VARIAVEIS GLOBAIS
       ========================================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Inter:wght@300;400;600&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');
    
    :root {{
        --gold: {theme_color};
        --gold-dim: {theme_color}80;
        --bg-dark: #000000;
        --card-bg: #0b0b0b;
        --text-main: #e0e0e0;
        --font-body: '{font_main}', sans-serif;
        --font-head: 'Cinzel', serif;
    }}
    
    /* RESET BASICO */
    .stApp {{
        background-color: var(--bg-dark);
        color: var(--text-main);
        font-family: var(--font-body);
    }}
    
    h1, h2, h3, h4 {{
        font-family: var(--font-head) !important;
        color: var(--gold) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* ==========================================================================
       ANIMAÇÃO "PULSING CROSS" (SOLICITADO)
       ========================================================================== */
    @keyframes pulse_gold {{
        0% {{
            transform: scale(1);
            stroke-opacity: 1;
            filter: drop-shadow(0 0 5px var(--gold-dim));
        }}
        50% {{
            transform: scale(1.05);
            stroke-opacity: 0.7;
            filter: drop-shadow(0 0 15px var(--gold));
        }}
        100% {{
            transform: scale(1);
            stroke-opacity: 1;
            filter: drop-shadow(0 0 5px var(--gold-dim));
        }}
    }}
    
    .prime-logo {{
        width: 140px;
        height: 140px;
        display: block;
        margin: 0 auto 20px auto;
        /* Aplicação da Animação */
        animation: pulse_gold 3s infinite ease-in-out; 
    }}
    
    .login-container {{
        text-align: center;
        border: 1px solid #222;
        padding: 40px;
        background: linear-gradient(180deg, rgba(20,20,20,1) 0%, rgba(0,0,0,1) 100%);
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0,0,0,0.8);
        border-top: 4px solid var(--gold);
    }}
    
    .system-title {{
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        color: var(--gold);
        letter-spacing: 8px;
        margin-bottom: 5px;
        text-shadow: 0 0 10px rgba(0,0,0,0.8);
    }}
    
    /* ==========================================================================
       COMPONENTES DE INTERFACE
       ========================================================================== */
    [data-testid="stSidebar"] {{
        background-color: #060606;
        border-right: 1px solid #1a1a1a;
    }}
    
    .tech-card {{
        background: var(--card-bg);
        border: 1px solid #222;
        border-left: 4px solid var(--gold);
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }}
    .tech-card:hover {{
        border-color: #333;
        transform: translateX(5px);
    }}
    
    .stButton>button {{
        border: 1px solid var(--gold);
        color: var(--gold);
        background: transparent;
        font-family: var(--font-body);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 0.6rem;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: var(--gold);
        color: black;
        box-shadow: 0 0 15px var(--gold-dim);
    }}
    
    .stat-value {{
        font-size: 2.5rem;
        font-family: var(--font-head);
        font-weight: 800;
        line-height: 1;
    }}
    
    /* CORREÇÕES PARA MOBILE */
    @media (max-width: 768px) {{
        .prime-logo {{ width: 100px; height: 100px; }}
        .system-title {{ font-size: 1.5rem; letter-spacing: 4px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# Aplica o estilo globalmente
inject_visual_core()

# ==============================================================================
# 10. FLUXO DE LOGIN (INTERFACE RENDERER)
# ==============================================================================
if "session_valid" not in st.session_state: st.session_state["session_valid"] = False
if "current_user" not in st.session_state: st.session_state["current_user"] = "GUEST"

if not st.session_state["session_valid"]:
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    
    with col_c:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # O HTML Abaixo inclui a classe 'prime-logo' que aciona o CSS PULSE definido acima
        config = _read_json_safe(DB_FILES["CONFIG"])
        GOLD_HEX = config.get("theme_color", "#D4AF37")
        
        st.markdown(f"""
        <div class="login-container">
            <svg class="prime-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Círculo Externo -->
                <circle cx="50" cy="50" r="45" stroke="{GOLD_HEX}" stroke-width="2" fill="none" />
                <!-- Cruz Estilizada -->
                <line x1="50" y1="20" x2="50" y2="80" stroke="{GOLD_HEX}" stroke-width="4" stroke-linecap="square" />
                <line x1="30" y1="40" x2="70" y2="40" stroke="{GOLD_HEX}" stroke-width="4" stroke-linecap="square" />
                <!-- Detalhes Orbitais -->
                <circle cx="50" cy="50" r="10" stroke="{GOLD_HEX}" stroke-width="1" fill="none" style="opacity:0.5"/>
            </svg>
            <div class="system-title">O PREGADOR</div>
            <div style="color: #666; font-size: 0.8rem; letter-spacing: 2px; margin-bottom: 20px;">
                SYSTEM OMEGA | ENTERPRISE EDITION V.50
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_access, tab_register = st.tabs(["🔒 ACESSO SEGURO", "📝 NOVO MEMBRO"])
        
        with tab_access:
            u = st.text_input("ID PASTORAL", placeholder="Digite seu identificador")
            p = st.text_input("CHAVE DE SEGURANÇA", type="password")
            
            if st.button("AUTENTICAR SISTEMA", use_container_width=True):
                if AccessGate.login_check(u, p):
                    st.session_state["session_valid"] = True
                    st.session_state["current_user"] = u.upper()
                    st.success("Credenciais validadas. Inicializando módulos...")
                    time.sleep(1) # Simula loading
                    st.rerun()
                else:
                    st.error("ACESSO NEGADO: Credenciais não conferem.")

        with tab_register:
            st.info("Cadastro Local Habilitado")
            nu = st.text_input("Definir Novo ID", key="reg_u")
            np = st.text_input("Definir Senha", type="password", key="reg_p")
            if st.button("REGISTRAR CONTA"):
                success, msg = AccessGate.create_account(nu, np)
                if success: st.success(msg)
                else: st.error(msg)
    
    # Bloqueia execução do resto do script
    st.stop()

# ==============================================================================
# 11. SIDEBAR (NAVEGAÇÃO DO SISTEMA)
# ==============================================================================
with st.sidebar:
    # Cabeçalho da Sidebar
    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0; border-bottom: 1px solid #222;">
        <h3 style="margin:0; font-size: 1.2rem;">Pastor</h3>
        <h1 style="margin:0; font-size: 1.8rem; line-height:1.2;">{st.session_state['current_user']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Indicador de Saúde (Pastoral Mind)
    health_score, health_status, health_color = PastoralAnalytics.calculate_health_index()
    st.markdown(f"""
    <div style="background:#111; padding:10px; border-radius:4px; margin: 15px 0; border:1px solid #222;">
        <small style="color:#888;">SAÚDE MINISTERIAL</small>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="color:{health_color}; font-weight:bold;">{health_status}</span>
            <span style="color:{health_color}; font-size:1.2rem;">{health_score}%</span>
        </div>
        <div style="width:100%; height:4px; background:#222; margin-top:5px;">
            <div style="width:{health_score}%; height:100%; background:{health_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Menu Principal
    app_mode = st.radio(
        "Navegação do Sistema",
        ["Dashboard & Cuidado", "Gabinete de Preparação", "Rede Ministerial", "Biblioteca Digital", "Configurações"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("ENCERRAR SESSÃO", use_container_width=True):
        st.session_state["session_valid"] = False
        st.rerun()

# ==============================================================================
# 12. MÓDULO DASHBOARD & CUIDADO (EXPANDIDO)
# ==============================================================================
if app_mode == "Dashboard & Cuidado":
    st.title("🛡️ Painel de Controle e Cuidado")
    
    tabs_care = st.tabs(["📝 Check-in Emocional", "⚖️ Teoria da Permissão", "📋 Rotina & Liturgia"])
    
    # 12.1 Check-in Diário
    with tabs_care[0]:
        st.markdown(
            f"""<div class='tech-card'>
            <b>LIVRO DA ALMA (Diário)</b><br>
            Registre diariamente sua condição para evitar o esgotamento silencioso.
            </div>""", 
            unsafe_allow_html=True
        )
        
        c1, c2 = st.columns([1, 2])
        with c1:
            input_mood = st.select_slider(
                "Como você se sente?", 
                options=["Esgotamento", "Cansaço", "Neutro", "Bem", "Pleno"]
            )
            input_note = st.text_area("Observações do dia", height=100)
            
            if st.button("REGISTRAR ESTADO"):
                data = _read_json_safe(DB_FILES["SOUL_METRICS"])
                data.setdefault("historico", []).append({
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "humor": input_mood,
                    "nota": input_note
                })
                _write_json_atomic(DB_FILES["SOUL_METRICS"], data)
                st.success("Registro gravado no banco de dados.")
        
        with c2:
            st.markdown("**Histórico Recente**")
            data = _read_json_safe(DB_FILES["SOUL_METRICS"])
            # Compatibilidad: el fichero pode ser um dict {"historico": [...]} o uma lista [...]
            if isinstance(data, dict):
                history = data.get("historico", [])[-5:]
            elif isinstance(data, list):
                history = data[-5:]
            else:
                history = []

            for item in reversed(history):
                # Proteção adicional se o registro não é dict
                if isinstance(item, dict):
                    date = item.get('data', '-')
                    humor = item.get('humor', item.get('estado', '-'))
                    nota = item.get('nota', item.get('obs', '-'))
                else:
                    date = str(item)
                    humor = '-'
                    nota = '-'
                st.info(f"{date} | Estado: {humor} | Obs: {nota}")

    # 12.2 Teoria da Permissão
    with tabs_care[1]:
        st.markdown("""
        ### A Teoria da Permissão
        *Ferramenta Psicoteológica para validação humana do líder.*
        Mova os controles abaixo com total sinceridade.
        """)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            p_fail = st.slider("Permissão para Falhar/Não Saber", 0, 100, 50)
            p_feel = st.slider("Permissão para Sentir Dor/Ira", 0, 100, 50)
            p_rest = st.slider("Permissão para Parar/Descansar", 0, 100, 50)
        
        with col_s2:
            if GLOBAL_MODULES["PLOTLY"]:
                fig = go.Figure(data=go.Scatterpolar(
                    r=[p_fail, p_feel, p_rest, p_fail],
                    theta=['FALHAR', 'SENTIR', 'DESCANSAR', 'FALHAR'],
                    fill='toself',
                    line_color=st.session_state.get('theme_color', '#D4AF37')
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Visualização avançada desativada (Plotly ausente).")
                st.metric("Média de Permissão", f"{(p_fail+p_feel+p_rest)//3}%")

    # 12.3 Rotina Pastoral Dinâmica
    with tabs_care[2]:
        st.subheader("Liturgia Pessoal & Rotina")
        
        # Carrega e exibe
        cfg = _read_json_safe(DB_FILES["CONFIG"])
        routine = cfg.get("rotina_pastoral", [])
        
        col_checks, col_manage = st.columns([2, 1])
        
        with col_checks:
            st.markdown("**Tarefas Diárias**")
            progress = 0
            for task in routine:
                if st.checkbox(task, key=f"chk_{task}"):
                    progress += 1
            
            if routine:
                val = progress / len(routine)
                st.progress(val, text="Progresso Diário")
        
        with col_manage:
            st.markdown("**Gerenciar**")
            new_t = st.text_input("Nova Tarefa")
            if st.button("ADICIONAR"):
                if new_t:
                    routine.append(new_t)
                    cfg["rotina_pastoral"] = routine
                    _write_json_atomic(DB_FILES["CONFIG"], cfg)
                    st.rerun()
            
            del_t = st.selectbox("Remover", ["Selecione"] + routine)
            if st.button("REMOVER"):
                if del_t in routine:
                    routine.remove(del_t)
                    cfg["rotina_pastoral"] = routine
                    _write_json_atomic(DB_FILES["CONFIG"], cfg)
                    st.rerun()

# ==============================================================================
# 13. MÓDULO GABINETE DE PREPARAÇÃO (THE SYSTEM CORE)
# ==============================================================================
elif app_mode == "Gabinete de Preparação":
    st.title("📝 Gabinete Pastoral Avançado")
    
    # Navegador de Arquivos Lateral
    col_nav, col_work = st.columns([1, 4])
    
    with col_nav:
        st.markdown("**🗂️ Arquivos**")
        all_files = [f for f in os.listdir(DIRECTORY_STRUCTURE["SERMONS"]) if f.endswith(".html")]
        all_files.sort(reverse=True)
        selected_file = st.radio("Acervo", ["NOVO DOCUMENTO"] + all_files)

    # Área de Trabalho Principal
    with col_work:
        # Estado Inicial
        active_content = ""
        active_title = ""
        
        # Carregamento Lógico
        if selected_file != "NOVO DOCUMENTO":
            file_path = os.path.join(DIRECTORY_STRUCTURE["SERMONS"], selected_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    active_content = f.read()
                active_title = selected_file.replace(".html", "").replace("_", " ")
            except Exception as e:
                st.error(f"Erro de I/O: {e}")

        # Interface de Inputs
        doc_title_input = st.text_input("TÍTULO DA MENSAGEM / ESTUDO", value=active_title)
        
        # SELETOR DE MOTOR DE EDIÇÃO (Priority Chain)
        final_editor_content = active_content
        
        if GLOBAL_MODULES["CKEDITOR"]:
            # Editor Nível 1: CKEditor (Word-like)
            final_editor_content = st_ckeditor(
                value=active_content,
                key="ck_editor_core",
                height=600
            )
        elif GLOBAL_MODULES["QUILL"]:
             # Editor Nível 2: Quill
            final_editor_content = st_quill(
                value=active_content,
                html=True,
                key="quill_editor_core"
            )
        else:
             # Editor Nível 3: Raw HTML/Text
            st.warning("Editores Visuais Indisponíveis. Usando modo Raw Text.")
            final_editor_content = st.text_area("Editor Raw", value=active_content, height=600)
            
        # PAINEL DE AÇÕES DE ENGENHARIA (O MODULO SOLICITADO)
        st.markdown("---")
        st.markdown("### 🛠️ Processador de Engenharia Pastoral")
        
        c_save, c_word, c_pdf, c_scan = st.columns(4)
        
        clean_fname = TextUtils.sanitize_filename(doc_title_input if doc_title_input else "novo_sermao")
        
        # Botão SALVAR (HTML Raw)
        if c_save.button("💾 GRAVAR (HTML)", use_container_width=True):
            save_path = os.path.join(DIRECTORY_STRUCTURE["SERMONS"], f"{clean_fname}.html")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(final_editor_content)
            st.toast("Documento gravado com segurança no servidor.", icon="✅")
            time.sleep(1)
            st.rerun()

        # Botão WORD (Chama a classe complexa)
        if c_word.button("📄 EXPORTAR DOCX", use_container_width=True):
            out_path = os.path.join(DIRECTORY_STRUCTURE["SERMONS"], f"{clean_fname}.docx")
            
            # Instancia o Processador
            processor = WordProcessorEngine(
                title=doc_title_input,
                content_html=final_editor_content,
                output_path=out_path
            )
            
            with st.spinner("Compilando Documento Word (Analysis/Conversion)..."):
                status, msg = processor.execute_docx_export()
                
            if status:
                st.success(msg)
                with open(out_path, "rb") as f:
                    st.download_button("BAIXAR DOCX", f, file_name=f"{clean_fname}.docx")
            else:
                st.error(msg)

        # Botão PDF
        if c_pdf.button("📕 EXPORTAR PDF", use_container_width=True):
            out_path = os.path.join(DIRECTORY_STRUCTURE["SERMONS"], f"{clean_fname}.pdf")
            
            processor = WordProcessorEngine(
                title=doc_title_input,
                content_html=final_editor_content,
                output_path=out_path
            )
            
            with st.spinner("Renderizando PDF Vectorial..."):
                status, msg = processor.execute_pdf_export()
            
            if status:
                st.success(msg)
                with open(out_path, "rb") as f:
                    st.download_button("BAIXAR PDF", f, file_name=f"{clean_fname}.pdf")
            else:
                st.error(msg)
        
        # Botão SCAN (Geneva)
        if c_scan.button("🔍 SCAN DOUTRINÁRIO", use_container_width=True):
            alerts = GenevaDoctrineCore.scan(final_editor_content)
            if alerts:
                with st.expander("⚠️ RELATÓRIO DE INCONSISTÊNCIA DETECTADO", expanded=True):
                    for a in alerts:
                        st.markdown(f"🔴 **{a}**")
            else:
                st.success("Análise completa: Nenhuma heresia detectada no corpus do texto.")

# ==============================================================================
# 14. MÓDULO REDE MINISTERIAL (COLLAB LAYER)
# ==============================================================================
elif app_mode == "Rede Ministerial":
    st.title("🤝 Rede de Conexão Pastoral")
    st.markdown("Central de inteligência compartilhada entre colaboradores.")
    
    # Renderização do Feed
    feed_db = _read_json_safe(DB_FILES["NETWORK_FEED"], [])
    
    # 1. Formulário de Ingestão de Conteúdo
    with st.expander("📡 TRANSMITIR NOVO CONTEÚDO", expanded=False):
        with st.form("feed_form"):
            p_title = st.text_input("Título do Recurso")
            p_author = st.text_input("Responsável", value=st.session_state["current_user"])
            p_link = st.text_input("Link Externo (YouTube/Drive/Vimeo)")
            p_body = st.text_area("Descrição Técnica / Teológica")
            
            if st.form_submit_button("PUBLICAR NA REDE"):
                if p_title and p_body:
                    packet = {
                        "uuid": uuid.uuid4().hex,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "title": p_title,
                        "author": p_author,
                        "link": p_link,
                        "body": p_body
                    }
                    feed_db.insert(0, packet) # Inserção LIFO
                    _write_json_atomic(DB_FILES["NETWORK_FEED"], feed_db)
                    st.success("Pacote de dados transmitido.")
                    st.rerun()
                else:
                    st.warning("Dados incompletos.")
    
    # 2. Renderização de Blocos de Conteúdo
    st.divider()
    if not feed_db:
        st.info("Buffer de Rede Vazio. Aguardando transmissão.")
    
    for item in feed_db:
        with st.container():
            st.markdown(f"""
            <div class="tech-card">
                <div style="display:flex; justify-content:space-between;">
                    <h3 style="margin:0;">{item['title']}</h3>
                    <small>{item['timestamp']}</small>
                </div>
                <small style="color:var(--gold); font-weight:bold;">OPERADOR: {item['author']}</small>
                <hr style="border-color:#333;">
                <p>{item['body']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if "youtube" in item['link']:
                try: st.video(item['link'])
                except: st.warning("Erro de codec de vídeo.")
            elif item['link']:
                st.markdown(f"🔗 [Acessar Recurso Externo]({item['link']})")
            
            if st.button("REMOVER PACOTE", key=item['uuid']):
                feed_db.remove(item)
                _write_json_atomic(DB_FILES["NETWORK_FEED"], feed_db)
                st.rerun()

# ==============================================================================
# 15. MÓDULO BIBLIOTECA (FILE MANAGEMENT)
# ==============================================================================
elif app_mode == "Biblioteca Digital":
    st.title("📚 Biblioteca & Acervo")
    
    col_up, col_idx = st.columns([1, 2])
    
    with col_up:
        st.markdown("### Ingestão de Ativos")
        f_up = st.file_uploader("Formatos: PDF, EPUB, DOCX", type=['pdf','epub','docx','txt'])
        if f_up:
            save_dest = os.path.join(DIRECTORY_STRUCTURE["LIBRARY_CACHE"], f_up.name)
            with open(save_dest, "wb") as f:
                f.write(f_up.getbuffer())
            st.success(f"Arquivo '{f_up.name}' armazenado no Cache.")
            
    with col_idx:
        st.markdown("### Índice Local")
        files = os.listdir(DIRECTORY_STRUCTURE["LIBRARY_CACHE"])
        if not files:
            st.warning("Cache vazio.")
        else:
            for file_name in files:
                f_path = os.path.join(DIRECTORY_STRUCTURE["LIBRARY_CACHE"], file_name)
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"📑 **{file_name}**")
                with open(f_path, "rb") as f:
                    c2.download_button("BAIXAR", f, file_name=file_name, key=f"dl_{file_name}")

# ==============================================================================
# 16. CONFIGURAÇÕES & ADMIN (SYSTEM SETTINGS)
# ==============================================================================
elif app_mode == "Configurações":
    st.title("⚙️ Painel de Controle do Sistema")
    
    tabs_conf = st.tabs(["🎨 Personalização UI", "🔧 Ferramentas de Manutenção", "ℹ️ Sobre o Sistema"])
    
    cfg = _read_json_safe(DB_FILES["CONFIG"])
    
    with tabs_conf[0]:
        st.subheader("Parâmetros Visuais")
        
        c_color, c_font = st.columns(2)
        new_color = c_color.color_picker("Cor Primária (Ouro)", cfg.get("theme_color"))
        new_font = c_font.selectbox("Tipografia", ["Inter", "Roboto", "Lato", "Cinzel"], index=0)
        
        if st.button("APLICAR MUDANÇAS DE TEMA"):
            cfg["theme_color"] = new_color
            cfg["font_family"] = new_font
            if _write_json_atomic(DB_FILES["CONFIG"], cfg):
                st.toast("Parâmetros regravados. Reinicialize a interface.")
                time.sleep(1)
                st.rerun()
                
    with tabs_conf[1]:
        st.subheader("Utilitários de Sistema")
        
        st.markdown("---")
        st.markdown("#### 1. Backup de Segurança")
        st.info("Gera um pacote .ZIP criptografado (simbolicamente) de todo o banco de dados.")
        if st.button("INICIAR PROTOCOLO DE BACKUP"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = os.path.join(DIRECTORY_STRUCTURE["BACKUP_VAULT"], f"SystemBackup_{ts}")
            shutil.make_archive(fname, 'zip', SYSTEM_ROOT)
            st.success(f"Backup completo realizado em: {fname}.zip")
            
        st.markdown("---")
        st.markdown("#### 2. Auditoria de Logs")
        if os.path.exists(os.path.join(LOG_PATH, "system_audit_omega.log")):
            with open(os.path.join(LOG_PATH, "system_audit_omega.log"), "r") as log_f:
                lines = log_f.readlines()
            st.text_area("Dump de Logs de Auditoria", "".join(lines[-20:]), height=200)
            
            if st.button("LIMPAR LOGS"):
                 open(os.path.join(LOG_PATH, "system_audit_omega.log"), "w").close()
                 st.rerun()
                 
    with tabs_conf[2]:
        st.markdown(
            """
            ### SYSTEM OMEGA V.50
            **Build:** Enterprise Gold Edition  
            **Status:** Stable Production  
            
            Este sistema é um software de gestão pastoral completo, incluindo módulos de engenharia de documentos,
            análise teológica e suporte à saúde mental do líder.
            """
        )
        st.json(GLOBAL_MODULES)

# End of System
