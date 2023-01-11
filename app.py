# import library

from flask import Flask, render_template, redirect, request, url_for, flash, g, session
import sqlite3
from datetime import date
import random
import string
import hashlib
import binascii


app_info = {
    'db_file': 'D:/nauka/Python/python_github/Social media - Flask/data/social.db'
}

app = Flask(__name__)

app.config['SECRET_KEY'] = 'VeryWiredK3y!'




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():           
    return render_template('login.html')
    


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
