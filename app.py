# app.py - O PREGADOR (consolidado)
import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import math
import shutil
import random
import logging
import hashlib
from datetime import datetime
from io import BytesIO

# Optional rich editor (quill)
try:
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except Exception:
    QUILL_AVAILABLE = False

# ------------------------------
# CONFIG / DIRS / LOG
# ------------------------------
ROOT = "Dados_Pregador_V29"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto"),
    "LOGS": os.path.join(ROOT, "System_Logs"),
    "BIB_CACHE": os.path.join(ROOT, "BibliaCache")
}
DBS = {
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "USERS": os.path.join(DIRS["USER"], "users_db.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
}

for p in DIRS.values():
    os.makedirs(p, exist_ok=True)

logging.basicConfig(filename=os.path.join(DIRS["LOGS"], "system.log"), level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

# ------------------------------
# SafeIO (atomic read/write)
# ------------------------------
class SafeIO:
    @staticmethod
    def ler_json(caminho, default_return):
        try:
            if not os.path.exists(caminho):
                return default_return
            with open(caminho, 'r', encoding='utf-8') as f:
                c = f.read().strip()
                return json.loads(c) if c else default_return
        except Exception as e:
            logging.error(f"Read Error {caminho}: {e}")
            return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            tmp = caminho + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            os.replace(tmp, caminho)
            # backup copy
            try:
                shutil.copy2(caminho, os.path.join(DIRS["BACKUP"], os.path.basename(caminho) + ".bak"))
            except Exception:
                pass
            return True
        except Exception as e:
            logging.error(f"Write Error {caminho}: {e}")
            return False

# ------------------------------
# Basic helpers: encryption, export
# ------------------------------
# detect crypto
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_OK = True
except Exception:
    CRYPTO_OK = False

def encrypt_sermon_aes(password, plaintext):
    if not CRYPTO_OK:
        raise RuntimeError("Cryptography não disponível")
    import os, hashlib
    key = hashlib.sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ct).decode('utf-8')

def decrypt_sermon_aes(password, b64payload):
    if not CRYPTO_OK:
        raise RuntimeError("Cryptography não disponível")
    import hashlib
    data = base64.b64decode(b64payload)
    nonce = data[:12]
    ct = data[12:]
    key = hashlib.sha256(password.encode()).digest()
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode('utf-8')

# export HTML -> DOCX flexible
try:
    import mammoth
    HTML2DOCX = "mammoth"
except Exception:
    try:
        from html2docx import html2docx
        HTML2DOCX = "html2docx"
    except Exception:
        HTML2DOCX = None

def export_html_to_docx_better(title, html_content, out_path):
    if HTML2DOCX == "mammoth":
        import mammoth
        with open(out_path, "wb") as docx_file:
            results = mammoth.convert_to_docx(html_content)
            docx_file.write(results.value)
        return out_path
    elif HTML2DOCX == "html2docx":
        from html2docx import html2docx
        with open(out_path, "wb") as f:
            f.write(html2docx(html_content))
        return out_path
    else:
        # fallback: python-docx plain paragraphs
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title or 'Documento', level=1)
            import re
            plain = re.sub(r"<.*?>", "", html_content or "")
            for line in plain.splitlines():
                doc.add_paragraph(line)
            doc.save(out_path)
            return out_path
        except Exception as e:
            raise RuntimeError('Nenhum método disponível para converter HTML->DOCX: ' + str(e))

