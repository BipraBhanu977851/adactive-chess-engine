"""
Chess Board Representation

Implements a bitboard-based chess board representation for efficient
move generation and position evaluation.
"""

from enum import IntEnum
from typing import List, Tuple, Optional
import copy


class Piece(IntEnum):
    """Chess piece types"""
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6


class Color(IntEnum):
    """Piece colors"""
    WHITE = 0
    BLACK = 1


class ChessBoard:
    """
    Chess board representation using 8x8 array.
    Each square contains: (piece_type, color) tuple or None
    """
    
    FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    RANKS = ['1', '2', '3', '4', '5', '6', '7', '8']
    
    def __init__(self, fen: Optional[str] = None):
        """
        Initialize chess board from FEN string or default starting position.
        
        Args:
            fen: FEN string representation (default: starting position)
        """
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.turn = Color.WHITE
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_target = None  # (row, col) or None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []
        
        if fen:
            self.load_fen(fen)
        else:
            self._set_initial_position()
    
    def _set_initial_position(self):
        """Set board to standard chess starting position"""
        # White pieces
        self.set_piece(7, 0, Piece.ROOK, Color.WHITE)
        self.set_piece(7, 1, Piece.KNIGHT, Color.WHITE)
        self.set_piece(7, 2, Piece.BISHOP, Color.WHITE)
        self.set_piece(7, 3, Piece.QUEEN, Color.WHITE)
        self.set_piece(7, 4, Piece.KING, Color.WHITE)
        self.set_piece(7, 5, Piece.BISHOP, Color.WHITE)
        self.set_piece(7, 6, Piece.KNIGHT, Color.WHITE)
        self.set_piece(7, 7, Piece.ROOK, Color.WHITE)
        for col in range(8):
            self.set_piece(6, col, Piece.PAWN, Color.WHITE)
        
        # Black pieces
        self.set_piece(0, 0, Piece.ROOK, Color.BLACK)
        self.set_piece(0, 1, Piece.KNIGHT, Color.BLACK)
        self.set_piece(0, 2, Piece.BISHOP, Color.BLACK)
        self.set_piece(0, 3, Piece.QUEEN, Color.BLACK)
        self.set_piece(0, 4, Piece.KING, Color.BLACK)
        self.set_piece(0, 5, Piece.BISHOP, Color.BLACK)
        self.set_piece(0, 6, Piece.KNIGHT, Color.BLACK)
        self.set_piece(0, 7, Piece.ROOK, Color.BLACK)
        for col in range(8):
            self.set_piece(1, col, Piece.PAWN, Color.BLACK)
    
    def load_fen(self, fen: str):
        """Load position from FEN string"""
        parts = fen.split()
        ranks = parts[0].split('/')
        
        # Clear board
        self.board = [[None for _ in range(8)] for _ in range(8)]
        
        # Parse piece placement
        for rank_idx, rank_str in enumerate(ranks):
            file_idx = 0
            for char in rank_str:
                if char.isdigit():
                    file_idx += int(char)
                else:
                    piece_map = {
                        'P': (Piece.PAWN, Color.WHITE),
                        'N': (Piece.KNIGHT, Color.WHITE),
                        'B': (Piece.BISHOP, Color.WHITE),
                        'R': (Piece.ROOK, Color.WHITE),
                        'Q': (Piece.QUEEN, Color.WHITE),
                        'K': (Piece.KING, Color.WHITE),
                        'p': (Piece.PAWN, Color.BLACK),
                        'n': (Piece.KNIGHT, Color.BLACK),
                        'b': (Piece.BISHOP, Color.BLACK),
                        'r': (Piece.ROOK, Color.BLACK),
                        'q': (Piece.QUEEN, Color.BLACK),
                        'k': (Piece.KING, Color.BLACK),
                    }
                    if char in piece_map:
                        piece, color = piece_map[char]
                        self.set_piece(rank_idx, file_idx, piece, color)
                    file_idx += 1
        
        # Parse active color
        self.turn = Color.WHITE if parts[1] == 'w' else Color.BLACK
        
        # Parse castling rights
        self.castling_rights = {
            'K': 'K' in parts[2],
            'Q': 'Q' in parts[2],
            'k': 'k' in parts[2],
            'q': 'q' in parts[2]
        }
        
        # Parse en passant
        if parts[3] != '-':
            self.en_passant_target = (8 - int(parts[3][1]), ord(parts[3][0]) - ord('a'))
        else:
            self.en_passant_target = None
        
        # Parse move counters
        if len(parts) > 4:
            self.halfmove_clock = int(parts[4])
        if len(parts) > 5:
            self.fullmove_number = int(parts[5])
    
    def get_piece(self, row: int, col: int) -> Optional[Tuple[Piece, Color]]:
        """Get piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Piece, color: Color):
        """Set piece at given position"""
        self.board[row][col] = (piece, color) if piece != Piece.EMPTY else None
    
    def remove_piece(self, row: int, col: int):
        """Remove piece from given position"""
        self.board[row][col] = None
    
    def is_valid_square(self, row: int, col: int) -> bool:
        """Check if square coordinates are valid"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def get_king_position(self, color: Color) -> Optional[Tuple[int, int]]:
        """Find king position for given color"""
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece[0] == Piece.KING and piece[1] == color:
                    return (row, col)
        return None
    
    def is_in_check(self, color: Color) -> bool:
        """
        Check if the given color is in check.
        Simplified version - checks if king is under attack.
        """
        king_pos = self.get_king_position(color)
        if not king_pos:
            return False
        
        # Check if any opponent piece attacks the king
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # For simplicity, we'll check against basic patterns
        # A full implementation would use move generation to verify attacks
        return self._is_square_attacked(king_pos[0], king_pos[1], opponent)
    
    def _is_square_attacked(self, row: int, col: int, by_color: Color) -> bool:
        """Check if square is attacked by pieces of given color"""
        # Check for pawn attacks
        pawn_dir = -1 if by_color == Color.WHITE else 1
        for dc in [-1, 1]:
            check_row, check_col = row + pawn_dir, col + dc
            if self.is_valid_square(check_row, check_col):
                piece = self.get_piece(check_row, check_col)
                if piece and piece[0] == Piece.PAWN and piece[1] == by_color:
                    return True
        
        # Check knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            check_row, check_col = row + dr, col + dc
            if self.is_valid_square(check_row, check_col):
                piece = self.get_piece(check_row, check_col)
                if piece and piece[0] == Piece.KNIGHT and piece[1] == by_color:
                    return True
        
        # Check king attacks (adjacent squares)
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in king_moves:
            check_row, check_col = row + dr, col + dc
            if self.is_valid_square(check_row, check_col):
                piece = self.get_piece(check_row, check_col)
                if piece and piece[0] == Piece.KING and piece[1] == by_color:
                    return True
        
        # Check rook/queen attacks (horizontal/vertical)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            for i in range(1, 8):
                check_row, check_col = row + dr * i, col + dc * i
                if not self.is_valid_square(check_row, check_col):
                    break
                piece = self.get_piece(check_row, check_col)
                if piece:
                    if piece[1] == by_color and piece[0] in [Piece.ROOK, Piece.QUEEN]:
                        return True
                    break
        
        # Check bishop/queen attacks (diagonal)
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            for i in range(1, 8):
                check_row, check_col = row + dr * i, col + dc * i
                if not self.is_valid_square(check_row, check_col):
                    break
                piece = self.get_piece(check_row, check_col)
                if piece:
                    if piece[1] == by_color and piece[0] in [Piece.BISHOP, Piece.QUEEN]:
                        return True
                    break
        
        return False
    
    def is_legal_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Check if a move is legal before making it.
        This validates piece movement rules and check constraints.
        
        Args:
            from_pos: Source square
            to_pos: Destination square
            
        Returns:
            True if move is legal, False otherwise
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check if source square has a piece
        piece = self.get_piece(from_row, from_col)
        if not piece or piece[1] != self.turn:
            return False
        
        # Check if destination is valid
        if not self.is_valid_square(to_row, to_col):
            return False
        
        # Use move generator to check if this is a valid move
        # Import here to avoid circular import
        from .movegen import MoveGenerator
        movegen = MoveGenerator(self)
        legal_moves = movegen.generate_all_moves(self.turn)
        
        # Check if this move is in the list of legal moves
        return (from_pos, to_pos) in legal_moves
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], promotion: Optional[Piece] = None) -> bool:
        """
        Make a move on the board.
        Returns True if move is legal, False otherwise.
        
        This method validates the move before making it.
        """
        # First validate that the move is legal
        if not self.is_legal_move(from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.get_piece(from_row, from_col)
        if not piece or piece[1] != self.turn:
            return False
        
        # Store move information
        captured_piece = self.get_piece(to_row, to_col)
        old_en_passant = self.en_passant_target
        moved_rook = None
        rook_from = None
        rook_to = None
        
        # Handle castling - must happen before moving the king
        if piece[0] == Piece.KING and abs(from_col - to_col) == 2:
            # Kingside castling (O-O)
            if to_col == 6:
                rook_from = (from_row, 7)
                rook_to = (from_row, 5)
            # Queenside castling (O-O-O)
            elif to_col == 2:
                rook_from = (from_row, 0)
                rook_to = (from_row, 3)
            
            if rook_from and rook_to:
                moved_rook = self.get_piece(rook_from[0], rook_from[1])
                if moved_rook and moved_rook[0] == Piece.ROOK and moved_rook[1] == piece[1]:
                    # Move rook first (before king move)
                    self.remove_piece(rook_from[0], rook_from[1])
                    self.set_piece(rook_to[0], rook_to[1], moved_rook[0], moved_rook[1])
        
        # Make the move
        final_piece = piece
        # Handle pawn promotion BEFORE moving
        if piece[0] == Piece.PAWN and ((piece[1] == Color.WHITE and to_row == 0) or (piece[1] == Color.BLACK and to_row == 7)):
            promote_to = promotion if promotion else Piece.QUEEN
            final_piece = (promote_to, piece[1])
        
        self.set_piece(to_row, to_col, final_piece[0], final_piece[1])
        self.remove_piece(from_row, from_col)
        
        # Handle en passant capture
        en_passant_capture_pos = None
        if piece[0] == Piece.PAWN and old_en_passant:
            # En passant target is the square the pawn "passes through"
            # The captured pawn is behind the target square
            ep_row, ep_col = old_en_passant
            if to_pos == (ep_row, ep_col):
                # Determine where the captured pawn is
                # The captured pawn is on the same row as the moving pawn (before move)
                # In standard chess: if white moves to ep square, black pawn is one row "behind" (towards black's side)
                if self.turn == Color.WHITE:
                    capture_row = ep_row + 1  # Black pawn is one row down (higher row number)
                else:
                    capture_row = ep_row - 1  # White pawn is one row up (lower row number)
                
                en_passant_capture_pos = (capture_row, ep_col)
                captured_en_passant = self.get_piece(capture_row, ep_col)
                if captured_en_passant and captured_en_passant[0] == Piece.PAWN:
                    captured_piece = captured_en_passant
                    self.remove_piece(capture_row, ep_col)
        
        # Update en passant target
        self.en_passant_target = None
        if piece[0] == Piece.PAWN and abs(from_row - to_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, from_col)
        
        # Update castling rights
        if piece[0] == Piece.KING:
            if self.turn == Color.WHITE:
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
        elif piece[0] == Piece.ROOK:
            if from_row == 7 and from_col == 0:
                self.castling_rights['Q'] = False
            elif from_row == 7 and from_col == 7:
                self.castling_rights['K'] = False
            elif from_row == 0 and from_col == 0:
                self.castling_rights['q'] = False
            elif from_row == 0 and from_col == 7:
                self.castling_rights['k'] = False
        
        # Check if move leaves own king in check
        if self.is_in_check(self.turn):
            # Undo move
            self.set_piece(from_row, from_col, piece[0], piece[1])
            if captured_piece:
                self.set_piece(to_row, to_col, captured_piece[0], captured_piece[1])
            else:
                self.remove_piece(to_row, to_col)
            # Undo castling rook move
            if moved_rook and rook_from and rook_to:
                self.set_piece(rook_from[0], rook_from[1], moved_rook[0], moved_rook[1])
                self.remove_piece(rook_to[0], rook_to[1])
            # Restore en passant
            self.en_passant_target = old_en_passant
            return False
        
        # Record move
        move_info = {
            'from': from_pos,
            'to': to_pos,
            'piece': piece,
            'captured': captured_piece,
            'promoted': final_piece if final_piece != piece else None,
            'castling': (rook_from, rook_to) if moved_rook else None,
            'en_passant_capture_pos': en_passant_capture_pos if en_passant_capture_pos else None
        }
        self.move_history.append(move_info)
        
        # Update turn
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
        
        if self.turn == Color.WHITE:
            self.fullmove_number += 1
        
        # Update halfmove clock
        if piece[0] == Piece.PAWN or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        return True
    
    def unmake_move(self):
        """Undo the last move"""
        if not self.move_history:
            return
        
        move_info = self.move_history.pop()
        from_pos = move_info['from']
        to_pos = move_info['to']
        piece = move_info['piece']
        captured = move_info.get('captured')
        promoted = move_info.get('promoted')
        castling = move_info.get('castling')
        ep_capture_pos = move_info.get('en_passant_capture_pos')
        
        # Get current turn (before undoing, this is the opponent's turn)
        current_turn = self.turn
        
        # Restore piece to original position (use original piece, not promoted)
        original_piece = piece
        self.set_piece(from_pos[0], from_pos[1], original_piece[0], original_piece[1])
        
        # Restore captured piece or clear square
        if captured:
            if ep_capture_pos:
                # En passant capture - restore pawn to its original position
                self.set_piece(ep_capture_pos[0], ep_capture_pos[1], captured[0], captured[1])
                self.remove_piece(to_pos[0], to_pos[1])
            else:
                # Regular capture - restore to destination square
                self.set_piece(to_pos[0], to_pos[1], captured[0], captured[1])
        else:
            self.remove_piece(to_pos[0], to_pos[1])
        
        # Undo castling
        if castling:
            rook_from, rook_to = castling
            if rook_from and rook_to:
                rook = self.get_piece(rook_to[0], rook_to[1])
                if rook:
                    self.remove_piece(rook_to[0], rook_to[1])
                    self.set_piece(rook_from[0], rook_from[1], rook[0], rook[1])
        
        # Restore turn
        self.turn = Color.BLACK if current_turn == Color.WHITE else Color.WHITE
        
        if current_turn == Color.BLACK:
            self.fullmove_number -= 1
    
    def to_fen(self) -> str:
        """Convert board to FEN string"""
        fen_parts = []
        
        # Piece placement
        for row in range(8):
            rank_str = ""
            empty_count = 0
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    
                    piece_type, color = piece
                    piece_chars = {
                        (Piece.PAWN, Color.WHITE): 'P',
                        (Piece.KNIGHT, Color.WHITE): 'N',
                        (Piece.BISHOP, Color.WHITE): 'B',
                        (Piece.ROOK, Color.WHITE): 'R',
                        (Piece.QUEEN, Color.WHITE): 'Q',
                        (Piece.KING, Color.WHITE): 'K',
                        (Piece.PAWN, Color.BLACK): 'p',
                        (Piece.KNIGHT, Color.BLACK): 'n',
                        (Piece.BISHOP, Color.BLACK): 'b',
                        (Piece.ROOK, Color.BLACK): 'r',
                        (Piece.QUEEN, Color.BLACK): 'q',
                        (Piece.KING, Color.BLACK): 'k',
                    }
                    rank_str += piece_chars[(piece_type, color)]
            
            if empty_count > 0:
                rank_str += str(empty_count)
            fen_parts.append(rank_str)
        
        # Active color
        fen_parts.append('w' if self.turn == Color.WHITE else 'b')
        
        # Castling rights
        castling = ""
        if self.castling_rights['K']:
            castling += 'K'
        if self.castling_rights['Q']:
            castling += 'Q'
        if self.castling_rights['k']:
            castling += 'k'
        if self.castling_rights['q']:
            castling += 'q'
        if not castling:
            castling = '-'
        fen_parts.append(castling)
        
        # En passant
        if self.en_passant_target:
            row, col = self.en_passant_target
            fen_parts.append(f"{self.FILES[col]}{8 - row}")
        else:
            fen_parts.append('-')
        
        # Move counters
        fen_parts.append(str(self.halfmove_clock))
        fen_parts.append(str(self.fullmove_number))
        
        return ' '.join(fen_parts)
    
    def copy(self) -> 'ChessBoard':
        """Create a deep copy of the board"""
        new_board = ChessBoard()
        new_board.board = copy.deepcopy(self.board)
        new_board.turn = self.turn
        new_board.castling_rights = self.castling_rights.copy()
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.move_history = copy.deepcopy(self.move_history)
        return new_board
    
    def __str__(self) -> str:
        """String representation of board"""
        result = "  a b c d e f g h\n"
        for row in range(8):
            result += f"{8 - row} "
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece is None:
                    result += ". "
                else:
                    piece_type, color = piece
                    symbols = {
                        (Piece.PAWN, Color.WHITE): 'P',
                        (Piece.KNIGHT, Color.WHITE): 'N',
                        (Piece.BISHOP, Color.WHITE): 'B',
                        (Piece.ROOK, Color.WHITE): 'R',
                        (Piece.QUEEN, Color.WHITE): 'Q',
                        (Piece.KING, Color.WHITE): 'K',
                        (Piece.PAWN, Color.BLACK): 'p',
                        (Piece.KNIGHT, Color.BLACK): 'n',
                        (Piece.BISHOP, Color.BLACK): 'b',
                        (Piece.ROOK, Color.BLACK): 'r',
                        (Piece.QUEEN, Color.BLACK): 'q',
                        (Piece.KING, Color.BLACK): 'k',
                    }
                    result += symbols[(piece_type, color)] + " "
            result += f"{8 - row}\n"
        result += "  a b c d e f g h"
        return result

