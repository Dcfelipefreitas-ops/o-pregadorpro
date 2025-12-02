# helpers.py
import json
import os
import requests
import io
import PyPDF2
from pathlib import Path

# -------------------------
# I/O: carregar JSONs genéricos
# -------------------------
def read_json(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {}

# -------------------------
# IA GRATUITA (fallback)
# -------------------------
def ia_gratis(prompt: str, timeout: int = 15):
    """
    Tenta usar um endpoint público gratuito. Se falhar, retorna fallback.
    NOTE: endpoints públicos variam; para produção configure st.secrets com uma LLM privada.
    """
    try:
        url = "https://api-free-llm.gptfree.cc/v1/chat/completions"
        payload = {
            "model": "llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 700
        }
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        if isinstance(j, dict) and "choices" in j and len(j["choices"])>0:
            # compatibilidades diversas: try nested keys
            choice = j["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            if "text" in choice:
                return choice["text"]
        # fallback to raw text if structure differs
        return str(j)
    except Exception as e:
        # fallback: curta resposta sintetizada localmente
        return ("[IA gratuita indisponível].\n\nResumo automático (fallback):\n" +
                prompt[:1000] + "\n\n-- Configure st.secrets['GOOGLE_API_KEY'] para usar Gemini ou defina uma LLM local.")

# -------------------------
# Ler texto de PDF (primeiras páginas)
# -------------------------
def read_pdf_text(file_like, max_pages=60):
    try:
        reader = PyPDF2.PdfReader(file_like)
        pages = []
        for i, p in enumerate(reader.pages):
            if i >= max_pages: break
            t = p.extract_text()
            if t:
                pages.append(t)
        return "\n\n".join(pages)
    except Exception as e:
        return f"Erro lendo PDF: {e}"

# -------------------------
# Utilitário para salvar arquivo (texto)
# -------------------------
def save_text(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return str(p)

# -------------------------
# Script helper: construir JSONs a partir de BOM TXT público
# -------------------------
def naive_parse_bible_txt(raw_text):
    """
    Heurística simples para quebrar textos em livros->cap->verse.
    Isso é apenas um ponto de partida: resultados podem precisar de revisão.
    """
    import re
    books = {}
    # tenta achar padrões "BOOK NAME" e linhas com "1:1"
    verses = re.findall(r'([A-Za-zÀ-ú ]+?)\s+(\d+):(\d+)\s+([^\n]+)', raw_text)
    if verses:
        for b, c, v, txt in verses:
            b = b.strip()
            books.setdefault(b, {}).setdefault(c, {})[v] = txt.strip()
    else:
        # fallback: guarda tudo no 'raw'
        books["raw"] = {"1": {"1": raw_text[:1000]}}
    return books

def build_json_from_txt_file(txt_path, out_json_path):
    """
    Lê arquivo TXT local e cria JSON estruturado (heurístico).
    """
    p = Path(txt_path)
    if not p.exists():
        raise FileNotFoundError(txt_path)
    raw = p.read_text(encoding="utf-8", errors="ignore")
    structured = naive_parse_bible_txt(raw)
    outp = Path(out_json_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(outp)
# utils/bible_loader.py
import json
import os
from pathlib import Path

def load_bible_from_folder(folder_path="Banco_Biblia/bibles"):
    """
    Carrega todos os JSONs na pasta e os mescla num dicionário:
    { "Gênesis": {"1": {"1": "...", ...}}, "João": {...} }
    """
    folder = Path(folder_path)
    bible = {}
    if not folder.exists():
        return bible
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() == ".json":
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                # se o JSON contém estrutura por livros (ex.: {"Genesis": {...}}) -> merge
                for k, v in data.items():
                    bible[k] = v
            except Exception as e:
                print("Erro ao carregar", f, e)
    return bible

def get_verse(bible, book, chapter, verse):
    try:
        # tolerância: chapter/verse podem ser ints
        chapter = str(int(chapter))
        verse = str(int(verse))
        return bible[book][chapter][verse]
    except Exception:
        return "Verso não encontrado."
# utils/lexicon_loader.py
import json
from pathlib import Path

def load_lexicon(folder_path="Banco_Biblia/lexico"):
    folder = Path(folder_path)
    lexicons = {}
    if not folder.exists():
        return lexicons
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() == ".json":
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    lexicons[f.stem] = json.load(fh)
            except Exception as e:
                print("Erro carregando lexicon", f, e)
    return lexicons

def search_strongs(lexicons, strong_id):
    if not strong_id:
        return "Informe um ID Strong (ex: G25 ou H430)"
    sid = strong_id.strip().upper()
    for name, lex in lexicons.items():
        # lex pode ser dict com keys 'G25' etc.
        if sid in lex:
            return lex[sid]
    return "Número Strong não encontrado."
# utils/reference_search.py
def find_references(bible, keyword):
    """
    Busca palavra-chave em todos os versos e devolve lista de matches.
    """
    if not keyword:
        return []
    results = []
    for book, chapters in bible.items():
        for ch, verses in chapters.items():
            for v, text in verses.items():
                try:
                    if keyword.lower() in (text or "").lower():
                        results.append({"book": book, "chapter": ch, "verse": v, "text": text})
                except Exception:
                    continue
    return results
# utils/chave_kai.py
import json
from pathlib import Path

def load_kai(path="Banco_Biblia/chave/kai.json"):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_cross_references(kai_data, key_or_term):
    if not kai_data:
        return []
    # key_or_term pode ser "João 3:16" ou um tema "fé"
    k = key_or_term.strip().lower()
    if k in kai_data:
        return kai_data[k]
    # partial match on keys (tema)
    results = []
    for tk, refs in kai_data.items():
        if k in tk.lower():
            results.extend(refs)
    return results
