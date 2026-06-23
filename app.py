import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import unicodedata
from datetime import datetime

st.set_page_config(
    page_title="Dashboard de Aderência de Embarque",
    layout="wide"
)

# ============================================================
# TEMA
# ============================================================
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

        section[data-testid="stSidebar"] * {{
            color: {TEXT};
        }}

        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1320px;
        }}

        h1, h2, h3 {{
            color: {TEXT};
            letter-spacing: -0.03em;
        }}

        .hero {{
            background: radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 40%),
                        linear-gradient(135deg, rgba(21, 31, 50, 0.98), rgba(17, 24, 39, 0.98));
            border: 1px solid {BORDER};
            border-radius: 26px;
            padding: 34px 38px;
            margin-bottom: 28px;
            box-shadow: 0 22px 60px rgba(0,0,0,0.28);
        }}

        .hero-title {{
            font-size: 42px;
            line-height: 1.06;
            font-weight: 850;
            color: {TEXT};
            margin-bottom: 12px;
        }}

        .hero-subtitle {{
            color: {MUTED};
            font-size: 16px;
            max-width: 850px;
        }}

        .section-title {{
            font-size: 24px;
            font-weight: 800;
            color: {TEXT};
            margin: 30px 0 16px 0;
        }}

        .kpi-card {{
            background: linear-gradient(180deg, rgba(21, 31, 50, 0.98), rgba(17, 24, 39, 0.98));
            border: 1px solid {BORDER};
            border-radius: 20px;
            padding: 20px 16px;
            min-height: 142px;
            box-shadow: 0 16px 42px rgba(0,0,0,0.22);
            overflow: hidden;
        }}

        .kpi-label {{
            color: {MUTED};
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 14px;
            min-height: 34px;
        }}

        .kpi-value {{
            color: {WHITE};
            font-size: clamp(23px, 1.9vw, 32px);
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
            margin: 18px 0 10px 0;
        }}

        .warning-box {{
            background: rgba(113, 63, 18, 0.35);
            border: 1px solid rgba(251, 191, 36, 0.35);
            border-radius: 18px;
            padding: 16px 18px;
            color: {LIGHT_GRAY};
            margin: 18px 0 10px 0;
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

        .stTabs [aria-selected="true"] {{
            background: {BLUE_DARK};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FUNÇÕES
# ============================================================
def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = " ".join(texto.split())
    return texto

def formatar_num(valor) -> str:
    try:
        return f"{float(valor):,.0f}".replace(",", ".")
    except Exception:
        return "0"

def formatar_pct(valor) -> str:
    try:
        return f"{float(valor):,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00%"

def limpar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.replace("\n", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )
    return df

def achar_coluna(df: pd.DataFrame, opcoes: list[str]):
    for opcao in opcoes:
        for col in df.columns:
            if opcao in col:
                return col
    return None

def preparar_embarques(df: pd.DataFrame, cliente_upload: str):
    df = limpar_colunas(df)

    mapa = {
        "cliente": achar_coluna(df, ["CLIENTE"]),
        "tipo": achar_coluna(df, ["TIPO", "MEIO", "FORMA"]),
        "passageiro": achar_coluna(df, ["PASSAGEIRO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO", "NOME"]),
        "linha": achar_coluna(df, ["LINHA", "ROTA"]),
        "prefixo": achar_coluna(df, ["PREFIXO", "VEICULO", "VEÍCULO", "CARRO"]),
        "data_hora": achar_coluna(df, ["DATA/HORA", "DATA HORA", "DATA", "HORARIO", "HORÁRIO"]),
        "latitude": achar_coluna(df, ["LATITUDE"]),
        "longitude": achar_coluna(df, ["LONGITUDE"]),
    }

    if mapa["data_hora"] is None:
        raise ValueError("Não encontrei coluna de data/hora no Excel de embarques.")
    if mapa["passageiro"] is None:
        raise ValueError("Não encontrei coluna de passageiro/colaborador no Excel de embarques.")

    df["DATA_HORA_TRATADA"] = pd.to_datetime(df[mapa["data_hora"]], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["DATA_HORA_TRATADA"]).copy()

    df["DATA"] = df["DATA_HORA_TRATADA"].dt.date
    df["MES"] = df["DATA_HORA_TRATADA"].dt.to_period("M").astype(str)

    if mapa["cliente"]:
        df["CLIENTE_TRATADO"] = df[mapa["cliente"]].astype(str).str.strip().str.upper()
    else:
        df["CLIENTE_TRATADO"] = cliente_upload.strip().upper() if cliente_upload else "CLIENTE NÃO INFORMADO"

    df["PASSAGEIRO_TRATADO"] = df[mapa["passageiro"]].astype(str).str.strip()
    df["PASSAGEIRO_KEY"] = df["PASSAGEIRO_TRATADO"].apply(normalizar_texto)

    if mapa["linha"]:
        df["LINHA_TRATADA"] = df[mapa["linha"]].astype(str).str.strip().str.upper()
    else:
        df["LINHA_TRATADA"] = "NÃO INFORMADO"

    if mapa["tipo"]:
        df["TIPO_TRATADO"] = df[mapa["tipo"]].astype(str).str.strip().str.upper()
    else:
        df["TIPO_TRATADO"] = "NÃO INFORMADO"

    if mapa["prefixo"]:
        df["PREFIXO_TRATADO"] = df[mapa["prefixo"]].astype(str).str.strip()
    else:
        df["PREFIXO_TRATADO"] = "NÃO INFORMADO"

    return df, mapa

def preparar_base_colaboradores(df: pd.DataFrame, cliente_upload: str):
    df = limpar_colunas(df)

    mapa = {
        "cliente": achar_coluna(df, ["CLIENTE"]),
        "nome": achar_coluna(df, ["NOME", "PASSAGEIRO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO"]),
        "linha": achar_coluna(df, ["LINHA", "ROTA"]),
        "turno": achar_coluna(df, ["TURNO"]),
        "cadastro": achar_coluna(df, ["CADASTRO", "DATA CADASTRO", "DT CADASTRO"]),
        "acesso_app": achar_coluna(df, ["ACESSO APP", "APP"]),
        "rfid": achar_coluna(df, ["RFID", "CARTAO", "CARTÃO", "CRACHA", "CRACHÁ"])
    }

    if mapa["nome"] is None:
        raise ValueError("Não encontrei coluna NOME/PASSAGEIRO/COLABORADOR na base de colaboradores.")

    df["NOME_TRATADO"] = df[mapa["nome"]].astype(str).str.strip()
    df["NOME_KEY"] = df["NOME_TRATADO"].apply(normalizar_texto)

    if mapa["cliente"]:
        df["CLIENTE_TRATADO"] = df[mapa["cliente"]].astype(str).str.strip().str.upper()
    else:
        df["CLIENTE_TRATADO"] = cliente_upload.strip().upper() if cliente_upload else "CLIENTE NÃO INFORMADO"

    if mapa["linha"]:
        df["LINHA_TRATADA"] = df[mapa["linha"]].astype(str).str.strip().str.upper()
    else:
        df["LINHA_TRATADA"] = "NÃO INFORMADO"

    if mapa["turno"]:
        df["TURNO_TRATADO"] = df[mapa["turno"]].astype(str).str.strip().str.upper()
    else:
        df["TURNO_TRATADO"] = "NÃO INFORMADO"

    if mapa["cadastro"]:
        df["DATA_CADASTRO"] = pd.to_datetime(df[mapa["cadastro"]], dayfirst=True, errors="coerce")
    else:
        df["DATA_CADASTRO"] = pd.NaT

    df = df[df["NOME_KEY"] != ""].copy()
    df = df.drop_duplicates(subset=["NOME_KEY"]).copy()

    return df, mapa

def datas_consideradas(inicio, fim, dados_embarque, modo):
    if modo == "Dias com registro de embarque":
        datas = sorted(dados_embarque["DATA"].dropna().unique().tolist())
        return [d for d in datas if d >= inicio and d <= fim]
    if modo == "Dias úteis do período":
        return [d.date() for d in pd.bdate_range(pd.to_datetime(inicio), pd.to_datetime(fim))]
    return [d.date() for d in pd.date_range(pd.to_datetime(inicio), pd.to_datetime(fim))]

def datas_operacao(inicio, fim, dias_semana_selecionados):
    todas = pd.date_range(pd.to_datetime(inicio), pd.to_datetime(fim), freq="D")
    return [d.date() for d in todas if d.weekday() in dias_semana_selecionados]

def calcular_esperado_por_dia(base_colab, datas, embarques_por_colaborador_dia, considerar_data_cadastro=True):
    linhas = []
    for data in datas:
        if considerar_data_cadastro and "DATA_CADASTRO" in base_colab.columns and base_colab["DATA_CADASTRO"].notna().any():
            elegiveis = base_colab[
                (base_colab["DATA_CADASTRO"].isna()) |
                (base_colab["DATA_CADASTRO"].dt.date <= data)
            ]
        else:
            elegiveis = base_colab

        cadastrados = elegiveis["NOME_KEY"].nunique()
        esperado = cadastrados * embarques_por_colaborador_dia

        linhas.append({
            "DATA": data,
            "COLABORADORES_CADASTRADOS": cadastrados,
            "ESPERADO": esperado
        })

    return pd.DataFrame(linhas)

def aplicar_layout(fig, titulo=None):
    fig.update_layout(
        title=dict(
            text=titulo or "",
            font=dict(size=18, color=TEXT, family="Arial"),
            x=0.02,
            y=0.95
        ),
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

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### Arquivos")
    cliente_upload = st.text_input("Cliente desta importação", value="CAIEIRAS")

    arquivo_embarques = st.file_uploader(
        "Relatório de embarque",
        type=["xlsx", "xls"],
        key="embarques",
        help="Arquivo com os embarques realizados via QR Code ou crachá."
    )

    arquivo_colaboradores = st.file_uploader(
        "Arquivo de colaboradores cadastrados",
        type=["xlsx", "xls"],
        key="colaboradores",
        help="Base com todos os colaboradores cadastrados/ativos."
    )

    st.divider()

    st.markdown("### Regra da operação")
    embarques_por_colaborador_dia = st.number_input(
        "Embarques esperados por colaborador/dia",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )

    preset_operacao = st.selectbox(
        "Dias que a operação roda",
        [
            "Segunda a sexta",
            "Segunda a sábado",
            "Segunda a domingo",
            "Personalizado"
        ],
        index=2
    )

    if preset_operacao == "Segunda a sexta":
        dias_semana_selecionados = [0, 1, 2, 3, 4]
    elif preset_operacao == "Segunda a sábado":
        dias_semana_selecionados = [0, 1, 2, 3, 4, 5]
    elif preset_operacao == "Segunda a domingo":
        dias_semana_selecionados = [0, 1, 2, 3, 4, 5, 6]
    else:
        mapa_dias = {
            "Segunda": 0,
            "Terça": 1,
            "Quarta": 2,
            "Quinta": 3,
            "Sexta": 4,
            "Sábado": 5,
            "Domingo": 6,
        }
        dias_escolhidos = st.multiselect(
            "Selecione os dias",
            list(mapa_dias.keys()),
            default=list(mapa_dias.keys())
        )
        dias_semana_selecionados = [mapa_dias[d] for d in dias_escolhidos]

    considerar_data_cadastro = st.checkbox(
        "Considerar data de cadastro do colaborador",
        value=True
    )

# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Dashboard de Aderência de Embarque</div>
        <div class="hero-subtitle">
            Controle de aderência com base em embarques realizados e colaboradores cadastrados.
            A regra padrão considera dois embarques esperados por colaborador a cada dia analisado.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if arquivo_embarques is None or arquivo_colaboradores is None:
    st.markdown(
        """
        <div class="info-box">
            Para calcular a aderência corretamente, envie os dois arquivos:
            <br><strong>1.</strong> Relatório de embarque
            <br><strong>2.</strong> Arquivo de colaboradores cadastrados
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Relatório", "Embarque", "Realizado")
    with c2:
        kpi_card("Base", "Colaboradores", "Cadastrados")
    with c3:
        kpi_card("Regra padrão", "2 por dia", "Por colaborador")
    st.stop()

# ============================================================
# LEITURA
# ============================================================
try:
    embarques_bruto = pd.read_excel(arquivo_embarques)
    colaboradores_bruto = pd.read_excel(arquivo_colaboradores)

    embarques, mapa_emb = preparar_embarques(embarques_bruto, cliente_upload)
    colaboradores, mapa_colab = preparar_base_colaboradores(colaboradores_bruto, cliente_upload)

except Exception as e:
    st.error(f"Erro ao ler arquivos: {e}")
    st.stop()

# ============================================================
# FILTROS
# ============================================================
with st.sidebar:
    st.divider()
    st.markdown("### Filtros")

    clientes = sorted(set(embarques["CLIENTE_TRATADO"].dropna().unique().tolist()) | set(colaboradores["CLIENTE_TRATADO"].dropna().unique().tolist()))
    linhas = sorted(set(embarques["LINHA_TRATADA"].dropna().unique().tolist()) | set(colaboradores["LINHA_TRATADA"].dropna().unique().tolist()))
    tipos = sorted(embarques["TIPO_TRATADO"].dropna().unique().tolist())
    prefixos = sorted(embarques["PREFIXO_TRATADO"].dropna().unique().tolist())
    turnos = sorted(colaboradores["TURNO_TRATADO"].dropna().unique().tolist())

    filtro_clientes = st.multiselect("Cliente", clientes, default=clientes)
    filtro_linhas = st.multiselect("Linha / Rota", linhas, default=linhas)
    filtro_turnos = st.multiselect("Turno", turnos, default=turnos)
    filtro_tipos = st.multiselect("Tipo de embarque", tipos, default=tipos)
    filtro_prefixos = st.multiselect("Prefixo", prefixos, default=prefixos)

    data_min = embarques["DATA"].min()
    data_max = embarques["DATA"].max()

    periodo = st.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max
    )

if isinstance(periodo, tuple) and len(periodo) == 2:
    inicio, fim = periodo
else:
    inicio, fim = data_min, data_max

embarques_filtrados = embarques[
    (embarques["CLIENTE_TRATADO"].isin(filtro_clientes)) &
    (embarques["LINHA_TRATADA"].isin(filtro_linhas)) &
    (embarques["TIPO_TRATADO"].isin(filtro_tipos)) &
    (embarques["PREFIXO_TRATADO"].isin(filtro_prefixos)) &
    (embarques["DATA"] >= inicio) &
    (embarques["DATA"] <= fim)
].copy()

colaboradores_filtrados = colaboradores[
    (colaboradores["CLIENTE_TRATADO"].isin(filtro_clientes)) &
    (colaboradores["LINHA_TRATADA"].isin(filtro_linhas)) &
    (colaboradores["TURNO_TRATADO"].isin(filtro_turnos))
].copy()

if embarques_filtrados.empty:
    st.warning("Nenhum embarque encontrado para os filtros selecionados.")
    st.stop()

if colaboradores_filtrados.empty:
    st.warning("Nenhum colaborador cadastrado encontrado para os filtros selecionados.")
    st.stop()

# ============================================================
# CÁLCULO CORRETO
# ============================================================
datas = datas_operacao(inicio, fim, dias_semana_selecionados)
if not datas:
    st.warning("Nenhum dia de operação foi selecionado para o período analisado.")
    st.stop()
esperado_dia = calcular_esperado_por_dia(
    colaboradores_filtrados,
    datas,
    embarques_por_colaborador_dia,
    considerar_data_cadastro
)

realizado_dia = (
    embarques_filtrados.groupby("DATA")
    .size()
    .reset_index(name="REALIZADO")
)

evolucao = esperado_dia.merge(realizado_dia, on="DATA", how="left")
evolucao["REALIZADO"] = evolucao["REALIZADO"].fillna(0).astype(int)
evolucao["ADERENCIA"] = evolucao.apply(
    lambda row: (row["REALIZADO"] / row["ESPERADO"] * 100) if row["ESPERADO"] else 0,
    axis=1
)
evolucao["FALTAS_ESTIMADAS"] = (evolucao["ESPERADO"] - evolucao["REALIZADO"]).clip(lower=0)

total_colaboradores_cadastrados = colaboradores_filtrados["NOME_KEY"].nunique()
total_colaboradores_que_embarcaram = embarques_filtrados["PASSAGEIRO_KEY"].nunique()
total_esperado = int(evolucao["ESPERADO"].sum())
total_embarcado = int(embarques_filtrados.shape[0])
aderencia = (total_embarcado / total_esperado * 100) if total_esperado else 0
faltas_estimadas = max(total_esperado - total_embarcado, 0)
dias_operacao_qtd = len(datas)

nomes_base = set(colaboradores_filtrados["NOME_KEY"].unique())
nomes_embarcaram = set(embarques_filtrados["PASSAGEIRO_KEY"].unique())

sem_embarque_keys = nomes_base - nomes_embarcaram
fora_da_base_keys = nomes_embarcaram - nomes_base

sem_embarque = colaboradores_filtrados[colaboradores_filtrados["NOME_KEY"].isin(sem_embarque_keys)].copy()
fora_da_base = embarques_filtrados[embarques_filtrados["PASSAGEIRO_KEY"].isin(fora_da_base_keys)].copy()

# ============================================================
# KPIS
# ============================================================
st.markdown('<div class="section-title">Indicadores</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    kpi_card("Colaboradores cadastrados", formatar_num(total_colaboradores_cadastrados), "Base enviada")
with k2:
    kpi_card("Dias de operação", formatar_num(dias_operacao_qtd), preset_operacao)
with k3:
    kpi_card("Esperado", formatar_num(total_esperado), f"{embarques_por_colaborador_dia} embarques por colaborador/dia")
with k4:
    kpi_card("Realizado", formatar_num(total_embarcado), "Relatório de embarque")
with k5:
    kpi_card("Aderência", formatar_pct(aderencia), "Realizado / Esperado")
with k6:
    kpi_card("Faltas estimadas", formatar_num(faltas_estimadas), "Esperado - realizado")

st.markdown(
    f"""
    <div class="info-box">
        <strong>Regra aplicada:</strong> {formatar_num(total_colaboradores_cadastrados)} colaboradores cadastrados × 
        {embarques_por_colaborador_dia} embarques por colaborador/dia × {dias_operacao_qtd} dias de operação.
        <br>
        <strong>Período analisado:</strong> {inicio.strftime('%d/%m/%Y')} até {fim.strftime('%d/%m/%Y')}.
        <br>
        <strong>Dias considerados:</strong> {preset_operacao}.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ABAS
# ============================================================
aba1, aba2 = st.tabs([
    "Visão geral",
    "Colaboradores"
])

with aba1:
    st.markdown('<div class="section-title">Evolução operacional</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=evolucao["DATA"],
            y=evolucao["ESPERADO"],
            mode="lines",
            line=dict(color=LIGHT_GRAY, width=2, dash="dash"),
            name="Esperado"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=evolucao["DATA"],
            y=evolucao["REALIZADO"],
            mode="lines+markers",
            line=dict(color=BLUE, width=3),
            marker=dict(size=6, color=WHITE, line=dict(color=BLUE, width=2)),
            fill="tozeroy",
            fillcolor="rgba(96,165,250,0.10)",
            name="Realizado"
        )
    )
    fig.update_xaxes(title_text="Data")
    fig.update_yaxes(title_text="Quantidade de embarques")
    fig = aplicar_layout(fig, "Esperado x realizado por dia")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        fig_ad = go.Figure()
        fig_ad.add_trace(
            go.Scatter(
                x=evolucao["DATA"],
                y=evolucao["ADERENCIA"],
                mode="lines+markers",
                line=dict(color=BLUE, width=3),
                marker=dict(size=6, color=WHITE, line=dict(color=BLUE, width=2)),
                name="Aderência"
            )
        )
        fig_ad.update_xaxes(title_text="Data")
        fig_ad.update_yaxes(title_text="Aderência (%)")
        fig_ad = aplicar_layout(fig_ad, "Aderência diária")
        st.plotly_chart(fig_ad, use_container_width=True)

    with c2:
        por_turno = (
            colaboradores_filtrados.groupby("TURNO_TRATADO")
            .size()
            .reset_index(name="Colaboradores")
            .rename(columns={"TURNO_TRATADO": "Turno"})
            .sort_values("Colaboradores", ascending=False)
        )
        fig_turno = px.bar(
            por_turno,
            x="Turno",
            y="Colaboradores",
            text="Colaboradores",
            color_discrete_sequence=[BLUE],
            labels={"Turno": "Turno", "Colaboradores": "Colaboradores"}
        )
        fig_turno.update_traces(marker_line_color=WHITE, marker_line_width=0.8, textposition="outside")
        fig_turno = aplicar_layout(fig_turno, "Colaboradores por turno")
        st.plotly_chart(fig_turno, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        por_tipo = (
            embarques_filtrados.groupby("TIPO_TRATADO")
            .size()
            .reset_index(name="Total")
            .rename(columns={"TIPO_TRATADO": "Tipo"})
            .sort_values("Total", ascending=False)
        )
        fig_tipo = px.bar(
            por_tipo,
            x="Tipo",
            y="Total",
            text="Total",
            color_discrete_sequence=[BLUE],
            labels={"Tipo": "Tipo de embarque", "Total": "Total de embarques"}
        )
        fig_tipo.update_traces(marker_line_color=WHITE, marker_line_width=0.8, textposition="outside")
        fig_tipo = aplicar_layout(fig_tipo, "Embarques por tipo")
        st.plotly_chart(fig_tipo, use_container_width=True)

    with c4:
        por_prefixo = (
            embarques_filtrados.groupby("PREFIXO_TRATADO")
            .size()
            .reset_index(name="Total")
            .rename(columns={"PREFIXO_TRATADO": "Prefixo"})
            .sort_values("Total", ascending=False)
            .head(10)
        )
        fig_prefixo = px.bar(
            por_prefixo,
            x="Prefixo",
            y="Total",
            text="Total",
            color_discrete_sequence=[BLUE],
            labels={"Prefixo": "Prefixo", "Total": "Total de embarques"}
        )
        fig_prefixo.update_traces(marker_line_color=WHITE, marker_line_width=0.8, textposition="outside")
        fig_prefixo.update_xaxes(type="category")
        fig_prefixo = aplicar_layout(fig_prefixo, "Top 10 prefixos por embarque")
        st.plotly_chart(fig_prefixo, use_container_width=True)

with aba2:
    st.markdown('<div class="section-title">Colaboradores</div>', unsafe_allow_html=True)

    ranking = (
        embarques_filtrados.groupby(["PASSAGEIRO_TRATADO", "PASSAGEIRO_KEY"])
        .size()
        .reset_index(name="Embarques realizados")
        .rename(columns={"PASSAGEIRO_TRATADO": "Colaborador"})
        .sort_values("Embarques realizados", ascending=False)
    )

    ranking["Está na base"] = ranking["PASSAGEIRO_KEY"].isin(nomes_base).map({True: "Sim", False: "Não"})

    st.subheader("Ranking de colaboradores por embarques")
    st.dataframe(
        ranking[["Colaborador", "Embarques realizados", "Está na base"]],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Colaboradores cadastrados que nunca fizeram embarque no período")
    if sem_embarque.empty:
        st.success("Todos os colaboradores cadastrados tiveram pelo menos um embarque no período analisado.")
    else:
        cols = ["NOME_TRATADO", "LINHA_TRATADA", "TURNO_TRATADO", "DATA_CADASTRO"]
        tabela_sem = sem_embarque[cols].rename(columns={
            "NOME_TRATADO": "Colaborador",
            "LINHA_TRATADA": "Linha",
            "TURNO_TRATADO": "Turno",
            "DATA_CADASTRO": "Data de cadastro"
        })
        st.dataframe(tabela_sem, use_container_width=True, hide_index=True)

    csv_sem = sem_embarque.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar colaboradores sem embarque em CSV",
        data=csv_sem,
        file_name="colaboradores_sem_embarque.csv",
        mime="text/csv"
    )
