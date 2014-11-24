from flask import Flask, render_template, g
from backend.exec import Exec
from common.db import *

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template('index.html', hotels=Hotel.select(), swfs=SWF.select())


@app.route('/updater/<hotel_tld>')
def updater(hotel_tld):
    return render_template('updater_output.html', results=Exec.process(hotel_tld))


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


def hotels():
    return SWF.select()

if __name__ == '__main__':
    app.run(host='0.0.0.0')