# ------------------------------
# Parser: many formats (TXT/JSON/XML/USFM/DOCX/PDF/EPUB/ZIP)
# ------------------------------
def parse_theword_export(path):
    """
    Tenta extrair textos de um arquivo (TheWord/Logos/USFM/JSON/XML/DOCX/PDF/EPUB/TXT/HTML/SWORD/ZIP).
    Retorna texto plano (máx 10000 chars) ou None se falhar.
    """
    try:
        if not os.path.exists(path):
            return None
        ext = os.path.splitext(path)[1].lower()

        # text-like files
        if ext in ['.txt', '.html', '.htm', '.xml', '.json', '.usfm']:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
            # USFM heuristics
            if ext == '.usfm' or raw.lstrip().startswith('\\id') or '\\c ' in raw:
                import re
                # very simple cleanup of backslash tags
                cleaned = re.sub(r'\\\w+\b', '', raw)
                cleaned = re.sub(r'\{[^}]*\}', '', cleaned)
                return cleaned.strip()[:10000]
            # XML/HTML heuristics
            if ext in ['.xml', '.html', '.htm'] or raw.lstrip().startswith('<'):
                try:
                    import re
                    verses = re.findall(r'<verse[^>]*>(.*?)</verse>', raw, flags=re.DOTALL|re.IGNORECASE)
                    if verses:
                        return '\n'.join(v.strip() for v in verses)[:10000]
                    # fallback: strip tags
                    text = re.sub(r'<[^>]+>', '', raw)
                    return text.strip()[:10000]
                except Exception:
                    return raw.strip()[:10000]
            # JSON
            if ext == '.json' or raw.strip().startswith('{'):
                try:
                    data = json.loads(raw)
                    texts = []
                    def walk(o):
                        if isinstance(o, dict):
                            for k, v in o.items():
                                walk(v)
                        elif isinstance(o, list):
                            for i in o: walk(i)
                        elif isinstance(o, str):
                            if len(o) > 10:
                                texts.append(o)
                    walk(data)
                    return '\n'.join(texts)[:10000]
                except Exception:
                    return raw.strip()[:10000]

        # DOCX
        if ext == '.docx':
            try:
                from docx import Document
                doc = Document(path)
                parts = [p.text for p in doc.paragraphs]
                return '\n'.join(parts)[:10000]
            except Exception:
                with open(path, 'rb') as f:
                    return f.read()[:10000].decode('utf-8', errors='ignore')

        # PDF
        if ext == '.pdf':
            try:
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(path)
                    texts = []
                    for p in reader.pages:
                        try:
                            texts.append(p.extract_text() or '')
                        except Exception:
                            pass
                    return '\n'.join(texts)[:10000]
                except Exception:
                    import PyPDF2
                    reader = PyPDF2.PdfFileReader(path)
                    texts = []
                    for i in range(reader.numPages):
                        texts.append(reader.getPage(i).extractText())
                    return '\n'.join(texts)[:10000]
            except Exception:
                with open(path, 'rb') as f:
                    return f.read()[:10000].decode('utf-8', errors='ignore')

        # EPUB
        if ext == '.epub':
            try:
                from ebooklib import epub
                book = epub.read_epub(path)
                items = []
                for item in book.get_items():
                    # item.get_type() returns ebooklib.ITEM_DOCUMENT constant (usually 9)
                    try:
                        cont = item.get_content().decode('utf-8', errors='ignore')
                        import re
                        cont = re.sub(r'<[^>]+>', '', cont)
                        items.append(cont)
                    except Exception:
                        pass
                return '\n'.join(items)[:10000]
            except Exception:
                with open(path, 'rb') as f:
                    return f.read()[:10000].decode('utf-8', errors='ignore')

        # ZIP / packages (TheWord / Logos / SWORD)
        if ext in ['.zip', '.bz2', '.tgz', '.tar', '.gz', '.vpl', '.conf'] or 'theword' in path.lower() or 'logos' in path.lower():
            try:
                import zipfile
                texts = []
                if zipfile.is_zipfile(path):
                    with zipfile.ZipFile(path, 'r') as z:
                        for name in z.namelist():
                            if name.lower().endswith(('.txt', '.usfm', '.xml', '.html', '.json', '.htm')):
                                with z.open(name) as fh:
                                    texts.append(fh.read().decode('utf-8', errors='ignore'))
                else:
                    with open(path, 'rb') as f:
                        texts.append(f.read().decode('utf-8', errors='ignore'))
                if texts:
                    return '\n'.join(texts)[:10000]
            except Exception:
                pass

        # generic fallback - read bytes and decode
        try:
            with open(path, 'rb') as f:
                return f.read()[:10000].decode('utf-8', errors='ignore')
        except Exception:
            return None
    except Exception as e:
        logging.error('parse_theword_export failed: %s', e)
        return None

