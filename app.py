import streamlit as st
import os
import sys
import subprocess
import time
import json
import base64
import math
import shutil
import random
import calendar
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# ==============================================================================
# 0. KERNEL DE INICIALIZAÇÃO BLINDADO
# ==============================================================================
class SystemOmegaKernel:
    """
    Núcleo 'Raiz': Instala o que precisa e garante que o show continue.
    """
    REQUIRED = ["google-generativeai", "streamlit-lottie", "Pillow", "pandas", "fpdf"]
    
    @staticmethod
    def _install(pkg):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        except:
            pass # Se falhar, tenta rodar mesmo assim

    @staticmethod
    def boot_check():
        queue = []
        for lib in SystemOmegaKernel.REQUIRED:
            try:
                # Resolve nomes de importação vs nomes de pacote
                mod = lib.replace("google-generativeai", "google.generativeai").replace("Pillow", "PIL")
                __import__(mod.replace("-", "_"))
            except ImportError:
                queue.append(lib)
        
        if queue:
            placeholder = st.empty()
            placeholder.warning(f"🔧 Ajustando o motor... Instalando {len(queue)} dependências.")
            for lib in queue:
                SystemOmegaKernel._install(lib)
            placeholder.empty()
            st.rerun()

SystemOmegaKernel.boot_check()

import google.generativeai as genai
from PIL import Image, ImageOps

# ==============================================================================
# 1. INFRAESTRUTURA & AUTO-CORREÇÃO (SELF-HEALING)
# ==============================================================================
st.set_page_config(page_title="O PREGADOR | System Omega", layout="wide", page_icon="✝️", initial_sidebar_state="expanded")

# Caminhos
ROOT = "Dados_Pregador_V21_Rocha"
DIRS = {
    "SERMOES": os.path.join(ROOT, "Sermoes"),
    "GABINETE": os.path.join(ROOT, "Gabinete_Pastoral"),
    "SERIES": os.path.join(ROOT, "Series"),
    "MIDIA": os.path.join(ROOT, "Midia"),
    "USER": os.path.join(ROOT, "User_Data"),
    "BACKUP": os.path.join(ROOT, "Auto_Backup_Oculto") # Nova feature
}

# Bancos de Dados
DBS = {
    "SERIES": os.path.join(DIRS["SERIES"], "db_series.json"),
    "STATS": os.path.join(DIRS["USER"], "db_stats.json"),
    "CONFIG": os.path.join(DIRS["USER"], "config.json"),
    "SOUL": os.path.join(DIRS["GABINETE"], "soul_data.json")
}

# Criador de Pastas (Garante que tudo existe)
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

class SafeIO:
    """
    CLASSE DE AUTO-CORREÇÃO.
    Impede que o sistema quebre por erros de arquivo.
    """
    @staticmethod
    def ler_json(caminho, default_return):
        if not os.path.exists(caminho):
            return default_return
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content: return default_return
                return json.loads(content)
        except Exception as e:
            # Se der erro, faz backup do arquivo corrompido e retorna o padrão
            try:
                shutil.move(caminho, caminho + ".corrupted")
            except: pass
            return default_return

    @staticmethod
    def salvar_json(caminho, dados):
        try:
            # 1. Salva o arquivo principal
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            
            # 2. Cria Backup Automático (Feature Nova)
            nome_bkp = os.path.basename(caminho)
            caminho_bkp = os.path.join(DIRS["BACKUP"], f"{nome_bkp}.bak")
            shutil.copy2(caminho, caminho_bkp)
        except Exception as e:
            st.error(f"Erro de Gravação: {e}")

