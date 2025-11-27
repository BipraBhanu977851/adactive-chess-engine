"""
Search Algorithm Module

Implements optimized minimax search with alpha-beta pruning,
move ordering, and other optimizations for finding the best move.
"""

from typing import Optional, Tuple, Dict, List
from .board import ChessBoard, Color, Piece
from .movegen import MoveGenerator
from .evaluation import EvaluationFunction


class SearchEngine:
    """
    Chess search engine using optimized minimax with alpha-beta pruning.
    """
    
    def __init__(self, evaluator: EvaluationFunction, max_depth: int = 4):
        """
        Initialize search engine with optimizations.
        
        Args:
            evaluator: Evaluation function instance
            max_depth: Maximum search depth (default: 4)
        """
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.nodes_searched = 0
        
        # Heuristic optimizations for faster search:
        # - Transposition table: cache evaluated positions
        # - Killer moves: moves that caused beta cutoffs (likely good in similar positions)
        # - History table: track which moves are good in general
        self.transposition_table = {}  # Simple TT for position caching
        self.killer_moves = {}  # Killer move heuristic - moves that cause cutoffs
        self.history_table = {}  # History heuristic - track move success rates
        self.max_quiescence_depth = 3  # Max depth for quiescence search (captures only)
        
        # Performance optimization: limit transposition table size
        self.max_tt_size = 10000  # Prevent memory bloat
        
        # Time constraint: Maximum nodes to search before returning best move found
        # This prevents infinite loops or extremely long searches
        self.max_nodes_per_move = 50000  # Limit nodes searched per move
    
    def find_best_move(self, board: ChessBoard, color: Color) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Find the best move for the given color using optimized minimax with alpha-beta pruning.
        
        Algorithm:
        1. Generate all legal moves
        2. Order moves (best first) for better pruning
        3. For each move:
           - Make the move
           - Search opponent's responses (minimax)
           - Undo the move
           - Track best move and update alpha
           - Prune if beta <= alpha (opponent won't allow this line)
        
        Performance fix: Uses iterative deepening with node limits to prevent hanging.
        If search takes too long, returns best move found so far.
        
        Args:
            board: Current chess position
            color: Color to find move for
            
        Returns:
            Best move as (from_pos, to_pos) tuple, or None if no moves available
        """
        # Reset search statistics
        self.nodes_searched = 0
        
        # Generate all legal moves
        movegen = MoveGenerator(board)
        moves = movegen.generate_all_moves(color)
        
        if not moves:
            return None  # No legal moves (checkmate or stalemate)
        
        # Performance fix: If only one move, return it immediately (no search needed)
        if len(moves) == 1:
            return moves[0]
        
        # Order moves for better alpha-beta pruning
        # Good move ordering dramatically reduces nodes searched
        ordered_moves = self._order_moves(board, moves, color)
        
        # Performance fix: Use iterative deepening - start shallow, go deeper if time allows
        # This ensures we always have a move ready, even if search is interrupted
        best_move = ordered_moves[0]  # Default to best-ordered move (heuristic fallback)
        best_score = float('-inf')
        
        # Try iterative deepening: search at depth 1, then 2, then 3, etc.
        # This ensures we have a move quickly, and improve it if time allows
        for search_depth in range(1, self.max_depth + 1):
            # Reset for this depth
            alpha = float('-inf')
            beta = float('inf')
            depth_best_move = None
            depth_best_score = float('-inf')
            
            # Try each move at this depth
            for move in ordered_moves:
                # Check node limit to prevent hanging
                if self.nodes_searched >= self.max_nodes_per_move:
                    # Return best move found so far
                    return best_move if best_move else ordered_moves[0]
                
                from_pos, to_pos = move
                
                # Make move on board
                if not board.make_move(from_pos, to_pos):
                    continue  # Skip illegal moves
                
                # Search opponent's responses
                opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
                score = self._minimax(board, search_depth - 1, alpha, beta, 
                                    opponent, False)
                
                # Undo move
                board.unmake_move()
                
                # Update best move for this depth
                if score > depth_best_score:
                    depth_best_score = score
                    depth_best_move = move
                    alpha = max(alpha, score)
                    
                    # Beta cutoff
                    if beta <= alpha:
                        break
                
                # Check node limit again
                if self.nodes_searched >= self.max_nodes_per_move:
                    break
            
            # Update overall best move if this depth found something better
            if depth_best_move and depth_best_score > best_score:
                best_move = depth_best_move
                best_score = depth_best_score
            
            # If we found a very good move early, we can stop (aspiration window)
            if best_score > 1000:  # Significant advantage
                break
        
        return best_move if best_move else ordered_moves[0]
    
    def _order_moves(self, board: ChessBoard, moves: List[Tuple[Tuple[int, int], Tuple[int, int]]], 
                     color: Color) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Order moves to improve alpha-beta pruning efficiency.
        Good move ordering dramatically reduces nodes searched.
        
        Priority order:
        1. Captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
        2. Killer moves (moves that caused beta cutoffs)
        3. History heuristic (moves that were good in similar positions)
        4. Central squares (good positional moves)
        5. Other moves
        
        Args:
            board: Current board position
            moves: List of moves to order
            color: Color making the move
            
        Returns:
            Ordered list of moves (best first)
        """
        scored_moves = []
        
        for move in moves:
            from_pos, to_pos = move
            score = 0
            
            # 1. CAPTURES - Highest priority (MVV-LVA heuristic)
            # Most Valuable Victim - Least Valuable Attacker
            # Capturing a queen with a pawn is better than capturing a pawn with a queen
            captured = board.get_piece(to_pos[0], to_pos[1])
            if captured:
                piece = board.get_piece(from_pos[0], from_pos[1])
                if piece:
                    victim_value = self._piece_value(captured[0])
                    attacker_value = self._piece_value(piece[0])
                    # Higher score for better captures (capturing valuable pieces with less valuable ones)
                    score += 10000 + (victim_value - attacker_value)
            
            # 2. KILLER MOVES - Moves that caused beta cutoffs in similar positions
            move_key = (from_pos, to_pos)
            if move_key in self.killer_moves:
                score += 1000
            
            # 3. HISTORY HEURISTIC - Moves that were good in past searches
            if move_key in self.history_table:
                score += self.history_table[move_key] * 100
            
            # 4. CENTRAL SQUARES - Good positional moves
            # Central control is important in chess
            if to_pos[0] in [3, 4] and to_pos[1] in [3, 4]:
                score += 50
            
            # 5. PIECE ACTIVITY - Moving pieces forward (for pawns)
            piece = board.get_piece(from_pos[0], from_pos[1])
            if piece and piece[0] == 1:  # Pawn
                if color == Color.WHITE and to_pos[0] < from_pos[0]:
                    score += 10  # White pawns move up (decreasing row)
                elif color == Color.BLACK and to_pos[0] > from_pos[0]:
                    score += 10  # Black pawns move down (increasing row)
            
            scored_moves.append((score, move))
        
        # Sort by score (descending) - best moves first for better pruning
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in scored_moves]
    
    def _piece_value(self, piece: Piece) -> int:
        """Get piece value for move ordering"""
        values = {
            Piece.PAWN: 100,
            Piece.KNIGHT: 320,
            Piece.BISHOP: 330,
            Piece.ROOK: 500,
            Piece.QUEEN: 900,
            Piece.KING: 20000
        }
        return values.get(piece, 0)
    
    def _minimax(self, board: ChessBoard, depth: int, alpha: float, beta: float, 
                 color: Color, maximizing: bool) -> float:
        """
        Optimized minimax algorithm with alpha-beta pruning and move ordering.
        
        Alpha-beta pruning: Skip branches that can't improve the best move.
        - Alpha: Best score maximizing player can guarantee
        - Beta: Best score minimizing player can guarantee
        - If alpha >= beta, we can prune (cutoff) this branch
        
        Move ordering: Search best moves first to get more cutoffs.
        
        Performance fix: Checks node limit to prevent infinite loops.
        
        Args:
            board: Current chess position
            depth: Remaining search depth
            alpha: Alpha value for pruning (best score for maximizing player)
            beta: Beta value for pruning (best score for minimizing player)
            color: Current player color
            maximizing: True if maximizing player, False if minimizing
            
        Returns:
            Evaluation score (positive favors maximizing player)
        """
        self.nodes_searched += 1
        
        # Performance fix: Check node limit to prevent hanging
        if self.nodes_searched >= self.max_nodes_per_move:
            # Return current evaluation as fallback
            score = self.evaluator.evaluate(board, color)
            return score if maximizing else -score
        
        # Terminal conditions
        movegen = MoveGenerator(board)
        moves = movegen.generate_all_moves(color)
        
        # Check for checkmate or stalemate first
        if not moves:
            if board.is_in_check(color):
                # Checkmate
                return float('-inf') if maximizing else float('inf')
            return 0.0  # Stalemate
        
        # Quiescence search at depth 0 (search captures only)
        # Prevents "horizon effect" - evaluating positions with hanging pieces
        # Only searches captures to avoid evaluating "quiet" positions incorrectly
        if depth == 0:
            return self._quiescence_search(board, alpha, beta, color, maximizing, self.max_quiescence_depth)
        
        # Order moves for better pruning
        ordered_moves = self._order_moves(board, moves, color)
        
        if maximizing:
            max_score = float('-inf')
            for move in ordered_moves:
                from_pos, to_pos = move
                
                if not board.make_move(from_pos, to_pos):
                    continue
                
                score = self._minimax(board, depth - 1, alpha, beta,
                                    Color.BLACK if color == Color.WHITE else Color.WHITE,
                                    False)
                
                board.unmake_move()
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    # Beta cutoff - this branch can't improve the best move
                    # Record as killer move for future move ordering
                    self.killer_moves[(from_pos, to_pos)] = depth
                    # Update history heuristic
                    move_key = (from_pos, to_pos)
                    self.history_table[move_key] = self.history_table.get(move_key, 0) + depth
                    break
            
            return max_score
        else:
            min_score = float('inf')
            for move in ordered_moves:
                from_pos, to_pos = move
                
                if not board.make_move(from_pos, to_pos):
                    continue
                
                score = self._minimax(board, depth - 1, alpha, beta,
                                    Color.BLACK if color == Color.WHITE else Color.WHITE,
                                    True)
                
                board.unmake_move()
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    # Alpha cutoff - this branch can't improve the best move
                    # Record as killer move for future move ordering
                    self.killer_moves[(from_pos, to_pos)] = depth
                    # Update history heuristic
                    move_key = (from_pos, to_pos)
                    self.history_table[move_key] = self.history_table.get(move_key, 0) + depth
                    break
            
            return min_score
    
    def _quiescence_search(self, board: ChessBoard, alpha: float, beta: float,
                          color: Color, maximizing: bool, depth: int = 3) -> float:
        """
        Quiescence search - search captures to avoid horizon effect.
        
        Problem: At depth 0, we might evaluate a position where a piece is hanging.
        Solution: Continue searching only captures until position is "quiet" (no captures).
        
        This prevents the "horizon effect" where the engine thinks a position is good
        because it doesn't see the capture coming.
        
        Args:
            board: Current chess position
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            color: Current player color
            maximizing: True if maximizing player
            depth: Remaining quiescence depth
            
        Returns:
            Evaluation score after searching captures
        """
        # Evaluate position (stand pat score)
        score = self.evaluator.evaluate(board, color)
        if not maximizing:
            score = -score
        
        # Stand pat if score is good enough (beta cutoff for maximizing, alpha cutoff for minimizing)
        # This is the "stand pat" optimization - if current position is already good enough, don't search
        if maximizing:
            if score >= beta:
                return beta  # Beta cutoff - position is too good, opponent won't allow it
            alpha = max(alpha, score)  # Update alpha with best score found
        else:
            if score <= alpha:
                return alpha  # Alpha cutoff - position is too bad, we won't allow it
            beta = min(beta, score)  # Update beta with best score found
        
        # Stop quiescence search at max depth
        if depth <= 0:
            return score
        
        # Only search captures (not quiet moves)
        # This is the key to quiescence search - we only continue searching if there are captures
        movegen = MoveGenerator(board)
        all_moves = movegen.generate_all_moves(color)
        capture_moves = [m for m in all_moves if board.get_piece(m[1][0], m[1][1]) is not None]
        
        # If no captures, position is "quiet" - return evaluation
        if not capture_moves:
            return score
        
        # Order captures by MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        # This improves pruning efficiency
        ordered_captures = self._order_moves(board, capture_moves, color)
        
        if maximizing:
            for move in ordered_captures:
                from_pos, to_pos = move
                if not board.make_move(from_pos, to_pos):
                    continue
                
                move_score = self._quiescence_search(board, alpha, beta,
                                                   Color.BLACK if color == Color.WHITE else Color.WHITE,
                                                   False, depth - 1)
                board.unmake_move()
                
                score = max(score, move_score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    break
            
            return score
        else:
            for move in ordered_captures:
                from_pos, to_pos = move
                if not board.make_move(from_pos, to_pos):
                    continue
                
                move_score = self._quiescence_search(board, alpha, beta,
                                                   Color.BLACK if color == Color.WHITE else Color.WHITE,
                                                   True, depth - 1)
                board.unmake_move()
                
                score = min(score, move_score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    break
            
            return score
    
    def set_depth(self, depth: int):
        """Set maximum search depth"""
        self.max_depth = depth
    
    def get_nodes_searched(self) -> int:
        """Get number of nodes searched in last search"""
        return self.nodes_searched

