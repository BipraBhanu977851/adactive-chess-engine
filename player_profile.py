"""
Player Profile Data Structure

Stores statistical information about a player's style and tendencies.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import json


@dataclass
class PlayerProfile:
    """
    Represents a player's profile with statistical tendencies
    and gameplay style characteristics.
    """
    player_id: str
    player_name: str = "Unknown"
    
    # Game statistics
    games_played: int = 0
    moves_recorded: int = 0
    
    # Style indicators (0.0 to 1.0, stored as 0-100 in database)
    aggression_score: float = 0.5  # How aggressive the player is
    defensive_score: float = 0.5   # How defensive the player is
    tactical_score: float = 0.5    # Preference for tactical play
    positional_score: float = 0.5  # Preference for positional play
    endgame_score: float = 0.5     # Endgame playing strength
    mistake_control: float = 0.5   # Mistake control (100 - blunder_rate)
    blunder_rate: float = 0.0      # Blunder rate percentage
    
    # Tendency scores
    trade_willingness: float = 0.5      # Willingness to trade pieces (0=avoid, 1=eager)
    king_safety_focus: float = 0.5      # How much player focuses on king safety
    central_control_preference: float = 0.5  # Preference for central control
    piece_activity_preference: float = 0.5   # Preference for active pieces
    pawn_structure_focus: float = 0.5        # Focus on pawn structure
    
    # Move statistics
    average_move_time: float = 0.0  # Average time per move (seconds)
    capture_rate: float = 0.0       # Percentage of moves that are captures
    check_rate: float = 0.0         # Percentage of moves that are checks
    castle_rate: float = 0.0        # Percentage of games where player castles
    
    # Move history (for analysis)
    recent_moves: List[Dict] = field(default_factory=list)
    recent_positions: List[str] = field(default_factory=list)
    
    # Last update timestamp
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlayerProfile':
        """Create profile from dictionary"""
        # Handle list fields
        recent_moves = data.get('recent_moves', [])
        recent_positions = data.get('recent_positions', [])
        
        return cls(
            player_id=data['player_id'],
            player_name=data.get('player_name', 'Unknown'),
            games_played=data.get('games_played', 0),
            moves_recorded=data.get('moves_recorded', 0),
            aggression_score=data.get('aggression_score', 0.5),
            defensive_score=data.get('defensive_score', 0.5),
            tactical_score=data.get('tactical_score', 0.5),
            positional_score=data.get('positional_score', 0.5),
            endgame_score=data.get('endgame_score', 0.5),
            mistake_control=data.get('mistake_control', 0.5),
            blunder_rate=data.get('blunder_rate', 0.0),
            trade_willingness=data.get('trade_willingness', 0.5),
            king_safety_focus=data.get('king_safety_focus', 0.5),
            central_control_preference=data.get('central_control_preference', 0.5),
            piece_activity_preference=data.get('piece_activity_preference', 0.5),
            pawn_structure_focus=data.get('pawn_structure_focus', 0.5),
            average_move_time=data.get('average_move_time', 0.0),
            capture_rate=data.get('capture_rate', 0.0),
            check_rate=data.get('check_rate', 0.0),
            castle_rate=data.get('castle_rate', 0.0),
            recent_moves=recent_moves,
            recent_positions=recent_positions,
            last_updated=data.get('last_updated')
        )
    
    def get_primary_style(self) -> str:
        """
        Determine primary playing style based on scores.
        
        Returns:
            Style string: 'aggressive', 'defensive', 'tactical', 'positional', or 'balanced'
        """
        if self.aggression_score > 0.65:
            return 'aggressive'
        elif self.defensive_score > 0.65:
            return 'defensive'
        elif self.tactical_score > 0.65:
            return 'tactical'
        elif self.positional_score > 0.65:
            return 'positional'
        else:
            return 'balanced'
    
    def get_style_percentages(self) -> Dict[str, float]:
        """
        Get style characteristics as percentages.
        
        Returns the 5 main indicators:
        - Aggressive: How often player makes attacking moves
        - Defensive: How often player focuses on safety
        - Tactical: Preference for tactical combinations
        - Positional: Preference for long-term positional play
        - Mistake Control: How well player avoids blunders
        
        Returns:
            Dictionary with style percentages (0-100 scale)
        """
        return {
            'aggressive': self.aggression_score * 100,
            'defensive': self.defensive_score * 100,
            'tactical': self.tactical_score * 100,
            'positional': self.positional_score * 100,
            'endgame': self.endgame_score * 100,
            'mistake_control': self.mistake_control * 100
        }
    
    def get_database_dict(self) -> Dict:
        """
        Get profile data as dictionary for database storage.
        Returns values in 0-100 scale.
        """
        return {
            'aggressive': self.aggression_score * 100,
            'defensive': self.defensive_score * 100,
            'positional': self.positional_score * 100,
            'tactical': self.tactical_score * 100,
            'endgame': self.endgame_score * 100,
            'mistake_control': self.mistake_control * 100,
            'blunder_rate': self.blunder_rate * 100,
            'games_played': self.games_played,
            'moves_recorded': self.moves_recorded,
            'player_name': self.player_name
        }
    
    @classmethod
    def from_database_dict(cls, data: Dict) -> 'PlayerProfile':
        """
        Create PlayerProfile from database dictionary.
        Assumes values are in 0-100 scale.
        """
        return cls(
            player_id=data['player_id'],
            player_name=data.get('player_name', 'Unknown'),
            games_played=data.get('games_played', 0),
            moves_recorded=data.get('moves_recorded', 0),
            aggression_score=data.get('aggressive', 50.0) / 100.0,
            defensive_score=data.get('defensive', 50.0) / 100.0,
            tactical_score=data.get('tactical', 50.0) / 100.0,
            positional_score=data.get('positional', 50.0) / 100.0,
            endgame_score=data.get('endgame', 50.0) / 100.0,
            mistake_control=data.get('mistake_control', 50.0) / 100.0,
            blunder_rate=data.get('blunder_rate', 0.0) / 100.0,
            last_updated=data.get('last_updated')
        )
    
    def update_stats(self, move_data: Dict):
        """
        Update statistics based on a move.
        
        Args:
            move_data: Dictionary containing move information
        """
        self.moves_recorded += 1
        
        # Update capture rate
        if move_data.get('is_capture', False):
            current_captures = self.capture_rate * (self.moves_recorded - 1)
            self.capture_rate = (current_captures + 1) / self.moves_recorded
        
        # Update check rate
        if move_data.get('is_check', False):
            current_checks = self.check_rate * (self.moves_recorded - 1)
            self.check_rate = (current_checks + 1) / self.moves_recorded
        
        # Update blunder rate (if move is a blunder)
        if move_data.get('piece_value_gain', 0) < -5:  # Lost significant material
            current_blunders = self.blunder_rate * (self.moves_recorded - 1)
            self.blunder_rate = (current_blunders + 1) / self.moves_recorded
            self.mistake_control = max(0.0, min(1.0, 1.0 - self.blunder_rate))
        
        # Store recent move
        self.recent_moves.append(move_data)
        if len(self.recent_moves) > 100:  # Keep last 100 moves
            self.recent_moves.pop(0)
    
    def record_game_start(self):
        """Record that a new game has started"""
        self.games_played += 1

