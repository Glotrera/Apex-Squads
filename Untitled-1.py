import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, g, session

app =