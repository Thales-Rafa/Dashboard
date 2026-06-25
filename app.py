import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import base64
import secrets
import unicodedata
from pathlib import Path
from datetime import datetime, date

st.set_page_config(page_title="Dashboard de Aderência", layout="wide")

st.markdown("""
<style>
.client-logo-section {
    margin-top: 24px;
    padding-top: 22px;
    border-top: 1px solid rgba(229,231,235,0.12);
}
.client-logo-section-title {
    color: #E5E7EB;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.client-logo-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
}
.client-logo-card {
    width: 145px;
    min-height: 126px;
    border: 1px solid rgba(229,231,235,0.16);
    background: rgba(15,23,42,0.78);
    border-radius: 20px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    text-decoration: none !important;
    transition: all .18s ease;
}
.client-logo-card:hover {
    transform: translateY(-2px);
    border-color: rgba(96,165,250,0.62);
    background: rgba(30,58,95,0.46);
}
.client-logo-img {
    width: 78px;
    height: 68px;
    object-fit: contain;
    border-radius: 14px;
    background: rgba(255,255,255,0.06);
    padding: 8px;
}
.client-logo-placeholder {
    width: 78px;
    height: 68px;
    border-radius: 14px;
    background: #1E3A5F;
    color: white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size: 24px;
    font-weight: 900;
}
.client-logo-card span {
    color: #F9FAFB;
    font-size: 13px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden !important; height: 0% !important; position: fixed;}
[data-testid="stDecoration"] {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


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
        if not isinstance(data, dict):
            data = DEFAULT_DB.copy()

        for k, v in DEFAULT_DB.items():
            if k not in data:
                data[k] = v

        if "settings" not in data or not isinstance(data["settings"], dict):
            data["settings"] = DEFAULT_DB["settings"].copy()

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
    src = src or ""
    nome = nome or ""

    if src:
        return f'<div class="brand-box"><img class="brand-logo" src="{src}" /><div><div class="brand-name">{nome}</div></div></div>'

    return f'<div class="brand-box"><div><div class="brand-name">{nome}</div></div></div>'

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

def periodo_relatorio_embarque(uploaded_file):
    if uploaded_file is None:
        return None, None, None

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    df = pd.read_excel(uploaded_file)

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    df = limpar_colunas(df)
    col_data = achar_coluna(df, ["DATA/HORA", "DATA HORA", "DATA", "HORARIO", "HORÁRIO"])

    if col_data is None:
        return None, None, 0

    datas = pd.to_datetime(df[col_data], dayfirst=True, errors="coerce").dropna()

    if datas.empty:
        return None, None, 0

    return datas.dt.date.min(), datas.dt.date.max(), int(datas.shape[0])


def identificar_periodo_relatorio(uploaded_file, cliente_nome):
    if uploaded_file is None:
        return None, None, 0

    posicao = uploaded_file.tell()
    uploaded_file.seek(0)
    df_temp = pd.read_excel(uploaded_file)
    uploaded_file.seek(posicao)

    df_temp = preparar_embarques(df_temp, cliente_nome)
    if df_temp.empty:
        return None, None, 0

    return df_temp["DATA"].min(), df_temp["DATA"].max(), int(df_temp.shape[0])

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

def filtrar_metricas_por_periodo(metricas_df, modo_filtro, data_ini=None, data_fim=None):
    if metricas_df.empty:
        return metricas_df

    metricas_df = metricas_df.copy()
    metricas_df["data"] = pd.to_datetime(metricas_df["data"])

    if modo_filtro == "Todo o período":
        return metricas_df

    if modo_filtro == "Por dia" and data_ini is not None:
        data_ini = pd.to_datetime(data_ini)
        return metricas_df[metricas_df["data"].dt.date == data_ini.date()].copy()

    if modo_filtro == "Intervalo personalizado" and data_ini is not None and data_fim is not None:
        data_ini = pd.to_datetime(data_ini)
        data_fim = pd.to_datetime(data_fim)
        return metricas_df[
            (metricas_df["data"] >= data_ini) &
            (metricas_df["data"] <= data_fim)
        ].copy()

    return metricas_df

def recalcular_resumo_metricas(metricas_df, importacao):
    if metricas_df.empty:
        return {
            "total_esperado": 0,
            "total_realizado": 0,
            "aderencia": 0,
            "faltas_estimadas": 0,
            "dias_operacao": 0,
            "colaboradores_cadastrados": importacao.get("colaboradores_cadastrados", 0),
            "colaboradores_que_embarcaram": importacao.get("colaboradores_que_embarcaram", 0),
            "colaboradores_sem_embarque": importacao.get("colaboradores_sem_embarque", 0),
        }

    total_esperado = int(metricas_df["esperado"].sum())
    total_realizado = int(metricas_df["realizado"].sum())
    aderencia = (total_realizado / total_esperado * 100) if total_esperado else 0
    faltas = max(total_esperado - total_realizado, 0)

    return {
        "total_esperado": total_esperado,
        "total_realizado": total_realizado,
        "aderencia": aderencia,
        "faltas_estimadas": faltas,
        "dias_operacao": int(metricas_df.shape[0]),
        "colaboradores_cadastrados": int(metricas_df["colaboradores_cadastrados"].max()) if "colaboradores_cadastrados" in metricas_df.columns and not metricas_df.empty else importacao.get("colaboradores_cadastrados", 0),
        "colaboradores_que_embarcaram": importacao.get("colaboradores_que_embarcaram", 0),
        "colaboradores_sem_embarque": importacao.get("colaboradores_sem_embarque", 0),
    }


def remover_importacao(importacao_id):
    db["importacoes"] = [i for i in db["importacoes"] if i["id"] != importacao_id]
    db["metricas_diarias"] = [m for m in db["metricas_diarias"] if m["importacao_id"] != importacao_id]
    db["sem_embarque"] = [s for s in db["sem_embarque"] if s["importacao_id"] != importacao_id]
    save_db(db)

def encontrar_importacao_semana(cliente_id, semana_inicio, semana_fim):
    inicio_txt = str(semana_inicio)
    fim_txt = str(semana_fim)
    for i in db["importacoes"]:
        if i["cliente_id"] == cliente_id and i["semana_inicio"] == inicio_txt and i["semana_fim"] == fim_txt:
            return i
    return None


def atualizar_cliente(cliente_id, nome=None, ativo=None, logo=None, regenerar_token=False):
    for c in db["clientes"]:
        if c["id"] == cliente_id:
            if nome is not None and nome.strip():
                novo_slug = criar_slug(nome)
                slug_em_uso = any(outro["slug"] == novo_slug and outro["id"] != cliente_id for outro in db["clientes"])
                if slug_em_uso:
                    raise ValueError("Já existe outro cliente com este nome/slug.")
                c["nome"] = nome.strip()
                c["slug"] = novo_slug
            if ativo is not None:
                c["ativo"] = bool(ativo)
            if logo is not None:
                c["logo"] = logo
            if regenerar_token:
                c["token"] = secrets.token_urlsafe(18)
            c["data_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            save_db(db)
            return c
    raise ValueError("Cliente não encontrado.")

def excluir_cliente(cliente_id):
    db["clientes"] = [c for c in db["clientes"] if c["id"] != cliente_id]
    ids_importacoes = [i["id"] for i in db["importacoes"] if i["cliente_id"] == cliente_id]
    db["importacoes"] = [i for i in db["importacoes"] if i["cliente_id"] != cliente_id]
    db["metricas_diarias"] = [m for m in db["metricas_diarias"] if m.get("importacao_id") not in ids_importacoes and m.get("cliente_id") != cliente_id]
    db["sem_embarque"] = [s for s in db["sem_embarque"] if s.get("importacao_id") not in ids_importacoes and s.get("cliente_id") != cliente_id]
    save_db(db)

def atualizar_importacao_manual(importacao_id, campos):
    for i in db["importacoes"]:
        if i["id"] == importacao_id:
            for k, v in campos.items():
                if k in i:
                    i[k] = v
            i["data_atualizacao_manual"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            save_db(db)
            return i
    raise ValueError("Importação não encontrada.")

def limpar_banco_total():
    db["clientes"] = []
    db["importacoes"] = []
    db["metricas_diarias"] = []
    db["sem_embarque"] = []
    save_db(db)

def status_adesao(valor_pct):
    if valor_pct >= 85:
        return "Bom"
    if valor_pct >= 70:
        return "Atenção"
    return "Crítico"

def status_faltantes(valor):
    if valor <= 0:
        return "Regularizado"
    return "Necessário ação"

def tabela_indicadores_adesao(importacao):
    total_cadastrados = int(importacao.get("colaboradores_cadastrados", 0))
    unicos_embarcaram = int(importacao.get("colaboradores_que_embarcaram", 0))
    faltantes_aderir = max(total_cadastrados - unicos_embarcaram, 0)
    adesao_pct = (unicos_embarcaram / total_cadastrados * 100) if total_cadastrados else 0

    return pd.DataFrame([
        {
            "INDICADOR": "Passageiros que embarcaram (únicos)",
            "VALOR": formatar_num(unicos_embarcaram),
            "STATUS": "Em andamento" if unicos_embarcaram < total_cadastrados else "Completo"
        },
        {
            "INDICADOR": "Porcentagem de adesão",
            "VALOR": formatar_pct(adesao_pct),
            "STATUS": status_adesao(adesao_pct)
        },
        {
            "INDICADOR": "Faltantes para aderir",
            "VALOR": formatar_num(faltantes_aderir),
            "STATUS": status_faltantes(faltantes_aderir)
        },
        {
            "INDICADOR": "Total de colaboradores cadastrados",
            "VALOR": formatar_num(total_cadastrados),
            "STATUS": "Base total"
        },
    ])

def tabela_resumo_adesao(importacao):
    total_cadastrados = int(importacao.get("colaboradores_cadastrados", 0))
    unicos_embarcaram = int(importacao.get("colaboradores_que_embarcaram", 0))
    faltantes = max(total_cadastrados - unicos_embarcaram, 0)

    return pd.DataFrame([
        {"STATUS": "Embarcaram", "VALOR": unicos_embarcaram},
        {"STATUS": "Faltantes", "VALOR": faltantes},
        {"STATUS": "Total cadastrados", "VALOR": total_cadastrados},
    ])


def gerar_link_cliente(cliente):
    app_url = db["settings"].get("app_url", "").strip().rstrip("/")
    if not app_url:
        app_url = "COLE-A-URL-PUBLICA-DO-APP-NAS-CONFIGURACOES"
    return f"{app_url}/?cliente={cliente['slug']}&token={cliente['token']}"

def gerar_opcoes_semanais(metricas_df):
    if metricas_df.empty:
        return {}

    temp = metricas_df.copy()
    temp["data"] = pd.to_datetime(temp["data"])
    temp["semana_inicio"] = temp["data"] - pd.to_timedelta(temp["data"].dt.weekday, unit="D")
    temp["semana_fim"] = temp["semana_inicio"] + pd.Timedelta(days=6)

    semanas = temp[["semana_inicio", "semana_fim"]].drop_duplicates().sort_values("semana_inicio")

    opcoes = {}
    for _, row in semanas.iterrows():
        label = f"Semana {row['semana_inicio'].strftime('%d/%m/%Y')} até {row['semana_fim'].strftime('%d/%m/%Y')}"
        opcoes[label] = (row["semana_inicio"].date(), row["semana_fim"].date())
    return opcoes

def html_logo_cliente(cliente):
    nome = cliente.get("nome", "Cliente")
    logo = cliente.get("logo", "") or ""
    link = gerar_link_cliente(cliente)

    if logo:
        logo_html = f'<img class="client-logo-img" src="{logo}" />'
    else:
        iniciais = "".join([p[:1] for p in nome.split()[:2]]).upper()
        logo_html = f'<div class="client-logo-placeholder">{iniciais}</div>'

    return f'<a class="client-logo-card" href="{link}" target="_blank" title="Abrir dashboard público de {nome}">{logo_html}<span>{nome}</span></a>'

def render_clientes_logos_admin():
    clientes_ativos = [c for c in db.get("clientes", []) if c.get("ativo", True)]
    if not clientes_ativos:
        return

    cards = "".join([html_logo_cliente(c) for c in clientes_ativos])
    html = f'<div class="client-logo-section"><div class="client-logo-section-title">Dashboards dos clientes</div><div class="client-logo-grid">{cards}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_header(cliente=None):
    settings = db.get("settings", {}) if isinstance(db, dict) else {}
    empresa_logo = settings.get("empresa_logo", "") or ""
    empresa_nome = settings.get("empresa_nome", "Operação de Fretamento") or "Operação de Fretamento"

    cliente_logo = ""
    cliente_nome = ""

    if isinstance(cliente, dict):
        cliente_logo = cliente.get("logo", "") or ""
        cliente_nome = cliente.get("nome", "") or ""

    if cliente:
        # Dashboard público do cliente:
        # Famatur no topo esquerdo, cliente no topo direito.
        topo = f'<div class="top-brand"><div>{imagem_html(empresa_logo, empresa_nome)}</div><div>{imagem_html(cliente_logo, cliente_nome) if (cliente_logo or cliente_nome) else ""}</div></div>'
        st.markdown(topo, unsafe_allow_html=True)

        hero = '<div class="hero"><div class="hero-title">Dashboard de Aderência de Embarque</div><div class="hero-subtitle">Acompanhamento de aderência do cliente, com evolução semanal, histórico comparativo e controle de colaboradores sem embarque.</div></div>'
        st.markdown(hero, unsafe_allow_html=True)
        return

    # Painel ADM:
    # Logo da Famatur dentro do bloco principal e logos clicáveis dos clientes abaixo.
    logo_html = ""
    if empresa_logo:
        logo_html = f'<div style="margin-bottom:22px;"><img class="brand-logo" src="{empresa_logo}" style="width:96px;height:96px;" /></div>'

    hero = f'<div class="hero">{logo_html}<div class="hero-title">Dashboard de Aderência de Embarque</div><div class="hero-subtitle">Acompanhamento de aderência por cliente, com histórico comparativo, evolução operacional e controle de colaboradores sem embarque.</div></div>'
    st.markdown(hero, unsafe_allow_html=True)

    render_clientes_logos_admin()

def render_dashboard_cliente(cliente):
    render_header(cliente)

    atual = ultima_importacao(cliente["id"])
    anterior = penultima_importacao(cliente["id"])

    if not atual:
        st.info("Ainda não há importações salvas para este cliente.")
        return

    metricas_base = pd.DataFrame(metricas_importacao(atual["id"]))
    if not metricas_base.empty:
        metricas_base["data"] = pd.to_datetime(metricas_base["data"])
        data_min_filtro = metricas_base["data"].min().date()
        data_max_filtro = metricas_base["data"].max().date()
    else:
        data_min_filtro = date.today()
        data_max_filtro = date.today()

    st.markdown('<div class="section-title">Filtros</div>', unsafe_allow_html=True)

    opcoes_semanais = gerar_opcoes_semanais(metricas_base)
    col_filtro1, col_filtro2, col_filtro3 = st.columns([1.1, 1.4, 1.5])

    with col_filtro1:
        modo_filtro = st.selectbox(
            "Visualizar",
            ["Por semana", "Todo o período", "Por dia", "Intervalo personalizado"],
            index=0
        )

    filtro_data_ini = None
    filtro_data_fim = None

    if modo_filtro == "Por semana":
        with col_filtro2:
            if opcoes_semanais:
                semana_label = st.selectbox("Semana", list(opcoes_semanais.keys()), index=len(opcoes_semanais) - 1)
                filtro_data_ini, filtro_data_fim = opcoes_semanais[semana_label]
            else:
                semana_label = "Sem semanas disponíveis"
                filtro_data_ini, filtro_data_fim = data_min_filtro, data_max_filtro

        with col_filtro3:
            st.markdown(
                f"""
                <div class="info-box">
                    Visualização semanal ativa. {semana_label}.
                </div>
                """,
                unsafe_allow_html=True
            )

    elif modo_filtro == "Por dia":
        with col_filtro2:
            filtro_data_ini = st.date_input(
                "Dia",
                value=data_min_filtro,
                min_value=data_min_filtro,
                max_value=data_max_filtro,
                format="DD/MM/YYYY"
            )
        with col_filtro3:
            st.markdown(
                """
                <div class="info-box">
                    Exibindo apenas o dia selecionado dentro do período importado.
                </div>
                """,
                unsafe_allow_html=True
            )

    elif modo_filtro == "Intervalo personalizado":
        with col_filtro2:
            filtro_intervalo = st.date_input(
                "Intervalo",
                value=(data_min_filtro, data_max_filtro),
                min_value=data_min_filtro,
                max_value=data_max_filtro,
                format="DD/MM/YYYY"
            )

        if isinstance(filtro_intervalo, tuple) and len(filtro_intervalo) == 2:
            filtro_data_ini, filtro_data_fim = filtro_intervalo
        else:
            filtro_data_ini, filtro_data_fim = data_min_filtro, data_max_filtro

        with col_filtro3:
            st.markdown(
                """
                <div class="info-box">
                    Exibindo intervalo personalizado dentro da importação atual.
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        with col_filtro2:
            st.markdown(
                f"""
                <div class="info-box">
                    Período completo: {data_min_filtro.strftime('%d/%m/%Y')} até {data_max_filtro.strftime('%d/%m/%Y')}.
                </div>
                """,
                unsafe_allow_html=True
            )

    if modo_filtro == "Por semana":
        metricas_filtradas = filtrar_metricas_por_periodo(metricas_base, "Intervalo personalizado", filtro_data_ini, filtro_data_fim)
    else:
        metricas_filtradas = filtrar_metricas_por_periodo(metricas_base, modo_filtro, filtro_data_ini, filtro_data_fim)
    resumo_filtro = recalcular_resumo_metricas(metricas_filtradas, atual)

    if modo_filtro == "Todo o período":
        titulo_periodo = f"{pd.to_datetime(atual['semana_inicio']).strftime('%d/%m/%Y')} até {pd.to_datetime(atual['semana_fim']).strftime('%d/%m/%Y')}"
    elif modo_filtro == "Por dia":
        titulo_periodo = filtro_data_ini.strftime("%d/%m/%Y")
    else:
        titulo_periodo = f"{filtro_data_ini.strftime('%d/%m/%Y')} até {filtro_data_fim.strftime('%d/%m/%Y')}"

    variacao = atual["aderencia"] - anterior["aderencia"] if anterior else None

    st.markdown('<div class="section-title">Resumo do período</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Aderência atual", formatar_pct(resumo_filtro["aderencia"]), titulo_periodo)
    with c2:
        kpi_card("Importação anterior", formatar_pct(anterior["aderencia"]) if anterior else "—", "Comparativo")
    with c3:
        if variacao is None:
            valor_var = "—"
            caption = "Sem base anterior"
        else:
            sinal = "+" if variacao >= 0 else ""
            valor_var = f"{sinal}{formatar_pct(variacao)}"
            caption = "Variação em pontos percentuais"
        kpi_card("Variação", valor_var, caption)
    with c4:
        kpi_card("Esperado", formatar_num(resumo_filtro["total_esperado"]), "Embarques previstos")
    with c5:
        kpi_card("Realizado", formatar_num(resumo_filtro["total_realizado"]), "Embarques realizados")
    with c6:
        kpi_card("Sem embarque", formatar_num(resumo_filtro["colaboradores_sem_embarque"]), "Colaboradores cadastrados")

    st.markdown(
        f"""
        <div class="info-box">
            <strong>Regra do período:</strong> {formatar_num(resumo_filtro['colaboradores_cadastrados'])} colaboradores cadastrados × 
            {atual['embarques_por_colaborador_dia']} embarques por colaborador/dia × {resumo_filtro['dias_operacao']} dias filtrados.
            <br>
            <strong>Última atualização:</strong> {atual['data_importacao']}.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">Adesão de colaboradores</div>', unsafe_allow_html=True)
    total_cadastrados = int(atual.get("colaboradores_cadastrados", 0))
    unicos_embarcaram = int(atual.get("colaboradores_que_embarcaram", 0))
    faltantes_aderir = max(total_cadastrados - unicos_embarcaram, 0)

    col_pizza, col_tab1, col_tab2 = st.columns([1.1, 1.4, 0.9])

    with col_pizza:
        pizza_df = pd.DataFrame({
            "Categoria": ["Embarcaram", "Faltantes"],
            "Quantidade": [unicos_embarcaram, faltantes_aderir]
        })
        fig_pizza = px.pie(
            pizza_df,
            names="Categoria",
            values="Quantidade",
            hole=0.58,
            color_discrete_sequence=[BLUE, "#CBD5E1"]
        )
        fig_pizza.update_traces(
            textinfo="label+percent+value",
            marker=dict(line=dict(color=PRIMARY_BG, width=2))
        )
        fig_pizza = aplicar_layout(fig_pizza, "Cadastrados x colaboradores que embarcaram")
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_tab1:
        st.subheader("Indicadores de adesão")
        st.dataframe(tabela_indicadores_adesao(atual), use_container_width=True, hide_index=True)

    with col_tab2:
        st.subheader("Resumo")
        st.dataframe(tabela_resumo_adesao(atual), use_container_width=True, hide_index=True)

    aba1, aba2, aba3 = st.tabs(["Visão do período", "Histórico", "Colaboradores sem embarque"])

    with aba1:
        metricas = metricas_filtradas.copy()
        if not metricas.empty:
            metricas["data"] = pd.to_datetime(metricas["data"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=metricas["data"], y=metricas["esperado"], mode="lines", name="Esperado", line=dict(color=LIGHT_GRAY, width=2, dash="dash")))
            fig.add_trace(go.Scatter(x=metricas["data"], y=metricas["realizado"], mode="lines+markers", name="Realizado", line=dict(color=BLUE, width=3), marker=dict(size=7, color=WHITE, line=dict(color=BLUE, width=2)), fill="tozeroy", fillcolor="rgba(96,165,250,0.10)"))
            fig.update_xaxes(title_text="Data", tickformat="%d/%m/%Y")
            fig.update_yaxes(title_text="Quantidade de embarques")
            st.plotly_chart(aplicar_layout(fig, "Esperado x realizado por dia"), use_container_width=True)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=metricas["data"], y=metricas["aderencia"], mode="lines+markers", name="Aderência", line=dict(color=BLUE, width=3), marker=dict(size=7, color=WHITE, line=dict(color=BLUE, width=2))))
            fig2.update_xaxes(title_text="Data", tickformat="%d/%m/%Y")
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
            fig_hist.add_trace(go.Scatter(x=hist["semana_inicio_dt"], y=hist["aderencia"], mode="lines+markers", name="Aderência por importação", line=dict(color=BLUE, width=3), marker=dict(size=8, color=WHITE, line=dict(color=BLUE, width=2))))
            fig_hist.update_xaxes(title_text="Semana", tickformat="%d/%m/%Y")
            fig_hist.update_yaxes(title_text="Aderência (%)")
            st.plotly_chart(aplicar_layout(fig_hist, "Histórico por importação de aderência"), use_container_width=True)

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
    senha_correta = st.secrets.get("ADMIN_PASSWORD", "admin123")

    if "adm_autenticado" not in st.session_state:
        st.session_state["adm_autenticado"] = False

    if not st.session_state["adm_autenticado"]:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-title">Acesso Administrativo</div>
                <div class="hero-subtitle">
                    Informe a senha para acessar o painel com todos os clientes, importações e configurações.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_login1, col_login2, col_login3 = st.columns([1, 1.2, 1])

        with col_login2:
            senha = st.text_input("Senha ADM", type="password")
            entrar = st.button("Entrar no painel ADM")

            if entrar:
                if senha == senha_correta:
                    st.session_state["adm_autenticado"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")

            st.info("No MVP, a senha padrão é admin123. Troque isso no Streamlit Secrets.")

        return

    with st.sidebar:
        st.markdown("### Painel ADM")
        if st.button("Sair do ADM"):
            st.session_state["adm_autenticado"] = False
            st.rerun()

    render_header()
    st.markdown('<div class="section-title">Painel administrativo</div>', unsafe_allow_html=True)

    aba1, aba2, aba3, aba4, aba5 = st.tabs(["Visão geral ADM", "Clientes", "Nova importação semanal", "Gerenciar importações", "Configurações e links"])

    with aba1:
        total_clientes = len(db["clientes"])
        total_importacoes = len(db["importacoes"])
        media_aderencia = sum(i["aderencia"] for i in db["importacoes"]) / len(db["importacoes"]) if db["importacoes"] else 0
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Clientes cadastrados", formatar_num(total_clientes), "Dashboards ativos")
        with c2:
            kpi_card("Importações salvas", formatar_num(total_importacoes), "Histórico por importação")
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
            tabela_clientes = pd.DataFrame([
                {
                    "Cliente": c["nome"],
                    "Slug": c["slug"],
                    "Ativo": "Sim" if c.get("ativo", True) else "Não",
                    "Importações": len(importacoes_cliente(c["id"])),
                    "Criado em": c.get("data_criacao", ""),
                    "Atualizado em": c.get("data_atualizacao", "")
                }
                for c in db["clientes"]
            ])
            st.dataframe(tabela_clientes, use_container_width=True, hide_index=True)

            st.markdown("### Editar cliente")
            nomes_clientes = {c["nome"]: c for c in db["clientes"]}
            cliente_editar_nome = st.selectbox("Selecionar cliente", list(nomes_clientes.keys()), key="cliente_editar_select")
            cliente_editar = nomes_clientes[cliente_editar_nome]

            with st.form("form_editar_cliente"):
                novo_nome = st.text_input("Nome do cliente", value=cliente_editar["nome"])
                ativo = st.checkbox("Cliente ativo", value=cliente_editar.get("ativo", True))
                nova_logo = st.file_uploader("Substituir logo do cliente", type=["png", "jpg", "jpeg"], key=f"logo_edit_{cliente_editar['id']}")
                remover_logo = st.checkbox("Remover logo atual")
                regenerar_token = st.checkbox("Regenerar token/link público")
                salvar_cliente = st.form_submit_button("Salvar alterações do cliente")

                if salvar_cliente:
                    try:
                        logo_base64 = None
                        if remover_logo:
                            logo_base64 = ""
                        elif nova_logo is not None:
                            logo_base64 = arquivo_para_base64(nova_logo)

                        atualizado = atualizar_cliente(
                            cliente_editar["id"],
                            nome=novo_nome,
                            ativo=ativo,
                            logo=logo_base64,
                            regenerar_token=regenerar_token
                        )
                        st.success("Cliente atualizado com sucesso.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar cliente: {e}")

            with st.expander("Link público e dados técnicos"):
                st.write(f"Slug: `{cliente_editar['slug']}`")
                st.write(f"Token: `{cliente_editar['token']}`")
                st.write("Link público do cliente:")
                st.code(gerar_link_cliente(cliente_editar))
                if not db["settings"].get("app_url"):
                    st.warning("Cadastre a URL pública do app na aba Configurações e links para o link ficar correto.")
                if cliente_editar.get("logo"):
                    st.image(cliente_editar["logo"], width=120)

            st.markdown("### Excluir cliente")
            st.warning("Excluir cliente remove também todas as importações, métricas diárias e listas de sem embarque vinculadas a ele.")
            confirmar_nome = st.text_input("Digite o nome exato do cliente para confirmar exclusão", key="confirmar_excluir_cliente")
            if st.button("Excluir cliente definitivamente"):
                if confirmar_nome == cliente_editar["nome"]:
                    excluir_cliente(cliente_editar["id"])
                    st.success("Cliente excluído com sucesso.")
                    st.rerun()
                else:
                    st.error("Nome de confirmação não confere.")

    with aba3:
        if not db["clientes"]:
            st.info("Cadastre um cliente primeiro.")
        else:
            nomes = {c["nome"]: c for c in db["clientes"]}
            cliente_nome = st.selectbox("Cliente", list(nomes.keys()))
            cliente = nomes[cliente_nome]

            st.markdown(
                """
                <div class="info-box">
                    O período da importação será identificado automaticamente pelo relatório de embarque.
                    O sistema usa a menor e a maior data encontradas na coluna DATA/HORA do arquivo.
                </div>
                """,
                unsafe_allow_html=True
            )

            rel_embarque = st.file_uploader("Relatório de embarque", type=["xlsx", "xls"], key="rel_embarque_admin")
            base_colab = st.file_uploader("Arquivo de colaboradores cadastrados", type=["xlsx", "xls"], key="base_colab_admin")

            semana_inicio = None
            semana_fim = None
            qtd_registros_relatorio = 0

            if rel_embarque is not None:
                try:
                    semana_inicio, semana_fim, qtd_registros_relatorio = identificar_periodo_relatorio(rel_embarque, cliente["nome"])
                    if semana_inicio is not None and semana_fim is not None:
                        st.success(
                            f"Período identificado automaticamente: "
                            f"{semana_inicio.strftime('%d/%m/%Y')} até {semana_fim.strftime('%d/%m/%Y')} "
                            f"({qtd_registros_relatorio} registros no relatório)."
                        )
                    else:
                        st.warning("Não foi possível identificar datas válidas no relatório de embarque.")
                except Exception as e:
                    st.error(f"Erro ao identificar período do relatório: {e}")

            embarques_por_dia = st.number_input(
                "Embarques esperados por colaborador/dia",
                min_value=1,
                max_value=10,
                value=2,
                step=1
            )

            preset = st.selectbox(
                "Dias que a operação roda",
                ["Segunda a sexta", "Segunda a sábado", "Segunda a domingo", "Personalizado"],
                index=2
            )

            if preset == "Segunda a sexta":
                dias_semana = [0, 1, 2, 3, 4]
            elif preset == "Segunda a sábado":
                dias_semana = [0, 1, 2, 3, 4, 5]
            elif preset == "Segunda a domingo":
                dias_semana = [0, 1, 2, 3, 4, 5, 6]
            else:
                mapa = {
                    "Segunda": 0,
                    "Terça": 1,
                    "Quarta": 2,
                    "Quinta": 3,
                    "Sexta": 4,
                    "Sábado": 5,
                    "Domingo": 6,
                }
                escolhidos = st.multiselect("Selecione os dias", list(mapa.keys()), default=list(mapa.keys()))
                dias_semana = [mapa[d] for d in escolhidos]

            importacao_existente = None
            if semana_inicio is not None and semana_fim is not None:
                importacao_existente = encontrar_importacao_semana(cliente["id"], semana_inicio, semana_fim)

            if importacao_existente:
                st.warning("Já existe uma importação salva para este cliente e para o mesmo período identificado no relatório.")
                substituir = st.checkbox("Substituir importação existente deste período", value=False)
            else:
                substituir = False

            if st.button("Processar e salvar período do relatório"):
                if rel_embarque is None or base_colab is None:
                    st.error("Envie os dois arquivos.")
                elif semana_inicio is None or semana_fim is None:
                    st.error("Não foi possível identificar o período do relatório de embarque.")
                elif importacao_existente and not substituir:
                    st.error("Marque a opção de substituição ou altere o arquivo.")
                else:
                    try:
                        if importacao_existente and substituir:
                            remover_importacao(importacao_existente["id"])

                        registro = salvar_importacao(
                            cliente,
                            semana_inicio,
                            semana_fim,
                            dias_semana,
                            embarques_por_dia,
                            rel_embarque,
                            base_colab
                        )
                        st.success("Período salvo com sucesso.")
                        st.json({
                            "Cliente": registro["cliente_nome"],
                            "Período": f"{registro['semana_inicio']} até {registro['semana_fim']}",
                            "Aderência": formatar_pct(registro["aderencia"]),
                            "Esperado": registro["total_esperado"],
                            "Realizado": registro["total_realizado"],
                            "Sem embarque": registro["colaboradores_sem_embarque"]
                        })
                    except Exception as e:
                        st.error(f"Erro ao processar: {e}")

    with aba4:
        st.subheader("Gerenciar importações salvas")

        if not db["importacoes"]:
            st.info("Nenhuma importação salva ainda.")
        else:
            clientes_map = {c["nome"]: c for c in db["clientes"]}
            cliente_ger = st.selectbox("Cliente para gerenciar", list(clientes_map.keys()), key="cliente_gerenciar")
            cliente_sel = clientes_map[cliente_ger]
            importacoes = importacoes_cliente(cliente_sel["id"])

            if not importacoes:
                st.info("Este cliente ainda não possui importações.")
            else:
                tabela_imp = pd.DataFrame(importacoes)
                tabela_exibir = tabela_imp[[
                    "id", "semana_inicio", "semana_fim", "data_importacao",
                    "total_esperado", "total_realizado", "aderencia", "colaboradores_sem_embarque"
                ]].rename(columns={
                    "id": "ID",
                    "semana_inicio": "Semana início",
                    "semana_fim": "Semana fim",
                    "data_importacao": "Importado em",
                    "total_esperado": "Esperado",
                    "total_realizado": "Realizado",
                    "aderencia": "Aderência (%)",
                    "colaboradores_sem_embarque": "Sem embarque"
                })
                st.dataframe(tabela_exibir, use_container_width=True, hide_index=True)

                opcoes = {
                    f"{i['semana_inicio']} até {i['semana_fim']} | {formatar_pct(i['aderencia'])} | ID {i['id']}": i
                    for i in importacoes
                }
                escolha = st.selectbox("Selecionar importação", list(opcoes.keys()))
                imp = opcoes[escolha]

                col_del1, col_del2 = st.columns([1, 2])
                with col_del1:
                    confirmar = st.checkbox("Confirmar exclusão desta importação")
                with col_del2:
                    if st.button("Excluir importação selecionada"):
                        if confirmar:
                            remover_importacao(imp["id"])
                            st.success("Importação excluída.")
                            st.rerun()
                        else:
                            st.error("Marque a confirmação antes de excluir.")

                st.markdown("### Ajuste manual da importação")
                st.caption("Use apenas para corrigir pequenas informações de histórico. Para recalcular de verdade, reimporte a semana.")
                with st.form("form_ajuste_importacao"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        novo_esperado = st.number_input("Total esperado", min_value=0, value=int(imp.get("total_esperado", 0)), step=1)
                        novo_realizado = st.number_input("Total realizado", min_value=0, value=int(imp.get("total_realizado", 0)), step=1)
                    with col_b:
                        novos_colab = st.number_input("Colaboradores cadastrados", min_value=0, value=int(imp.get("colaboradores_cadastrados", 0)), step=1)
                        novo_sem = st.number_input("Colaboradores sem embarque", min_value=0, value=int(imp.get("colaboradores_sem_embarque", 0)), step=1)
                    with col_c:
                        novos_dias = st.number_input("Dias de operação", min_value=0, value=int(imp.get("dias_operacao", 0)), step=1)
                        novo_emb_por_dia = st.number_input("Embarques por colaborador/dia", min_value=1, value=int(imp.get("embarques_por_colaborador_dia", 2)), step=1)

                    nova_aderencia = (novo_realizado / novo_esperado * 100) if novo_esperado else 0
                    st.info(f"Nova aderência calculada: {formatar_pct(nova_aderencia)}")

                    salvar_ajuste = st.form_submit_button("Salvar ajuste manual")
                    if salvar_ajuste:
                        atualizar_importacao_manual(imp["id"], {
                            "total_esperado": int(novo_esperado),
                            "total_realizado": int(novo_realizado),
                            "colaboradores_cadastrados": int(novos_colab),
                            "colaboradores_sem_embarque": int(novo_sem),
                            "dias_operacao": int(novos_dias),
                            "embarques_por_colaborador_dia": int(novo_emb_por_dia),
                            "aderencia": float(nova_aderencia),
                            "faltas_estimadas": int(max(novo_esperado - novo_realizado, 0))
                        })
                        st.success("Importação ajustada.")
                        st.rerun()

        st.markdown(
            """
            <div class="info-box">
                Para corrigir uma semana com arquivo errado, você pode excluir a importação aqui 
                ou reprocessar a mesma semana na aba Nova importação semanal marcando a opção de substituição.
            </div>
            """,
            unsafe_allow_html=True
        )

    with aba5:
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

        st.subheader("Backup e manutenção")
        backup_json = json.dumps(db, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            "Baixar backup do banco JSON",
            data=backup_json,
            file_name="backup_dashboard_aderencia.json",
            mime="application/json"
        )

        st.warning("Área perigosa: limpar banco apaga clientes, importações, métricas e listas de sem embarque.")
        confirmar_limpeza = st.text_input("Digite LIMPAR para confirmar limpeza total", key="confirmar_limpeza_total")
        if st.button("Limpar banco total"):
            if confirmar_limpeza == "LIMPAR":
                limpar_banco_total()
                st.success("Banco limpo com sucesso.")
                st.rerun()
            else:
                st.error("Confirmação inválida.")

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