# ------------------------------
# Library indexer (scan user folders)
# ------------------------------
def index_user_books(folder=None):
    """
    Escaneia pasta do usuário para encontrar formatos suportados.
    Por padrão escaneia ~/Documents
    """
    base = folder or os.path.join(os.path.expanduser('~'), 'Documents')
    results = []
    exts = {'.usfm', '.xml', '.json', '.txt', '.pdf', '.epub', '.docx', '.html', '.htm', '.zip', '.bz2', '.conf', '.vpl', '.tgz', '.tar', '.gz'}
    for root, dirs, files in os.walk(base):
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                results.append(os.path.join(root, f))
    return results

def user_books_ui():
    st.markdown('### Meus livros locais')
    custom = st.text_input('Pasta a escanear (deixe vazio para Documents)', value='')
    if st.button('Escanear pasta de livros'):
        folder = custom.strip() or None
        with st.spinner('Escaneando...'):
            hits = index_user_books(folder)
            st.success(f'Encontrados {len(hits)} arquivos')
            for i, p in enumerate(hits[:200]):
                st.markdown(f'- **{os.path.basename(p)}** — `{p}`')
            if len(hits) > 200:
                st.info('Mostrando apenas os primeiros 200 arquivos.')
    st.markdown('---')

# ------------------------------
# Hybrid Bible fetch: online (bible-api.com) + local cache fallback
# ------------------------------
def get_bible_verse(reference, prefer='almeida', allow_online=True):
    """
    Pipeline híbrido:
    1) Tenta API pública (https://bible-api.com/) se internet e permitido
    2) Se falhar, tenta cache local (Dados_Pregador_V29/BibliaCache/)
    3) Se ainda falhar, retorna mensagem de erro amigável
    """
    reference = reference.strip()
    cache_dir = DIRS['BIB_CACHE']
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = hashlib.sha256(reference.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, cache_key + ".json")

    # 1) online
    if allow_online:
        try:
            import requests
            # bible-api.com supports /book+chapter:verse (english). We attempt a simple call.
            url = f"https://bible-api.com/{requests.utils.requote_uri(reference)}"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                # data usually contains 'text'
                text = data.get('text') or (data.get('verses') and ' '.join(v.get('text','') for v in data.get('verses')))
                # save to cache
                SafeIO.salvar_json(cache_path, {"source": "bible-api.com", "ref": reference, "text": text, "fetched": datetime.now().isoformat()})
                return {"source": "online", "text": text}
        except Exception as e:
            logging.warning("Bible API online failed: %s", e)

    # 2) local cache
    try:
        cached = SafeIO.ler_json(cache_path, {})
        if cached and cached.get('text'):
            return {"source": "cache", "text": cached.get('text')}
    except Exception:
        pass

    # 3) local fallback - if the app contains a small ARA/ACF file under DATA
    local_candidates = [
        os.path.join(ROOT, 'local_bibles', 'ARA.txt'),
        os.path.join(ROOT, 'local_bibles', 'ACF.txt'),
        os.path.join(ROOT, 'local_bibles', 'KJV.txt'),
    ]
    for p in local_candidates:
        if os.path.exists(p):
            txt = ''
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    txt = f.read()
                # try to find the reference string simply (naive)
                # e.g. find "João 3:16" or "John 3:16"
                if reference in txt:
                    # return snippet +- 300 chars
                    idx = txt.find(reference)
                    start = max(0, idx-300)
                    end = min(len(txt), idx+600)
                    snippet = txt[start:end]
                    return {"source": "local_file", "text": snippet}
            except Exception:
                continue

    return {"source": "none", "text": f"Não foi possível obter '{reference}' via API nem via cache local."}

