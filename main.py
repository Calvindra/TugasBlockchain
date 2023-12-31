
# import libraries 
import datetime 
import hashlib
import json
from flask import Flask, jsonify, request

# 1. create the blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        # genesis block 
        self.create_block(proof=1, prev_hash='0', hash_operation='0')

    def create_block(self, proof, prev_hash, hash_operation, data= None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            'hash_operation': hash_operation,
            'data': data
        }
        block['hash'] = self.hash(block) #2. Menyimpan hash ke dalam block 
        self.chain.append(block) 
        return block
    
    # def modify

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        hash_operation = hashlib.sha256(encoded_block).hexdigest()
        return hash_operation

    def is_chain_valid(self, chain):
        # init
        prev_block = chain[0]
        block_index = 1
        # loop 
        while block_index < len(chain):
            block = chain[block_index]
            # check if current prev hash has same hash with prev_block hash 
            if block['prev_hash'] != self.hash(prev_block):
                return False
            # check if the hash of the block has four leading zeros 
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            # update loop
            prev_block = block
            block_index += 1
        return True
    
    def modify_block_data(self, block_index, new_data):  # Added a method to modify block data
        if block_index < len(self.chain):
            self.chain[block_index]['data'] = new_data

# 2. mining our blockchain

app = Flask(__name__)

blockchain = Blockchain()

#endpoint
@app.route("/get_chain", methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# define route 
@app.route('/mine_block', methods=['GET'])
def mine_block():
    # get proof 
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof, hash_operation = blockchain.proof_of_work(prev_proof)
    # get prev hash 
    prev_hash = blockchain.hash(prev_block)
    # create block 
    block = blockchain.create_block(proof, prev_hash, hash_operation)
    # response message 
    response = {
        'message': 'Congratulation you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'prev_hash': block['prev_hash'],
        'hash_operation': block['hash_operation']
    }
    return jsonify(response), 200

# @app.route('/get_chain', methods=['GET'])
# def get_chain():
#     response = {
#         'length': len(blockchain.chain),
#         'chain': blockchain.chain
#     }
#     return jsonify(response), 200

#3. Menambahkan data di dalam block 
@app.route("/create", methods=['POST'])
def create_block():
    data = request.form

    prev_block = blockchain.get_prev_block()
    # get prev proof 
    prev_proof = prev_block['proof']
    proof, hash_operation = blockchain.proof_of_work(prev_proof) 
    # get prev hash 
    prev_hash = blockchain.hash(prev_block)
    # create block 
    created_block = blockchain.create_block(proof, prev_hash, hash_operation, data['data'])
    response = {
        'message': "Blockchain is successfully created",
        'created block': created_block
    }
    return jsonify(response), 200


# 1. buatkan endpoint yang mengecek apakah chainnya valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Blockchain Valid!'}
    else:
        response = {'message': 'Maaf, tidak valid'}
    return jsonify(response), 200


@app.route('/modify_block_and_invalidate', methods=['POST'])
def modify_block_and_invalidate():
    data = request.get_json()
    block_index = data.get('block_index')
    new_data = data.get('new_data')

    if block_index is None or new_data is None:
        return jsonify({'message': 'Invalid request. Please provide block_index and new_data.'}), 400

    blockchain.modify_block_data(block_index, new_data)

    response = {
        'message': f'Data in block {block_index} has been modified, making the chain invalid.',
        'new_data': new_data,
    }
    return jsonify(response), 200


# run the app 
app.run(host='0.0.0.0', port=5000)

# tugas 
# 1. buatkan endpoint yang mengecek apakah chainnya valid
# 2. simpan hash dalam blocknya
# 3. tambah data di dalam block 
# 4. fungsi dan endpoint yang mensimulasikan adanya modifikasi di dalam block, sehingga chainnya tdk valid
