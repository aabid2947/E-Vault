from django.shortcuts import render,redirect
from .Blockchain import *
from django.http import HttpResponse
import base64

# for authenticating user
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout

# for compressing and decompressing
import gzip
from io import BytesIO

# database to store block
from .models import *

# Create your views here.

# instance of blockchain
blockchain = Blockchain()

# instance of blockchain model
blockchain_database = Blockchain_database()

# instance of Nodes model
node = Nodes()





# to compress file
def compress_file(content):
    with BytesIO() as buffer:
        with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
            f.write(content)
        return buffer.getvalue()

# to decompress file
def decompress_file(content):
    with BytesIO(content) as buffer:
        with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
            return f.read()

def Home(request):
    return render(request,'Home.html')

# Handling user signUp
def sign_Up(request):
    if(request.method == "POST"):
        if request.POST['password'] != request.POST['confirm_password']:
            return HttpResponse('Password and confirm Password deos not match') 
        else:
            username = request.POST['username']
            password = request.POST['password']
            name = request.POST['fname']
            email = request.POST['email']

            # creating private key for e-vault
            private_key = blockchain.create_private_key().to_string().hex()
            
            # Handle creation of node
            if request.POST['sign_up_asnode'] == 'yes':
                new_node = create_node(username,email)
                if type(new_node) == str:
                    return HttpResponse(new_node)
            
            # create a user in django
            myuser = User.objects.create_user(username,email,password)
            myuser.first_name = name
            myuser.save()

            # creating the user for blockchain
            new_user = Users(username=username,private_key=private_key,amount= 10)
            new_user.save() #saving in local model

            messages.success(request,'Account created successfully')
            return redirect('Home')  
        
    else:
        return HttpResponse('404:Not found')

# Handling user signIN
def logIn(request):
    if(request.method == "POST"):
        # get the param
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('vault_blockchain')
        else:
            messages.success(request,'User not found')
            return redirect('home')

    else:
        return HttpResponse('Please LogIn')
    

# Handle logout
def logOut(request):
        logout(request)
        messages.success(request,'Successfully Logged Out')
        return redirect('Home')

# Creating node to handle blockchain
def create_node(username,email):
    try:
        blockchain = Blockchain()
        node_ID = blockchain.create_node_ID(username=username)
        new_node = Nodes(
                         node_name=username,
                         node_ID=node_ID,
                         Email=email,
                         blockchain_copy=[]
                         )
        
        # providing every block to node
        blockchain_copy =Blockchain_database.objects.all()
        print(blockchain)
        for block in blockchain_copy:
            block_copy = blockchain.create_block(
                                                 timestamp=block.timestamp,
                                                 index=block.index,
                                                 block_data=block.block_data,
                                                 block_hash=block.block_hash,
                                                 proof_of_work=block.proof_of_work,
                                                 previous_block_hash=block.previous_block_hash,
                                                 transaction=block.transaction
                                                 )
        new_node.blockchain_copy.append(block_copy)
        new_node.save()
             
    except Exception as error:
               return f'Error creating node:{error}'

# Handling uploading file on blockchain
def vault_blockchain_view(request):
    # Retrieve the user instance
    user_instance = Users.objects.get(username=request.user)

    if(str(request.user) == 'AnonymousUser'): 
        messages.success(request,'Please login first')
        return redirect('Home')

    elif request.method == 'POST':
        try:
            #get uploaded file in frontend
            uploaded_file = request.FILES['files']

            # Create block 
            block = create_block(uploaded_file=uploaded_file,username=request.user,user_instance=user_instance)  
            if type(block) == str:
                return HttpResponse(f'Error creating block: {block}')
            # storing block in a database
            new_block = Blockchain_database(
                                            timestamp=block['timestamp'],
                                            block_data=block['block_data'],
                                            block_hash=block['block_hash'],
                                            previous_block_hash=block['previous_block_hash'],
                                            index=block['index'],
                                            transaction=block['transaction'],
                                            proof_of_work=block['proof_of_work'])
            
            # sharing a copy of block with every node
            nodes = Nodes.objects.all()
            for node in nodes:
                node.blockchain_copy.append(block)
                node.save()    
            
            # saving changes
            user_instance.save()  

            # saving new block
            new_block.save()
        
            return HttpResponse(f'Successfully uploaded to blockchain. Block hash: {block["hash"]}')
        except Exception as e:
            return HttpResponse(f'Error uploading block: {str(e)}')

    # verify whether user is node or not
    if Nodes.objects.filter(node_name__icontains = request.user):
        isNode = True
    else:
        isNode = False    

    # getting all the files uer has uploaded  to pass as arg to frontend
    files_name = user_instance.file_name
    context = {
        'files_name':files_name,
        'isNode':isNode
    }
    
    return render(request,'vault.html',context)

