import streamlit as st
import os
import requests
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import PyPDF2
from gtts import gTTS

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="O Pregador", layout="wide", page_icon="🧷", initial_sidebar_state="expanded")

# --- 2. GESTÃO DE ESTADO ---
if 'logado' not in st.session_state: st.session_state.update({'logado': False, 'user': ''})
if 'bg_url' not in st.session_state: st.session_state['bg_url'] = "https://images.unsplash.com/photo-1497294815431-9365093b7331?q=80&w=2070&auto=format&fit=crop"
if 'layout_split' not in st.session_state: st.session_state['layout_split'] = 60
if 'texto_esboco' not in st.session_state: st.session_state['texto_esboco'] = ""
if 'login_streak' not in st.session_state: st.session_state['login_streak'] = 1
if 'last_login' not in st.session_state: st.session_state['last_login'] = str(datetime.now().date())

# Função Gamificação
def update_streak():
    hoje = str(datetime.now().date())
    if st.session_state['last_login'] != hoje:
        st.session_state['login_streak
