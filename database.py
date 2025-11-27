"""
SQLite Database Module for Player Profiles

Stores and manages player profiles in SQLite database.
"""

import sqlite3
import os
from typing import Optional, Dict, List
from datetime import datetime


class PlayerDatabase:
    """
    SQLite database manager for player profiles.
    """
    
    def __init__(self, db_path: str = "profiles.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_profiles (
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
        ''')
        
        conn.commit()
        conn.close()
    
    def get_profile(self, player_id: str) -> Optional[Dict]:
        """
        Get player profile from database.
        
        Args:
            player_id: Unique player identifier
            
        Returns:
            Dictionary with profile data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM player_profiles WHERE player_id = ?', (player_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def create_profile(self, player_id: str, player_name: str, initial_values: Optional[Dict] = None) -> Dict:
        """
        Create a new player profile.
        
        Args:
            player_id: Unique player identifier
            player_name: Player display name
            initial_values: Optional initial values for profile metrics
            
        Returns:
            Created profile dictionary
        """
        if initial_values is None:
            initial_values = {
                'aggressive': 50.0,
                'defensive': 50.0,
                'positional': 50.0,
                'tactical': 50.0,
                'endgame': 50.0,
                'mistake_control': 50.0,
                'blunder_rate': 0.0
            }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO player_profiles 
            (player_id, player_name, aggressive, defensive, positional, tactical, endgame, mistake_control, blunder_rate, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id,
            player_name,
            initial_values.get('aggressive', 50.0),
            initial_values.get('defensive', 50.0),
            initial_values.get('positional', 50.0),
            initial_values.get('tactical', 50.0),
            initial_values.get('endgame', 50.0),
            initial_values.get('mistake_control', 50.0),
            initial_values.get('blunder_rate', 0.0),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return self.get_profile(player_id)
    
    def update_profile(self, player_id: str, updates: Dict):
        """
        Update player profile fields.
        
        Args:
            player_id: Unique player identifier
            updates: Dictionary of fields to update
        """
        if not updates:
            return
        
        # Build update query dynamically
        fields = []
        values = []
        
        for key, value in updates.items():
            if key in ['aggressive', 'defensive', 'positional', 'tactical', 'endgame', 
                      'mistake_control', 'blunder_rate', 'games_played', 'moves_recorded', 'player_name']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return
        
        # Add last_updated
        fields.append("last_updated = ?")
        values.append(datetime.now().isoformat())
        
        # Add player_id for WHERE clause
        values.append(player_id)
        
        query = f"UPDATE player_profiles SET {', '.join(fields)} WHERE player_id = ?"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def update_after_game(self, player_id: str, game_stats: Dict):
        """
        Update profile after a game ends.
        
        Args:
            player_id: Unique player identifier
            game_stats: Dictionary with game statistics to update
        """
        # Get current profile
        profile = self.get_profile(player_id)
        if not profile:
            return
        
        # Calculate new values (weighted average with existing values)
        updates = {}
        
        # Update metrics with weighted average (70% old, 30% new)
        weight_old = 0.7
        weight_new = 0.3
        
        for metric in ['aggressive', 'defensive', 'positional', 'tactical', 'endgame']:
            if metric in game_stats:
                old_value = profile.get(metric, 50.0)
                new_value = game_stats[metric]
                updates[metric] = old_value * weight_old + new_value * weight_new
        
        # Update mistake control (100 - blunder_rate)
        if 'blunder_rate' in game_stats:
            updates['blunder_rate'] = game_stats['blunder_rate']
            updates['mistake_control'] = 100.0 - game_stats['blunder_rate']
        elif 'mistake_control' in game_stats:
            updates['mistake_control'] = game_stats['mistake_control']
            updates['blunder_rate'] = 100.0 - game_stats['mistake_control']
        
        # Update counters
        if 'games_played' in game_stats:
            updates['games_played'] = profile.get('games_played', 0) + 1
        if 'moves_recorded' in game_stats:
            updates['moves_recorded'] = profile.get('moves_recorded', 0) + game_stats.get('moves_recorded', 0)
        
        self.update_profile(player_id, updates)
    
    def get_all_profiles(self) -> List[Dict]:
        """Get all player profiles"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM player_profiles')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_profile(self, player_id: str):
        """Delete a player profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM player_profiles WHERE player_id = ?', (player_id,))
        conn.commit()
        conn.close()

