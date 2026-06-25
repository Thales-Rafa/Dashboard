import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import base64
import secrets
import unicodedata
from pathlib import Path
from datetime import datetime, date

st.set_page_config(page_title="Dashboard de Aderência", layout="wide")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "database.json"

DEFAULT_DB = {
    "settings": {
        "empresa_nome": "Famatur / Operação de Fretamento",
        "empresa_logo": "",
        "app_url": ""
    },
    "clientes": [],
    "importacoes": [],
    "metricas_diarias": [],
    "sem_embarque": []
}

def load_db():
    if not DB_PATH.exists():
        save_db(DEFAULT_DB)
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        for k, v in DEFAULT_DB.items():
            if k not in data:
                data[k] = v
        for k, v in DEFAULT_DB["settings"].items():
            if k not in data["settings"]:
                data["settings"][k] = v
        return data
    except Exception:
        return DEFAULT_DB.copy()

def save_db(db):
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

db = load_db()

PRIMARY_BG = "#0B1220"
SECONDARY_BG = "#111827"
CARD_BG = "#151F32"
BORDER = "#263449"
TEXT = "#F9FAFB"
MUTED = "#AAB4C3"
BLUE = "#60A5FA"
BLUE_DARK = "#1E3A5F"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#E5E7EB"
GREEN = "#22C55E"
RED = "#EF4444"
YELLOW = "#F59E0B"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(135deg, {PRIMARY_BG} 0%, #0F172A 45%, #111827 100%);
            color: {TEXT};
        }}
        section[data-testid="stSidebar"] {{
            background: {SECONDARY_BG};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] * {{ color: {TEXT}; }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1380px;
        }}
        h1, h2, h3 {{ color: {TEXT}; letter-spacing: -0.03em; }}
        .top-brand {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            margin-bottom: 18px;
        }}
        .brand-box {{ display: flex; align-items: center; gap: 14px; }}
        .brand-logo {{
            width: 74px;
            height: 74px;
            border-radius: 18px;
            object-fit: contain;
            background: rgba(255,255,255,0.06);
            border: 1px solid {BORDER};
            padding: 8px;
        }}
        .brand-name {{
            color: {MUTED};
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .hero {{
            background: radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 40%),
                        linear-gradient(135deg, rgba(21, 31, 50, 0.98), rgba(17, 24, 39, 0.98));
            border: 1px solid {BORDER};
            border-radius: 26px;
            padding: 30px 34px;
            margin-bottom: 24px;
            box-shadow: 0 22px 60px rgba(0,0,0,0.28);
        }}
        .hero-title {{
            font-size: 42px;
            line-height: 1.06;
            font-weight: 850;
            color: {TEXT};
            margin-bottom: 10px;
        }}
        .hero-subtitle {{
            color: {MUTED};
            font-size: 16px;
            max-width: 900px;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 800;
            color: {TEXT};
            margin: 28px 0 16px 0;
        }}
        .kpi-card {{
            background: linear-gradient(180deg, rgba(21, 31, 50, 0.98), rgba(17, 24, 39, 0.98));
            border: 1px solid {BORDER};
            border-radius: 20px;
            padding: 19px 16px;
            min-height: 136px;
            box-shadow: 0 16px 42px rgba(0,0,0,0.22);
            overflow: hidden;
        }}
        .kpi-label {{
            color: {MUTED};
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 14px;
            min-height: 32px;
        }}
        .kpi-value {{
            color: {WHITE};
            font-size: clamp(22px, 1.9vw, 32px);
            font-weight: 850;
            letter-spacing: -0.04em;
            line-height: 1;
            white-space: nowrap;
        }}
        .kpi-caption {{
            color: {BLUE};
            font-size: 12px;
            margin-top: 14px;
            line-height: 1.35;
        }}
        .info-box {{
            background: rgba(30, 58, 95, 0.38);
            border: 1px solid rgba(96, 165, 250, 0.35);
            border-radius: 18px;
            padding: 16px 18px;
            color: {LIGHT_GRAY};
            margin: 16px 0 12px 0;
            line-height: 1.55;
        }}
        .stButton button, .stDownloadButton button {{
            border-radius: 14px;
            border: 1px solid {BORDER};
            background: linear-gradient(135deg, {BLUE_DARK}, #2563EB);
            color: white;
            font-weight: 700;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: {CARD_BG};
            border-radius: 14px;
            padding: 10px 18px;
            border: 1px solid {BORDER};
        }}
        .stTabs [aria-selected="true"] {{ background: {BLUE_DARK}; }}
    </style>
    """,
    unsafe_allow_html=True
)

def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = " ".join(texto.split())
    return texto

def criar_slug(nome):
    texto = normalizar_texto(nome).lower().replace(" ", "-")
    texto = "".join(c for c in texto if c.isalnum() or c == "-")
    while "--" in texto:
        texto = texto.replace("--", "-")
    return texto.strip("-")

def formatar_num(valor):
    try:
        return f"{float(valor):,.0f}".replace(",", ".")
    except Exception:
        return "0"

def formatar_pct(valor):
    try:
        return f"{float(valor):,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00%"

def arquivo_para_base64(uploaded_file):
    if uploaded_file is None:
        return ""
    encoded = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    mime = uploaded_file.type or "image/png"
    return f"data:{mime};base64,{encoded}"

def imagem_html(src, nome):
    if not src:
        return ""
    return f"""
    <div class="brand-box">
        <img class="brand-logo" src="{src}" />
        <div><div class="brand-name">{nome}</div></div>
    </div>
    """

def kpi_card(label, value, caption=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def aplicar_layout(fig, titulo=None):
    fig.update_layout(
        title=dict(text=titulo or "", font=dict(size=18, color=TEXT, family="Arial"), x=0.02, y=0.95),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.55)",
        font=dict(color=LIGHT_GRAY, family="Arial"),
        margin=dict(l=20, r=20, t=70, b=45),
        xaxis=dict(showgrid=False, zeroline=False, color=MUTED, linecolor=BORDER),
        yaxis=dict(showgrid=True, gridcolor="rgba(229,231,235,0.10)", zeroline=False, color=MUTED, linecolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=LIGHT_GRAY)),
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor=BLUE, font=dict(color=WHITE))
    )
    return fig

def limpar_colunas(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.replace("\n", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )
    return df

def achar_coluna(df, opcoes):
    for opcao in opcoes:
        for col in df.columns:
            if opcao in col:
                return col
    return None

def preparar_embarques(df, cliente_nome):
    df = limpar_colunas(df)
    mapa = {
        "tipo": achar_coluna(df, ["TIPO", "MEIO", "FORMA"]),
        "passageiro": achar_coluna(df, ["PASSAGEIRO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO", "NOME"]),
        "linha": achar_coluna(df, ["LINHA", "ROTA"]),
        "prefixo": achar_coluna(df, ["PREFIXO", "VEICULO", "VEÍCULO", "CARRO"]),
        "data_hora": achar_coluna(df, ["DATA/HORA", "DATA HORA", "DATA", "HORARIO", "HORÁRIO"]),
    }
    if mapa["data_hora"] is None:
        raise ValueError("Não encontrei coluna de data/hora no relatório de embarque.")
    if mapa["passageiro"] is None:
        raise ValueError("Não encontrei coluna de passageiro/colaborador no relatório de embarque.")

    df["DATA_HORA_TRATADA"] = pd.to_datetime(df[mapa["data_hora"]], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["DATA_HORA_TRATADA"]).copy()
    df["DATA"] = df["DATA_HORA_TRATADA"].dt.date
    df["PASSAGEIRO_TRATADO"] = df[mapa["passageiro"]].astype(str).str.strip()
    df["PASSAGEIRO_KEY"] = df["PASSAGEIRO_TRATADO"].apply(normalizar_texto)
    df["CLIENTE_TRATADO"] = cliente_nome.upper()
    df["LINHA_TRATADA"] = df[mapa["linha"]].astype(str).str.strip().str.upper() if mapa["linha"] else "NÃO INFORMADO"
    df["TIPO_TRATADO"] = df[mapa["tipo"]].astype(str).str.strip().str.upper() if mapa["tipo"] else "NÃO INFORMADO"
    df["PREFIXO_TRATADO"] = df[mapa["prefixo"]].astype(str).str.strip() if mapa["prefixo"] else "NÃO INFORMADO"
    return df

def preparar_colaboradores(df, cliente_nome):
    df = limpar_colunas(df)
    mapa = {
        "nome": achar_coluna(df, ["NOME", "PASSAGEIRO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO"]),
        "linha": achar_coluna(df, ["LINHA", "ROTA"]),
        "turno": achar_coluna(df, ["TURNO"]),
        "cadastro": achar_coluna(df, ["CADASTRO", "DATA CADASTRO", "DT CADASTRO"]),
        "matricula": achar_coluna(df, ["MATRICULA", "MATRÍCULA"]),
    }
    if mapa["nome"] is None:
        raise ValueError("Não encontrei coluna NOME/PASSAGEIRO/COLABORADOR no arquivo de colaboradores.")

    df["NOME_TRATADO"] = df[mapa["nome"]].astype(str).str.strip()
    df["NOME_KEY"] = df["NOME_TRATADO"].apply(normalizar_texto)
    df["CLIENTE_TRATADO"] = cliente_nome.upper()
    df["LINHA_TRATADA"] = df[mapa["linha"]].astype(str).str.strip().str.upper() if mapa["linha"] else "NÃO INFORMADO"
    df["TURNO_TRATADO"] = df[mapa["turno"]].astype(str).str.strip().str.upper() if mapa["turno"] else "NÃO INFORMADO"
    df["MATRICULA_TRATADA"] = df[mapa["matricula"]].astype(str).str.strip() if mapa["matricula"] else ""
    df["DATA_CADASTRO"] = pd.to_datetime(df[mapa["cadastro"]], dayfirst=True, errors="coerce") if mapa["cadastro"] else pd.NaT
    return df[df["NOME_KEY"] != ""].drop_duplicates(subset=["NOME_KEY"]).copy()

def datas_operacao(inicio, fim, dias_semana):
    todas = pd.date_range(pd.to_datetime(inicio), pd.to_datetime(fim), freq="D")
    return [d.date() for d in todas if d.weekday() in dias_semana]

def get_cliente_por_slug_token(slug, token):
    for c in db["clientes"]:
        if c.get("slug") == slug and c.get("token") == token and c.get("ativo", True):
            return c
    return None

def importacoes_cliente(cliente_id):
    dados = [i for i in db["importacoes"] if i["cliente_id"] == cliente_id]
    return sorted(dados, key=lambda x: x["semana_inicio"])

def ultima_importacao(cliente_id):
    dados = importacoes_cliente(cliente_id)
    return dados[-1] if dados else None

def penultima_importacao(cliente_id):
    dados = importacoes_cliente(cliente_id)
    return dados[-2] if len(dados) >= 2 else None

def metricas_importacao(importacao_id):
    return [m for m in db["metricas_diarias"] if m["importacao_id"] == importacao_id]

def sem_embarque_importacao(importacao_id):
    return [s for s in db["sem_embarque"] if s["importacao_id"] == importacao_id]

def gerar_link_cliente(cliente):
    app_url = db["settings"].get("app_url", "").strip().rstrip("/")
    if not app_url:
        app_url = "COLE-A-URL-PUBLICA-DO-APP-NAS-CONFIGURACOES"
    return f"{app_url}/?cliente={cliente['slug']}&token={cliente['token']}"

def salvar_importacao(cliente, semana_inicio, semana_fim, dias_semana, embarques_por_dia, embarques_file, colaboradores_file):
    embarques_df = preparar_embarques(pd.read_excel(embarques_file), cliente["nome"])
    colaboradores_df = preparar_colaboradores(pd.read_excel(colaboradores_file), cliente["nome"])

    embarques_df = embarques_df[
        (embarques_df["DATA"] >= semana_inicio) &
        (embarques_df["DATA"] <= semana_fim)
    ].copy()

    datas = datas_operacao(semana_inicio, semana_fim, dias_semana)
    if not datas:
        raise ValueError("Nenhum dia de operação selecionado no período.")

    nomes_base = set(colaboradores_df["NOME_KEY"].unique())
    nomes_emb = set(embarques_df["PASSAGEIRO_KEY"].unique())

    metricas = []
    total_esperado = 0
    total_realizado = 0

    for d in datas:
        if colaboradores_df["DATA_CADASTRO"].notna().any():
            elegiveis = colaboradores_df[
                (colaboradores_df["DATA_CADASTRO"].isna()) |
                (colaboradores_df["DATA_CADASTRO"].dt.date <= d)
            ]
        else:
            elegiveis = colaboradores_df

        cadastrados_dia = elegiveis["NOME_KEY"].nunique()
        esperado = cadastrados_dia * embarques_por_dia
        realizado = int((embarques_df["DATA"] == d).sum())
        aderencia = (realizado / esperado * 100) if esperado else 0
        faltas = max(esperado - realizado, 0)

        total_esperado += esperado
        total_realizado += realizado

        metricas.append({
            "data": str(d),
            "colaboradores_cadastrados": int(cadastrados_dia),
            "esperado": int(esperado),
            "realizado": int(realizado),
            "aderencia": float(aderencia),
            "faltas": int(faltas)
        })

    aderencia_total = (total_realizado / total_esperado * 100) if total_esperado else 0
    faltas_total = max(total_esperado - total_realizado, 0)
    sem_emb_keys = nomes_base - nomes_emb
    sem_emb_df = colaboradores_df[colaboradores_df["NOME_KEY"].isin(sem_emb_keys)].copy()

    importacao_id = secrets.token_hex(8)
    registro = {
        "id": importacao_id,
        "cliente_id": cliente["id"],
        "cliente_nome": cliente["nome"],
        "semana_inicio": str(semana_inicio),
        "semana_fim": str(semana_fim),
        "data_importacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "dias_operacao": len(datas),
        "dias_operacao_config": ",".join(map(str, dias_semana)),
        "embarques_por_colaborador_dia": int(embarques_por_dia),
        "colaboradores_cadastrados": int(colaboradores_df["NOME_KEY"].nunique()),
        "colaboradores_que_embarcaram": int(embarques_df["PASSAGEIRO_KEY"].nunique()),
        "total_esperado": int(total_esperado),
        "total_realizado": int(total_realizado),
        "aderencia": float(aderencia_total),
        "faltas_estimadas": int(faltas_total),
        "colaboradores_sem_embarque": int(sem_emb_df.shape[0]),
        "arquivo_embarque": embarques_file.name,
        "arquivo_colaboradores": colaboradores_file.name
    }

    db["importacoes"].append(registro)

    for m in metricas:
        m["importacao_id"] = importacao_id
        m["cliente_id"] = cliente["id"]
        db["metricas_diarias"].append(m)

    for _, row in sem_emb_df.iterrows():
        db["sem_embarque"].append({
            "importacao_id": importacao_id,
            "cliente_id": cliente["id"],
            "nome": row.get("NOME_TRATADO", ""),
            "matricula": row.get("MATRICULA_TRATADA", ""),
            "linha": row.get("LINHA_TRATADA", ""),
            "turno": row.get("TURNO_TRATADO", "")
        })

    save_db(db)
    return registro

def render_header(cliente=None):
    empresa_logo = db["settings"].get("empresa_logo", "")
    empresa_nome = db["settings"].get("empresa_nome", "Operação de Fretamento")
    cliente_logo = cliente.get("logo", "") if cliente else ""
    cliente_nome = cliente.get("nome", "") if cliente else ""

    st.markdown(
        f"""
        <div class="top-brand">
            <div>{imagem_html(empresa_logo, empresa_nome)}</div>
            <div>{imagem_html(cliente_logo, cliente_nome)}</div>
        </div>
        <div class="hero">
            <div class="hero-title">Dashboard de Aderência de Embarque</div>
            <div class="hero-subtitle">
                Acompanhamento semanal de aderência por cliente, com histórico comparativo,
                evolução operacional e controle de colaboradores sem embarque.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_dashboard_cliente(cliente):
    render_header(cliente)

    atual = ultima_importacao(cliente["id"])
    anterior = penultima_importacao(cliente["id"])

    if not atual:
        st.info("Ainda não há importações salvas para este cliente.")
        return

    variacao = atual["aderencia"] - anterior["aderencia"] if anterior else None

    st.markdown('<div class="section-title">Resumo semanal</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Aderência atual", formatar_pct(atual["aderencia"]), f"{atual['semana_inicio']} até {atual['semana_fim']}")
    with c2:
        kpi_card("Semana anterior", formatar_pct(anterior["aderencia"]) if anterior else "—", "Comparativo")
    with c3:
        if variacao is None:
            valor_var = "—"
            caption = "Sem base anterior"
        else:
            sinal = "+" if variacao >= 0 else ""
            valor_var = f"{sinal}{formatar_pct(variacao)}"
            caption = "Variação em pontos percentuais"
        kpi_card("Variação semanal", valor_var, caption)
    with c4:
        kpi_card("Esperado", formatar_num(atual["total_esperado"]), "Embarques previstos")
    with c5:
        kpi_card("Realizado", formatar_num(atual["total_realizado"]), "Embarques realizados")
    with c6:
        kpi_card("Sem embarque", formatar_num(atual["colaboradores_sem_embarque"]), "Colaboradores cadastrados")

    st.markdown(
        f"""
        <div class="info-box">
            <strong>Regra da semana:</strong> {formatar_num(atual['colaboradores_cadastrados'])} colaboradores cadastrados × 
            {atual['embarques_por_colaborador_dia']} embarques por colaborador/dia × {atual['dias_operacao']} dias de operação.
            <br>
            <strong>Última atualização:</strong> {atual['data_importacao']}.
        </div>
        """,
        unsafe_allow_html=True
    )

    aba1, aba2, aba3 = st.tabs(["Visão semanal", "Histórico", "Colaboradores sem embarque"])

    with aba1:
        metricas = pd.DataFrame(metricas_importacao(atual["id"]))
        if not metricas.empty:
            metricas["data"] = pd.to_datetime(metricas["data"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=metricas["data"], y=metricas["esperado"], mode="lines", name="Esperado", line=dict(color=LIGHT_GRAY, width=2, dash="dash")))
            fig.add_trace(go.Scatter(x=metricas["data"], y=metricas["realizado"], mode="lines+markers", name="Realizado", line=dict(color=BLUE, width=3), marker=dict(size=7, color=WHITE, line=dict(color=BLUE, width=2)), fill="tozeroy", fillcolor="rgba(96,165,250,0.10)"))
            fig.update_xaxes(title_text="Data")
            fig.update_yaxes(title_text="Quantidade de embarques")
            st.plotly_chart(aplicar_layout(fig, "Esperado x realizado por dia"), use_container_width=True)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=metricas["data"], y=metricas["aderencia"], mode="lines+markers", name="Aderência", line=dict(color=BLUE, width=3), marker=dict(size=7, color=WHITE, line=dict(color=BLUE, width=2))))
            fig2.update_xaxes(title_text="Data")
            fig2.update_yaxes(title_text="Aderência (%)")
            st.plotly_chart(aplicar_layout(fig2, "Aderência diária"), use_container_width=True)

    with aba2:
        hist = pd.DataFrame(importacoes_cliente(cliente["id"]))
        if hist.empty:
            st.info("Sem histórico.")
        else:
            hist["semana_inicio_dt"] = pd.to_datetime(hist["semana_inicio"])
            hist = hist.sort_values("semana_inicio_dt")
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(x=hist["semana_inicio_dt"], y=hist["aderencia"], mode="lines+markers", name="Aderência semanal", line=dict(color=BLUE, width=3), marker=dict(size=8, color=WHITE, line=dict(color=BLUE, width=2))))
            fig_hist.update_xaxes(title_text="Semana")
            fig_hist.update_yaxes(title_text="Aderência (%)")
            st.plotly_chart(aplicar_layout(fig_hist, "Histórico semanal de aderência"), use_container_width=True)

            tabela = hist[["semana_inicio", "semana_fim", "colaboradores_cadastrados", "dias_operacao", "total_esperado", "total_realizado", "aderencia", "faltas_estimadas", "colaboradores_sem_embarque", "data_importacao"]].rename(columns={
                "semana_inicio": "Semana início",
                "semana_fim": "Semana fim",
                "colaboradores_cadastrados": "Colaboradores",
                "dias_operacao": "Dias operação",
                "total_esperado": "Esperado",
                "total_realizado": "Realizado",
                "aderencia": "Aderência (%)",
                "faltas_estimadas": "Faltas estimadas",
                "colaboradores_sem_embarque": "Sem embarque",
                "data_importacao": "Importado em"
            })
            st.dataframe(tabela, use_container_width=True, hide_index=True)

    with aba3:
        sem = pd.DataFrame(sem_embarque_importacao(atual["id"]))
        if sem.empty:
            st.success("Não há colaboradores sem embarque nesta semana.")
        else:
            tabela = sem[["nome", "matricula", "linha", "turno"]].rename(columns={"nome": "Colaborador", "matricula": "Matrícula", "linha": "Linha", "turno": "Turno"})
            st.dataframe(tabela, use_container_width=True, hide_index=True)

