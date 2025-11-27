"""
Style Analyzer Module

Analyzes player moves to detect playing style and tendencies with improved accuracy.
"""

from typing import Dict, List, Tuple
from engine.board import ChessBoard, Piece, Color
from player_profile.player_profile import PlayerProfile


class StyleAnalyzer:
    """
    Analyzes player moves to determine playing style characteristics with high accuracy.
    """
    
    def __init__(self):
        """Initialize style analyzer"""
        pass
    
    def analyze_move(self, board: ChessBoard, from_pos: Tuple[int, int], 
                     to_pos: Tuple[int, int], color: Color) -> Dict:
        """
        Analyze a single move for style indicators.
        
        Args:
            board: Chess board before move
            from_pos: Move source square
            to_pos: Move destination square
            color: Color making the move
            
        Returns:
            Dictionary with move analysis data
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = board.get_piece(from_row, from_col)
        target = board.get_piece(to_row, to_col)
        
        # Detect castling
        is_castling = (piece and piece[0] == Piece.KING and abs(from_col - to_col) == 2)
        
        analysis = {
            'is_capture': target is not None,
            'is_check': False,
            'is_castling': is_castling,
            'piece_type': piece[0] if piece else None,
            'target_piece': target[0] if target else None,
            'move_forward': to_row < from_row if color == Color.WHITE else to_row > from_row,
            'central_square': self._is_central_square(to_row, to_col),
            'attacking_value': 0.0,
            'defensive_value': 0.0,
            'piece_value_gain': 0.0 if not target else self._get_piece_value_difference(piece[0], target[0]),
            'from': from_pos,
            'to': to_pos
        }
        
        # Check if move puts opponent in check
        test_board = board.copy()
        if test_board.make_move(from_pos, to_pos):
            analysis['is_check'] = test_board.is_in_check(Color.BLACK if color == Color.WHITE else Color.WHITE)
        
        # Calculate attacking/defensive value
        analysis['attacking_value'] = self._calculate_attacking_value(board, from_pos, to_pos, color)
        analysis['defensive_value'] = self._calculate_defensive_value(board, from_pos, to_pos, color)
        
        return analysis
    
    def update_profile_from_moves(self, profile: PlayerProfile, moves: List[Dict]) -> PlayerProfile:
        """
        Update player profile based on move history with improved accuracy.
        
        Args:
            profile: PlayerProfile to update
            moves: List of move analysis dictionaries
            
        Returns:
            Updated PlayerProfile
        """
        if not moves:
            return profile
        
        total_moves = len(moves)
        
        # Basic statistics
        capture_count = sum(1 for m in moves if m.get('is_capture', False))
        check_count = sum(1 for m in moves if m.get('is_check', False))
        central_moves = sum(1 for m in moves if m.get('central_square', False))
        castling_count = sum(1 for m in moves if m.get('is_castling', False))
        
        # Update basic stats
        profile.capture_rate = capture_count / total_moves if total_moves > 0 else 0.0
        profile.check_rate = check_count / total_moves if total_moves > 0 else 0.0
        profile.castle_rate = castling_count / total_moves if total_moves > 0 else 0.0
        profile.trade_willingness = capture_count / total_moves if total_moves > 0 else 0.5
        
        # ========== AGGRESSION SCORE - Improved Algorithm ==========
        # Aggressive players: frequent captures, checks, forward pawn moves, sacrifices, attacking moves
        aggression_indicators = []
        
        for move in moves:
            move_aggression = 0.0
            
            # 1. Captures (weighted by piece value)
            if move.get('is_capture', False):
                target_val = self._get_piece_value(move.get('target_piece', Piece.PAWN))
                move_aggression += 0.3 + (target_val / 30.0)  # 0.3-0.6 for captures
            
            # 2. Checks (strong attacking indicator)
            if move.get('is_check', False):
                move_aggression += 0.4
            
            # 3. Forward pawn moves (initiative)
            if move.get('piece_type') == Piece.PAWN and move.get('move_forward', False):
                move_aggression += 0.2
            
            # 4. Material sacrifices (negative value gain)
            value_gain = move.get('piece_value_gain', 0)
            if value_gain < -3:  # Sacrificing 3+ points
                move_aggression += 0.5
            elif value_gain < -1:  # Small sacrifice
                move_aggression += 0.2
            
            # 5. High attacking value (threatening pieces)
            attacking_val = move.get('attacking_value', 0)
            if attacking_val > 20:
                move_aggression += 0.3
            elif attacking_val > 10:
                move_aggression += 0.15
            
            # 6. Moving pieces forward (aggressive positioning)
            if move.get('move_forward', False) and move.get('piece_type') in [Piece.QUEEN, Piece.ROOK]:
                move_aggression += 0.15
            
            aggression_indicators.append(move_aggression)
        
        # Calculate average aggression per move
        avg_aggression = sum(aggression_indicators) / total_moves if total_moves > 0 else 0.0
        
        # Normalize to 0-1 scale (typical range is 0.0-1.5)
        profile.aggression_score = min(1.0, max(0.0, 0.2 + avg_aggression * 0.6))
        
        # ========== DEFENSIVE SCORE - Improved Algorithm ==========
        # Defensive players: avoid captures, focus on safety, castling, protecting pieces
        defensive_indicators = []
        
        for move in moves:
            move_defense = 0.0
            
            # 1. Castling (king safety)
            if move.get('is_castling', False):
                move_defense += 0.5
            
            # 2. High defensive value (protecting pieces)
            defensive_val = move.get('defensive_value', 0)
            if defensive_val > 15:
                move_defense += 0.4
            elif defensive_val > 8:
                move_defense += 0.2
            
            # 3. Avoiding bad trades (not capturing when behind)
            value_gain = move.get('piece_value_gain', 0)
            if not move.get('is_capture', False) and value_gain <= 0:
                # Non-capturing move that doesn't lose material
                move_defense += 0.1
            
            # 4. Pawn moves (building structure)
            if move.get('piece_type') == Piece.PAWN and not move.get('is_capture', False):
                move_defense += 0.15
            
            # 5. Retreating pieces (moving away from center/forward)
            if move.get('piece_type') in [Piece.ROOK, Piece.BISHOP, Piece.QUEEN]:
                if not move.get('is_capture', False) and not move.get('central_square', False):
                    if not move.get('move_forward', False):
                        move_defense += 0.1
            
            # 6. Low aggression moves (not attacking)
            move_aggression = aggression_indicators[moves.index(move)] if move in moves else 0.0
            if move_aggression < 0.2:
                move_defense += 0.1
            
            defensive_indicators.append(move_defense)
        
        avg_defense = sum(defensive_indicators) / total_moves if total_moves > 0 else 0.0
        profile.defensive_score = min(1.0, max(0.0, 0.2 + avg_defense * 0.7))
        
        # ========== TACTICAL SCORE - Improved Algorithm ==========
        # Tactical players: checks, material wins, combinations, forks, pins
        tactical_score = 0.0
        tactical_moves = 0
        
        for move in moves:
            move_tactical = 0.0
            
            # 1. Checks (tactical)
            if move.get('is_check', False):
                move_tactical += 0.5
            
            # 2. Material gains (winning pieces)
            value_gain = move.get('piece_value_gain', 0)
            if value_gain >= 5:  # Winning queen or major piece
                move_tactical += 0.6
            elif value_gain >= 3:  # Winning minor piece
                move_tactical += 0.4
            elif value_gain > 0:  # Any material gain
                move_tactical += 0.2
            
            # 3. High attacking value (threatening multiple pieces)
            if move.get('attacking_value', 0) > 25:
                move_tactical += 0.4
            elif move.get('attacking_value', 0) > 15:
                move_tactical += 0.2
            
            # 4. Knight moves to central squares (tactical positioning)
            if move.get('piece_type') == Piece.KNIGHT and move.get('central_square', False):
                move_tactical += 0.15
            
            if move_tactical > 0.2:
                tactical_moves += 1
                tactical_score += move_tactical
        
        profile.tactical_score = min(1.0, max(0.0, 0.2 + (tactical_score / total_moves) * 0.8))
        if tactical_moves > 0:
            profile.tactical_score = max(profile.tactical_score, (tactical_moves / total_moves) * 0.6)
        
        # ========== POSITIONAL SCORE - Improved Algorithm ==========
        # Positional players: central control, piece development, pawn structure, long-term plans
        positional_score = 0.0
        positional_moves = 0
        
        for move in moves:
            move_positional = 0.0
            
            # 1. Central control (non-capturing)
            if move.get('central_square', False) and not move.get('is_capture', False):
                piece_type = move.get('piece_type')
                if piece_type:
                    piece_val = self._get_piece_value(piece_type)
                    move_positional += 0.2 + (piece_val / 50.0)  # More valuable pieces = better
            
            # 2. Piece development (knights, bishops in opening)
            if move.get('piece_type') in [Piece.KNIGHT, Piece.BISHOP]:
                if not move.get('is_capture', False):
                    move_positional += 0.25
            
            # 3. Pawn structure (non-capturing pawn moves)
            if move.get('piece_type') == Piece.PAWN and not move.get('is_capture', False):
                move_positional += 0.15
            
            # 4. Rook moves to open files
            if move.get('piece_type') == Piece.ROOK and not move.get('is_capture', False):
                move_positional += 0.2
            
            # 5. Low tactical value but strategic (not checks, not material gains)
            if not move.get('is_check', False) and move.get('piece_value_gain', 0) <= 0:
                if not move.get('is_capture', False):
                    move_positional += 0.1
            
            if move_positional > 0.15:
                positional_moves += 1
                positional_score += move_positional
        
        profile.positional_score = min(1.0, max(0.0, 0.2 + (positional_score / total_moves) * 0.8))
        if positional_moves > 0:
            profile.positional_score = max(profile.positional_score, (positional_moves / total_moves) * 0.6)
        
        # ========== CENTRAL CONTROL PREFERENCE ==========
        central_score = 0.0
        for move in moves:
            if move.get('central_square', False):
                piece_type = move.get('piece_type')
                if piece_type:
                    piece_val = self._get_piece_value(piece_type)
                    central_score += piece_val / 15.0
        
        profile.central_control_preference = min(1.0, max(0.0, 0.2 + (central_score / total_moves) * 1.2))
        
        # ========== PIECE ACTIVITY PREFERENCE ==========
        active_pieces = sum(1 for m in moves if m.get('piece_type') in [Piece.KNIGHT, Piece.BISHOP, Piece.QUEEN, Piece.ROOK])
        profile.piece_activity_preference = active_pieces / total_moves if total_moves > 0 else 0.5
        
        # ========== KING SAFETY FOCUS ==========
        king_safety_score = 0.0
        for move in moves:
            if move.get('is_castling', False):
                king_safety_score += 0.5
            elif move.get('piece_type') == Piece.KING:
                king_safety_score += 0.2
            elif move.get('defensive_value', 0) > 10:
                king_safety_score += 0.1
        
        profile.king_safety_focus = min(1.0, max(0.0, 0.2 + (king_safety_score / total_moves) * 0.8))
        
        # ========== PAWN STRUCTURE FOCUS ==========
        pawn_moves = sum(1 for m in moves if m.get('piece_type') == Piece.PAWN and not m.get('is_capture', False))
        profile.pawn_structure_focus = pawn_moves / total_moves if total_moves > 0 else 0.5
        
        # ========== ENDGAME SCORE - Improved Algorithm ==========
        # Endgame skill: king activity, pawn advancement, piece coordination, promotion threats
        endgame_score = 0.0
        endgame_moves = 0
        
        for move in moves:
            move_endgame = 0.0
            piece_type = move.get('piece_type')
            
            # 1. King activity (crucial in endgame)
            if piece_type == Piece.KING:
                if move.get('move_forward', False) or move.get('central_square', False):
                    move_endgame += 0.4
                else:
                    move_endgame += 0.2
            
            # 2. Pawn advancement (towards promotion)
            if piece_type == Piece.PAWN:
                if move.get('move_forward', False):
                    # Closer to promotion = more endgame skill
                    to_row = move.get('to', (0, 0))[0]
                    if color == Color.WHITE:
                        # White pawns move towards row 0
                        if to_row <= 2:
                            move_endgame += 0.5  # Close to promotion
                        elif to_row <= 4:
                            move_endgame += 0.3
                    else:
                        # Black pawns move towards row 7
                        if to_row >= 5:
                            move_endgame += 0.5
                        elif to_row >= 3:
                            move_endgame += 0.3
                
                # Pawn captures in endgame
                if move.get('is_capture', False):
                    move_endgame += 0.2
            
            # 3. Promoting pawns (strong endgame)
            if piece_type == Piece.PAWN:
                to_row = move.get('to', (0, 0))[0]
                if (color == Color.WHITE and to_row == 0) or (color == Color.BLACK and to_row == 7):
                    move_endgame += 0.6
            
            # 4. Piece coordination (queen/rook + king)
            if piece_type in [Piece.QUEEN, Piece.ROOK]:
                if move.get('is_capture', False) or move.get('is_check', False):
                    move_endgame += 0.25
            
            if move_endgame > 0.1:
                endgame_moves += 1
                endgame_score += move_endgame
        
        profile.endgame_score = min(1.0, max(0.0, 0.2 + (endgame_score / total_moves) * 1.0))
        if endgame_moves > 0:
            profile.endgame_score = max(profile.endgame_score, (endgame_moves / total_moves) * 0.5)
        
        # ========== MISTAKE CONTROL - Improved Algorithm ==========
        # Blunders: losing significant material, hanging pieces, weak moves
        blunders = 0
        mistakes = 0
        
        for move in moves:
            value_gain = move.get('piece_value_gain', 0)
            
            # Severe blunder: losing 5+ points of material
            if value_gain < -5:
                blunders += 1
            # Mistake: losing 2-5 points
            elif value_gain < -2:
                mistakes += 1
            # Minor mistake: losing 1-2 points
            elif value_gain < -1:
                mistakes += 0.5
        
        # Calculate blunder rate
        total_errors = blunders * 2 + mistakes
        profile.blunder_rate = min(1.0, max(0.0, total_errors / max(total_moves * 2, 1)))
        
        # Mistake control: inverse relationship, but more nuanced
        if blunders == 0 and mistakes == 0:
            profile.mistake_control = 0.9  # Excellent
        elif blunders == 0:
            profile.mistake_control = max(0.7, 1.0 - (mistakes / total_moves) * 0.5)
        else:
            profile.mistake_control = max(0.0, 1.0 - (blunders / total_moves) * 1.2)
        
        return profile
    
    def _is_central_square(self, row: int, col: int) -> bool:
        """Check if square is in central area (d4, d5, e4, e5)"""
        central_rows = [3, 4]
        central_cols = [3, 4]
        return row in central_rows and col in central_cols
    
    def _get_piece_value(self, piece: Piece) -> int:
        """Get material value of piece"""
        values = {
            Piece.PAWN: 1,
            Piece.KNIGHT: 3,
            Piece.BISHOP: 3,
            Piece.ROOK: 5,
            Piece.QUEEN: 9,
            Piece.KING: 100
        }
        return values.get(piece, 0)
    
    def _get_piece_value_difference(self, attacker: Piece, defender: Piece) -> int:
        """Calculate material gain from capture"""
        attacker_val = self._get_piece_value(attacker)
        defender_val = self._get_piece_value(defender)
        return defender_val - attacker_val
    
    def _calculate_attacking_value(self, board: ChessBoard, from_pos: Tuple[int, int], 
                                   to_pos: Tuple[int, int], color: Color) -> float:
        """Calculate how attacking a move is"""
        value = 0.0
        to_row, to_col = to_pos
        
        # Check if move threatens opponent pieces
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Check all adjacent and attackable squares
        for dr in [-2, -1, 0, 1, 2]:
            for dc in [-2, -1, 0, 1, 2]:
                if dr == 0 and dc == 0:
                    continue
                check_row, check_col = to_row + dr, to_col + dc
                if board.is_valid_square(check_row, check_col):
                    piece = board.get_piece(check_row, check_col)
                    if piece and piece[1] == opponent:
                        piece_val = self._get_piece_value(piece[0])
                        # Weight by distance (closer = more threatening)
                        distance = max(abs(dr), abs(dc))
                        value += piece_val * (1.0 / max(distance, 1))
        
        return value
    
    def _calculate_defensive_value(self, board: ChessBoard, from_pos: Tuple[int, int], 
                                   to_pos: Tuple[int, int], color: Color) -> float:
        """Calculate how defensive a move is"""
        value = 0.0
        to_row, to_col = to_pos
        
        # Check if move protects own pieces
        for dr in [-2, -1, 0, 1, 2]:
            for dc in [-2, -1, 0, 1, 2]:
                if dr == 0 and dc == 0:
                    continue
                check_row, check_col = to_row + dr, to_col + dc
                if board.is_valid_square(check_row, check_col):
                    piece = board.get_piece(check_row, check_col)
                    if piece and piece[1] == color:
                        piece_val = self._get_piece_value(piece[0])
                        distance = max(abs(dr), abs(dc))
                        value += piece_val * (1.0 / max(distance, 1))
        
        return value
