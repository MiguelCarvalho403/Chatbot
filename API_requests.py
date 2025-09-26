import requests
import pandas as pd

key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJINWNwUGpicUpFdFdKMjdTSlI5UFNNZUY1N09xQ1lRVWhjejJCa3UyTFNQa01qVVB5VUVTVWhNZFNOZnVhQnZRRmMtZFhYc0ZvUWFDSjVEVCIsImlhdCI6MTcxMDg0Njc4MX0.yzj8qQ2eq28LoKSp2KAOb05MmDSooirEwVB9LCtoDjg"
base_gov_url = "https://dados.gov.br/dados/api/publico/conjuntos-dados"

def gov_request_id(id,):
    response = requests.get(base_gov_url+"/"+id, headers = {"chave-api-dados-abertos" : key})
    if response.headers.get('content-type') == 'application/json':
        return response.json()
    else:
        raise ValueError("Resposta não é JSON")

def gov_request_cat(word, params=None):
    repos = []
    for page in range(1, params['pagina']+1):
        params = {
            'isPrivado': 'false',
            'pagina': page,
            'nomeConjuntoDados': word
        }
        response = requests.get(base_gov_url, params=params, headers = {"chave-api-dados-abertos" : key})
        
        if response.headers.get('content-type') == 'application/json':
            repos += response.json()
            # raise ValueError("Resposta não é JSON")    
    return repos
    
def getCsv(url):
    df = pd.read_csv(url, encoding='latin1')
    return df


params = {
    "ano": 2025,  # Exemplo de filtro por ano
    "cidade": -1,
    "pagina": 1
}

while True:
    inp = str(input("Digite o nome do conjunto de dados que deseja buscar:"))

    if inp.lower() == 'sair':
        break

    rq = gov_request_cat(inp, params=params)

    for r in rq:
        print(r)
        print()
    
    print(f"Foram encontrados {len(rq)} conjuntos de dados.")
    print("Digite 'sair' para encerrar o programa.")

    print("---------------------------------------------------")
    print()

    inp = str(input("deseja se aprofundar em algum dado?"))
    print(rq[int(inp)])      

    rq = gov_request_id(rq[int(inp)]['id'])
    print(rq)