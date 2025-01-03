# utils.py
import requests

# Função para obter o token de autorização
def obter_token_autorizacao(usuario, senha):
    url_login = "https://api.grupohne.com.br/api/login"  # URL de login
    dados_login = {
        "usuario": usuario,  
        "password": senha     
    }

    headers = {
        "Content-Type": "application/json" 
    }

    try:
        # Realiza a requisição de login
        response = requests.post(url_login, headers=headers, json=dados_login)

        if response.ok:
            data = response.json()
            if "token" in data:
                token = data["token"]
                return token
            else:
                return None
        else:
            print(f"Erro ao fazer login: {response.status_code}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição: {e}")
        return None
