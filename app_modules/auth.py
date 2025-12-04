from .core import _read_json_safe, _write_json_atomic, DB_FILES
import hashlib, logging

class AccessGate:
    @staticmethod
    def login_check(username, password):
        db = _read_json_safe(DB_FILES["USERS_DB"])
        if username == "ADMIN" and password == "1234" and len(db) <= 1:
            return True
        user_hash = db.get(username.upper())
        if not user_hash:
            logging.warning(f"Login fail: {username}")
            return False
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        return pass_hash == user_hash

    @staticmethod
    def create_account(username, password):
        db = _read_json_safe(DB_FILES["USERS_DB"])
        if username.upper() in db:
            return False, "Usuário Duplicado."
        db[username.upper()] = hashlib.sha256(password.encode()).hexdigest()
        if _write_json_atomic(DB_FILES["USERS_DB"], db):
            return True, "Conta criada."
        return False, "Erro ao gravar."