from block import Block
from blockchain import Blockchain

from flask import Flask, request, jsonify
from utils import get_ip

import json
import requests

app = Flask(__name__)


# the address to other participating members of the network
peers = set()

# endpoint to add new peers to the network.
@app.route('/add_node', methods=['POST'])
def register_new_peers():
    data = request.get_json()

    if not data:
        return 'Invalid data' , 400

    request_addr = data['ipaddress']
    port = data['port']
    node = request_addr + ':' + str(port)

    if not node:
        return "Invalid data", 400

    peers.add(node)

    return "Success", 201

@app.route('/broadcast_block', methods=['POST'])
def announce_new_block():
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    block = Block.fromDict(request.get_json())
    if not block:
    	return "Invalid data at announce_new_block", 400

    request_addr = request.remote_addr

    offline_node = []

    for peer in peers:
        try:
            if peer.find(request_addr) != -1:
                continue
            url = "http://{}/add_block".format(peer)
            requests.post(url, json=block.__dict__)
        except requests.exceptions.ConnectionError:
            print('Cant connect to node {}. Remove it from peers list'.format(peer))
            offline_node.append(peer)

    for peer in offline_node:
        peers.remove(peer)

    return "Success", 201

@app.route('/broadcast_transaction', methods=['POST'])
def announce_new_transaction():
    """
    A function to announce to the network once a transaction has been added.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    data = request.get_json()
    if not data:
        return "Invalid data at announce_new_block", 400

    request_addr = request.remote_addr

    offline_node = []

    for peer in peers:
        try:
            if peer.find(request_addr) != -1:
                continue
            url = "http://{}/get_transaction".format(peer)
            requests.post(url, json=data)
        except requests.exceptions.ConnectionError:
            print('Cant connect to node {}. Remove it from peers list'.format(peer))
            offline_node.append(peer)

    for peer in offline_node:
        peers.remove(peer)

    return "Success", 201

@app.route('/consensus', methods=['GET'])
def consensus():
    """
    Our simple consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    longest_chain = Blockchain()
    current_len = len(longest_chain.chain)
    
    offline_node = []
    
    for peer in peers:
        try:
            response = requests.get('http://{}/local_chain'.format(peer))
            length = response.json()['length']
            chain = response.json()['chain']
            new_blockchain = Blockchain.fromList(chain)

            if length > current_len and longest_chain.check_chain_validity(new_blockchain.chain):
                current_len = length
                longest_chain = new_blockchain
        except requests.exceptions.ConnectionError:
            print('Cant connect to node {}. Remove it from peers list'.format(peer))
            offline_node.append(peer)

    for peer in offline_node:
        peers.remove(peer)
    
    chain_data = []

    for block in longest_chain.chain:
        chain_data.append(block.__dict__)

    return jsonify({"length": len(chain_data),
                       "chain": chain_data})

#get current list of nodes in the network
@app.route('/list_nodes', methods=['GET','POST'])
def get_node():
    result = {
        'Nodes in System' : list(peers),
        'Count of Nodes' : len(peers)
    }
    return jsonify(result)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5002, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    print('My ip address : ' + get_ip())

    app.run(host='0.0.0.0', port=port, debug = True, threaded = True)

