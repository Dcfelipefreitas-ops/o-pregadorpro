# -*- coding: utf-8 -*-
"""
===============================================================================
 O PREGADOR | CANAL DE ACONSELHAMENTO PASTORAL
 Visitas · Abrir o Coração · Diário de Meditação · Devocionais
===============================================================================

Como usar:
- Rode este arquivo direto: streamlit run app_pregador_aconselhamento.py
- Ou copie os blocos que quiser para dentro do seu app principal
  (ex.: dentro do modo "Rede Ministerial" que já existia).

Não há senha (conforme pedido). A separação entre "Membro" e "Pastor" é
apenas uma escolha na barra lateral, não uma proteção de segurança. Se um
dia quiser um mínimo de proteção para o painel do Pastor sem virar um
sistema de login completo, dá pra usar só uma palavra-chave simples — me
avise se quiser isso.
"""

import streamlit as st
import os
import json
import uuid
from datetime import datetime, timezone

# ==============================================================================
# 01. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(
    page_title="O PREGADOR | Aconselhamento Pastoral",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)

SYSTEM_ROOT = "Dados_Pregador_V31"
PASTORAL_PATH = os.path.join(SYSTEM_ROOT, "pastoral")
os.makedirs(PASTORAL_PATH, exist_ok=True)

VISITS_FILE = os.path.join(PASTORAL_PATH, "visitas.json")
HEART_FILE = os.path.join(PASTORAL_PATH, "abrir_coracao.json")
DIARY_FILE = os.path.join(PASTORAL_PATH, "diario.json")
DEVOTIONALS_FILE = os.path.join(PASTORAL_PATH, "devocionais.json")
COMPLETIONS_FILE = os.path.join(PASTORAL_PATH, "devocionais_concluidas.json")


# ==============================================================================
# 02. FUNÇÕES DE ARMAZENAMENTO (JSON simples, sem dependências externas)
# ==============================================================================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_br():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def new_id():
    return uuid.uuid4().hex[:8]


# ==============================================================================
# 03. SESSÃO — QUEM É VOCÊ (sem senha)
# ==============================================================================
if "papel" not in st.session_state:
    st.session_state["papel"] = None
if "nome_membro" not in st.session_state:
    st.session_state["nome_membro"] = ""

with st.sidebar:
    st.markdown("## 💗 Aconselhamento Pastoral")
    papel = st.radio("Quem é você?", ["Membro da Igreja", "Pastor"])
    st.session_state["papel"] = papel

    if papel == "Membro da Igreja":
        st.session_state["nome_membro"] = st.text_input(
            "Seu nome", value=st.session_state["nome_membro"]
        )
        st.caption(
            "Seu nome só é usado para o pastor saber quem escreveu. "
            "Nas mensagens sensíveis você pode optar por não se identificar."
        )

st.title("💗 Canal de Aconselhamento Pastoral")

