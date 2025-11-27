# Radar Chart Integration Guide

## Overview

This document explains the database storage system and radar chart visualization that have been integrated into the Adaptive Chess Engine.

## Features

✅ **SQLite Database Storage** - Persistent storage for player profiles  
✅ **Auto-Updating Radar Chart** - Visual representation of player style  
✅ **Tkinter GUI Integration** - Embedded matplotlib chart  
✅ **Real-Time Updates** - Chart refreshes after each game  

## Components

### 1. Database Module (`player_profile/database.py`)

The `PlayerDatabase` class manages SQLite database operations:

- **Schema**: Stores player profiles with fields:
  - `aggressive` (0-100)
  - `defensive` (0-100)
  - `positional` (0-100)
  - `tactical` (0-100)
  - `endgame` (0-100)
  - `mistake_control` (0-100)
  - `blunder_rate` (0-100)
  - Game statistics (games_played, moves_recorded)

- **Key Methods**:
  - `get_profile(player_id)` - Retrieve profile from database
  - `create_profile(player_id, name, initial_values)` - Create new profile
  - `update_profile(player_id, updates)` - Update profile fields
  - `update_after_game(player_id, game_stats)` - Update after game completion (weighted average)

### 2. Radar Chart Widget (`gui/radar_chart.py`)

The `RadarChartWidget` class creates and manages the radar chart visualization:

- **Features**:
  - Embedded in Tkinter using `FigureCanvasTkAgg`
  - Dark theme matching GUI design
  - Auto-resizes with window
  - Updates in real-time

- **Categories Displayed**:
  - Aggressive
  - Defensive
  - Positional
  - Tactical
  - Endgame
  - Mistake Control

- **Usage**:
  ```python
  radar_chart = RadarChartWidget(parent_frame, width=5, height=5)
  radar_chart.update_chart(profile_data)
  ```

### 3. Integration in Chess GUI

The radar chart is integrated into the main chess GUI (`gui/chess_gui.py`):

- **Display**: Shows above the profile details text
- **Auto-Update**: Refreshes after:
  - Every move
  - Game completion
  - Profile reset
  - New game start

### 4. Profile Updates

Profile updates happen automatically:

1. **During Game**: Moves are analyzed and style scores updated
2. **After Game**: `end_game()` saves to database using weighted average:
   - 70% old values
   - 30% new game statistics
3. **Chart Refresh**: Chart updates automatically via `_update_radar_chart()`

## Database Schema

```sql
CREATE TABLE player_profiles (
    player_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    games_played INTEGER DEFAULT 0,
    moves_recorded INTEGER DEFAULT 0,
    aggressive REAL DEFAULT 50.0,
    defensive REAL DEFAULT 50.0,
    positional REAL DEFAULT 50.0,
    tactical REAL DEFAULT 50.0,
    endgame REAL DEFAULT 50.0,
    mistake_control REAL DEFAULT 50.0,
    blunder_rate REAL DEFAULT 0.0,
    last_updated TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## Usage Examples

### Demo Script

Run the demo to see the radar chart in action:

```bash
python3 demo_radar_chart.py
```

This creates a standalone demo showing:
- Database integration
- Radar chart display
- Simulated game completion
- Auto-updating chart

### Integration in Main Application

The radar chart is automatically integrated. When you run:

```bash
python3 main.py
```

or

```bash
make run
```

The radar chart will appear in the right panel of the chess GUI.

### Manual Database Operations

```python
from player_profile.database import PlayerDatabase

# Initialize database
db = PlayerDatabase()

# Create profile with initial values
db.create_profile("player1", "John Doe", {
    'aggressive': 60,
    'defensive': 50,
    'positional': 55,
    'tactical': 70,
    'endgame': 40,
    'mistake_control': 65,
    'blunder_rate': 35.0
})

# Get profile
profile = db.get_profile("player1")

# Update after game
db.update_after_game("player1", {
    'aggressive': 65,
    'defensive': 45,
    'positional': 60,
    'tactical': 75,
    'endgame': 45,
    'blunder_rate': 30.0,
    'games_played': 1,
    'moves_recorded': 45
})
```

## Data Flow

1. **Player Makes Move** → Move analyzed → Profile updated
2. **Game Ends** → `end_game()` called → Database updated (weighted average)
3. **GUI Refresh** → `_update_radar_chart()` called → Chart displays current values
4. **New Game** → Profile loaded from database → Chart shows persisted values

## Files Modified/Created

- ✅ `player_profile/database.py` - SQLite database operations
- ✅ `gui/radar_chart.py` - Radar chart widget (NEW)
- ✅ `gui/chess_gui.py` - Integrated radar chart display
- ✅ `player_profile/player_profile.py` - Added endgame/mistake_control fields
- ✅ `adaptive_logic/adaptive_engine.py` - Database integration in end_game()
- ✅ `adaptive_logic/style_analyzer.py` - Calculate endgame/mistake scores
- ✅ `demo_radar_chart.py` - Standalone demo (NEW)

## Requirements

- Python 3.7+
- matplotlib (install: `pip install matplotlib`)
- tkinter (usually included with Python)
- sqlite3 (included in Python standard library)

## Testing

To test the integration:

1. Run the demo: `python3 demo_radar_chart.py`
2. Click "Simulate Game Completion" multiple times
3. Observe the radar chart updating with weighted averages
4. Click "Reset to Demo Values" to restore initial state

## Notes

- **Weighted Average**: Uses 70% old / 30% new to prevent sudden changes
- **Value Ranges**: All values stored as 0-100 in database, converted to 0-1 internally
- **Auto-Update**: Chart refreshes automatically - no manual refresh needed
- **Persistence**: Profile data persists between sessions in SQLite database








