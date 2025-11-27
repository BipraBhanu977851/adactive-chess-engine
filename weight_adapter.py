"""
Weight Adapter Module

Dynamically adjusts evaluation weights based on detected player style.
"""

from typing import Dict
from player_profile.player_profile import PlayerProfile
from engine.evaluation import EvaluationFunction


class WeightAdapter:
    """
    Adapts evaluation weights based on player style to create
    challenging and appropriate gameplay.
    """
    
    def __init__(self, base_evaluator: EvaluationFunction):
        """
        Initialize weight adapter.
        
        Args:
            base_evaluator: Base evaluation function to adapt
        """
        self.base_evaluator = base_evaluator
        self.original_weights = base_evaluator.get_weights().copy()
    
    def adapt_to_player(self, profile: PlayerProfile) -> Dict[str, float]:
        """
        Generate adapted weights based on player profile.
        
        Args:
            profile: PlayerProfile instance
            
        Returns:
            Dictionary of adapted weights
        """
        # Start with original weights
        adapted_weights = self.original_weights.copy()
        
        primary_style = profile.get_primary_style()
        
        # Adaptation logic based on player style
        if primary_style == 'aggressive':
            # Against aggressive players: increase defense and king safety
            adapted_weights['king_safety'] += 0.3
            adapted_weights['piece_activity'] -= 0.2
            adapted_weights['central_control'] += 0.2
            adapted_weights['trade_preference'] -= 0.3  # Avoid unnecessary trades
            
        elif primary_style == 'defensive':
            # Against defensive players: increase attack and central control
            adapted_weights['central_control'] += 0.3
            adapted_weights['piece_activity'] += 0.2
            adapted_weights['king_safety'] -= 0.1
            adapted_weights['trade_preference'] += 0.2  # Seek trades when advantageous
            
        elif primary_style == 'tactical':
            # Against tactical players: focus on solid positions and avoid traps
            adapted_weights['pawn_structure'] += 0.3
            adapted_weights['king_safety'] += 0.2
            adapted_weights['piece_coordination'] += 0.2
            adapted_weights['mobility'] -= 0.1
            
        elif primary_style == 'positional':
            # Against positional players: increase piece activity and tactics
            adapted_weights['piece_activity'] += 0.3
            adapted_weights['mobility'] += 0.2
            adapted_weights['central_control'] -= 0.1
            adapted_weights['trade_preference'] += 0.1
            
        # Fine-tune based on specific tendencies
        if profile.trade_willingness > 0.6:
            # Player likes trades - be more selective
            adapted_weights['trade_preference'] -= 0.2
        elif profile.trade_willingness < 0.4:
            # Player avoids trades - seek favorable trades
            adapted_weights['trade_preference'] += 0.2
        
        if profile.king_safety_focus > 0.6:
            # Player focuses on king safety - apply more pressure
            adapted_weights['piece_activity'] += 0.15
            adapted_weights['mobility'] += 0.1
        
        if profile.central_control_preference > 0.6:
            # Player likes center - contest it more
            adapted_weights['central_control'] += 0.15
        else:
            # Player ignores center - exploit it
            adapted_weights['central_control'] += 0.2
        
        # Ensure weights are positive and valid (not NaN or inf)
        # Bug fix: Validate weights to prevent search engine failures
        import math
        for key in adapted_weights:
            value = adapted_weights[key]
            # Check for NaN or infinity
            if math.isnan(value) or math.isinf(value):
                # Reset to original weight if invalid
                adapted_weights[key] = self.original_weights.get(key, 1.0)
            else:
                # Ensure positive
                adapted_weights[key] = max(0.0, value)
        
        return adapted_weights
    
    def apply_adaptation(self, profile: PlayerProfile):
        """
        Apply weight adaptation to the evaluation function.
        
        Args:
            profile: PlayerProfile instance
        """
        adapted_weights = self.adapt_to_player(profile)
        self.base_evaluator.set_weights(adapted_weights)
    
    def reset_weights(self):
        """Reset weights to original values"""
        self.base_evaluator.set_weights(self.original_weights.copy())
    
    def get_adaptation_explanation(self, profile: PlayerProfile) -> str:
        """
        Get human-readable explanation of weight adaptations.
        
        Args:
            profile: PlayerProfile instance
            
        Returns:
            Explanation string
        """
        primary_style = profile.get_primary_style()
        adapted_weights = self.adapt_to_player(profile)
        
        explanations = []
        
        for key, value in adapted_weights.items():
            original = self.original_weights.get(key, 0)
            delta = value - original
            if abs(delta) > 0.1:
                if delta > 0:
                    explanations.append(f"Increased {key.replace('_', ' ')} by {delta:.2f}")
                else:
                    explanations.append(f"Decreased {key.replace('_', ' ')} by {abs(delta):.2f}")
        
        if explanations:
            return f"Adapting to {primary_style} player: " + "; ".join(explanations)
        else:
            return f"No significant adaptation needed for {primary_style} player"

