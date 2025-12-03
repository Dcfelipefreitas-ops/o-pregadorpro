import streamlit as st
import os
import json
from datetime import datetime

# --------- CONFIGURAÇÃO GLOBAL ---------
st.set_page_config(
    page_title="O PREGADOR",
    page_icon="✝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------- CARREGA MÓDULOS ---------
from modules.editor import editor_page
from modules.biblioteca import biblioteca_page
from modules.sermoes import sermoes_page
from modules.gabinete import gabinete_page
from modules.membros import membros_page
from modules.estatisticas import estatisticas_page
from modules.sincronizacao import sincronizacao_page
from modules.conta import conta_page

# --------- SIDEBAR ---------
menu = st.sidebar.radio(
    "📂 Navegação",
    [
        "✍️ Editor de Sermões",
        "📚 Biblioteca",
        "📖 Sermões Salvos",
        "🧩 Gabinete Pastoral",
        "👥 Rebanho",
        "📊 Estatísticas",
        "☁️ Sincronização",
        "⚙️ Conta e Configurações"
    ]
)

# --------- ROTAS ---------
if menu == "✍️ Editor de Sermões":
    editor_page()

elif menu == "📚 Biblioteca":
    biblioteca_page()

elif menu == "📖 Sermões Salvos":
    sermoes_page()

elif menu == "🧩 Gabinete Pastoral":
    gabinete_page()

elif menu == "👥 Rebanho":
    membros_page()

elif menu == "📊 Estatísticas":
    estatisticas_page()

elif menu == "☁️ Sincronização":
    sincronizacao_page()

elif menu == "⚙️ Conta e Configurações":
    conta_page()
    
