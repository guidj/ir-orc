import os
import json
import flask
import requests
from werkzeug.utils import secure_filename
from irocr.meta import censure
from irocr import config

UPLOAD_FOLDER = '/root/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


class SolrConfig(object):
    def __init__(self):
        cfg = config.get('solr')
        if not cfg:
            raise RuntimeError('Solr config not found')
        assert 'host' in cfg
        assert 'port' in cfg
        self.host = cfg['host']
        self.port = cfg['port']


solar_config = SolrConfig()

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def query_by_image():
    if flask.request.method == 'POST':
        file = flask.request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fullpath)
            keypoints = censure(fullpath)

            url = 'http://{}:{}/solr/{}/query'.format(
                solar_config.host,
                solar_config.port,
                'photos'
            )
            # ?echoParams=none

            json_query = {'filter': [], 'query': 'exif.*'}
            for x, y in keypoints:
                json_query['filter'].append('keypoints.x:' + str(x))
                json_query['filter'].append('keypoints.y:' + str(y))

            response = requests.post(url, data=json.dumps(json_query), headers={'Content-type': 'application/json'})
            return flask.jsonify(response.json())

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Search by image</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Search>
    </form>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0')
