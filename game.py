import time
import json

from wordle import WordleFactory, NormalWordle, HostCheatingWordle
# from server import Server
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
        self.result = 'none' # none, win, lose
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
        game_type_msg = ''
        for idx, t in enumerate(Game.game_type_list):
            game_type_msg += f'{idx} - {Game.game_type_list[idx]}\n'
        game_type_idx = int(input(f'=======\nPlease select the game type:\n{game_type_msg}'))
        param_dict['game_type_idx'] = game_type_idx
        # 
        if game_type_idx == 2:  # Multi-player game
            is_host = input('Are you the host? (yes/no): ').strip().lower() == 'yes'
            param_dict['is_host'] = is_host
            if not is_host:
                print('You are a player. Waiting for the host to set up the game.')
                param_dict['max_round'] = None
                param_dict['word_path_idx'] = None
                return json.dumps(param_dict)
            else:
                print('You are the host. Please set up the game parameters.')
        #
        max_round = int(input('=======\ninput max round:'))
        param_dict['max_round'] = max_round
        # 
        word_path_msg = ''
        for idx, t in enumerate(Game.word_path_list):
            word_path_msg += f'{idx} - {Game.word_path_list[idx]}\n'
        word_path_idx = int(input(f'=======\nPlease input which word list you want to use:\n{word_path_msg}'))
        param_dict['word_path_idx'] = word_path_idx
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
            if len(self.client_input_word_list) > precnt or (len(co.command_history) > 0 and co.command_history[-1][2].split('')[0] == 'REQUIREINPUTWORD'):
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