# ------------------------------
# Minimal AccessControl and Gamification (keeps previous state)
# ------------------------------
class AccessControl:
    DEFAULT_USERS = {"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}

    @staticmethod
    def _hash(text):
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def register(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        u_upper = username.upper().strip()
        if u_upper in users:
            return False, "USUÁRIO JÁ EXISTE."
        if not username or not password:
            return False, "PREENCHA TUDO."
        users[u_upper] = AccessControl._hash(password)
        SafeIO.salvar_json(DBS['USERS'], users)
        return True, "REGISTRO OK."

    @staticmethod
    def login(username, password):
        users = SafeIO.ler_json(DBS['USERS'], {})
        if not users and username.upper() == "ADMIN" and password == "1234":
            return True
        u_upper = username.upper().strip()
        hashed = AccessControl._hash(password)
        if u_upper in users:
            stored = users[u_upper]
            if len(stored) != 64:
                return stored == password
            return stored == hashed
        return False

# ------------------------------
# Default app state and UI boot
# ------------------------------
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18, "enc_password": "", "bible_api": {}, "prefer_translation": "ARA"})

# UI layout
st.set_page_config(page_title="O PREGADOR", layout="wide")
if "hide_menu" not in st.session_state:
    st.session_state.hide_menu = False

# Login flow (simple)
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if not st.session_state["logado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<h2 style='text-align:center'>O PREGADOR</h2>", unsafe_allow_html=True)
        tl, tr = st.tabs(["ENTRAR", "REGISTRAR"])
        with tl:
            with st.form("gate"):
                u = st.text_input("ID", placeholder="IDENTIFICAÇÃO")
                p = st.text_input("SENHA", type="password", placeholder="SENHA")
                if st.form_submit_button("ACESSAR"):
                    if AccessControl.login(u, p):
                        st.session_state["logado"] = True
                        st.session_state["user_name"] = u.upper()
                        st.success("BEM VINDO.")
                        st.experimental_rerun()
                    else:
                        st.error("NEGO A VOS CONHECER.")
        with tr:
            with st.form("reg"):
                nu = st.text_input("Novo ID")
                np = st.text_input("Senha", type="password")
                if st.form_submit_button("CRIAR"):
                    ok, msg = AccessControl.register(nu, np)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
    st.stop()

# After login: main app
# top toggle to hide sidebar/menu while working
col_main, col_toggle = st.columns([0.87, 0.13])
with col_toggle:
    if st.button("Ocultar Menu" if not st.session_state.hide_menu else "Mostrar Menu"):
        st.session_state.hide_menu = not st.session_state.hide_menu

if not st.session_state.hide_menu:
    menu = st.sidebar.radio("SISTEMA", [
        "Teoria da Permissão",
        "Cuidado Pastoral",
        "Gabinete Pastoral",
        "Biblioteca",
        "Configurações"
    ], index=0)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Usuário: **{st.session_state.get('user_name','ANON')}**")
    if st.sidebar.button("LOGOUT (SALVAR)"):
        # simple logout
        st.session_state["logado"] = False
        st.experimental_rerun()
else:
    # when hidden, default to Gabinete
    menu = "Gabinete Pastoral"

# Pages
if menu == "Teoria da Permissão":
    st.title("📘 Teoria da Permissão")
    st.markdown("Ajuste as réguas de permissão interna para gerar um diagnóstico de saúde mental.")
    col1, col2 = st.columns(2)
    with col1:
        f = st.slider("Permissão para Falhar (Graça)", 0, 100, 50)
        s = st.slider("Permissão para Sentir (Humanidade)", 0, 100, 50)
    with col2:
        d = st.slider("Permissão para Descansar (Limite)", 0, 100, 50)
        suc = st.slider("Permissão para ter Sucesso (Dignidade)", 0, 100, 50)
    if st.button("RODAR DIAGNÓSTICO"):
        avg = (f + s + d + suc) / 4
        feedback = "Liberdade na Graça" if avg >= 60 else ("Em Progresso" if avg >= 30 else "Modo de Sobrevivência")
        st.metric("Índice de Permissão Interna", f"{int(avg)}/100")
        if avg < 50:
            st.error(feedback)
        else:
            st.success(feedback)

elif menu == "Cuidado Pastoral":
    st.title("💛 Cuidado Pastoral")
    st.markdown("Ferramentas para organização de visitas, acompanhamento e notas pastorais.")
    st.markdown("- Agenda de visitas (em breve)")
    st.markdown("- Registro de atendimentos (use o Gabinete para escrever relatórios)")

