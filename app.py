# import matplotlib.pyplot as plt
from flask import Flask, request, render_template, jsonify


app = Flask(__name__)


@app.route('/')
def index():
    context = {}
    return render_template('index.html', **context)



if __name__ == '__main__':
    app.debug = True
    app.run()
