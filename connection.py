from game import Game

class Connection:
    def __init__(self, client_socket, client_addr):
        self.client_socket = client_socket 
        self.client_addr = client_addr # ip + port
        self.game: Game = None
        self.command_history = [] # [[src, des, full_cmd], ] # s for server, c for client, g for game

    def set_game(self, game: Game):
        self.game = game
    
    def add_command_history(self, src, des, full_cmd):
        self.command_history.append([src, des, full_cmd])