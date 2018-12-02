from block import Block
from blockchain import Blockchain

from flask import Flask, request

import requests

app = Flask(__name__)

orderer = 'http://0.0.0.0:5002'

@app.route('/add_node', methods=['GET','POST'])
def validate_connection():

	data = request.get_json()

	if not data:
		return 'Invalid data' , 400

	node = data['ipaddress']
	# add some role with node in here
	url = '{}/add_node'.format(orderer)
	response = requests.post(url,json=data)

	return "Success", 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port, debug = True, threaded = True)