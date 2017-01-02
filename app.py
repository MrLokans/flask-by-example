from collections import Counter
import operator
import os
import re

from bs4 import BeautifulSoup
import nltk
import requests

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from stop_words import stop_words

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from models import Result

NON_PUNCTUATION = re.compile('.*[A-Za-z].*')


def parse_page(resp, stops):
    text = BeautifulSoup(resp.text, 'html.parser').get_text()
    nltk.data.path.append('./nltk_data/')
    tokens = nltk.word_tokenize(text)
    text = nltk.Text(tokens)

    raw_words = [w for w in text if NON_PUNCTUATION.match(w)]
    raw_word_count = Counter(raw_words)

    not_stop_words = [w for w in raw_words
                      if w.lower() not in stops]
    not_stop_words_count = Counter(not_stop_words)

    return raw_word_count, not_stop_words_count


def get_result_dict(not_stop_words):
    return sorted(not_stop_words.items(),
                  key=operator.itemgetter(1),
                  reverse=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        try:
            url = request.form['url']
            resp = requests.get(url)
        except KeyError:
            app.logger.warn('Error reading URL from request form.')
            errors.append('No URL submitted')
        except requests.exceptions.InvalidURL:
            # TODO: sanitize user input
            app.logger.exception('Invalid URL supplied: {}.'.format(url))
            errors.append('Invalid URL supplied')
        except requests.exceptions.ConnectionError:
            app.logger.exception('Inexistent host supplied: {}.'.format(url))
            errors.append('Probably host does not exist.')
        except:
            app.logger.exception('Unknown error scraping website: {}.'
                                 .format(url))
            errors.append('Invalid URL supplied')
        if resp:
            raw_words, not_stop_words = parse_page(resp, stop_words)
            results = get_result_dict(not_stop_words)
            try:
                result = Result(
                    url=url,
                    result_all=raw_words,
                    result_no_stop_words=not_stop_words
                )
                db.session.add(result)
                db.session.commit()
            except:
                app.logger.exception('Error loading result into the database.')
                errors.append('Unable to add item to the database')
    return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    app.run()
