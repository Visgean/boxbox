from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('../settings/default.py')

from . import views