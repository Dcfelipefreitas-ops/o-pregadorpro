import streamlit as st
import os
import json
from datetime import datetime

# --------- CONFIGURAÇÃO GLOBAL ---------
st.set_page_config(
    page_title="O PREGADOR",
    page_icon="✝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------- CARREGA MÓDULOS ---------
from modules.editor import editor_page
from modules.biblioteca import biblioteca_page
from modules.sermoes import sermoes_page
from modules.gabinete import gabinete_page
from modules.membros import membros_page
from modules.estatisticas import estatisticas_page
from modules.sincronizacao import sincronizacao_page
from modules.conta import conta_page

# --------- SIDEBAR ---------
menu = st.sidebar.radio(
    "📂 Navegação",
    [
        "✍️ Editor de Sermões",
        "📚 Biblioteca",
        "📖 Sermões Salvos",
        "🧩 Gabinete Pastoral",
        "👥 Rebanho",
        "📊 Estatísticas",
        "☁️ Sincronização",
        "⚙️ Conta e Configurações"
    ]
)

# --------- ROTAS ---------
if menu == "✍️ Editor de Sermões":
    editor_page()

elif menu == "📚 Biblioteca":
    biblioteca_page()

elif menu == "📖 Sermões Salvos":
    sermoes_page()

elif menu == "🧩 Gabinete Pastoral":
    gabinete_page()

elif menu == "👥 Rebanho":
    membros_page()

elif menu == "📊 Estatísticas":
    estatisticas_page()

elif menu == "☁️ Sincronização":
    sincronizacao_page()

elif menu == "⚙️ Conta e Configurações":
    conta_page()
 import streamlit as st
from streamlit_quill import st_quill
from datetime import datetime
import json
import os
from io import BytesIO
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --------------------------- FUNÇÕES AUXILIARES ---------------------------

def salvar_sermao(texto):
    """Salva a versão atual do sermão no histórico."""
    data = datetime.now().strftime("%Y-%m-%d %H:%M")
    registro = {"data": data, "conteudo": texto}

    if not os.path.exists("data/sermoes"):
        os.makedirs("data/sermoes")

    historico_path = "data/sermoes/historico.json"

    if os.path.exists(historico_path):
        with open(historico_path, "r") as f:
            historico = json.load(f)
    else:
        historico = []

    historico.append(registro)

    with open(historico_path, "w") as f:
        json.dump(historico, f, indent=4)


def carregar_historico():
    path = "data/sermoes/historico.json"
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def exportar_docx(texto):
    doc = Document()
    doc.add_paragraph(texto)
    buffer = BytesIO()
    doc.save(buffer)
    return buffer


def exportar_pdf(texto):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    y = 750
    for linha in texto.split("\n"):
        pdf.drawString(50, y, linha)
        y -= 18
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 750

    pdf.save()
    return buffer


# --------------------------- TEMPLATES DE SERMÃO ---------------------------

templates = {
    "🔥 Sermão Temático": "Título do Sermão\n\nTema:\n\nIntrodução:\n\nPontos Principais:\n - 1.\n - 2.\n - 3.\n\nConclusão:\n",
    "📖 Sermão Expositivo": "Título do Sermão\n\nTexto Base:\n\nIntrodução:\n\nExposição do Texto:\n\nAplicação:\n\nConclusão:\n",
    "🎯 Sermão Evangelístico": "Título do Sermão\n\nTexto Base:\n\nA Situação Humana:\n\nA Solução em Cristo:\n\nConvite:\n\nConclusão:\n",
}


# --------------------------- INTERFACE PRINCIPAL ---------------------------

def editor_page():
    st.title("✍️ Editor de Sermões")

    # ---------------- MENU LATERAL ----------------
    with st.sidebar.expander("📄 Templates", expanded=False):
        escolha = st.selectbox("Escolha um modelo:", list(templates.keys()))
        if st.button("Carregar Template"):
            st.session_state["texto_ativo"] = templates[escolha]

    with st.sidebar.expander("🕒 Histórico de Versões", expanded=False):
        historico = carregar_historico()
        if historico:
            for item in historico[::-1]:
                if st.button(f"{item['data']}"):
                    st.session_state["texto_ativo"] = item["conteudo"]
        else:
            st.write("Nenhum histórico salvo ainda.")

    # ---------------- EDITOR ----------------
    texto = st_quill(
        value=st.session_state.get("texto_ativo", ""),
        placeholder="Comece a escrever seu sermão...",
        html=True,
        key="editor_sermao",
        theme="snow"
    )

    # Salvamento automático
    if texto and texto != st.session_state.get("texto_ativo"):
        st.session_state["texto_ativo"] = texto
        salvar_sermao(texto)

    # ---------------- EXPORTAÇÃO ----------------
    st.subheader("📤 Exportar Sermão")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Exportar DOCX"):
            docx = exportar_docx(st.session_state.get("texto_ativo", ""))
            st.download_button("Baixar DOCX", data=docx, file_name="sermao.docx")

    with col2:
        if st.button("📕 Exportar PDF"):
            pdf = exportar_pdf(st.session_state.get("texto_ativo", ""))
            st.download_button("Baixar PDF", data=pdf, file_name="sermao.pdf")

    # ---------------- NOTAS AUXILIARES ----------------
    st.markdown("### 📝 Notas Rápidas")
    st.text_area("Escreva notas auxiliares:", height=120)
# -*- coding: utf-8 -*-
"""
modules/library.py
Biblioteca integrada para "O PREGADOR"
- Indexa arquivos locais (pdf, docx, txt, epub)
- Importa arquivos para a pasta de cache
- Pré-visualiza trechos de PDFs/DOCX/TXT
- Busca no Google Books (simulada se não houver API key)
- Fornece funções utilitárias: index_user_books, preview_book, import_book
"""

import os
import json
from io import BytesIO, StringIO
from typing import List, Dict

# tentativas de leitura de formatos
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import mammoth
except Exception:
    mammoth = None

try:
    import ebooklib
    from ebooklib import epub
except Exception:
    epub = None

try:
    from docx import Document
except Exception:
    Document = None

# Ajuste o caminho se necessário; o app principal usa DIRS["BIB_CACHE"]
DEFAULT_CACHE = os.path.join("Dados_Pregador_V31", "BibliaCache")
os.makedirs(DEFAULT_CACHE, exist_ok=True)


def index_user_books(folder: str = None) -> List[str]:
    """
    Retorna lista de arquivos indexados localmente (apenas nomes).
    """
    folder = folder or DEFAULT_CACHE
    books = []
    try:
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith((".pdf", ".docx", ".txt", ".epub", ".md")):
                books.append(f)
    except Exception:
        pass
    return books


def import_book(uploaded_file, dest_folder: str = None) -> Dict:
    """
    Salva um arquivo enviado (arquivo tipo Streamlit UploadedFile) em dest_folder.
    Retorna metadata simples.
    """
    dest_folder = dest_folder or DEFAULT_CACHE
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, uploaded_file.name)
    with open(dest_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    meta = {
        "filename": uploaded_file.name,
        "size": os.path.getsize(dest_path),
        "path": dest_path
    }
    return meta


def _preview_pdf(path: str, max_chars: int = 2000) -> str:
    text = ""
    try:
        if PyPDF2:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    if i >= 3:  # limita a 3 páginas de preview
                        break
                    try:
                        text += page.extract_text() or ""
                    except Exception:
                        continue
        else:
            # fallback: apenas informa que o PyPDF2 não está disponível
            text = "[Preview não disponível localmente — instale PyPDF2 para extrair texto de PDFs]"
    except Exception:
        text = "[Erro ao extrair preview do PDF]"
    return (text or "").strip()[:max_chars]


def _preview_docx(path: str, max_chars: int = 2000) -> str:
    try:
        if Document:
            doc = Document(path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs[:20])[:max_chars]
        else:
            return "[Preview de DOCX requer python-docx instalada]"
    except Exception:
        return "[Erro ao extrair preview do DOCX]"


def _preview_txt(path: str, max_chars: int = 2000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read(max_chars)
            return data
    except Exception:
        return "[Erro ao abrir TXT]"


def _preview_epub(path: str, max_chars: int = 2000) -> str:
    try:
        if epub:
            book = epub.read_epub(path)
            text = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                txt = item.get_content().decode("utf-8", errors="ignore")
                text.append(txt)
                if len("".join(text)) > max_chars:
                    break
            return "".join(text)[:max_chars]
        else:
            return "[Preview de EPUB requer ebooklib]"
    except Exception:
        return "[Erro ao extrair preview do EPUB]"


def preview_book(filename: str, folder: str = None, max_chars: int = 2000) -> Dict:
    """
    Retorna metadata e trecho de preview do arquivo.
    """
    folder = folder or DEFAULT_CACHE
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return {"error": "Arquivo não encontrado", "path": path}

    ext = filename.lower().split(".")[-1]
    preview = ""
    try:
        if ext == "pdf":
            preview = _preview_pdf(path, max_chars=max_chars)
        elif ext == "docx":
            preview = _preview_docx(path, max_chars=max_chars)
        elif ext in ("txt", "md"):
            preview = _preview_txt(path, max_chars=max_chars)
        elif ext == "epub":
            preview = _preview_epub(path, max_chars=max_chars)
        else:
            preview = "[Formato não suportado para preview]"
    except Exception as e:
        preview = f"[Erro no preview: {e}]"

    meta = {
        "filename": filename,
        "path": path,
        "size": os.path.getsize(path),
        "preview": preview[:max_chars]
    }
    return meta


# ------------------------------
# BUSCA GOOGLE BOOKS (simulada / leve)
# ------------------------------
def search_google_books(query: str, api_key: str = None, max_results: int = 5) -> List[Dict]:
    """
    Busca no Google Books API se api_key for fornecida; caso contrário, faz uma busca simulada.
    Retorna lista de objetos: {title, authors, publishedDate, description, previewLink}
    """
    query = (query or "").strip()
    if not query:
        return []

    if api_key:
        try:
            # uso leve sem dependências extras -> requests
            import requests
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {"q": query, "maxResults": max_results, "key": api_key}
            r = requests.get(url, params=params, timeout=8)
            data = r.json()
            out = []
            for item in data.get("items", [])[:max_results]:
                info = item.get("volumeInfo", {})
                out.append({
                    "title": info.get("title"),
                    "authors": info.get("authors", []),
                    "publishedDate": info.get("publishedDate"),
                    "description": (info.get("description") or "")[:500],
                    "previewLink": info.get("previewLink") or item.get("selfLink")
                })
            return out
        except Exception:
            # fallback para simulação
            pass

    # Simulação quando não há api_key ou quando falha
    return [{
        "title": f"{query} — Introdução (Simulado)",
        "authors": ["Autor Desconhecido"],
        "publishedDate": "—",
        "description": f"Resultado simulado para a busca '{query}'. Para resultados reais, configure uma API Key na tela de Configurações.",
        "previewLink": ""
    }]


# ------------------------------
# COMPONENTE STREAMLIT PRONTO (pode ser chamado no app principal)
# ------------------------------
def library_page(st, cache_folder: str = None, api_key: str = None):
    """
    Interface Streamlit para a biblioteca.
    Chame: from modules.library import library_page; library_page(st, cache_folder=DIRS['BIB_CACHE'], api_key=cfg['api_key'])
    """
    folder = cache_folder or DEFAULT_CACHE
    os.makedirs(folder, exist_ok=True)

    st.header("📚 Biblioteca Integrada")
    st.markdown("Gerencie livros locais, importe recursos e busque no Google Books (opcional).")

    # IMPORTAR LIVROS
    up = st.file_uploader("Importar livro (PDF / DOCX / TXT / EPUB)", type=["pdf", "docx", "txt", "epub"], key="lib_up", help="Importe arquivos para a biblioteca local")
    if up:
        meta = import_book(up, dest_folder=folder)
        st.success(f"Importado: {meta.get('filename')} ({meta.get('size',0)} bytes)")

    st.markdown("### Livros locais")
    books = index_user_books(folder)
    if books:
        for b in books:
            cols = st.columns([6,1,1])
            cols[0].markdown(f"**{b}**")
            if cols[1].button("Preview", key=f"pv_{b}"):
                m = preview_book(b, folder)
                st.markdown(f"**Preview — {m.get('filename','')}**")
                st.text_area("Trecho", value=m.get("preview","(sem preview)"), height=200)
            if cols[2].button("Baixar", key=f"dl_{b}"):
                path = os.path.join(folder, b)
                with open(path, "rb") as f:
                    st.download_button(label="Download", data=f.read(), file_name=b)
    else:
        st.info("Nenhum livro local indexado. Use 'Importar' acima para adicionar arquivos.")

    st.markdown("---")
    st.markdown("### Busca no Google Books")
    q = st.text_input("Termo de busca (ex: teologia pactal)", key="lib_q")
    if st.button("Buscar (Google Books)"):
        results = search_google_books(q, api_key=api_key)
        if not results:
            st.info("Nenhum resultado (ou API Key não configurada).")
        else:
            for r in results:
                st.markdown(f"**{r.get('title')}** — {', '.join(r.get('authors',[]))}")
                st.markdown(r.get("description","")[:600])
                if r.get("previewLink"):
                    st.markdown(f"[Abrir preview]({r.get('previewLink')})", unsafe_allow_html=True)

# If run as script for quick test (non-blocking)
if __name__ == "__main__":
    print("Módulo library.py — functions: index_user_books, preview_book, import_book, library_page")
# -*- coding: utf-8 -*-
"""
modules/backup_sync.py
Backup & Sync helpers para "O PREGADOR"
- backup_local: cria ZIP do diretório ROOT (usa shutil.make_archive)
- cleanup_backups: mantém apenas N backups
- sync_to_google_drive: placeholder com instruções (retorna dict status)
- sync_to_icloud: placeholder com instruções (retorna dict status)
- health_check: verifica espaço e permissões nas pastas
"""

import os
import shutil
import time
import logging
from datetime import datetime

# Ajuste conforme app principal
ROOT = "Dados_Pregador_V31"
BACKUP_DIR = os.path.join(ROOT, "Auto_Backup_Oculto")
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_local(prefix="backup"):
    """
    Cria backup zip de ROOT. Retorna caminho do arquivo se OK, else None.
    """
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.join(BACKUP_DIR, f"{prefix}_{now}")
        shutil.make_archive(base, 'zip', ROOT)
        zip_path = base + ".zip"
        logging.info(f"[backup_local] criado: {zip_path}")
        return zip_path
    except Exception as e:
        logging.exception("[backup_local] erro")
        return None

def cleanup_backups(keep=10):
    """
    Mantém apenas os 'keep' backups mais recentes na pasta BACKUP_DIR.
    """
    try:
        files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.lower().endswith(".zip")]
        files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
        for f in files[keep:]:
            try:
                os.remove(f)
                logging.info(f"[cleanup_backups] removido {f}")
            except Exception:
                logging.exception(f"[cleanup_backups] falha ao remover {f}")
        return True
    except Exception:
        logging.exception("[cleanup_backups] erro")
        return False

def sync_to_google_drive(local_path, creds=None):
    """
    Placeholder: retorna dicionário com o resultado.
    - Se quiser implementar: use google-api-python-client, OAuth2, drive.files.create media upload.
    """
    if not os.path.exists(local_path):
        return {"ok": False, "error": "arquivo local não existe"}
    # instruções que serão úteis ao integrar:
    hint = ("Para ativar: crie projeto no Google Cloud, habilite Drive API, faça OAuth2, e "
            "use googleapiclient.discovery build + MediaFileUpload.")
    logging.info(f"[sync_to_google_drive] simulated upload {local_path}")
    return {"ok": True, "message": "sincronização simulada (configure credenciais)", "hint": hint}

def sync_to_icloud(local_path, creds=None):
    """
    Placeholder: retorna dicionário com o resultado.
    - iCloud não tem uma API pública oficial para Drive-like; considere usar Apple CloudKit ou recomenda sincronizar via pasta iCloud local.
    """
    if not os.path.exists(local_path):
        return {"ok": False, "error": "arquivo local não existe"}
    hint = ("Para iCloud: uma forma prática é copiar arquivo para a pasta iCloud Drive local do servidor/usuário. "
            "Integrações server-to-server requerem soluções proprietárias ou o uso de WebDAV/terceiros.")
    logging.info(f"[sync_to_icloud] simulated upload {local_path}")
    return {"ok": True, "message": "sincronização simulada (configure iCloud local folder)", "hint": hint}

def health_check():
    """
    Verifica se diretórios essenciais existem e se temos permissão de escrita.
    Retorna dict com statuses.
    """
    status = {}
    for path in (ROOT, BACKUP_DIR):
        try:
            ok = os.path.exists(path)
            can_write = False
            test_file = os.path.join(path, ".perm_test")
            with open(test_file, "w") as f:
                f.write("x")
            os.remove(test_file)
            can_write = True
            status[path] = {"exists": ok, "writable": can_write}
        except Exception as e:
            status[path] = {"exists": os.path.exists(path), "writable": False, "error": str(e)}
    return status
# -*- coding: utf-8 -*-
"""
modules/auth_oauth.py
Autenticação / registro OAuth-simulado para "O PREGADOR"
- funções para criar tokens simulados para Google / Apple / Email
- helpers para validar tokens simples
- instruções em docstring para integrar OAuth real no futuro
"""

import time
import hashlib
import hmac
import os
import json

# JWT-light simulada (não use em produção)
SECRET = os.environ.get("PREGADOR_SECRET", "troque_essa_chave_para_producao")

def make_token(username, method="local"):
    """
    Gera token simples (HMAC-SHA256) contendo username+method+timestamp.
    Use JWT real quando integrar.
    """
    payload = f"{username}|{method}|{int(time.time())}"
    sig = hmac.new(SECRET.encode(), payload.encode(), "sha256").hexdigest()
    token = f"{payload}|{sig}"
    return token

def verify_token(token, max_age_seconds=3600*24*30):
    """
    Verifica token simples gerado acima. Retorna dict com sucesso e dados.
    """
    try:
        parts = token.split("|")
        if len(parts) < 4:
            return {"ok": False, "error": "token malformado"}
        username, method, ts, sig = parts[0], parts[1], parts[2], parts[3]
        payload = f"{username}|{method}|{ts}"
        expected = hmac.new(SECRET.encode(), payload.encode(), "sha256").hexdigest()
        if not hmac.compare_digest(expected, sig):
            return {"ok": False, "error": "assinatura inválida"}
        age = time.time() - int(ts)
        if age > max_age_seconds:
            return {"ok": False, "error": "token expirado"}
        return {"ok": True, "username": username, "method": method}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# Simulações de fluxos OAuth (úteis para testes locais)
def simulate_google_oauth(username):
    # Simula receber email do Google e cria registro/token
    token = make_token(username, method="google")
    return {"ok": True, "token": token, "method": "google", "username": username}

def simulate_apple_oauth(username):
    token = make_token(username, method="apple")
    return {"ok": True, "token": token, "method": "apple", "username": username}

def simulate_email_verification(email):
    # Cria token de verificação e (simulado) enviaria e-mail
    token = make_token(email, method="email")
    return {"ok": True, "token": token, "method": "email", "username": email, "message": "Simulado: verifique seu e-mail para confirmar"}

# Instruções breves:
# - Para integrar Google OAuth real: use `google-auth-oauthlib` / `google-auth` ou google cloud console,
#   implemente flow de OAuth2 (redirect URI), e troque simulate_google_oauth por criação de registro real.
# - Para Apple Sign-in: siga Apple Developer docs, troque simulate_apple_oauth por flow real.
# - Para Email verification: utilize um serviço SMTP (ou SendGrid/Mailgun) para enviar link com token.
# -*- coding: utf-8 -*-
"""
modules/ui_helpers.py
Componentes UI e Gráficos aprimorados (plug-and-play)
- inject_css_modern: atualiza CSS com correções de espaçamento das fontes e responsividade
- modern_radar: versão com cores e animação plotly pronta
- modern_gauge: gauge responsivo com rótulos
- small helpers: card, pill_label
"""

import streamlit as st

def inject_css_modern(cfg):
    """
    Injeta CSS moderno. Recebe cfg (dict) com keys: theme_color, font_family, font_size.
    Mantém nomes e 'casca' do app; melhora espaçamento de fontes e responsividade.
    """
    color = cfg.get("theme_color", "#D4AF37")
    font = cfg.get("font_family", "Inter")
    fsize = cfg.get("font_size", 18)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&family=Cinzel:wght@500;800&display=swap');
    :root {{ --gold: {color}; --bg: #000; --panel: #0A0A0A; --txt: #EAEAEA; }}
    .stApp {{ background: var(--bg); color: var(--txt); font-family: '{font}', Inter, sans-serif; font-size: {fsize}px; }}
    h1,h2,h3 {{ color: var(--gold); font-family: 'Cinzel', serif; letter-spacing: 1px; }}
    .tech-card {{ background: #0b0b0b; border-left: 3px solid var(--gold); padding: 14px; border-radius:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.6); }}
    .stTextInput input, .stTextArea textarea {{ color: var(--txt); background: #0a0a0a; border:1px solid #222; padding:8px; }}
    .prime-logo {{ filter: drop-shadow(0 0 6px rgba(212,175,55,0.2)); }}
    @media (max-width: 700px) {{
        .stApp {{ font-size: {max(14, int(fsize*0.85))}px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def card(title, body):
    st.markdown(f"<div class='tech-card'><strong>{title}</strong><div style='margin-top:8px'>{body}</div></div>", unsafe_allow_html=True)

def pill_label(text, theme_color):
    st.markdown(f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,0.03);border:1px solid {theme_color};color:{theme_color};font-size:12px'>{text}</span>", unsafe_allow_html=True)

# Gráficos simples (convenience wrappers — usa plotly se disponível)
def modern_radar(categories, values, title, theme_color="#D4AF37"):
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line=dict(color=theme_color, width=2)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0,100], showgrid=True, gridcolor="#222")), margin=dict(t=30,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(title, list(zip(categories, values)))

def modern_gauge(value, title, theme_color="#D4AF37"):
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta={'reference': 50},
            title={'text': title},
            gauge={'axis': {'range': [0,100]}, 'bar': {'color': theme_color}, 'steps': [{'range':[0,50],'color':'#2b2b2b'},{'range':[50,100],'color':'#111111'}]}
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.write(f"{title}: {value}%")
# -*- coding: utf-8 -*-
"""
modules/utils.py
Funções utilitárias pequenas para harmonizar com o app principal:
- safe_filename: remove espaços problemáticos e caracteres
- read_json_safe / write_json_safe: wrappers sobre SafeIO (alternativa)
- normalize_font_name: corrige espaços e nomes de fontes para CSS
"""

import re
import json
import os

def safe_filename(name):
    """
    Normaliza um nome para usar em filesystem: replace espaços por _, remove acentos básicos.
    """
    s = name.strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9A-Za-z_\-\.]", "", s)
    return s or "file"

def read_json_safe(path, default=None):
    default = default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def write_json_safe(path, data):
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

def normalize_font_name(fname):
    """
    Remove espaços e caracteres estranhos para injetar em CSS safe.
    Ex: 'Inter, sans-serif' -> 'Inter'
    """
    if not fname: return "Inter"
    base = fname.split(",")[0]
    base = base.strip().strip("'\"")
    return base
   
