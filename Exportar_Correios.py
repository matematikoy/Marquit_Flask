import requests
from termcolor import colored
from datetime import datetime, timedelta
import os
import pyfiglet

# Texto
text = "Exportar do Correios"

# Definir bordas
border = "*" * (len(text) + 6)
ascii_art_with_border = f"{border}\n"
ascii_art_with_border += f"* {colored(text, 'yellow')} *\n"
ascii_art_with_border += border

# Exibir o resultado
print(ascii_art_with_border)
print("")

# Função para obter o token de autorização e salvar em um arquivo
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
                print("Token obtido com sucesso.")
                # Salva o token
                with open("token.txt", "w", encoding="utf-8") as token_file:
                    token_file.write(token)
                return token
            else:
                print("Token não encontrado na resposta.")
                return None
        else:
            print(f"Erro ao fazer login: {response.status_code}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição: {e}")
        return None

# Função para ler o token de um arquivo
def ler_token_do_arquivo():
    if os.path.exists("token.txt"):
        with open("token.txt", "r", encoding="utf-8") as token_file:
            return token_file.read().strip()
    else:
        return None

# Função para fazer a requisição ao endpoint e filtrar os dados com a nota 'EMITIDA'
def enviar_livros(token, unidade, data_inicial, data_final):
    url = "https://api.grupohne.com.br/api/v1/aluno/enviar-livros?page=1&pageSize=10"
    headers = {
        "Authorization": f"Bearer {token}",  
        "Content-Type": "application/json"   
    }

    payload = {
        "filtro": {
            "tipo": "pacsedex",
            "tipo_curso": "",
            "cidade": "",
            "unidade": unidade,  # Unidade baseada no Centro de Custo
            "status_inscricao": "",
            "material_entrega": {"pac": True, "sedex": True},
            "data_inicial": data_inicial,  # API espera no formato yyyy-mm-dd
            "data_final": data_final       # API espera no formato yyyy-mm-dd
        },
        "page": 1,
        "pageSize": 350
    }

    # Enviar requisição POST
    response = requests.post(url, json=payload, headers=headers)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        
        # Filtrar os itens com "nota" == "EMITIDA" e coletar ID, Nome e Curso
        ids_nomes_cursos_emitidos = [(item['id'], item['nome'], item.get('curso', 'Curso não disponível')) for item in data['data'] if item['nota'] == "EMITIDA"]
        
        # Exibir os ids, nomes e cursos filtrados
        if ids_nomes_cursos_emitidos:
            print("IDs, Nomes e Cursos com nota 'EMITIDA':")
            print("")
            for id, nome, curso in ids_nomes_cursos_emitidos:
                print(colored(f"ID: {id}, Nome: {nome}, Curso: {curso}", 'light_blue'))
            return ids_nomes_cursos_emitidos
        else:
            print(colored("Nenhum item com nota 'EMITIDA' encontrado.", 'yellow'))
            return []
    else:
        print("Erro na requisição:", response.status_code)
        return []

# Função para enviar os IDs para o endpoint de exportação e salvar o arquivo CSV
def exportar_correios(token, ids):
    url = "https://api.grupohne.com.br/api/v1/aluno/exportar_correios"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "ids": ids
    }

    # Enviar requisição POST para exportar os correios
    response = requests.post(url, json=payload, headers=headers)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Obter a data de hoje no formato ddmmaaaa para nomear o arquivo
        data_hoje = datetime.today().strftime("%d%m%Y")
        
        # O conteúdo da resposta será em formato CSV
        linhas = response.content.decode('utf-8').splitlines()
        
        if len(linhas) > 1:
            # Verificar se a pasta 'EXPORTADOS' existe, caso contrário, criar
            pasta_exportados = 'EXPORTADOS'
            if not os.path.exists(pasta_exportados):
                os.makedirs(pasta_exportados)  # Cria a pasta

            # Caminho completo do arquivo
            caminho_arquivo = os.path.join(pasta_exportados, f"CORREIOS_{data_hoje}.csv")
            
            # Ignorar a primeira linha e escrever o restante no arquivo
            with open(caminho_arquivo, "wb") as f:
                # Definir o cabeçalho
                cabecalho = "SERVICO;DESTINATARIO;CEP;LOGRADOURO;NUMERO;COMPLEMENTO;BAIRRO;EMAIL;;;CPF/CNPJ;VALOR_DECLARADO;;TIPO_OBJETO;;;;;AR;MP;;;OBSERVACAO\n"
                f.write(cabecalho.encode('utf-8'))
                
                # Escrever todas as linhas, ignorando a primeira
                for linha in linhas[1:]:
                    f.write(linha.encode('utf-8') + b"\n")
        
            print(colored(f"Arquivo CSV exportado com sucesso como '{caminho_arquivo}'.", 'green'))
        else:
            print("Resposta da API não contém dados válidos.")
    else:
        print("Erro ao exportar correios:", response.status_code)

