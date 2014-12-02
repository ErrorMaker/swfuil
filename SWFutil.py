from flask import Flask, render_template, g, request, send_file, abort
from backend.exec import Exec
from common.db import *
from urllib import request as req
import os


app = Flask(__name__)
app.debug = True
operating_dir = os.path.dirname(os.path.abspath(__file__))


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
            return 'http://tanji.pw/gordon/{0}/Habbo.swf'.format(h.latest.name)
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


@app.route('/gordon/RELEASE<version>/<file>.swf')
def get_resource(version, file):
    local_path = operating_dir + '/gordon/RELEASE' + version
    local = '{0}/{1}.swf'.format(local_path, file)
    remote = 'http://habboo-a.akamaihd.net/gordon/RELEASE{0}/{1}.swf'.format(version, file)

    print(version, file, local_path, local, remote)

    if not os.path.exists(local_path):
        raise Exception('Fuck off, this is our cache.')

    if not os.path.isfile(local):
        print('acquiring', remote, local)
        print(req.urlretrieve(remote, local))

    return send_file(local)


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


def external_url_handler(error, endpoint, **values):
    """Looks up an external URL when `url_for` cannot build a URL."""
    # lol jk, I don't give a fuck
    try:
        print(endpoint, values)
    except:
        pass


DatabaseHelper.setup_db()

app.url_build_error_handlers.clear()
app.url_build_error_handlers.append(external_url_handler)

if __name__ == '__main__':
    app.run()