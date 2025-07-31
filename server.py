import socket
import threading
import sys
import json

from game import Game, GameFactory
from connection import Connection

class Server:
    # port = 5555
    def __init__(self):
        self.game = None
        self.socket = None
        self.connection_list: list[Connection] = []
    
    #  always listen to new connections
    def start_connection(self, ):
        for i in range(7):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
                self.socket.bind(('0.0.0.0', 5555))
                self.socket.listen(5)
                print("Server started on port 5555")

                while True:
                    client_socket, addr = self.socket.accept()
                    print(f"Connection from {addr} accepted.")
                    c = Connection(client_socket, addr)
                    self.connection_list.append(c)
                    threading.Thread(target = self.listen_to_client, args = (c,)).start()
                    threading.Thread(target = self.execute_game, args = ()).start()

            except OSError as e:
                print(f"Error: {e}. The address may already be in use.")
                print('Retrying.')

    def close_connection(self, ):
        self.socket.close()

    def listen_to_client(self, co: Connection):
        while co.client_socket:
            try:
                client_command = co.client_socket.recv(1024).decode('utf-8')
                if client_command:
                    print(f"Received: {client_command}")
                    self.handle_command(co, client_command)
            except:
                break
                
        # connection.client_socket.close()
        # self.client_list.remove(connection)

    def handle_command(self, co: Connection, command: str):
        cmd = command.strip().split(':')[0]
        param = command.strip().split(':')[1]
        co.add_command_history('c', 's', command)
        if cmd == 'SETUPGAME':
            g = None
            try:
                game_type_idx, max_round, word_path_idx = json.loads(param)
                g = GameFactory().new_game(game_type_idx, max_round, word_path_idx)
                co.set_game(g)
            except Exception as e:
                print('server.handle_command error')
                print(e)
        elif cmd == 'INPUTWORD':
            print(f'CLient {co.client_addr} send word {param}')
            is_valid_word, msg = co.game.score(param)
            print('is_valid_word, msg', is_valid_word, msg)
            if is_valid_word:
                full_cmd = f'PRINT:Round {len(co.game.client_input_word_list)} \t {msg}'
                co.add_command_history('s', 'c', full_cmd)
                co.client_socket.send(full_cmd.encode('utf-8'))
                co.game.client_input_word_list.append([param, msg])
            else:
                full_cmd = f'PRINT:{msg}'
                co.add_command_history('s', 'c', full_cmd.encode('utf-8'))
                co.client_socket.send(f'PRINT:{msg}'.encode('utf-8'))
                co.add_command_history('s', 'g', 'REQUIREINPUTWORD:')

    def execute_game(self, ):
        while True:
            for co in self.connection_list:
                if co.game and co.game.state == 'setup':
                    co.game.set_state('setup_reminded')
                    threading.Thread(target=self.help_client_play, args = (co, )).start()
                elif co.game and co.game.state == 'end':
                    if co.game.result == 'win':
                        full_cmd = 'PRINT:Win\n'
                        co.client_socket.send(full_cmd.encode('utf-8'))
                        co.add_command_history('s', 'c', 'PRINT:Win')
                    else:
                        full_cmd = 'PRINT:Lose\n'
                        co.client_socket.send(full_cmd.encode('utf-8'))
                        co.add_command_history('s', 'c', 'PRINT:Lose')

                    full_cmd = 'PRINT:Close connection\n'
                    co.client_socket.send(full_cmd.encode('utf-8'))
                    co.add_command_history('s', 'c', full_cmd)

                    full_cmd = 'CLOSECONNECTION:\n'
                    co.client_socket.send(full_cmd.encode('utf-8'))
                    co.add_command_history('s', 'c', full_cmd)

                    co.game.set_state('end_reminded')



    def help_client_play(self, co: Connection):
        co.game.play(co)
        return
        


if __name__ == "__main__":
    s = Server()
    s.start_connection()
    
