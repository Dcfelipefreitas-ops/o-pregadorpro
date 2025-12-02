# app.py (VERSÃO UNIFICADA, CORRIGIDA, COM INTERLINEAR, NOTES (SQLite) E CONVERTERS)
import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO, StringIO
from datetime import datetime
import json
import sqlite3
import PyPDF2
from gtts import gTTS

# --- IMPORTS OPCIONAIS (evitam crash se não instalados) ---
try:
    import speech_recognition as sr
    SR_OK = True
except Exception:
    SR_OK = False

try:
    import google.generativeai as genai
    GENAI_INSTALLED = True
except Exception:
    GENAI_INSTALLED = False

try:
    from duckduckgo_search import DDGS
    DDGS_OK = True
except Exception:
    DDGS_OK = False

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(
    page_title="O Pregador",
    layout="wide",
    page_icon="🧷",
    initial_sidebar_state="expanded"
)

# --- 2. ESTADO INICIAL ---
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state:
    st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state:
    st.session_state['layout_split'] = 60
if 'texto_esboco' not in st.session_state:
    st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state:
    st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state:
    st.session_state['last_login'] = str(datetime.now().date())
if 'anuncio_atual' not in st.session_state:
    st.session_state['anuncio_atual'] = "📚 Bíblia de Estudo Premium"
if 'idioma' not in st.session_state:
    st.session_state['idioma'] = "Português"
if 'api_input' not in st.session_state:
    st.session_state['api_input'] = ""

USER = st.session_state.get('user', 'Admin')

# --- PASTAS & DB ---
os.makedirs("Banco_Biblia/bibles", exist_ok=True)
os.makedirs("Banco_Biblia/lexico", exist_ok=True)
os.makedirs("Banco_Biblia/crossrefs", exist_ok=True)
os.makedirs("Banco_Biblia/chave", exist_ok=True)
os.makedirs("Banco_Sermoes", exist_ok=True)
DB_NOTES = os.path.join("Banco_Sermoes", "notes.db")

# --- UTILIDADES & FUNÇÕES CENTRAIS ---

def update_streak():
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak'] += 1
        st.session_state['last_login'] = hoje

def safety_filter(prompt):
    blacklist = ["porn", "sex", "erotic", "xxx", "fraude", "hack", "roubar", "cassino", "bet", "apostas"]
    if any(p in prompt.lower() for p in blacklist):
        return False
    return True

def ai_brain(prompt, key, mode="Professor"):
    if not key:
        return "⚠️ Configure a Chave Google no Menu (st.secrets['GOOGLE_API_KEY'] ou campo de configurações)."
    if not safety_filter(prompt):
        return "🚫 Conteúdo bloqueado por segurança e ética."
    if not GENAI_INSTALLED:
        return "⚠️ google.generativeai não instalado no ambiente."
    try:
        genai.configure(api_key=key)
        roles = {
            "Razão": "Teólogo apologético e histórico. Use lógica e exegese.",
            "Sentimento": "Pastor pentecostal e acolhedor. Use emoção e consolo.",
            "Professor": "Professor de homilética. Corrija o texto e aponte erros.",
            "Coder": "Programador Senior Python/Streamlit.",
            "Tradutor": "Tradutor especialista em Teologia Cristã.",
            "Marketing": "Gere um título de livro cristão fictício."
        }
        lang_instruction = f"Responda sempre em {st.session_state.get('idioma','Português')}."
        system_prompt = f"MODO: {roles.get(mode,'Assistente')}\n{lang_instruction}\nCONTEXTO: {prompt}"
        model = genai.GenerativeModel('gemini-1.5-flash')
        out = model.generate_content(system_prompt)
        if hasattr(out, "text"):
            return out.text
        return str(out)
    except Exception as e:
        return f"Erro na Nuvem IA: {e}"

