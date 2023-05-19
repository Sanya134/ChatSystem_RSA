import socket
import threading
from tkinter import *
from rsa_alg import *
import pickle

import time

def receive_message(sock, private_key, chat_window, sender_name):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        start_time = time.time()
        dec_data = b""
        for i in range(0, len(data), 128):
            chunk = data[i:i+128]
            dec_chunk = decrypt(chunk, private_key)
            dec_data += dec_chunk
        dec_data = dec_data.decode('latin-1')
        end_time = time.time()
        dec_time = end_time - start_time
        print(f"Received message from {sender_name}, decrypted in {dec_time:.6f} seconds")
        chat_window.config(state=NORMAL)
        chat_window.insert(END, sender_name + ': ' + dec_data + '\n')
        chat_window.config(state=DISABLED)
        chat_window.see(END)

def send_message(sock, public_key, message_entry, chat_window):
    message = message_entry.get()
    start_time = time.time()
    enc_data = b""
    for i in range(0, len(message), 117):
        chunk = message[i:i+117]
        enc_chunk = encrypt(chunk.encode('latin-1'), public_key)
        enc_data += enc_chunk
    sock.sendall(enc_data)
    end_time = time.time()
    enc_time = end_time - start_time
    print(f"Sent message, encrypted in {enc_time:.6f} seconds")
    chat_window.config(state=NORMAL)
    chat_window.insert(END, 'me' + ': ' + message + '\n')
    chat_window.config(state=DISABLED)
    chat_window.see(END)
    message_entry.delete(0, END)



def join_chat(sock, recipient_username, user_name, private_key, message_entry, chat_window, root, join_button):
    # Hide the "Join" button
    join_button.pack_forget()
    global recipient_public_key
    # Request the recipient's public key from the server
    sock.send(pickle.dumps({'action': 'get_public_key', 'user_name': recipient_username}))
    response = sock.recv(1024)
    if not response:
        raise Exception('Failed to get public key for recipient')
    else:
        recipient_public_key = pickle.loads(response)

    #THIS IS ONLY AFTER JOIN
    send_button = Button(root, text='Send', command=lambda: send_message(sock, recipient_public_key, message_entry, chat_window))
    send_button.pack(side=RIGHT, padx=10, pady=10)

    # Bind the <Return> event to the send_message function
    message_entry.bind('<Return>', lambda event: send_message(sock, recipient_public_key, message_entry, chat_window))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_message, args=(sock, private_key, chat_window, user_name))
    receive_thread.start()

def connect_to_server(address, recipient_username):
    # Create a socket and connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)

    # Generate a key pair
    public_key, private_key = generate_key_pair(1024)
    print(public_key, private_key)

    # Send the public key to the server
    user_name = 'ira'
    sock.send(pickle.dumps([public_key, user_name]))

    # Create a GUI for the chat system
    root = Tk()
    root.title('RSA Chat Client')

    chat_window = Text(root, state=DISABLED, width=50)
    chat_window.pack(padx=10, pady=10)

    message_entry = Entry(root, width=40)
    message_entry.pack(side=LEFT, padx=10, pady=10)

    join_chat_button = Button(root, text='Join', command=lambda: join_chat(sock, recipient_username, user_name, private_key, message_entry, chat_window, root, join_chat_button))
    join_chat_button.pack(side=LEFT, padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    connect_to_server(('192.168.239.51', 8080), 'sanya')