elif menu == "Biblioteca":
    st.title("📚 Biblioteca (Reformada)")
    st.markdown("Busca rápida via Google Books (filtrada para teologia reformada) e importação de recursos.")
    with st.form("google_books_search"):
        gb_query = st.text_input("Buscar livros (Google Books)", value="Reformed theology")
        gb_limit = st.number_input("Resultados", min_value=1, max_value=40, value=8)
        gb_submit = st.form_submit_button("Buscar")
    if gb_submit:
        try:
            import requests
            q = f"{gb_query} reformed theology"
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {"q": q, "maxResults": gb_limit}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                items = r.json().get('items', [])
                for i, it in enumerate(items):
                    info = it.get('volumeInfo', {})
                    st.markdown(f"**{info.get('title')}** — {', '.join(info.get('authors', []) or [])}")
                    st.write(info.get('description', '')[:400])
                    if st.button(f"Importar recurso #{i}", key=f"imp_{i}"):
                        dest = os.path.join(DIRS['GABINETE'], f"book_{it.get('id')}.json")
                        SafeIO.salvar_json(dest, info)
                        st.success("Recurso importado para Gabinete")
            else:
                st.error("Falha na consulta Google Books")
        except Exception as e:
            st.error(f"Erro ao buscar Google Books: {e}")

    st.markdown("---")
    st.markdown("**Meus livros locais**")
    user_books_ui()

