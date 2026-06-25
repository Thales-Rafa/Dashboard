# Dashboard de Aderência - V5.1 Link Público Corrigido

Sistema em Streamlit para acompanhamento semanal de aderência de embarque por cliente.

## Correção principal da V5.1

O link do cliente não usa mais placeholder fixo `SEU-APP`.

Agora o ADM informa a URL pública real do app em:

```text
Configurações e links > URL pública do app
```

Exemplo:

```text
https://dashboard-famatur.streamlit.app
```

Depois disso, os links dos clientes são gerados assim:

```text
https://dashboard-famatur.streamlit.app/?cliente=total-express&token=TOKEN
```

## Acesso ADM

Senha padrão do MVP:

```text
admin123
```

Recomendado configurar no Streamlit Secrets:

```toml
ADMIN_PASSWORD = "sua-senha-forte"
```

## Recursos

- Painel ADM
- Cadastro de clientes
- Logo da sua empresa
- Logo por cliente
- Histórico semanal
- Comparativo semanal
- Link público individual por cliente com token
- Cliente vê apenas o próprio dashboard

## Observação

Esta versão usa armazenamento local em JSON:

```text
data/database.json
```

Para uso contínuo real, a próxima etapa é migrar para Supabase/PostgreSQL.

## V5.2

Novidades:

- Aba **Gerenciar importações**
- Excluir importação errada
- Substituir importação da mesma semana/cliente
- Gráfico pizza comparando:
  - colaboradores cadastrados que embarcaram
  - colaboradores cadastrados faltantes
- Tabela de indicadores com:
  - indicador
  - valor
  - status
- Tabela resumo:
  - Embarcaram
  - Faltantes
  - Total cadastrados


## V5.3 CRUD

Novidades:

- CRUD de clientes:
  - criar cliente
  - visualizar clientes
  - editar nome
  - ativar/desativar cliente
  - trocar/remover logo
  - regenerar token/link público
  - excluir cliente com importações vinculadas
- CRUD de importações:
  - visualizar importações por cliente
  - excluir importação
  - substituir semana já existente
  - ajuste manual de totais de uma importação
- Configurações:
  - editar URL pública do app
  - editar nome/logo da operação
  - baixar backup JSON
  - limpar banco total


## V5.4

Correções:

- Corrige erro `NameError` no gráfico de pizza importando `plotly.express`.
- Identifica automaticamente o período real do relatório de embarque.
- Permite usar automaticamente o período encontrado no arquivo.
- Mostra alerta quando o período selecionado não bate com as datas do relatório.
- Evita importações com realizado zerado por período selecionado errado.
