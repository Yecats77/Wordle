import time
import json
from colorama import Fore, Style

from wordle import WordleFactory, NormalWordle, HostCheatingWordle
from connection import Connection 

class GameFactory():
    @staticmethod
    def new_game(param_json: str): 
        print('game fac param_json', param_json)
        param_dict = json.loads(param_json)
        game_type_idx = param_dict['game_type_idx']
        g = None
        if game_type_idx == 0:
            g = ServerClientGame(param_dict)
        elif game_type_idx == 1:
            g = HostCheatingGame(param_dict)
        elif game_type_idx == 2:
            g = MultiPlayerGame(param_dict)
        return g

class Game():
    # game_type_list = ['normal', 'server/client']
    game_type_list = ['server/client', 'host cheating', 'multi-player']
    word_path_list = ['full', 'short']
    max_score: int = 0 

    def __init__(self, ):
        self.state = 'notsetup' # notsetup, setup, playing
        self.result = '' # '', win, lose
        self.wordle = None
        self.client_input_word_list = []
    
    @staticmethod
    def send_msg_to_client(co: Connection, src, des, msg):
        try:
            msg += '\n'
            co.add_command_history(src, des, msg)
            co.client_socket.send(msg.encode('utf-8'))
        except Exception as e:
            print(f"Warning sending message to client {co.addr}: {e}")
            print(f'The connection may have been closed or lost.')

    def set_state(self, state):
        if state not in ['notsetup', 'setup', 'setup_reminded', 'playing', 'end', 'end_reminded']:
            raise NameError
        self.state = state
    
    def set_result(self, result):
        if result not in ['none', 'win', 'lose']:
            raise NameError
        self.result = result

    @staticmethod
    def setup_game_console():
        param_dict = {}
        # 
        print("=" * 40)
        print(Fore.CYAN + "Welcome to Wordle Setup Console" + Style.RESET_ALL)
        print("=" * 40)
        #
        # Select game type
        print(Fore.YELLOW + "\nPlease select the game type:" + Style.RESET_ALL)
        for idx, t in enumerate(Game.game_type_list):
            print(f"  {idx} - {t}")
        while True:
            try:
                game_type_idx = int(input("\nYour choice: "))
                if game_type_idx not in range(len(Game.game_type_list)):
                    raise ValueError
                break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a valid number." + Style.RESET_ALL)
        param_dict['game_type_idx'] = game_type_idx
        # 
        # Multiplayer-specific settings
        if game_type_idx == 2:
            while True:
                is_host_input = input("\nAre you the host? (yes/no): ").strip().lower()
                if is_host_input in ['yes', 'no']:
                    is_host = is_host_input == 'yes'
                    param_dict['is_host'] = is_host
                    break
                else:
                    print(Fore.RED + "Please answer with 'yes' or 'no'." + Style.RESET_ALL)

            if not is_host:
                print(Fore.MAGENTA + "\nYou are a player. Waiting for the host to set up the game..." + Style.RESET_ALL)
                param_dict['max_round'] = None
                param_dict['word_path_idx'] = None
                return json.dumps(param_dict)
            else:
                print(Fore.MAGENTA + "\nYou are the host. Please set up the game parameters." + Style.RESET_ALL)
        #
        # Input max round
        while True:
            try:
                max_round = int(input("\n Enter max number of rounds (e.g., 6): "))
                if max_round <= 0:
                    raise ValueError
                param_dict['max_round'] = max_round
                break
            except ValueError:
                print(Fore.RED + "Invalid number. Please enter a positive integer." + Style.RESET_ALL)

        # 
        # Select word list
        print(Fore.YELLOW + "\n Choose word list:" + Style.RESET_ALL)
        for idx, t in enumerate(Game.word_path_list):
            print(f"  {idx} - {t}")
        while True:
            try:
                word_path_idx = int(input("\nYour choice: "))
                if word_path_idx not in range(len(Game.word_path_list)):
                    raise ValueError
                param_dict['word_path_idx'] = word_path_idx
                break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a valid number." + Style.RESET_ALL)

        print(Fore.GREEN + "\n🟢 Game setup complete!\n" + Style.RESET_ALL)
        return json.dumps(param_dict)
    
    
'''
class NormalGame(Game):
    game_type = ''

    def __init__(self, max_round: int, word_path: str):
        super().__init__(max_round = max_round, word_path = word_path)
        self.game_type = 'normal'

    def play(self, server_socket, client_socket):
        # p = Player()
        # self.player_list.append(p)

        for i in range(self.wordle.max_round):
            client_socket.send('INPUTWORD|'.encode('utf-8'))

            # w = input('Please input:\t')
            # if len(w) != 5:
            #     print('Wrong word length')
            #     i -= 1
            # elif w not in self.wordle.word_list:
            #     print('Invalid word')
            #     i -= 1
            # else:
            #     result = self.wordle.check(w)
            #     print('round', str(i) + ':', '\t', result)
            #     if result == '00000':
            #         print('WIN')
            #         return
        
        print('LOSE')
        print('The objective word is', self.wordle.objective_word)
'''

