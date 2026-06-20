import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Dashboard de Aderência de Embarque", layout="wide")

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

st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(135deg, {PRIMARY_BG} 0%, #0F172A 45%, #111827 100%); color: {TEXT}; }}
section[data-testid="stSidebar"] {{ background: {SECONDARY_BG}; border-right: 1px solid {BORDER}; }}
section[data-testid="stSidebar"] * {{ color: {TEXT}; }}
.block-container {{ padding-top: 2.3rem; padding-bottom: 3rem; max-width: 1280px; }}
h1, h2, h3 {{ color: {TEXT}; letter-spacing: -0.03em; }}
.hero {{ background: radial-gradient(circle at top left, rgba(96,165,250,.18), transparent 40%), linear-gradient(135deg, rgba(21,31,50,.98), rgba(17,24,39,.98)); border: 1px solid {BORDER}; border-radius: 26px; padding: 34px 38px; margin-bottom: 28px; box-shadow: 0 22px 60px rgba(0,0,0,.28); }}
.hero-title {{ font-size: 44px; line-height: 1.04; font-weight: 800; color: {TEXT}; margin-bottom: 12px; }}
.hero-subtitle {{ color: {MUTED}; font-size: 16px; max-width: 760px; }}
.section-title {{ font-size: 24px; font-weight: 800; color: {TEXT}; margin: 30px 0 16px 0; }}
.kpi-card {{ background: linear-gradient(180deg, rgba(21,31,50,.98), rgba(17,24,39,.98)); border: 1px solid {BORDER}; border-radius: 20px; padding: 22px 20px; min-height: 132px; box-shadow: 0 16px 42px rgba(0,0,0,.22); }}
.kpi-label {{ color: {MUTED}; font-size: 13px; font-weight: 600; margin-bottom: 12px; }}
.kpi-value {{ color: {WHITE}; font-size: 32px; font-weight: 800; letter-spacing: -0.04em; }}
.kpi-caption {{ color: {BLUE}; font-size: 12px; margin-top: 8px; }}
.info-box {{ background: rgba(30,58,95,.38); border: 1px solid rgba(96,165,250,.35); border-radius: 18px; padding: 16px 18px; color: {LIGHT_GRAY}; margin: 18px 0 10px 0; }}
.stButton button, .stDownloadButton button {{ border-radius: 14px; border: 1px solid {BORDER}; background: linear-gradient(135deg, {BLUE_DARK}, #2563EB); color: white; font-weight: 700; }}
.stTabs [data-baseweb="tab"] {{ background: {CARD_BG}; border-radius: 14px; padding: 10px 18px; border: 1px solid {BORDER}; }}
.stTabs [aria-selected="true"] {{ background: {BLUE_DARK}; }}
</style>
""", unsafe_allow_html=True)

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

def limpar_colunas(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.upper().str.replace("\n", " ", regex=False).str.replace("  ", " ", regex=False)
    return df

def achar_coluna(df, opcoes):
    for opcao in opcoes:
        for col in df.columns:
            if opcao in col:
                return col
    return None

def preparar_dados(df, cliente_upload):
    df = limpar_colunas(df)
    mapa = {
        "cliente": achar_coluna(df, ["CLIENTE"]),
        "tipo": achar_coluna(df, ["TIPO", "MEIO", "FORMA"]),
        "passageiro": achar_coluna(df, ["PASSAGEIRO", "COLABORADOR", "FUNCIONARIO", "FUNCIONÁRIO", "NOME"]),
        "linha": achar_coluna(df, ["LINHA", "ROTA"]),
        "prefixo": achar_coluna(df, ["PREFIXO", "VEICULO", "VEÍCULO", "CARRO"]),
        "data_hora": achar_coluna(df, ["DATA/HORA", "DATA HORA", "DATA", "HORARIO", "HORÁRIO"]),
        "esperado": achar_coluna(df, ["ESPERADO", "PREVISTO", "PROGRAMADO"]),
    }
    if mapa["data_hora"] is None:
        raise ValueError("Não encontrei coluna de data/hora. Use DATA/HORA, DATA ou DATA HORA.")
    df["DATA_HORA_TRATADA"] = pd.to_datetime(df[mapa["data_hora"]], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["DATA_HORA_TRATADA"]).copy()
    df["DATA"] = df["DATA_HORA_TRATADA"].dt.date
    df["MES"] = df["DATA_HORA_TRATADA"].dt.to_period("M").astype(str)
    df["CLIENTE_TRATADO"] = df[mapa["cliente"]].astype(str).str.strip() if mapa["cliente"] else (cliente_upload.strip().upper() if cliente_upload else "CLIENTE NÃO INFORMADO")
    df["PASSAGEIRO_TRATADO"] = df[mapa["passageiro"]].astype(str).str.strip() if mapa["passageiro"] else "Não informado"
    df["LINHA_TRATADA"] = df[mapa["linha"]].astype(str).str.strip() if mapa["linha"] else "Não informado"
    df["TIPO_TRATADO"] = df[mapa["tipo"]].astype(str).str.strip() if mapa["tipo"] else "Não informado"
    df["PREFIXO_TRATADO"] = df[mapa["prefixo"]].astype(str).str.strip() if mapa["prefixo"] else "Não informado"
    return df, mapa

def aplicar_layout(fig, titulo=""):
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=18, color=TEXT, family="Arial"), x=0.02, y=0.95),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.55)",
        font=dict(color=LIGHT_GRAY, family="Arial"),
        margin=dict(l=20, r=20, t=70, b=45),
        xaxis=dict(showgrid=False, zeroline=False, color=MUTED, linecolor=BORDER),
        yaxis=dict(showgrid=True, gridcolor="rgba(229,231,235,0.10)", zeroline=False, color=MUTED, linecolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=LIGHT_GRAY)),
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor=BLUE, font=dict(color=WHITE)),
    )
    return fig

def kpi_card(label, value, caption=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)

def salvar_resumo_sessao(cliente, arquivo_nome, dados, total_esperado, total_embarcado, aderencia):
    if "historico_sessao" not in st.session_state:
        st.session_state["historico_sessao"] = pd.DataFrame(columns=["data_importacao", "cliente", "arquivo", "periodo_inicial", "periodo_final", "total_esperado", "total_embarcado", "aderencia"])
    novo = pd.DataFrame([{
        "data_importacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "cliente": cliente,
        "arquivo": arquivo_nome,
        "periodo_inicial": str(dados["DATA"].min()) if not dados.empty else "",
        "periodo_final": str(dados["DATA"].max()) if not dados.empty else "",
        "total_esperado": int(total_esperado),
        "total_embarcado": int(total_embarcado),
        "aderencia": float(aderencia),
    }])
    st.session_state["historico_sessao"] = pd.concat([st.session_state["historico_sessao"], novo], ignore_index=True)

with st.sidebar:
    st.markdown("### Arquivo")
    cliente_upload = st.text_input("Cliente desta importação", value="CAIEIRAS")
    arquivo = st.file_uploader("Envie o Excel de embarque", type=["xlsx", "xls"])
    st.divider()
    st.markdown("### Regra do esperado")
    modo_esperado = st.radio("Como calcular o total esperado?", ["Informar total esperado manualmente", "Colaboradores únicos × dias com registro", "Colaboradores únicos × dias úteis do período", "Usar coluna ESPERADO/PREVISTO se existir"], index=0)

st.markdown("""
<div class="hero">
    <div class="hero-title">Dashboard de Aderência de Embarque</div>
    <div class="hero-subtitle">Análise operacional de embarques por cliente, período, tipo de identificação, linha e prefixo. Estrutura preparada para evolução com histórico de importações e comparação mensal.</div>
</div>
""", unsafe_allow_html=True)

if arquivo is None:
    st.markdown("""
    <div class="info-box">Envie um arquivo Excel para gerar o dashboard. Caso o Excel não tenha coluna CLIENTE, o cliente será definido pelo campo informado na barra lateral.</div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Entrada", "Excel", ".xlsx ou .xls")
    with c2: kpi_card("Separação", "Cliente", "Manual ou por coluna")
    with c3: kpi_card("Histórico", "Sessão", "Base para próxima etapa")
    st.stop()

try:
    bruto = pd.read_excel(arquivo)
    df, mapa = preparar_dados(bruto, cliente_upload)
except Exception as e:
    st.error(f"Erro ao ler o Excel: {e}")
    st.stop()

with st.sidebar:
    st.divider()
    st.markdown("### Filtros")
    clientes = sorted(df["CLIENTE_TRATADO"].dropna().unique().tolist())
    linhas = sorted(df["LINHA_TRATADA"].dropna().unique().tolist())
    tipos = sorted(df["TIPO_TRATADO"].dropna().unique().tolist())
    prefixos = sorted(df["PREFIXO_TRATADO"].dropna().unique().tolist())
    filtro_clientes = st.multiselect("Cliente", clientes, default=clientes)
    filtro_linhas = st.multiselect("Linha / Rota", linhas, default=linhas)
    filtro_tipos = st.multiselect("Tipo de embarque", tipos, default=tipos)
    filtro_prefixos = st.multiselect("Prefixo", prefixos, default=prefixos)
    data_min = df["DATA"].min()
    data_max = df["DATA"].max()
    periodo = st.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)

inicio, fim = periodo if isinstance(periodo, tuple) and len(periodo) == 2 else (data_min, data_max)
dados = df[(df["CLIENTE_TRATADO"].isin(filtro_clientes)) & (df["LINHA_TRATADA"].isin(filtro_linhas)) & (df["TIPO_TRATADO"].isin(filtro_tipos)) & (df["PREFIXO_TRATADO"].isin(filtro_prefixos)) & (df["DATA"] >= inicio) & (df["DATA"] <= fim)].copy()
if dados.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

total_embarcado = len(dados)
colaboradores_unicos = dados["PASSAGEIRO_TRATADO"].nunique()
dias_com_registro = dados["DATA"].nunique()
dias_uteis = len(pd.bdate_range(pd.to_datetime(inicio), pd.to_datetime(fim)))

if modo_esperado == "Informar total esperado manualmente":
    total_esperado = st.sidebar.number_input("Total esperado no período filtrado", min_value=0, value=max(total_embarcado, 1), step=1)
elif modo_esperado == "Colaboradores únicos × dias com registro":
    total_esperado = colaboradores_unicos * dias_com_registro
elif modo_esperado == "Colaboradores únicos × dias úteis do período":
    total_esperado = colaboradores_unicos * dias_uteis
else:
    col_esperado = mapa.get("esperado")
    total_esperado = pd.to_numeric(dados[col_esperado], errors="coerce").fillna(0).sum() if col_esperado and col_esperado in dados.columns else max(total_embarcado, 1)

aderencia = (total_embarcado / total_esperado * 100) if total_esperado else 0
faltas_estimadas = max(total_esperado - total_embarcado, 0)

with st.sidebar:
    st.divider()
    st.markdown("### Histórico")
    if st.button("Salvar resumo desta importação"):
        cliente_salvo = ", ".join(filtro_clientes) if filtro_clientes else cliente_upload
        salvar_resumo_sessao(cliente_salvo, arquivo.name, dados, total_esperado, total_embarcado, aderencia)
        st.success("Resumo salvo nesta sessão.")

st.markdown('<div class="section-title">Indicadores</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
with k1: kpi_card("Total esperado", formatar_num(total_esperado), "Base planejada")
with k2: kpi_card("Total embarcado", formatar_num(total_embarcado), "Registros no Excel")
with k3: kpi_card("Aderência", formatar_pct(aderencia), "Embarcado / Esperado")
with k4: kpi_card("Colaboradores únicos", formatar_num(colaboradores_unicos), "Passageiros distintos")
with k5: kpi_card("Faltas estimadas", formatar_num(faltas_estimadas), "Diferença calculada")

st.markdown("""<div class="info-box">O arquivo atual contém registros de embarques realizados. Para aderência definitiva, use uma base de esperados ou informe manualmente o total planejado do período.</div>""", unsafe_allow_html=True)

aba1, aba2, aba3 = st.tabs(["Visão geral", "Cliente e linhas", "Histórico da sessão"])

with aba1:
    st.markdown('<div class="section-title">Evolução dos embarques</div>', unsafe_allow_html=True)
    por_dia = dados.groupby("DATA").size().reset_index(name="EMBARQUES").sort_values("DATA")
    fig_dia = go.Figure()
    fig_dia.add_trace(go.Scatter(x=por_dia["DATA"], y=por_dia["EMBARQUES"], mode="lines+markers", line=dict(color=BLUE, width=3), marker=dict(size=7, color=WHITE, line=dict(color=BLUE, width=2)), fill="tozeroy", fillcolor="rgba(96,165,250,0.12)", name="Embarques"))
    st.plotly_chart(aplicar_layout(fig_dia, "Embarques por dia"), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        por_tipo = dados.groupby("TIPO_TRATADO").size().reset_index(name="TOTAL").sort_values("TOTAL", ascending=False)
        fig_tipo = px.bar(por_tipo, x="TIPO_TRATADO", y="TOTAL", text="TOTAL", color_discrete_sequence=[BLUE])
        fig_tipo.update_traces(marker_line_color=WHITE, marker_line_width=.8, textposition="outside")
        st.plotly_chart(aplicar_layout(fig_tipo, "Distribuição por tipo"), use_container_width=True)
    with c2:
        por_prefixo = dados.groupby("PREFIXO_TRATADO").size().reset_index(name="TOTAL").sort_values("TOTAL", ascending=False).head(12)
        fig_prefixo = px.bar(por_prefixo, x="TOTAL", y="PREFIXO_TRATADO", orientation="h", text="TOTAL", color_discrete_sequence=[BLUE])
        fig_prefixo.update_traces(marker_line_color=WHITE, marker_line_width=.7, textposition="outside")
        fig_prefixo.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(aplicar_layout(fig_prefixo, "Prefixos com mais embarques"), use_container_width=True)

with aba2:
    st.markdown('<div class="section-title">Análise por cliente e linha</div>', unsafe_allow_html=True)
    por_cliente = dados.groupby("CLIENTE_TRATADO").agg(embarques=("PASSAGEIRO_TRATADO", "count"), colaboradores=("PASSAGEIRO_TRATADO", "nunique"), linhas=("LINHA_TRATADA", "nunique"), prefixos=("PREFIXO_TRATADO", "nunique")).reset_index().sort_values("embarques", ascending=False)
    st.dataframe(por_cliente, use_container_width=True, hide_index=True)
    por_linha = dados.groupby("LINHA_TRATADA").size().reset_index(name="TOTAL").sort_values("TOTAL", ascending=False).head(15)
    fig_linha = px.bar(por_linha, x="TOTAL", y="LINHA_TRATADA", orientation="h", text="TOTAL", color_discrete_sequence=[BLUE])
    fig_linha.update_traces(marker_line_color=WHITE, marker_line_width=.7, textposition="outside")
    fig_linha.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(aplicar_layout(fig_linha, "Linhas com mais embarques"), use_container_width=True)

with aba3:
    st.markdown('<div class="section-title">Histórico da sessão</div>', unsafe_allow_html=True)
    st.markdown("""<div class="info-box">Este histórico é temporário e serve para validar o fluxo. A próxima versão pode gravar os dados em SQLite ou em uma base externa, permitindo comparação real mês a mês.</div>""", unsafe_allow_html=True)
    historico = st.session_state.get("historico_sessao")
    if historico is None or historico.empty:
        st.info("Nenhuma importação salva nesta sessão. Use o botão 'Salvar resumo desta importação' na barra lateral.")
    else:
        st.dataframe(historico, use_container_width=True, hide_index=True)
        hist_plot = historico.copy()
        hist_plot["aderencia"] = pd.to_numeric(hist_plot["aderencia"], errors="coerce")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(x=hist_plot["data_importacao"], y=hist_plot["aderencia"], mode="lines+markers", line=dict(color=BLUE, width=3), marker=dict(size=8, color=WHITE, line=dict(color=BLUE, width=2)), name="Aderência"))
        st.plotly_chart(aplicar_layout(fig_hist, "Aderência por importação salva"), use_container_width=True)

st.markdown('<div class="section-title">Ranking de colaboradores</div>', unsafe_allow_html=True)
ranking = dados.groupby("PASSAGEIRO_TRATADO").size().reset_index(name="EMBARQUES").sort_values("EMBARQUES", ascending=False)
st.dataframe(ranking, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Dados filtrados</div>', unsafe_allow_html=True)
st.dataframe(dados, use_container_width=True, hide_index=True)

csv = dados.to_csv(index=False).encode("utf-8-sig")
st.download_button("Baixar dados filtrados em CSV", data=csv, file_name="dados_filtrados_aderencia.csv", mime="text/csv")
