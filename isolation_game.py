import numpy as np
import pygame 
import math

class IsolationGame: 
    def __init__(self):
        self.board = np.array([[' ' for _ in range(6)] for _ in range(6)])
        self.board[0, 0] = '1'  # Speler 1 startpositie
        self.board[5, 5] = '2'  # Speler 2 startpositie
        self.player = 1
        self.player_positions = [(0, 0), (5, 5)]  # Houdt de posities van de spelers bij 
        self.game_over = False
    
    def __str__(self):
        board_str = '\n'.join([' '.join(row) for row in self.board])
        return board_str
    
    def is_move_valid(self, x, y, new_x, new_y):
        if not (0 <= new_x < 6 and 0 <= new_y < 6):
            return False
        if self.board[new_x, new_y] != ' ':
            return False
        
        # controleert of de zet geldig is (voor een koningin)
        dx = new_x - x
        dy = new_y - y
        if dx != 0 and dy != 0 and abs(dx) != abs(dy):
            return False
        if dx == 0 and dy == 0:
            return False
        
        # controleert voor blokkades
        step_x = 1 if dx > 0 else -1 if dx < 0 else 0
        step_y = 1 if dy > 0 else -1 if dy < 0 else 0
        steps = max(abs(dx), abs(dy))
        for step in range(1, steps):
            if self.board[x + step * step_x, y + step * step_y] != ' ':
                return False
        return True

    def move(self, new_x, new_y):
        if self.game_over:
            print("Game is already over.")
            return False
        
        current_position = self.player_positions[self.player - 1]
        if self.is_move_valid(*current_position, new_x, new_y):
            self.board[current_position] = 'X'  # Markeer het oude vak als geblokkeerd
            self.board[new_x, new_y] = str(self.player)
            self.player_positions[self.player - 1] = (new_x, new_y)  # Update de positie
            
            self.player = 1 if self.player == 2 else 2  # Wissel van speler
            
            # Controleer na de zet of de volgende speler geen geldige zetten meer heeft
            if self.terminal_state(self.player_positions[self.player - 1]):
                print(f"Game over. Player {3 - self.player} wins!")
                self.game_over = True
            return True 
        else: 
            print("Invalid move") 
        return False

    def terminal_state(self, player_position):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        x, y = player_position
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            # Controleer of de nieuwe positie binnen het bord is en of het veld leeg is.
            if 0 <= new_x < 6 and 0 <= new_y < 6 and self.board[new_x, new_y] == ' ':
                return False  # Er is een geldige zet gevonden
        return True  # Geen geldige zetten gevonden, spel is voorbij

class IsolationGameAI(IsolationGame): # klasse met alle AI gebeuren
    def __init__(self):
        super().__init__() # roept de constructor van de parent klasse aan (IsolationGame)
        self.max_depth = 3  # depth. bij 4 gaat het lang duren (zelfs op mijn pc die eigenlijk best goed is) en lager dan 2 dan is hij dom. met AB pruning wordt sneller miss
        

    def move(self, new_x, new_y): # als speler 2 is, dan speelt AI
        if self.player != 2: 
            return super().move(new_x, new_y)

        best_score = -math.inf 
        best_move = None 
        current_position = self.player_positions[self.player - 1]

        for x in range(6): # simuleert elke mogelijke zet, roept minimax aan om score te berekenen  en houdt het bij
            for y in range(6):
                if self.is_move_valid(*current_position, x, y):
                    self.board[current_position] = 'X'
                    self.board[x, y] = '2'
                    self.player_positions[self.player - 1] = (x, y)
                    score = self.minimax(0, False)
                    self.board[x, y] = ' '
                    self.board[current_position] = '2'
                    self.player_positions[self.player - 1] = current_position

                    if score > best_score: # beste score tracking
                        best_score = score
                        best_move = (x, y)

        if best_move is None:
            print("No valid moves available. Player 1 wins!")
            self.game_over = True
            return False

        return super().move(*best_move) # roept de move functie van de parent klasse aan

    def minimax(self, depth, is_maximizing): # minimax algoritme methode
        if depth == self.max_depth or self.terminal_state(self.player_positions[self.player - 1]):
            return self.evaluate()

        original_board = self.board.copy()  # kopie van het bord
        original_positions = self.player_positions.copy()  # kopie van de posities van de spelers

        if is_maximizing: # globaal maximaliseert deze if else de score voor AI en minimaliseert die voor tegenstander om de best move te vinden
            best_score = -math.inf
            for x in range(6): # deze for loop probeert de minimax score van een bepaalde zet te vinden
                for y in range(6):
                    if self.is_move_valid(*self.player_positions[self.player - 1], x, y):
                        self.board[self.player_positions[self.player - 1]] = 'X'
                        self.board[x, y] = '2'
                        self.player_positions[self.player - 1] = (x, y)
                        best_score = max(best_score, self.minimax(depth + 1, False))
                        self.board = original_board.copy()
                        self.player_positions = original_positions.copy()
            return best_score
        else:
            best_score = math.inf
            for x in range(6):
                for y in range(6):
                    if self.is_move_valid(*self.player_positions[2 - self.player], x, y):
                        self.board[self.player_positions[2 - self.player]] = 'X'
                        self.board[x, y] = '1'
                        self.player_positions[2 - self.player] = (x, y)
                        best_score = min(best_score, self.minimax(depth + 1, True))
                        self.board = original_board.copy() 
                        self.player_positions = original_positions.copy()  
            return best_score

    def evaluate(self): #deze functie geeft een waarde aan de huidige staat van het bord. positief is goed voor speler 2, negatief is goed voor speler 1. denk aan schaken
        player_1_moves = self.get_available_moves(self.player_positions[0])
        player_2_moves = self.get_available_moves(self.player_positions[1])
        return len(player_2_moves) - len(player_1_moves)

    def get_available_moves(self, player_position):
        moves = []
        x, y = player_position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 6 and 0 <= new_y < 6 and self.board[new_x, new_y] == ' ':
                moves.append((new_x, new_y))
        return moves

