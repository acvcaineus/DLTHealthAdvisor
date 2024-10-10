import requests

# URL da API
base_url = "http://127.0.0.1:5001/api"

# Dados de entrada para a recomendação
input_data = {
    "privacy": 8,
    "integration": 7,
    "data_volume": 6,
    "energy_efficiency": 7.5,
    "Security": 9,
    "Scalability": 8,
    "Governance": 7,
    "Interoperability": 7.5,
    "Operational Complexity": 6,
    "Implementation Cost": 7,
    "Latency": 5
}

# Solicitação de recomendação
response = requests.post(f"{base_url}/recommend", json=input_data)

# Verificando a resposta da API
if response.status_code == 200:
    print("Recommendation:", response.json())
else:
    print("Error:", response.status_code, response.text)

# Solicitação de análise de sensibilidade
response = requests.post(f"{base_url}/sensitivity_analysis", json=input_data)

# Verificando a resposta da análise de sensibilidade
if response.status_code == 200:
    print("Sensitivity Analysis:", response.json())
else:
    print("Error:", response.status_code, response.text)