elif menu == "Gabinete Pastoral":
    st.title("📝 Gabinete Pastoral — Criar Sermão / Esboço")
    METADATA_PATH = os.path.join(DIRS["SERMOES"], "metadata.json")
    if not os.path.exists(METADATA_PATH):
        SafeIO.salvar_json(METADATA_PATH, {"sermons": []})

    with st.expander("🎨 Personalizar Editor (opcional)"):
        font_size = st.slider("Tamanho da Fonte", 12, 40, st.session_state["config"].get("font_size", 18))
        theme = st.selectbox("Tema do Editor", ["Padrão", "Escuro", "Pergaminho", "Página Branca"])
        fullscreen = st.checkbox("Modo Tela Cheia")
        autosave = st.checkbox("Salvar automaticamente enquanto digita (autosave)", value=True)

    title_col, tags_col = st.columns([3,1])
    with title_col:
        st.session_state["titulo_ativo"] = st.text_input("Título do Sermão", st.session_state.get("titulo_ativo",""))
    with tags_col:
        tags_text = st.text_input("Tags (vírgula)", value=",".join(st.session_state.get("last_tags", [])))
        if st.button("Aplicar Tags"):
            st.session_state["last_tags"] = [t.strip() for t in tags_text.split(",") if t.strip()]

    st.markdown("---")

    # import area (many formats)
    st.markdown("### Importar recursos (TheWord / Logos / Tesla / USFM / DOCX / PDF / EPUB / ZIP)")
    uploaded = st.file_uploader("Carregar export (vários formatos)", accept_multiple_files=True)
    if uploaded:
        for uf in uploaded:
            dest = os.path.join(DIRS['GABINETE'], uf.name)
            with open(dest, 'wb') as f:
                f.write(uf.getbuffer())
            parsed = parse_theword_export(dest)
            if parsed:
                rid = f"resource_{int(time.time())}.txt"
                with open(os.path.join(DIRS['GABINETE'], rid), 'w', encoding='utf-8') as rf:
                    rf.write(parsed)
                st.success(f"Importado e convertido: {uf.name} -> {rid}")
            else:
                st.warning(f"Falha ao parsear: {uf.name}")

    # Editor
    if QUILL_AVAILABLE:
        toolbar = [
            [{"header": [1,2,3,False]}],
            ["bold","italic","underline","strike"],
            [{"color": []}, {"background": []}],
            [{"align": []}],
            [{"list": "ordered"}, {"list": "bullet"}],
            ["blockquote", "code-block"],
            ["link", "image"],
            ["clean"]
        ]
        content = st_quill(key="editor", value=st.session_state.get("texto_ativo", ""), toolbar=toolbar, height=420)
    else:
        st.warning("Componente rich-text não disponível — usando editor simples.")
        content = st.text_area("Editor Texto Plano (fallback)", value=st.session_state.get("texto_ativo", ""), height=420)

    # autosave
    if autosave and content != st.session_state.get("texto_ativo", ""):
        st.session_state["texto_ativo"] = content
        if st.session_state.get("titulo_ativo"):
            fname = f"{st.session_state['titulo_ativo'].strip() or 'SemTitulo'}.txt"
            try:
                with open(os.path.join(DIRS["SERMOES"], fname), 'w', encoding='utf-8') as f:
                    f.write(content or "")
                meta = SafeIO.ler_json(METADATA_PATH, {"sermons": []})
                entry = {"title": st.session_state.get("titulo_ativo","SemTitulo"), "file": fname, "tags": st.session_state.get("last_tags", []), "updated": datetime.now().isoformat()}
                replaced = False
                for i,e in enumerate(meta.get("sermons", [])):
                    if e.get("file") == fname:
                        meta["sermons"][i] = entry
                        replaced = True
                        break
                if not replaced:
                    meta.setdefault("sermons", []).append(entry)
                SafeIO.salvar_json(METADATA_PATH, meta)
            except Exception as e:
                logging.error("Autosave failed: %s", e)

    # Save / Export buttons
    col_save, col_export = st.columns([2,2])
    with col_save:
        if st.button("Salvar Sermão"):
            filename = f"{(st.session_state.get('titulo_ativo') or 'SemTitulo').strip()}.txt"
            path = os.path.join(DIRS["SERMOES"], filename)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content or "")
                meta = SafeIO.ler_json(METADATA_PATH, {"sermons": []})
                entry = {"title": st.session_state.get("titulo_ativo","SemTitulo"), "file": filename, "tags": st.session_state.get("last_tags", []), "updated": datetime.now().isoformat()}
                found=False
                for i,e in enumerate(meta.get("sermons", [])):
                    if e.get("file") == filename:
                        meta["sermons"][i] = entry
                        found=True
                        break
                if not found:
                    meta.setdefault("sermons", []).append(entry)
                SafeIO.salvar_json(METADATA_PATH, meta)
                st.success(f"Sermão salvo: {filename}")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

        if st.button("Salvar (Encriptado)"):
            try:
                cfg = st.session_state.get('config', {})
                pw = cfg.get('enc_password')
                if not pw:
                    st.error('Nenhuma senha de encriptação definida. Vá em Configurações e defina uma senha mestra.')
                else:
                    enc = encrypt_sermon_aes(pw, content or "")
                    filename = f"{(st.session_state.get('titulo_ativo') or 'SemTitulo').strip()}.enc"
                    with open(os.path.join(DIRS['GABINETE'], filename), 'w', encoding='utf-8') as f:
                        f.write(enc)
                    st.success(f"Sermão encriptado salvo: {filename}")
            except Exception as e:
                st.error(f"Falha ao encriptar: {e}")

    with col_export:
        if st.button("Exportar PDF"):
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                buf = BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                width, height = A4
                text_obj = c.beginText(40, height - 60)
                import textwrap, re
                plain = re.sub(r"<.*?>", "", content or "")
                for para in plain.split("\n\n"):
                    for line in textwrap.wrap(para, 90):
                        text_obj.textLine(line)
                    text_obj.textLine("")
                c.drawText(text_obj)
                c.showPage()
                c.save()
                buf.seek(0)
                outp = os.path.join(DIRS["SERMOES"], f"{(st.session_state.get('titulo_ativo') or 'sermao')}.pdf")
                with open(outp, 'wb') as f:
                    f.write(buf.read())
                with open(outp, 'rb') as fp:
                    b64 = base64.b64encode(fp.read()).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{os.path.basename(outp)}">Baixar PDF</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Exportação para PDF falhou: {e}")

        if st.button("Exportar DOCX"):
            try:
                title = st.session_state.get('titulo_ativo') or 'sermao'
                outp = os.path.join(DIRS["SERMOES"], f"{title}.docx")
                export_html_to_docx_better(title, content or "", outp)
                with open(outp, 'rb') as fp:
                    b64 = base64.b64encode(fp.read()).decode()
                st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="{os.path.basename(outp)}">Baixar DOCX</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Exportação para DOCX falhou: {e}")

    # Manager
    if st.button("Abrir Gerenciador de Sermões"):
        meta = SafeIO.ler_json(METADATA_PATH, {"sermons": []})
        for s in meta.get("sermons", [])[::-1]:
            c1, c2, c3 = st.columns([6,2,2])
            with c1:
                st.markdown(f"**{s.get('title')}** — {', '.join(s.get('tags', []))} — atualizado {s.get('updated')}")
            with c2:
                if st.button(f"Abrir##{s.get('file')}", key=f"open_{s.get('file')}"):
                    try:
                        with open(os.path.join(DIRS["SERMOES"], s.get('file')), 'r', encoding='utf-8') as fh:
                            st.session_state['texto_ativo'] = fh.read()
                            st.session_state['titulo_ativo'] = s.get('title')
                            st.success('Sermão carregado no editor.')
                    except Exception as e:
                        st.error(f"Erro ao abrir: {e}")
            with c3:
                if st.button(f"Excluir##{s.get('file')}", key=f"del_{s.get('file')}"):
                    try:
                        os.remove(os.path.join(DIRS["SERMOES"], s.get('file')))
                        meta = SafeIO.ler_json(METADATA_PATH, {"sermons": []})
                        meta["sermons"] = [m for m in meta.get("sermons", []) if m["file"] != s.get('file')]
                        SafeIO.salvar_json(METADATA_PATH, meta)
                        st.success("Sermão removido.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Falha ao remover: {e}")