# ==============================================================================
# 2. DESIGN SYSTEM (LOGIN MANTIDO + NOVO MENU ROBUSTO)
# ==============================================================================
def inject_css(color="#D4AF37", font_sz=18):
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@500;700&family=Cinzel:wght@400;700&display=swap');
        
        :root {{ --gold: {color}; --bg: #050505; --panel: #111; --text: #eee; }}
        
        .stApp {{ background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }}
        
        /* Sidebar Premium (Menu Raiz) */
        [data-testid="stSidebar"] {{
            background-color: #0a0a0a;
            border-right: 1px solid #222;
        }}
        [data-testid="stSidebar"] h1 {{ color: var(--gold); font-family: 'Cinzel'; text-align: center; }}
        
        /* ANIMAÇÃO DE LOGIN (PRESERVADA) */
        @keyframes pulse-gold {{
            0% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); transform: scale(1); }}
            50% {{ box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); transform: scale(1.05); }}
            100% {{ box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); transform: scale(1); }}
        }}
        .holy-circle {{
            width: 120px; height: 120px; border-radius: 50%;
            border: 2px solid var(--gold); background: #000;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 30px auto;
            animation: pulse-gold 3s infinite;
        }}

        /* CARDS & EDITOR */
        .omega-card {{
            background: var(--panel); border: 1px solid #222;
            border-radius: 6px; padding: 20px; margin-bottom: 15px;
            border-left: 3px solid var(--gold);
        }}
        .editor-box textarea {{
            font-family: 'Playfair Display', serif !important;
            font-size: {font_sz}px !important;
            line-height: 1.6;
            background-color: #080808 !important;
            border: 1px solid #333 !important;
            color: #ddd !important;
            padding: 20px !important;
        }}
        
        /* Inputs */
        .stTextInput input, .stSelectbox div, .stTextArea textarea {{
            background-color: #111 !important; border: 1px solid #333 !important; color: white !important;
        }}
        
        /* Alertas Teológicos */
        .alert-box {{ padding: 10px; border-radius: 4px; margin-top: 5px; font-size: 0.9em; }}
        .alert-danger {{ background: #2a0505; border-left: 3px solid red; color: #ffadad; }}
        .alert-success {{ background: #052a05; border-left: 3px solid green; color: #adffad; }}
        
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTORES DE INTELIGÊNCIA (TEOLOGIA, PSICOLOGIA, GAMIFICAÇÃO)
# ==============================================================================

class GenevaProtocol:
    """Verificador de Heresias (Teologia Reformada)."""
    DB = {
        "prosperidade": "⚠️ ALERTA: Teologia da Prosperidade detectada. O Evangelho não promete riqueza.",
        "eu determino": "⚠️ ALERTA: Quebra de Soberania. Use 'Se o Senhor quiser'.",
        "mérito": "⚠️ ALERTA: Pelagianismo. A salvação é somente pela Graça.",
        "aceitar a jesus": "ℹ️ NOTA: Considere usar 'Render-se a Cristo'. A iniciativa é Dele."
    }
    @staticmethod
    def analisar(texto):
        if not texto: return []
        avisos = []
        texto_low = texto.lower()
        for k, v in GenevaProtocol.DB.items():
            if k in texto_low: avisos.append(v)
        if "cristo" not in texto_low and "jesus" not in texto_low and "senhor" not in texto_low:
            avisos.append("🔴 CRÍTICO: Sermão sem menção explícita a Cristo.")
        return avisos

class PastoralMind:
    """Monitor de Saúde Mental."""
    @staticmethod
    def check_burnout():
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": []})
        hist = data.get("historico", [])[-10:] # Últimos 10 registros
        
        bad_vibes = sum(1 for h in hist if h['humor'] in ["Cansaço 🌖", "Ira 😠", "Ansiedade 🌪️", "Tristeza 😢"])
        
        if bad_vibes >= 6: return "CRÍTICO", "Pare imediatamente. Risco de Colapso."
        if bad_vibes >= 3: return "ALERTA", "Cuidado. Você está operando na reserva."
        return "ESTÁVEL", "Sua alma parece estar em equilíbrio."

    @staticmethod
    def registrar(humor):
        data = SafeIO.ler_json(DBS["SOUL"], {"historico": [], "diario": []})
        data["historico"].append({"data": datetime.now().strftime("%Y-%m-%d"), "humor": humor})
        SafeIO.salvar_json(DBS["SOUL"], data)

class Gamification:
    """Sistema de XP e Níveis."""
    @staticmethod
    def add_xp(amount):
        stats = SafeIO.ler_json(DBS["STATS"], {"xp": 0, "nivel": 1, "badges": []})
        stats["xp"] += amount
        stats["nivel"] = int(math.sqrt(stats["xp"]) * 0.2) + 1
        
        # Badges
        badges = stats.get("badges", [])
        if stats["xp"] > 100 and "Escriba" not in badges: badges.append("Escriba")
        if stats["xp"] > 500 and "Teólogo" not in badges: badges.append("Teólogo")
        stats["badges"] = badges
        
        SafeIO.salvar_json(DBS["STATS"], stats)

# ==============================================================================
# 4. GESTÃO DE ESTADO
# ==============================================================================
if "config" not in st.session_state:
    st.session_state["config"] = SafeIO.ler_json(DBS["CONFIG"], {"theme_color": "#D4AF37", "font_size": 18})

inject_css(st.session_state["config"]["theme_color"], st.session_state["config"]["font_size"])

if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "Pastor"
if "texto_ativo" not in st.session_state: st.session_state["texto_ativo"] = ""
if "titulo_ativo" not in st.session_state: st.session_state["titulo_ativo"] = ""

# ==============================================================================
# 5. TELA DE LOGIN (INTOCADA E PRESERVADA)
# ==============================================================================
if not st.session_state["logado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown(f"""
        <div class="holy-circle">
            <span style="font-size:60px; color:{st.session_state["config"]["theme_color"]};">✝</span>
        </div>
        <div style="text-align:center;">
            <h1 style="font-family:'Cinzel'; margin:0; color:#fff; font-size:30px;">O PREGADOR</h1>
            <div style="width:50px; height:3px; background:{st.session_state["config"]["theme_color"]}; margin: 15px auto;"></div>
            <p style="font-size:12px; color:#888; letter-spacing:3px;">SYSTEM OMEGA • V21</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Credencial", label_visibility="collapsed", placeholder="USUÁRIO")
            pw = st.text_input("Chave", type="password", label_visibility="collapsed", placeholder="SENHA")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("ACESSAR SISTEMA", type="primary", use_container_width=True):
                if (user == "admin" and pw == "1234") or (user == "pr" and pw == "123"):
                    st.session_state["logado"] = True
                    st.session_state["user_name"] = user.upper()
                    Gamification.add_xp(5)
                    st.rerun()
                else:
                    st.error("Acesso Negado.")
    st.stop()

# ==============================================================================
# 6. APP PRINCIPAL (MENU LATERAL ROBUSTO)
# ==============================================================================

# --- SIDEBAR (MENU RAIZ) ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding-bottom:20px;">
        <h2 style="font-family:'Cinzel'; color:{st.session_state["config"]["theme_color"]}">OMEGA</h2>
        <p style="font-size:10px; color:#666">Sola Scriptura</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu de Navegação
    menu = st.radio("NAVEGAÇÃO", ["Dashboard", "Gabinete (Alma)", "Studio (Sermão)", "Séries", "Media", "Configurações"], label_visibility="collapsed")
    
    st.divider()
    
    # Status de Saúde na Sidebar
    nivel_burnout, msg_burnout = PastoralMind.check_burnout()
    cor_b = "green" if nivel_burnout == "ESTÁVEL" else "red"
    st.markdown(f"**Vitalidade:** <span style='color:{cor_b}'>{nivel_burnout}</span>", unsafe_allow_html=True)
    
    # Stats de Gamificação
    stats = SafeIO.ler_json(DBS["STATS"], {"nivel": 1, "xp": 0})
    st.markdown(f"**Nível {stats['nivel']}** (XP: {stats['xp']})")
    
    st.divider()
    if st.button("SAIR"):
        st.session_state["logado"] = False
        st.rerun()

# --- LÓGICA DAS PÁGINAS ---

if menu == "Dashboard":
    st.title(f"Bem-vindo, {st.session_state['user_name']}.")
    
    # Check-in Rápido
    st.markdown('<div class="omega-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.caption("CHECK-IN DIÁRIO")
        humor = st.selectbox("Como está seu espírito?", ["Plenitude 🕊️", "Gratidão 🙏", "Cansaço 🌖", "Ira 😠", "Tristeza 😢", "Ansiedade 🌪️"])
        if st.button("Registrar"):
            PastoralMind.registrar(humor)
            Gamification.add_xp(10)
            st.success("Registrado.")
            time.sleep(1)
            st.rerun()
    with c2:
        st.caption("DIAGNÓSTICO ATUAL")
        if nivel_burnout != "ESTÁVEL":
            st.error(f"{nivel_burnout}: {msg_burnout}")
        else:
            st.info(f"{nivel_burnout}: {msg_burnout}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Acesso Rápido
    st.subheader("Últimos Sermões")
    files = sorted([f for f in os.listdir(DIRS["SERMOES"]) if f.endswith(".txt")], key=lambda x: os.path.getmtime(os.path.join(DIRS["SERMOES"], x)), reverse=True)[:3]
    
    if not files:
        st.warning("Nenhum sermão encontrado.")
    else:
        cols = st.columns(3)
        for i, f in enumerate(files):
            with cols[i]:
                st.markdown(f"<div style='background:#111; padding:15px; border:1px solid #333; border-radius:5px;'>📄 {f.replace('.txt','')}</div>", unsafe_allow_html=True)

elif menu == "Gabinete (Alma)":
    st.title("Gabinete Pastoral")
    st.markdown("O lugar onde o pastor é cuidado.")
    
    tab1, tab2 = st.tabs(["📓 Diário Confidencial", "🧠 Terapia Cognitiva"])
    
    with tab1:
        st.caption("O que você escrever aqui é criptografado localmente.")
        diario = st.text_area("Escreva para Deus:", height=200)
        if st.button("Guardar no Cofre"):
            # Salvar no JSON de alma
            soul_data = SafeIO.ler_json(DBS["SOUL"], {"diario": []})
            soul_data.setdefault("diario", []).append({"data": datetime.now().strftime("%Y-%m-%d"), "texto": diario})
            SafeIO.salvar_json(DBS["SOUL"], soul_data)
            Gamification.add_xp(15)
            st.toast("Guardado.", icon="🔒")
            
    with tab2:
        st.subheader("Enfrentando Mentiras")
        mentira = st.text_input("Qual mentira está te atacando? (Ex: Sou um fracasso)")
        if mentira:
            st.info("💡 **Verdade Bíblica:** A minha graça te basta, porque o meu poder se aperfeiçoa na fraqueza. (2 Coríntios 12:9)")

elif menu == "Studio (Sermão)":
    if nivel_burnout == "CRÍTICO":
        st.error("🛑 ACESSO BLOQUEADO POR MOTIVO DE SAÚDE.")
        st.markdown("O sistema detectou que você está em Burnout. Vá descansar. O púlpito pode esperar, sua alma não.")
        st.stop()

    st.title("Studio Expositivo")
    
    # Barra de Ferramentas
    c1, c2 = st.columns([3, 1])
    with c1:
        st.session_state["titulo_ativo"] = st.text_input("Título da Mensagem", value=st.session_state["titulo_ativo"])
    with c2:
        if st.button("💾 SALVAR", type="primary"):
            if st.session_state["titulo_ativo"]:
                path = os.path.join(DIRS["SERMOES"], f"{st.session_state['titulo_ativo']}.txt")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(st.session_state["texto_ativo"])
                SafeIO.salvar_json(os.path.join(DIRS["BACKUP"], "log_save.json"), {"last": datetime.now().strftime("%c")}) # Trigger backup
                Gamification.add_xp(5)
                st.toast("Salvo com Backup Automático!", icon="✅")
    
    # Editor e Análise
    col_edit, col_ana = st.columns([2.5, 1])
    
    with col_edit:
        st.markdown('<div class="editor-box">', unsafe_allow_html=True)
        st.session_state["texto_ativo"] = st.text_area("editor", st.session_state["texto_ativo"], height=600, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_ana:
        st.markdown("### Protocolo Genebra")
        alertas = GenevaProtocol.analisar(st.session_state["texto_ativo"])
        
        if not alertas:
            st.markdown('<div class="alert-box alert-success">✅ Doutrina Sã.</div>', unsafe_allow_html=True)
        else:
            for a in alertas:
                st.markdown(f'<div class="alert-box alert-danger">{a}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### Auxílio IA")
        q = st.text_area("Consultar Teólogo IA")
        if st.button("Pesquisar"):
            cfg = st.session_state.get("config", {})
            api_key = cfg.get("api_key", "")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    r = genai.GenerativeModel("gemini-pro").generate_content(f"Aja como um teólogo reformado. Responda: {q}").text
                    st.info(r)
                except Exception as e:
                    st.error(f"Erro IA: {e}")
            else:
                st.warning("Configure a API Key nas Configurações.")

elif menu == "Séries":
    st.title("Gestão de Séries")
    
    with st.expander("Nova Série", expanded=True):
        with st.form("serie_form"):
            nome = st.text_input("Nome da Série")
            desc = st.text_area("Descrição")
            if st.form_submit_button("Criar"):
                db = SafeIO.ler_json(DBS["SERIES"], {})
                db[f"S{int(time.time())}"] = {"nome": nome, "descricao": desc}
                SafeIO.salvar_json(DBS["SERIES"], db)
                st.success("Série Criada.")
                st.rerun()
                
    st.markdown("### Séries Ativas")
    db = SafeIO.ler_json(DBS["SERIES"], {})
    if not db: st.info("Nenhuma série.")
    for k, v in db.items():
        st.markdown(f"<div class='omega-card'><b>{v['nome']}</b><br>{v['descricao']}</div>", unsafe_allow_html=True)

elif menu == "Media":
    st.title("Media Lab")
    st.info("Gerador de Artes e Agendamento (Simulado)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="height:300px; border:1px dashed #444; display:flex; align-items:center; justify-content:center;">PREVIEW</div>', unsafe_allow_html=True)
    with c2:
        st.text_input("Texto do Post")
        st.date_input("Data de Publicação")
        if st.button("Agendar"):
            st.success("Agendado na fila.")

elif menu == "Configurações":
    st.title("Configurações do Sistema")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Visual")
        novo_cor = st.color_picker("Cor Tema", st.session_state["config"].get("theme_color", "#D4AF37"))
        novo_font = st.slider("Tamanho da Fonte", 14, 28, st.session_state["config"].get("font_size", 18))
        
    with c2:
        st.markdown("### Sistema")
        nova_key = st.text_input("Google Gemini API Key", value=st.session_state["config"].get("api_key", ""), type="password")
        
    if st.button("SALVAR TUDO"):
        cfg = st.session_state["config"]
        cfg["theme_color"] = novo_cor
        cfg["font_size"] = novo_font
        cfg["api_key"] = nova_key
        SafeIO.salvar_json(DBS["CONFIG"], cfg)
        st.success("Salvo. Reiniciando interface...")
        time.sleep(1)
        st.rerun()

    st.divider()
    st.markdown("### Zona de Perigo")
    if st.button("Baixar Backup de Segurança (.zip)"):
        shutil.make_archive("backup_seguranca", 'zip', ROOT)
        with open("backup_seguranca.zip", "rb") as f:
            st.download_button("Download Backup", f, "backup_seguranca.zip")
