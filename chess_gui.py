"""
Chess GUI Module

Tkinter-based graphical user interface for playing chess against
the adaptive engine.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple
from engine.board import ChessBoard, Color, Piece
from adaptive_logic.adaptive_engine import AdaptiveEngine
from gui.radar_chart import RadarChartWidget


class ChessGUI:
    """
    Chess game GUI using Tkinter.
    """
    
    SQUARE_SIZE = 75  # Increased from 60 for bigger board
    BOARD_SIZE = SQUARE_SIZE * 8
    
    # Colors - Modern aesthetic
    LIGHT_SQUARE = "#f0d9b5"
    DARK_SQUARE = "#b58863"
    SELECTED_SQUARE = "#4a9eff"  # Blue highlight
    LAST_MOVE_SQUARE = "#ffd700"  # Gold highlight
    CHECK_SQUARE = "#ff4444"  # Red for check
    
    def __init__(self, player_id: str = "default_player", player_name: str = "Player"):
        """
        Initialize chess GUI.
        
        Args:
            player_id: Unique identifier for the player
            player_name: Display name for the player
        """
        self.root = tk.Tk()
        self.root.title("Adaptive Chess Engine")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(1200, 700)
        
        # Modern color scheme
        self.BG_COLOR = "#2b2b2b"
        self.FG_COLOR = "#ffffff"
        self.ACCENT_COLOR = "#4a9eff"
        self.PANEL_BG = "#1e1e1e"
        
        # Configure root background
        self.root.configure(bg=self.BG_COLOR)
        
        # Initialize engine
        self.engine = AdaptiveEngine(player_id, search_depth=4)
        self.player_name = player_name
        
        # Game state
        self.selected_square: Optional[Tuple[int, int]] = None
        self.last_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
        self.player_color = Color.WHITE
        self.engine_color = Color.BLACK
        
        # UI components
        self.canvas = None
        self.info_frame = None
        self.style_frame = None
        self.radar_frame = None
        self.buttons_frame = None
        self.radar_chart = None
        
        # Performance fix: Track when radar chart was last updated to avoid frequent redraws
        self.last_radar_update_move_count = 0
        
        self._setup_ui()
        self._update_display()
        self._update_style_info()
        self._update_radar_chart()
    
    def _setup_ui(self):
        """Setup user interface components"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.configure(style="Main.TFrame")
        
        # Configure main frame grid
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel: Board
        board_frame = ttk.Frame(main_frame)
        board_frame.grid(row=0, column=0, padx=10)
        
        self.canvas = tk.Canvas(
            board_frame,
            width=self.BOARD_SIZE,
            height=self.BOARD_SIZE,
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_square_click)
        
        # Right panel: Info and controls
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Game info - Minimal design
        self.info_frame = ttk.LabelFrame(right_panel, text="Game Status", padding="12")
        self.info_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.turn_label = ttk.Label(self.info_frame, text="Turn: White", font=("Segoe UI", 11, "bold"))
        self.turn_label.pack(anchor=tk.W, pady=(0, 4))
        
        self.status_label = ttk.Label(self.info_frame, text="Status: Active", font=("Segoe UI", 10))
        self.status_label.pack(anchor=tk.W)
        
        # Radar chart frame - Embedded matplotlib
        self.radar_frame = ttk.LabelFrame(right_panel, text="Style Radar Chart", padding="10")
        self.radar_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Create radar chart widget
        self.radar_chart = RadarChartWidget(self.radar_frame, width=4.5, height=4.5, dpi=80)
        self.radar_chart.get_widget().pack(fill=tk.BOTH, expand=True)
        
        # Style indicators - Minimal expanded display
        self.style_frame = ttk.LabelFrame(right_panel, text="Player Profile Details", padding="10")
        self.style_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Text widget for displaying all indicators with scrollbar
        self.style_text = tk.Text(
            self.style_frame, 
            width=38, 
            height=12, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            selectbackground="#4a9eff",
            relief=tk.FLAT,
            borderwidth=0,
            padx=8,
            pady=8
        )
        self.style_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        style_scrollbar = ttk.Scrollbar(self.style_frame, orient=tk.VERTICAL, command=self.style_text.yview)
        self.style_text.config(yscrollcommand=style_scrollbar.set)
        style_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons - Minimal design
        self.buttons_frame = ttk.Frame(right_panel)
        self.buttons_frame.pack(fill=tk.X)
        
        new_game_btn = ttk.Button(
            self.buttons_frame, 
            text="New Game", 
            command=self._new_game,
            width=20
        )
        new_game_btn.pack(fill=tk.X, pady=(0, 4))
        
        reset_profile_btn = ttk.Button(
            self.buttons_frame, 
            text="Reset Profile", 
            command=self._reset_profile,
            width=20
        )
        reset_profile_btn.pack(fill=tk.X, pady=(0, 4))
        
        quit_btn = ttk.Button(
            self.buttons_frame, 
            text="Quit", 
            command=self.root.quit,
            width=20
        )
        quit_btn.pack(fill=tk.X)
    
    def _draw_board(self):
        """Draw chess board"""
        self.canvas.delete("all")
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE
                y1 = row * self.SQUARE_SIZE
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                
                # Check if selected
                if self.selected_square == (row, col):
                    color = self.SELECTED_SQUARE
                # Check if last move
                elif self.last_move and ((row, col) == self.last_move[0] or (row, col) == self.last_move[1]):
                    color = self.LAST_MOVE_SQUARE
                # Check if in check
                elif self.engine.board.is_in_check(self.engine.board.turn):
                    king_pos = self.engine.board.get_king_position(self.engine.board.turn)
                    if king_pos == (row, col):
                        color = self.CHECK_SQUARE
                    elif is_light:
                        color = self.LIGHT_SQUARE
                    else:
                        color = self.DARK_SQUARE
                else:
                    color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        
        # Draw pieces
        piece_symbols = {
            (Piece.PAWN, Color.WHITE): '♙',
            (Piece.KNIGHT, Color.WHITE): '♘',
            (Piece.BISHOP, Color.WHITE): '♗',
            (Piece.ROOK, Color.WHITE): '♖',
            (Piece.QUEEN, Color.WHITE): '♕',
            (Piece.KING, Color.WHITE): '♔',
            (Piece.PAWN, Color.BLACK): '♟',
            (Piece.KNIGHT, Color.BLACK): '♞',
            (Piece.BISHOP, Color.BLACK): '♝',
            (Piece.ROOK, Color.BLACK): '♜',
            (Piece.QUEEN, Color.BLACK): '♛',
            (Piece.KING, Color.BLACK): '♚',
        }
        
        for row in range(8):
            for col in range(8):
                piece = self.engine.board.get_piece(row, col)
                if piece:
                    piece_type, piece_color = piece
                    symbol = piece_symbols.get((piece_type, piece_color), '?')
                    
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    
                    # Use better font size for bigger board
                    font_size = 48
                    self.canvas.create_text(
                        x, y,
                        text=symbol,
                        font=("Arial", font_size),
                        fill="black" if piece_color == Color.WHITE else "black"
                    )
    
    def _update_display(self):
        """Update board display and game info"""
        self._draw_board()
        
        # Update turn indicator
        turn_color = "White" if self.engine.board.turn == Color.WHITE else "Black"
        self.turn_label.config(text=f"Turn: {turn_color}")
        
        # Check for game end
        from engine.movegen import MoveGenerator
        movegen = MoveGenerator(self.engine.board)
        moves = movegen.generate_all_moves(self.engine.board.turn)
        
        if not moves:
            if self.engine.board.is_in_check(self.engine.board.turn):
                winner = "Black" if self.engine.board.turn == Color.WHITE else "White"
                self.status_label.config(text=f"Checkmate! {winner} wins!", foreground="green")
                messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
            else:
                self.status_label.config(text="Stalemate!", foreground="orange")
                messagebox.showinfo("Game Over", "Stalemate!")
        else:
            # Only update status if it's not already set to a specific message
            current_status = self.status_label.cget("text")
            if current_status == "Status: Active" or "Status:" not in current_status:
                self.status_label.config(text="Status: Active", foreground="black")
    
    def _update_style_info(self):
        """Update player style information display - Minimal aesthetic design"""
        profile = self.engine.profile
        style_info = self.engine.get_player_style_info()
        
        self.style_text.delete(1.0, tk.END)
        
        # Game Statistics - Compact
        text = " STATISTICS\n"
        text += "─" * 35 + "\n"
        text += f"Games: {profile.games_played}  |  Moves: {profile.moves_recorded}\n\n"
        
        # Primary Style
        text += " PRIMARY STYLE\n"
        text += "─" * 35 + "\n"
        text += f"{style_info['primary_style'].title()}\n\n"
        
        # Style Percentages - Compact bars
        text += " STYLE BREAKDOWN\n"
        text += "─" * 35 + "\n"
        for style, percentage in style_info['style_percentages'].items():
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            text += f"{style.title():10} {percentage:5.1f}% {bar}\n"
        text += "\n"
        
        # Tendency Scores - Compact
        text += " TENDENCIES\n"
        text += "─" * 35 + "\n"
        
        trade_bar = "█" * int(profile.trade_willingness * 15) + "░" * (15 - int(profile.trade_willingness * 15))
        text += f"Trade:      {profile.trade_willingness*100:4.0f}% {trade_bar}\n"
        
        king_bar = "█" * int(profile.king_safety_focus * 15) + "░" * (15 - int(profile.king_safety_focus * 15))
        text += f"King Safe:  {profile.king_safety_focus*100:4.0f}% {king_bar}\n"
        
        central_bar = "█" * int(profile.central_control_preference * 15) + "░" * (15 - int(profile.central_control_preference * 15))
        text += f"Center:     {profile.central_control_preference*100:4.0f}% {central_bar}\n"
        
        activity_bar = "█" * int(profile.piece_activity_preference * 15) + "░" * (15 - int(profile.piece_activity_preference * 15))
        text += f"Activity:   {profile.piece_activity_preference*100:4.0f}% {activity_bar}\n"
        
        pawn_bar = "█" * int(profile.pawn_structure_focus * 15) + "░" * (15 - int(profile.pawn_structure_focus * 15))
        text += f"Pawn Str:   {profile.pawn_structure_focus*100:4.0f}% {pawn_bar}\n"
        text += "\n"
        
        # Move Statistics - Compact
        text += " MOVE STATS\n"
        text += "─" * 35 + "\n"
        text += f"Captures: {profile.capture_rate*100:4.1f}%  "
        text += f"Checks: {profile.check_rate*100:4.1f}%  "
        text += f"Castles: {profile.castle_rate*100:4.1f}%\n\n"
        
        # Engine Adaptation - Compact
        text += "  ADAPTATION\n"
        text += "─" * 35 + "\n"
        # Split long explanation into multiple lines
        explanation = style_info['adaptation_explanation']
        words = explanation.split()
        line = ""
        for word in words:
            if len(line + word) < 35:
                line += word + " "
            else:
                text += line + "\n"
                line = word + " "
        if line:
            text += line + "\n"
        text += "\n"
        
        # Evaluation Weights - Compact
        text += "  WEIGHTS\n"
        text += "─" * 35 + "\n"
        weights = self.engine.evaluator.get_weights()
        for key, value in sorted(weights.items()):
            text += f"{key.replace('_', ' ').title():18} {value:4.2f}\n"
        
        # Add Endgame and Mistake Control stats
        text += "\n"
        text += " ADVANCED\n"
        text += "─" * 35 + "\n"
        text += f"Endgame:       {profile.endgame_score*100:4.0f}%\n"
        text += f"Mistake Ctrl:  {profile.mistake_control*100:4.0f}%\n"
        text += f"Blunder Rate:  {profile.blunder_rate*100:4.1f}%\n"
        
        self.style_text.insert(1.0, text)
        
        # Update radar chart
        self._update_radar_chart()
    
    def _update_radar_chart(self):
        """
        Update the radar chart with current profile data.
        
        Performance fix: Only update radar chart when style scores actually change
        (every 5 moves when profile is recalculated), not on every move.
        This prevents GUI blocking from frequent matplotlib redraws.
        """
        if self.radar_chart:
            current_move_count = len(self.engine.current_game_moves)
            
            # Fix: Always show chart data - update on first display or when scores change
            # Update chart if:
            # 1. First time (last_radar_update_move_count == 0) - show initial data
            # 2. It's been 5+ moves since last update (style scores recalculated)
            should_update = False
            
            if self.last_radar_update_move_count == 0:
                # First update - always show initial profile data
                should_update = True
            elif (current_move_count >= 5 and 
                  current_move_count % 5 == 0 and 
                  current_move_count != self.last_radar_update_move_count):
                # Style scores were recalculated
                should_update = True
            
            if should_update:
                # Get profile data in database format
                profile_data = self.engine.profile.get_database_dict()
                profile_data['player_id'] = self.engine.player_id
                profile_data['player_name'] = self.player_name
                
                # Update chart
                self.radar_chart.update_chart(profile_data)
                self.last_radar_update_move_count = current_move_count
    
    def _on_square_click(self, event):
        """Handle square click"""
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        
        clicked_square = (row, col)
        
        if self.engine.board.turn != self.player_color:
            # Show message that it's not player's turn
            self.status_label.config(text="Status: Wait for engine to move", foreground="orange")
            self.root.after(2000, lambda: self._update_display())  # Reset status after 2 seconds
            return  # Not player's turn
        
        if self.selected_square is None:
            # Select piece
            piece = self.engine.board.get_piece(row, col)
            if piece and piece[1] == self.player_color:
                self.selected_square = clicked_square
                self.status_label.config(text="Status: Piece selected - choose destination", foreground="blue")
            else:
                self.status_label.config(text="Status: Select your piece", foreground="black")
            self._update_display()
        else:
            # Try to make move
            from_square = self.selected_square
            to_square = clicked_square
            
            if from_square == to_square:
                # Deselect
                self.selected_square = None
                self.status_label.config(text="Status: Active", foreground="black")
                self._update_display()
            else:
                # Check if move is legal BEFORE attempting
                if not self.engine.board.is_legal_move(from_square, to_square):
                    # Illegal move - show error and deselect
                    self.status_label.config(text="Status: Illegal move! Try again.", foreground="red")
                    piece = self.engine.board.get_piece(row, col)
                    if piece and piece[1] == self.player_color:
                        # Select the clicked piece instead
                        self.selected_square = clicked_square
                        self.status_label.config(text="Status: Piece selected - choose destination", foreground="blue")
                    else:
                        # Deselect
                        self.selected_square = None
                    self._update_display()
                    # Reset status after 2 seconds
                    self.root.after(2000, lambda: self.status_label.config(text="Status: Active", foreground="black"))
                    return
                
                # Make move - make_player_move validates internally
                if self.engine.make_player_move(from_square, to_square):
                    # Move successful - update display
                    self.last_move = (from_square, to_square)
                    self.selected_square = None
                    self.status_label.config(text="Status: Active", foreground="black")
                    
                    # Force immediate display update
                    self._update_display()
                    self.root.update_idletasks()  # Force GUI update
                    
                    self._update_style_info()  # This also updates radar chart
                    
                    # Engine's turn - wait a bit then make engine move
                    self.status_label.config(text="Status: Engine thinking...", foreground="orange")
                    self.root.update_idletasks()
                    self.root.after(300, self._make_engine_move)
                else:
                    # This shouldn't happen if validation worked, but handle it anyway
                    self.status_label.config(text="Status: Illegal move! Try again.", foreground="red")
                    piece = self.engine.board.get_piece(row, col)
                    if piece and piece[1] == self.player_color:
                        self.selected_square = clicked_square
                    else:
                        self.selected_square = None
                    self._update_display()
                    # Reset status after 2 seconds
                    self.root.after(2000, lambda: self.status_label.config(text="Status: Active", foreground="black"))
    
    def _make_engine_move(self):
        """
        Make engine move.
        
        Bug fix: Added error handling to ensure engine always attempts to move,
        even if previous operations failed. This prevents engine from stopping.
        """
        if self.engine.board.turn == self.engine_color:
            try:
                # Verify board state before engine move
                engine_move = self.engine.make_engine_move()
                if engine_move:
                    from_pos, to_pos = engine_move
                    # Verify the move was actually made
                    if self.engine.board.turn == self.player_color:
                        self.last_move = engine_move
                        self.status_label.config(text="Status: Active", foreground="black")
                        
                        # Force immediate display update
                        self._update_display()
                        self.root.update_idletasks()  # Force GUI update
                        
                        # Performance fix: Update style info (radar chart updates are throttled inside)
                        self._update_style_info()
                    else:
                        # Move didn't complete properly
                        print(f"Warning: Engine move {from_pos} -> {to_pos} didn't change turn")
                        self.status_label.config(text="Status: Engine move error", foreground="red")
                else:
                    # Root cause fix: If engine returns None, check if it's checkmate/stalemate
                    from engine.movegen import MoveGenerator
                    movegen = MoveGenerator(self.engine.board)
                    moves = movegen.generate_all_moves(self.engine.board.turn)
                    if not moves:
                        if self.engine.board.is_in_check(self.engine.board.turn):
                            self.status_label.config(text="Status: Checkmate! You win!", foreground="green")
                        else:
                            self.status_label.config(text="Status: Stalemate!", foreground="orange")
                    else:
                        # Engine should have found a move - this is an error
                        print(f"Error: Engine returned None but {len(moves)} moves available")
                        self.status_label.config(text="Status: Engine error - trying fallback", foreground="red")
                        # Try to make first available move as emergency fallback
                        if moves:
                            emergency_move = moves[0]
                            if self.engine.board.make_move(emergency_move[0], emergency_move[1]):
                                self.last_move = emergency_move
                                self.status_label.config(text="Status: Active (fallback move)", foreground="orange")
                                self._update_display()
                                self._update_style_info()
            except Exception as e:
                # Root cause fix: Catch any exceptions during engine move
                print(f"Error during engine move: {e}")
                import traceback
                traceback.print_exc()
                self.status_label.config(text="Status: Engine error - check console", foreground="red")
                # Try emergency fallback
                try:
                    from engine.movegen import MoveGenerator
                    movegen = MoveGenerator(self.engine.board)
                    moves = movegen.generate_all_moves(self.engine.board.turn)
                    if moves:
                        emergency_move = moves[0]
                        if self.engine.board.make_move(emergency_move[0], emergency_move[1]):
                            self.last_move = emergency_move
                            self.status_label.config(text="Status: Active (emergency move)", foreground="orange")
                            self._update_display()
                except:
                    pass  # If even fallback fails, game is likely over
    
    def _new_game(self):
        """Start a new game"""
        # End previous game (saves to database and updates chart)
        self.engine.end_game()
        
        # Start new game
        self.engine.start_new_game()
        self.selected_square = None
        self.last_move = None
        # Performance fix: Reset radar update counter for new game
        self.last_radar_update_move_count = 0
        self._update_display()
        self._update_style_info()  # This updates radar chart
        messagebox.showinfo("New Game", "New game started!")
    
    def _reset_profile(self):
        """Reset player profile"""
        if messagebox.askyesno("Reset Profile", "Are you sure you want to reset your profile? This will clear all learning data."):
            # Create new profile (this effectively resets)
            self.engine.profile_manager.profiles_dir = "profiles"
            self.engine.profile = self.engine.profile_manager.create_profile(self.engine.player_id, self.player_name)
            self.engine.update_adaptation()
            self._update_style_info()
            messagebox.showinfo("Profile Reset", "Player profile has been reset!")
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

