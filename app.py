# -*- coding: utf-8 -*-
import os
import json
import logging
import uuid
import hashlib
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any
os.makedirs(os.path.join(SYSTEM_ROOT, "acervo_pastoral"), exist_ok=True)
# ==============================================================================
# 01. ESTÉTICA GABINETE: VISUAL MINISTERIAL PROFISSIONAL
# ==============================================================================
st.set_page_config(
    page_title="DISCIPULADO | PR FELIPE FREITAS",
    page_icon="✝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_ministerial_ui():
    """Injeta a arquitetura visual para ambiente de Discipulado."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        
        .main { background-color: #0b0e14; color: #e0e0e0; }
        .stDeployButton { display: none !important; }
        
        /* Estilo dos Cards do Painel */
        .ministerial-card {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #D4AF37;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid rgba(212, 175, 55, 0.1);
            margin-bottom: 20px;
        }
        .status-ready { color: #28a745; font-weight: bold; font-size: 0.8rem; }
        .message-in { background: #1a232e; padding: 12px; border-radius: 5px; margin-bottom: 8px; border-left: 3px solid #2b5c8f; }
    </style>
    """, unsafe_allow_html=True)

inject_ministerial_ui()

# ==============================================================================
# 02. NÚCLEO DE DADOS E SEGURANÇA
# ==============================================================================
SYSTEM_ROOT = "Dados_Pregador_V31"
os.makedirs(os.path.join(SYSTEM_ROOT, "db"), exist_ok=True)

def hashlib_sha256(value):
    return hashlib.sha256(value.encode()).hexdigest()

def _read_json_safe(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception: return default

def _write_json_atomic(p, d):
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=4)
        return True
    except: return False

# ==============================================================================
# 03. ACESSO AO SISTEMA (LOGIN E IDENTIDADE)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align:center; color:#D4AF37; padding-top:40px;'>PORTAL DE DISCIPULADO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Gabinete Pastoral Pr. Felipe Freitas</p>", unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.8, 1])
    with col_c:
        tab1, tab2 = st.tabs(["🔐 ACESSO RESTRITO", "📝 NOVO CADASTRO"])
        
        with tab1:
            with st.form("f_login"):
                u_input = st.text_input("NOME DE USUÁRIO").upper().strip()
                p_input = st.text_input("SENHA DE ACESSO", type="password")
                col_b1, col_b2 = st.columns(2)
                if col_b1.form_submit_button("CONECTAR"):
                    users = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
                    if u_input in users and users[u_input].get("hash") == hashlib_sha256(p_input):
                        st.session_state["current_user"] = u_input
                        st.session_state["user_role"] = users[u_input].get("role", "MEMBRO")
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else: st.error("Dados incorretos.")
                if col_b2.form_submit_button("ENTRAR COMO VISITANTE"):
                    st.session_state["current_user"] = "VISITANTE"
                    st.session_state["user_role"] = "MEMBRO"
                    st.session_state["logged_in"] = True
                    st.rerun()

        with tab2:
            with st.form("f_reg"):
                n_user = st.text_input("NOME PARA CADASTRO").upper().strip()
                n_pass = st.text_input("SENHA", type="password")
                if st.form_submit_button("CONFIRMAR"):
                    if n_user and n_pass:
                        db_p = os.path.join(SYSTEM_ROOT, "db", "users_db.json")
                        usrs = _read_json_safe(db_p, default={})
                        role = "ADMIN" if n_user == "ADMIN" or not usrs else "MEMBRO"
                        usrs[n_user] = {"hash": hashlib_sha256(n_pass), "role": role, "data": datetime.now().strftime("%d/%m/%Y")}
                        _write_json_atomic(db_p, usrs)
                        st.success("Cadastro realizado!")
    st.stop()

