import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="Dashboard de Aderência de Embarque",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Dashboard de Aderência de Embarque")
st.caption("Upload de Excel • QR Code / Crachá • Fretamento corporativo")

# -----------------------------
# Funções auxiliares
# -----------------------------
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
    cols = list(df.columns)
    for opcao in opcoes:
        for col in cols:
            if opcao in col:
                return col
    return None

def preparar_dados(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = limpar_colunas(df)

    mapa = {
        "tipo": achar_coluna(df, ["TIPO", "MEIO", "FORMA"]),
        "passageiro": achar_coluna(df, ["PASSAGEIRO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO", "NOME"]),
        "linha": achar_coluna(df, ["LINHA", "ROTA", "CLIENTE"]),
        "prefixo": achar_coluna(df, ["PREFIXO", "VEICULO", "VEÍCULO", "CARRO"]),
        "data_hora": achar_coluna(df, ["DATA/HORA", "DATA HORA", "DATA", "HORARIO", "HORÁRIO"]),
        "latitude": achar_coluna(df, ["LATITUDE"]),
        "longitude": achar_coluna(df, ["LONGITUDE"]),
        "esperado": achar_coluna(df, ["ESPERADO", "PREVISTO", "PROGRAMADO"])
    }

    if mapa["data_hora"] is None:
        raise ValueError("Não encontrei uma coluna de data/hora. O Excel precisa ter DATA/HORA, DATA ou DATA HORA.")

    df["DATA_HORA_TRATADA"] = pd.to_datetime(df[mapa["data_hora"]], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["DATA_HORA_TRATADA"]).copy()
    df["DATA"] = df["DATA_HORA_TRATADA"].dt.date
    df["HORA"] = df["DATA_HORA_TRATADA"].dt.time
    df["MES"] = df["DATA_HORA_TRATADA"].dt.to_period("M").astype(str)
    df["DIA_SEMANA"] = df["DATA_HORA_TRATADA"].dt.day_name(locale=None)

    if mapa["passageiro"]:
        df["PASSAGEIRO_TRATADO"] = df[mapa["passageiro"]].astype(str).str.strip()
    else:
        df["PASSAGEIRO_TRATADO"] = "Não informado"

    if mapa["linha"]:
        df["LINHA_TRATADA"] = df[mapa["linha"]].astype(str).str.strip()
    else:
        df["LINHA_TRATADA"] = "Não informado"

    if mapa["tipo"]:
        df["TIPO_TRATADO"] = df[mapa["tipo"]].astype(str).str.strip()
    else:
        df["TIPO_TRATADO"] = "Não informado"

    if mapa["prefixo"]:
        df["PREFIXO_TRATADO"] = df[mapa["prefixo"]].astype(str).str.strip()
    else:
        df["PREFIXO_TRATADO"] = "Não informado"

    return df, mapa

def formatar_pct(valor: float) -> str:
    if pd.isna(valor):
        return "0,00%"
    return f"{valor:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_num(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")

# -----------------------------
# Upload
# -----------------------------
with st.sidebar:
    st.header("📁 Arquivo")
    arquivo = st.file_uploader("Envie o Excel de embarque", type=["xlsx", "xls"])

    st.divider()
    st.header("⚙️ Regra do esperado")
    modo_esperado = st.radio(
        "Como calcular o total esperado?",
        [
            "Informar total esperado manualmente",
            "Colaboradores únicos × dias com registro",
            "Colaboradores únicos × dias úteis do período",
            "Usar coluna ESPERADO/PREVISTO se existir"
        ],
        index=0
    )

if arquivo is None:
    st.info("Envie um arquivo Excel para gerar o dashboard.")
    st.markdown(
        """
        **Modelo esperado de colunas:**  
        `TIPO`, `PASSAGEIRO`, `LINHA`, `PREFIXO`, `DATA/HORA`, `LATITUDE`, `LONGITUDE`.

        No Excel enviado como referência, o app identifica:
        - `TIPO` como meio de embarque;
        - `PASSAGEIRO` como colaborador;
        - `LINHA` como cliente/rota;
        - `DATA/HORA` como data de embarque.
        """
    )
    st.stop()

try:
    bruto = pd.read_excel(arquivo)
    df, mapa = preparar_dados(bruto)
except Exception as e:
    st.error(f"Erro ao ler o Excel: {e}")
    st.stop()

