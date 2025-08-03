# wget https://raw.githubusercontent.com/tabatkins/wordle-list/main/words 

import random
from colorama import Fore, Style

class WordleFactory():
    @staticmethod
    def new_wordle(game_type: str, max_round: int, word_path: str):
        w = None
        if game_type == 'server/client':
            w = NormalWordle(max_round, word_path)
        elif game_type == 'host cheating':
            w = HostCheatingWordle(max_round, word_path)
        elif game_type == 'multi-player':
            w = MultiPlayerWordle(max_round, word_path)
        return w

class Wordle:

    def __init__(self, max_round: int = 6, word_path: str = 'data/full'):
        self.word_path = word_path
        self.set_max_round(max_round)
        self.set_word_list(word_path)

    def set_max_round(self, max_round: int):
        self.max_round = max_round

    def set_word_list(self, word_path: str):
        self.word_path = word_path
        with open(word_path, mode = 'r') as f:
            L = f.readlines()
        self.word_list = [i.strip().replace('\n', '') for i in L]
        self.word_list.sort()

class NormalWordle(Wordle):

    def __init__(self, max_round = 6, word_path = 'data/full'):
        super().__init__(max_round, word_path)
        self.objective_word = self.random_word()
        print('==========>', self.objective_word)

    def random_word(self, ):
        return random.choice(self.word_list)

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
    def __init__(self, max_round = 6, word_path = 'data/full'):
        super().__init__(max_round, word_path)
        self.objective_word = ''
        self.candidate_word_list = self.word_list

    def score(self, word1, word2):
        s = 0
        for i in range(5):
            if word1[i] == word2[i]:
                s += 10
            elif word1[i] in word2:
                s += 1
        return s
    
    def random_word(self, ):
        return random.choice(self.candidate_word_list)
    
    def check_util(self, input_word: str):
        print('wordle.check_util input_word', input_word, 'objective_word', self.objective_word)
        res = '' 
        for i in range(5):
            if input_word[i] == self.objective_word[i]:
                res += '0'
            elif input_word[i] in self.objective_word:
                res += '?'
            else:
                res += '_'
        return res

    def check(self, input_word: str):
        if self.objective_word == '':
            print('wordle.check')
            tmp_score = [[] for i in range(51)]
            for word in self.candidate_word_list:
                s = self.score(word, input_word)
                tmp_score[s].append(word)
            
            # min_s = 50
            for i in range(51):
                print('i', i, 'len', len(tmp_score[i]), tmp_score[i])
                if len(tmp_score[i]) == 0:
                    continue
                elif len(tmp_score[i]) == 1:
                    # min_s = i
                    self.objective_word = tmp_score[i][0]
                    return self.check_util(input_word)
                else:
                    # min_s = i
                    self.candidate_word_list = tmp_score[i]
                    if i == 0:
                        return '_____'
                    else:
                        self.objective_word = self.random_word()
                        print('len of candidate', len(self.candidate_word_list), self.candidate_word_list)
                        print('randomly choose', self.objective_word)
                        return self.check_util(input_word)

        else:
            return self.check_util(input_word)

class MultiPlayerWordle(Wordle):
    def __init__(self, max_round = 6, word_path = 'data/full'):
        print(Fore.CYAN + "[ Initializing MultiPlayer Wordle Game ]" + Style.RESET_ALL)
        if max_round is None or word_path is None:
            self.max_round = None
            self.word_list = None
            self.word_path = word_path
            self.objective_word = None
            print(Fore.YELLOW + "Incomplete configuration (waiting for host setup)" + Style.RESET_ALL)
        else:
            super().__init__(max_round, word_path)
            self.word_path = word_path
            self.objective_word = self.random_word()
            print(Fore.GREEN + "Game initialized successfully:" + Style.RESET_ALL)
            print(Fore.GREEN + f"  - Max Rounds       : {self.max_round}" + Style.RESET_ALL)
            print(Fore.GREEN + f"  - Word List Source : {self.word_path}" + Style.RESET_ALL)
            print(Fore.MAGENTA + f"  - Objective Word   : {self.objective_word}" + Style.RESET_ALL)
        print(Fore.CYAN + "[ MultiPlayerWordle Ready ]\n" + Style.RESET_ALL)

    def re_init(self, max_round: int, word_path: str):
        try:
            super().__init__(max_round, word_path)
            self.word_path = word_path
        except Exception as e:
            print(f'word_path {word_path}')
            print(f"Error re-initializing MultiPlayerWordle: {e}")

    def set_objective_word(self, objective_word: str):
        self.objective_word = objective_word

    def random_word(self, ):
        return random.choice(self.word_list)

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