class IsolationGamePygame: 
    def __init__(self): 
        pygame.init() 
        self.font = pygame.font.SysFont("arial", 36)
        self.screen = pygame.display.set_mode((600, 600))
        self.clock = pygame.time.Clock()
        self.game = IsolationGameAI()
        self.cell_size = 100
        self.running = True

        self.black_queen = pygame.image.load("PI7-main\\img\\black_queen.png")
        self.white_queen = pygame.image.load("PI7-main\\img\\white_queen.png")

    def draw_board(self):
        queen_size = int(self.cell_size * 0.6)  # 
        for x in range(6):
            for y in range(6):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, pygame.Color('grey' if (x + y) % 2 == 0 else 'white'), rect)
                if self.game.board[y, x] == '1':
                    queen_rect = self.white_queen.get_rect(center=rect.center)
                    queen_rect.width = queen_size
                    queen_rect.height = queen_size
                    self.screen.blit(pygame.transform.scale(self.white_queen, (queen_size, queen_size)), queen_rect)
                elif self.game.board[y, x] == '2':
                    queen_rect = self.black_queen.get_rect(center=rect.center)
                    queen_rect.width = queen_size
                    queen_rect.height = queen_size
                    self.screen.blit(pygame.transform.scale(self.black_queen, (queen_size, queen_size)), queen_rect)
                elif self.game.board[y, x] == 'X':
                    pygame.draw.line(self.screen, pygame.Color('blue'), rect.topleft, rect.bottomright, 5)
                    pygame.draw.line(self.screen, pygame.Color('blue'), rect.bottomleft, rect.topright, 5)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if self.game.game_over:
                    self.show_game_over_message(3 - self.game.player) # Toon bericht met de winnaar
                    pygame.time.wait(5000) # Wacht 5 seconden
                    self.running = False # Stop de game loop

                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Bepaal de cel waarin geklikt is
                    x, y = event.pos
                    grid_y, grid_x = x // self.cell_size, y // self.cell_size # Draai x en y om

                    if self.game.player == 1:  # splr 1 is menselijke speler
                        if self.game.is_move_valid(*self.game.player_positions[self.game.player - 1], grid_x, grid_y):
                            self.game.move(grid_x, grid_y)
                            if not self.game.game_over:
                                self.ai_move()  # call de zet van de AI na de zet van de speler
                        else:
                            print("Invalid move")


            self.screen.fill(pygame.Color('black'))
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def ai_move(self):
        self.game.move(None, None)  # AI doet een zet
        self.draw_board()  # update het bord

    def show_game_over_message(self, winner):
        message = f"Game Over. Player {winner} wins!"
        text_surface = self.font.render(message, True, pygame.Color('orange'))
        text_rect = text_surface.get_rect(center=(300, 300))  # Centreer het bericht
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()  # Update het scherm om het bericht te tonen

if __name__ == "__main__":
    game_vis = IsolationGamePygame()
    game_vis.run() 
