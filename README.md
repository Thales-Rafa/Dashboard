# Dashboard de Aderência de Embarque

Aplicação web em Streamlit para análise de aderência de embarque em fretamento corporativo.

## Objetivo

Ler arquivos Excel de embarque e gerar indicadores rápidos para acompanhamento de uso por QR Code, crachá ou outros meios de identificação.

## Funcionalidades do MVP

- Upload de Excel `.xlsx` ou `.xls`
- Filtro por cliente / linha / rota
- Filtro por período
- Filtro por tipo de embarque
- Filtro por prefixo
- KPIs:
  - Total esperado
  - Total embarcado
  - Percentual de aderência
  - Colaboradores únicos
  - Dias analisados
- Gráfico de embarques por dia
- Gráfico por tipo de embarque
- Ranking de prefixos
- Ranking de colaboradores
- Download dos dados filtrados em CSV

## Colunas reconhecidas

O app tenta identificar automaticamente colunas com nomes parecidos com:

- `TIPO`
- `PASSAGEIRO`
- `COLABORADOR`
- `NOME`
- `LINHA`
- `ROTA`
- `CLIENTE`
- `PREFIXO`
- `DATA/HORA`
- `DATA`
- `LATITUDE`
- `LONGITUDE`
- `ESPERADO`
- `PREVISTO`
- `PROGRAMADO`

## Observação sobre aderência

O Excel de embarque normalmente traz apenas os embarques realizados.  
Para calcular aderência real, o ideal é ter também uma base de esperados, por exemplo:

- colaboradores ativos por cliente;
- colaboradores previstos por dia;
- escala planejada;
- lista de pessoas esperadas por rota/período.

Enquanto isso, o app permite calcular o esperado de quatro formas:

1. Informar total esperado manualmente;
2. Colaboradores únicos × dias com registro;
3. Colaboradores únicos × dias úteis do período;
4. Usar coluna `ESPERADO` ou `PREVISTO`, caso exista no Excel.

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como publicar no Streamlit Cloud

1. Suba estes arquivos no GitHub:
   - `app.py`
   - `requirements.txt`
   - `README.md`

2. Acesse o Streamlit Cloud.

3. Clique em **New app**.

4. Selecione este repositório.

5. Configure:
   - Branch: `main`
   - Main file path: `app.py`

6. Clique em **Deploy**.

## Estrutura

```text
dashboard-aderencia-fretamento/
├── app.py
├── requirements.txt
└── README.md
```

## Próxima evolução recomendada

- Upload de uma segunda planilha com colaboradores esperados;
- Histórico de importações em CSV ou SQLite;
- Separação por cliente;
- Login simples por cliente;
- Exportação de relatório em PDF;
- Comparação mês a mês.
```