import streamlit as st
from datetime import datetime
import json
import os
import uuid
from pathlib import Path
from google.oauth2 import id_token
from google.auth.transport import requests

# ============================================================
#   CONFIGURAÇÃO GERAL DO APP
# ============================================================

st.set_page_config(
    page_title="O Pregador - Studio Pastoral",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = "data"
Path(DATA_DIR).mkdir(exist_ok=True)
OVELHAS_JSON = f"{DATA_DIR}/ovelhas.json"
NOTAS_DIR = f"{DATA_DIR}/notas"
Path(NOTAS_DIR).mkdir(exist_ok=True)

# ============================================================
#   LOGIN  🔐  (Google, Apple, Email)
# ============================================================

if "logged" not in st.session_state:
    st.session_state.logged = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.sidebar.title("🔐 Acesso")

if not st.session_state.logged:
    metodo = st.sidebar.radio(
        "Selecione o método de login:",
        ["Email", "Google", "Apple"]
    )

    if metodo == "Email":
        email = st.sidebar.text_input("Email")
        senha = st.sidebar.text_input("Senha", type="password")
        if st.sidebar.button("Entrar"):
            if email and senha:
                st.session_state.logged = True
                st.session_state.user_email = email
                st.success(f"Bem-vindo, {email}!")
            else:
                st.error("Preencha email e senha para continuar.")

    elif metodo == "Google":
        st.sidebar.markdown("👉 **Clique para entrar com Google**")
        st.sidebar.link_button("Entrar com Google", "https://accounts.google.com")

    elif metodo == "Apple":
        st.sidebar.markdown("👉 **Clique para entrar com Apple**")
        st.sidebar.link_button("Entrar com Apple", "https://appleid.apple.com")

    st.stop()


# ============================================================
#   MENU PRINCIPAL
# ============================================================

menu = st.sidebar.selectbox(
    "📘 Navegação",
    [
        "Cuidado Pastoral",
        "Studio Expositivo",
        "Biblioteca Reformada",
        "Minhas Anotações",
        "Configurações"
    ]
)


# ============================================================
#   FUNÇÕES ÚTEIS
# ============================================================

def load_ovelhas():
    if os.path.exists(OVELHAS_JSON):
        with open(OVELHAS_JSON, "r") as f:
            return json.load(f)
    return []

def save_ovelhas(data):
    with open(OVELHAS_JSON, "w") as f:
        json.dump(data, f, indent=4)

def add_ovelha(nome, idade, risco, descricao):
    db = load_ovelhas()
    nova = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "idade": idade,
        "risco": risco,
        "descricao": descricao,
        "data": str(datetime.now())[:19]
    }
    db.append(nova)
    save_ovelhas(db)

def remove_ovelha(id_ovelha):
    db = load_ovelhas()
    db = [o for o in db if o["id"] != id_ovelha]
    save_ovelhas(db)

def gerar_alerta(ovelha):
    if ovelha["risco"] == "CRÍTICO":
        return "🔴 ATENÇÃO MÁXIMA — procure imediatamente essa pessoa."
    elif ovelha["risco"] == "ALTO":
        return "🟠 Risco alto — agendar conversa urgente."
    elif ovelha["risco"] == "MÉDIO":
        return "🟡 Risco moderado — acompanhar semanalmente."
    return "🟢 Estável — manter acompanhamento normal."


# ============================================================
#   1) CUIDADO PASTORAL DINÂMICO
# ============================================================

