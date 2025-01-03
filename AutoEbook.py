import pandas as pd
import requests
import os
import json
from datetime import datetime, timedelta
import time
import openpyxl
from termcolor import colored
import pyfiglet
import getpass





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
                print("")
                print(colored("Token obtido com sucesso.", 'green'))
                print("")
                # Salva o token
                with open("token.txt", "w", encoding="utf-8") as token_file:
                    token_file.write(token)
                return token
            else:
                print("Token não encontrado na resposta.")
                return None
        else:
            print("")
            print(f"Erro ao fazer login: {colored('Error', 'red')}: {response.status_code}")
            return
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição: {e}")
        return None


# Função obter os livros
def enviar_livros(token, pagina=1, tamanho_pagina=10, id_aluno=None, tipo_curso="ACLS", unidade=[14]):
    url_livros = "https://api.grupohne.com.br/api/v1/aluno/enviar-livros"
    headers = {
        "Authorization": f"Bearer {token}",  
        "Content-Type": "application/json"   
    }

    # Data de hoje
    data_inicial = datetime.today().date()

        # Solicitar a quantidade de dias para o cálculo da data final
    while True:
        dias_para_adicionar = input("3 - Digite a quantidade de dias para a data final: ").strip()

        # Verificar se a entrada é um número inteiro
        if dias_para_adicionar.isdigit():
            dias_para_adicionar = int(dias_para_adicionar)  # Converte para inteiro
            if dias_para_adicionar > 0:
                break  # Sai do loop se o valor for válido

            else:
                print("")
                print(colored("Por favor, insira um número maior que 0.", 'red'))
                print("")
        else:
            print("")
            print(colored("Por favor, insira apenas números.",'red'))
            print("")


    # Verificar se a entrada é um número válido
    try:
        dias_para_adicionar = int(dias_para_adicionar)  # Converte a entrada para um número inteiro
        if dias_para_adicionar < 0:
            print("Por favor, insira um número de dias positivo.")
            return
    except ValueError:
        print("Por favor, insira um número válido de dias.")
        return

    # Data final, que é a data inicial mais os dias informados pelo usuário
    data_final = data_inicial + timedelta(days=dias_para_adicionar)

    data_inicial_str = data_inicial.isoformat()
    data_final_str = data_final.isoformat()

    # Definir número do curso
    tipo_curso_map = {
        "ACLS": 8,
        "PALS": 143,
        "BLS": 9,
        "IACLS": 161
    }

    tipo_curso_valor = tipo_curso_map.get(tipo_curso.upper())

    if tipo_curso_valor is None:
        print("Tipo de curso inválido. Usando valor default 8 (ACLS).")
        tipo_curso_valor = 8 

    filtro = {
        "tipo": "ebook",
        "tipo_curso": tipo_curso_valor, 
        "cidade": "",
        "status_inscricao": "",
        "data_inicial": data_inicial_str,
        "data_final": data_final_str,
        "unidade": unidade,  
        "id_aluno": id_aluno
    }

    dados = {
        "filtro": filtro,
        "page": pagina,
        "pageSize": tamanho_pagina
    }

    try:
        # Realiza a requisição POST para enviar os livros
        response = requests.post(url_livros, headers=headers, json=dados)

        if response.ok:

            livros = response.json()

            # Verifica se contém uma lista de livros
            if "data" in livros and isinstance(livros["data"], list):
                return livros["data"]
            else:
                print("A resposta não contém uma lista válida de livros no campo 'data'.")
                return None
        else:
            print(f"Erro ao obter livros: {response.status_code}")
            print(f"Detalhes do erro: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição: {e}")
        return None
    
# Função para enviar código de rastreio para o aluno
def enviar_codigo_rastreio(token, livro, codigo_rastreio):
    url_rastreio = "https://api.grupohne.com.br/api/v1/aluno/enviar-livros-acoes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"   
    }

    dados_rastreio = {
        "acao": "codigoEbook",
        "id": [
            {
                "id": livro["id"],
                "id_aluno": livro["id_aluno"],
                "id_acao": livro["id_acao"],
                "nome": livro["nome"],
                "data_curso": livro["data_curso"],
                "rua": livro["rua"],
                "numero": livro["numero"],
                "estado": livro["estado"],
                "cidade": livro["cidade"],
                "cep": livro["cep"],
                "bairro": livro["bairro"],
                "complemento": livro["complemento"],
                "tags_folders": livro["tags_folders"],
                "qtd_envios": livro["qtd_envios"],
                "tipo_envio": livro["tipo_envio"],
                "curso": livro["curso"],
                "data_inscricao": livro["data_inscricao"],
                "data_pagamento": livro["data_pagamento"],
                "endereco": livro["endereco"],
                "nota": livro["nota"]
            }
        ],
        "codigo_rastreio": codigo_rastreio
    }

    try:
      
        response = requests.post(url_rastreio, headers=headers, json=dados_rastreio)

        if response.ok:
            print("")
            print(colored(f"- Código de rastreio '{codigo_rastreio}' enviado com sucesso para {livro['nome']}.", 'green'))
            print("")

        else:
            print("")
            print(colored(f"Erro ao enviar o código de rastreio: {response.status_code}", 'red'))
            print("")

            print(f"Detalhes do erro: {response.text}")
    except requests.exceptions.RequestException as e:
        print(colored(f"Erro de requisição ao enviar código de rastreio: {e}", 'red'))


