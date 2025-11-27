"""
Player Profile Manager

Manages loading, saving, and updating player profiles.
Uses SQLite database for persistent storage.
"""

import os
import json
from typing import Optional, Dict
from datetime import datetime
from .player_profile import PlayerProfile
from .database import PlayerDatabase


class PlayerProfileManager:
    """
    Manages player profiles with JSON-based persistence.
    """
    
    def __init__(self, profiles_dir: str = "profiles"):
        """
        Initialize profile manager.
        
        Args:
            profiles_dir: Directory to store profile files
        """
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
    
    def get_profile_path(self, player_id: str) -> str:
        """Get file path for a player profile"""
        return os.path.join(self.profiles_dir, f"{player_id}.json")
    
    def load_profile(self, player_id: str) -> Optional[PlayerProfile]:
        """
        Load player profile from disk.
        
        Args:
            player_id: Unique player identifier
            
        Returns:
            PlayerProfile instance or None if not found
        """
        profile_path = self.get_profile_path(player_id)
        
        if not os.path.exists(profile_path):
            return None
        
        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)
                return PlayerProfile.from_dict(data)
        except Exception as e:
            print(f"Error loading profile for {player_id}: {e}")
            return None
    
    def save_profile(self, profile: PlayerProfile):
        """
        Save player profile to disk.
        
        Args:
            profile: PlayerProfile instance to save
        """
        profile_path = self.get_profile_path(profile.player_id)
        profile.last_updated = datetime.now().isoformat()
        
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving profile for {profile.player_id}: {e}")
    
    def create_profile(self, player_id: str, player_name: Optional[str] = None) -> PlayerProfile:
        """
        Create a new player profile.
        
        Args:
            player_id: Unique player identifier
            player_name: Optional player name
            
        Returns:
            New PlayerProfile instance
        """
        profile = PlayerProfile(
            player_id=player_id,
            player_name=player_name or player_id
        )
        self.save_profile(profile)
        return profile
    
    def get_or_create_profile(self, player_id: str, player_name: Optional[str] = None) -> PlayerProfile:
        """
        Get existing profile or create new one.
        
        Args:
            player_id: Unique player identifier
            player_name: Optional player name
            
        Returns:
            PlayerProfile instance
        """
        profile = self.load_profile(player_id)
        if profile is None:
            profile = self.create_profile(player_id, player_name)
        return profile
    
    def list_profiles(self) -> list:
        """List all available player IDs"""
        if not os.path.exists(self.profiles_dir):
            return []
        
        profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                player_id = filename[:-5]  # Remove .json extension
                profiles.append(player_id)
        
        return profiles