# ==============================================================================
# 04. ÁREA DO MEMBRO
# ==============================================================================
if st.session_state["papel"] == "Membro da Igreja":

    tab_visita, tab_coracao, tab_diario, tab_devocional = st.tabs(
        ["🙋 Pedir Visita", "💗 Abrir o Coração", "📔 Diário de Meditação", "📖 Devocionais"]
    )

    # --- Pedir visita ---------------------------------------------------
    with tab_visita:
        st.subheader("Pedir uma visita pastoral")
        st.write("Conte um pouco do que está acontecendo. O pastor vai ver seu pedido e entrar em contato.")

        with st.form("form_visita", clear_on_submit=True):
            nome = st.text_input("Seu nome", value=st.session_state["nome_membro"])
            contato = st.text_input("Telefone ou forma de contato")
            urgencia = st.select_slider(
                "Quão urgente é isso pra você?",
                options=["Sem pressa", "Gostaria em breve", "É urgente"],
            )
            motivo = st.text_area("O que você gostaria de conversar? (fique à vontade)", height=150)
            enviar = st.form_submit_button("Enviar pedido de visita")

        if enviar:
            if not nome.strip() or not motivo.strip():
                st.error("Por favor, preencha ao menos seu nome e o motivo.")
            else:
                visitas = load_json(VISITS_FILE, [])
                visitas.append({
                    "id": new_id(),
                    "nome": nome.strip(),
                    "contato": contato.strip(),
                    "urgencia": urgencia,
                    "motivo": motivo.strip(),
                    "data_criacao": now_iso(),
                    "data_criacao_br": now_br(),
                    "status": "Pendente",
                    "obs_pastor": "",
                })
                save_json(VISITS_FILE, visitas)
                st.success("Seu pedido foi enviado. O pastor vai te procurar em breve. 🙏")

    # --- Abrir o coração --------------------------------------------------
    with tab_coracao:
        st.subheader("Abrir o coração")
        st.write("Um espaço para escrever o que está pesando, sem precisar estruturar nada. Só o pastor vai ler.")

        anonimo = st.checkbox("Prefiro não me identificar (enviar anonimamente)")

        with st.form("form_coracao", clear_on_submit=True):
            nome_msg = "Anônimo" if anonimo else st.text_input(
                "Seu nome", value=st.session_state["nome_membro"], key="nome_coracao"
            )
            mensagem = st.text_area("O que você quer dizer?", height=200)
            enviar_msg = st.form_submit_button("Enviar")

        if enviar_msg:
            if not mensagem.strip():
                st.error("Escreva algo antes de enviar.")
            else:
                mensagens = load_json(HEART_FILE, [])
                mensagens.append({
                    "id": new_id(),
                    "nome": "Anônimo" if anonimo else (nome_msg.strip() or "Anônimo"),
                    "mensagem": mensagem.strip(),
                    "data_criacao": now_iso(),
                    "data_criacao_br": now_br(),
                    "status": "Novo",
                    "resposta_pastor": "",
                })
                save_json(HEART_FILE, mensagens)
                st.success("Sua mensagem foi enviada com cuidado. Obrigado por confiar. 💗")

    # --- Diário de meditação ----------------------------------------------
    with tab_diario:
        st.subheader("Diário de meditação")
        st.write("Registre o que Deus tem falado com você. Você escolhe se quer compartilhar cada entrada com o pastor ou mantê-la só sua.")

        nome_diario = st.session_state["nome_membro"] or st.text_input("Seu nome para o diário", key="nome_diario_input")

        with st.form("form_diario", clear_on_submit=True):
            sentimento = st.selectbox(
                "Como você está hoje?",
                ["🙏 Em paz", "😊 Grato(a)", "😔 Triste", "😟 Ansioso(a)", "😤 Frustrado(a)", "🤔 Refletindo"],
            )
            texto_diario = st.text_area("O que Deus tem colocado no seu coração hoje?", height=200)
            compartilhar = st.checkbox("Compartilhar esta entrada com o pastor")
            salvar_diario = st.form_submit_button("Salvar no diário")

        if salvar_diario:
            if not nome_diario.strip() or not texto_diario.strip():
                st.error("Preencha seu nome e o texto da meditação.")
            else:
                diario = load_json(DIARY_FILE, [])
                diario.append({
                    "id": new_id(),
                    "nome": nome_diario.strip(),
                    "sentimento": sentimento,
                    "texto": texto_diario.strip(),
                    "data_criacao": now_iso(),
                    "data_criacao_br": now_br(),
                    "compartilhado": compartilhar,
                })
                save_json(DIARY_FILE, diario)
                st.success("Entrada salva no seu diário. 📔")

        st.divider()
        st.markdown("#### Suas últimas entradas")
        diario_todos = load_json(DIARY_FILE, [])
        minhas = [d for d in diario_todos if d["nome"].strip().lower() == nome_diario.strip().lower()]
        minhas = sorted(minhas, key=lambda x: x["data_criacao"], reverse=True)[:5]
        if not minhas:
            st.caption("Nenhuma entrada ainda.")
        for entrada in minhas:
            with st.expander(f"{entrada['data_criacao_br']} — {entrada['sentimento']}"):
                st.write(entrada["texto"])
                st.caption("Compartilhado com o pastor" if entrada["compartilhado"] else "Privado")

    # --- Devocionais --------------------------------------------------
    with tab_devocional:
        st.subheader("Devocionais")
        devocionais = load_json(DEVOTIONALS_FILE, [])
        devocionais = sorted(devocionais, key=lambda x: x["data_criacao"], reverse=True)

        if not devocionais:
            st.info("Ainda não há devocionais publicados.")
        else:
            nome_devocional = st.session_state["nome_membro"] or st.text_input("Seu nome", key="nome_devocional_input")
            concluidas = load_json(COMPLETIONS_FILE, [])
            ids_concluidos = {
                c["devocional_id"] for c in concluidas
                if c["nome"].strip().lower() == (nome_devocional or "").strip().lower()
            }

            for dev in devocionais:
                feito = dev["id"] in ids_concluidos
                titulo = f"{'✅' if feito else '⬜'} {dev['titulo']}"
                with st.expander(titulo):
                    st.markdown(f"**Texto bíblico:** {dev['texto_biblico']}")
                    st.write(dev["reflexao"])

                    if feito:
                        st.success("Você já concluiu este devocional.")
                    else:
                        with st.form(f"form_dev_{dev['id']}"):
                            reflexao_pessoal = st.text_area(
                                "O que esse devocional falou com você?", height=120,
                                key=f"reflexao_{dev['id']}"
                            )
                            marcar = st.form_submit_button("Marcar como concluído")
                        if marcar:
                            if not nome_devocional.strip():
                                st.error("Preencha seu nome antes de marcar como concluído.")
                            else:
                                concluidas.append({
                                    "id": new_id(),
                                    "devocional_id": dev["id"],
                                    "nome": nome_devocional.strip(),
                                    "reflexao_pessoal": reflexao_pessoal.strip(),
                                    "data_criacao": now_iso(),
                                    "data_criacao_br": now_br(),
                                })
                                save_json(COMPLETIONS_FILE, concluidas)
                                st.rerun()

