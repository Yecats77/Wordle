import socket
import threading
import time
import json

from game import Game

class Client:
    client_list = []

    def __init__(self):
        self.name = 'name' + str(len(self.client_list))
        self.socket = None
    
    def start_connection(self, ):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(1)  # Delay for 1 second
        self.socket.connect(('127.0.0.1', 5555))
        print('Connected')
        
    def listen_to_server(self):
        while self.socket:
            try:
                server_command = self.socket.recv(1024).decode('utf-8')
                if server_command:
                    self.handle_command(server_command)
            except Exception as e:
                print(f"Error in receiving data: {e}")
                self.connected = False

    def select_game(self, ):
        game_type_idx, max_round, word_path_idx = Game.setup_game_console()
        json_list = json.dumps([game_type_idx, max_round, word_path_idx])  
        self.socket.send(f"SETUPGAME:{json_list}\n".encode('utf-8'))

    def handle_command(self, commands):
        for command in commands.split('\n'):
            cmds = command.strip().split(':') 
            cmd = cmds[0]

            if cmd == 'PRINT':
                print(f'Message from server: {command}\n')
            elif cmd == 'INPUTWORD':
                w = input('Input word: ')
                self.socket.send(f"INPUTWORD:{w}\n".encode('utf-8'))
            elif cmd == 'CLOSECONNECTION':
                self.close_connection()
        
    def close_connection(self, ):
        print(self.socket)
        if self.socket:
            self.socket.close()
            self.socket = None
        return


if __name__ == '__main__':
    c = Client()
    n_retry = 1
    for i in range(n_retry):
        try:
            c.start_connection()
            c.select_game()
            c.listen_to_server()
        except Exception as e:
            print(e)
            print('Connect failed. Retrying.')

