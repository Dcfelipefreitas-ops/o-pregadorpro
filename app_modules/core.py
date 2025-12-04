import os, json, shutil, uuid, logging
from datetime import datetime

SYSTEM_ROOT = "Dados_Pregador_V31"
LOG_PATH = os.path.join(SYSTEM_ROOT, "System_Logs")

DIRECTORY_STRUCTURE = {
    "ROOT": SYSTEM_ROOT,
    "SERMONS": os.path.join(SYSTEM_ROOT, "Sermoes"),
    "GABINETE": os.path.join(SYSTEM_ROOT, "Gabinete_Pastoral"),
    "USER_CONFIG": os.path.join(SYSTEM_ROOT, "User_Data"),
    "BACKUP_VAULT": os.path.join(SYSTEM_ROOT, "Auto_Backup_Oculto"),
    "LIBRARY_CACHE": os.path.join(SYSTEM_ROOT, "BibliaCache"),
    "MEMBERSHIP": os.path.join(SYSTEM_ROOT, "Membresia"),
    "NETWORK_LAYER": os.path.join(SYSTEM_ROOT, "Rede_Ministerial")
}

DB_FILES = {
    "CONFIG": os.path.join(DIRECTORY_STRUCTURE["USER_CONFIG"], "config.json"),
    "USERS_DB": os.path.join(DIRECTORY_STRUCTURE["USER_CONFIG"], "users_db.json"),
    "SOUL_METRICS": os.path.join(DIRECTORY_STRUCTURE["GABINETE"], "soul_data.json"),
    "STATS_METRICS": os.path.join(DIRECTORY_STRUCTURE["USER_CONFIG"], "db_stats.json"),
    "MEMBERS_DB": os.path.join(DIRECTORY_STRUCTURE["MEMBERSHIP"], "members.json"),
    "NETWORK_FEED": os.path.join(DIRECTORY_STRUCTURE["NETWORK_LAYER"], "feed_data.json")
}

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_PATH, "system_audit_omega.log"),
    level=logging.INFO,
    format='[%(asctime)s] | [%(levelname)s] | MODULE: %(module)s | MSG: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def _write_json_atomic(path, data):
    temp_path = f"{path}.tmp.{uuid.uuid4().hex}"
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        shutil.move(temp_path, path)
        return True
    except Exception as e:
        logging.error(f"Erro na escrita atômica {path}: {e}")
        return False

def _read_json_safe(path, default=None):
    if default is None: default = {}
    try:
        if not os.path.exists(path): return default
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return default
            return json.loads(content)
    except Exception as e:
        logging.error(f"Erro leitura JSON {path}: {e}")
        return default

def _ensure_empty_json_list(path):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    if not os.path.exists(path):
        _write_json_atomic(path, [])

def genesis_filesystem_integrity_check():
    logging.info("Genesis: checagem de integridade iniciada.")
    for key, path in DIRECTORY_STRUCTURE.items():
        os.makedirs(path, exist_ok=True)
        sentinel = os.path.join(path, ".sentinel")
        if not os.path.exists(sentinel):
            try:
                with open(sentinel, "w") as f:
                    f.write("System Integrity File - Do Not Delete")
            except Exception as e:
                logging.error(f"Erro sentinel {path}: {e}")

    if not os.path.exists(DB_FILES["CONFIG"]):
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

    if not os.path.exists(DB_FILES["USERS_DB"]):
        admin_hash = hashlib_sha256("admin")
        _write_json_atomic(DB_FILES["USERS_DB"], {"ADMIN": admin_hash})

    _ensure_empty_json_list(DB_FILES["NETWORK_FEED"])
    _ensure_empty_json_list(DB_FILES["MEMBERS_DB"])
    _ensure_empty_json_list(DB_FILES["SOUL_METRICS"])

def hashlib_sha256(value):
    import hashlib
    return hashlib.sha256(value.encode()).hexdigest()