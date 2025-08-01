import time

from wordle import WordleFactory, NormalWordle, HostCheatingWordle

class GameFactory():
    @staticmethod
    def new_game(game_type_idx: int, max_round: int, word_path_idx: int): 
        g = None
        if game_type_idx == 0:
            g =  ServerClientGame(max_round, f'data/{Game.word_path_list[word_path_idx]}.txt')
        elif game_type_idx == 1:
            g = HostCheatingGame(max_round, f'data/{Game.word_path_list[word_path_idx]}.txt')
        g.set_state('setup')
        return g

class Game():
    # game_type_list = ['normal', 'server/client']
    game_type_list = ['server/client', 'host cheating']
    word_path_list = ['full', 'short']
    max_score: int = 0 

    def __init__(self, max_round: int, word_path: str):
        self.state = 'notsetup' # notsetup, setup, playing
        self.result = 'none' # none, win, lose
        self.wordle = None
        self.client_input_word_list = []

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
        # 
        game_type_msg = ''
        for idx, t in enumerate(Game.game_type_list):
            game_type_msg += f'{idx} - {Game.game_type_list[idx]}\n'
        game_type_idx = int(input(f'=======\nPlease select the game type:\n{game_type_msg}'))
        # 
        max_round = int(input('=======\ninput max round:'))
        # 
        word_path_msg = ''
        for idx, t in enumerate(Game.word_path_list):
            word_path_msg += f'{idx} - {Game.word_path_list[idx]}\n'
        word_path_idx = int(input(f'=======\nPlease input which word list you want to use:\n{word_path_msg}'))
        return int(game_type_idx), int(max_round), int(word_path_idx)
    
    
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
            client_socket.send('INPUTWORD:'.encode('utf-8'))

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
    game_type = ''

    def __init__(self, max_round: int, word_path: str):
        super().__init__(max_round = max_round, word_path = word_path)
        self.game_type = 'server/client'
        self.wordle = WordleFactory().new_wordle(self.game_type, max_round, word_path)
    
    def play(self, co):
        precnt = -1
        while True:
            if len(self.client_input_word_list) >= self.wordle.max_round:
                break
            if len(self.client_input_word_list) > 0 and self.client_input_word_list[-1][1] == '00000':
                co.client_socket.send('PRINT:Win'.encode('utf-8'))
                self.set_result('win')
                break
            if len(self.client_input_word_list) > precnt or (len(co.command_history) > 0 and co.command_history[-1][2].split(':')[0] == 'REQUIREINPUTWORD'):
                co.client_socket.send('INPUTWORD:'.encode('utf-8'))
                co.add_command_history('s', 'c', 'INPUTWORD:')
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

    def __init__(self, max_round: int, word_path: str):
        super().__init__(max_round = max_round, word_path = word_path)
        self.game_type = 'host cheating'
        self.wordle = WordleFactory().new_wordle(self.game_type, max_round, word_path)

    def play(self, co):
        precnt = -1
        while True:
            if len(self.client_input_word_list) >= self.wordle.max_round:
                break
            if len(self.client_input_word_list) > 0 and self.client_input_word_list[-1][1] == '00000':
                co.client_socket.send('PRINT:Win'.encode('utf-8'))
                self.set_result('win')
                break
            if len(self.client_input_word_list) > precnt or (len(co.command_history) > 0 and co.command_history[-1][2].split(':')[0] == 'REQUIREINPUTWORD'):
                co.client_socket.send('INPUTWORD:'.encode('utf-8'))
                co.add_command_history('s', 'c', 'INPUTWORD:')
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
