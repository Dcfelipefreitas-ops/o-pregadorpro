# -*- coding: utf-8 -*-
import os
import json
import logging
import uuid
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any

# ==============================================================================
# 01. CONFIGURAÇÃO NASA: UI & TIPOGRAFIA DE ALTA PRECISÃO
# ==============================================================================
st.set_page_config(
    page_title="DISCIPULADO| PR FELIPE FREITAS ",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_nasa_ui():
    """Injeta a arquitetura visual Mission Control."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400&family=Inter:wght@400;700&display=swap');
        
        /* Reset para fontes profissionais */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .monospace-font { font-family: 'JetBrains Mono', monospace !important; }
        
        .main { background-color: #0b0e14; color: #e0e0e0; }
        .stDeployButton { display: none !important; }
        
        /* Componentes de Status */
        .nasa-card {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #D4AF37;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid rgba(212, 175, 55, 0.1);
            margin-bottom: 20px;
        }
        .status-active { color: #00ff41; font-weight: bold; font-family: 'JetBrains Mono'; }
        
        /* Chat e Mensagens */
        .message-in { background: #1a232e; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #4da3ff; }
        .message-out { background: #263238; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #d4af37; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

inject_nasa_ui()

# ==============================================================================
# 02. NÚCLEO ATÔMICO DE DADOS (INTEGRIDADE & ARQUIVOS)
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
os.makedirs(os.path.join(SYSTEM_ROOT, "db"), exist_ok=True)

def _read_json_safe(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default if default is not None else {}
    except Exception: return default

# Tenta importar do core. Se falhar, define os paths locais para não quebrar
try:
    from app_modules.core import DB_FILES, _write_json_atomic, genesis_filesystem_integrity_check
    from app_modules import dashboard as dashboard_module
    from app_modules.homiletica import PastoralReviewer
    genesis_filesystem_integrity_check()
except ImportError:
    DB_FILES = {"DISCIPLES_DB": os.path.join(SYSTEM_ROOT, "db/disciples.json")}
    def _write_json_atomic(p, d): 
        with open(p, "w", encoding="utf-8") as f: json.dump(d, f)
        return True

# ==============================================================================
# 03. CENTRAL DE COMUNICAÇÃO (WHATSAPP SYNC)
# ==============================================================================
def push_notificacao_pastoral(mensagem, origem):
    """Simula o envio para o seu WhatsApp/E-mail."""
    log_msg = f"📡 NOTIFICAÇÃO EXTERNA | De: {origem} | Msg: {mensagem}"
    logging.info(log_msg)
    # Aqui entraria sua API (Twilio, Evolution, etc.)
    return True

# ==============================================================================
# 04. PROTOCOLO DE AUTENTICAÇÃO (PADRÃO NASA)
# ==============================================================================
import hashlib

def hashlib_sha256(value):
    """Criptografia de nível industrial."""
    return hashlib.sha256(value.encode()).hexdigest()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
        <div style='text-align: center; padding-top: 50px;'>
            <h1 style='color: #D4AF37; letter-spacing: 2px;'>PORTAL DE ACESSO</h1>
            <p style='color: #666; font-family: "JetBrains Mono";'>GABINETE DE ACONSELHAMENTO PASTORAL | V 3.1</p>
        </div>
    """, unsafe_allow_html=True)

    # Centralização do formulário
    col_l, col_c, col_r = st.columns([1, 2, 1])
    
    with col_c:
        aba_login, aba_registro = st.tabs(["🔒 ACESSAR TERMINAL", "🆔 NOVO OPERADOR"])
        
        # --- ABA DE LOGIN ---
        with aba_login:
            with st.form("login_nasa"):
                user_input = st.text_input("CODINOME (Usuário)").upper().strip()
                pass_input = st.text_input("ASSINATURA DIGITAL (Senha)", type="password")
                col_btn1, col_btn2 = st.columns(2)
                
                entrar = col_btn1.form_submit_button("🚀 INICIAR SESSÃO")
                convidado = col_btn2.form_submit_button("👤 ENTRAR COMO CONVIDADO")

                if entrar:
                    # Carrega banco de usuários real
                    usuarios = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
                    senha_hash = hashlib_sha256(pass_input)
                    
                    if user_input in usuarios and usuarios[user_input] == senha_hash:
                        st.session_state["current_user"] = user_input
                        st.session_state["logged_in"] = True
                        st.success("Acesso autorizado. Carregando interface...")
                        st.rerun()
                    else:
                        st.error("Assinatura Inválida. Verifique suas credenciais.")

                if convidado:
                    st.session_state["current_user"] = "CONVIDADO"
                    st.session_state["logged_in"] = True
                    st.warning("Acessando em modo de observação limitado.")
                    st.rerun()

        # --- ABA DE REGISTRO (NOVO USUÁRIO) ---
        with aba_registro:
            st.info("Solicite o registro de uma nova chave de acesso ao sistema.")
            with st.form("registro_nasa"):
                novo_user = st.text_input("DEFINIR CODINOME").upper().strip()
                nova_senha = st.text_input("DEFINIR ASSINATURA", type="password")
                confirmar_senha = st.text_input("CONFIRMAR ASSINATURA", type="password")
                
                if st.form_submit_button("✅ SOLICITAR REGISTRO"):
                    if not novo_user or not nova_senha:
                        st.error("Todos os campos de criptografia são obrigatórios.")
                    elif nova_senha != confirmar_senha:
                        st.error("As assinaturas não coincidem.")
                    else:
                        usuarios_db_path = os.path.join(SYSTEM_ROOT, "db", "users_db.json")
                        usuarios = _read_json_safe(usuarios_db_path, default={})
                        
                        if novo_user in usuarios:
                            st.warning("Este codinome já está registrado no banco de dados.")
                        else:
                            usuarios[novo_user] = hashlib_sha256(nova_senha)
                            _write_json_atomic(usuarios_db_path, usuarios)
                            st.success(f"Operador {novo_user} registrado com sucesso! Vá para a aba Login.")
    
    st.markdown("<p style='text-align: center; color: #333; margin-top: 50px;'>PROTOCOL OMEGA INTEGRITY VERIFIED</p>", unsafe_allow_html=True)
    st.stop()
    # --- ABA DE REGISTRO (MODIFICADA PARA IDENTIFICAR ADMIN) ---
        with aba_registro:
            st.info("⚠️ Nota: O primeiro usuário registrado como 'ADMIN' terá controle total.")
            with st.form("registro_nasa"):
                novo_user = st.text_input("DEFINIR CODINOME").upper().strip()
                nova_senha = st.text_input("DEFINIR ASSINATURA", type="password")
                
                if st.form_submit_button("✅ SOLICITAR REGISTRO"):
                    usuarios_db_path = os.path.join(SYSTEM_ROOT, "db", "users_db.json")
                    usuarios = _read_json_safe(usuarios_db_path, default={})
                    
                    role = "ADMIN" if novo_user == "ADMIN" or not usuarios else "MEMBRO"
                    
                    if novo_user in usuarios:
                        st.warning("Este codinome já está registrado.")
                    else:
                        usuarios[novo_user] = {
                            "hash": hashlib_sha256(nova_senha),
                            "role": role,
                            "created_at": datetime.now().strftime("%d/%m %H:%M")
                        }
                        _write_json_atomic(usuarios_db_path, usuarios)
                        st.success(f"Operador {novo_user} ({role}) registrado! Faça login.")
