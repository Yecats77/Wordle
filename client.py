import socket
import threading
import time
import json
from colorama import Fore, Style

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
        Client.console_template('Connected:' + str(self.socket.getsockname()))
        
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
        param_json = Game.setup_game_console()
        self.socket.send(f"SETUPGAME|{param_json}\n".encode('utf-8'))

    @staticmethod
    def console_template(str):
        if 'Round' in str:
            for c in str:
                if c == '?':
                    print(Fore.YELLOW + c + Style.RESET_ALL, end = '')
                elif c.isdigit():
                    print(Fore.GREEN + c + Style.RESET_ALL, end = '')
                else:
                    print(c, end = '')
            print('\n')
        elif 'win' in str.lower().split(' ')[0]:
            print('\n' + '=' * 40)
            print('🟢  Message from server')
            print('-' * 40)
            print(Fore.GREEN + str + Style.RESET_ALL)
            print('=' * 40 + '\n')
        elif 'lose' in str.lower().split(' ')[0] or 'fail' in str.lower().split(' ')[0]:
            print('\n' + '=' * 40)
            print('🔴  Message from server')
            print('-' * 40)
            print(Fore.RED + str + Style.RESET_ALL)
            print('=' * 40 + '\n')
        else:
            print('\n' + '=' * 40)
            print('🟢  Message from server')
            print('-' * 40)
            print(str)
            print('=' * 40 + '\n')

    def console_select_opponent(self, ):
        print(Fore.YELLOW + "\nSelect opponent (format: IP-PORT, e.g., 127.0.0.1-8888):" + Style.RESET_ALL)
        op = input('Your input: ').strip()
        msg = f'{self.socket.getsockname()[0]}-{self.socket.getsockname()[1]}-{op}'
        self.socket.send(f'SELECTOPPONENT|{msg}\n'.encode('utf-8'))     

    def handle_command(self, commands):
        for command in commands.split('\n'):
            if not command.strip(): # skip empty line
                continue  
            cmds = command.strip().split('|') 
            cmd = cmds[0]
            if not cmd.strip():
                continue

            if cmd == 'PRINT':
                Client.console_template(command + '\n')
            elif cmd == 'SELECTOPPONENT':
                self.console_select_opponent()
            elif cmd == 'INPUTWORD':
                w = input('Input word: ')
                self.socket.send(f"INPUTWORD|{w}\n".encode('utf-8'))
            elif cmd == 'CLOSECONNECTION':
                time.sleep(1)
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

