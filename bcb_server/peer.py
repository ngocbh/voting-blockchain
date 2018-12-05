from block import Block
from blockchain import Blockchain
from utils import get_ip

from flask import Flask, request, jsonify

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

# for validate transaction and return to user. like account in ethereum
open_surveys = {}

# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["type", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    url = 'http://{}/broadcast_transaction'.format(ordererIP + ':' + ordererPort)
    response = requests.post(url, json=tx_data)

    return "Success", 201

# endpoint to get a new transaction from another node. 
@app.route('/get_transaction', methods=['POST'])
def get_transaction():
    tx_data = request.get_json()
    required_fields = ["type", "content", "timestamp"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    blockchain.add_new_transaction(tx_data)

    return "Success", 201

# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/open_surveys', methods=['GET'])
def get_open_surveys():
    # make sure we've the longest chain
    global blockchain
    global open_surveys
    
    url = 'http://{}/consensus'.format(ordererIP + ':' + ordererPort)
    response = requests.get(url)

    length = response.json()['length']
    chain = response.json()['chain']
    longest_chain = Blockchain.fromList(chain)

    if len(blockchain.chain) < length and blockchain.check_chain_validity(longest_chain.chain):
        

        # recompute open_surveys
        open_surveys = {}

        for block in longest_chain.chain:
            if not compute_open_surveys(block,open_surveys):
                return "Invalid Blockchain", 400

        blockchain = longest_chain

    surveys = []
    for _ , survey in open_surveys.items():
        surveys.append(survey)

    return jsonify({"length": len(open_surveys),
                       "surveys": list(surveys)})


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    # make sure we've the longest chain
    global blockchain
    global open_surveys
    
    url = 'http://{}/consensus'.format(ordererIP + ':' + ordererPort)
    response = requests.get(url)

    length = response.json()['length']
    chain = response.json()['chain']
    longest_chain = Blockchain.fromList(chain)

    if len(blockchain.chain) < length and blockchain.check_chain_validity(longest_chain.chain):
        # recompute open_surveys
        open_surveys = {}

        for block in longest_chain.chain:
            if not compute_open_surveys(block,open_surveys):
                return "Invalid Blockchain", 400

        blockchain = longest_chain

    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return jsonify({"length": len(chain_data),
                       "chain": chain_data})

# get local chain for running consensus
@app.route('/local_chain', methods=['GET'])
def get_local_chain():
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return jsonify({"length": len(chain_data),
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
        return "None transactions"

    last_block = blockchain.last_block

    new_block = Block(index=last_block.index + 1,
                      transactions=[],
                      timestamp=time.time(),
                      previous_hash=last_block.hash)

    for transaction in blockchain.unconfirmed_transactions:
        #validate_transaction
        if not validate_transaction(transaction):
            continue

        new_block.transactions.append(transaction)

    if ( len(new_block.transactions) == 0 ):
        return "None transactions"

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
    global open_surveys

    block_data = request.get_json()

    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    tmp_open_surveys = open_surveys

    if not compute_open_surveys(block, tmp_open_surveys):
        return "The block was discarded by the node", 400

    open_surveys = tmp_open_surveys

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return jsonify(blockchain.unconfirmed_transactions)

@app.route('/list_nodes', methods=['GET','POST'])
def list_node():
    url = 'http://{}/list_nodes'.format(ordererIP + ':' + ordererPort)
    response = requests.get(url)

    data = response.json()

    return jsonify(data)


def validate_transaction(transaction):
    global open_surveys
    #check permission of transaction
    author = transaction['content']['author']
    url = 'http://{}/validate_permission'.format(caIP + ':' + caPort)
    response = requests.post(url,json={'peer' : author, 'action' : transaction['type']})

    if response.json()['decision'] != 'accept':
        return False

    #check validate transaction and compute open_surveys
    questionid = transaction['content']['questionid']

    if transaction['type'].lower() == 'open':
        if questionid in open_surveys:
            return False
        open_surveys[questionid] = transaction['content']
        return True
    elif transaction['type'].lower() == 'close':
        if questionid in open_surveys and open_surveys[questionid]['author'] == transaction['content']['author']:
            del open_surveys[questionid]
            return True
        return False
    elif transaction['type'].lower() == 'vote':
        if questionid in open_surveys:
            vote = transaction['content']['vote']
            author = transaction['content']['author']
            if author not in open_surveys[questionid]['answers'][vote]:
                open_surveys[questionid]['answers'][vote].append(author)
                return True
            return False


def compute_open_surveys(block, open_surveys):
    for transaction in block.transactions:
        author = transaction['content']['author']
        url = 'http://{}/validate_permission'.format(caIP + ':' + caPort)
        response = requests.post(url,json={'peer' : author, 'action' : transaction['type']})

        if response.json()['decision'] != 'accept':
            return False

        #check validate transaction and compute open_surveys
        questionid = transaction['content']['questionid']

        if transaction['type'].lower() == 'open':
            if questionid in open_surveys:
                return False
            open_surveys[questionid] = transaction['content']
        elif transaction['type'].lower() == 'close':
            if questionid in open_surveys and open_surveys[questionid]['author'] == transaction['content']['author']:
                del open_surveys[questionid]
            return False
        elif transaction['type'].lower() == 'vote':
            if questionid in open_surveys:
                vote = transaction['content']['vote']
                author = transaction['content']['author']
                if author not in open_surveys[questionid]['answers'][vote]:
                    open_surveys[questionid]['answers'][vote].append(author)
                return False

    return True

# ask ca server to join network
def join_to_network(orderer, ca, me):
    url = 'http://{}/add_node'.format(ca)

    response = requests.post(url, json={'ipaddress' : me})
    print(response)


if __name__ == '__main__':
    from argparse import ArgumentParser

    myIP = get_ip()
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-c', '--ca', default=myIP, type=str, help='port to listen on')
    parser.add_argument('-o', '--orderer', default=myIP, type=str, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    caIP = args.ca
    ordererIP = args.orderer
    

    join_to_network(ordererIP + ':' + ordererPort, caIP + ':' + caPort, myIP + ':' + str(port))

    app.run(host=myIP, port=port, debug = True, threaded = True)

