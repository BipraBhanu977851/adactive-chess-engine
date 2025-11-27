"""
Chess Engine Core Module

This module contains the core chess engine functionality:
- Board representation
- Move generation
- Search algorithms (minimax with alpha-beta pruning)
- Base evaluation function
"""

from .board import ChessBoard
from .movegen import MoveGenerator
from .search import SearchEngine
from .evaluation import EvaluationFunction

__all__ = ['ChessBoard', 'MoveGenerator', 'SearchEngine', 'EvaluationFunction']

