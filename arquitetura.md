# Arquitetura Chatbot


## Diagrama de estados


```mermaid
stateDiagram



    1boas_vindas: 1 Boas-vindas
    2retorna_colecao: 2 Retorna coleções de dados
    3dados_brutos: 3 Retorna Dados brutos

    baixar: Baixar
    visualizar: Visualizar

    state if_state1 <<choice>>
    state if_state2 <<choice>>

    [*] --> 1boas_vindas

    1boas_vindas --> 2retorna_colecao : Usuário requisita coleção de dados
    2retorna_colecao --> if_state1
        if_state1 --> 2retorna_colecao: Enriquecer busca
        if_state1 --> 3dados_brutos: Usuário escolhe uma coleção
     3dados_brutos --> if_state2
        if_state2 --> baixar: Baixar dados brutos
        if_state2 --> visualizar: Visualizar dados        

    

```

## Explicação

1. **Boas vindas :** Dá boas vindas ao usuário e explica brevemente como o sistema funciona.
2. **Retorna coleções de dados :** Retorna uma lista de coleções de dados, o usuário pode escolher uma em meio a lista ou enriquecer a pergunta com filtros(datas, locais, nomes...) a fim de obter a coleção mais adequada.
3. **Retorna dados brutos :** Retorna dados brutos, o usuário pode optar entre baixa-los e analisa-los por conta própria ou pedir ao ChatBot para visualizar os dados em meio adequado.
4.

## Referenciais:

[9]A Chatbot for Searching and Exploring Open Data: Implementation and Evaluation in E-Government