def transcrever_audio_file(uploaded_file):
    if not SR_OK:
        return "Transcrição local não disponível. Instale 'speechrecognition' e dependências."
    try:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="pt-BR")
                return text
            except sr.UnknownValueError:
                return "Não foi possível reconhecer o áudio."
            except sr.RequestError as e:
                return f"Erro no serviço de reconhecimento: {e}"
    except Exception as e:
        return f"Erro ao processar áudio: {e}"

def get_bible(ref):
    if not ref:
        return None
    try:
        r = ref.strip()
        r = r.replace(",", " ").replace(".", " ")
        if ":" in r:
            query = r.replace(" ", "+")
        else:
            parts = r.split()
            if len(parts) >= 3:
                book = parts[0]; chapter = parts[1]; verse = parts[2]
                query = f"{book}+{chapter}:{verse}"
            else:
                query = r.replace(" ", "+")
        url = f"https://bible-api.com/{query}?translation=almeida"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

def gerar_qr(link):
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def read_pdf_text(file_like):
    try:
        reader = PyPDF2.PdfReader(file_like)
        pages = []
        for i, p in enumerate(reader.pages[:40]):
            txt = p.extract_text()
            if txt:
                pages.append(txt)
        return "\n".join(pages)
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

# --- CSS (mantive visual e cores) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {{font-family: 'Inter', sans-serif;}}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{st.session_state['bg_url']}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stSidebar"], .stTextArea textarea, .stTextInput input, div[data-testid="stExpander"], .stSelectbox {{
        background-color: rgba(20, 22, 28, 0.90) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }}
    header, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1rem; max-width: 96%;}}
    .brand-box {{ text-align: center; padding-bottom: 20px; border-bottom: 1px solid #333; margin-bottom: 15px; }}
    .brand-title {{ font-size: 26px; font-weight: 800; color: #D4AF37; letter-spacing: 2px; margin-top: 5px; }}
    .ad-card {{ background: linear-gradient(135deg, #FFD700, #DAA520); color: black; padding: 12px; border-radius: 8px; margin-top: 10px; text-align: center; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
    .stButton button {{ background-color: #2b2b2b; color: #eee; border: 1px solid #444; border-radius: 6px; font-weight: 600; }}
    .stButton button:hover {{ border-color: #D4AF37; color: #D4AF37; background-color: #1a1a1a; }}
    .footer-insta {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #000; color: #666; text-align: center; padding: 6px; font-size: 11px; z-index: 9999; border-top: 1px solid #222; }}
    .footer-insta a {{ color: #E1306C; font-weight: bold; text-decoration: none; }}
    .interlinear-col {{ padding: 6px; border-left: 1px solid rgba(255,255,255,0.03); }}
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; background: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="90">
            <h1 style="color:#D4AF37; font-family:'Inter'; margin-top:10px;">O PREGADOR</h1>
            <p style="color:#ccc">Workstation Pastoral Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_seguro"):
            u = st.text_input("Identificação")
            p = st.text_input("Credencial", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA", type="primary"):
                if u in ["admin", "pastor", "felipe"] and p in ["1234", "pregar", "hope"]:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    update_streak()
                    st.rerun()
                else:
                    st.error("Acesso Não Autorizado")
    st.stop()

# --- APLICAÇÃO PRINCIPAL ---
USER = st.session_state.get('user', 'Admin')
PASTA = os.path.join("Banco_Sermoes", USER)
os.makedirs(PASTA, exist_ok=True)

# --- BÍBLIA + LÉXICO + STRONG + CROSSREFS + INTERLINEAR ---
def carregar_json(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

BIBLIA = carregar_json("Banco_Biblia/bibles/acf.json")
LEXICO = carregar_json("Banco_Biblia/lexico/strongs.json")
XREF   = carregar_json("Banco_Biblia/crossrefs/referencias.json")
KAI    = carregar_json("Banco_Biblia/chave/kai.json")
INTERLINEAR = carregar_json("Banco_Biblia/interlinear.json")  # formato: {"Book": {"3": {"16": {"pt":"...", "gr":"...", "strongs":["G25"]}}}}

def buscar_palavra(termo):
    resultados = []
    if not termo or not isinstance(termo, str):
        return resultados

    termo_raw = termo.strip()
    termo = termo_raw.lower()

    # Strong search pattern detection (G#### / H####)
    if (termo_raw.upper().startswith("G") or termo_raw.upper().startswith("H")) and termo_raw[1:].isdigit():
        for livro, capitulos in BIBLIA.items():
            for cap, versos in capitulos.items():
                for num, texto in versos.items():
                    if termo_raw.upper() in (texto or ""):
                        resultados.append((livro, cap, num, texto))
        return resultados

    # Operators AND, OR, NEAR
    if " AND " in termo_raw.upper():
        a, b = termo_raw.upper().split(" AND ", 1)
        a = a.lower(); b = b.lower()
        for livro, capitulos in BIBLIA.items():
            for cap, versos in capitulos.items():
                for num, texto in versos.items():
                    t = (texto or "").lower()
                    if a in t and b in t:
                        resultados.append((livro, cap, num, texto))
        return resultados

    if " OR " in termo_raw.upper():
        a, b = termo_raw.upper().split(" OR ", 1)
        a = a.lower(); b = b.lower()
        for livro, capitulos in BIBLIA.items():
            for cap, versos in capitulos.items():
                for num, texto in versos.items():
                    t = (texto or "").lower()
                    if a in t or b in t:
                        resultados.append((livro, cap, num, texto))
        return resultados

    if " NEAR " in termo_raw.upper():
        a, b = termo_raw.upper().split(" NEAR ", 1)
        a = a.lower(); b = b.lower()
        for livro, capitulos in BIBLIA.items():
            for cap, versos in capitulos.items():
                for num, texto in versos.items():
                    t = (texto or "").lower()
                    if a in t and b in t:
                        try:
                            posA = t.index(a)
                            posB = t.index(b)
                            if abs(posA - posB) < 200:
                                resultados.append((livro, cap, num, texto))
                        except ValueError:
                            continue
        return resultados

    # Wildcard *
    if termo_raw.endswith("*"):
        base = termo_raw[:-1].lower()
        for livro, capitulos in BIBLIA.items():
            for cap, versos in capitulos.items():
                for num, texto in versos.items():
                    t = (texto or "").lower()
                    if any(w.startswith(base) for w in t.split()):
                        resultados.append((livro, cap, num, texto))
        return resultados

    # Simple contains
    for livro, capitulos in BIBLIA.items():
        for cap, versos in capitulos.items():
            for num, texto in versos.items():
                if termo in (texto or "").lower():
                    resultados.append((livro, cap, num, texto))
    return resultados

def strongs_info(codigo):
    codigo = codigo.upper().strip()
    if codigo in LEXICO:
        return LEXICO[codigo]
    return "❌ Código não encontrado no Léxico Strong."

def referencias_cruzadas(ref):
    ref = ref.strip()
    return XREF.get(ref, [])

def chave_kai(term):
    term = term.lower().strip()
    return KAI.get(term, [])

def interlinear_entry(book, chapter, verse):
    try:
        return INTERLINEAR.get(book, {}).get(str(chapter), {}).get(str(verse), {})
    except Exception:
        return {}

# --- NOTES (SQLite) ---
def get_db_connection():
    conn = sqlite3.connect(DB_NOTES, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            book TEXT,
            chapter TEXT,
            verse TEXT,
            title TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn

def add_note(user, book, chapter, verse, title, content):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notes (user, book, chapter, verse, title, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user, book, str(chapter), str(verse), title, content, str(datetime.now())))
    conn.commit()
    conn.close()

def get_notes_for_verse(user, book, chapter, verse):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, content, created_at FROM notes
        WHERE user=? AND book=? AND chapter=? AND verse=?
        ORDER BY created_at DESC
    """, (user, book, str(chapter), str(verse)))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

# --- CONVERTERS (CSV / TSK -> JSON) ---
def convert_strongs_csv_to_json(csv_bytes):
    """
    Expects CSV with columns: code, lemma, transliteration, strong_type, definition
    Returns dict { "G1": {...}, "H2": {...} }
    """
    text = csv_bytes.decode('utf-8', errors='ignore')
    lines = [l for l in text.splitlines() if l.strip()]
    result = {}
    for i, line in enumerate(lines):
        # naive CSV parse (comma separated). For robust solution use csv module.
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            continue
        code = parts[0].upper()
        entry = {
            "lemma": parts[1] if len(parts) > 1 else "",
            "translit": parts[2] if len(parts) > 2 else "",
            "type": parts[3] if len(parts) > 3 else "",
            "def": parts[4] if len(parts) > 4 else ""
        }
        result[code] = entry
    return result

def convert_tsk_to_json(tsk_text):
    """
    Very simple converter for TSK-like files (Thematic Study Key). This is placeholder:
    Splits by lines, looks for verses like 'John 3:16 — text' and indexes them.
    """
    lines = [l.strip() for l in tsk_text.splitlines() if l.strip()]
    out = {}
    for line in lines:
        # try to find pattern "Book Chapter:Verse - text"
        parts = line.split('—', 1)
        if len(parts) == 2:
            ref = parts[0].strip()
            text = parts[1].strip()
            out[ref] = text
        else:
            # fallback append to last
            pass
    return out

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div class="brand-box">
        <img src="https://cdn-icons-png.flaticon.com/512/9430/9430594.png" width="50">
        <div class="brand-title">O PREGADOR</div>
        <div style="color:#4CAF50; font-size:12px; margin-top:5px">🟢 {st.session_state['login_streak']} Dias Online</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"Pastor(a): {USER.capitalize()}")

    menu_tabs = st.tabs(["📂 PROJETOS", "⚙️ CONFIG", "📱 SOCIAL"])
    api_input_local = st.session_state.get('api_input', '')

    with menu_tabs[0]:
        try:
            files = [f.replace(".txt", "") for f in os.listdir(PASTA) if f.endswith(".txt")]
        except Exception:
            files = []
        sel = st.radio("Selecione o Estudo:", ["+ Novo Projeto"] + files, label_visibility="collapsed")
        st.write("")
        if st.button("🚪 Sair do Sistema"):
            st.session_state['logado'] = False
            st.rerun()

    with menu_tabs[1]:
        st.write("**Personalização**")
        st.session_state['idioma'] = st.selectbox("Idioma da IA:", ["Português", "English", "Español"], index=0 if st.session_state.get('idioma', 'Português') == 'Português' else 1)
        tamanho = st.slider("Área do Editor", 30, 80, st.session_state['layout_split'])
        st.session_state['layout_split'] = tamanho
        novo_bg = st.text_input("Wallpaper URL:", st.session_state['bg_url'])
        if st.button("Aplicar Fundo"):
            st.session_state['bg_url'] = novo_bg
            st.rerun()
        st.divider()
        st.write("**Credenciais (opcional)**")
        api_input_local = st.text_input("Chave Google API:", type="password", value=st.session_state.get('api_input', ''))
        st.session_state['api_input'] = api_input_local

    with menu_tabs[2]:
        st.write("**Contato do Dev**")
        try:
            buf = BytesIO()
            img = gerar_qr("https://instagram.com/felipefreitashope")
            img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, caption="Scan para Instagram")
        except Exception:
            pass
        st.divider()
        st.markdown(f"""
        <div class="ad-card">
            📖 Sugestão:<br>{st.session_state['anuncio_atual']}<br>
            <a href="https://amazon.com.br" style="color:#000; text-decoration:underline;">ADQUIRIR AGORA</a>
        </div>
        """, unsafe_allow_html=True)

# --- ÁREA DE TRABALHO ---
ratio = st.session_state['layout_split'] / 100
c_editor, c_tools = st.columns([ratio, 1 - ratio])

# Gerenciamento de arquivo
txt_curr = ""
tit_curr = ""
if 'sel' not in locals():
    sel = "+ Novo Projeto"
if sel != "+ Novo Projeto":
    tit_curr = sel
    try:
        with open(os.path.join(PASTA, f"{sel}.txt"), "r", encoding="utf-8") as f:
            txt_curr = f.read()
    except Exception:
        txt_curr = ""

if 'last_file' not in st.session_state or st.session_state.get('last_file') != sel:
    st.session_state['texto_esboco'] = txt_curr
    st.session_state['last_file'] = sel

# EDITOR PRINCIPAL
with c_editor:
    c1, c2 = st.columns([3, 1])
    with c1:
        new_tit = st.text_input("TEMA", value=tit_curr, placeholder="Título da Pregação...", label_visibility="collapsed")
    with c2:
        if st.button("💾 GRAVAR", type="primary", use_container_width=True):
            if new_tit:
                save_path = os.path.join(PASTA, f"{new_tit}.txt")
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(st.session_state.get('texto_esboco', ''))
                    api_key = st.session_state.get('api_input', '') or st.secrets.get("GOOGLE_API_KEY", "")
                    if api_key and GENAI_INSTALLED:
                        sugestao = ai_brain(f"Indique 1 livro cristão clássico sobre: '{new_tit}'. Apenas título.", api_key, "Marketing")
                        st.session_state['anuncio_atual'] = sugestao
                    st.success("Estudo Salvo e Seguro!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    main_text = st.text_area("PAPEL", value=st.session_state.get('texto_esboco', ''), height=700, label_visibility="collapsed")
    st.session_state['texto_esboco'] = main_text

    st.caption("🛠️ Ações Rápidas de IA")

    st.markdown("**Ditar para o Editor (upload WAV recomendado)**")
    audio_file = st.file_uploader("Envie WAV (recomendado) ou MP3/M4A", type=['wav', 'mp3', 'm4a'], accept_multiple_files=False)
    if audio_file is not None:
        if audio_file.type == "audio/wav" or audio_file.name.lower().endswith(".wav"):
            st.info("Processando WAV...")
            texto_voz = transcrever_audio_file(audio_file)
            st.text_area("Transcrição", value=texto_voz, height=150)
            if st.button("Inserir transcrição no editor"):
                st.session_state['texto_esboco'] = st.session_state.get('texto_esboco', '') + "\n\n" + texto_voz
                st.rerun()
        else:
            st.warning("Formato diferente de WAV. Para MP3/M4A você precisa de 'pydub' + 'ffmpeg' no servidor para transcrição automática. Use download + ditado local se necessário.")

    b1, b2, b3 = st.columns(3)
    api_key = st.session_state.get('api_input', '') or st.secrets.get("GOOGLE_API_KEY", "")
    with b1:
        if st.button("✨ REVISAR ORTOGRAFIA"):
            if api_key and GENAI_INSTALLED:
                with st.spinner("Professor revisando..."):
                    res = ai_brain(f"Corrija apenas a gramática mantendo o sentido e estilo pastoral:\n{main_text}", api_key, "Professor")
                    st.code(res, language="text")
                    st.success("Copie o texto acima 👆")
            else:
                st.warning("Configure Google API e instale google.generativeai para usar revisão avançada.")
    with b2:
        if st.button("🗣 TRADUZIR TUDO"):
            if api_key and GENAI_INSTALLED:
                res = ai_brain(main_text, api_key, "Tradutor")
                st.session_state['texto_esboco'] = res
                st.rerun()
            else:
                st.warning("Configure Google API e instale google.generativeai para usar tradução.")
    with b3:
        if st.button("🎓 AVALIAR HOMILÉTICA"):
            if api_key and GENAI_INSTALLED:
                st.info(ai_brain(main_text, api_key, "Professor"))
            else:
                st.info("Configure Google API + google.generativeai para avaliação.")

    if new_tit and main_text != txt_curr:
        try:
            with open(os.path.join(PASTA, f"{new_tit}.txt"), "w", encoding="utf-8") as f:
                f.write(main_text)
        except Exception:
            pass

# SATÉLITE: ferramentas (IA, Bíblia, PDF, DEV)
with c_tools:
    st.markdown("#### 🧠 CENTRAL")
    tab_ia, tab_biblia, tab_pdf, tab_dev = st.tabs(["🤖 IA", "📖 BÍBLIA", "📚 LIVRO", "👨‍💻 DEV"])

    # IA
    with tab_ia:
        st.write("Conselheiro Virtual")
        ask = st.text_area("Pergunta:", height=100, placeholder="Digite sua dúvida teológica...")
        c_r, c_e = st.columns(2)
        if c_r.button("🧠 Razão"):
            if api_key:
                st.markdown(ai_brain(ask, api_key, "Razão"))
            else:
                st.warning("Configure Google API.")
        if c_e.button("❤️ Emoção"):
            if api_key:
                st.markdown(ai_brain(ask, api_key, "Sentimento"))
            else:
                st.warning("Configure Google API.")

    # BÍBLIA
    with tab_biblia:
        st.write("Consulta Rápida")
        ref = st.text_input("Verso (Ex: Jo 3 16 ou John 3:16)")
        if ref:
            bd = get_bible(ref)
            if bd:
                txt_b = bd.get('text', '')
                ref_label = bd.get('reference', ref)
                st.success(f"{ref_label}")
                st.write(txt_b)

                # Interlinear display (if available)
                try:
                    # attempt to parse common book name formatting
                    parts = ref.replace(":", " ").split()
                    book = parts[0] if parts else ""
                    chapter = parts[1] if len(parts) > 1 else ""
                    verse_num = parts[2] if len(parts) > 2 else ""
                    inter = interlinear_entry(book, chapter, verse_num)
                except Exception:
                    inter = {}

                if inter:
                    st.markdown("**Interlinear (se disponível localmente)**")
                    cols = st.columns([1,1,0.8])
                    cols[0].markdown(f"**PT:**\n{inter.get('pt','—')}")
                    cols[1].markdown(f"**Original:**\n{inter.get('orig','—')}")
                    cols[2].markdown(f"**Strongs:**\n{', '.join(inter.get('strongs',[])) if inter.get('strongs') else '—'}")

                ck1, ck2, ck3 = st.columns(3)
                if ck1.button("⬇ Inserir"):
                    st.session_state['texto_esboco'] += f"\n\n**{ref_label}**\n{txt_b}"
                    st.rerun()
                if ck2.button("🔊 Ouvir"):
                    try:
                        tts = gTTS(txt_b, lang='pt')
                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)
                        st.audio(mp3_fp, format='audio/mp3')
                    except Exception as e:
                        st.error(f"Erro Audio: {e}")
                if ck3.button("📝 Notas deste Verso"):
                    # show notes UI
                    try:
                        parts = ref.replace(":", " ").split()
                        book = parts[0]; chapter = parts[1]; verse_num = parts[2]
                    except Exception:
                        st.warning("Formato do verso inválido para notas (use 'Jo 3 16').")
                        book = chapter = verse_num = ""
                    if book:
                        rows = get_notes_for_verse(USER, book, chapter, verse_num)
                        st.markdown("### Notas salvas")
                        for row in rows:
                            nid, title, content, created_at = row
                            st.markdown(f"**{title}** — {created_at}")
                            st.write(content)
                            if st.button(f"Deletar {nid}"):
                                delete_note(nid)
                                st.success("Nota deletada")
                                st.rerun()
                        st.markdown("### Adicionar nova nota")
                        n_title = st.text_input("Título da nota")
                        n_content = st.text_area("Conteúdo da nota")
                        if st.button("Salvar nota"):
                            add_note(USER, book, chapter, verse_num, n_title or "Nota", n_content or "")
                            st.success("Nota salva")
                            st.rerun()
            else:
                st.warning("Versículo não encontrado (API offline ou formato inválido). Use 'Jo 3 16' ou 'John 3:16'.")

    # PDF
    with tab_pdf:
        st.write("Resumir Livro")
        pdf = st.file_uploader("Upload PDF", type="pdf")
        if pdf and st.button("Analisar PDF"):
            raw = read_pdf_text(pdf)
            st.success("Lido! Gerando resumo...")
            if api_key and GENAI_INSTALLED:
                summary = ai_brain(f"Resuma este texto teológico: {raw[:4000]}", api_key, "Professor")
                st.markdown(summary)
            else:
                st.write(raw[:2000])
                st.info("Para resumo automático configure Google API e instale google.generativeai.")

    # DEV: converters + misc
    with tab_dev:
        st.caption("Fábrica de Código e Ferramentas de Importação")
        st.markdown("**1) Convert Strongs CSV → JSON**")
        csv_file = st.file_uploader("Suba CSV de Strongs (code,lemma,translit,type,definition)", type=['csv'], key="csv_strongs")
        if csv_file and st.button("Converter CSV para JSON"):
            try:
                js = convert_strongs_csv_to_json(csv_file.read())
                out_path = "Banco_Biblia/lexico/strongs_converted.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(js, f, ensure_ascii=False, indent=2)
                st.success(f"Salvo em {out_path}")
            except Exception as e:
                st.error(f"Erro conversão: {e}")

        st.markdown("**2) Convert TSK-like → JSON**")
        tsk_file = st.file_uploader("Suba arquivo TSK (texto)", type=['txt'], key="tsk_file")
        if tsk_file and st.button("Converter TSK para JSON"):
            try:
                txt = tsk_file.read().decode('utf-8', errors='ignore')
                out = convert_tsk_to_json(txt)
                out_path = "Banco_Biblia/converted_tsk.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(out, f, ensure_ascii=False, indent=2)
                st.success(f"Salvo em {out_path}")
            except Exception as e:
                st.error(f"Erro conversão TSK: {e}")

        st.markdown("**3) Import Interlinear JSON**")
        inter_file = st.file_uploader("Suba JSON Interlinear (opcional)", type=['json'], key="inter_json")
        if inter_file and st.button("Instalar Interlinear"):
            try:
                content = json.load(inter_file)
                out_path = "Banco_Biblia/interlinear.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                st.success(f"Interlinear salvo em {out_path}")
            except Exception as e:
                st.error(f"Erro salvar interlinear: {e}")

        st.markdown("**4) Quick utilities**")
        if st.button("Verificar paths e permissões"):
            ok = True
            msgs = []
            for p in ["Banco_Biblia/bibles", "Banco_Biblia/lexico", "Banco_Biblia/chave", "Banco_Sermoes"]:
                try:
                    os.makedirs(p, exist_ok=True)
                    msgs.append(f"{p}: OK")
                except Exception as e:
                    ok = False
                    msgs.append(f"{p}: ERRO {e}")
            st.write("\n".join(msgs))
            if ok:
                st.success("Ambiente OK")
            else:
                st.error("Problemas detectados. Veja mensagens acima.")

# RODAPÉ
st.markdown("""
<div class="footer-insta">
    DESENVOLVEDOR: <a href="https://instagram.com/felipefreitashope" target="_blank">@FELIPEFREITASHOPE</a> 
    | V13 PLATINUM
</div>
""", unsafe_allow_html=True)
