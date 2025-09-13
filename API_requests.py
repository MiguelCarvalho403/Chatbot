import requests

key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJINWNwUGpicUpFdFdKMjdTSlI5UFNNZUY1N09xQ1lRVWhjejJCa3UyTFNQa01qVVB5VUVTVWhNZFNOZnVhQnZRRmMtZFhYc0ZvUWFDSjVEVCIsImlhdCI6MTcxMDg0Njc4MX0.yzj8qQ2eq28LoKSp2KAOb05MmDSooirEwVB9LCtoDjg"
base_gov_url = "https://dados.gov.br/dados/api/publico/conjuntos-dados"
                
def gov_request(word, params=None):
    repos = []
    for page in range(1, 10):
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
    
params = {
    "ano": 2025,  # Exemplo de filtro por ano
    "cidade": -1
}

inp = str(input("Digite o nome do conjunto de dados que deseja buscar:"))

rq = gov_request(inp, params=params)

for r in rq:
    print(r)
    
    print()
