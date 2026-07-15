import streamlit as st

def inject_nasa_ui():
    st.markdown("""
    <style>
        /* Importação de Fontes de Alta Legibilidade */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stCodeBlock, code, .monospace-font {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Estética "Mission Control" */
        .main {
            background-color: #0e1117;
            color: #e0e0e0;
        }

        /* Card Profissional */
        .nasa-card {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #D4AF37;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 15px;
            border: 1px solid rgba(212, 175, 55, 0.2);
        }

        .status-badge {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: #1a2c3e;
            color: #4da3ff;
            border: 1px solid #4da3ff;
        }
    </style>
    """, unsafe_allow_html=True)

def pastoral_card(titulo, subtitulo, stats):
    st.markdown(f"""
    <div class="nasa-card">
        <div style="display: flex; justify-content: space-between;">
            <span class="status-badge">Integridade de Dados: Nominal</span>
            <span style="font-size: 10px; color: gray;">{stats}</span>
        </div>
        <h3 style="margin: 10px 0 5px 0; color: #D4AF37;">{titulo}</h3>
        <p style="font-size: 14px; color: #999;">{subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)
