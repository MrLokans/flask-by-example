from collections import Counter
import json
import operator
import os
import re

from bs4 import BeautifulSoup
import nltk
import requests
from rq import Queue
from rq.job import Job

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from stop_words import stop_words
from worker import connection

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

queue = Queue(connection=connection)


from models import Result

NON_PUNCTUATION = re.compile('.*[A-Za-z].*')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'http://' not in url[:7]:
        url = 'http://' + url

    job = queue.enqueue_call(func=count_and_save_words,
                             args=(url, stop_words),
                             result_ttl=5000)
    job_id = job.get_id()
    app.logger.info("Job {} started. ".format(job_id))
    return job_id


def count_and_save_words(url, stop_words):
    errors = []

    try:
        app.logger.info("Requesting page {}".format(url))
        resp = requests.get(url)
    except requests.exceptions.InvalidURL:
        # TODO: sanitize user input
        app.logger.exception('Invalid URL supplied: {}.'.format(url))
        errors.append('Invalid URL supplied')
        return {'errors': errors}
    except requests.exceptions.ConnectionError:
        app.logger.exception('Inexistent host supplied: {}.'.format(url))
        errors.append('Probably host does not exist.')
        return {'errors': errors}
    except:
        app.logger.exception('Unknown error scraping website: {}.'
                             .format(url))
        errors.append('Invalid URL supplied')
        return {'errors': errors}
    raw_words, not_stop_words = parse_page(resp, stop_words)
    app.logger.info("Page parsed.")
    try:
        result = Result(
            url=url,
            result_all=raw_words,
            result_no_stop_words=not_stop_words
        )
        db.session.add(result)
        db.session.commit()
        app.logger.info("Result saved to the database: id={}"
                        .format(result.id))
        return result.id
    except:
        app.logger.exception('Error loading result into the database.')
        errors.append('Unable to add item to the database')
        return {'errors': errors}


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


@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    app.logger.info("Requesting JobID={}".format(job_key))
    job = Job.fetch(job_key, connection=connection)

    if job.is_finished:
        result = job.result
        app.logger.info("Job found, result: {}".format(result))
        if isinstance(result, dict) and 'errors' in result:
            return jsonify(result), 400
        result = Result.query.filter_by(id=result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:10]

        results = jsonify(results)
        return results, 200
    else:
        return "Job is not ready yet", 202


if __name__ == '__main__':
    app.run()
