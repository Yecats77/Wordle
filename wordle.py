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

    def __init__(self, max_round: int = 6, word_path: str = 'data/full'):
        self.set_max_round(max_round)
        self.set_word_list(word_path)

    def set_max_round(self, max_round: int):
        self.max_round = max_round

    def set_word_list(self, word_path: str):
        with open(word_path, mode = 'r') as f:
            L = f.readlines()
        self.word_list = [i.strip().replace('\n', '') for i in L]
        print(self.word_list[:10])
        self.word_list.sort()
        print(self.word_list[:10])

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

    # def cnt_char(self, word1, word2): # count num of char from word1 in word2
    #     cnt = 0
    #     for c in word1:
    #         if c in word2:
    #             cnt += 1
    #     return cnt
    
    # def return_char(self, input_word):
    #     res = '' 
    #     for i in range(5):
    #         if input_word[i] == self.objective_word[i]:
    #             res += '0'
    #         elif input_word[i] in self.objective_word:
    #             res += '?'
    #         else:
    #             res += '_'
    #     return res

    def score(self, word1, word2):
        s = 0
        for i in range(5):
            if word1[i] == word2[i]:
                s += 10
            elif word1[i] in word2:
                s += 1
        return s
    
    def check_util(self, input_word: str):
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
            
            min_s = 50
            for i in range(51):
                if len(tmp_score[i]) == 0:
                    continue
                elif len(tmp_score[i]) == 1:
                    min_s = i
                    self.objective_word = tmp_score[i][0]
                    return self.check_util(input_word)
                else:
                    min_s = i
                    self.candidate_word_list = tmp_score[i]
                    if i == 0:
                        print('len of candidate', len(self.candidate_word_list), self.candidate_word_list)
                        return '_____'
                    else:
                        self.objective_word = random.choice(self.candidate_word_list)
                        print('len of candidate', len(self.candidate_word_list), self.candidate_word_list)
                        print('randomly choose', self.objective_word)
                        return self.check_util(input_word)

        else:
            return self.check_util(input_word)

            

