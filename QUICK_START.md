# Quick Start Guide

## Installation

No installation required! The project uses only Python standard library modules.

**Requirements:**
- Python 3.7 or higher

## Running the Game

### Basic Usage (Using Makefile - Recommended)

```bash
make
```

Or simply:
```bash
make run
```

### Using Python Directly

```bash
python main.py
```

### With Custom Settings

**Using Makefile:**
```bash
make run PLAYER_ID=my_name PLAYER_NAME="My Name" DEPTH=5
```

**Using Python:**
```bash
python main.py --player-id my_name --player-name "My Name" --depth 5
```

### Makefile Commands

For all available commands:
```bash
make help
```

Common commands:
- `make` or `make run` - Start the game
- `make quick` - Quick start with defaults
- `make clean` - Clean cache files
- `make check` - Check code syntax

Options:
- `--player-id`: Your unique identifier (default: `default_player`)
- `--player-name`: Your display name (default: `Player`)
- `--depth`: Engine strength (default: `4`, range: 1-6 recommended)

## How to Play

1. **Start the game**: Run `python main.py`
2. **Select a piece**: Click on one of your pieces (white pieces)
3. **Make a move**: Click on the destination square
4. **Watch adaptation**: Check the "Player Style Analysis" panel on the right
5. **Engine moves**: The engine moves automatically after your move

## Understanding the Display

### Board
- White pieces: ♔♕♖♗♘♙ (Your pieces - bottom of board)
- Black pieces: ♚♛♜♝♞♟ (Engine pieces - top of board)
- Selected square: Highlighted in green
- Last move: Highlighted in light tan
- Check: King in check highlighted in red

### Style Analysis Panel
- **Primary Style**: Your detected playing style (aggressive, defensive, tactical, positional, or balanced)
- **Style Percentages**: Bar charts showing your style breakdown
- **Adaptation Explanation**: How the engine is adapting to your style

## Example Session

1. Start a new game
2. Play aggressively (make captures, give checks)
3. Watch your "Aggressive %" increase
4. Notice the engine becomes more defensive
5. The engine adapts its play style to counter yours!

## Tips

- **Play multiple games**: The engine learns across games
- **Play consistently**: Consistent style leads to better adaptation
- **Check your profile**: Your profile is saved in `profiles/` directory
- **Reset profile**: Click "Reset Profile" to start fresh

## Troubleshooting

**Game doesn't start:**
- Ensure Python 3.7+ is installed
- Check that you're in the project directory

**Import errors:**
- Make sure you're running from the project root directory
- Check that all files are in place

**Engine moves slowly:**
- Reduce depth: `python main.py --depth 3`
- Depth 3-4 is recommended for responsive play
- Depth 5+ is stronger but slower

## Next Steps

- Read the [README.md](README.md) for full documentation
- Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system architecture
- Read [docs/ADAPTIVE_LEARNING.md](docs/ADAPTIVE_LEARNING.md) for learning details

## Have Fun!

The engine adapts as you play. Try different styles and see how it responds!