# -----------------------------
# Filtros
# -----------------------------
with st.sidebar:
    st.divider()
    st.header("🔎 Filtros")

    linhas = sorted(df["LINHA_TRATADA"].dropna().unique().tolist())
    tipos = sorted(df["TIPO_TRATADO"].dropna().unique().tolist())
    prefixos = sorted(df["PREFIXO_TRATADO"].dropna().unique().tolist())

    filtro_linhas = st.multiselect("Cliente / Linha / Rota", linhas, default=linhas)
    filtro_tipos = st.multiselect("Tipo de embarque", tipos, default=tipos)
    filtro_prefixos = st.multiselect("Prefixo", prefixos, default=prefixos)

    data_min = df["DATA_HORA_TRATADA"].dt.date.min()
    data_max = df["DATA_HORA_TRATADA"].dt.date.max()

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

dados = df[
    (df["LINHA_TRATADA"].isin(filtro_linhas)) &
    (df["TIPO_TRATADO"].isin(filtro_tipos)) &
    (df["PREFIXO_TRATADO"].isin(filtro_prefixos)) &
    (df["DATA"] >= inicio) &
    (df["DATA"] <= fim)
].copy()

# -----------------------------
# Cálculo do esperado
# -----------------------------
total_embarcado = len(dados)
colaboradores_unicos = dados["PASSAGEIRO_TRATADO"].nunique()
dias_com_registro = dados["DATA"].nunique()

dias_uteis = 0
if inicio and fim:
    dias_uteis = len(pd.bdate_range(pd.to_datetime(inicio), pd.to_datetime(fim)))

if modo_esperado == "Informar total esperado manualmente":
    total_esperado = st.sidebar.number_input(
        "Total esperado no período filtrado",
        min_value=0,
        value=max(total_embarcado, 1),
        step=1
    )
elif modo_esperado == "Colaboradores únicos × dias com registro":
    total_esperado = colaboradores_unicos * dias_com_registro
elif modo_esperado == "Colaboradores únicos × dias úteis do período":
    total_esperado = colaboradores_unicos * dias_uteis
else:
    col_esperado = mapa.get("esperado")
    if col_esperado and col_esperado in dados.columns:
        total_esperado = pd.to_numeric(dados[col_esperado], errors="coerce").fillna(0).sum()
    else:
        st.sidebar.warning("Não encontrei coluna de esperado/previsão. Use outro modo.")
        total_esperado = max(total_embarcado, 1)

aderencia = (total_embarcado / total_esperado * 100) if total_esperado else 0

# -----------------------------
# KPIs
# -----------------------------
st.subheader("📌 Indicadores principais")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total esperado", formatar_num(total_esperado))
kpi2.metric("Total embarcado", formatar_num(total_embarcado))
kpi3.metric("% aderência", formatar_pct(aderencia))
kpi4.metric("Colaboradores únicos", formatar_num(colaboradores_unicos))
kpi5.metric("Dias analisados", formatar_num(dias_com_registro))

if modo_esperado != "Usar coluna ESPERADO/PREVISTO se existir":
    st.warning(
        "Atenção: o Excel atual contém registros de embarques realizados. "
        "O total esperado está sendo calculado por regra estimada ou informado manualmente."
    )

# -----------------------------
# Gráficos
# -----------------------------
st.subheader("📈 Evolução dos embarques")

if dados.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

por_dia = (
    dados.groupby("DATA")
    .size()
    .reset_index(name="EMBARQUES")
    .sort_values("DATA")
)

fig_dia = px.line(
    por_dia,
    x="DATA",
    y="EMBARQUES",
    markers=True,
    title="Embarques por dia"
)
st.plotly_chart(fig_dia, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    por_tipo = (
        dados.groupby("TIPO_TRATADO")
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL", ascending=False)
    )
    fig_tipo = px.bar(
        por_tipo,
        x="TIPO_TRATADO",
        y="TOTAL",
        title="Embarques por tipo"
    )
    st.plotly_chart(fig_tipo, use_container_width=True)

with col2:
    por_prefixo = (
        dados.groupby("PREFIXO_TRATADO")
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL", ascending=False)
        .head(15)
    )
    fig_prefixo = px.bar(
        por_prefixo,
        x="PREFIXO_TRATADO",
        y="TOTAL",
        title="Top 15 prefixos"
    )
    st.plotly_chart(fig_prefixo, use_container_width=True)

st.subheader("👥 Ranking de colaboradores por embarques")
ranking = (
    dados.groupby("PASSAGEIRO_TRATADO")
    .size()
    .reset_index(name="EMBARQUES")
    .sort_values("EMBARQUES", ascending=False)
)
st.dataframe(ranking, use_container_width=True, hide_index=True)

st.subheader("🧾 Prévia dos dados filtrados")
st.dataframe(dados, use_container_width=True, hide_index=True)

# -----------------------------
# Download
# -----------------------------
csv = dados.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇️ Baixar dados filtrados em CSV",
    data=csv,
    file_name="dados_filtrados_aderencia.csv",
    mime="text/csv"
)