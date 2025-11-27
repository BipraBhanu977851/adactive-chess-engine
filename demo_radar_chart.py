#!/usr/bin/env python3
"""
Demo Script: Radar Chart with Database Integration

Demonstrates:
- SQLite database setup and profile storage
- Radar chart creation and auto-updating
- Tkinter GUI embedding with matplotlib

Run this script to see a complete working example.
"""

import tkinter as tk
from tkinter import ttk
from gui.radar_chart import RadarChartWidget
from player_profile.database import PlayerDatabase
import random


class RadarChartDemo:
    """Demo application showing radar chart with database integration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Radar Chart Demo - Adaptive Chess Engine")
        self.root.geometry("800x700")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize database
        self.db = PlayerDatabase()
        
        # Demo player ID
        self.player_id = "demo_player"
        
        # Create initial demo profile
        self._create_demo_profile()
        
        # Setup UI
        self._setup_ui()
        
        # Initial chart update
        self._update_chart()
    
    def _create_demo_profile(self):
        """Create demo profile with initial values"""
        demo_data = {
            'aggressive': 60,
            'defensive': 50,
            'positional': 55,
            'tactical': 70,
            'endgame': 40,
            'mistake_control': 65,
            'blunder_rate': 35.0
        }
        
        # Check if profile exists
        existing = self.db.get_profile(self.player_id)
        if not existing:
            self.db.create_profile(
                self.player_id,
                "Demo Player",
                demo_data
            )
            print("✓ Created demo profile in database")
        else:
            print("✓ Using existing demo profile")
    
    def _setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Player Style Radar Chart",
            font=("Segoe UI", 18, "bold"),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        title_label.pack(pady=(0, 20))
        
        # Radar chart frame
        chart_frame = ttk.LabelFrame(main_frame, text="Style Analysis", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create radar chart widget
        self.radar_chart = RadarChartWidget(chart_frame, width=6, height=6, dpi=100)
        self.radar_chart.get_widget().pack(fill=tk.BOTH, expand=True)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Current Profile Values", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.info_text = tk.Text(
            info_frame,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.info_text.pack(fill=tk.X)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Simulate game button
        simulate_btn = ttk.Button(
            buttons_frame,
            text="Simulate Game Completion",
            command=self._simulate_game,
            width=30
        )
        simulate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset button
        reset_btn = ttk.Button(
            buttons_frame,
            text="Reset to Demo Values",
            command=self._reset_profile,
            width=20
        )
        reset_btn.pack(side=tk.LEFT)
    
    def _update_chart(self):
        """Update radar chart with current profile"""
        profile = self.db.get_profile(self.player_id)
        if profile:
            self.radar_chart.update_chart(profile)
            self._update_info_text(profile)
    
    def _update_info_text(self, profile):
        """Update info text with current values"""
        self.info_text.delete(1.0, tk.END)
        text = f"Player: {profile['player_name']}\n"
        text += f"Games Played: {profile['games_played']}\n\n"
        text += f"Aggressive:      {profile['aggressive']:.1f}\n"
        text += f"Defensive:       {profile['defensive']:.1f}\n"
        text += f"Positional:      {profile['positional']:.1f}\n"
        text += f"Tactical:        {profile['tactical']:.1f}\n"
        text += f"Endgame:         {profile['endgame']:.1f}\n"
        text += f"Mistake Control: {profile['mistake_control']:.1f} (Blunder Rate: {profile['blunder_rate']:.1f}%)\n"
        self.info_text.insert(1.0, text)
    
    def _simulate_game(self):
        """Simulate a completed game with random statistics"""
        print("\n🎮 Simulating game completion...")
        
        # Generate random game statistics
        game_stats = {
            'aggressive': random.uniform(45, 75),
            'defensive': random.uniform(40, 70),
            'positional': random.uniform(45, 75),
            'tactical': random.uniform(50, 80),
            'endgame': random.uniform(35, 65),
            'blunder_rate': random.uniform(20, 50),
            'games_played': 1,
            'moves_recorded': random.randint(30, 80)
        }
        
        # Update database (this uses weighted average internally)
        self.db.update_after_game(self.player_id, game_stats)
        
        print("✓ Game statistics updated in database")
        print(f"  New values: Aggressive={game_stats['aggressive']:.1f}, "
              f"Tactical={game_stats['tactical']:.1f}, "
              f"Endgame={game_stats['endgame']:.1f}")
        
        # Update chart (auto-refreshes)
        self._update_chart()
        print("✓ Radar chart updated!\n")
    
    def _reset_profile(self):
        """Reset profile to demo values"""
        demo_data = {
            'aggressive': 60,
            'defensive': 50,
            'positional': 55,
            'tactical': 70,
            'endgame': 40,
            'mistake_control': 65,
            'blunder_rate': 35.0,
            'games_played': 0,
            'moves_recorded': 0
        }
        
        self.db.update_profile(self.player_id, demo_data)
        print("✓ Profile reset to demo values")
        self._update_chart()
    
    def run(self):
        """Start the demo"""
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 60)
    print("Radar Chart Demo - Adaptive Chess Engine")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ SQLite database storage")
    print("  ✓ Auto-updating radar chart")
    print("  ✓ Tkinter GUI integration")
    print("  ✓ Profile update simulation")
    print("\nClick 'Simulate Game Completion' to see the chart update!")
    print("=" * 60 + "\n")
    
    app = RadarChartDemo()
    app.run()