class ServerClientGame(Game):

    def __init__(self, param_dict: dict):
        super().__init__()
        self.game_type = 'server/client'
        max_round = param_dict.get('max_round', None)
        word_path_idx = param_dict.get('word_path_idx', None)
        word_path = f'data/{Game.word_path_list[word_path_idx]}.txt'
        self.wordle = WordleFactory().new_wordle(self.game_type, max_round, word_path)
        self.set_state('setup')
    
    def play(self, co):
        precnt = -1
        while co.client_socket:
            if len(self.client_input_word_list) >= self.wordle.max_round:
                break
            if len(self.client_input_word_list) > 0 and self.client_input_word_list[-1][1] == '00000':
                Game.send_msg_to_client(co, 's', 'c', 'PRINT|Win')
                self.set_result('win')
                break
            if len(self.client_input_word_list) > precnt or (len(co.command_history) > 0 and co.command_history[-1][2].split('|')[0] == 'REQUIREINPUTWORD'):
                Game.send_msg_to_client(co, 's', 'c', 'INPUTWORD|')
                precnt = len(self.client_input_word_list)
            else:
                time.sleep(0.1)

        print('self.result', self.result)
        if self.result != 'win':
            self.set_result('lose')
        self.set_state('end')
        return
        

    def score(self, word: str):
        if len(word) != 5:
            return False, 'Wrong word length'
        elif word not in self.wordle.word_list:
            return False, 'Invalid word'
        else:
            res = self.wordle.check(word)
            return True, res
    
class HostCheatingGame(Game):

    def __init__(self, param_dict: dict):
        super().__init__()
        self.game_type = 'host cheating'
        max_round = param_dict.get('max_round', None)
        word_path_idx = param_dict.get('word_path_idx', None)
        word_path = f'data/{Game.word_path_list[word_path_idx]}.txt'
        self.wordle = WordleFactory().new_wordle(self.game_type, max_round, word_path)
        self.set_state('setup')

    def play(self, co):
        precnt = -1
        while co.client_socket:
            time.sleep(0.1)
            if len(self.client_input_word_list) >= self.wordle.max_round:
                break
            print('self.client_input_word_list', self.client_input_word_list)
            if len(self.client_input_word_list) > 0 and self.client_input_word_list[-1][1] == '00000':
                # Game.send_msg_to_client(co, 's', 'c', 'PRINT|Win')
                self.set_result('win')
                break
            if len(self.client_input_word_list) > precnt or (len(co.command_history) > 0 and co.command_history[-1][2].split('|')[0] == 'REQUIREINPUTWORD'):
                Game.send_msg_to_client(co, 's', 'c', 'INPUTWORD|')
                precnt = len(self.client_input_word_list)
            else:
                time.sleep(0.1)
        
        if self.result == '':
            if len(self.client_input_word_list) > 0 and self.client_input_word_list[-1][1] == '00000':
                self.set_result('win')

        print('self.result', self.result)
        if self.result != 'win':
            self.set_result('lose')
        self.set_state('end')
        return
        

    def score(self, word: str):
        if len(word) != 5:
            return False, 'Wrong word length'
        elif word not in self.wordle.word_list:
            return False, 'Invalid word'
        else:
            res = self.wordle.check(word)
            return True, res

class MultiPlayerGame(Game): 
    def __init__(self, param_dict: dict):
        print('set multiplyer game')
        print('param_dict', param_dict, param_dict.get('word_path_idx', None))
        super().__init__()
        self.game_type = 'multi-player'
        max_round = param_dict.get('max_round', None)
        word_path_idx = param_dict.get('word_path_idx', None)
        word_path = f'data/{Game.word_path_list[int(word_path_idx)]}.txt' if word_path_idx != None else None
        self.is_host = param_dict['is_host']
        self.opponent = None
        print('word_path', word_path)
        self.wordle = WordleFactory().new_wordle(self.game_type, max_round, word_path)

        # if self.wordle:
        #     self.set_state('setup')
        # else:
        self.set_state('notsetup')

    def set_opponent(self, opponent):
        self.opponent = opponent
    
    def re_init(self, max_round: int, word_path: str):
        print('game.re_init', max_round, word_path)
        self.wordle.re_init(max_round, word_path)
    
    def set_objective_word(self, objective_word: str):
        self.wordle.set_objective_word(objective_word)
        
    def play(self, co):
        precnt = -1
        while True and co.client_socket and co.game.state != 'end' and co.game.state != 'end_reminded':
            if len(self.client_input_word_list) >= self.wordle.max_round:
                break
            if len(self.client_input_word_list) > 0 and self.client_input_word_list[-1][1] == '00000':
                Game.send_msg_to_client(co, 's', 'c', 'PRINT|Win')
                self.set_result('win')
                break
            if len(self.client_input_word_list) > precnt or (len(co.command_history) > 0 and co.command_history[-1][2].split('|')[0] == 'REQUIREINPUTWORD'):
                Game.send_msg_to_client(co, 's', 'c', 'INPUTWORD|')
                precnt = len(self.client_input_word_list)
            else:
                time.sleep(0.1)

        print('self.result', self.result)
        if self.result != 'win':
            self.set_result('lose')
        self.set_state('end')
        return

    def score(self, word: str):
        if len(word) != 5:
            return False, 'Wrong word length'
        elif word not in self.wordle.word_list:
            return False, 'Invalid word'
        else:
            res = self.wordle.check(word)
            return True, res