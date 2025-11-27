# Architecture Documentation

## System Overview

The Adaptive Chess Engine is designed with a modular architecture that separates concerns into distinct components:

1. **Chess Engine Core** - Pure chess logic (no learning)
2. **Player Profiling** - Statistics tracking and persistence
3. **Adaptive Logic** - Style analysis and weight adaptation
4. **GUI** - User interface layer

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                         GUI Layer                        │
│                   (gui/chess_gui.py)                     │
│  - User interaction                                     │
│  - Board visualization                                  │
│  - Style display                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Adaptive Engine                        │
│            (adaptive_logic/adaptive_engine.py)           │
│  - Coordinates all systems                              │
│  - Manages game flow                                    │
│  - Integrates learning                                  │
└─────┬──────────────────────────┬────────────────────────┘
      │                          │
      ▼                          ▼
┌──────────────────┐    ┌──────────────────────┐
│  Chess Engine    │    │  Player Profiling    │
│  (engine/)       │    │  (player_profile/)   │
├──────────────────┤    ├──────────────────────┤
│ - Board          │    │ - Profile Manager    │
│ - Move Gen       │    │ - Profile Storage    │
│ - Search         │    │ - Statistics         │
│ - Evaluation     │    │ - Persistence        │
└──────────────────┘    └──────────────────────┘
      │                          │
      └──────────┬───────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Adaptive Logic  │
        │ (adaptive_logic/)│
        ├─────────────────┤
        │ - Style Analyzer│
        │ - Weight Adapter│
        └─────────────────┘
