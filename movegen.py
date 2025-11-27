"""
Move Generation Module

Generates all legal moves for a given chess position.
"""

from typing import List, Tuple
from .board import ChessBoard, Piece, Color


class MoveGenerator:
    """Generates all legal moves for a chess board"""
    
    def __init__(self, board: ChessBoard):
        self.board = board
    
    def generate_all_moves(self, color: Color) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Generate all legal moves for the given color.
        Returns list of (from_pos, to_pos) tuples.
        """
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece[1] == color:
                    piece_moves = self._generate_moves_for_piece(row, col, piece[0], piece[1])
                    moves.extend(piece_moves)
        
        # Filter out illegal moves (those that leave own king in check)
        legal_moves = []
        for move in moves:
            from_pos, to_pos = move
            if self._is_legal_move(from_pos, to_pos):
                legal_moves.append(move)
        
        return legal_moves
    
    def _generate_moves_for_piece(self, row: int, col: int, piece: Piece, color: Color) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate moves for a specific piece"""
        moves = []
        from_pos = (row, col)
        
        if piece == Piece.PAWN:
            moves.extend(self._generate_pawn_moves(row, col, color))
        elif piece == Piece.KNIGHT:
            moves.extend(self._generate_knight_moves(row, col, color))
        elif piece == Piece.BISHOP:
            moves.extend(self._generate_sliding_moves(row, col, color, [(1, 1), (1, -1), (-1, 1), (-1, -1)]))
        elif piece == Piece.ROOK:
            moves.extend(self._generate_sliding_moves(row, col, color, [(1, 0), (-1, 0), (0, 1), (0, -1)]))
        elif piece == Piece.QUEEN:
            moves.extend(self._generate_sliding_moves(row, col, color, [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]))
        elif piece == Piece.KING:
            moves.extend(self._generate_king_moves(row, col, color))
        
        return [(from_pos, move) for move in moves]
    
    def _generate_pawn_moves(self, row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate pawn moves"""
        moves = []
        direction = -1 if color == Color.WHITE else 1
        start_row = 6 if color == Color.WHITE else 1
        
        # Move forward one square
        new_row = row + direction
        if self.board.is_valid_square(new_row, col):
            if self.board.get_piece(new_row, col) is None:
                moves.append((new_row, col))
                
                # Move forward two squares from starting position
                if row == start_row:
                    new_row2 = row + 2 * direction
                    if self.board.is_valid_square(new_row2, col) and self.board.get_piece(new_row2, col) is None:
                        moves.append((new_row2, col))
        
        # Capture diagonally
        for dc in [-1, 1]:
            new_row = row + direction
            new_col = col + dc
            if self.board.is_valid_square(new_row, new_col):
                target = self.board.get_piece(new_row, new_col)
                # Regular capture
                if target and target[1] != color:
                    moves.append((new_row, new_col))
                # En passant capture (only if no piece on square)
                elif not target and self.board.en_passant_target == (new_row, new_col):
                    moves.append((new_row, new_col))
        
        return moves
    
    def _generate_knight_moves(self, row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate knight moves"""
        moves = []
        knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_deltas:
            new_row, new_col = row + dr, col + dc
            if self.board.is_valid_square(new_row, new_col):
                target = self.board.get_piece(new_row, new_col)
                if target is None or target[1] != color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _generate_sliding_moves(self, row: int, col: int, color: Color, directions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate moves for sliding pieces (rook, bishop, queen)"""
        moves = []
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.board.is_valid_square(new_row, new_col):
                    break
                
                target = self.board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target[1] != color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def _generate_king_moves(self, row: int, col: int, color: Color) -> List[Tuple[int, int]]:
        """Generate king moves"""
        moves = []
        king_deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in king_deltas:
            new_row, new_col = row + dr, col + dc
            if self.board.is_valid_square(new_row, new_col):
                target = self.board.get_piece(new_row, new_col)
                if target is None or target[1] != color:
                    moves.append((new_row, new_col))
        
        # Castling - check all conditions
        if color == Color.WHITE and row == 7 and col == 4:  # King on e1
            # Kingside castling (O-O)
            if (self.board.castling_rights['K'] and
                self.board.get_piece(7, 5) is None and
                self.board.get_piece(7, 6) is None and
                self.board.get_piece(7, 7) and
                self.board.get_piece(7, 7)[0] == Piece.ROOK and
                self.board.get_piece(7, 7)[1] == Color.WHITE):
                # Check if king is not in check
                if not self.board.is_in_check(Color.WHITE):
                    # Check if squares king moves through are not attacked
                    opponent = Color.BLACK
                    if (not self.board._is_square_attacked(7, 4, opponent) and  # e1 not attacked
                        not self.board._is_square_attacked(7, 5, opponent) and  # f1 not attacked
                        not self.board._is_square_attacked(7, 6, opponent)):   # g1 not attacked
                        moves.append((7, 6))
            # Queenside castling (O-O-O)
            if (self.board.castling_rights['Q'] and
                self.board.get_piece(7, 1) is None and
                self.board.get_piece(7, 2) is None and
                self.board.get_piece(7, 3) is None and
                self.board.get_piece(7, 0) and
                self.board.get_piece(7, 0)[0] == Piece.ROOK and
                self.board.get_piece(7, 0)[1] == Color.WHITE):
                # Check if king is not in check
                if not self.board.is_in_check(Color.WHITE):
                    # Check if squares king moves through are not attacked
                    opponent = Color.BLACK
                    if (not self.board._is_square_attacked(7, 4, opponent) and  # e1 not attacked
                        not self.board._is_square_attacked(7, 3, opponent) and  # d1 not attacked
                        not self.board._is_square_attacked(7, 2, opponent)):   # c1 not attacked
                        moves.append((7, 2))
        elif color == Color.BLACK and row == 0 and col == 4:  # King on e8
            # Kingside castling (O-O)
            if (self.board.castling_rights['k'] and
                self.board.get_piece(0, 5) is None and
                self.board.get_piece(0, 6) is None and
                self.board.get_piece(0, 7) and
                self.board.get_piece(0, 7)[0] == Piece.ROOK and
                self.board.get_piece(0, 7)[1] == Color.BLACK):
                # Check if king is not in check
                if not self.board.is_in_check(Color.BLACK):
                    # Check if squares king moves through are not attacked
                    opponent = Color.WHITE
                    if (not self.board._is_square_attacked(0, 4, opponent) and  # e8 not attacked
                        not self.board._is_square_attacked(0, 5, opponent) and  # f8 not attacked
                        not self.board._is_square_attacked(0, 6, opponent)):   # g8 not attacked
                        moves.append((0, 6))
            # Queenside castling (O-O-O)
            if (self.board.castling_rights['q'] and
                self.board.get_piece(0, 1) is None and
                self.board.get_piece(0, 2) is None and
                self.board.get_piece(0, 3) is None and
                self.board.get_piece(0, 0) and
                self.board.get_piece(0, 0)[0] == Piece.ROOK and
                self.board.get_piece(0, 0)[1] == Color.BLACK):
                # Check if king is not in check
                if not self.board.is_in_check(Color.BLACK):
                    # Check if squares king moves through are not attacked
                    opponent = Color.WHITE
                    if (not self.board._is_square_attacked(0, 4, opponent) and  # e8 not attacked
                        not self.board._is_square_attacked(0, 3, opponent) and  # d8 not attacked
                        not self.board._is_square_attacked(0, 2, opponent)):   # c8 not attacked
                        moves.append((0, 2))
        
        return moves
    
    def _is_legal_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Check if a move is legal (doesn't leave own king in check).
        This is done by making the move and checking if king is in check.
        Handles castling specially.
        """
        # Store original state
        original_turn = self.board.turn
        piece = self.board.get_piece(from_pos[0], from_pos[1])
        if not piece or piece[1] != original_turn:
            return False
        
        # Handle castling moves specially
        is_castling = (piece[0] == Piece.KING and abs(from_pos[1] - to_pos[1]) == 2)
        rook_from = None
        rook_to = None
        moved_rook = None
        
        if is_castling:
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            # Kingside castling
            if to_col == 6:
                rook_from = (from_row, 7)
                rook_to = (from_row, 5)
            # Queenside castling
            elif to_col == 2:
                rook_from = (from_row, 0)
                rook_to = (from_row, 3)
            
            if rook_from and rook_to:
                moved_rook = self.board.get_piece(rook_from[0], rook_from[1])
        
        # Make the move temporarily (including rook for castling)
        captured = self.board.get_piece(to_pos[0], to_pos[1])
        self.board.set_piece(to_pos[0], to_pos[1], piece[0], piece[1])
        self.board.remove_piece(from_pos[0], from_pos[1])
        
        # Handle castling rook move
        if is_castling and moved_rook and rook_from and rook_to:
            self.board.set_piece(rook_to[0], rook_to[1], moved_rook[0], moved_rook[1])
            self.board.remove_piece(rook_from[0], rook_from[1])
        
        # Check if own king is in check
        in_check = self.board.is_in_check(original_turn)
        
        # Undo the move (including rook for castling)
        self.board.set_piece(from_pos[0], from_pos[1], piece[0], piece[1])
        if captured:
            self.board.set_piece(to_pos[0], to_pos[1], captured[0], captured[1])
        else:
            self.board.remove_piece(to_pos[0], to_pos[1])
        
        # Undo castling rook move
        if is_castling and moved_rook and rook_from and rook_to:
            self.board.set_piece(rook_from[0], rook_from[1], moved_rook[0], moved_rook[1])
            self.board.remove_piece(rook_to[0], rook_to[1])
        
        return not in_check

