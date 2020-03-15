# A Simple Blockchain-based Voting System

A simple  blockchain-based voting system application built from scratch by Python. It's available for running with multipeer.
You can see [video demo](https://www.youtube.com/watch?v=CqNoDjuf6EE), or tutorials [part 1](https://medium.com/datadriveninvestor/build-a-blockchain-application-from-scratch-in-python-understanding-blockchain-1a6f1592e42a), [part 2(not ready now)]().

## How it looks

![alt tag](https://raw.githubusercontent.com/ngocjr7/voting-blockchain/master/docs/sample.png)


#### How to use
-> Note: At the first run, click **Update Chaincode** and **Mine** to init chaincode (I wrote a simple chaincode ```count_down_opening_time``` to auto close survey after a period of time) before using.

* Mine : mine unconfirmed transaction
* Resync : Reload front-end
* Update Chaincode : Load smart contract from chaincode.py in vosy_app to blockchain transaction
* Pending Transaction : List unconfirmed transaction
* List Node : List node in the network

## Instructions to run

This project can run separately by [python](https://github.com/ngocjr7/voting-blockchain#running-by-python-command) or use [docker-compose](https://github.com/ngocjr7/voting-blockchain#running-by-docker-compose)

### Running by Docker-compose
-> NOTE: Only available for linux user. If you have any problem with request ip address, try to uncomment `network_mode: "host"` in `docker-compose.yml`.

#### Prerequisites

You need to install `docker` and `docker-compose` before

#### Running

###### In first machine 

Follow this command:

```
docker-compose build
docker-compose up
```

You can run in background:
```
docker-compose up -d
```
You can stop this application:
```
docker-compose stop
```
Or down ( delete container ): 
```
docker-compose down
```

###### In second machine
You have to provide IP address of machine 1 in `.env` file. For example:

```
ORDERER_IP=192.168.43.162
CA_IP=192.168.43.162
PEER_IP=192.168.43.162
```

Then run command

```
docker-compose -f docker-compose-peer-only.yml build
docker-compose -f docker-compose-peer-only.yml up
```

### Running by Python command

#### Prerequisites

It needs `python`, `pip` to run. Install requirements 

```
pip install -r requirements.txt
```

#### Running

###### In first machine
You need to run 4 app `orderer.py` `certificate_authority.py` `peer.py` `vosy.py` ( if you don't need front-end in this machine, you don't need to run `vosy.py`) . You can run each app on different machines but need to provide ip address for it. 

```
python bcb_server/orderer.py
```

Certificate authority need to know aleast 1 orderer. so if is not default value `0.0.0.0`, you need to pass orderer ip address to certificate_authority by argument `--orderer`
```
python bcb_server/certificate_authority.py
```

Peer need to know aleast 1 orderer and 1 certificate_authority so you need to pass orderer ip address and ca ip address to peer by argument `--orderer` and `--ca`
```
python bcb_server/peer.py
```

Vosy need to know aleast 1 peer so you need to pass peer ip address to vosy app by argument `--host`
```
python vosy_app/vosy.py
```

##### for example, with window users, ip address `0.0.0.0` is not available, so you need to run in `127.0.0.1` instead, so you have to follow this command in 4 cmd:

```
python bcb_server/orderer.py
```
```
python bcb_server/certificate_authority.py --orderer 127.0.0.1
```
```
python bcb_server/peer.py --orderer 127.0.0.1 --ca 127.0.0.1
```
```
python vosy_app/vosy.py --host 127.0.0.1
```

###### In second machine
You just need to run `peer.py` and `vosy.py` but you need to provide Lan IP address `orderer.py` and `certificate_authority.py` run in machine 1. In my case, it is `192.168.43.162`

```
python bcb_server/peer.py --orderer 192.168.43.162 --ca 192.168.43.162
```

```
python vosy_app/vosy.py
```

this vosy will auto connect to local peer in address `0.0.0.0:5000`

## Tutorial

You can see [video demo](https://www.youtube.com/watch?v=CqNoDjuf6EE), or tutorials [part 1](https://medium.com/datadriveninvestor/build-a-blockchain-application-from-scratch-in-python-understanding-blockchain-1a6f1592e42a), [part 2(not ready now)]().

It is simple architecture of my network

![alt tag](https://raw.githubusercontent.com/ngocjr7/voting-blockchain/master/docs/architecture.png)

![alt tag](https://raw.githubusercontent.com/ngocjr7/voting-blockchain/master/docs/network_sample.png)


#### Certificate Authority

It can validate connection when a node ask to join to network and Set permission for each node and validate transaction

#### Orderer

It can hold a list of peers and broadcast to all peer when receive a request broadcast new block or new transaction.
It also have consensus method, which can return the longest blockchain in the network

#### Peer

It hold all data about blockchain, it have some method like mine, validate_transaction, return chain, open surveys, ...

#### Vosy

A blockchain-based application for voting system
