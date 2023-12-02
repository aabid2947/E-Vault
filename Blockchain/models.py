from django.db import models
import json

# Create your models here.

class Blockchain_database(models.Model):
    timestamp = models.CharField(max_length=10000)
    index = models.IntegerField()
    block_data = models.TextField() #to store dictionary
    block_hash = models.CharField(max_length=100)
    proof_of_work = models.CharField(max_length=100)
    previous_block_hash = models.CharField(max_length=100)
    transaction = models.JSONField(null=True, blank=True)
    

    def __str__(self):
        return f'Block : {str(self.index)}'


    def get_block(self,block_hash):
        try:
            # Retrieve the stored block using the block_hash
            block = Blockchain_database.objects.get(block_hash=block_hash)
            return (block)
        except Blockchain_database.DoesNotExist:
            return None
        
    def get_previous_block_hash(self,index):
       try:
            # Retrieve the stored block with an index one less than the current block
            previous_block =  Blockchain_database.objects.filter(index__icontains=index)
            return previous_block[0].block_hash
       except Blockchain_database.DoesNotExist:
            return None
        
    class Meta:
        db_table = 'block'

class Users(models.Model):
    username = models.CharField( max_length=50)
    private_key = models.CharField(max_length=100)
    amount = models.IntegerField(max_length=10000)
    block_hashes = models.JSONField(null=True, blank=True) #to store block created using user private key
    file_name = models.JSONField(null=True, blank=True) #to store file name 

    
    def __str__(self):
        return self.username
    
    
    class Meta:
        db_table = 'users'

class Nodes(models.Model):
    node_name = models.CharField(max_length=20)
    node_ID = models.CharField(max_length=40)
    blockchain_copy = models.JSONField(null=True, blank=True)
    Email = models.CharField(max_length=20)

    def __str__(self):
        return self.node_name
    
    class Meta:
        db_table = 'nodes'


    