# ==============================================================================
# 05. ÁREA DO PASTOR
# ==============================================================================
elif st.session_state["papel"] == "Pastor":

    tab_p_visitas, tab_p_coracao, tab_p_diario, tab_p_devocionais, tab_p_publicar = st.tabs(
        ["📋 Visitas", "💌 Abrir o Coração", "📔 Diários Compartilhados", "📖 Acompanhamento", "✍️ Publicar Devocional"]
    )

    # --- Painel de visitas ------------------------------------------------
    with tab_p_visitas:
        st.subheader("Pedidos de visita")
        visitas = load_json(VISITS_FILE, [])
        visitas = sorted(visitas, key=lambda x: x["data_criacao"], reverse=True)

        if not visitas:
            st.caption("Nenhum pedido de visita ainda.")
        else:
            filtro = st.multiselect(
                "Filtrar por status", ["Pendente", "Agendada", "Concluída"],
                default=["Pendente", "Agendada"],
            )
            for v in visitas:
                if v["status"] not in filtro:
                    continue
                with st.expander(f"{v['nome']} — {v['urgencia']} — {v['data_criacao_br']} [{v['status']}]"):
                    st.write(v["motivo"])
                    st.caption(f"Contato: {v['contato'] or 'não informado'}")

                    col1, col2 = st.columns(2)
                    with col1:
                        novo_status = st.selectbox(
                            "Status", ["Pendente", "Agendada", "Concluída"],
                            index=["Pendente", "Agendada", "Concluída"].index(v["status"]),
                            key=f"status_visita_{v['id']}",
                        )
                    with col2:
                        obs = st.text_input("Observação", value=v.get("obs_pastor", ""), key=f"obs_visita_{v['id']}")

                    if st.button("Salvar", key=f"salvar_visita_{v['id']}"):
                        for item in visitas:
                            if item["id"] == v["id"]:
                                item["status"] = novo_status
                                item["obs_pastor"] = obs
                        save_json(VISITS_FILE, visitas)
                        st.rerun()

    # --- Painel de mensagens (abrir o coração) -----------------------------
    with tab_p_coracao:
        st.subheader("Mensagens — Abrir o Coração")
        mensagens = load_json(HEART_FILE, [])
        mensagens = sorted(mensagens, key=lambda x: x["data_criacao"], reverse=True)

        if not mensagens:
            st.caption("Nenhuma mensagem ainda.")
        else:
            for m in mensagens:
                with st.expander(f"{m['nome']} — {m['data_criacao_br']} [{m['status']}]"):
                    st.write(m["mensagem"])
                    resposta = st.text_area(
                        "Resposta / anotação pastoral (privada)", value=m.get("resposta_pastor", ""),
                        key=f"resp_{m['id']}",
                    )
                    novo_status_m = st.selectbox(
                        "Status", ["Novo", "Lido", "Respondido"],
                        index=["Novo", "Lido", "Respondido"].index(m["status"]),
                        key=f"status_msg_{m['id']}",
                    )
                    if st.button("Salvar", key=f"salvar_msg_{m['id']}"):
                        for item in mensagens:
                            if item["id"] == m["id"]:
                                item["resposta_pastor"] = resposta
                                item["status"] = novo_status_m
                        save_json(HEART_FILE, mensagens)
                        st.rerun()

    # --- Diários compartilhados ---------------------------------------------
    with tab_p_diario:
        st.subheader("Diários compartilhados com você")
        diario = load_json(DIARY_FILE, [])
        compartilhados = [d for d in diario if d.get("compartilhado")]
        compartilhados = sorted(compartilhados, key=lambda x: x["data_criacao"], reverse=True)

        if not compartilhados:
            st.caption("Ninguém compartilhou entradas do diário ainda.")
        else:
            nomes = sorted(set(d["nome"] for d in compartilhados))
            filtro_nome = st.selectbox("Filtrar por pessoa", ["Todos"] + nomes)
            for d in compartilhados:
                if filtro_nome != "Todos" and d["nome"] != filtro_nome:
                    continue
                with st.expander(f"{d['nome']} — {d['sentimento']} — {d['data_criacao_br']}"):
                    st.write(d["texto"])

    # --- Acompanhamento de devocionais ---------------------------------------
    with tab_p_devocionais:
        st.subheader("Quem está fazendo os devocionais")
        devocionais = load_json(DEVOTIONALS_FILE, [])
        concluidas = load_json(COMPLETIONS_FILE, [])

        if not devocionais:
            st.caption("Publique um devocional na aba ao lado para começar a acompanhar.")
        else:
            for dev in sorted(devocionais, key=lambda x: x["data_criacao"], reverse=True):
                feitos = [c for c in concluidas if c["devocional_id"] == dev["id"]]
                with st.expander(f"{dev['titulo']} — {len(feitos)} concluíram"):
                    if not feitos:
                        st.caption("Ninguém concluiu ainda.")
                    for f in feitos:
                        st.markdown(f"**{f['nome']}** ({f['data_criacao_br']})")
                        if f["reflexao_pessoal"]:
                            st.write(f["reflexao_pessoal"])
                        st.divider()

    # --- Publicar devocional ---------------------------------------------
    with tab_p_publicar:
        st.subheader("Publicar novo devocional")
        with st.form("form_publicar_devocional", clear_on_submit=True):
            titulo = st.text_input("Título")
            texto_biblico = st.text_input("Texto bíblico de referência (ex.: Salmo 23:1-3)")
            reflexao = st.text_area("Reflexão / conteúdo do devocional", height=200)
            publicar = st.form_submit_button("Publicar")

        if publicar:
            if not titulo.strip() or not reflexao.strip():
                st.error("Preencha ao menos o título e a reflexão.")
            else:
                devocionais = load_json(DEVOTIONALS_FILE, [])
                devocionais.append({
                    "id": new_id(),
                    "titulo": titulo.strip(),
                    "texto_biblico": texto_biblico.strip(),
                    "reflexao": reflexao.strip(),
                    "data_criacao": now_iso(),
                    "data_criacao_br": now_br(),
                })
                save_json(DEVOTIONALS_FILE, devocionais)
                st.success("Devocional publicado!")

else:
    st.info("Escolha na barra lateral se você é Membro da Igreja ou Pastor para começar.")
