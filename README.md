# Adaptive Chess Engine

A chess engine that **adapts to your playing style** instead of using fixed difficulty levels. The engine learns whether you're aggressive, defensive, tactical, or positional and dynamically adjusts its evaluation function to provide a challenging and personalized gameplay experience.

## Features

### Core Capabilities

- **Adaptive Learning System**: Analyzes your move history to detect long-term playing tendencies
- **Player Profiling**: Maintains persistent profiles with statistical analysis across multiple games
- **Dynamic Evaluation Function**: Modifies evaluation weights in real-time based on detected playing style
- **Full Chess Engine**: Complete implementation with:
  - Board representation
  - Move generation
  - Minimax search with alpha-beta pruning
  - Position evaluation
- **Modern GUI**: Clean Tkinter-based interface with:
  - Move highlighting
  - Player style indicators (aggressive %, defensive %, tactical %, positional %)
  - Game status display

### Adaptive Behavior

The engine adapts in the following ways:

- **Against Aggressive Players**: Increases king safety and defensive weights
- **Against Defensive Players**: Increases attack and central control weights
- **Against Tactical Players**: Focuses on solid positions and avoids tactical traps
- **Against Positional Players**: Increases piece activity and tactical play

##  Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

##  Quick Start

### Installation

1. Clone or download this repository
2. Navigate to the project directory

### Running the Game

**Quick Start (using Makefile):**
```bash
make
```

**Using Python directly:**
```bash
python main.py
```

### Using Makefile (Recommended)

The project includes a Makefile for easy single-command execution:

```bash
# Run with default settings
make
make run

# Quick run
make quick

# Custom player
make player PLAYER_ID=my_name PLAYER_NAME="My Name"

# Custom depth
make depth DEPTH=5

# Combined custom options
make run PLAYER_ID=alice PLAYER_NAME="Alice" DEPTH=6

# Other useful commands
make clean          # Remove cache files
make clean-profiles # Remove all profiles
make check          # Check code syntax
make test           # Run basic tests
make help           # Show all commands
```

### Command Line Options

```bash
python main.py --player-id my_id --player-name "My Name" --depth 5
```

Options:
- `--player-id`: Unique identifier for your player profile (default: `default_player`)
- `--player-name`: Display name (default: `Player`)
- `--depth`: Engine search depth (default: `4`, higher = stronger but slower)

## How to Play

1. **Start the game**: Run `python main.py`
2. **Make moves**: Click on a piece to select it, then click on the destination square
3. **Watch the adaptation**: The engine learns your style as you play - check the "Player Style Analysis" panel
4. **New game**: Click "New Game" to start a fresh game while keeping your profile

## 📁 Project Structure

```
adaptive-chess-engine/
├── engine/                 # Core chess engine
│   ├── board.py           # Board representation
│   ├── movegen.py         # Move generation
│   ├── search.py          # Minimax with alpha-beta
│   └── evaluation.py      # Position evaluation
├── adaptive_logic/        # Adaptive learning system
│   ├── style_analyzer.py  # Analyzes player moves
│   ├── weight_adapter.py  # Adapts evaluation weights
│   └── adaptive_engine.py # Main adaptive engine
├── player_profile/        # Player profiling system
│   ├── player_profile.py  # Profile data structure
│   └── profile_manager.py # Profile persistence
├── gui/                   # Graphical user interface
│   └── chess_gui.py       # Tkinter GUI
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   └── ADAPTIVE_LEARNING.md # Adaptive learning details
├── profiles/              # Player profiles (created automatically)
├── main.py                # Main entry point
└── README.md              # This file
```

## How Adaptive Learning Works

The engine tracks various statistics from your moves:

1. **Aggression Score**: Based on captures, checks, and attacking moves
2. **Defensive Score**: Based on defensive moves and piece protection
3. **Tactical Score**: Based on tactical sequences and piece exchanges
4. **Positional Score**: Based on central control and positional moves
5. **Trade Willingness**: How often you trade pieces
6. **King Safety Focus**: How much you focus on king safety
7. **Central Control**: Preference for central squares

Every few moves, the engine:
- Updates your profile statistics
- Determines your primary playing style
- Adjusts its evaluation weights accordingly
- Saves your profile for future games

See [docs/ADAPTIVE_LEARNING.md](docs/ADAPTIVE_LEARNING.md) for detailed information.

##  Player Profiles

Player profiles are stored in the `profiles/` directory as JSON files. Each profile contains:
- Game statistics (games played, moves recorded)
- Style indicators (aggression, defense, tactical, positional)
- Tendency scores (trade willingness, king safety, etc.)
- Move history (for analysis)

Profiles persist across games, so the engine remembers your style!

##  Architecture

The system is designed with clear separation of concerns:

- **Engine**: Pure chess engine logic (no learning)
- **Adaptive Logic**: Learning and adaptation algorithms
- **Player Profile**: Data management and persistence
- **GUI**: User interface (completely separate from engine logic)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

##  Extending the System

### Adding New Evaluation Parameters

1. Add weight to `evaluation.py` in `_get_default_weights()`
2. Implement evaluation function in `EvaluationFunction` class
3. Update `weight_adapter.py` to adapt the new weight based on player style

### Adding New Style Indicators

1. Add analysis in `style_analyzer.py`
2. Update `PlayerProfile` to store the new indicator
3. Update `weight_adapter.py` to use the new indicator

### Customizing Adaptation Logic

Modify `weight_adapter.py` in the `adapt_to_player()` method to change how the engine adapts to different playing styles.

##  Future Improvements

Potential enhancements:

- [ ] Opening book integration
- [ ] Endgame tablebase support
- [ ] More sophisticated learning algorithms (e.g., neural networks)
- [ ] Multiple difficulty levels within adaptive mode
- [ ] Game replay and analysis features
- [ ] Online multiplayer support
- [ ] Move hint system
- [ ] Evaluation bar visualization
- [ ] Save/load game positions

##  Known Limitations

- Simplified check detection (may not catch all check patterns)
- Basic castling rules (doesn't check if squares are attacked)
- No threefold repetition or 50-move rule detection
- Evaluation function is basic (can be improved with more features)

##  License

This project is provided as-is for educational and personal use.

##  Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

##  Additional Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Adaptive Learning Guide](docs/ADAPTIVE_LEARNING.md)

##  Learning Resources

This project demonstrates:
- Chess engine implementation
- Minimax algorithm with alpha-beta pruning
- Machine learning concepts (adaptive weights)
- Player profiling and statistics
- GUI development with Tkinter
- Software architecture and modular design

---

**Enjoy playing chess against an engine that learns and adapts to you!** 

