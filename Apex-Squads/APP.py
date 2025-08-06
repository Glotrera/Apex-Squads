""" Ficheiro principal do Flask para o projeto Apex Squads """

import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, g, session
from dotenv import load_dotenv

def configure_app():
    load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
    app.config['API_KEY'] = os.getenv('api_key')  # Obtém a chave da API do ambiente

app = Flask(__name__)
app.secret_key = 'chave_secret_key'
app.vonfig['DATABASE'] = 'apex_status.db'
app.config['API_KEY'] = 'sua_chave_api_aqui'

legend_images = {
    "wraith": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/a/a4/Wraith.jpg",
    "mirage": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/a/a6/Mirage.jpg",
    "bangalore": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/f/f7/Bangalore.jpg",
    "gibraltar": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/8/8b/Gibraltar.jpg",
    "lifeline": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/4/4f/Lifeline.jpg",
    "pathfinder": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/53/Pathfinder.jpg",
    "caustic": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/e/e7/Caustic.jpg",
    "octane": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/d/d6/Octane.jpg",
    "wattson": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/8/82/Wattson.jpg",
    "crypto": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/1/1f/Crypto.jpg",
    "revenant": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/59/Revenant.jpg",
    "loba": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/7/7d/Loba.jpg",
    "rampart": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/51/Rampart.jpg",
    "horizon": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/7/7d/Horizon.jpg",
    "fuse": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/2/25/Fuse.jpg",
    "valkyrie": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/5f/Valkyrie.jpg",
    "seer": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/4/4b/Seer.jpg",
    "ash": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/7/70/Ash.jpg",
    "mad maggie": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/5f/Mad_Maggie.jpg",
    "newcastle": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/b/b9/Newcastle.jpg",
    "vantage": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/5a/Vantage.jpg",
    "catalyst": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/9/9d/Catalyst.jpg",
    "ballistic": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/4/4a/Ballistic.jpg",
    "conduit": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/8/8f/Conduit.jpg",
    "alter": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/f/f8/Alter.jpg",
    "sparrow": "https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/3/36/Sparrow.jpg"
}

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
    
@app.route('/register', methods=['GET', 'POST'])
def register():
   
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            session['user'] = {'id': user['id'], 'username': user['username']}
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already exists.')

    return render_template('register.html')

    """
    Rota para o registo de novos utilizadores.
    Verifica se o utilizador já existe e armazena o novo utilizador na base de dados.
    Se o registo for bem-sucedido, armazena o utilizador na sessão.
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
    
    api_url = f"https://api.mozambiquehe.re/bridge?auth={app.config['API_KEY']}&player={player_name}&platform={platform}"
    
    player_data = None
    most_played_legend_image = None
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        player_data = response.json()
        
        if 'legends' in player_data and 'selected' in player_data['legends'] and 'legend_name' in player_data['legends']['selected']:
            legend_name = player_data['legends']['selected']['legend_name'].lower()
            
            most_played_legend_image = legend_images.get(legend_name, "https://placehold.co/1920x1080/2c3e50/ffffff?text=Lenda+Desconhecida")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados do jogador: {e}")
        
    return render_template('profile.html', player=player_data, user=session.get('user'), legend_image=most_played_legend_image)

    """
    Exibe o perfil de um jogador específico.
    Faz a chamada à API para obter os dados do jogador.
    """
    
@app.route('/discord_links')
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
    
if __name__ == '__main__':
    app.run(debug=True)
    """
    Executa a aplicação Flask.
    """