class Client : 
    def __init__(self,client_socket,client_address,client_name):
        self._client_name = client_name
        self._client_socket= client_socket
        self._client_address= client_address 
    @property 
    def client_name(self):
        return self._client_name
    @client_name.setter 
    def client_name(self,value):
        self._client_name = value 

class Clients():
    def __init__(self):
        self.client_list = []
    def add_client(self,client:Client) : 
        self.client_list.append(client)        
    def remove_client(self,client:Client):
        self.client_list.remove(client)
    def clients_number(self):
        return len(self.client_list)