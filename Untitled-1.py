import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, g, session

app = Flask(__name__)
app.secret_key = 'chave_secret_key'
app.vonfig['DATABASE'] = 'apex_status.db'
app.config['API_KEY'] = 'sua_chave_api_aqui'