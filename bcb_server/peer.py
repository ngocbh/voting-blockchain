from block import Block
from blockchain import Blockchain
from utils import get_ip

from flask import Flask, request

import json
import requests
import time


app = Flask(__name__)

# define server IP
ordererIP = '0.0.0.0'
ordererPort = '5002'
caIP = '0.0.0.0'
caPort = '5001'

# the node's copy of blockchain
blockchain = Blockchain()

# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invlaid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    # make sure we've the longest chain
    global blockchain
    
    url = 'http://{}/consensus'.format(ordererIP + ':' + ordererPort)
    response = requests.get(url)

    length = response.json()['length']
    chain = response.json()['chain']
    longest_chain = Blockchain.fromList(chain)

    if len(blockchain.chain) < length and blockchain.check_chain_validity(longest_chain.chain):
        blockchain = longest_chain

    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

# get local chain for running consensus
@app.route('/local_chain', methods=['GET'])
def get_local_chain():
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    """
    This function serves as an interface to add the pending
    transactions to the blockchain by adding them to the block
    and figuring out Proof Of Work.
    """
    if not blockchain.unconfirmed_transactions:
        return False

    last_block = blockchain.last_block

    new_block = Block(index=last_block.index + 1,
                      transactions=blockchain.unconfirmed_transactions,
                      timestamp=time.time(),
                      previous_hash=last_block.hash)

    proof = blockchain.proof_of_work(new_block)
    blockchain.add_block(new_block, proof)

    blockchain.unconfirmed_transactions = []
    # announce it to the network
    url = 'http://{}/broadcast_block'.format(ordererIP + ':' + ordererPort)
    response = requests.post(url, json=new_block.__dict__)

    result = new_block.index

    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()

    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def join_to_network(orderer, ca, me):

    url = 'http://{}/add_node'.format(ca)
    response = requests.post(url, json={'ipaddress' : me})
    print(response)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-c', '--ca', default='0.0.0.0', type=str, help='port to listen on')
    parser.add_argument('-o', '--orderer', default='0.0.0.0', type=str, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    caIP = args.ca
    ordererIP = args.orderer
    myIP = get_ip()

    join_to_network(ordererIP + ':' + ordererPort, caIP + ':' + caPort, myIP + ':' + str(port))

    app.run(host='0.0.0.0', port=port, debug = True, threaded = True)

