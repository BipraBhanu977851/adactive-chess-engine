"""
Evaluation Function Module

Provides material and positional evaluation for chess positions.
Designed to work with adaptive weights that can be modified
by the adaptive learning system.
"""

from typing import Dict, Optional
from .board import ChessBoard, Piece, Color


class EvaluationFunction:
    """
    Evaluates chess positions using material and positional heuristics.
    Supports adaptive weight modification for style-based play.
    """
    
    # Piece values (centipawns)
    PIECE_VALUES = {
        Piece.PAWN: 100,
        Piece.KNIGHT: 320,
        Piece.BISHOP: 330,
        Piece.ROOK: 500,
        Piece.QUEEN: 900,
        Piece.KING: 20000
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize evaluation function with weights.
        
        Args:
            weights: Dictionary of evaluation weights. If None, uses defaults.
        """
        self.weights = weights if weights else self._get_default_weights()
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Get default evaluation weights"""
        return {
            'material': 1.0,
            'piece_activity': 0.5,
            'king_safety': 0.8,
            'central_control': 0.3,
            'pawn_structure': 0.4,
            'piece_coordination': 0.2,
            'mobility': 0.6,
            'trade_preference': 0.0  # Positive = willing to trade, negative = avoid trades
        }
    
    def evaluate(self, board: ChessBoard, color: Color) -> float:
        """
        Evaluate position from the perspective of the given color.
        
        Evaluation components:
        1. Material: Piece values (most important)
        2. Piece activity: How active pieces are
        3. King safety: How safe the king is
        4. Central control: Control of center squares
        5. Pawn structure: Quality of pawn formation
        6. Piece coordination: How well pieces work together
        7. Mobility: Number of legal moves available
        
        Weights can be adjusted by the adaptive system to match player style.
        
        Args:
            board: Chess board position
            color: Color to evaluate for (WHITE or BLACK)
            
        Returns:
            Evaluation score in centipawns (positive = good for color, negative = bad)
        """
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Material evaluation - most important factor
        material_score = self._evaluate_material(board, color)
        
        # Positional evaluations - these are weighted by adaptive system
        piece_activity = self._evaluate_piece_activity(board, color)
        king_safety = self._evaluate_king_safety(board, color)
        central_control = self._evaluate_central_control(board, color)
        pawn_structure = self._evaluate_pawn_structure(board, color)
        piece_coordination = self._evaluate_piece_coordination(board, color)
        mobility = self._evaluate_mobility(board, color)
        
        # Combine evaluations with adaptive weights
        # Weights are adjusted by WeightAdapter based on player style
        total_score = (
            material_score * self.weights['material'] +
            piece_activity * self.weights['piece_activity'] +
            king_safety * self.weights['king_safety'] +
            central_control * self.weights['central_control'] +
            pawn_structure * self.weights['pawn_structure'] +
            piece_coordination * self.weights['piece_coordination'] +
            mobility * self.weights['mobility']
        )
        
        return total_score
    
    def _evaluate_material(self, board: ChessBoard, color: Color) -> float:
        """
        Evaluate material balance.
        
        Material is the most important evaluation factor.
        Counts piece values for own color, subtracts opponent's piece values.
        
        Piece values (centipawns):
        - Pawn: 100
        - Knight: 320
        - Bishop: 330
        - Rook: 500
        - Queen: 900
        - King: 20000 (not used in material count, but for checkmate detection)
        
        Args:
            board: Chess board position
            color: Color to evaluate for
            
        Returns:
            Material score (positive = more material, negative = less material)
        """
        score = 0.0
        
        # Count all pieces on the board
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_type, piece_color = piece
                    value = self.PIECE_VALUES[piece_type]
                    if piece_color == color:
                        score += value  # Own pieces add to score
                    else:
                        score -= value  # Opponent pieces subtract from score
        
        return score
    
    def _evaluate_piece_activity(self, board: ChessBoard, color: Color) -> float:
        """Evaluate how active pieces are (simplified)"""
        score = 0.0
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Count pieces in central squares
        central_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for row, col in central_squares:
            piece = board.get_piece(row, col)
            if piece:
                if piece[1] == color:
                    score += 20
                else:
                    score -= 20
        
        return score
    
    def _evaluate_king_safety(self, board: ChessBoard, color: Color) -> float:
        """Evaluate king safety"""
        score = 0.0
        king_pos = board.get_king_position(color)
        
        if king_pos:
            row, col = king_pos
            
            # Penalize exposed king (simplified)
            # Count nearby friendly pieces (good)
            friendly_count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    check_row, check_col = row + dr, col + dc
                    if board.is_valid_square(check_row, check_col):
                        piece = board.get_piece(check_row, check_col)
                        if piece and piece[1] == color:
                            friendly_count += 1
            
            score += friendly_count * 15
            
            # Penalize if king is attacked
            if board.is_in_check(color):
                score -= 100
        
        return score
    
    def _evaluate_central_control(self, board: ChessBoard, color: Color) -> float:
        """Evaluate control of central squares"""
        score = 0.0
        central_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        extended_center = [(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 5), (4, 2), (4, 5), (5, 2), (5, 3), (5, 4), (5, 5)]
        
        all_central = central_squares + extended_center
        
        for row, col in all_central:
            piece = board.get_piece(row, col)
            if piece:
                if piece[1] == color:
                    if (row, col) in central_squares:
                        score += 15
                    else:
                        score += 8
        
        return score
    
    def _evaluate_pawn_structure(self, board: ChessBoard, color: Color) -> float:
        """Evaluate pawn structure"""
        score = 0.0
        
        # Count doubled pawns (bad)
        for col in range(8):
            pawn_count = 0
            for row in range(8):
                piece = board.get_piece(row, col)
                if piece and piece[0] == Piece.PAWN and piece[1] == color:
                    pawn_count += 1
            if pawn_count > 1:
                score -= 20 * (pawn_count - 1)
        
        # Reward passed pawns (simplified check)
        direction = -1 if color == Color.WHITE else 1
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece[0] == Piece.PAWN and piece[1] == color:
                    # Check if pawn is passed (no enemy pawns ahead)
                    is_passed = True
                    for check_row in range(row + direction, 8 if direction > 0 else -1, direction):
                        for check_col in [col - 1, col, col + 1]:
                            if board.is_valid_square(check_row, check_col):
                                enemy_piece = board.get_piece(check_row, check_col)
                                if enemy_piece and enemy_piece[0] == Piece.PAWN:
                                    if enemy_piece[1] != color:
                                        is_passed = False
                                        break
                        if not is_passed:
                            break
                    
                    if is_passed:
                        score += 30
        
        return score
    
    def _evaluate_piece_coordination(self, board: ChessBoard, color: Color) -> float:
        """Evaluate piece coordination (simplified)"""
        # This is a simplified version - full implementation would check
        # if pieces protect each other, work together, etc.
        score = 0.0
        
        # Count pieces on same files/ranks (for rooks/queens)
        for row in range(8):
            rook_count = 0
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece[1] == color and piece[0] in [Piece.ROOK, Piece.QUEEN]:
                    rook_count += 1
            if rook_count >= 2:
                score += 15
        
        return score
    
    def _evaluate_mobility(self, board: ChessBoard, color: Color) -> float:
        """Evaluate piece mobility (how many moves pieces can make)"""
        from .movegen import MoveGenerator
        
        movegen = MoveGenerator(board)
        moves = movegen.generate_all_moves(color)
        
        return len(moves) * 2.0  # Each legal move worth 2 centipawns
    
    def update_weights(self, weight_deltas: Dict[str, float]):
        """
        Update evaluation weights.
        
        Args:
            weight_deltas: Dictionary of weight changes to apply
        """
        for key, delta in weight_deltas.items():
            if key in self.weights:
                self.weights[key] = max(0.0, self.weights[key] + delta)
    
    def get_weights(self) -> Dict[str, float]:
        """Get current evaluation weights"""
        return self.weights.copy()
    
    def set_weights(self, weights: Dict[str, float]):
        """Set evaluation weights"""
        self.weights.update(weights)

