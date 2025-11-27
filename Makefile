# Makefile for Adaptive Chess Engine
# Run 'make' or 'make run' to start the game

.PHONY: run clean help test install check

# Default target
.DEFAULT_GOAL := run

# Variables
PYTHON := python3
MAIN := main.py
PLAYER_ID ?= default_player
PLAYER_NAME ?= Player
DEPTH ?= 4

# Run the chess engine
run:
	@echo "Starting Adaptive Chess Engine..."
	@echo "Player ID: $(PLAYER_ID)"
	@echo "Player Name: $(PLAYER_NAME)"
	@echo "Engine Depth: $(DEPTH)"
	@echo ""
	$(PYTHON) $(MAIN) --player-id $(PLAYER_ID) --player-name "$(PLAYER_NAME)" --depth $(DEPTH)

# Quick run with default settings
quick:
	$(PYTHON) $(MAIN)

# Run with custom player
player:
	$(PYTHON) $(MAIN) --player-id $(PLAYER_ID) --player-name "$(PLAYER_NAME)"

# Run with custom depth
depth:
	$(PYTHON) $(MAIN) --depth $(DEPTH)

# Clean generated files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "Clean complete!"

# Clean profiles (reset all player profiles)
clean-profiles:
	@echo "Cleaning player profiles..."
	rm -rf profiles/
	@echo "Profiles cleaned!"

# Full clean (including profiles)
clean-all: clean clean-profiles
	@echo "Full clean complete!"

# Check code syntax
check:
	@echo "Checking Python syntax..."
	$(PYTHON) -m py_compile $(MAIN)
	@echo "Checking engine module..."
	$(PYTHON) -m py_compile engine/*.py
	@echo "Checking adaptive_logic module..."
	$(PYTHON) -m py_compile adaptive_logic/*.py
	@echo "Checking player_profile module..."
	$(PYTHON) -m py_compile player_profile/*.py
	@echo "Checking gui module..."
	$(PYTHON) -m py_compile gui/*.py
	@echo "All checks passed!"

# Run basic tests
test:
	@echo "Running basic functionality tests..."
	$(PYTHON) -c "from engine.board import ChessBoard; b = ChessBoard(); print('✓ Board initialization OK')"
	$(PYTHON) -c "from engine.movegen import MoveGenerator; from engine.board import ChessBoard, Color; b = ChessBoard(); mg = MoveGenerator(b); moves = mg.generate_all_moves(Color.WHITE); print(f'✓ Move generation OK ({len(moves)} moves)')"
	$(PYTHON) -c "from engine.board import ChessBoard; b = ChessBoard(); b.make_move((6, 4), (4, 4)); print('✓ Move execution OK')"
	@echo "All tests passed!"

# Install (create necessary directories)
install:
	@echo "Installing..."
	mkdir -p profiles
	@echo "Installation complete!"

# Help message
help:
	@echo "Adaptive Chess Engine - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "Usage:"
	@echo "  make              - Run the chess engine (default)"
	@echo "  make run          - Run the chess engine"
	@echo "  make quick        - Quick run with default settings"
	@echo ""
	@echo "Custom options:"
	@echo "  make player PLAYER_ID=myid PLAYER_NAME='My Name'"
	@echo "  make depth DEPTH=5"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove Python cache files"
	@echo "  make clean-profiles - Remove all player profiles"
	@echo "  make clean-all    - Clean everything"
	@echo ""
	@echo "Development:"
	@echo "  make check        - Check Python syntax"
	@echo "  make test         - Run basic tests"
	@echo "  make install      - Create necessary directories"
	@echo ""
	@echo "Help:"
	@echo "  make help         - Show this help message"
	@echo ""

