# wget https://raw.githubusercontent.com/tabatkins/wordle-list/main/words 

import random

class WordleFactory():
    @staticmethod
    def new_wordle(game_type: str, max_round: int, word_path: str):
        w = None
        if game_type == 'host cheating':
            w = HostCheatingWordle(max_round, word_path)
        else:
            w = NormalWordle(max_round, word_path)
        return w

class Wordle:

    def __init__(self, max_round: int = 6, word_path: str = 'data/configurable'):
        self.set_max_round(max_round)
        self.set_word_list(word_path)
        self.objective_word = self.random_word()
        print('==========>', self.objective_word)

    def set_max_round(self, max_round: int):
        self.max_round = max_round

    def set_word_list(self, word_path: str):
        with open(word_path, mode = 'r') as f:
            L = f.readlines()
        self.word_list = [i.strip().replace('\n', '') for i in L]

    
    def random_word(self, ):
        return random.choice(self.word_list)

    def score(self, ):
        pass

class NormalWordle(Wordle):

    def check(self, input_word: str):
        res = '' 
        for i in range(5):
            if input_word[i] == self.objective_word[i]:
                res += '0'
            elif input_word[i] in self.objective_word:
                res += '?'
            else:
                res += '_'
        return res
    
class HostCheatingWordle(Wordle):

    def check(self, input_word: str):
        pass
