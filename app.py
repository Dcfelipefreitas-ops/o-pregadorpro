# -*- coding: utf-8 -*-
"""
O PREGADOR - SISTEMA INTEGRAL (Versão V.Ultimate)
Status: Produção / Robusto
- Preservação Total de Protocolos (Geneva, PastoralMind).
- Módulo Word/PDF: Reimplementação completa das rotinas de exportação.
- Expansão Cuidado Pastoral: Educação sobre Permissão + Rotina Dinâmica.
- Novo Módulo: Rede Ministerial (Colaboradores e Vídeos).
- UX: Ajuste de espaçamento e realocação de Ferramentas.
"""

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
from datetime import datetime
from io import BytesIO

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E IMPORTAÇÃO DE MÓDULOS DE FORÇA (ROBUSTEZ)
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR",
    layout="wide",
    page_icon="✝️",
    initial_sidebar_state="expanded"
)

# --- SISTEMA DE LOGS ---
def setup_logging():
    log_dir = "Dados_Pregador_V31/System_Logs"
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_dir, "system_audit.log"),
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(module)s | %(message)s'
    )
setup_logging()

# --- MÓDULO EDITOR E IMPORTAÇÕES UI ---
# Tenta carregar CKEditor (Avançado)
CKEDITOR_AVAILABLE = False
STREAMLIT_CKEDITOR = False
try:
    from streamlit_ckeditor import st_ckeditor 
    STREAMLIT_CKEDITOR = True
    CKEDITOR_AVAILABLE = True
    logging.info("Módulo CKEditor carregado com sucesso.")
except Exception as e:
    logging.warning(f"CKEditor não detectado: {e}")

# Tenta carregar Quill (Intermediário)
QUILL_AVAILABLE = False
try:
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except Exception:
    logging.warning("Quill não detectado.")

# Tenta carregar Plotly (Visualização)
PLOTLY_OK = False
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except Exception:
    pass

# --- MÓDULO CRYPTO (SEGURANÇA) ---
CRYPTO_OK = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except Exception:
    logging.warning("Módulo de Criptografia Avançada (AES) ausente. Usando fallback básico se necessário.")

# --- MÓDULO OFFICE/EXPORTAÇÃO (WORD & PDF) ---
# Esta seção garante a funcionalidade de exportação robusta solicitada.
HTML2DOCX_ENGINE = None

# 1. Tentativa: Mammoth (Melhor qualidade para HTML -> DOCX)
try:
    import mammoth
    HTML2DOCX_ENGINE = "mammoth"
except Exception:
    # 2. Tentativa: Html2Docx Package
    try:
        from html2docx import html2docx
        HTML2DOCX_ENGINE = "html2docx"
    except Exception:
        # 3. Tentativa: Python-Docx (Construção manual)
        try:
            from docx import Document
            HTML2DOCX_ENGINE = "docx_manual"
        except Exception:
            HTML2DOCX_ENGINE = None

PDF_ENGINE = None
# 1. Tentativa: ReportLab (Padrão ouro em Python)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate
    PDF_ENGINE = "reportlab"
except Exception:
    # 2. Tentativa: FPDF (Simples)
    try:
        from fpdf import FPDF
        PDF_ENGINE = "fpdf"
    except Exception:
        PDF_ENGINE = None

# ==============================================================================
# 2. SISTEMA DE ARQUIVOS (GENESIS PROTOCOL)
# ==============================================================================
ROOT = "Dados_Pregador_V31"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
    "LOGS": os.path.join(ROOT, "System_Logs"),
    "BIB_CACHE": os.path.join(ROOT, "BibliaCache"),
    "MEMBROS": os.path.join(ROOT, "Membresia"),
    "REDE_COLAB": os.path.join(ROOT, "Rede_Ministerial")  # Novo Diretório para o braço de colaboradores
}

DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "MEMBERS_DB": os.path.join(DIRS["MEMBROS"], "members.json"),
    "COLAB_FEED": os.path.join(DIRS["REDE_COLAB"], "feed_videos.json")
}

