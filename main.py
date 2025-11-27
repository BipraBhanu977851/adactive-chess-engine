#!/usr/bin/env python3
"""
Adaptive Chess Engine - Main Entry Point

Run this script to start the chess game with adaptive learning.
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.chess_gui import ChessGUI


def main():
    """Main entry point for the chess engine"""
    parser = argparse.ArgumentParser(description='Adaptive Chess Engine')
    parser.add_argument(
        '--player-id',
        type=str,
        default='default_player',
        help='Unique identifier for the player (default: default_player)'
    )
    parser.add_argument(
        '--player-name',
        type=str,
        default='Player',
        help='Display name for the player (default: Player)'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=4,
        help='Engine search depth (default: 4)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Adaptive Chess Engine")
    print("=" * 60)
    print(f"Player ID: {args.player_id}")
    print(f"Player Name: {args.player_name}")
    print(f"Engine Depth: {args.depth}")
    print("=" * 60)
    print("\nStarting game...")
    print("Click on a piece to select it, then click on a square to move.")
    print("The engine adapts to your playing style as you play!\n")
    
    # Create and run GUI
    gui = ChessGUI(player_id=args.player_id, player_name=args.player_name)
    gui.engine.set_search_depth(args.depth)
    gui.run()


if __name__ == '__main__':
    main()