# Handle creation of block
def create_block(uploaded_file,username,user_instance):
   try:
            #get the name of uploaded file
            file_name = uploaded_file.name

            # read the content of the files
            file_content = uploaded_file.read()
        
            # encode the content
            encoded_content = base64.b64encode(compress_file(file_content)).decode('utf-8')
           
            # get previous block , proof and previous hash
            if Blockchain_database.objects.last() is None:
                previous_block_hash ='0'
                previous_proof = 1
                index = 1
            else:
               previous_block_hash = blockchain_database.get_previous_block_hash(Blockchain_database.objects.last().index)
               previous_block = blockchain_database.get_block(previous_block_hash)
               #verifying previous block
               if verify_block(previous_block.index,previous_block.block_hash) is False: 
                  return 'Block invalid'
               
               previous_proof = previous_block.proof_of_work
               index = Blockchain_database.objects.last().index + 1
            
            # create proof and privatekey
            proof = blockchain.proof_of_work(int(previous_proof))
            
            # Getting the username to update the info
            user = Users.objects.filter(username__icontains=username)
            private_key = user[0].private_key
            amount = user[0].amount
            
            # Checking whether user have sufficient amount or not
            if amount >= 1:
                # create block and store info 
                block  =  blockchain.create_block(
                                                 timestamp=str(datetime.datetime.now()),
                                                 index=index,
                                                 block_data=json.dumps(encoded_content),
                                                 block_hash="",
                                                 proof_of_work=proof,
                                                 previous_block_hash=previous_block_hash,
                                                 transaction=None
                                                 )
            else:
                return ("Not Sufficient Amount")

            # generate and assign hash 
            block_hash = blockchain.hash(block)
            block['hash'] = block_hash

            #adding hash and files to user database
            current_files = user_instance.file_name
            current_hashes = user_instance.block_hashes
            
            # Making hash and file field an array 
            if current_hashes is None:
               current_hashes = []
            if current_files is None:
               current_files = []
            
            # Adding file and hash in array
            current_hashes.append(block_hash)
            current_files.append(file_name)

            # store file name and hash in user database
            user_instance.file_name = current_files
            user_instance.block_hashes = current_hashes
            
            # deduce 1ad
            user_instance.amount = amount -1
        
            
            return block

   except Exception as error:
       return (f"error in uploading files:{error}")  

# Handle user request to get there files
def get_files(request,requested_file):
    if(request.method == 'POST' ):
        try:
            # get the user who request to get his file
            user = Users.objects.filter(username__icontains=request.user)
            for file,_hash in zip(user[0].file_name,user[0].block_hashes):
                if file == requested_file:
                    file_name = file
                    block_hash = _hash              
                    block = blockchain_database.get_block(block_hash)

                    # verifying if block is valid or not 
                    if verify_block(block.index,block.previous_block_hash):
                        block_data = block.block_data

                    if block_data:
                        block_data = json.loads(block_data)
                        # Extract the file content 
                        file_content_base64 = block_data
                        
                        # Decode the base64-encoded file content
                        compressed_file_content = base64.b64decode(file_content_base64)
                        file_content = decompress_file(compressed_file_content)
                        
                        # Set up the response with appropriate headers
                        response = HttpResponse(file_content, content_type='application/octet-stream')
                        response['Content-Disposition'] = f'attachment; filename={file_name}'
                        return response
                    else:
                        return HttpResponse('file not found')
                    
        except Exception as error:
                return HttpResponse(f"error in getting block: {error}")
    else:
        return HttpResponse("Upload Files")
    
# Validate block
def verify_block(index,previous_block_hash):
    if index == 1:
        return True
    else:
        # get block
        previous_block = Blockchain_database.objects.filter(block_hash__icontains = previous_block_hash)
        if previous_block:
            return True
        else:
            return False

# displaying blockchain for nodes
def display_blockchain(request):
    try:
        if Nodes.objects.filter(node_name__icontains = request.user):
            blockchain = Blockchain_database.objects.all()
            return render(request,'display_blocks.html',{'blockchain':blockchain})
        else:
            return HttpResponse("You are not autherize to see blockchain")
    except Exception as error:
       return HttpResponse(f'Error in getting blockchain:{error}')    


    