# Dashboard de Aderência de Embarque - V3

Versão com cálculo correto de aderência usando duas bases:

1. Excel de embarques realizados
2. Base de colaboradores cadastrados

## Fórmula principal

```text
Esperado = colaboradores cadastrados × embarques esperados por colaborador/dia × dias considerados
Aderência = embarques realizados / embarques esperados
```

Por padrão:

```text
2 embarques esperados por colaborador/dia
```

## Arquivos esperados

### Excel de embarques

Colunas aceitas:

- TIPO
- PASSAGEIRO
- LINHA
- PREFIXO
- DATA/HORA
- LATITUDE
- LONGITUDE

### Base de colaboradores

Colunas aceitas:

- NOME
- MATRÍCULA
- LINHA
- TURNO
- ACESSO APP
- CADASTRO
- RFID
- OBSERVAÇÃO

## Recursos da V3

- Upload separado para embarques realizados
- Upload separado para colaboradores cadastrados
- Cálculo de esperado com base em colaboradores cadastrados
- Regra de 2 embarques por colaborador/dia
- Opção para considerar data de cadastro
- Filtro por cliente
- Filtro por linha
- Filtro por turno
- Filtro por tipo de embarque
- Esperado x Realizado por dia
- Aderência diária
- Colaboradores cadastrados sem embarque
- Embarques fora da base de colaboradores
- Exportação de CSV

## Deploy

Arquivos necessários:

```text
app.py
requirements.txt
runtime.txt
pyproject.toml
README.md
```