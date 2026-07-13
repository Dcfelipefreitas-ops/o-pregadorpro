import re
import unicodedata
from typing import Optional

class TextUtils:
    # Compilamos os regexes apenas uma vez no escopo da classe para economizar processamento
    _UNSAFE_FILENAME_CHARS = re.compile(r'[^-\w.]')
    _HTML_TAGS = re.compile(r'<[^>]*>')
    _MULTIPLE_NEWLINES = re.compile(r'\n\s*\n')

    @classmethod
    def sanitize_filename(cls, name: str) -> str:
        """
        Transforma uma string em um nome de arquivo seguro.
        Remove acentos, substitui espaços por underscores e remove caracteres inválidos.
        """
        if not name:
            return "untitled"
            
        # Converte para string, remove espaços nas pontas e troca espaços internos por '_'
        s = str(name).strip().replace(" ", "_")
        
        # Decompõe caracteres acentuados (ex: 'ã' vira 'a' + '~') e remove os acentos
        s = unicodedata.normalize('NFKD', s)
        s = "".join([c for c in s if not unicodedata.combining(c)])
        
        # Remove qualquer caractere que não seja letra, número, hífen, underscore ou ponto
        sanitized = cls._UNSAFE_FILENAME_CHARS.sub('', s)
        
        # Garante que se o nome virar algo vazio (ex: se era só "!!!"), tenha um fallback
        return sanitized if sanitized else "untitled"

    @classmethod
    def clean_html_tags(cls, text: str) -> str:
        """
        Remove tags HTML substituindo-as por quebras de linha e limpa excessos de espaçamento.
        """
        if not text:
            return ""
            
        # Substitui as tags por quebra de linha
        cleaned = cls._HTML_TAGS.sub('\n', text)
        
        # Evita que fiquem 5 quebras de linha seguidas caso houvesse muitas tags juntas
        return cls._MULTIPLE_NEWLINES.sub('\n', cleaned).strip()

    @classmethod
    def normalize_font(cls, font_name: Optional[str]) -> str:
        """
        Extrai o primeiro nome de fonte de uma lista estilo CSS (ex: '"Open Sans", sans-serif' -> 'Open Sans').
        """
        if not font_name or not font_name.strip():
            return "Inter"
            
        # Pega a primeira fonte antes da vírgula, limpa espaços e remove aspas simples/duplas
        first_font = font_name.split(",")[0]
        return first_font.strip().replace("'", "").replace('"', '')
