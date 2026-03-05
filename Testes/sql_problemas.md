# Problemas com geração de SQL

## Gerenciar case sensitive

lower(), upper()... escrever tabaco ao invés de Tabaco gera erros

## Dificuldade de interpretação de colunas

No csv Tabela 1 - Base de Incidência, o modelo possui dificuldades de enteder que a coluna descrição são entidades,
nomes fornecidos pelas tabelas podem ser ambiguos, adiconar que, por exemplo, Tabaco ou IOF são do tipo descrição na query do usuário ajudou significamente na interpretação do modelo, deve passar essa resposabilidade para context prompt

## Colunas compostas

Algumas colunas podem apresentar a seguinte formatação a LLM pode gerar código sem "", como Mês/Ano, o que gera
o seguinte erro: "no such column: Mês". 

Sugestão: Limpar colunas com nomes compostos


Gerado pela LLM:
~~~
    SELECT 
        Terceirizado, 
        Cargo, 
        Mês/Ano
    FROM 
        dt_table 
    WHERE 
        Empresa = 'REAL JG SERVIÇOS GERAIS'
~~~
Corrigido: 
~~~
    SELECT 
        Terceirizado, 
        Cargo, 
        "Mês/Ano" <-------
    FROM 
        dt_table 
    WHERE 
        Empresa = 'REAL JG SERVIÇOS GERAIS'
~~~
    
Fonte: "https://dados.df.gov.br/dataset/4cd9832d-959d-405e-8e21-69c40187195d/resourcefbf987e6-982b-4765-94cd-817144e5ace3/download/funcionariosterceirizados2022.csv"

# Problemas com tabelas

## Fusão de colunas e blanklines

Algumas colunas 

Alguns campos apresentam as seguintes aberrações "NELSON JOSÉ OAQUIM JUNIOR                             DIRETOR PRESIDENTE"