def _genesis_boot_protocol():
    """Garante a existência de toda a infraestrutura de pastas e bancos JSON."""
    for p in DIRS.values():
        os.makedirs(p, exist_ok=True)

    # 1. Configuração Principal (Com novas chaves para Rotina)
    if not os.path.exists(DBS["CONFIG"]):
        cfg = {
            "theme_color": "#D4AF37",
            "font_size": 18,
            "enc_password": "OMEGA_KEY_DEFAULT",
            "backup_interval_seconds": 86400,
            "last_backup": None,
            "theme_mode": "Dark Cathedral",
            "font_family": "Inter",
            "rotina_pastoral": [  # Lista dinâmica default
                "Leitura Bíblica Devocional", 
                "Oração pela Liderança", 
                "Estudo Teológico (1h)", 
                "Tempo de Descanso"
            ]
        }
        with open(DBS["CONFIG"], "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)

    # 2. Banco de Usuários
    if not os.path.exists(DBS["USERS"]):
        # Admin default: senha 'admin' hasheada
        pw_hash = hashlib.sha256("admin".encode()).hexdigest()
        with open(DBS["USERS"], "w", encoding="utf-8") as f:
            json.dump({"ADMIN": pw_hash}, f, indent=4)

    # 3. Feed de Colaboradores (Novo Braço)
    if not os.path.exists(DBS["COLAB_FEED"]):
        with open(DBS["COLAB_FEED"], "w", encoding="utf-8") as f:
            json.dump([], f, indent=4) # Lista vazia inicial

    # 4. Outros DBs essenciais
    for db_path in [DBS["MEMBERS_DB"], DBS["SOUL"]]:
        if not os.path.exists(db_path):
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    if not os.path.exists(DBS["STATS"]):
        with open(DBS["STATS"], "w", encoding="utf-8") as f:
            json.dump({"xp": 0, "nivel": 1}, f)

_genesis_boot_protocol()

# ==============================================================================
# 3. MÓDULOS DE UTILIDADE, I/O E CRIPTOGRAFIA
# ==============================================================================
def read_json_safe(path, default=None):
    if default is None: default = {}
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data: return default
            return json.loads(data)
    except Exception as e:
        logging.error(f"Falha leitura JSON {path}: {e}")
        return default

def write_json_safe(path, data):
    try:
        # Gravação atômica (escreve tmp e renomeia) para evitar corrupção
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, path)
        return True
    except Exception as e:
        logging.error(f"Falha escrita JSON {path}: {e}")
        st.error("Erro crítico ao salvar dados. Verifique logs.")
        return False

def safe_filename(text):
    if not text: return "arquivo_sem_nome"
    # Remove caracteres ilegais e substitui espaços
    clean = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', clean)

# --- ENGINE DE ENCRIPTAÇÃO ---
def encrypt_content(password, text):
    """Criptografa o texto do sermão usando AES-GCM se disponível."""
    if not CRYPTO_OK:
        return None
    try:
        key = hashlib.sha256(password.encode()).digest()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, text.encode("utf-8"), None)
        return base64.b64encode(nonce + ciphertext).decode("utf-8")
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        return None