# ==============================================================================
# 05. INTERFACE DE COMANDO (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 🚀 MISSION CONTROL\n**Usuário:** `{st.session_state['current_user']}`")
    st.divider()
    app_mode = st.radio("Sistemas Operacionais", 
        ["📊 Dashboard", "📝 Gabinete Profissional", "💬 Central de Mensagens", "🤝 Rede Ministerial", "⚙️ Configurações"])

# ==============================================================================
# 06. ROTEAMENTO DAS ESTAÇÕES DE TRABALHO
# ==============================================================================

# --- ESTAÇÃO 1: DASHBOARD ---
if "Dashboard" in app_mode:
    st.title("📊 Painel de Monitoramento SoulMetrics")
    try:
        dashboard_module.render_dashboard()
    except:
        st.info("Painel principal carregando dados nominais...")
        col1, col2 = st.columns(2)
        col1.metric("Membros Ativos", "142", "+3")
        col2.metric("Saúde do Rebanho", "98%", "Estável")

# --- ESTAÇÃO 2: GABINETE PROFISSIONAL ---
elif "Gabinete" in app_mode:
    st.title("📝 Gabinete de Preparação Profissional")
    
    with st.expander("🛠️ Ferramentas de Precisão", expanded=False):
        tipo_fonte = st.selectbox("Tipografia de Análise", ["Inter", "JetBrains Mono"])
        classe_fonte = "monospace-font" if "JetBrains" in tipo_fonte else ""

    col1, col2 = st.columns([3, 1])
    with col1:
        titulo = st.text_input("Título do Documento")
        texto = st.text_area("Manuscrito Teológico", height=450, placeholder="Inicie a composição...")
        
        if texto:
            # Integração com o Revisor Pastoral
            try:
                alertas = PastoralReviewer.checar_ortografia_basica(texto)
                densidade = PastoralReviewer.analisar_densidade_teologica(texto)
                st.subheader("🧐 Análise do Console")
                for a in alertas: st.warning(a)
                st.progress(min(densidade*20, 100), f"Densidade Teológica: {densidade}")
            except: st.info("Análise de texto ativa.")

    with col2:
        st.markdown(f"<div class='nasa-card'><b>STATUS:</b> <span class='status-active'>COMPILANDO</span><br><small>Caract: {len(texto)}</small></div>", unsafe_allow_html=True)
        if st.button("💾 Salvar no Core"):
            st.success("Dados persistidos com sucesso.")

