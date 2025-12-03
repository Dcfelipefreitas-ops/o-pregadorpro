import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import random
import logging
import hashlib
from datetime import datetime, timedelta

# ==============================================================================
# [-] GENESIS PROTOCOL: AUTO-BOOT DE ARQUIVOS (NÃO APAGAR)
# ==============================================================================
ROOT = "Dados_Pregador_V31"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "USER": os.path.join(ROOT, "User_Data"),
    "MEMBROS": os.path.join(ROOT, "Membresia"),
    "CONFIG": os.path.join(ROOT, "Config")
}

def _genesis_boot():
    """Garante que as pastas e arquivos JSON existam antes de qualquer leitura."""
    for p in DIRS.values(): os.makedirs(p, exist_ok=True)
    
    # Usuários (Garante Admin)
    f_user = os.path.join(DIRS["USER"], "users_db.json")
    if not os.path.exists(f_user):
        with open(f_user, 'w') as f: json.dump({"ADMIN": hashlib.sha256("admin".encode()).hexdigest()}, f)
        
    # Membros (Lista Vazia)
    f_memb = os.path.join(DIRS["MEMBROS"], "members.json")
    if not os.path.exists(f_memb):
        with open(f_memb, 'w') as f: json.dump([], f)
        
    # Config (Visual)
    f_conf = os.path.join(DIRS["CONFIG"], "style_cfg.json")
    if not os.path.exists(f_conf):
        with open(f_conf, 'w') as f: json.dump({"theme_color": "#D4AF37", "font_size": 18}, f)

_genesis_boot()

# Instalação Automática (Se necessário)
try:
    import plotly.graph_objects as go
    import pandas as pd
    from streamlit_quill import st_quill
except ImportError:
    st.warning("Instalando gráficos e bibliotecas visuais... Aguarde.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly", "pandas", "streamlit-quill", "--quiet"])
    st.rerun()

# ==============================================================================
# 1. IO ENGINE & ACESSO (Login Seguro)
# ==============================================================================
st.set_page_config(page_title="O PREGADOR V31", layout="wide", page_icon="✝️")

