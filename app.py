import os

import requests

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from models import Result


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        try:
            url = request.form['url']
            r = requests.get(url)
        except KeyError:
            app.logger.warn("Error reading URL from request form.")
            errors.append('No URL submitted')
        except requests.exceptions.InvalidURL:
            # TODO: sanitize user input
            app.logger.exception("Invalid URL supplied: {}.".format(url))
            errors.append('Invalid URL supplied')
        except requests.exceptions.ConnectionError:
            app.logger.exception("Inexistent host supplied: {}.".format(url))
            errors.append('Probably host does not exist.')
        except:
            app.logger.exception("Unknown error scraping website: {}."
                                 .format(url))
            errors.append('Invalid URL supplied')
    return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    app.run()
