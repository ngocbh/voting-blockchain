from flask import Flask
from flask import render_template, redirect, request, jsonify

from utils import get_ip

import datetime, time
import json

import requests

app = Flask(__name__)

@app.context_processor
def my_utility_processor():

    def len_list(li):
        return len(li)

    return dict(len=len_list)


# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://0.0.0.0:5000"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/open_surveys".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        data = json.loads(response.content)
        surveys = data['surveys']

        global posts
        posts = sorted(surveys, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='A Simple Blockchain based Voting System',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/mine', methods=['GET','POST'])
def mine():
    
    url = '{}/mine'.format(CONNECTED_NODE_ADDRESS)
    response = requests.get(url)

    data = response.json()['response']
    return data

@app.route('/pending_tx', methods=['GET','POST'])
def get_pending_tx():

    url = '{}/pending_tx'.format(CONNECTED_NODE_ADDRESS)
    response = requests.get(url)

    data = response.json()

    return jsonify(data)

@app.route('/list_nodes', methods=['GET','POST'])
def get_list_nodes():

    url = '{}/list_nodes'.format(CONNECTED_NODE_ADDRESS)
    response = requests.get(url)

    data = response.json()

    return jsonify(data)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """

    author = get_ip(request.remote_addr)
    questionid = request.form["questionid"]
    question = request.form["question"]
    answersList = request.form["answer"].split('|')
    answers = {}

    for answer in answersList:
        answers[answer] = []

    post_object = {
        'type' : 'open',
        'content' : {
            'questionid': questionid,
            'question': question,
            'answers': answers,
            'author': author + ':5000',
            'timestamp': time.time()
        }
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')

@app.route('/close_survey', methods=['GET','POST'])
def close_survey():
    """
    Endpoint to create a new transaction via our application.
    """

    author = get_ip(request.remote_addr)
    questionid = request.args.get('id')

    post_object = {
        'type' : 'close',
        'content' : {
            'questionid': questionid,
            'author': author + ':5000',
            'timestamp': time.time()
        }
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')

@app.route('/vote', methods=['GET','POST'])
def vote():
    """
    Endpoint to create a new transaction via our application.
    """

    author = get_ip(request.remote_addr)
    questionid = request.args.get('id')
    answer = request.args.get('answer')

    post_object = {
        'type' : 'vote',
        'content' : {
            'questionid': questionid,
            'author': author + ':5000',
            'vote': answer,
            'timestamp': time.time()
        }
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


if __name__ == '__main__':
    from argparse import ArgumentParser

    myIP = get_ip()
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    parser.add_argument('--host', default='0.0.0.0', type=str, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    CONNECTED_NODE_ADDRESS = 'http://{}:5000'.format(args.host)

    print('My ip address : ' + get_ip())
    
    app.run(host='0.0.0.0', port=port, debug = True, threaded = True)

