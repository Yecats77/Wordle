import socket
import threading
import sys
import json
from colorama import Fore, Style
import time

from game import GameFactory
from connection import Connection

class Server:
    def __init__(self):
        self.game = None
        self.socket = None
        self.connection_list: list[Connection] = []
        self.pre_connection_list: list[Connection] = []
    
    #  always listen to new connections
    def start_connection(self):
        for i in range(7):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind(('0.0.0.0', 5555))
                self.socket.listen(5)

                print(Fore.GREEN + f"Server started on port 5555 — waiting for connections..." + Style.RESET_ALL)

                while True:
                    client_socket, addr = self.socket.accept()
                    print(Fore.CYAN + f"Connection from {addr} accepted." + Style.RESET_ALL)

                    c = Connection(client_socket, addr)
                    print(Fore.MAGENTA + f"Added to connection list: {addr}" + Style.RESET_ALL)
                    self.connection_list.append(c)

                    threading.Thread(
                        target=self.listen_to_client, args=(c,), daemon=True
                    ).start()

                    threading.Thread(
                        target=self.execute_game, args=(), daemon=True
                    ).start()

            except OSError as e:
                print(Fore.RED + f"Error: {e}. Address may be in use." + Style.RESET_ALL)
                print(Fore.YELLOW + f"Retrying in 3 seconds..." + Style.RESET_ALL)
                time.sleep(3)

    def close_connection(self, ):
        self.socket.close()

    def listen_to_client(self, co: Connection):
        while co.client_socket:
            try:
                client_command = co.client_socket.recv(1024).decode('utf-8')
                if client_command:
                    for line in client_command.strip().split('\n'):
                        if line.strip():
                            print(f"{Fore.BLUE}[RECEIVED]{Style.RESET_ALL} {Fore.CYAN}{co.addr}{Style.RESET_ALL} → {Fore.YELLOW}{line}{Style.RESET_ALL}")
                            self.handle_command(co, line)
                else:
                    print(f"{Fore.LIGHTBLACK_EX}[DISCONNECT]{Style.RESET_ALL} Client {co.addr} closed the connection.")
                    break
            except ConnectionResetError:
                print(f"{Fore.RED}[CONNECTION RESET]{Style.RESET_ALL} Client {co.addr} unexpectedly dropped.")
                break
            except Exception as e:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} while receiving from {co.addr}: {e}")
                break

    @staticmethod
    def send_msg_to_client(co: Connection, src, des, msg):
        if co.game.state == 'refuse_result_msg':
            return
        try:
            msg += '\n'
            co.add_command_history(src, des, msg)
            co.client_socket.send(msg.encode('utf-8'))
        except Exception as e:
            pass
            # print(f"Warning sending message to client {co.addr}: {e}")
            # print(f'The connection may have been closed or lost.')

    def handle_command(self, co: Connection, command: str):
        try:
            cmd = command.strip().split('|')[0]
            param = command.strip().split('|')[1] 
            co.add_command_history('c', 's', command)
            if cmd == 'SETUPGAME':
                g = None
                try:
                    param_json = param
                    param_dict = json.loads(param)
                    game_type_idx = param_dict['game_type_idx']
                    g = GameFactory().new_game(param_json)
                    print('new game', co.addr, g.wordle.word_path)
                    co.set_game(g)
                    print(co.addr, 'has set up a game:', g.game_type)
                    if game_type_idx == 2: # Multi-player game
                        is_host = param_dict['is_host']
                        if is_host:
                            Server.send_msg_to_client(co, 's', 'c', 'SELECTOPPONENT|')
                except Exception as e:
                    print('server.handle_command error')
                    print(e)
            elif cmd == 'SELECTOPPONENT':
                try:
                    print(f'receive {param}')
                    host_ip, host_port, opponent_ip, opponent_port = param.split('-') # these two are both clients
                    print(f'Host {host_ip}:{host_port} selected opponent {opponent_ip}:{opponent_port}')
                    print('self.connection_list len', len(self.connection_list))
                    host_co = None
                    opponent_co = None
                    for co in self.connection_list:
                        ip_, port_ = co.addr
                        if ip_ == host_ip and str(port_) == str(host_port):
                            host_co = co
                        elif ip_ == opponent_ip and str(port_) == str(opponent_port):
                            opponent_co = co
                        if host_co and opponent_co:
                            break
                    if not host_co or not opponent_co:
                        raise ValueError(f'Host or opponent connection not found. Host {host_co}, Opponent {opponent_co}')
                    else:
                        print(f'Host {host_co.addr} and Opponent {opponent_co.addr} are ready to play.')
                    host_co.game.set_opponent(opponent_co.addr)
                    opponent_co.game.set_opponent(host_co.addr)
                    opponent_co.game.set_objective_word(host_co.game.wordle.objective_word)
                    opponent_co.game.re_init(host_co.game.wordle.max_round, host_co.game.wordle.word_path)
                    host_co.game.set_state('setup')
                    opponent_co.game.set_state('setup')
                except Exception as e:
                    print(f"Error in SELECTOPPONENT command: {e}")
                    Server.send_msg_to_client(co, 's', 'c', 'PRINT|Opponent selection failed. Please try again.')
                    Server.send_msg_to_client(co, 's', 'c', 'SELECTOPPONENT|')
            elif cmd == 'INPUTWORD':
                is_valid_word, msg = co.game.score(param)
                if is_valid_word or is_valid_word == True:
                    Server.send_msg_to_client(co, 's', 'c', f'PRINT|Round {len(co.game.client_input_word_list)} \t {msg}')
                    co.game.client_input_word_list.append([param, msg])
                else:
                    if len(param) != 0:
                        Server.send_msg_to_client(co, 's', 'c', f'PRINT|{msg}')
                    co.add_command_history('s', 'g', 'REQUIREINPUTWORD|')
        except Exception as e:
            print(f"Error handling command: {e}")

    @staticmethod
    def addr_to_str(addr):
        return f"{addr[0]}-{addr[1]}"

    def execute_game(self, ):
        try:
            while True:
                for co in self.connection_list:
                    if co.game and co.game.state == 'setup':
                        print(co.addr, 'game state is setup, the odj word is', co.game.wordle.objective_word)
                        co.game.set_state('setup_reminded')
                        if co.game.game_type == 'multi-player' and co.game.is_host:
                            print('monitor', co.addr[0] + '-' + str(co.addr[1]), co.game.opponent)
                            # op = self.find_connection_by_addr(co.game.opponent)
                            # threading.Thread(target=self.monitor_host_and_opponent, args = (co, op)).start()
                        threading.Thread(target=self.help_client_play, args = (co, )).start()
                    # multi-player mode will be processed by self.monitor_host_and_opponent()
                    elif co.game and co.game.state == 'end':
                        print('co.game.client_input_word_list', co.game.client_input_word_list)
                        if co.game.result == '':
                            if co.game.client_input_word_list[-1][1] == '00000':
                                co.game.set_result('win')
                        print('co.game.result', co.game.result)
                        if co.game.game_type == 'multi-player':
                            op = self.find_connection_by_addr(co.game.opponent)
                            if co.game.state != 'end':
                                self.monitor_host_and_opponent(co, op)
                        if co.game.result == 'win':
                            Server.send_msg_to_client(co, 's', 'c', f'PRINT|Win The objective word is {co.game.wordle.objective_word}')
                        else:
                            Server.send_msg_to_client(co, 's', 'c', f'PRINT|Lose The objective word is {co.game.wordle.objective_word}')
                        Server.send_msg_to_client(co, 's', 'c', 'PRINT|Close connection')
                        Server.send_msg_to_client(co, 's', 'c', 'CLOSECONNECTION|')
                        self.connection_list.remove(co)
                        self.pre_connection_list.append(co)
                        co.game.set_state('end_reminded')
        except Exception as e:
            print(f"Error in execute_game: {e}")
            print("Exiting game execution thread.")
    
    def find_connection_by_addr(self, addr):
        for co in self.connection_list:
            if co.addr == addr:
                return co
        for co in self.pre_connection_list:
            if co.addr == addr:
                return co
        return None

    def monitor_host_and_opponent(self, host_co: Connection, opponent_co: Connection):
        print(f"Monitoring game between {host_co.client_socket} and {opponent_co.client_socket}")
        while host_co.client_socket or opponent_co.client_socket:
            if host_co.game.result == 'win':
                host_co.game.set_state('end')
                opponent_co.game.set_state('end')
                opponent_co.game.set_result('lose')
                Server.send_msg_to_client(host_co, 's', 'c', 'PRINT|You win')
                Server.send_msg_to_client(opponent_co, 's', 'c', 'PRINT|You lose. Your opponent wins')
                host_co.game.set_state('refuse_result_msg')
                opponent_co.game.set_state('refuse_result_msg')
            elif opponent_co.game.result == 'win':
                host_co.game.set_state('end')
                host_co.game.set_result('lose')
                opponent_co.game.set_state('end')
                Server.send_msg_to_client(opponent_co, 's', 'c', 'PRINT|You win')
                Server.send_msg_to_client(host_co, 's', 'c', 'PRINT|You lose. Your opponent wins')
                host_co.game.set_state('refuse_result_msg')
                opponent_co.game.set_state('refuse_result_msg')
            elif host_co.game.result == 'lose' or opponent_co.game.result == 'lose':
                host_co.game.set_result('lose')
                opponent_co.game.set_result('lose')
                host_co.game.set_state('end')
                opponent_co.game.set_state('end')
                Server.send_msg_to_client(host_co, 's', 'c', 'PRINT|Both of you lose')
                Server.send_msg_to_client(opponent_co, 's', 'c', 'PRINT|Both of you lose')
                host_co.game.set_state('refuse_result_msg')
                opponent_co.game.set_state('refuse_result_msg')
                
    def help_client_play(self, co: Connection):
        co.game.play(co)
        print('co.game.client_input_word_list', co.game.client_input_word_list)
        return
        


if __name__ == "__main__":
    s = Server()
    s.start_connection()
    