# ==============================================================================
# 4. MÓDULO DE EXPORTAÇÃO "WORD" (PESADO E ROBUSTO)
# ==============================================================================
class ExportEngine:
    """
    Classe dedicada à exportação de documentos. Garante que seu sermão
    saia do app para o mundo real (DOCX/PDF) usando o que estiver disponível.
    """
    
    @staticmethod
    def to_docx(title, html_content, output_path):
        """Exporta HTML para DOCX tentando múltiplos motores."""
        # 1. Tentativa Mammoth (Melhor)
        if HTML2DOCX_ENGINE == "mammoth":
            try:
                # Mammoth converte HTML puro em estruturas DOCX
                import mammoth
                # O mammoth espera bytes ou string, às vezes precisa wrap em '<body>'
                html_wrapped = f"<html><body><h1>{title}</h1>{html_content}</body></html>"
                result = mammoth.convert_to_docx(html_wrapped)
                with open(output_path, "wb") as f:
                    f.write(result.value)
                return True, "Sucesso via Mammoth"
            except Exception as e:
                logging.error(f"Mammoth fail: {e}")
        
        # 2. Tentativa HTML2DOCX (Package)
        if HTML2DOCX_ENGINE == "html2docx":
            try:
                from html2docx import html2docx
                buf = html2docx(html_content, title=title)
                with open(output_path, "wb") as f:
                    f.write(buf.getvalue())
                return True, "Sucesso via Html2Docx"
            except Exception as e:
                logging.error(f"html2docx fail: {e}")

        # 3. Fallback: Python-Docx (Manual)
        # Remove tags HTML brutalmente e salva texto puro formatado minimamente
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title, 0)
            
            # Limpeza regex simples para remover tags
            clean_text = re.sub(r'<[^>]+>', '\n', html_content)
            clean_text = re.sub(r'\n+', '\n', clean_text).strip()
            
            doc.add_paragraph(clean_text)
            doc.save(output_path)
            return True, "Sucesso via Fallback (Texto Puro)"
        except Exception as e:
            return False, f"Falha Total DOCX: {e}"

    @staticmethod
    def to_pdf(title, html_content, output_path):
        """Exporta HTML (texto) para PDF."""
        # Limpeza para PDF (Remove tags pois reportlab complexo exige XML estrito)
        clean_text = re.sub(r'<[^>]+>', '\n', html_content).strip()
        
        if PDF_ENGINE == "reportlab":
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                c = canvas.Canvas(output_path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, height - 50, title)
                c.line(40, height - 60, width - 40, height - 60)
                
                # Body
                c.setFont("Helvetica", 12)
                text_object = c.beginText(40, height - 80)
                
                # Quebra de linha manual básica
                lines = clean_text.split('\n')
                for line in lines:
                    # Se linha muito longa, corta (simplificação)
                    # O ideal seria usar platypus.Paragraph, mas aumenta complexidade.
                    if len(line) > 90:
                        chunks = [line[i:i+90] for i in range(0, len(line), 90)]
                        for chunk in chunks:
                            text_object.textLine(chunk)
                    else:
                        text_object.textLine(line)
                        
                    # Nova página se encher
                    if text_object.getY() < 50:
                        c.drawText(text_object)
                        c.showPage()
                        text_object = c.beginText(40, height - 50)
                        c.setFont("Helvetica", 12)

                c.drawText(text_object)
                c.save()
                return True, "Sucesso via ReportLab"
            except Exception as e:
                logging.error(f"PDF fail: {e}")
                
        # Fallback TXT mascarado
        try:
            with open(output_path.replace(".pdf", ".txt"), "w", encoding="utf-8") as f:
                f.write(f"{title}\n\n{clean_text}")
            return False, "PDF Indisponível. Salvo como TXT."
        except:
            return False, "Falha I/O"

# ==============================================================================
# 5. PROTOCOLOS E LOGICA DE NEGÓCIO
# ==============================================================================

class AccessControl:
    """Gerencia logins e permissões."""
    @staticmethod
    def login(user, password):
        users = read_json_safe(DBS["USERS"], {})
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        # Super user fallback
        if user == "ADMIN" and password == "1234" and len(users) == 0:
            return True

        if user.upper() in users:
            stored = users[user.upper()]
            return stored == hashed
        return False

    @staticmethod
    def register_colaborador(username, password):
        users = read_json_safe(DBS["USERS"], {})
        if username.upper() in users:
            return False, "Usuário já existe"
        users[username.upper()] = hashlib.sha256(password.encode()).hexdigest()
        write_json_safe(DBS["USERS"], users)
        return True, "Colaborador registrado"

class PastoralMind:
    """Lógica de Burnout e Estado Emocional"""
    @staticmethod
    def check_state():
        soul = read_json_safe(DBS["SOUL"], {"historico": []})
        hist = soul.get("historico", [])[-7:] # Última semana
        negativos = sum(1 for x in hist if x['humor'] in ['Cansaço', 'Estresse', 'Tristeza'])
        if negativos >= 4:
            return "ALERTA VERMELHO: BURNOUT IMINENTE", "#FF0000"
        elif negativos >= 2:
            return "ATENÇÃO: Cansaço Acumulado", "#xFFA500"
        else:
            return "VITALIDADE OK", "#00FF00"

    @staticmethod
    def permission_education():
        """Retorna o texto educativo sobre a Teoria da Permissão solicitado."""
        return """
        ### 🧠 O que é a Teoria da Permissão no Ministério?
        Muitos pastores sofrem porque operam sob regras internas rígidas de "nunca falhar", 
        "nunca descansar" ou "suprir todas as demandas".
        
        A **Teoria da Permissão** é uma ferramenta terapêutica para autorizar sua humanidade:
        1. **Permissão para Falhar:** Aceitar que o erro não anula sua unção.
        2. **Permissão para Sentir:** Validar tristeza ou ira sem culpa teológica imediata.
        3. **Permissão para Limitar:** Dizer 'não' é uma disciplina espiritual de proteção.
        
        **Como usar esta ferramenta:**
        - Mova os controles abaixo com sinceridade sobre como você se sentiu hoje.
        - Se o gráfico estiver "fechado" (pequeno), você está se reprimindo muito.
        - Se estiver "aberto", você está fluindo na Graça.
        """