```

## Module Details

### Engine Module (`engine/`)

The core chess engine with no learning capabilities.

#### `board.py` - Board Representation

- **ChessBoard**: 8x8 array representation
- Supports FEN notation
- Move making/unmaking
- Check detection
- Board state management

**Key Classes:**
- `ChessBoard`: Main board class
- `Piece`: Piece type enumeration
- `Color`: Piece color enumeration

#### `movegen.py` - Move Generation

- **MoveGenerator**: Generates all legal moves
- Piece-specific move patterns
- Legal move validation (no check)
- Castling support

**Key Methods:**
- `generate_all_moves(color)`: Generate all legal moves for a color
- `_generate_moves_for_piece(...)`: Generate moves for specific piece
- `_is_legal_move(...)`: Validate move legality

#### `search.py` - Search Algorithm

- **SearchEngine**: Minimax with alpha-beta pruning
- Configurable depth
- Node counting
- Position evaluation integration

**Key Methods:**
- `find_best_move(board, color)`: Find optimal move
- `_minimax(...)`: Recursive minimax with alpha-beta

#### `evaluation.py` - Position Evaluation

- **EvaluationFunction**: Evaluates positions
- Material counting
- Positional factors:
  - Piece activity
  - King safety
  - Central control
  - Pawn structure
  - Piece coordination
  - Mobility
- **Adaptive weights**: Can be modified dynamically

**Key Features:**
- Default weights for all evaluation factors
- Weight modification methods
- Combines material and positional evaluation

### Player Profile Module (`player_profile/`)

Manages player statistics and persistence.

#### `player_profile.py` - Profile Data Structure

**PlayerProfile**: Dataclass storing:
- Player identification
- Game statistics (games played, moves recorded)
- Style indicators (0.0 to 1.0):
  - Aggression score
  - Defensive score
  - Tactical score
  - Positional score
- Tendency scores:
  - Trade willingness
  - King safety focus
  - Central control preference
  - Piece activity preference
  - Pawn structure focus
- Move statistics (capture rate, check rate, etc.)
- Move history

**Key Methods:**
- `get_primary_style()`: Determine dominant style
- `get_style_percentages()`: Get style breakdown
- `update_stats(move_data)`: Update statistics
- `to_dict() / from_dict()`: Serialization

#### `profile_manager.py` - Profile Management

**PlayerProfileManager**: Handles profile I/O

- JSON-based persistence
- Profile loading/saving
- Profile creation
- Profile listing

**Storage:** Profiles stored in `profiles/` directory as JSON files

### Adaptive Logic Module (`adaptive_logic/`)

Implements the learning and adaptation system.

#### `style_analyzer.py` - Style Analysis

**StyleAnalyzer**: Analyzes moves to detect playing style

**Key Functionality:**
- Analyzes individual moves for style indicators
- Detects:
  - Aggressive patterns (captures, checks, attacks)
  - Defensive patterns (protection, pawn moves)
  - Tactical patterns (tactical sequences, exchanges)
  - Positional patterns (central control, structure)
- Updates player profiles based on move history

**Key Methods:**
- `analyze_move(...)`: Analyze single move
- `update_profile_from_moves(...)`: Update profile statistics

#### `weight_adapter.py` - Weight Adaptation

**WeightAdapter**: Adapts evaluation weights based on player style

**Adaptation Logic:**

1. **Against Aggressive Players:**
   - Increase king safety (+0.3)
   - Decrease piece activity (-0.2)
   - Increase central control (+0.2)
   - Decrease trade preference (-0.3)

2. **Against Defensive Players:**
   - Increase central control (+0.3)
   - Increase piece activity (+0.2)
   - Decrease king safety (-0.1)
   - Increase trade preference (+0.2)

3. **Against Tactical Players:**
   - Increase pawn structure (+0.3)
   - Increase king safety (+0.2)
   - Increase piece coordination (+0.2)
   - Decrease mobility (-0.1)

4. **Against Positional Players:**
   - Increase piece activity (+0.3)
   - Increase mobility (+0.2)
   - Decrease central control (-0.1)
   - Increase trade preference (+0.1)

**Key Methods:**
- `adapt_to_player(profile)`: Generate adapted weights
- `apply_adaptation(profile)`: Apply weights to evaluator
- `get_adaptation_explanation(profile)`: Human-readable explanation

#### `adaptive_engine.py` - Adaptive Engine Integration

**AdaptiveEngine**: Main adaptive engine that integrates all components

**Responsibilities:**
- Initialize all subsystems
- Manage game state
- Coordinate move analysis
- Update profiles periodically
- Apply adaptations
- Save profiles

**Key Methods:**
- `make_player_move(...)`: Record and make player move
- `make_engine_move()`: Generate and make engine move
- `update_adaptation()`: Update weights based on profile
- `get_player_style_info()`: Get current style analysis

### GUI Module (`gui/`)

Tkinter-based graphical interface.

#### `chess_gui.py` - Main GUI

**ChessGUI**: Main GUI class

**Features:**
- Board visualization (8x8 grid)
- Piece rendering (Unicode chess symbols)
- Move highlighting:
  - Selected square
  - Last move squares
  - Check indicator
- Style display panel:
  - Primary style
  - Style percentages with bars
  - Adaptation explanation
- Game controls:
  - New game
  - Reset profile
  - Quit

**Interaction:**
- Click to select piece
- Click destination to move
- Automatic engine move after player move

## Data Flow

### Game Flow

1. **Game Start:**
   - Load/create player profile
   - Initialize board to starting position
   - Apply initial adaptation

2. **Player Move:**
   - Analyze move for style indicators
   - Make move on board
   - Store move analysis
   - Update profile statistics (periodically)
   - Update adaptation (periodically)

3. **Engine Move:**
   - Generate best move using adapted evaluation
   - Make move on board
   - Display updated board

4. **Game End:**
   - Final profile update
   - Save profile to disk

### Learning Flow

1. **Move Analysis:**
   ```
   Player Move → StyleAnalyzer.analyze_move() → Move Analysis Dict
   ```

2. **Profile Update:**
   ```
   Move Analysis → Profile.update_stats() → Updated Statistics
   ```

3. **Style Detection:**
   ```
   Recent Moves → StyleAnalyzer.update_profile_from_moves() → Updated Style Scores
   ```

4. **Weight Adaptation:**
   ```
   Updated Profile → WeightAdapter.adapt_to_player() → Adapted Weights
   ```

5. **Evaluation Update:**
   ```
   Adapted Weights → EvaluationFunction.set_weights() → Updated Evaluator
   ```

## Design Patterns

### Separation of Concerns

Each module has a single, well-defined responsibility:
- **Engine**: Chess logic only
- **Profile**: Data management only
- **Adaptive Logic**: Learning only
- **GUI**: Presentation only

### Strategy Pattern

The evaluation function uses adaptive weights, allowing different strategies based on player style without modifying the core evaluation code.

### Observer Pattern (Implicit)

The GUI observes game state changes and updates the display accordingly.

### Factory Pattern

ProfileManager creates and loads profiles, abstracting the persistence layer.

## Extension Points

### Adding New Evaluation Factors

1. Add weight to `EvaluationFunction._get_default_weights()`
2. Implement evaluation method
3. Add to `evaluate()` method
4. Optionally update `WeightAdapter` to adapt the new weight

### Adding New Style Indicators

1. Add field to `PlayerProfile`
2. Update `StyleAnalyzer` to detect the indicator
3. Update `WeightAdapter` to use the indicator

### Customizing Adaptation

Modify `WeightAdapter.adapt_to_player()` to implement custom adaptation logic.

## Performance Considerations

- **Search Depth**: Default depth of 4 provides good balance between strength and speed
- **Profile Updates**: Updates occur every 5 moves to balance responsiveness and efficiency
- **Move History**: Limited to last 100 moves to prevent memory growth
- **Position Caching**: Search engine could implement transposition tables for better performance

## Testing Considerations

Each module can be tested independently:
- **Engine**: Test move generation, search, evaluation
- **Profile**: Test statistics updates, serialization
- **Adaptive Logic**: Test style detection, weight adaptation
- **GUI**: Test user interaction, display updates

## Future Architecture Improvements

- Implement proper transposition tables in search
- Add opening book support
- Implement endgame tablebase integration
- Add network layer for online play
- Implement move history and game replay