# ==============================================================================
# 04. MENU PRINCIPAL (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown(f"👤 **CONECTADO:** `{st.session_state['current_user']}`")
    st.caption(f"Perfil: {st.session_state['user_role']}")
    st.divider()
    
    modulos = ["📊 Resumo do Ministério", "📚 Material de Estudo", "✍️ Esboços e Sermões", "💬 Comunicação Direta", "⚙️ Definições"]
    app_mode = st.radio("Selecione o Módulo:", modulos)

    if st.session_state.get("user_role") == "MEMBRO":
        with st.expander("💬 ACONSELHAMENTO PASTORAL"):
            txt_sos = st.text_area("Sua mensagem privada:")
            if st.button("Enviar para o Pr. Felipe"):
                m_path = os.path.join(SYSTEM_ROOT, "db", "msgs.json")
                todas = _read_json_safe(m_path, default=[])
                todas.append({"de": st.session_state["current_user"], "texto": txt_sos, "data": datetime.now().strftime("%H:%M")})
                _write_json_atomic(m_path, todas)
                st.success("Mensagem enviada.")

    if st.button("SAIR DO SISTEMA"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==============================================================================
# 05. PAINEL DE GESTÃO EXCLUSIVA (SOMENTE ADMIN)
# ==============================================================================
if st.session_state["user_role"] == "ADMIN":
    with st.sidebar:
        st.divider()
        if st.checkbox("⚙️ PAINEL DE GESTÃO (SECRETARIA)"):
            app_mode = "GESTAO_PASTORAL"

if app_mode == "GESTAO_PASTORAL":
    st.title("🗄️ Secretaria Ministerial")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👥 Lista de Inscritos")
        usrs = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "users_db.json"), default={})
        for u, d in usrs.items():
            if isinstance(d, dict): # PREVINE O ERRO QUE DEU ANTES
                r = d.get("role", "Membro")
                dt = d.get("data", "S/D")
                st.write(f"🔹 **{u}** | {r} | Início: {dt}")
    with col2:
        st.subheader("📬 Pedidos de Oração / Aconselhamento")
        m_list = _read_json_safe(os.path.join(SYSTEM_ROOT, "db", "msgs.json"), default=[])
        for m in reversed(m_list):
            with st.chat_message("user"):
                st.write(f"**De: {m.get('de')}** | {m.get('data')}")
                st.write(m.get('texto'))
# --- ADICIONE ESTE BLOCO DENTRO DO IF DA GESTAO_PASTORAL ---
    with st.expander("➕ PUBLICAR NOVO LIVRO/MATERIAL"):
        with st.form("form_livro"):
            titulo_livro = st.text_input("Título da Obra")
            subtitulo_livro = st.text_input("Subtítulo ou Volume")
            categoria = st.selectbox("Categoria", ["Discipulado", "Teologia", "Vida Cristã", "Família"])
            conteudo_livro = st.text_area("Conteúdo do Livro (Texto ou Link para PDF)", height=300)
            
        
        with st.form("form_importacao"):
            t_obra = st.text_input("Título do Livro/Material")
            cat = st.selectbox("Categoria", ["Discipulado", "Teologia", "Sermões", "Ebooks"])
            tipo_entrada = st.radio("Origem do Material", ["Importar Arquivo do PC (PDF/DOCX)", "Digitar Texto Manual"])
            
            # Campo de Upload (Aparece se selecionar importar)
            uploaded_file = None
            conteudo_txt = ""
            if "Importar" in tipo_entrada:
                uploaded_file = st.file_uploader("Escolha o arquivo no seu computador", type=["pdf", "docx", "txt", "epub"])
            else:
                conteudo_txt = st.text_area("Cole ou escreva o conteúdo aqui", height=200)

            if st.form_submit_button("📁 INCORPORAR AO ACERVO"):
                db_livros = os.path.join(SYSTEM_ROOT, "db", "livros.json")
                acervo = _read_json_safe(db_livros, default=[])
                novo_id = str(uuid.uuid4())[:8]
                file_path = ""

                # Lógica para salvar o arquivo físico no servidor
                if uploaded_file is not None:
                    file_path = os.path.join(SYSTEM_ROOT, "acervo_pastoral", f"{novo_id}_{uploaded_file.name}")
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"Arquivo '{uploaded_file.name}' importado com sucesso!")
                
                # Salva o registro no Banco de Dados
                acervo.append({
                    "id": novo_id,
                    "titulo": t_obra,
                    "categoria": cat,
                    "tipo": tipo_entrada,
                    "conteudo_texto": conteudo_txt,
                    "file_path": file_path,
                    "nome_arquivo": uploaded_file.name if uploaded_file else "",
                    "data": datetime.now().strftime("%d/%m/%Y")
                })
                _write_json_atomic(db_livros, acervo)
                st.balloons()
