from flask import Flask, render_template, request, redirect, url_for, session
from utils import obter_token_autorizacao  # Importa a função do arquivo utils.py
import os
import time

app = Flask(__name__)

# Defina uma chave secreta para a sessão
app.secret_key = os.urandom(24)

# Página principal (root), que redireciona para a página de login
@app.route('/')
def index():
    if 'token' in session:
        return redirect(url_for('bem_vindo'))  # Redireciona para a página de boas-vindas se o token estiver na sessão
    return redirect(url_for('login'))  # Caso contrário, redireciona para o login

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None  # Variável para armazenar a mensagem de erro
    sucesso = None  # Variável para armazenar a mensagem de sucesso

    if request.method == 'POST':  # Quando o formulário for enviado
        usuario = request.form['usuario']
        senha = request.form['senha']

        # Chama a função para obter o token de autorização
        token = obter_token_autorizacao(usuario, senha)

        if token:
            sucesso = "Login bem-sucedido! Você será redirecionado em breve."
            # Armazena o token na sessão
            session['token'] = token
            return redirect(url_for('bem_vindo'))  # Redireciona para a página de boas-vindas
        else:
            erro = "Credenciais incorretas!"  # Mensagem de erro

    return render_template('login.html', erro=erro, sucesso=sucesso)  # Passa erro e sucesso para o template

# Página de boas-vindas após o login correto
@app.route('/bem-vindo')
def bem_vindo():
    if 'token' in session:
        return render_template('index.html')  # Renderiza a página index.html quando o token está na sessão
    else:
        return redirect(url_for('login'))  # Se o token não estiver na sessão, redireciona para o login

@app.route('/sobre')
def sobre():
    if 'token' in session:
        return render_template('sobre.html')  # Renderiza a página sobre.html quando o token está na sessão
    else:
        return redirect(url_for('login'))  # Se o token não estiver na sessão, redireciona para o login


# Página para deslogar
@app.route('/logout')
def logout():
    # Remove o token da sessão
    session.pop('token', None)
    return redirect(url_for('login'))  # Redireciona para a página de login após deslogar


if __name__ == '__main__':
    app.run(debug=True)