# Função para carregar o token salvo no arquivo
def carregar_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r", encoding="utf-8") as token_file:
            token = token_file.read().strip()
            return token
    else:
        return None


# Função para registrar um log sobre o envio (usado para preencher a planilha de controle)
def registrar_log(livro, codigo_rastreio):

    # Obter a data atual
    data_criacao_log = datetime.now().strftime("%d-%m-%Y")  # Usar '-' ao invés de '/'
    
    log = f"Nome: {livro['nome']}, Curso: {livro['curso']} - {livro['cidade']}, Data do Curso: {livro['data_curso']}, Código de Rastreamento: {codigo_rastreio}, Data de Criação: {data_criacao_log}\n"
    
    # Criar o nome do arquivo com a data do dia
    nome_arquivo_log = f"envio_codigos_log_{data_criacao_log}.txt"
    
    # Abre o arquivo de log correspondente à data e escreve a nova linha
    with open(nome_arquivo_log, "a", encoding="utf-8") as log_file:
        log_file.write(log)


# Função para enviar código de rastreio para todos os alunos e registrar o nome na planilha
def enviar_codigos_rastreio_para_todos(token, livros, df, caminho_arquivo):
    
    wb = openpyxl.load_workbook(caminho_arquivo)
    sheet = wb["ACLS"]  # Inicia a planilha na aba ACLS

    # Verifica a primeira linha vazia da coluna C
    coluna_enviado_para = df.columns[2] 
    linha_vazia_pandas = df[df[coluna_enviado_para].isna()].index[0]
    linha_vazia_excel = linha_vazia_pandas + 3  # Linha onde inicia a planilha (Por conta do cabeçalho)

    print("")
    print(f"A primeira linha vazia na planilha é: {linha_vazia_excel}")
    print(f"Valor da coluna B na linha {linha_vazia_excel}: {df.iloc[linha_vazia_pandas, 1]}")

    # Enviar o código de rastreio para todos os alunos
    for index, livro in enumerate(livros):
        nome_aluno = livro['nome']
        print("")
        print(colored(f"\nVerificando se o nome {nome_aluno} já está na planilha...", 'yellow'))

        # Verificar se o nome já existe na coluna B da planilha (coluna com os nomes dos alunos)
        if nome_aluno in df['Nome do aluno'].values: 
            print(colored(f"Nome '{nome_aluno}' já encontrado na planilha. Código de rastreio não será enviado.", 'red'))
            continue
        print("")
        print(f"Enviando código de rastreio para: {colored(f'{nome_aluno} - Curso: {livro['curso']}', 'light_blue')}")
        print(f"Código de rastreio: {df.iloc[linha_vazia_pandas, 1]}")
        
        enviar_codigo_rastreio(token, livro, df.iloc[linha_vazia_pandas, 1])

        registrar_log(livro, df.iloc[linha_vazia_pandas, 1])

        # Atualiza a planilha com o nome do aluno
        df.at[linha_vazia_pandas, coluna_enviado_para] = livro['nome']  
        sheet[f"C{linha_vazia_excel}"] = livro['nome']
        wb.save(caminho_arquivo)

        # Delay para evitar que os nomes seja sobrepostos
        print(f"")
        time.sleep(2)

        # Atualiza o índice da linha vazia
        linha_vazia_pandas += 1
        linha_vazia_excel += 1
    
    realizar_requisicao()


