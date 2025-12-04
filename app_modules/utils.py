import re

class TextUtils:
    @staticmethod
    def sanitize_filename(name):
        s = str(name).strip().replace(" ", "_")
        return re.sub(r'(?u)[^-\w.]', '', s)

    @staticmethod
    def clean_html_tags(text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '\n', text)

    @staticmethod
    def normalize_font(font_name):
        if not font_name: return "Inter"
        return font_name.split(",")[0].strip().replace("'","").replace('"','')