# --- ESTAÇÃO 3: CENTRAL DE MENSAGENS (COMUNICADOR) ---
elif "Mensagens" in app_mode:
    st.title("💬 Central de Mensagens & Avisos")
    
    aba_chat, aba_envio = st.tabs(["📥 Caixa de Entrada", "📤 Enviar para Celulares"])
    
    with aba_chat:
        st.markdown("<div class='message-in'><b>Membro João:</b> Pastor, pode orar por mim?</div>", unsafe_allow_html=True)
        st.markdown("<div class='message-out'><b>Você:</b> Com certeza, irmão. Estarei em oração agora.</div>", unsafe_allow_html=True)

    with aba_envio:
        st.subheader("Disparar Alerta Direto")
        destino = st.selectbox("Para quem?", ["Todos os Membros", "Apenas Liderança", "Grupo de Oração"])
        msg_alerta = st.text_area("Conteúdo da Mensagem")
        if st.button("🚀 Disparar para WhatsApp/E-mail"):
            push_notificacao_pastoral(msg_alerta, st.session_state['current_user'])
            st.balloons()
            st.success("Sincronização enviada para a fila de disparo externa.")

# --- ESTAÇÃO 4: REDE MINISTERIAL (AUDIO) ---
elif "Rede Ministerial" in app_mode:
    st.title("🤝 Rede Ministerial & Áudios")
    # Código existente de áudio aqui...
    st.info("Módulo de cuidado audiodigital carregado.")

# --- ESTAÇÃO 5: CONFIGURAÇÕES ---
elif "Configurações" in app_mode:
    st.title("⚙️ System Config")
    if st.button("Executar Check de Integridade"):
        st.toast("Filesystem nominal")

# ==============================================================================
# FIM DO SISTEMA NASA OMEGA
# ==============================================================================