class Database:
    @staticmethod
    def load(path, default=[]):
        try:
            if not os.path.exists(path): return default
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except: return default

    @staticmethod
    def save(path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
            return False

class Auth:
    FILE = os.path.join(DIRS["USER"], "users_db.json")
    
    @staticmethod
    def register(u, p):
        db = Database.load(Auth.FILE, {})
        if u.upper() in db: return False
        db[u.upper()] = hashlib.sha256(p.encode()).hexdigest()
        Database.save(Auth.FILE, db)
        return True
    
    @staticmethod
    def login(u, p):
        db = Database.load(Auth.FILE, {})
        h = hashlib.sha256(p.encode()).hexdigest()
        # Admin Backdoor para emergência
        if u.upper() == "ADMIN" and p == "admin" and "ADMIN" not in db: return True
        return db.get(u.upper()) == h

# ==============================================================================
# 2. ESTILO DARK CATHEDRAL (Alinhamento & Gráficos Integrados)
# ==============================================================================
cfg = Database.load(os.path.join(DIRS["CONFIG"], "style_cfg.json"), {"theme_color": "#D4AF37", "font_size": 18})

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Inter:wght@300;400;600&display=swap');
    
    /* VARIÁVEIS DO TEMA */
    :root {{ --gold: {cfg['theme_color']}; --bg: #000000; --panel: #111111; --border: #333; }}
    
    /* GERAL */
    .stApp {{ background-color: var(--bg); color: #EEE; font-family: 'Inter', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Cinzel', serif !important; color: var(--gold) !important; text-transform: uppercase; letter-spacing: 2px; }}
    
    /* INPUTS ALINHADOS */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {{ 
        background-color: var(--panel) !important; 
        border: 1px solid var(--border) !important; 
        color: #FFF !important; 
        border-radius: 4px;
    }}
    .stTextInput input:focus {{ border-color: var(--gold) !important; box-shadow: 0 0 5px rgba(212,175,55,0.5); }}
    
    /* TABELA DE DADOS (DataFrame) */
    div[data-testid="stDataFrame"] {{ border: 1px solid var(--border); }}
    div[data-testid="stDataFrame"] header {{ background-color: var(--panel); border-bottom: 2px solid var(--gold); }}

    /* LOGIN LOGO */
    @keyframes holy-pulse {{ 0% {{ filter: drop-shadow(0 0 2px var(--gold)); }} 50% {{ filter: drop-shadow(0 0 10px var(--gold)); }} 100% {{ filter: drop-shadow(0 0 2px var(--gold)); }} }}
    .cross-logo {{ display:block; margin: 0 auto; animation: holy-pulse 4s infinite; }}
    
    /* BOTÕES */
    .stButton button {{ border: 1px solid var(--gold); color: var(--gold); background: transparent; text-transform: uppercase; font-weight: bold; border-radius: 0; transition: 0.3s; }}
    .stButton button:hover {{ background: var(--gold); color: black; }}

    /* BARRA LATERAL */
    [data-testid="stSidebar"] {{ background-color: #080808; border-right: 1px solid #222; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. GRÁFICOS DINÂMICOS (Plotly Dark Theme)
# ==============================================================================
def draw_chart_radar(title, values, names):
    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=names, fill='toself', 
        line_color=cfg['theme_color'], 
        marker=dict(color='white'), opacity=0.8
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='#444'),
            bgcolor='rgba(0,0,0,0)', gridshape='linear'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#EEE', family='Inter'),
        margin=dict(l=30, r=30, t=30, b=30),
        title=dict(text=title, font=dict(family="Cinzel", size=20))
    )
    return fig

# ==============================================================================
# 4. TELA DE LOGIN (Cruz Animada + Persistência)
# ==============================================================================
if "user" not in st.session_state: st.session_state["user"] = None

if not st.session_state["user"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # A Cruz Dourada Original (SVG)
        st.markdown(f"""
            <svg class="cross-logo" width="100" height="150" viewBox="0 0 100 150">
                <rect x="45" y="10" width="10" height="130" fill="{cfg['theme_color']}" />
                <rect x="20" y="40" width="60" height="10" fill="{cfg['theme_color']}" />
                <circle cx="50" cy="45" r="5" fill="#000" stroke="{cfg['theme_color']}" stroke-width="2"/>
            </svg>
            <h2 style="text-align:center; font-size:24px; margin-top:20px;">SYSTEM OMEGA</h2>
            <p style="text-align:center; color:#666; font-size:12px; letter-spacing:3px;">SHEPHERD EDITION V31</p>
        """, unsafe_allow_html=True)

        tab_log, tab_new = st.tabs(["ENTRAR", "REGISTRAR"])
        
        with tab_log:
            u_in = st.text_input("Identificação (ID)", key="l_u")
            p_in = st.text_input("Senha", type="password", key="l_p")
            if st.button("ACESSAR SISTEMA", use_container_width=True):
                if Auth.login(u_in, p_in):
                    st.session_state["user"] = u_in.upper()
                    st.rerun()
                else: st.error("Acesso Negado.")
        
        with tab_new:
            nu_in = st.text_input("Novo Usuário", key="r_u")
            np_in = st.text_input("Nova Senha", type="password", key="r_p")
            if st.button("CRIAR CREDENCIAL", use_container_width=True):
                if len(np_in) < 4: st.warning("Senha muito curta.")
                elif Auth.register(nu_in, np_in): st.success("Registrado! Faça login.")
                else: st.error("Usuário já existe.")
    st.stop()

# ==============================================================================
# 5. SISTEMA PRINCIPAL (Layout Ajustado)
# ==============================================================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center; color:#555; padding-bottom:10px;'>USER: {st.session_state['user']}</div>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO", ["Cuidado Pastoral", "Gabinete (Sermões)", "Configurações"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("SAIR (LOGOUT)"):
        st.session_state["user"] = None
        st.rerun()

# --- CUIDADO PASTORAL (Revisão Gráfica e Tabela) ---
if menu == "Cuidado Pastoral":
    st.title("🛡️ Cuidado do Rebanho")
    
    t_painel, t_memb = st.tabs(["📊 Visão Gráfica", "🐑 Rol de Membros"])
    
    with t_painel:
        c_rad, c_not = st.columns([1.5, 1])
        with c_rad:
            # Gráfico de Radar Dark/Gold
            st.markdown("<div style='border:1px solid #222; padding:10px; border-radius:5px;'>", unsafe_allow_html=True)
            chart = draw_chart_radar("Saúde da Congregação", 
                                   [random.randint(50,90) for _ in range(5)], 
                                   ["Fé", "Comunhão", "Oração", "Missões", "Doutrina"])
            st.plotly_chart(chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c_not:
            st.info("ℹ️ **Notificações:** \n- 3 Aniversariantes essa semana.\n- Irmão Carlos pediu visita.")
            st.warning("⚠️ **Alerta:** \n- Finanças do departamento de Missões em baixa.")
            
    with t_memb:
        st.subheader("Lista de Membros (Alinhada)")
        path_memb = os.path.join(DIRS["MEMBROS"], "members.json")
        membros = Database.load(path_memb)
        
        # MODO ADIÇÃO EM UMA LINHA (Para economizar espaço)
        with st.expander("➕ Adicionar Novo Membro", expanded=False):
            with st.form("form_membro"):
                cols = st.columns([3, 2, 3, 1])
                n_nm = cols[0].text_input("Nome")
                n_st = cols[1].selectbox("Status", ["Comungante", "Não Comungante", "Disciplinado", "Visitante"])
                n_ob = cols[2].text_input("Observação / Necessidade")
                submitted = cols[3].form_submit_button("Salvar")
                if submitted and n_nm:
                    membros.append({"Nome": n_nm, "Status": n_st, "Obs": n_ob, "Data": datetime.now().strftime("%d/%m/%Y")})
                    Database.save(path_memb, membros)
                    st.success("Salvo.")
                    st.rerun()

        # TABELA PROFISSIONAL ALINHADA (DATAFRAME)
        if membros:
            df = pd.DataFrame(membros)
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Nome": st.column_config.TextColumn("Nome da Ovelha", width="medium"),
                    "Status": st.column_config.SelectboxColumn("Situação Eclesiástica", options=["Comungante", "Disciplinado"], width="small"),
                    "Obs": "Necessidades Pastorais",
                    "Data": "Desde"
                },
                hide_index=True
            )
        else:
            st.markdown("*Nenhum membro cadastrado. Use o botão acima.*")

# --- GABINETE (Sermões) ---
elif menu == "Gabinete (Sermões)":
    st.title("📝 Gabinete da Palavra")
    
    # Gerenciador de Arquivos na Lateral
    col_file, col_edit = st.columns([1, 4])
    
    with col_file:
        st.markdown("**Seus Sermões**")
        all_files = [f for f in os.listdir(DIRS["SERMOES"]) if f.endswith('.txt')]
        sel_sermon = st.selectbox("Abrir:", ["- Novo -"] + all_files, label_visibility="collapsed")
    
    # Lógica de Carregamento
    content_area = ""
    title_area = ""
    
    if sel_sermon != "- Novo -":
        path = os.path.join(DIRS["SERMOES"], sel_sermon)
        content_area = open(path, 'r', encoding='utf-8').read() if os.path.exists(path) else ""
        title_area = sel_sermon.replace(".txt", "")
        
    with col_edit:
        # Título e Ações
        c_t1, c_t2 = st.columns([3, 1])
        final_title = c_t1.text_input("Título do Sermão", value=title_area)
        
        # Editor (Quill se disponível, senão Area simples)
        st.markdown("<div style='background:#111; border:1px solid #333; border-radius:4px;'>", unsafe_allow_html=True)
        texto = st_quill(value=content_area, html=True, placeholder="Escreva a revelação aqui...")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if c_t2.button("💾 SALVAR", use_container_width=True):
            if final_title:
                fpath = os.path.join(DIRS["SERMOES"], f"{final_title}.txt")
                with open(fpath, 'w', encoding='utf-8') as f: f.write(texto)
                st.success("Salvo no disco.")
            else: st.warning("Precisa de título.")

# --- CONFIGURAÇÕES (Simplificadas e Estáveis) ---
elif menu == "Configurações":
    st.title("⚙️ Personalização")
    
    path_cfg = os.path.join(DIRS["CONFIG"], "style_cfg.json")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Visual Litúrgico")
        nc = st.color_picker("Cor Destaque (Padrão: Ouro)", value=cfg['theme_color'])
        st.caption("A cor usada na Cruz, botões e títulos.")
        
    with col_b:
        st.markdown("### Sistema")
        fs = st.slider("Tamanho da Fonte de Leitura", 14, 24, cfg['font_size'])
        if st.button("Aplicar e Reiniciar Interface"):
            Database.save(path_cfg, {"theme_color": nc, "font_size": fs})
            st.rerun()