# Função principal
def main():
    # Verificar se já existe um token no arquivo
    token = ler_token_do_arquivo()

    if token:
        print(colored("Token encontrado no arquivo.", 'green'))
    else:
        # Caso o token não seja encontrado, solicitar login
        print("Token não encontrado, realizando login...")
        usuario = input("Digite seu usuário: ")
        senha = input("Digite sua senha: ")
        token = obter_token_autorizacao(usuario, senha)

        if not token:
            print("Não foi possível obter o token. Encerrando a execução.")
            return

    # Perguntar o Centro de Custo
    print("")
    centro_custo = input("Digite o Centro de Custo (BH, GO, ES): ").strip().upper()
    print("")

    if centro_custo == "BH":
        unidade = [29, 27, 18, 1, 30, 19, 20, 28, 12, 7, 8, 21, 22, 10, 25, 4, 26, 9, 11, 23, 13, 24]
    elif centro_custo == "GO":
        unidade = [14]
    elif centro_custo == "ES":
        unidade = [3]
    else:
        print("")
        print(colored("Centro de Custo inválido.", 'red'))
        return


    # Solicitar ao usuário a quantidade de dias após hoje

    print("")
    dias_apos_hoje = int(input("Quantos dias após HOJE para a data final? "))
    print("")
        
    # Calcular as datas
    data_inicial_api = datetime.today().strftime("%Y-%m-%d")  # Data de hoje no formato yyyy-mm-dd para a API
    data_final_api = (datetime.today() + timedelta(days=dias_apos_hoje)).strftime("%Y-%m-%d")  # Data final no formato yyyy-mm-dd para a API
        
    # Mostrar as datas no formato dd/mm/yyyy para o usuário
    data_inicial_usuario = datetime.today().strftime("%d/%m/%Y")  # Data de hoje no formato dd/mm/yyyy para exibição
    data_final_usuario = (datetime.today() + timedelta(days=dias_apos_hoje)).strftime("%d/%m/%Y")  # Data final no formato dd/mm/yyyy para exibição
        
    print(f"Período do Curso: de {data_inicial_usuario} a {data_final_usuario}")
    print(f"")
        
    # Chamar a função para enviar os livros e filtrar os resultados
    ids_nomes_cursos_emitidos = enviar_livros(token, unidade, data_inicial_api, data_final_api)

    if ids_nomes_cursos_emitidos:
        # Perguntar se o usuário quer enviar os IDs para exportação
        print("")
        confirmar_envio = input(colored(f"Você deseja realmente enviar os {len(ids_nomes_cursos_emitidos)} IDs para exportação? (s/n): ", 'yellow')).strip().lower()
        print("")

        if confirmar_envio == 's':
            # Extrair apenas os IDs
            ids = [id for id, nome, curso in ids_nomes_cursos_emitidos]
            # Enviar os IDs para o endpoint de exportação
            exportar_correios(token, ids)
        else:
            print("")
            print(colored("Envio cancelado.", 'yellow'))
            print("")

    else:
        print(colored("Nenhum ID encontrado para envio.", 'yellow'))

# Executar a função principal
if __name__ == "__main__":
    main()
