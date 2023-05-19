import socket
import threading
from rsa_alg import *
import pickle

def handle_client(sock, address, clients, client_public_keys):
    # Add the client to the list of clients
    clients.append(sock)

    # Receive messages from the client and broadcast them to other clients
    while True:
        data = sock.recv(1024)
        if not data:
            clients.remove(sock)
            sock.close()
            break
        try:
            request = pickle.loads(data)
            if request['action'] == 'get_public_key':
                recipient_user_name = request['user_name']
                if recipient_user_name in client_public_keys:
                    sock.send(pickle.dumps(client_public_keys[recipient_user_name]))
                else:
                    sock.send(pickle.dumps(None))
            else:
                for client in clients:
                    if client != sock:
                        client.send(data)
        except:
            for client in clients:
                if client != sock:
                    client.send(data)

def start_server(address):
    # Create a socket and start listening for connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(address)
    sock.listen()
    print("listening at ", address)
    # Create lists to store the connected clients and their public keys
    clients = []
    client_public_keys = {}

    # Start a thread to accept new connections
    def accept_connections():
        while True:
            client_sock, client_address = sock.accept()
            print('New client joined:', client_address)
            # Receive the client's public key and store it
            data_recv = client_sock.recv(1024)
            data = pickle.loads(data_recv)
            public_key = data[0]
            user_name = data[1]

            client_public_keys[user_name] = public_key
            print('public key', client_public_keys)

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_sock, client_address, clients, client_public_keys))
            client_thread.start()

    accept_thread = threading.Thread(target=accept_connections)
    accept_thread.start()

if __name__ == '__main__':
    start_server(('192.168.239.51', 8080))