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