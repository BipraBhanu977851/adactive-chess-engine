"""
Adaptive Engine Module

Integrates adaptive learning, style analysis, and weight adaptation
into the chess engine workflow.
"""

from typing import List, Dict, Tuple, Optional
from engine.board import ChessBoard, Color
from engine.evaluation import EvaluationFunction
from engine.search import SearchEngine
from player_profile.player_profile import PlayerProfile
from player_profile.profile_manager import PlayerProfileManager
from .style_analyzer import StyleAnalyzer
from .weight_adapter import WeightAdapter


class AdaptiveEngine:
    """
    Main adaptive engine that combines chess engine with learning capabilities.
    """
    
    def __init__(self, player_id: str, search_depth: int = 4, profiles_dir: str = "profiles"):
        """
        Initialize adaptive engine.
        
        Args:
            player_id: Unique identifier for the player
            search_depth: Maximum search depth for engine
            profiles_dir: Directory for storing player profiles
        """
        self.player_id = player_id
        
        # Initialize components
        self.evaluator = EvaluationFunction()
        self.search_engine = SearchEngine(self.evaluator, search_depth)
        self.profile_manager = PlayerProfileManager(profiles_dir)
        self.style_analyzer = StyleAnalyzer()
        self.weight_adapter = WeightAdapter(self.evaluator)
        
        # Load or create player profile
        # Try to load from database first, then JSON
        from player_profile.database import PlayerDatabase
        db = PlayerDatabase()
        db_profile = db.get_profile(player_id)
        
        if db_profile:
            # Load from database
            self.profile = PlayerProfile.from_database_dict(db_profile)
        else:
            # Load or create from JSON
            self.profile = self.profile_manager.get_or_create_profile(player_id)
        
        # Move history for current game
        # Performance fix: Limit move list to prevent memory bloat and slow processing
        self.MAX_MOVES_IN_GAME = 100  # Maximum moves to keep in memory per game
        self.current_game_moves: List[Dict] = []
        self.board = ChessBoard()
        
        # Apply initial adaptation
        self.update_adaptation()
    
    def make_player_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Record and make a player move.
        
        Process:
        1. Validate it's player's turn
        2. Validate move is legal
        3. Analyze move for style detection
        4. Make the move
        5. Update player profile
        6. Periodically update adaptation
        
        Args:
            from_pos: Move source square (row, col)
            to_pos: Move destination square (row, col)
            
        Returns:
            True if move is legal and made successfully, False otherwise
        """
        # Check if it's player's turn (player is white)
        if self.board.turn != Color.WHITE:
            return False
        
        # Validate move first (without making it) - prevents illegal moves
        if not self.board.is_legal_move(from_pos, to_pos):
            return False
        
        # Analyze move before making it (on current board state)
        # This captures the position before the move for style analysis
        move_analysis = self.style_analyzer.analyze_move(self.board, from_pos, to_pos, Color.WHITE)
        
        # Make the move (make_move also validates, but we already checked for safety)
        if not self.board.make_move(from_pos, to_pos):
            return False  # Move failed (shouldn't happen after validation)
        
        # Store move analysis for profile updates
        move_analysis['color'] = 'white'
        move_analysis['from'] = from_pos
        move_analysis['to'] = to_pos
        self.current_game_moves.append(move_analysis)
        
        # Performance fix: Limit move list size to prevent memory bloat
        if len(self.current_game_moves) > self.MAX_MOVES_IN_GAME:
            # Keep only the most recent moves (remove oldest)
            self.current_game_moves = self.current_game_moves[-self.MAX_MOVES_IN_GAME:]
        
        self.profile.update_stats(move_analysis)
        
        # Update profile periodically (every 5 moves) to avoid too frequent updates
        # Performance fix: Only update if we have enough moves for meaningful analysis
        # Bug fix: Wrap in try-except to prevent engine from stopping if update fails
        if len(self.current_game_moves) >= 5 and len(self.current_game_moves) % 5 == 0:
            try:
                self._update_profile_from_moves()
                self.update_adaptation()  # Adjust engine weights based on new profile
            except Exception as e:
                # Root cause fix: If profile update fails, log error but don't stop game
                # This prevents engine from stopping after 5th move
                print(f"Warning: Profile update failed: {e}")
                print("Game will continue with current profile settings")
                # Continue with game - don't let profile update failure stop the engine
        
        return True
    
    def make_engine_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Generate and make engine move.
        
        Bug fix: Changed return type to Optional to handle None case.
        Root cause: Type hint didn't match actual return value (could return None).
        
        Performance fix: Added fallback mechanism - if search fails, use heuristic move.
        This ensures engine always makes a move and game can continue.
        
        Returns:
            (from_pos, to_pos) tuple of engine move, or None if no move available
        """
        # Check if it's engine's turn (engine plays black)
        if self.board.turn != Color.BLACK:
            return None
        
        # Find best move using search engine
        # Bug fix: Wrap search in try-except to handle any exceptions
        try:
            best_move = self.search_engine.find_best_move(self.board, Color.BLACK)
        except Exception as e:
            # Root cause fix: If search fails (e.g., due to invalid weights), use fallback
            print(f"Warning: Search engine failed: {e}")
            print("Using fallback move selection...")
            best_move = None
        
        if best_move:
            from_pos, to_pos = best_move
            # Make the move - verify it succeeds
            if self.board.make_move(from_pos, to_pos):
                return best_move
            else:
                # Bug: Move failed - try fallback
                print(f"Warning: Engine move {from_pos} -> {to_pos} failed! Trying fallback...")
                # Fall through to fallback mechanism
        
        # Fallback: If search failed or returned invalid move, use heuristic
        # Generate all moves and pick the best one by simple evaluation
        from engine.movegen import MoveGenerator
        movegen = MoveGenerator(self.board)
        moves = movegen.generate_all_moves(Color.BLACK)
        
        if not moves:
            return None  # No legal moves (checkmate or stalemate)
        
        # Fallback: Pick move with highest immediate evaluation
        best_fallback_move = None
        best_fallback_score = float('-inf')
        
        for move in moves:
            from_pos, to_pos = move
            if self.board.make_move(from_pos, to_pos):
                # Evaluate position
                score = self.evaluator.evaluate(self.board, Color.BLACK)
                self.board.unmake_move()
                
                if score > best_fallback_score:
                    best_fallback_score = score
                    best_fallback_move = move
        
        # Make the fallback move
        if best_fallback_move:
            from_pos, to_pos = best_fallback_move
            if self.board.make_move(from_pos, to_pos):
                return best_fallback_move
        
        # Last resort: return first legal move
        if moves:
            from_pos, to_pos = moves[0]
            if self.board.make_move(from_pos, to_pos):
                return moves[0]
        
        return None
    
    def update_adaptation(self):
        """
        Update evaluation weights based on current player profile.
        This makes the engine adapt to the player's style.
        
        Bug fix: Added error handling to prevent invalid weights from breaking search.
        """
        try:
            self.weight_adapter.apply_adaptation(self.profile)
        except Exception as e:
            # Root cause fix: If adaptation fails, log error but don't crash
            # Invalid weights could cause search to fail or return NaN/inf
            print(f"Warning: Weight adaptation failed: {e}")
            print("Engine will continue with previous weights")
            # Don't update weights if adaptation fails - keep current weights
            pass
    
    def _update_profile_from_moves(self):
        """
        Update profile statistics from recent moves.
        Analyzes the last 10-20 moves to update style indicators.
        
        Performance fix: Only analyze recent moves, not entire game history.
        This prevents slowdown as game progresses.
        
        Bug fix: Added error handling to prevent crashes.
        """
        if len(self.current_game_moves) >= 5:
            try:
                # Performance fix: Analyze only last 20 moves max (not all moves)
                # This keeps analysis fast even in long games
                recent_moves = self.current_game_moves[-20:]  # Last 20 moves max
                self.profile = self.style_analyzer.update_profile_from_moves(self.profile, recent_moves)
            except Exception as e:
                # Root cause fix: If style analysis fails, log but don't crash
                print(f"Warning: Style analysis failed: {e}")
                # Keep existing profile - don't update if analysis fails
                pass
    
    def start_new_game(self):
        """Start a new game"""
        self.board = ChessBoard()
        self.current_game_moves = []
        self.profile.record_game_start()
        self.profile_manager.save_profile(self.profile)
        self.update_adaptation()
    
    def end_game(self):
        """End current game and save profile to database and JSON"""
        if len(self.current_game_moves) >= 5:
            self.profile = self.style_analyzer.update_profile_from_moves(self.profile, self.current_game_moves)
        
        # Save to JSON (existing method)
        self.profile_manager.save_profile(self.profile)
        
        # Also save to database
        from player_profile.database import PlayerDatabase
        db = PlayerDatabase()
        
        # Get database representation
        db_data = self.profile.get_database_dict()
        db_data['player_id'] = self.player_id
        
        # Update database
        existing = db.get_profile(self.player_id)
        if existing:
            # Calculate game statistics for this game
            game_stats = {
                'aggressive': db_data['aggressive'],
                'defensive': db_data['defensive'],
                'positional': db_data['positional'],
                'tactical': db_data['tactical'],
                'endgame': db_data.get('endgame', 50.0),
                'blunder_rate': db_data['blunder_rate'],
                'games_played': 1,  # Increment by 1
                'moves_recorded': len(self.current_game_moves)
            }
            db.update_after_game(self.player_id, game_stats)
        else:
            # Create new profile
            db.create_profile(self.player_id, self.profile.player_name, {
                'aggressive': db_data['aggressive'],
                'defensive': db_data['defensive'],
                'positional': db_data['positional'],
                'tactical': db_data['tactical'],
                'endgame': db_data.get('endgame', 50.0),
                'mistake_control': db_data['mistake_control'],
                'blunder_rate': db_data['blunder_rate']
            })
        
        self.current_game_moves = []
    
    def get_player_style_info(self) -> Dict:
        """Get current player style information"""
        return {
            'primary_style': self.profile.get_primary_style(),
            'style_percentages': self.profile.get_style_percentages(),
            'adaptation_explanation': self.weight_adapter.get_adaptation_explanation(self.profile)
        }
    
    def set_search_depth(self, depth: int):
        """Set engine search depth"""
        self.search_engine.set_depth(depth)

