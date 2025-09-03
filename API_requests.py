import requests

key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJINWNwUGpicUpFdFdKMjdTSlI5UFNNZUY1N09xQ1lRVWhjejJCa3UyTFNQa01qVVB5VUVTVWhNZFNOZnVhQnZRRmMtZFhYc0ZvUWFDSjVEVCIsImlhdCI6MTcxMDg0Njc4MX0.yzj8qQ2eq28LoKSp2KAOb05MmDSooirEwVB9LCtoDjg"

def gov_request(id_set, params=None):
    url = "https://dados.gov.br/dados/api/publico/conjuntos-dados/" + id_set
    response = requests.get(url, params=params, headers = {"chave-api-dados-abertos" : key})


    if response.headers.get('content-type') != 'application/json':
        return print(response.headers.get('content-type'))
    
    return response.json()
    
params = {
    "ano": 2025,  # Exemplo de filtro por ano
    "cidade": -1,
    "pagina": 1   # Página inicial
}


rq = gov_request("bolsa-familia", params=params)

print(rq['tags'])