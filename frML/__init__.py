from flask import Flask
import os

app = Flask(__name__.split('.')[0])

import routes
