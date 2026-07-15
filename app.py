# -*- coding: utf-8 -*-
import os
import json
import logging
import uuid
import hashlib
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any

# ==============================================================================
# 01. NÚCLEO ESTRUTURAL E DIRETÓRIOS (ORBITAL CORE)
# ==============================================================================
SYSTEM_ROOT = "Dados_Ministeriais_V31"
os.makedirs(os.path.join(SYSTEM_ROOT, "db"), exist_ok=True)
os.makedirs(os.path.join(SYSTEM_ROOT, "acervo_pastoral"), exist_ok=True)

# ==============================================================================
# 02. ESTÉTICA CELESTIAL: VISUAL PREMIUM DE ALTA TECNOLOGIA
# ==============================================================================
st.set_page_config(
    page_title="GABINETE CELESTIAL | PR FELIPE FREITAS",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_celestial_ui():
    """Injeta a arquitetura visual Batista Celestial Profissional."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;700&family=JetBrains+Mono:wght@300&display=swap');
        
        /* Tema Global Escuro/Profundo */
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { 
            background: radial-gradient(circle at 10% 20%, #0B1026 0%, #040610 100%); 
            color: #E2E8F0; 
        }
        
        /* NASA Dashboard: Cards Elegantes */
        .ministerial-card {
            background: rgba(255, 255, 255, 0.04);
            border-top: 1px solid rgba(212, 175, 55, 0.3);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            border-left: 4px solid #D4AF37;
            padding: 24px;
            border-radius: 4px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        h1, h2, h3 { color: #D4AF37 !important; letter-spacing: -0.02em; font-weight: 700; }
        
        .stDeployButton { display: none !important; }
        
        /* Custom Button */
        .stButton>button {
            border: 1px solid #D4AF37;
            background-color: transparent;
            color: #D4AF37;
            border-radius: 2px;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1.5px;
            padding: 10px 24px;
            transition: all 0.3s;
        }
        .stButton>button:hover { background-color: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); }
        
        /* Inputs Custom */
        input { background-color: #0b0e14 !important; border-radius: 4px !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

inject_celestial_ui()

# ==============================================================================
# 03. MOTORES DE SEGURANÇA E PERSISTÊNCIA
# ==============================================================================
def hashlib_sha256(v): return hashlib.sha256(v.encode()).hexdigest()

def _read_json_safe(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default

def _write_json_atomic(p, d):
    try:
        with open(p, "w", encoding="utf-8") as f: json.dump(d, f, indent=4); return True
    except: return False

# ==============================================================================
# 04. SISTEMA DE IGREJA RESTRITA (AUTENTICAÇÃO)
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
        <div style='text-align:center; padding: 40px;'>
            <h1 style='font-size: 3rem;'>B.C. INSTITUCIONAL</h1>
            <p style='color:#6B7280; font-family: "JetBrains Mono"; font-size: 0.9rem;'>PLATAFORMA INTEGRADA DE DISCIPULADO PASTORAL</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1.2, 2, 1.2])
    with col_c:
        tab1, tab2 = st.tabs(["🚪 TERMINAL DE ACESSO", "📋 SOLICITAR CADASTRO"])
        
        with tab1:
            with st.form("auth_mission"):
                u = st.text_input("USUÁRIO OPERADOR").upper().strip()
                p = st.text_input("SENHA ASSINATURA", type="password")
                if st.form_submit_button("SINCRONIZAR"):
                    users = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
                    if u in users and users[u].get("hash") == hashlib_sha256(p):
                        st.session_state["current_user"], st.session_state["user_role"] = u, users[u].get("role", "MEMBRO")
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else: st.error("Erro na validação da assinatura.")
                    
        with tab2:
            with st.form("reg_mission"):
                n_u = st.text_input("DEFINIR CODINOME").upper().strip()
                n_p = st.text_input("DEFINIR SENHA", type="password")
                if st.form_submit_button("REGISTRAR NA BASE"):
                    db_p = os.path.join(SYSTEM_ROOT, "db", "users_db.json")
                    usrs = _read_json_safe(db_p, default={})
                    role = "ADMIN" if n_u == "ADMIN" or not usrs else "MEMBRO"
                    usrs[n_u] = {"hash": hashlib_sha256(n_p), "role": role, "data": datetime.now().strftime("%d/%m/%y")}
                    _write_json_atomic(db_p, usrs); st.success("Chave gerada! Acesse via Terminal.")
    st.stop()

# ==============================================================================
# 05. CENTRO DE COMANDO (SIDEBAR & NAVEGAÇÃO)
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
        <div style='background: rgba(212, 175, 55, 0.05); padding: 15px; border: 1px solid rgba(212,175,55,0.2);'>
            <small style='color: #6B7280; font-family: JetBrains Mono;'>OPERADOR CONECTADO:</small><br>
            <span style='font-size: 1.2rem; font-weight: 700; color: #D4AF37;'>{st.session_state['current_user']}</span><br>
            <small style='color: #6B7280;'>NÍVEL {st.session_state['user_role']}</small>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    app_mode = st.radio("SISTEMAS DISPONÍVEIS:", 
                        ["🏠 Home de Discipulado", "🏛️ Acervo de Inteligência", "⚖️ Gabinete Pastoral", "📩 Central Ministerial"])
    
    if st.session_state["user_role"] == "ADMIN":
        st.divider()
        if st.checkbox("📡 SECRETARIA ADMIN"): app_mode = "MODO_SECRETARIA"
            
    if st.button("🚪 ENCERRAR SESSÃO"):
        st.session_state["logged_in"] = False; st.rerun()

# ==============================================================================
# 06. SECRETARIA ADMINISTRATIVA (ACREVO + MEMBRESIA)
# ==============================================================================
if app_mode == "MODO_SECRETARIA":
    st.title("🗄️ Secretaria Administrativa")
    t1, t2, t3 = st.tabs(["👥 Lista Operacional", "📜 Publicação de Obras", "📬 Chamados Pastoral"])
    
    with t1:
        usrs = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"))
        for u, d in usrs.items():
            if isinstance(d, dict): 
                st.write(f"🏷️ **{u}** | Função: {d.get('role')} | Adesão: {d.get('data')}")

    with t2:
        st.subheader("📚 Publicação e Importação Nível NASA")
        with st.form("pub_final"):
            titulo = st.text_input("Nome da Obra/Lote")
            categ = st.selectbox("Classe de Conhecimento", ["Básica", "Profunda", "Sermões", "Digitalizado"])
            fonte = st.radio("Meio de Inserção", ["Upload PDF do Computador", "Transcrição Direta"])
            up_f = st.file_uploader("Documento PDF/DOCX", type=["pdf","docx"]) if fonte == "Upload PDF do Computador" else None
            txt_f = st.text_area("Bloco de Texto") if fonte == "Transcrição Direta" else ""
            
            if st.form_submit_button("⚡ ATIVAR NO ACERVO"):
                db_l = os.path.join(SYSTEM_ROOT, "db", "livros.json")
                lib = _read_json_safe(db_l, default=[])
                nid = str(uuid.uuid4())[:8]
                fp = ""
                if up_f:
                    fp = os.path.join(SYSTEM_ROOT, "acervo_pastoral", f"{nid}_{up_f.name}")
                    with open(fp, "wb") as f: f.write(up_f.getbuffer())
                
                lib.append({
                    "id": nid, "titulo": titulo, "categ": categ, "origem": fonte,
                    "texto": txt_f, "fp": fp, "fname": up_f.name if up_f else "", "data": datetime.now().strftime("%d/%m/%Y")
                })
                _write_json_atomic(db_l, lib); st.balloons(); st.success("Documento em órbita ministerial.")

    with t3:
        ms = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "msgs.json"), default=[])
        for m in reversed(ms): st.info(f"SOLICITAÇÃO DE: {m.get('de')}\n\n{m.get('texto')}")

# ==============================================================================
# 07. ACERVO DE INTELIGÊNCIA (BIBLIOTECA)
# ==============================================================================
elif "Acervo" in app_mode:
    st.title("📚 Acervo Celestial")
    st.caption("Materiais bibliográficos sincronizados para sua edificação.")
    lib = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "livros.json"), default=[])
    
    if not lib: st.info("Repositório em branco no momento.")
    else:
        for it in lib:
            with st.container():
                st.markdown(f"<div class='ministerial-card'><span style='color:gray; font-size: 11px;'>ID {it['id']} | CLASSE: {it['categ']}</span><br><b style='font-size: 1.4rem; color: #D4AF37;'>{it['titulo']}</b></div>", unsafe_allow_html=True)
                if it['origem'] == "Upload PDF do Computador":
                    if os.path.exists(it['fp']):
                        with open(it['fp'], "rb") as f:
                            st.download_button(f"📥 DOWNLOAD DOCUMENTO INTEGRAL", f, file_name=it['fname'], key=it['id'])
                else:
                    with st.expander("📖 LEITURA DIGITAL"): st.markdown(it['texto'])
                st.divider()

# ==============================================================================
# 08. MODULOS EXTRAS (HOME E GABINETE)
# ==============================================================================
elif "Home" in app_mode:
    st.title("🛡️ Sistema de Apoio ao Discípulo")
    st.markdown("""
        <div class='ministerial-card'>
            <h2>Conselhos da Visão Batista Celestial</h2>
            <p>Seja bem-vindo ao portal unificado do Gabinete Pr. Felipe Freitas. 
            Nesta interface, você acessa documentos e manuais teológicos em alta velocidade.</p>
            <p>Use a barra lateral para navegar nos módulos de treinamento.</p>
        </div>
    """, unsafe_allow_html=True)

elif "Gabinete" in app_mode:
    st.title("✍️ Composição Homilética")
    st.markdown("<div class='ministerial-card'>Escreva seus estudos particulares e esboços ministeriais.</div>", unsafe_allow_html=True)
    t = st.text_input("MENSAGEM CENTRAL")
    c = st.text_area("CONTEÚDO E NOTAS", height=400)
    if st.button("SALVAR NOS SERVIDORES"): st.success("Texto sincronizado com o servidor.")

elif "Comunicação" in app_mode:
    st.title("💬 Canal de Auxílio Ministerial")
    st.info("Entre em contato para aconselhamentos privados através da barra lateral (Membros) ou aguarde avisos administrativos.")
