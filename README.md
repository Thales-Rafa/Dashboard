# Dashboard de Aderência de Embarque - V2

Melhorias:

- Visual premium com azul escuro, branco e cinza claro
- Interface sem emojis
- Cards de indicadores personalizados
- Gráficos redesenhados
- Campo de cliente no upload
- Filtro por cliente
- Aba de cliente e linhas
- Histórico temporário da sessão

## Separação por cliente

Se o Excel tiver coluna CLIENTE, o app usa essa coluna.
Se não tiver, usa o campo Cliente desta importação na barra lateral.

## Histórico

A V2 possui histórico temporário por sessão. Para salvar, envie o Excel e clique em Salvar resumo desta importação.

Para histórico permanente, a próxima versão deve usar SQLite ou banco externo.
