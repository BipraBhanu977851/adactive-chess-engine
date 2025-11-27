# Adaptive Learning System Documentation

## Overview

The Adaptive Chess Engine learns from player moves and dynamically adjusts its evaluation function to provide challenging gameplay tailored to each player's style. This document explains how the learning system works.

## Learning Process

### 1. Move Analysis

Every player move is analyzed to extract style indicators:

```python
move_analysis = {
    'is_capture': bool,           # Is the move a capture?
    'is_check': bool,              # Does the move give check?
    'piece_type': Piece,           # What piece is moving?
    'target_piece': Piece,         # What piece is captured (if any)?
    'move_forward': bool,          # Is the move forward?
    'central_square': bool,        # Is the destination central?
    'attacking_value': float,      # How attacking is the move?
    'defensive_value': float,      # How defensive is the move?
    'piece_value_gain': int        # Material gain from capture
}
```

### 2. Style Detection

The engine tracks four primary style dimensions:

#### Aggression Score (0.0 - 1.0)
- **Increased by:**
  - Captures (+0.5 per capture)
  - Checks (+0.3 per check)
  - High attacking value moves (+0.2)
- **Interpretation:** Higher values indicate aggressive play

#### Defensive Score (0.0 - 1.0)
- **Increased by:**
  - High defensive value moves (+0.4)
  - Non-capturing pawn moves (+0.1)
- **Interpretation:** Higher values indicate defensive play

#### Tactical Score (0.0 - 1.0)
- **Increased by:**
  - Checks
  - Piece exchanges with material gain
- **Interpretation:** Higher values indicate tactical play

#### Positional Score (0.0 - 1.0)
- **Increased by:**
  - Moves to central squares (non-capturing)
- **Interpretation:** Higher values indicate positional play

### 3. Tendency Analysis

Additional tendencies are tracked:

#### Trade Willingness (0.0 - 1.0)
- Calculated as: `capture_count / total_moves`
- **0.0-0.4**: Avoids trades
- **0.4-0.6**: Balanced
- **0.6-1.0**: Seeks trades

#### King Safety Focus (0.0 - 1.0)
- Measures how much player focuses on king safety
- Based on defensive moves near king

#### Central Control Preference (0.0 - 1.0)
- Calculated as: `central_moves / total_moves`
- Measures preference for central squares

#### Piece Activity Preference (0.0 - 1.0)
- Calculated as: `active_piece_moves / total_moves`
- Measures preference for moving knights, bishops, queens

### 4. Primary Style Determination

The engine determines the primary style based on style scores:

```python
if aggression_score > 0.65:
    primary_style = 'aggressive'
elif defensive_score > 0.65:
    primary_style = 'defensive'
elif tactical_score > 0.65:
    primary_style = 'tactical'
elif positional_score > 0.65:
    primary_style = 'positional'
else:
    primary_style = 'balanced'
```

## Weight Adaptation

The engine adapts its evaluation weights based on the detected style:

### Against Aggressive Players

**Strategy:** Increase defense and king safety

**Weight Changes:**
```python
weights['king_safety'] += 0.3      # Prioritize king safety
weights['piece_activity'] -= 0.2   # Reduce risky piece activity
weights['central_control'] += 0.2  # Control center more
weights['trade_preference'] -= 0.3 # Avoid unnecessary trades
```

**Rationale:** Aggressive players often attack, so the engine should focus on solid defense.

### Against Defensive Players

**Strategy:** Increase attack and initiative

**Weight Changes:**
```python
weights['central_control'] += 0.3  # Seize center
weights['piece_activity'] += 0.2   # Activate pieces
weights['king_safety'] -= 0.1      # Slightly less defensive
weights['trade_preference'] += 0.2 # Seek favorable trades
```

**Rationale:** Defensive players may be passive, so the engine should apply pressure.

### Against Tactical Players

**Strategy:** Focus on solid positions, avoid tactical traps

**Weight Changes:**
```python
weights['pawn_structure'] += 0.3   # Maintain solid pawns
weights['king_safety'] += 0.2      # Keep king safe
weights['piece_coordination'] += 0.2 # Coordinate pieces
weights['mobility'] -= 0.1         # Less about moving, more about position
```

**Rationale:** Tactical players look for tricks, so solid positional play avoids traps.

### Against Positional Players

**Strategy:** Increase piece activity and tactical play

**Weight Changes:**
```python
weights['piece_activity'] += 0.3   # Activate all pieces
weights['mobility'] += 0.2         # Seek piece mobility
weights['central_control'] -= 0.1  # Slightly less central focus
weights['trade_preference'] += 0.1 # Look for tactical opportunities
```