def render_admin():
    st.sidebar.markdown("### Acesso ADM")
    senha = st.sidebar.text_input("Senha ADM", type="password")
    senha_correta = st.secrets.get("ADMIN_PASSWORD", "admin123")

    if senha != senha_correta:
        st.warning("Informe a senha de administrador para acessar todos os clientes.")
        st.info("No MVP, a senha padrão é admin123. Troque isso no Streamlit Secrets.")
        return

    render_header()
    st.markdown('<div class="section-title">Painel administrativo</div>', unsafe_allow_html=True)

    aba1, aba2, aba3, aba4 = st.tabs(["Visão geral ADM", "Clientes", "Nova importação semanal", "Configurações e links"])

    with aba1:
        total_clientes = len(db["clientes"])
        total_importacoes = len(db["importacoes"])
        media_aderencia = sum(i["aderencia"] for i in db["importacoes"]) / len(db["importacoes"]) if db["importacoes"] else 0
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Clientes cadastrados", formatar_num(total_clientes), "Dashboards ativos")
        with c2:
            kpi_card("Importações salvas", formatar_num(total_importacoes), "Histórico semanal")
        with c3:
            kpi_card("Média geral", formatar_pct(media_aderencia), "Média das importações")

        if db["importacoes"]:
            hist = pd.DataFrame(db["importacoes"])
            resumo = hist.groupby("cliente_nome", as_index=False).agg(
                importacoes=("id", "count"),
                aderencia_media=("aderencia", "mean"),
                ultimo_realizado=("total_realizado", "last"),
                ultimo_esperado=("total_esperado", "last"),
                ultima_importacao=("data_importacao", "last")
            )
            st.dataframe(resumo, use_container_width=True, hide_index=True)

    with aba2:
        st.subheader("Cadastrar novo cliente")
        with st.form("form_cliente"):
            nome = st.text_input("Nome do cliente")
            logo_cliente = st.file_uploader("Logo do cliente", type=["png", "jpg", "jpeg"], key="logo_cliente_form")
            criar = st.form_submit_button("Cadastrar cliente")

            if criar:
                if not nome.strip():
                    st.error("Informe o nome do cliente.")
                else:
                    slug = criar_slug(nome)
                    if any(c["slug"] == slug for c in db["clientes"]):
                        st.error("Já existe um cliente com esse nome/slug.")
                    else:
                        novo = {
                            "id": secrets.token_hex(6),
                            "nome": nome.strip(),
                            "slug": slug,
                            "token": secrets.token_urlsafe(18),
                            "ativo": True,
                            "logo": arquivo_para_base64(logo_cliente),
                            "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }
                        db["clientes"].append(novo)
                        save_db(db)
                        st.success("Cliente cadastrado com sucesso.")
                        st.rerun()

        st.subheader("Clientes cadastrados")
        if not db["clientes"]:
            st.info("Nenhum cliente cadastrado ainda.")
        else:
            for cliente in db["clientes"]:
                with st.expander(cliente["nome"]):
                    st.write(f"Slug: `{cliente['slug']}`")
                    st.write(f"Token: `{cliente['token']}`")
                    st.write("Link público do cliente:")
                    st.code(gerar_link_cliente(cliente))
                    if not db["settings"].get("app_url"):
                        st.warning("Cadastre a URL pública do app na aba Configurações e links para o link ficar correto.")
                    if cliente.get("logo"):
                        st.image(cliente["logo"], width=120)

    with aba3:
        if not db["clientes"]:
            st.info("Cadastre um cliente primeiro.")
        else:
            nomes = {c["nome"]: c for c in db["clientes"]}
            cliente_nome = st.selectbox("Cliente", list(nomes.keys()))
            cliente = nomes[cliente_nome]

            col_data1, col_data2 = st.columns(2)
            with col_data1:
                semana_inicio = st.date_input("Início da semana", value=date.today())
            with col_data2:
                semana_fim = st.date_input("Fim da semana", value=date.today())

            embarques_por_dia = st.number_input("Embarques esperados por colaborador/dia", min_value=1, max_value=10, value=2, step=1)
            preset = st.selectbox("Dias que a operação roda", ["Segunda a sexta", "Segunda a sábado", "Segunda a domingo", "Personalizado"], index=2)

            if preset == "Segunda a sexta":
                dias_semana = [0, 1, 2, 3, 4]
            elif preset == "Segunda a sábado":
                dias_semana = [0, 1, 2, 3, 4, 5]
            elif preset == "Segunda a domingo":
                dias_semana = [0, 1, 2, 3, 4, 5, 6]
            else:
                mapa = {"Segunda": 0, "Terça": 1, "Quarta": 2, "Quinta": 3, "Sexta": 4, "Sábado": 5, "Domingo": 6}
                escolhidos = st.multiselect("Selecione os dias", list(mapa.keys()), default=list(mapa.keys()))
                dias_semana = [mapa[d] for d in escolhidos]

            rel_embarque = st.file_uploader("Relatório de embarque", type=["xlsx", "xls"], key="rel_embarque_admin")
            base_colab = st.file_uploader("Arquivo de colaboradores cadastrados", type=["xlsx", "xls"], key="base_colab_admin")

            if st.button("Processar e salvar semana"):
                if rel_embarque is None or base_colab is None:
                    st.error("Envie os dois arquivos.")
                elif semana_fim < semana_inicio:
                    st.error("A data final não pode ser menor que a inicial.")
                else:
                    try:
                        registro = salvar_importacao(cliente, semana_inicio, semana_fim, dias_semana, embarques_por_dia, rel_embarque, base_colab)
                        st.success("Semana salva com sucesso.")
                        st.json({
                            "Cliente": registro["cliente_nome"],
                            "Aderência": formatar_pct(registro["aderencia"]),
                            "Esperado": registro["total_esperado"],
                            "Realizado": registro["total_realizado"],
                            "Sem embarque": registro["colaboradores_sem_embarque"]
                        })
                    except Exception as e:
                        st.error(f"Erro ao processar: {e}")

    with aba4:
        st.subheader("URL pública do app")
        st.markdown("Cole aqui a URL pública que termina com `.streamlit.app`. Não use a URL do painel interno do Streamlit.")
        app_url = st.text_input("URL pública do app", value=db["settings"].get("app_url", ""), placeholder="https://dashboard-famatur.streamlit.app")

        st.subheader("Logo e nome da sua empresa")
        empresa_nome = st.text_input("Nome da sua empresa/operação", value=db["settings"].get("empresa_nome", ""))
        empresa_logo = st.file_uploader("Logo da sua empresa", type=["png", "jpg", "jpeg"], key="empresa_logo_upload")

        if st.button("Salvar configurações"):
            db["settings"]["app_url"] = app_url.strip().rstrip("/")
            db["settings"]["empresa_nome"] = empresa_nome
            if empresa_logo is not None:
                db["settings"]["empresa_logo"] = arquivo_para_base64(empresa_logo)
            save_db(db)
            st.success("Configurações salvas.")
            st.rerun()

        if db["settings"].get("empresa_logo"):
            st.image(db["settings"]["empresa_logo"], width=160)

        st.subheader("Links públicos dos clientes")
        if not db["clientes"]:
            st.info("Cadastre clientes para gerar links.")
        else:
            for cliente in db["clientes"]:
                st.write(f"**{cliente['nome']}**")
                st.code(gerar_link_cliente(cliente))

params = st.query_params
cliente_slug = params.get("cliente", None)
token = params.get("token", None)

if cliente_slug and token:
    cliente = get_cliente_por_slug_token(cliente_slug, token)
    if not cliente:
        st.error("Link inválido ou cliente não encontrado.")
    else:
        render_dashboard_cliente(cliente)
else:
    render_admin()