# Função principal - Configurações
def realizar_requisicao():
    # Verificar se o token já está salvo
    token = carregar_token()  # Tenta carregar o token do arquivo

    if not token:
        # Se não encontrar o token, solicita o login
        print("")
        print(colored("Token não encontrado. Realizando login...", 'light_red'))
        print("")

        usuario = input("Digite seu usuário: ")
        senha = getpass.getpass("Digite sua senha: ")
        token = obter_token_autorizacao(usuario, senha)  # Realiza o login e salva o token

    if token:
        # Agora que o token foi obtido ou carregado, prossegue com a lógica do programa
        acls = "ACLS"
        pals = "PALS"
        bls = "BLS"
        iacls = "IACLS"

        print("")
        print('Escolha um Centro de Custo')
        print("")
        centro_custo = input("1 - Centro de Custo (BH, GO, ES): ").upper()

        # Lógica para o centro de custo BH
        if centro_custo == "BH":
            caminho_arquivo = r"EBOOKS - CUREM BH 2024.xlsx"

            while True:
                print("")
                tipo_curso = input("2 - Digite o tipo de curso (ACLS, PALS, BLS, IACLS): ").upper()
                unidade = [29, 27, 18, 1, 30, 19, 20, 28, 12, 7, 8, 21, 22, 10, 25, 4, 26, 9, 11, 23, 13, 24]

                if tipo_curso == pals:
                    df = pd.read_excel(caminho_arquivo, sheet_name="PALS", header=1)
                    break
                elif tipo_curso == bls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="BLS", header=1)
                    break
                elif tipo_curso == acls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="ACLS", header=1)
                    break
                elif tipo_curso == iacls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="I-ACLS", header=1)
                    break

                else:
                    print("")
                    print(colored("Tipo de curso inválido. Por favor, digite 'ACLS', 'PALS' ou 'BLS'.", 'red'))

        # Lógica para o centro de custo ES
        elif centro_custo == "ES":
            caminho_arquivo = r"EBOOKS - CUREM ES 2024.xlsx"
            while True:
                tipo_curso = input("2 - Digite o tipo de curso (ACLS, PALS, BLS, IACLS): ")
                unidade = [3]

                if tipo_curso == pals:
                    df = pd.read_excel(caminho_arquivo, sheet_name="PALS", header=1)
                    break
                elif tipo_curso == bls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="BLS", header=1)
                    break
                elif tipo_curso == acls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="ACLS", header=1)
                    break
                elif tipo_curso == iacls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="I-ACLS", header=1)
                    break

                else:
                    print("")
                    print(colored("Tipo de curso inválido. Por favor, digite 'ACLS', 'PALS' ou 'BLS'.", 'red'))

        # Lógica para o centro de custo GO
        elif centro_custo == "GO":
            caminho_arquivo = r"EBOOKS - CUREM GO 2024.xlsx"
            while True:
                tipo_curso = input("2 - Digite o tipo de curso (ACLS, PALS, BLS, IACLS): ")
                unidade = [14]

                if tipo_curso == pals:
                    df = pd.read_excel(caminho_arquivo, sheet_name="PALS", header=1)
                    break
                elif tipo_curso == bls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="BLS", header=1)
                    break
                elif tipo_curso == acls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="ACLS", header=1)
                    break
                elif tipo_curso == iacls:
                    df = pd.read_excel(caminho_arquivo, sheet_name="I-ACLS", header=1)
                    break
                else:
                    print("")
                    print(colored("Tipo de curso inválido. Por favor, digite 'ACLS', 'PALS' ou 'BLS'.", 'red'))

        else:
            print("Centro de custo inválido. Por favor, insira um valor válido.")
            return

        print("")

        livros = enviar_livros(token, pagina=1, tamanho_pagina=350, tipo_curso=tipo_curso, unidade=unidade)
        if livros:
            print("-")
            print("Livros recebidos:")
            print("")
            for index, livro in enumerate(livros, 1):
                print("")
                print(colored(f"{index}. Nome: {livro['nome']}, Curso: {livro['curso']}, Data do Curso: {livro['data_curso']}", 'light_blue'))
                print("")
            # Solicitar confirmação antes de enviar os livros
            confirmacao = input(colored(f"\n* Você tem certeza que deseja enviar os códigos de rastreio para os {len(livros)} livros? (s/n): ", 'yellow')).strip().lower()

            print("")

            # Solicitar confirmação antes de enviar os livros
            while True:
                if confirmacao == 's':
                    print("")
                    print("Iniciando o envio dos códigos de rastreio para todos os alunos...")
                    print("")
                    enviar_codigos_rastreio_para_todos(token, livros, df, caminho_arquivo)
                    break  # Sai do loop após confirmação de envio
                elif confirmacao == 'n':
                    print("")
                    print(colored("Envio cancelado!!", 'yellow'))
                    print("")
                    realizar_requisicao()
                    break  # Sai do loop após cancelamento
                else:
                    print("Digite 's' para SIM e 'n' para NÃO.")  # Mensagem de erro para respostas inválidas
        else:
            print("")
            print(colored("* Não foi possível obter os livros. Tente novamente, ou tente outro Centro de Custo.", 'red'))
            realizar_requisicao()

    else:
        print("Não foi possível obter o token de autorização.")

        

# Chama a função principal
realizar_requisicao()