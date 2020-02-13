import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "current_proof": proof,
            "previous_hash": previous_hash
        }


        # Reset the current list of transactions
        # Append the chain to the block
        # Return the new block

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1


    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string

        block_string = json.dumps(block, sort_keys=True)
        encoded_string = block_string.encode()

        # TODO: Hash this string using sha256

        hashed_block = hashlib.sha256(encoded_string)
        hexa_hash = hashed_block.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hexa_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof
        :return: A valid proof for the provided block
        """
        # TODO
        block_string = json.dumps(block, sort_keys=True)
        proof = 0
        while self.valid_proof(block_string, proof) is False:
            proof += 1

        return proof

    # @staticmethod
    # def valid_proof(block_string, proof):
    #     """
    #     Validates the Proof:  Does hash(block_string, proof) contain 3
    #     leading zeroes?  Return true if the proof is valid
    #     :param block_string: <string> The stringified block to use to
    #     check in combination with `proof`
    #     :param proof: <int?> The value that when combined with the
    #     stringified previous block results in a hash that has the
    #     correct number of leading zeroes.
    #     :return: True if the resulting hash is a valid proof, False otherwise
    #     """
    #     # TODO
        
    #     guess = f'{block_string}{proof}'.encode()
    #     guess_hash = hashlib.sha256(guess).hexdigest()

    #     # return True or False
    #     return guess_hash[:3] == '000'



# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()
print(blockchain.chain)

@app.route('/transaction/new', methods=['POST'])
def receive_new_transaction():
    #     * use `request.get_json()` to pull the data out of the POST
    # * check that 'sender', 'recipient', and 'amount' are present
    #     * return a 400 error using `jsonify(response)` with a 'message'
    # * upon success, return a 'message' indicating index of the block
    #   containing the transaction
    data = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in data for k in required):
        # TODO Better error messaging
        return "Missing values", 400
    index = blockchain.new_transaction(data['sender'],
                                       data['recipient'],
                                       data['amount'])

    response = {'message': f'Transactions will be included in block {index}'}

    return jsonify(response), 200



@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof of work algorithm to get the next proof
    proof = blockchain.proof_of_work(blockchain.last_block)
    # Forge the new Block by adding it to the chain with the proof
    previous_hash = blockchain.hash(blockchain.last_block)
    new_block = blockchain.new_block(proof, previous_hash)

    response = {
        "block": new_block
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000)