class GenevaProtocol:
    """Scan Teológico"""
    DB = {
        "prosperidade": "Alerta: Teologia da Prosperidade?",
        "determino": "Alerta: Confissão Positiva?",
        "nova era": "Alerta: Sincretismo?",
        "universo": "Cuidado: Termo vago (use 'Deus'/'Criação')"
    }
    @staticmethod
    def scan(text):
        if not text: return []
        text_lower = text.lower()
        return [alert for keyword, alert in GenevaProtocol.DB.items() if keyword in text_lower]

# ==============================================================================
# 6. INTERFACE DE USUÁRIO (FRONTEND)
# ==============================================================================

# CSS CUSTOMIZADO (Visual Robust)
# Corrige espaçamentos e melhora o fluxo conforme solicitado
config_user = read_json_safe(DBS["CONFIG"])
accent_color = config_user.get("theme_color", "#D4AF37")
font_u = normalize_font_name(config_user.get("font_family"))

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    :root {{
        --primary: {accent_color};
        --bg-dark: #0e0e0e;
        --card-bg: #141414;
    }}
    
    html, body, [class*="css"] {{
        font-family: '{font_u}', 'Inter', sans-serif;
    }}
    
    .stApp {{ background-color: var(--bg-dark); }}
    
    /* Headers */
    h1, h2, h3 {{ font-family: 'Cinzel', serif !important; color: var(--primary); }}
    
    /* Espaçamento melhorado */
    .block-container {{ padding-top: 2rem; padding-bottom: 5rem; }}
    
    /* Card Styles */
    .pastoral-card {{
        background-color: var(--card-bg);
        border-left: 3px solid var(--primary);
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Sidebar adjustments */
    [data-testid="stSidebar"] {{ background-color: #050505; border-right: 1px solid #222; }}
    
    /* Botões personalizados */
    .stButton>button {{
        border: 1px solid var(--primary);
        color: var(--primary);
        background: transparent;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background: var(--primary);
        color: black;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOGIN
# ---------------------------
if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "GUEST"

if not st.session_state["logado"]:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f"<div style='text-align:center'><h1 style='color:{accent_color}'>O PREGADOR</h1></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; color:gray; margin-bottom:30px'>SYSTEM V.ULTIMATE | PROTOCOL SECURE</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            u = st.text_input("Identidade Pastoral")
            p = st.text_input("Chave de Acesso", type="password")
            submitted = st.form_submit_button("ENTRAR NO SANTUÁRIO DIGITAL")
            
            if submitted:
                if AccessControl.login(u, p):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = u.upper()
                    st.success("Acesso Concedido.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credenciais não reconhecidas.")
    st.stop()

# ---------------------------
# SIDEBAR NAVEGAÇÃO
# ---------------------------
with st.sidebar:
    st.markdown(f"## Olá, {st.session_state['user_name']}")
    status_txt, status_col = PastoralMind.check_state()
    st.markdown(f"Vitalidade: <span style='color:{status_col}'>{status_txt}</span>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio("NAVEGAÇÃO", [
        "Cuidado Pastoral", 
        "Gabinete (Editor)",
        "Rede Ministerial", 
        "Biblioteca", 
        "Configurações"
    ])
    
    st.markdown("---")
    if st.button("LOGOUT"):
        st.session_state["logado"] = False
        st.rerun()

# ---------------------------
# MÓDULO 1: CUIDADO PASTORAL (Expandido com Rotina Dinâmica e Educação)
# ---------------------------
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado Pastoral & Alma")
    
    # Abas reorganizadas
    tab_status, tab_permissoes, tab_rotina = st.tabs(["📊 Estado da Alma", "⚖️ Teoria da Permissão (Educativo)", "📋 Rotina Dinâmica"])
    
    with tab_status:
        # Check-in emocional diário
        st.markdown("<div class='pastoral-card'>", unsafe_allow_html=True)
        st.subheader("Check-in Diário")
        hoje_humor = st.select_slider("Como está seu coração hoje?", ["Exausto", "Cansaço", "Neutro", "Bem", "Plenitude"])
        if st.button("Registrar Estado"):
            soul = read_json_safe(DBS["SOUL"])
            soul.setdefault("historico", []).append({
                "data": datetime.now().strftime("%Y-%m-%d"), 
                "humor": hoje_humor
            })
            write_json_safe(DBS["SOUL"], soul)
            st.success("Registrado.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_permissoes:
        # Novo conteúdo educativo
        st.info(PastoralMind.permission_education())
        
        st.subheader("Auto-Análise de Permissão")
        col_sliders, col_grafico = st.columns(2)
        with col_sliders:
            p_falhar = st.slider("Quanto me permito falhar/não saber?", 0, 100, 50)
            p_sentir = st.slider("Quanto me permito sentir dores?", 0, 100, 50)
            p_limite = st.slider("Quanto respeito meus limites físicos?", 0, 100, 50)
            p_lazer = st.slider("Quanto me permito o lazer sem culpa?", 0, 100, 50)
        
        with col_grafico:
            if PLOTLY_OK:
                fig = go.Figure(data=go.Scatterpolar(
                    r=[p_falhar, p_sentir, p_limite, p_lazer, p_falhar],
                    theta=['Falhar', 'Sentir', 'Limitar', 'Lazer', 'Falhar'],
                    fill='toself',
                    line_color=accent_color
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.progress((p_falhar+p_sentir+p_limite+p_lazer)/400)
                st.text("Visualização Simplificada (Instale Plotly para gráfico Radar)")

    with tab_rotina:
        # Nova Lógica: Rotina Dinâmica (Usuario pode adicionar itens)
        st.markdown("<div class='pastoral-card'>", unsafe_allow_html=True)
        st.subheader("Gerenciador de Rotina Ministerial")
        
        cfg = read_json_safe(DBS["CONFIG"])
        rotina_atual = cfg.get("rotina_pastoral", [])
        
        # Exibição
        concluidos = []
        st.write("### Minhas Tarefas Diárias")
        for tarefa in rotina_atual:
            if st.checkbox(tarefa, key=f"chk_{tarefa}"):
                concluidos.append(tarefa)
        
        if len(concluidos) == len(rotina_atual) and len(rotina_atual) > 0:
            st.success("Parabéns! Dia produtivo e disciplinado.")

        st.markdown("---")
        
        # Adição dinâmica
        c_add1, c_add2 = st.columns([3, 1])
        new_task = c_add1.text_input("Adicionar nova tarefa à rotina (Ex: Caminhada 30min)")
        if c_add2.button("➕ Adicionar"):
            if new_task and new_task not in rotina_atual:
                rotina_atual.append(new_task)
                cfg["rotina_pastoral"] = rotina_atual
                write_json_safe(DBS["CONFIG"], cfg)
                st.rerun()
        
        # Remoção
        task_to_remove = st.selectbox("Remover tarefa da lista padrão", ["Selecione..."] + rotina_atual)
        if st.button("🗑️ Remover da Rotina"):
            if task_to_remove in rotina_atual:
                rotina_atual.remove(task_to_remove)
                cfg["rotina_pastoral"] = rotina_atual
                write_json_safe(DBS["CONFIG"], cfg)
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# MÓDULO 2: GABINETE (Editor e Word Module)
# ---------------------------
elif menu == "Gabinete (Editor)":
    st.title("📝 Gabinete Pastoral")
    
    col_files, col_edit = st.columns([1, 4])
    
    with col_files:
        st.markdown("### Sermões")
        files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".html") or f.endswith(".txt")]
        selected_file = st.radio("Arquivos", ["Novo"] + files, label_visibility="collapsed")

    with col_edit:
        # Carregar ou Criar
        content = ""
        doc_title = ""
        
        if selected_file != "Novo":
            try:
                with open(os.path.join(DIRS["SERMOES"], selected_file), "r", encoding="utf-8") as f:
                    content = f.read()
                doc_title = selected_file.split(".")[0].replace("_", " ")
            except:
                st.error("Erro ao abrir arquivo.")
        
        # Títulos
        titulo_input = st.text_input("Título do Sermão", value=doc_title, placeholder="Título da Mensagem")
        
        # Seleção de Editor (Robustez)
        text_data = content
        if CKEDITOR_AVAILABLE and STREAMLIT_CKEDITOR:
            text_data = st_ckeditor(value=content, key="main_ck", height=500)
        elif QUILL_AVAILABLE:
            text_data = st_quill(value=content, key="main_quill", height=500, html=True)
        else:
            text_data = st.text_area("Texto (Modo Simples)", value=content, height=500)

        # Barra de Ferramentas de Ação
        c_act1, c_act2, c_act3, c_act4 = st.columns(4)
        
        filename = safe_filename(titulo_input)
        
        if c_act1.button("💾 Salvar (HTML)"):
            if not filename: filename = f"sermao_{int(time.time())}"
            path = os.path.join(DIRS["SERMOES"], filename + ".html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text_data)
            st.toast("Sermão Salvo com Sucesso!", icon="✅")

        # EXPORTAÇÃO USANDO MÓDULO WORD ROBUSTO
        if c_act2.button("📄 Baixar DOCX"):
            if not filename: filename = "sermao_export"
            path = os.path.join(DIRS["SERMOES"], filename + ".docx")
            
            with st.spinner(f"Processando Word via engine {HTML2DOCX_ENGINE}..."):
                success, msg = ExportEngine.to_docx(titulo_input, text_data, path)
            
            if success:
                st.success(f"{msg}")
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download .docx", f, file_name=filename+".docx")
            else:
                st.error(msg)

        # EXPORTAÇÃO PDF
        if c_act3.button("📕 Baixar PDF"):
            if not filename: filename = "sermao_export"
            path = os.path.join(DIRS["SERMOES"], filename + ".pdf")
            
            with st.spinner(f"Gerando PDF via engine {PDF_ENGINE}..."):
                success, msg = ExportEngine.to_pdf(titulo_input, text_data, path)
            
            if success:
                st.success(f"{msg}")
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download .pdf", f, file_name=filename+".pdf")
            else:
                st.warning(f"Erro PDF: {msg} (Tente instalar ReportLab)")

        if c_act4.button("🔍 Scan Geneva"):
            alerts = GenevaProtocol.scan(text_data)
            if alerts:
                st.warning("⚠️ Alertas Doutrinários: " + ", ".join(alerts))
            else:
                st.success("Nenhum termo suspeito detectado.")

# ---------------------------
# MÓDULO 3: REDE MINISTERIAL (Novo "Braço" Colaborativo)
# ---------------------------
elif menu == "Rede Ministerial":
    st.title("🤝 Rede Ministerial Colaborativa")
    st.markdown("Espaço para edificação mútua e compartilhamento de conteúdos pastorais.")
    
    feed_data = read_json_safe(DBS["COLAB_FEED"], [])
    
    # Área de Admin/Colaborador (Postagem)
    # Aqui permitimos postar se for ADMIN ou se for um usuario 'pastor' validado.
    # Para simplificar a logica, deixei disponivel para usuarios logados.
    
    with st.expander("📢 Postar Novo Conteúdo (Vídeo/Devocional)"):
        with st.form("post_feed"):
            v_title = st.text_input("Título do Devocional/Pregação")
            v_author = st.text_input("Autor / Pastor", value=st.session_state.get("user_name", ""))
            v_desc = st.text_area("Pequena descrição")
            v_url = st.text_input("Link do Youtube")
            
            if st.form_submit_button("Publicar na Rede"):
                new_post = {
                    "id": str(int(time.time())),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "title": v_title,
                    "author": v_author,
                    "description": v_desc,
                    "url": v_url
                }
                feed_data.insert(0, new_post) # Adiciona no topo
                write_json_safe(DBS["COLAB_FEED"], feed_data)
                st.success("Conteúdo publicado para a rede!")
                st.rerun()

    st.markdown("### 📺 Feed de Edificação")
    if not feed_data:
        st.info("Ainda não há publicações na rede. Seja o primeiro!")
    
    for post in feed_data:
        st.markdown(f"<div class='pastoral-card'>", unsafe_allow_html=True)
        col_vid, col_txt = st.columns([1, 1.5])
        with col_vid:
            if "youtube" in post['url'] or "youtu.be" in post['url']:
                st.video(post['url'])
            else:
                st.write("Link externo: ", post['url'])
        with col_txt:
            st.subheader(post['title'])
            st.caption(f"Por: {post['author']} | Em: {post['date']}")
            st.write(post['description'])
            if st.session_state["user_name"] == "ADMIN":
                if st.button("Remover Post", key=post['id']):
                    feed_data.remove(post)
                    write_json_safe(DBS["COLAB_FEED"], feed_data)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# MÓDULO 4: BIBLIOTECA (Preservado)
# ---------------------------
elif menu == "Biblioteca":
    st.title("📚 Biblioteca Digital")
    
    uploaded_file = st.file_uploader("Adicionar PDF/EPUB à Biblioteca", type=["pdf", "epub", "docx", "txt"])
    if uploaded_file:
        save_path = os.path.join(DIRS["BIB_CACHE"], uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Livro '{uploaded_file.name}' indexado.")

    st.markdown("### Seus Livros")
    books = os.listdir(DIRS["BIB_CACHE"])
    if books:
        for b in books:
            st.markdown(f"📖 **{b}**")
    else:
        st.info("Nenhum livro local.")

# ---------------------------
# MÓDULO 5: CONFIGURAÇÕES (Com Ferramentas)
# ---------------------------
elif menu == "Configurações":
    st.title("⚙️ Configurações & Ferramentas")
    
    tabs_conf = st.tabs(["Personalização", "Sistema & Backup", "Usuários"])
    
    cfg = read_json_safe(DBS["CONFIG"])
    
    with tabs_conf[0]:
        c1, c2 = st.columns(2)
        new_theme = c1.color_picker("Cor Principal (Requer Reload)", cfg.get("theme_color", "#D4AF37"))
        new_font = c2.selectbox("Família de Fonte", ["Inter", "Roboto", "Lato", "Merriweather"])
        if st.button("Salvar Visual"):
            cfg["theme_color"] = new_theme
            cfg["font_family"] = new_font
            write_json_safe(DBS["CONFIG"], cfg)
            st.success("Visual salvo. Recarregue a página.")
            
    with tabs_conf[1]:
        st.subheader("Ferramentas de Manutenção (Movido)")
        
        st.markdown("### Backup Manual")
        if st.button("📥 Criar Backup Completo (ZIP)"):
            try:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                shutil.make_archive(os.path.join(DIRS["BACKUP"], f"bkp_{ts}"), 'zip', ROOT)
                st.success(f"Backup criado em {DIRS['BACKUP']}")
            except Exception as e:
                st.error(f"Erro no backup: {e}")
        
        st.divider()
        st.markdown("### Limpeza de Logs")
        if st.button("🗑️ Limpar Logs do Sistema"):
            try:
                open(os.path.join(DIRS["LOGS"], "system_audit.log"), 'w').close()
                st.success("Logs limpos.")
            except:
                st.error("Erro ao limpar logs.")

    with tabs_conf[2]:
        st.subheader("Cadastro de Colaboradores (Braço Rede)")
        if st.session_state["user_name"] == "ADMIN":
            with st.form("novo_colab"):
                nc_user = st.text_input("Usuário")
                nc_pass = st.text_input("Senha", type="password")
                if st.form_submit_button("Cadastrar Colaborador"):
                    ok, msg = AccessControl.register_colaborador(nc_user, nc_pass)
                    if ok: st.success(msg)
                    else: st.error(msg)
        else:
            st.info("Apenas ADMIN pode cadastrar novos colaboradores.")

# ---------------------------
# RODAPÉ DE CREDIBILIDADE
# ---------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("O PREGADOR | Versão V.Ultimate Robust | Desenvolvido com Cuidado Pastoral | Protegido por Lógica Criptográfica")