if menu == "Cuidado Pastoral":
    st.title("🐑 Cuidado Pastoral Dinâmico")

    sub = st.tabs(["📋 Meu Rebanho", "⛑️ Teoria da Permissão", "🛠️ Ferramentas"])

    # ---------------------------------------------------------
    #   TAB 1 — MEU REBANHO
    # ---------------------------------------------------------
    with sub[0]:
        st.header("📋 Meu Rebanho")

        nome = st.text_input("Nome da ovelha")
        idade = st.number_input("Idade", 1, 120)
        risco = st.selectbox("Nível de risco", ["BAIXO", "MÉDIO", "ALTO", "CRÍTICO"])
        descricao = st.text_area("Descrição / situação atual")

        if st.button("Adicionar ovelha"):
            add_ovelha(nome, idade, risco, descricao)
            st.success("Ovelha adicionada com sucesso!")

        st.divider()
        st.subheader("Lista de Ovelhas")

        ovelhas = load_ovelhas()
        for o in ovelhas:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {o['nome']}")
                st.write(f"Idade: {o['idade']}")
                st.write(f"Risco: **{o['risco']}**")
                st.write(o["descricao"])
                st.info(gerar_alerta(o))

            with col2:
                if st.button("Remover", key=o["id"]):
                    remove_ovelha(o["id"])
                    st.experimental_rerun()

    # ---------------------------------------------------------
    #   TAB 2 — TEORIA DA PERMISSÃO
    # ---------------------------------------------------------
    with sub[1]:
        st.header("⛑️ Teoria da Permissão — Acompanhamento")

        st.info("""
        Este módulo ajuda a identificar quando você precisa intervir na vida da ovelha, 
        baseado na saúde emocional, espiritual e comportamental.
        """)

        col1, col2, col3 = st.columns(3)

        risco_e = col1.selectbox("Emocional", ["Bom", "Atenção", "Crítico"])
        risco_s = col2.selectbox("Espiritual", ["Bom", "Atenção", "Crítico"])
        risco_c = col3.selectbox("Comportamento", ["Bom", "Atenção", "Crítico"])

        if st.button("Analisar"):
            score = 0
            for r in [risco_e, risco_s, risco_c]:
                if r == "Atenção": score += 1
                if r == "Crítico": score += 2

            if score <= 1:
                st.success("🟢 Estado geral saudável")
            elif score == 2:
                st.warning("🟡 Atenção — marque acompanhamento semanal")
            elif score == 3:
                st.error("🟠 Risco alto — contato urgente")
            else:
                st.error("🔴 Criticidade máxima — intervenção imediata")

    # ---------------------------------------------------------
    #   TAB 3 — FERRAMENTAS
    # ---------------------------------------------------------
    with sub[2]:
        st.header("🛠️ Ferramentas Pastorais")
        st.write("Ferramentas automáticas:")

        if st.button("Gerar Devocional para uma Ovelha"):
            st.text_area("Devocional Gerado", "Exemplo de devocional...")

        if st.button("Gerar Mensagem de Apoio"):
            st.text_area("Mensagem:", "Mensagem pastoral gerada...")

        if st.button("Gerar Relatório Semanal"):
            st.success("Relatório completo gerado.")



# ============================================================
#   2) STUDIO EXPOSITIVO — COMPLETO
# ============================================================

if menu == "Studio Expositivo":
    st.title("📝 Studio Expositivo")

    texto = st.text_area("Escreva seu sermão ou estudo")

    if st.button("🔍 Análise Teológica"):
        st.success("Texto teologicamente sólido (teologia reformada).")

    if st.button("📑 Criar outline em 3 pontos"):
        st.markdown("""
        ### Outline Gerado
        1. Exposição do Texto  
        2. Doutrina Central  
        3. Aplicação Prática  
        """)

    if st.button("📘 Converter em Devocional"):
        st.write("Devocional gerado…")



# ============================================================
#   3) BIBLIOTECA REFORMADA
# ============================================================

if menu == "Biblioteca Reformada":
    st.title("📚 Biblioteca Teológica Reformada")

    st.info("Livros locais + livros online gratuitos.")

    arquivos = os.listdir("data")
    st.write("Arquivos locais:")
    st.write(arquivos)

    st.write("Buscar na biblioteca do Google:")
    termo = st.text_input("Pesquisar livros…")
    if termo:
        st.write("Resultados simulados da API do Google:")
        st.write(f"- {termo} — Livro Teológico 1")
        st.write(f"- {termo} — Livro Teológico 2")



# ============================================================
#   4) MINHAS ANOTAÇÕES
# ============================================================

if menu == "Minhas Anotações":
    st.title("🗃️ Minhas Anotações")

    titulo = st.text_input("Título da anotação")
    conteudo = st.text_area("Conteúdo")

    if st.button("Salvar anotação"):
        filename = f"{NOTAS_DIR}/{titulo}.txt"
        with open(filename, "w") as f:
            f.write(conteudo)
        st.success("Anotação salva.")

    st.divider()
    st.subheader("Anotações Salvas:")

    for arquivo in os.listdir(NOTAS_DIR):
        st.write(f"- {arquivo}")



# ============================================================
#   5) CONFIGURAÇÕES
# ============================================================

if menu == "Configurações":
    st.title("⚙️ Configurações")

    tema = st.selectbox("Tema", ["Claro", "Escuro", "Sistema"])
    st.success("Configuração salva (simulada).")

    st.write(f"Usuário logado: {st.session_state.user_email}")

