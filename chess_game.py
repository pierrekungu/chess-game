from tabulate import tabulate

class ChessVar:
    def __init__(self):
        # Initialize the game status, chessboard, turn, and game state
        self.status = 0
        self.board = [[''] * 8 for _ in range(8)]
        self.turn = 'WHITE'
        self.game_state = 'UNFINISHED'

        # Define initial positions of chess pieces
        self.piece_positions = {
            'WHITE': {
                'King W': (0, 0),
                'Rook W': (1, 0),
                'Bishop W': (1, 1),
                'Bishop1 W': (0, 1),
                'Knight W': (1, 2),
                'Knight1 W': (0, 2)
            },
            'BLACK': {
                'King B': (0, 7),
                'Rook B': (1, 7),
                'Bishop B': (1, 6),
                'Bishop1 B': (0, 6),
                'Knight B': (1, 5),
                'Knight1 B': (0, 5)
            }
        }

        # Initialize the board with pieces
        for player, positions in self.piece_positions.items():
            for piece, (row, col) in positions.items():
                self.board[row][col] = f'{player}_{piece}'

    def draw_board(self):
        # Display the chessboard with pieces
        headers = [''] + [chr(ord('a') + col) for col in range(8)]
        rows = []

        for row_num, row in enumerate(self.board[::-1], start=1):
            row_data = [9 - row_num]
            for square in row:
                piece = square.split('_')[-1] if square else ''
                row_data.append(piece)
            rows.append(row_data)

        table = tabulate(rows, headers=headers, tablefmt='grid')
        print(table)

    def get_game_state(self):
        # Get the current game state
        return self.game_state

    def make_move(self, from_square, to_square):
        # Check various conditions before making a move
        if self.game_state != 'UNFINISHED':
            return False

        if len(from_square) != 2 or len(to_square) != 2:
            return False

        if not (from_square[0].isalpha() and from_square[1].isdigit()):
            return False

        if not (to_square[0].isalpha() and to_square[1].isdigit()):
            return False

        # Convert coordinates to row and column indices
        from_col = ord(from_square[0]) - ord('a')
        from_row = int(from_square[1]) - 1
        to_col = ord(to_square[0]) - ord('a')
        to_row = int(to_square[1]) - 1

        # Deny move if either source or destination is out of bounds
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
            return False

        # Get the piece being moved
        piece = self.board[from_row][from_col]

        if not piece or piece.split('_')[0] != self.turn:
            return False

        # Deny move if destination square is occupied by the player's own piece
        if self.board[to_row][to_col] and self.board[to_row][to_col].split('_')[0] == self.turn:
            return False
        
        # Check if the move is valid and update the board
        if self.is_valid_move(piece, from_col, from_row, to_col, to_row):                      
            captured_piece = self.board[to_row][to_col]
            self.board[from_row][from_col] = ''
            self.board[to_row][to_col] = piece

            # Check for check condition
            if self.is_check(self.turn, piece):
                # Return board to previous state
                self.board[from_row][from_col] = piece
                self.board[to_row][to_col] = captured_piece

                return False            

            # Capture the opponent's piece if it exists
            if captured_piece:
                self.capture_piece(captured_piece)

            # Get the opponents KING coordinates
            for row in range(8):
                for col in range(8):
                    piece = self.board[row][col]
                    if piece and piece.split('_')[1] == 'King W':
                        white_king_row = row
                    elif piece and piece.split('_')[1] == 'King B':
                        black_king_row = row                
                
            # Update the game state based on the current move
            self.update_game_state(to_row, self.turn, white_king_row, black_king_row, self.status)

            # Take note of White king's position when a row == 7
            if white_king_row == 7:
                self.status += 1

                if self.status > 1:
                    self.update_game_state(to_row, self.turn, white_king_row, black_king_row, self.status)

            # If it's BLACK's turn and the game is still UNFINISHED, switch to WHITE's turn
            if self.turn == 'BLACK' and self.game_state == 'UNFINISHED':
                self.turn = 'WHITE'
            else:
                # Switch turns
                self.turn = 'BLACK' if self.turn == 'WHITE' else 'WHITE'

            return True
        
    def is_valid_move(self, piece, from_col, from_row, to_col, to_row):
        _, piece_type = piece.split('_')

        # Valid moves for KING
        if piece_type in ['King W', 'King B']:
            return self.is_valid_king_move(from_col, from_row, to_col, to_row)

        # Valid moves for ROOK
        elif piece_type in ['Rook W', 'Rook B']:
            if self.is_valid_rook_move(from_col, from_row, to_col, to_row):
                return self.is_path_clear(from_col, from_row, to_col, to_row)
            return False

        # Valid moves for BISHOP
        elif piece_type in ['Bishop W', 'Bishop1 W', 'Bishop B', 'Bishop1 B']:
            if self.is_valid_bishop_move(from_col, from_row, to_col, to_row):
                return self.is_path_clear(from_col, from_row, to_col, to_row)
            return False

        # Valid moves for KNIGHT
        elif piece_type in ['Knight W', 'Knight1 W', 'Knight B', 'Knight1 B']:
            return self.is_valid_knight_move(from_col, from_row, to_col, to_row)

        return False

    def is_path_clear(self, from_col, from_row, to_col, to_row):
        col_direction = 1 if to_col > from_col else -1 if to_col < from_col else 0
        row_direction = 1 if to_row > from_row else -1 if to_row < from_row else 0

        col, row = from_col + col_direction, from_row + row_direction
        while col != to_col or row != to_row:
            if self.board[row][col]:
                return False
            col += col_direction
            row += row_direction
        return True

    def is_valid_king_move(self, from_col, from_row, to_col, to_row):
        col_diff = abs(to_col - from_col)
        row_diff = abs(to_row - from_row)

        # Check if the move is within the range of one square in any direction
        if col_diff <= 1 and row_diff <= 1:
            return True

        return False

    def is_valid_rook_move(self, from_col, from_row, to_col, to_row):
        if from_col == to_col and from_row != to_row:
            return True
        
        elif from_row == to_row and from_col != to_col:
            return True
        
        return False

    def is_valid_bishop_move(self, from_col, from_row, to_col, to_row):
        col_diff = abs(to_col - from_col)
        row_diff = abs(to_row - from_row)
        return col_diff == row_diff

    def is_valid_knight_move(self, from_col, from_row, to_col, to_row):
        col_diff = abs(to_col - from_col)
        row_diff = abs(to_row - from_row)
        return (col_diff == 2 and row_diff == 1) or (col_diff == 1 and row_diff == 2)

    def is_check(self, player, played_piece):
        if played_piece.split('_')[1] in ['King W', 'King B']:
            king_piece_name = 'King W' if player == 'WHITE' else 'King B'
        else:
            king_piece_name = 'King B' if player == 'WHITE' else 'King W'
        
        # Get the opponents KING coordinates
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.split('_')[1] == king_piece_name:
                    king_col = col
                    king_row = row
                    king = piece
                    print(king, king_col, king_row)

        # Check for opponent's pieces that threaten the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if king.split('_')[0] == 'BLACK' or played_piece.split('_')[1] == 'King B':
                    if piece and piece.split('_')[0] != 'BLACK':                    
                        if self.is_valid_move(piece, col, row, king_col, king_row):                            
                            return True
                
                elif king.split('_')[0] == 'WHITE' or played_piece.split('_')[1] == 'King W':
                    if piece and piece.split('_')[0] != 'WHITE':                    
                        if self.is_valid_move(piece, col, row, king_col, king_row):
                            return True

        return False

    def capture_piece(self, piece):
        player, piece_type = piece.split('_')

        if piece_type != ('King W' or 'King B'):
            self.piece_positions[player][piece_type] = None

    def update_game_state(self, row, player, white_king_row, black_king_row, status):    
        
        if row == 7 and white_king_row == 7 and player == 'BLACK':
            self.game_state = 'TIE'

        elif row == 7 and black_king_row !=6 and player == 'WHITE':
            self.game_state = 'WHITE WON'

        elif row == 7 and player == 'BLACK':
            self.game_state = 'BLACK WON'  

        elif status == 2:
            self.game_state = 'WHITE WON'

# Example gameplay
game = ChessVar()
game.draw_board()

while game.get_game_state() == 'UNFINISHED':
    from_square = input(f"{game.turn}'s turn. Enter 'from' square: ")
    to_square = input(f"{game.turn}'s turn. Enter 'to' square: ")

    if game.make_move(from_square, to_square):
        game.draw_board()
        
    else:
        print("Invalid move. Try again.")

print(game.get_game_state())
