# For timestamp
import datetime

#for creating private key
from ecdsa import SigningKey, SECP256k1,SECP112r1

from .models import Users
from django.contrib.auth.models import User



# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To create uid for nodes
import uuid

# To store data
# in our blockchain
import json



class Blockchain:


    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain = []
    
     
    # This function is created
    # to add further blocks
    # into the chain
    def create_block(self,timestamp,index, block_data,block_hash,proof_of_work,previous_block_hash,transaction):
        block = {
                'timestamp': timestamp,
                'index' : index,
                'block_data':block_data,
                'block_hash': block_hash,
                'proof_of_work':proof_of_work, #data to be stored
                'previous_block_hash':previous_block_hash,
                'transaction':transaction,
        }
      
        self.chain.append(block)
        return block
    
    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest() #A mathmatical operation for mining
            # .encode(): Converts the string into bytes using UTF-8 encoding.
            # hashlib.sha256(...): Creates a new SHA-256 hash object from the hashlib module in Python. SHA-256 is a cryptographic 
            # hash function that takes an input and produces a 256-bit (32-byte) hexadecimal number.
            # .hexdigest(): This method is called on the hash object and returns the hexadecimal representation of the hash.
            #  It converts the binary hash value into a human-readable string of hexadecimal digits.

            if hash_operation[:5] == '00000': #check whether first five digit is 0
                check_proof = True
            else:
                new_proof += 1
 
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        # json.dumps(block, sort_keys=True): This part uses the json.dumps function from the json module to serialize the Python object block 
        # into a JSON-formatted string. The sort_keys=True parameter is used to ensure that the keys in the JSON string are sorted alphabetically

        return hashlib.sha256(encoded_block).hexdigest()
        
    def create_private_key(self):
        # Step 1: Choose Elliptic Curve
        curve = SECP256k1

        # Step 2: Choose a Base Point (G) - Included in the curve parameters
        base_point = curve.generator

        # Step 3: Select a Private Key
        private_key = SigningKey.generate(curve=curve)

        # Step 4: Calculate the Public Key
        public_key = private_key.get_verifying_key()

        # Step 5: Print Private and Public Keys
        # print(f"Private Key: {private_key.to_string().hex()}")
        # print(f"Public Key: {public_key.to_string().hex()}")
        # print(f"Base Point (G): {base_point.x().to_bytes(32, 'big').hex()}, {base_point.y().to_bytes(32, 'big').hex()}")
        return private_key
    
    # Create private hash to identify nodes
    def create_node_ID(self,username):
        print(93927)
        namespace_uuid = uuid.UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
        node_ID  = str(uuid.uuid3(namespace_uuid,username))
        print(node_ID)
        return node_ID

        

    
    
        
    
    
    
    
        
    
        
    