**Rationale:** Positional players focus on structure, so introduce tactical complications.

### Fine-Tuning Based on Tendencies

Additional adjustments based on specific tendencies:

```python
# Trade willingness
if trade_willingness > 0.6:
    weights['trade_preference'] -= 0.2  # Be selective with trades
elif trade_willingness < 0.4:
    weights['trade_preference'] += 0.2  # Seek favorable trades

# King safety focus
if king_safety_focus > 0.6:
    weights['piece_activity'] += 0.15   # Apply pressure
    weights['mobility'] += 0.1

# Central control preference
if central_control_preference > 0.6:
    weights['central_control'] += 0.15  # Contest center more
else:
    weights['central_control'] += 0.2   # Exploit center
```

## Update Frequency

- **Move Analysis:** Every move
- **Profile Statistics:** Every 5 moves
- **Weight Adaptation:** Every 5 moves
- **Profile Save:** End of game + periodically

This frequency balances responsiveness with computational efficiency.

## Profile Persistence

Player profiles are saved to JSON files in the `profiles/` directory:

```json
{
  "player_id": "player1",
  "player_name": "Alice",
  "games_played": 10,
  "moves_recorded": 350,
  "aggression_score": 0.72,
  "defensive_score": 0.45,
  "tactical_score": 0.68,
  "positional_score": 0.55,
  "trade_willingness": 0.65,
  ...
}
```

Profiles persist across games, so the engine remembers your style!

## Example Adaptation Scenario

### Game 1: Learning an Aggressive Player

**Moves 1-10:**
- Player makes many captures
- Player gives checks frequently
- Player moves pieces aggressively

**Profile Update (after 10 moves):**
- `aggression_score`: 0.45 → 0.58 → 0.72
- `primary_style`: "balanced" → "aggressive"

**Weight Adaptation:**
- `king_safety`: 0.8 → 1.1 (increased defense)
- `piece_activity`: 0.5 → 0.3 (more cautious)
- `central_control`: 0.3 → 0.5 (control center)

**Result:** Engine becomes more defensive to counter aggression

### Game 2: Continued Learning

**Same Player, New Game:**
- Profile loaded with `aggression_score: 0.72`
- Immediate adaptation: weights adjusted from start
- Player continues aggressive play
- Profile updates further

**Result:** Engine adapts faster, remembers style

## Extending the Learning System

### Adding New Style Indicators

1. **Add to PlayerProfile:**
```python
@dataclass
class PlayerProfile:
    ...
    new_indicator: float = 0.5
```

2. **Detect in StyleAnalyzer:**
```python
def analyze_move(...):
    ...
    analysis['new_indicator_value'] = calculate_new_indicator(...)
    return analysis
```

3. **Update Profile:**
```python
def update_profile_from_moves(...):
    ...
    profile.new_indicator = calculate_average(...)
```

4. **Use in WeightAdapter:**
```python
def adapt_to_player(...):
    ...
    if profile.new_indicator > threshold:
        weights['relevant_weight'] += delta
```

### Customizing Adaptation Logic

Modify `WeightAdapter.adapt_to_player()` to implement custom strategies:

```python
def adapt_to_player(self, profile: PlayerProfile) -> Dict[str, float]:
    adapted_weights = self.original_weights.copy()
    
    # Custom adaptation logic here
    if profile.aggression_score > 0.7:
        # Strongly counter aggression
        adapted_weights['king_safety'] += 0.5
        ...
    
    return adapted_weights
```

## Limitations and Future Improvements

### Current Limitations

- Simple heuristics for style detection
- Fixed adaptation rules (not learned)
- No learning rate adjustment
- Style detection based on short-term patterns

### Potential Improvements

1. **Machine Learning:**
   - Use neural networks for style detection
   - Learn adaptation strategies through reinforcement learning

2. **Temporal Patterns:**
   - Track style changes over time
   - Detect style switching during games

3. **Context-Aware Adaptation:**
   - Adapt differently based on game phase (opening/middlegame/endgame)
   - Consider position type (tactical/positional)

4. **Multi-Factor Learning:**
   - Learn correlations between player characteristics
   - Complex interaction effects

5. **Online Learning:**
   - Continuous weight adjustment during search
   - Immediate feedback loops

## Conclusion

The adaptive learning system provides a foundation for personalized chess engine behavior. While the current implementation uses simple heuristics, the architecture supports more sophisticated learning algorithms in the future.

