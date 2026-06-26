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


## V5.5 - Período automático

Nesta versão o ADM não escolhe mais manualmente a semana/período da importação.

O sistema identifica automaticamente:

```text
Período inicial = menor DATA/HORA encontrada no relatório de embarque
Período final = maior DATA/HORA encontrada no relatório de embarque
```

Isso evita importar um relatório com datas antigas usando uma semana errada e gerar aderência zerada.


## V5.6 - Correção definitiva do período automático

A tela de nova importação não possui mais campos manuais de início/fim da semana.

Fluxo correto:

1. Selecionar cliente
2. Enviar relatório de embarque
3. Enviar arquivo de colaboradores cadastrados
4. O sistema identifica automaticamente a menor e maior data do relatório de embarque
5. O ADM define somente a regra operacional, como dias de operação e embarques por colaborador/dia
6. Processar e salvar

Isso elimina o erro de salvar importações com período fora do relatório.


## V5.7 - Filtros e limpeza visual

Novidades:

- Filtro lateral no dashboard do cliente:
  - Todo o período
  - Por dia
  - Intervalo personalizado
- Cards de resumo recalculados conforme o filtro escolhido
- Gráficos de esperado x realizado e aderência diária respeitam o filtro
- CSS para ocultar elementos padrão do Streamlit, como menu, rodapé e toolbar quando possível

Observação: em alguns ambientes do Streamlit Cloud, o botão Share pode continuar aparecendo por limitação da própria plataforma.


## V5.8 - Correção CSS

Corrigido erro de NameError causado por CSS inserido fora do bloco HTML.


## V5.11 - Correção definitiva render_header

Correção:
- `render_header()` agora é definido antes do `render_admin()`.
- Cabeçalho não quebra sem logo ou configuração.
- Mantém filtros no link público do cliente.
- Corrige `titulo_periodo`.


## V5.14 - Filtro inline limpo

- Base: V5.11 estável.
- Move filtros do dashboard público do cliente para o corpo da página.
- Não adiciona CSS extra, para evitar erros de `NameError`.


## V5.15 - Login ADM no corpo da página

- Campo de senha ADM saiu da barra lateral.
- Login agora aparece no centro da página.
- Após login, o ADM pode sair pelo botão na lateral.


## V5.17 - Semanal + logos com CSS seguro

- Datas em português no formato DD/MM/AAAA.
- Filtro padrão do dashboard público agora é Por semana.
- Mantém Todo o período, Por dia e Intervalo personalizado.
- Logo da empresa aparece dentro do bloco principal no ADM.
- Logos dos clientes aparecem abaixo do subtítulo no ADM e são clicáveis.
- CSS dos cards de logo foi inserido em bloco seguro, evitando NameError.


## V5.18 - Correção HTML renderizado

Correções:
- Corrigido cabeçalho que estava exibindo HTML como texto/código.
- Logos dos clientes agora são renderizadas com `st.markdown(..., unsafe_allow_html=True)` diretamente.
- Mantém filtro semanal, datas em português e logos clicáveis.


## V5.19 - Correção de indentação HTML

Correções:
- HTML do cabeçalho e cards de clientes sem indentação.
- Evita que Streamlit/Markdown interprete o HTML como bloco de código.
- Mantém logos clicáveis, filtro semanal e datas em português.


## V5.20 - Ajuste do cabeçalho do cliente

- Remove duplicidade da logo Famatur no dashboard público do cliente.
- Cliente vê Famatur no topo esquerdo e sua própria logo no topo direito.
- Bloco principal do cliente fica mais limpo, apenas com título e subtítulo.
- ADM mantém logo Famatur dentro do bloco principal e logos clicáveis dos clientes abaixo.


## V5.21 - Adesão unificada

- Remove a tabela duplicada de resumo.
- Junta os indicadores em uma única tabela consolidada.
- Altera legenda para "Colaboradores com pelo menos 1 embarque".
- Aumenta o gráfico de pizza para evitar cortes.
- Pizza e tabela usam os valores de adesão da base/importação e mantêm indicadores operacionais sensíveis ao filtro.


## V5.22 - Pizza sem corte

- Rótulos da pizza movidos para dentro do gráfico.
- Legenda foi movida para baixo.
- Nome do gráfico simplificado para evitar cortes laterais.


## V5.23 - Histórico semanal real

- O gráfico de histórico não usa mais a data da importação como referência.
- O histórico agora é agrupado pela semana operacional real dos embarques.
- Cada ponto representa:
  - semana segunda a domingo
  - esperado da semana
  - realizado da semana
  - aderência semanal
- A tabela de histórico também passa a mostrar semanas operacionais.


## V5.24 - Cards por semana operacional

- Card "Importação anterior" trocado por "Semana anterior".
- Card "Variação" trocado por "Variação semanal".
- Comparativo agora usa a semana operacional anterior, não a importação anterior.
- Se não houver semana anterior salva, aparece "Sem histórico anterior".


## V5.25 - Tooltips em português

- Corrigido tooltip padrão do Plotly que mostrava `(data, valor)`.
- Tooltips agora aparecem em português:
  - Data
  - Semana
  - Esperado
  - Realizado
  - Aderência
- Percentuais aparecem com símbolo `%`.


## V5.26 - Correção salvar_importacao

- Restaurada/garantida a função `salvar_importacao`.
- Corrige erro `name 'salvar_importacao' is not defined` ao processar nova importação.
- Mantém tooltips em português, histórico semanal real e demais ajustes visuais.


## V5.27 - Persistência com Supabase

Esta versão resolve o problema de perda de dados no Streamlit Cloud.

### Por que os dados sumiam?

O Streamlit Cloud não deve ser usado como banco de dados. Arquivos locais como:

```text
data/database.json
```

podem ser perdidos quando o app reinicia, hiberna, atualiza ou troca de máquina.

### Como configurar o Supabase

Crie um projeto no Supabase e execute este SQL:

```sql
create table if not exists app_state (
  id integer primary key,
  data jsonb not null,
  updated_at timestamp with time zone default now()
);
```

Depois, no Streamlit Cloud, configure em:

```text
Manage app > Settings > Secrets
```

Adicione:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_KEY = "SUA-ANON-KEY"
ADMIN_PASSWORD = "sua-senha-adm"
```

Depois clique em:

```text
Manage app > Reboot app
```

### Funcionamento

- Se Supabase estiver configurado, todos os clientes, logos, importações, métricas e histórico ficam salvos no banco.
- Se Supabase não estiver configurado, o app usa JSON local, mas isso é apenas temporário e pode ser perdido.
