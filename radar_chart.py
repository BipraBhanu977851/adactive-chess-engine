"""
Radar Chart Module for Player Profile Visualization

Creates and updates radar charts showing player style characteristics.
Displays 5 main indicators:
- Aggressive: How often player makes attacking moves
- Defensive: How often player focuses on safety
- Tactical: Preference for tactical combinations
- Positional: Preference for long-term positional play
- Mistake Control: How well player avoids blunders
"""

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for Tkinter integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, Optional


class RadarChartWidget:
    """
    Radar chart widget that can be embedded in Tkinter.
    Auto-updates when profile data changes.
    """
    
    def __init__(self, parent_frame, width=5, height=5, dpi=100):
        """
        Initialize radar chart widget.
        
        Args:
            parent_frame: Tkinter parent frame
            width: Figure width in inches
            height: Figure height in inches
            dpi: DPI for the figure
        """
        self.parent_frame = parent_frame
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1e1e1e')
        self.ax = self.fig.add_subplot(111, projection='polar', facecolor='#1e1e1e')
        
        # Configure axes
        self.ax.set_facecolor('#1e1e1e')
        
        # Categories for radar chart - 5 main indicators
        self.categories = [
            'Aggressive',
            'Defensive',
            'Tactical',
            'Positional',
            'Mistake Control'
        ]
        
        # Number of categories
        self.N = len(self.categories)
        
        # Angles for each category
        self.angles = [n / float(self.N) * 2 * np.pi for n in range(self.N)]
        self.angles += self.angles[:1]  # Complete the circle
        
        # Initialize with empty data
        self.values = [0] * self.N
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
        self.canvas.draw()
        
        # Store plot reference for updates
        self.plot = None
    
    def update_chart(self, profile_data: Dict):
        """
        Update radar chart with new profile data.
        
        The radar chart displays 5 indicators in a polar plot:
        Each indicator is shown as a point on the chart, with values from 0-100.
        The chart automatically updates when player profile changes.
        
        Args:
            profile_data: Dictionary with profile metrics
                Expected keys: aggressive, defensive, tactical, positional, mistake_control
                Values should be 0-100 (will be converted from 0-1 scale if needed)
        """
        # Extract values from profile data
        # Handle both 0-1 scale and 0-100 scale
        def get_value(key, default=50.0):
            value = profile_data.get(key, default)
            # Convert from 0-1 scale to 0-100 if needed
            if value <= 1.0:
                return value * 100.0
            return value
        
        # Extract 5 main indicators (no endgame)
        self.values = [
            get_value('aggressive', 50.0),
            get_value('defensive', 50.0),
            get_value('tactical', 50.0),
            get_value('positional', 50.0),
            get_value('mistake_control', 50.0)
        ]
        
        # Complete the circle
        values_plot = self.values + self.values[:1]
        
        # Clear previous plot
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        
        # Set angles and labels
        self.ax.set_theta_offset(np.pi / 2)  # Start from top
        self.ax.set_theta_direction(-1)  # Clockwise
        
        # Set the angle positions
        self.ax.set_xticks(self.angles[:-1])
        self.ax.set_xticklabels(self.categories, color='#d4d4d4', fontsize=10, fontweight='bold')
        
        # Set radial limits
        self.ax.set_ylim(0, 100)
        
        # Set radial grid
        self.ax.set_yticks([20, 40, 60, 80, 100])
        self.ax.set_yticklabels(['20', '40', '60', '80', '100'], color='#888888', fontsize=8)
        self.ax.grid(True, color='#444444', linestyle='--', linewidth=0.5)
        
        # Plot the data
        self.plot = self.ax.plot(self.angles, values_plot, 'o-', linewidth=2.5, 
                                 color='#4a9eff', label='Player Style')
        self.ax.fill(self.angles, values_plot, alpha=0.25, color='#4a9eff')
        
        # Set title
        player_name = profile_data.get('player_name', 'Player')
        self.ax.set_title(f'{player_name}\'s Playing Style', 
                         color='#ffffff', fontsize=12, fontweight='bold', pad=20)
        
        # Refresh canvas
        self.canvas.draw()
    
    def get_widget(self):
        """Get the Tkinter widget for embedding"""
        return self.canvas.get_tk_widget()
    
    def destroy(self):
        """Clean up the widget"""
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