# ==============================================================================
# 06. ÁREAS DE CONTEÚDO
# ==============================================================================
elif "Resumo" in app_mode:
    st.title("📊 Painel Ministerial")
    st.info("Sistemas de integridade ativos. Dados nominais de discipulado.")

elif "Estudo" in app_mode:
    st.title("📚 Biblioteca Digital")
    st.markdown("<p style='color:gray;'>Acervo intelectual exclusivo Pr. Felipe Freitas</p>", unsafe_allow_html=True)

    db_livros = os.path.join(SYSTEM_ROOT, "db", "livros.json")
    acervo = _read_json_safe(db_livros, default=[])

    if not acervo:
        st.info("Nenhum material disponível no acervo no momento.")
    else:
        for item in acervo:
            with st.container():
                st.markdown(f"""
                <div class='ministerial-card'>
                    <h3 style='margin:0; color:#D4AF37;'>{item['titulo']}</h3>
                    <small style='color:gray;'>Categoria: {item['categoria']} | Adicionado: {item['data']}</small>
                </div>
                """, unsafe_allow_html=True)

                # Se o material for texto, abre o expansor. Se for arquivo, mostra o botão de baixar.
                if "Importar" in item['tipo']:
                    if os.path.exists(item['file_path']):
                        with open(item['file_path'], "rb") as f:
                            st.download_button(
                                label=f"📥 BAIXAR MATERIAL: {item['nome_arquivo']}",
                                data=f,
                                file_name=item['nome_arquivo'],
                                mime="application/octet-stream"
                            )
                    else:
                        st.error("Erro: O arquivo físico não foi encontrado no servidor.")
                else:
                    with st.expander("📖 ABRIR PARA LEITURA"):
                        st.markdown(item['conteudo_texto'])
            st.divider()
    if not acervo:
        st.info("O Pastor ainda não publicou materiais neste módulo.")
    else:
        # Filtro de Categoria
        cats = list(set([l['categoria'] for l in acervo]))
        filtro = st.multiselect("Filtrar por Categoria:", cats, default=cats)

        for livro in acervo:
            if livro['categoria'] in filtro:
                with st.container():
                    st.markdown(f"""
                    <div class='ministerial-card'>
                        <h3 style='margin:0; color:#D4AF37;'>{livro['titulo']}</h3>
                        <small style='color:gray;'>{livro['categoria']} | Publicado em: {livro['data']}</small>
                        <p style='margin-top:10px;'>{livro['subtitulo']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"📖 LER: {livro['titulo']}"):
                        st.markdown(livro['conteudo'])
                        st.divider()
                        st.caption("Dica: Você pode copiar o texto acima para seus estudos pessoais.")
    

elif "Esboços" in app_mode:
    st.title("✍️ Esboços Pastoral")
    t_esb = st.text_input("Tema Central")
    c_esb = st.text_area("Desenvolvimento Homilético", height=400)
    if st.button("Arquivar Manuscrito"): st.success("Salvo com sucesso.")

elif "Comunicação" in app_mode:
    st.title("💬 Central Ministerial")
    st.write("Fique por dentro das novidades da nossa rede.")

elif "Definições" in app_mode:
    st.title("⚙️ Configurações do Sistema")
    st.caption("Firmware: 3.1 | Gabinete de TI Pastoral")
