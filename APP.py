""" Ficheiro principal do Flask para o projeto Apex Squads """

import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, g, session

app = Flask(__name__)
app.secret_key = 'chave_secret_key'
app.vonfig['DATABASE'] = 'apex_status.db'
app.config['API_KEY'] = 'sua_chave_api_aqui'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

    """
    Cria uma conexão com a base de dados SQL
    """

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
    """
    Fecha a conexão com a base de dados no final da requisição
    """
        
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS wishlist (
                user_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            ); 
        ''')
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', 'password'))
            db.commit()
        except sqlite3.IntegrityError:
            print("Utilizador 'testuser' já existe.")
        print("Base de dados inicializada e tabelas criadas.")
    """
    Inicializa a base de dados com as tabelas necessárias
    """

@app.cli.command('initdb')
def initdb_command():
    """
    Inicializa a base de dados.
    """
    init_db()
    print('Base de dados inicializada.')
        
# --- Rotas da Aplicação ---

@app.route('/')
def home():
    return render_template('home.html', user=session.get('user'))
    """
    Rota para a página principal, com um formulário de pesquisa.
    """
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        
        if user:
            session['user'] = {'id': user['id'], 'username': user['username']}
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Credenciais inválidas.')
        
    return render_template('login.html')

    """
    Rota para o login do utilizador.
    Verifica as credenciais e armazena o utilizador na sessão.
    """
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))
    """
    Rota para o logout do utilizador.
    Remove o utilizador da sessão.
    """
    
@app.route('/perfil', methods=['POST'])
def search_profile():
    player_name = request.form['player_name']
    platform = request.form['platform']
    return redirect(url_for('show_profile', player_name=player_name, platform=platform))
    
    """
    Rota para pesquisar o perfil de um jogador.
    Redireciona para a rota de exibição do perfil
    """
    
@app.route('/perfil/<string:player_name>/<string:platform>')
def show_profile(platform, player_name):
    api_url = f"https://api.mozambiquehe.re/bridge?auth=YOUR_API_KEY&player=PLAYER_NAME&platform=PLATFORM"
    headers = {"Authorization": app.config['API_KEY']}
    player_data = None
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        player_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados do jogador: {e}")
        
    return render_template('profile.html', player_data=player_data, user=session.get('user'))

    """
    Exibe o perfil de um jogador específico.
    Faz a chamada à API para obter os dados do jogador.
    """
    
@app.route('/wishlist')
def wishlist():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    db = get_db()
    items = db.execute('SELECT item_id FROM wishlist WHERE user_id = ?', (user_id,)).fetchall()
    
    return render_template('wishlist.html', items=items, user=session.get('user'))

    """
    Rota para a wishlist do utilizador.
    """
    
@app.route('/add_to_wishlist' , methods=['POST'])
def add_to_wishlist():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    item_id = request.form.get('item_id')
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO wishlist (user_id, item_id) VALUES (?, ?)', (user_id, item_id))
        db.commit()
    except sqlite3.IntegrityError:
        print(f"Item {item_id} já está na wishlist.")
        
    """
    Adiciona um item à wishlist do utilizador.
    """

@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    item_id = request.form.get('item_id')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM wishlist WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    db.commit()
    
    return redirect(url_for('wishlist'))

    """
    Remove um item da wishlist do utilizador.
    """

@route('/discord_links')
def discord_links():
    
    discord_servers = [
        {'name': 'Apex Legends', 'url': 'https://discord.com/servers/apex-legends-541484311354933258'},
        {'name': 'Apex Legends FR', 'url': 'https://discord.com/servers/apex-legends-fr-463019891658588180'},
        {'name': 'Apex Legends Brasil', 'url': 'https://discord.com/servers/apex-legends-brasil-542501711860727848'},
        {'name': 'Battlecord | Apex', 'url': 'https://discord.com/servers/battlecord-apex-633157361074176000'},
    ]
    return render_template('discord_links.html', servers=discord_servers, user=session.get('user'))

    """
    Rota para exibir links de servidores do Discord relacionados ao Apex Legends.
    """
    
