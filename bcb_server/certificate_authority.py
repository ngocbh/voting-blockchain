from block import Block
from blockchain import Blockchain

from flask import Flask, request, jsonify
from utils import get_ip

import requests

app = Flask(__name__)

orderer = '0.0.0.0'

# the address to other participating members of the network
peers = set()

# list grouped peers
groups = {}
# list permission for each group
# O : Open | C : Close | V : Vote
permission = { 'admin' : 'OCV', 'peer' : 'OCV', 'guest' : 'V' }

groups[get_ip() + ':5000'] = 'admin'


@app.route('/add_node', methods=['GET','POST'])
def validate_connection():

	data = request.get_json()

	if not data:
		return 'Invalid data' , 400

	node = data['ipaddress']

	if not node: 
		return 'Invalid data' , 400

	peers.add(node)
	# add some role with node in here
	# set permission for node 
	groups[node] = 'peer'

	url = 'http://{}:5002/add_node'.format(orderer)
	response = requests.post(url,json=data)

	return "Success", 201


@app.route('/validate_permission', methods=['POST'])
def validate_permission():

	data = request.get_json()
	if not data:
		return 'Invalid data', 400

	node = data["peer"]
	action = data["action"]

	if not node in groups:
		groups[node] = 'guest'

	if permission[groups[node]].find(action[0].upper()) != -1 :
		return jsonify({'decision' : 'accept'})

	return jsonify({'decision' : 'reject'})


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    myIP = get_ip()
    orderer = get_ip()

    app.run(host=myIP, port=port, debug = True, threaded = True)