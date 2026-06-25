# Dashboard de Aderência - V5 Multi-clientes

Sistema em Streamlit para acompanhamento semanal de aderência de embarque por cliente.

## Recursos

- Painel ADM com senha
- Cadastro de múltiplos clientes
- Upload de logo da sua empresa
- Upload de logo do cliente
- Importação semanal por cliente
- Histórico semanal de aderência
- Comparativo semana atual x semana anterior
- Link individual por cliente com token
- Cliente visualiza apenas o próprio dashboard
- Lista de colaboradores sem embarque por semana

## Acesso ADM

Senha padrão do MVP:

```text
admin123
```

Recomendado configurar no Streamlit Secrets:

```toml
ADMIN_PASSWORD = "sua-senha-forte"
```

## Link do cliente

Cada cliente recebe link com slug e token:

```text
https://SEU-APP.streamlit.app/?cliente=total-express&token=TOKEN
```

## Importante

Esta versão usa armazenamento local em JSON:

```text
data/database.json
```

Serve para validar o fluxo. Para uso contínuo e seguro, a próxima etapa recomendada é migrar para Supabase/PostgreSQL.
