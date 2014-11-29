from flask import Flask, render_template, g, request
from backend.exec import Exec
from common.db import *

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template('index.html', hotels=Hotel.select(), swfs=SWF.select())


@app.route('/api')
@app.route('/api.php')
def api():
    if request.method == 'GET':
        h = Hotel.select().where(Hotel.url == request.args.get('hotel', 'com')).get()
        request_type = request.args.get('type', 'swf')
        if request_type == 'swf':
            return 'http://tanji.pw/clients/{0}.swf'.format(h.latest.name)
        elif request_type == 'keys':
            return ','.join([h.latest.newPublicModulus, h.latest.newPublicExponent, h.latest.newPrivateExponent])


@app.route('/updater/<hotel_tld>')
def updater(hotel_tld):
    hotel_tlds = ['com', 'fi', 'nl', 'dk', 'fr', 'de', 'it', 'no', 'se', 'com.tr', 'com.br', 'es']
    results = []
    if hotel_tld == 'all':
        for hotel in hotel_tlds:
            e = Exec.process(hotel)
            if e['complete'] is True:
                results.append(e)
    else:
        results.append(Exec.process(hotel_tld))

    return render_template('updater_output.html', results=results)


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
    app.run()
