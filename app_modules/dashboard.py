import streamlit as st
from datetime import datetime
from .core import _read_json_safe, _write_json_atomic, DB_FILES
from .utils import TextUtils

def render_dashboard():
    st.title("🛡️ Painel de Controle e Cuidado")
    tabs_care = st.tabs(["📝 Check-in Emocional", "⚖️ Teoria da Permissão", "📋 Rotina & Liturgia"])

    # Check-in
    with tabs_care[0]:
        st.markdown("<div class='tech-card'><b>LIVRO DA ALMA (Diário)</b></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1,2])
        with c1:
            input_mood = st.select_slider("Como você se sente?", options=["Esgotamento","Cansaço","Neutro","Bem","Pleno"])
            input_note = st.text_area("Observações do dia", height=100)
            if st.button("REGISTRAR ESTADO"):
                data = _read_json_safe(DB_FILES["SOUL_METRICS"])
                if isinstance(data, list): data = {"historico": data}
                elif not isinstance(data, dict): data = {"historico": []}
                data.setdefault("historico", []).append({
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "humor": input_mood,
                    "nota": input_note
                })
                if _write_json_atomic(DB_FILES["SOUL_METRICS"], data):
                    st.success("Registro gravado.")
                else:
                    st.error("Erro ao gravar.")

        with c2:
            st.markdown("**Histórico Recente**")
            data = _read_json_safe(DB_FILES["SOUL_METRICS"])
            history = data.get("historico", [])[-5:] if isinstance(data, dict) else (data[-5:] if isinstance(data, list) else [])
            for item in reversed(history):
                if isinstance(item, dict):
                    date = item.get('data','-'); humor = item.get('humor', item.get('estado','-')); nota = item.get('nota', item.get('obs','-'))
                else:
                    date = str(item); humor = '-'; nota = '-'
                st.info(f"{date} | Estado: {humor} | Obs: {nota}")

    # Permissão & Rotina: (mantener lo principal, puedes extender)
    with tabs_care[1]:
        st.markdown("Teoria da Permissão - versão modular")
        p_fail = st.slider("Permissão para Falhar/Não Saber", 0, 100, 50)
        p_feel = st.slider("Permissão para Sentir Dor/Ira", 0, 100, 50)
        p_rest = st.slider("Permissão para Parar/Descansar", 0, 100, 50)
        st.metric("Média de Permissão", f"{(p_fail+p_feel+p_rest)//3}%")

    with tabs_care[2]:
        cfg = _read_json_safe(DB_FILES["CONFIG"])
        routine = cfg.get("rotina_pastoral", [])
        st.subheader("Liturgia Pessoal & Rotina")
        progress = 0
        for task in routine:
            if st.checkbox(task, key=f"chk_{task}"):
                progress += 1
        if routine:
            st.progress(progress / len(routine))