# Configurações
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    cfg = st.session_state.get("config", {})
    st.markdown("### Aparência")
    cfg['theme_color'] = st.text_input("Cor primária (hex)", value=cfg.get('theme_color', '#D4AF37'))
    cfg['font_size'] = st.number_input("Tamanho de fonte padrão", min_value=10, max_value=36, value=cfg.get('font_size', 18))
    st.markdown("---")
    st.markdown("### Encriptação")
    enc_pw = st.text_input("Senha mestra para encriptação local (não esqueça)", type='password', value=cfg.get('enc_password',''))
    if st.button("Salvar senha de encriptação"):
        cfg['enc_password'] = enc_pw
        st.session_state['config'] = cfg
        SafeIO.salvar_json(DBS["CONFIG"], st.session_state['config'])
        st.success("Senha salva (localmente). Para segurança, use um vault externo.")
    st.markdown("---")
    st.markdown("### API Bíblica / Cache")
    allowed = st.checkbox("Permitir buscas online para versos (usa bible-api.com se disponível)", value=True)
    cfg.setdefault('bible_api', {})['allow_online'] = allowed
    prefer = st.selectbox("Versão preferida (fallback local)", ["ARA", "ACF", "KJV", "WEB"], index=0)
    cfg['prefer_translation'] = prefer
    if st.button("Salvar configurações gerais"):
        st.session_state['config'] = cfg
        SafeIO.salvar_json(DBS["CONFIG"], st.session_state['config'])
        st.success("Configurações atualizadas.")

    st.markdown("---")
    st.markdown("### Requisitos opcionais (instale para melhor experiência)")
    st.code("\n".join([
        "pip install requests",
        "pip install python-docx",
        "pip install reportlab",
        "pip install cryptography",
        "pip install PyPDF2",
        "pip install ebooklib",
        "pip install mammoth html2docx",
        "pip install streamlit-quill"
    ]), language='bash')

# ------------------------------
# End - small helper for quick testing: search bible
# ------------------------------
st.markdown("---")
with st.expander("Busca Bíblica Rápida (teste)"):
    ref = st.text_input("Referência (ex: John 3:16 ou João 3:16)", value="")
    if st.button("Buscar Verso"):
        res = get_bible_verse(ref, prefer=st.session_state['config'].get('prefer_translation','ARA'), allow_online=st.session_state['config'].get('bible_api',{}).get('allow_online', True))
        if res['source'] == 'online' or res['source'] == 'cache' or res['source'] == 'local_file':
            st.success(f"Fonte: {res['source']}")
            st.write(res['text'])
        else:
            st.error(res['text'])
