import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import time
import json
import copy
import sys
from datetime import datetime

class SudokuGame:
    """Sudoku game logic and puzzle generation"""
    
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.difficulty = "Medium"
        self.start_time = None
        self.elapsed_time = 0
        self.hints_used = 0
        self.mistakes = 0
        self.game_active = False
        self.selected_cell = None
        self.notes = [[[False for _ in range(9)] for _ in range(9)] for _ in range(9)]
        self.highlight_conflicts = True
        self.auto_notes = False
        
    def generate_puzzle(self, difficulty="Medium"):
        """Generate a new Sudoku puzzle based on difficulty"""
        self.difficulty = difficulty
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill the board using backtracking
        self._fill_board(0, 0)
        self.solution = copy.deepcopy(self.board)
        
        # Remove numbers based on difficulty
        cells_to_remove = {
            "Easy": 30,
            "Medium": 40,
            "Hard": 50,
            "Expert": 55,
            "Master": 60
        }
        
        remove_count = cells_to_remove.get(difficulty, 40)
        self._remove_numbers(remove_count)
        self.initial_board = copy.deepcopy(self.board)
        
        # Reset game state
        self.start_time = time.time()
        self.elapsed_time = 0
        self.hints_used = 0
        self.mistakes = 0
        self.game_active = True
        self.selected_cell = None
        self.notes = [[[False for _ in range(9)] for _ in range(9)] for _ in range(9)]
        
        return self.board
    
    def _fill_board(self, row, col):
        """Recursive backtracking to fill the board"""
        if row == 9:
            return True
            
        if col == 9:
            return self._fill_board(row + 1, 0)
            
        if self.board[row][col] != 0:
            return self._fill_board(row, col + 1)
        
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for num in numbers:
            if self._is_valid(row, col, num):
                self.board[row][col] = num
                if self._fill_board(row, col + 1):
                    return True
                self.board[row][col] = 0
                
        return False
    
    def _remove_numbers(self, count):
        """Remove numbers while ensuring a unique solution"""
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        
        removed = 0
        for row, col in cells:
            if removed >= count:
                break
                
            # Store the value
            temp = self.board[row][col]
            if temp == 0:
                continue
                
            # Try removing it
            self.board[row][col] = 0
            
            # Check if still has unique solution
            solutions = self._count_solutions(copy.deepcopy(self.board))
            if solutions == 1:
                removed += 1
            else:
                # Put it back
                self.board[row][col] = temp
    
    def _count_solutions(self, board, count=0):
        """Count number of solutions (used for uniqueness check)"""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self._is_valid_on_board(board, row, col, num):
                            board[row][col] = num
                            count = self._count_solutions(board, count)
                            board[row][col] = 0
                            if count > 1:
                                return count
                    return count
        return count + 1
    
    def _is_valid_on_board(self, board, row, col, num):
        """Check if a number is valid on a given board"""
        # Check row
        for c in range(9):
            if board[row][c] == num:
                return False
        
        # Check column
        for r in range(9):
            if board[r][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = row // 3, col // 3
        for r in range(box_row * 3, box_row * 3 + 3):
            for c in range(box_col * 3, box_col * 3 + 3):
                if board[r][c] == num:
                    return False
        
        return True
    
    def _is_valid(self, row, col, num):
        """Check if a number can be placed at (row, col)"""
        return self._is_valid_on_board(self.board, row, col, num)
    
    def is_correct(self, row, col, num):
        """Check if placed number matches solution"""
        return self.solution[row][col] == num
    
    def get_hint(self):
        """Get a hint (reveal a correct cell)"""
        if not self.game_active:
            return None
            
        # Find an empty cell
        empty_cells = [(r, c) for r in range(9) for c in range(9) 
                      if self.board[r][c] == 0]
        
        if not empty_cells:
            return None
            
        row, col = random.choice(empty_cells)
        correct_value = self.solution[row][col]
        
        # Update board
        self.board[row][col] = correct_value
        self.hints_used += 1
        
        return row, col, correct_value
    
    def check_solution(self):
        """Check if current board matches solution"""
        for row in range(9):
            for col in range(9):
                if self.board[row][col] != self.solution[row][col]:
                    return False
        return True
    
    def solve_puzzle(self):
        """Solve the current puzzle completely"""
        if not self.game_active:
            return
            
        self.board = copy.deepcopy(self.solution)
        return True
    
    def place_number(self, row, col, num):
        """Place a number on the board"""
        if not self.game_active:
            return False, "Game not active"
            
        if self.initial_board[row][col] != 0:
            return False, "Cannot modify initial numbers"
            
        if num < 1 or num > 9:
            return False, "Invalid number"
            
        self.board[row][col] = num
        
        # Check if correct
        if not self.is_correct(row, col, num):
            self.mistakes += 1
            if self.highlight_conflicts:
                return False, "Incorrect"
            else:
                self.board[row][col] = 0
                return False, "Incorrect - number removed"
        
        # Check if puzzle is complete
        if self.check_solution():
            self.game_active = False
            return True, "Puzzle completed!"
            
        return True, "Correct"
    
    def toggle_note(self, row, col, num):
        """Toggle a note/pencil mark"""
        if not self.game_active:
            return
            
        if self.initial_board[row][col] == 0:
            self.notes[row][col][num-1] = not self.notes[row][col][num-1]
    
    def clear_cell(self, row, col):
        """Clear a cell"""
        if not self.game_active:
            return
            
        if self.initial_board[row][col] == 0:
            self.board[row][col] = 0
            # Clear notes for this cell
            for i in range(9):
                self.notes[row][col][i] = False
    
    def get_conflicts(self, row, col, num):
        """Get conflicting cells for a given number"""
        conflicts = []
        
        if num == 0:
            return conflicts
        
        # Check row
        for c in range(9):
            if c != col and self.board[row][c] == num:
                conflicts.append((row, c))
        
        # Check column
        for r in range(9):
            if r != row and self.board[r][col] == num:
                conflicts.append((r, col))
        
        # Check 3x3 box
        box_row, box_col = row // 3, col // 3
        for r in range(box_row * 3, box_row * 3 + 3):
            for c in range(box_col * 3, box_col * 3 + 3):
                if (r != row or c != col) and self.board[r][c] == num:
                    conflicts.append((r, c))
        
        return conflicts
    
    def update_time(self):
        """Update elapsed time"""
        if self.game_active and self.start_time:
            self.elapsed_time = int(time.time() - self.start_time)
    
    def save_game(self, filename):
        """Save current game state to file"""
        game_state = {
            'board': self.board,
            'initial_board': self.initial_board,
            'solution': self.solution,
            'difficulty': self.difficulty,
            'elapsed_time': self.elapsed_time,
            'hints_used': self.hints_used,
            'mistakes': self.mistakes,
            'game_active': self.game_active,
            'notes': self.notes,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(game_state, f)
    
    def load_game(self, filename):
        """Load game state from file"""
        try:
            with open(filename, 'r') as f:
                game_state = json.load(f)
            
            self.board = game_state['board']
            self.initial_board = game_state['initial_board']
            self.solution = game_state['solution']
            self.difficulty = game_state['difficulty']
            self.elapsed_time = game_state['elapsed_time']
            self.hints_used = game_state['hints_used']
            self.mistakes = game_state['mistakes']
            self.game_active = game_state['game_active']
            self.notes = game_state['notes']
            
            # Update start time if game is active
            if self.game_active:
                self.start_time = time.time() - self.elapsed_time
            
            return True
        except:
            return False


class SudokuUI:
    """Sudoku game user interface"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Sudoku")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Game instance
        self.game = SudokuGame()
        
        # Colors
        self.colors = {
            'bg': '#f0f0f0',
            'grid_bg': '#ffffff',
            'cell_bg': '#ffffff',
            'initial_cell_bg': '#e8f4f8',
            'selected_cell_bg': '#c9e9ff',
            'conflict_cell_bg': '#ffcccc',
            'same_number_bg': '#e6f7ff',
            'highlight_bg': '#f0f8ff',
            'grid_line': '#000000',
            'thick_line': '#000000',
            'text': '#000000',
            'initial_text': '#0000aa',
            'note_text': '#666666',
            'button_bg': '#4a86e8',
            'button_fg': '#ffffff',
            'timer_bg': '#333333',
            'timer_fg': '#ffffff'
        }
        
        # Fonts
        self.cell_font = font.Font(family="Arial", size=20, weight="bold")
        self.note_font = font.Font(family="Arial", size=9)
        self.button_font = font.Font(family="Arial", size=11)
        self.timer_font = font.Font(family="Courier", size=14, weight="bold")
        self.title_font = font.Font(family="Arial", size=18, weight="bold")
        
        # Variables
        self.selected_cell = None
        self.number_buttons = []
        self.cell_widgets = [[None for _ in range(9)] for _ in range(9)]
        self.timer_running = False
        self.highlight_same = True
        
        self.setup_ui()
        self.start_timer()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame - Title and controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            top_frame,
            text="Advanced Sudoku",
            font=self.title_font,
            bg=self.colors['bg']
        )
        title_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Difficulty selector
        diff_frame = ttk.Frame(top_frame)
        diff_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(diff_frame, text="Difficulty:").pack(side=tk.LEFT, padx=(0, 5))
        self.difficulty_var = tk.StringVar(value="Medium")
        difficulties = ["Easy", "Medium", "Hard", "Expert", "Master"]
        diff_menu = ttk.Combobox(
            diff_frame,
            textvariable=self.difficulty_var,
            values=difficulties,
            state="readonly",
            width=10
        )
        diff_menu.pack(side=tk.LEFT)
        diff_menu.bind("<<ComboboxSelected>>", self.change_difficulty)
        
        # New game button
        new_game_btn = tk.Button(
            top_frame,
            text="New Game",
            font=self.button_font,
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            command=self.new_game
        )
        new_game_btn.pack(side=tk.LEFT, padx=10)
        
        # Middle frame - Game board and controls
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Game board
        board_frame = ttk.Frame(middle_frame)
        board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create Sudoku grid
        self.create_board(board_frame)
        
        # Right panel - Controls and info
        control_frame = ttk.Frame(middle_frame, width=200)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_frame.pack_propagate(False)
        
        # Timer display
        timer_frame = tk.Frame(control_frame, bg=self.colors['timer_bg'])
        timer_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.timer_label = tk.Label(
            timer_frame,
            text="00:00:00",
            font=self.timer_font,
            bg=self.colors['timer_bg'],
            fg=self.colors['timer_fg'],
            padx=10,
            pady=5
        )
        self.timer_label.pack()
        
        # Stats frame
        stats_frame = ttk.LabelFrame(control_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.hints_label = tk.Label(
            stats_frame,
            text="Hints: 0",
            font=self.button_font
        )
        self.hints_label.pack(anchor=tk.W, pady=2)
        
        self.mistakes_label = tk.Label(
            stats_frame,
            text="Mistakes: 0",
            font=self.button_font
        )
        self.mistakes_label.pack(anchor=tk.W, pady=2)
        
        self.diff_label = tk.Label(
            stats_frame,
            text="Difficulty: Medium",
            font=self.button_font
        )
        self.diff_label.pack(anchor=tk.W, pady=2)
        
        # Game control buttons
        btn_frame = ttk.LabelFrame(control_frame, text="Game Controls", padding=10)
        btn_frame.pack(fill=tk.X)
        
        buttons = [
            ("Hint", self.give_hint),
            ("Check Solution", self.check_solution),
            ("Solve Puzzle", self.solve_puzzle),
            ("Clear Cell", self.clear_selected),
            ("Undo", self.undo_move),
            ("Redo", self.redo_move)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                font=self.button_font,
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                command=command,
                width=15
            )
            btn.pack(pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(control_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Highlight options
        self.highlight_var = tk.BooleanVar(value=True)
        highlight_cb = tk.Checkbutton(
            options_frame,
            text="Highlight conflicts",
            variable=self.highlight_var,
            font=self.button_font,
            command=self.toggle_highlight
        )
        highlight_cb.pack(anchor=tk.W, pady=2)
        
        self.highlight_same_var = tk.BooleanVar(value=True)
        highlight_same_cb = tk.Checkbutton(
            options_frame,
            text="Highlight same numbers",
            variable=self.highlight_same_var,
            font=self.button_font,
            command=self.toggle_highlight_same
        )
        highlight_same_cb.pack(anchor=tk.W, pady=2)
        
        # Note mode toggle
        self.note_mode_var = tk.BooleanVar(value=False)
        note_btn = tk.Checkbutton(
            options_frame,
            text="Note Mode (Pencil Marks)",
            variable=self.note_mode_var,
            font=self.button_font,
            command=self.toggle_note_mode
        )
        note_btn.pack(anchor=tk.W, pady=2)
        
        # Bottom frame - Number pad
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Number buttons
        num_frame = ttk.Frame(bottom_frame)
        num_frame.pack()
        
        for i in range(1, 10):
            btn = tk.Button(
                num_frame,
                text=str(i),
                font=self.cell_font,
                width=3,
                height=1,
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                command=lambda n=i: self.number_click(n)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.number_buttons.append(btn)
        
        # Clear button
        clear_btn = tk.Button(
            num_frame,
            text="Clear",
            font=self.button_font,
            width=6,
            height=1,
            bg="#e74c3c",
            fg="white",
            command=self.clear_click
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Save/Load buttons
        save_load_frame = ttk.Frame(bottom_frame)
        save_load_frame.pack(pady=(10, 0))
        
        save_btn = tk.Button(
            save_load_frame,
            text="Save Game",
            font=self.button_font,
            bg="#27ae60",
            fg="white",
            command=self.save_game
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = tk.Button(
            save_load_frame,
            text="Load Game",
            font=self.button_font,
            bg="#f39c12",
            fg="white",
            command=self.load_game
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize with a new game
        self.new_game()
    
    def create_board(self, parent):
        """Create the 9x9 Sudoku grid"""
        board_canvas = tk.Canvas(
            parent,
            bg=self.colors['grid_bg'],
            highlightthickness=0
        )
        board_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        board_canvas.bind("<Configure>", self.resize_board)
        board_canvas.bind("<Button-1>", self.board_click)
        
        self.board_canvas = board_canvas
        self.cell_size = 50  # Initial size
        
        # Create cell frames (invisible, for event handling)
        self.cell_frames = [[None for _ in range(9)] for _ in range(9)]
        
        for row in range(9):
            for col in range(9):
                frame = tk.Frame(
                    board_canvas,
                    bg=self.colors['cell_bg'],
                    width=self.cell_size,
                    height=self.cell_size
                )
                self.cell_frames[row][col] = frame
                
                # Create label for numbers
                label = tk.Label(
                    frame,
                    text="",
                    font=self.cell_font,
                    bg=self.colors['cell_bg'],
                    fg=self.colors['text']
                )
                label.place(relx=0.5, rely=0.5, anchor="center")
                self.cell_widgets[row][col] = label
        
    def resize_board(self, event=None):
        """Resize the board when window size changes"""
        if not self.board_canvas:
            return
            
        width = self.board_canvas.winfo_width()
        height = self.board_canvas.winfo_height()
        
        # Calculate cell size
        self.cell_size = min(width, height) // 10
        
        # Redraw grid
        self.board_canvas.delete("all")
        self.draw_grid()
        self.update_board_display()
        
        # Position cell frames
        for row in range(9):
            for col in range(9):
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                
                self.board_canvas.create_window(
                    x, y,
                    window=self.cell_frames[row][col],
                    width=self.cell_size,
                    height=self.cell_size
                )
    
    def draw_grid(self):
        """Draw the Sudoku grid lines"""
        # Draw thick lines for 3x3 boxes
        for i in range(0, 10, 3):
            # Vertical lines
            x = i * self.cell_size
            self.board_canvas.create_line(
                x, 0, x, 9 * self.cell_size,
                width=3, fill=self.colors['thick_line']
            )
            # Horizontal lines
            y = i * self.cell_size
            self.board_canvas.create_line(
                0, y, 9 * self.cell_size, y,
                width=3, fill=self.colors['thick_line']
            )
        
        # Draw thin lines for cells
        for i in range(1, 9):
            if i % 3 != 0:
                # Vertical lines
                x = i * self.cell_size
                self.board_canvas.create_line(
                    x, 0, x, 9 * self.cell_size,
                    width=1, fill=self.colors['grid_line']
                )
                # Horizontal lines
                y = i * self.cell_size
                self.board_canvas.create_line(
                    0, y, 9 * self.cell_size, y,
                    width=1, fill=self.colors['grid_line']
                )
    
    def update_board_display(self):
        """Update the display with current board state"""
        for row in range(9):
            for col in range(9):
                value = self.game.board[row][col]
                label = self.cell_widgets[row][col]
                frame = self.cell_frames[row][col]
                
                # Set cell background
                if self.game.initial_board[row][col] != 0:
                    frame.config(bg=self.colors['initial_cell_bg'])
                elif self.selected_cell and self.selected_cell == (row, col):
                    frame.config(bg=self.colors['selected_cell_bg'])
                else:
                    frame.config(bg=self.colors['cell_bg'])
                
                # Highlight conflicts
                if (self.highlight_var.get() and value != 0 and 
                    self.game.get_conflicts(row, col, value)):
                    frame.config(bg=self.colors['conflict_cell_bg'])
                
                # Highlight same numbers
                if (self.highlight_same_var.get() and self.selected_cell and 
                    value != 0 and value == self.get_selected_value()):
                    frame.config(bg=self.colors['same_number_bg'])
                
                # Update label
                if value != 0:
                    label.config(
                        text=str(value),
                        font=self.cell_font,
                        fg=self.colors['initial_text'] if self.game.initial_board[row][col] != 0 else self.colors['text']
                    )
                else:
                    # Show notes if any
                    notes = self.game.notes[row][col]
                    note_text = ""
                    for i, note in enumerate(notes):
                        if note:
                            note_text += str(i+1)
                        else:
                            note_text += " "
                        if i % 3 == 2 and i < 8:
                            note_text += "\n"
                    
                    if any(notes):
                        label.config(
                            text=note_text,
                            font=self.note_font,
                            fg=self.colors['note_text']
                        )
                    else:
                        label.config(text="")
        
        # Update stats
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        self.hints_label.config(text=f"Hints: {self.game.hints_used}")
        self.mistakes_label.config(text=f"Mistakes: {self.game.mistakes}")
        self.diff_label.config(text=f"Difficulty: {self.game.difficulty}")
    
    def board_click(self, event):
        """Handle click on the board"""
        if not self.game.game_active:
            return
            
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if 0 <= row < 9 and 0 <= col < 9:
            # Don't select initial cells if in note mode
            if self.note_mode_var.get() and self.game.initial_board[row][col] != 0:
                return
                
            self.selected_cell = (row, col)
            self.game.selected_cell = (row, col)
            self.update_board_display()
    
    def number_click(self, number):
        """Handle number button click"""
        if not self.selected_cell or not self.game.game_active:
            return
            
        row, col = self.selected_cell
        
        # Don't modify initial cells
        if self.game.initial_board[row][col] != 0:
            messagebox.showwarning("Warning", "Cannot modify initial numbers!")
            return
        
        if self.note_mode_var.get():
            # Add/remove note
            self.game.toggle_note(row, col, number)
        else:
            # Place number
            success, message = self.game.place_number(row, col, number)
            
            if not success:
                messagebox.showwarning("Warning", message)
        
        self.update_board_display()
        
        # Check if game is complete
        if message == "Puzzle completed!":
            self.game_complete()
    
    def clear_click(self):
        """Handle clear button click"""
        if not self.selected_cell or not self.game.game_active:
            return
            
        row, col = self.selected_cell
        
        # Don't clear initial cells
        if self.game.initial_board[row][col] != 0:
            messagebox.showwarning("Warning", "Cannot clear initial numbers!")
            return
        
        self.game.clear_cell(row, col)
        self.update_board_display()
    
    def clear_selected(self):
        """Clear the selected cell"""
        if self.selected_cell:
            self.clear_click()
    
    def new_game(self):
        """Start a new game"""
        difficulty = self.difficulty_var.get()
        self.game.generate_puzzle(difficulty)
        self.selected_cell = None
        self.game.selected_cell = None
        self.update_board_display()
        self.start_timer()
        
        messagebox.showinfo("New Game", f"New {difficulty} puzzle generated!")
    
    def change_difficulty(self, event=None):
        """Change game difficulty"""
        if self.game.game_active:
            response = messagebox.askyesno(
                "Change Difficulty",
                "Changing difficulty will start a new game. Continue?"
            )
            if response:
                self.new_game()
    
    def give_hint(self):
        """Give a hint to the player"""
        if not self.game.game_active:
            messagebox.showinfo("Game Complete", "The puzzle is already solved!")
            return
            
        hint = self.game.get_hint()
        if hint:
            row, col, value = hint
            self.selected_cell = (row, col)
            self.update_board_display()
            
            # Check if game is complete
            if self.game.check_solution():
                self.game_complete()
        else:
            messagebox.showinfo("Hint", "No empty cells remaining!")
    
    def check_solution(self):
        """Check the current solution"""
        if not self.game.game_active:
            messagebox.showinfo("Game Complete", "The puzzle is already solved!")
            return
            
        if self.game.check_solution():
            messagebox.showinfo("Solution Check", "Congratulations! Your solution is correct!")
            self.game_complete()
        else:
            incorrect_cells = []
            for row in range(9):
                for col in range(9):
                    if (self.game.board[row][col] != 0 and 
                        self.game.board[row][col] != self.game.solution[row][col]):
                        incorrect_cells.append((row, col))
            
            message = f"Found {len(incorrect_cells)} incorrect cells."
            if incorrect_cells:
                message += "\n\nIncorrect cells (row, column):\n"
                for i, (r, c) in enumerate(incorrect_cells[:10]):
                    message += f"({r+1}, {c+1}) "
                    if (i + 1) % 5 == 0:
                        message += "\n"
            
            messagebox.showinfo("Solution Check", message)
    
    def solve_puzzle(self):
        """Solve the entire puzzle"""
        if not self.game.game_active:
            messagebox.showinfo("Game Complete", "The puzzle is already solved!")
            return
            
        response = messagebox.askyesno(
            "Solve Puzzle",
            "This will solve the entire puzzle. Are you sure?"
        )
        
        if response:
            self.game.solve_puzzle()
            self.update_board_display()
            self.game_complete()
    
    def toggle_highlight(self):
        """Toggle conflict highlighting"""
        self.game.highlight_conflicts = self.highlight_var.get()
        self.update_board_display()
    
    def toggle_highlight_same(self):
        """Toggle same number highlighting"""
        self.highlight_same = self.highlight_same_var.get()
        self.update_board_display()
    
    def toggle_note_mode(self):
        """Toggle note/pencil mark mode"""
        if self.note_mode_var.get():
            # Highlight cells where notes can be added
            for row in range(9):
                for col in range(9):
                    if self.game.initial_board[row][col] != 0:
                        self.cell_frames[row][col].config(bg="#f0f0f0")
        else:
            self.update_board_display()
    
    def get_selected_value(self):
        """Get value of selected cell"""
        if self.selected_cell:
            row, col = self.selected_cell
            return self.game.board[row][col]
        return 0
    
    def undo_move(self):
        """Undo last move (simplified - clear selected cell)"""
        # Note: For full undo/redo, you'd need to implement a move history
        if self.selected_cell:
            self.clear_click()
    
    def redo_move(self):
        """Redo last move (placeholder)"""
        messagebox.showinfo("Redo", "Redo functionality would require move history implementation.")
    
    def start_timer(self):
        """Start or restart the game timer"""
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update the timer display"""
        if self.timer_running and self.game.game_active:
            self.game.update_time()
            
            # Format time
            hours = self.game.elapsed_time // 3600
            minutes = (self.game.elapsed_time % 3600) // 60
            seconds = self.game.elapsed_time % 60
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            
            # Schedule next update
            self.root.after(1000, self.update_timer)
    
    def game_complete(self):
        """Handle game completion"""
        self.game.game_active = False
        self.timer_running = False
        
        # Calculate score
        score = self.calculate_score()
        
        # Show completion message
        hours = self.game.elapsed_time // 3600
        minutes = (self.game.elapsed_time % 3600) // 60
        seconds = self.game.elapsed_time % 60
        
        message = (
            f"🎉 Puzzle Completed! 🎉\n\n"
            f"Difficulty: {self.game.difficulty}\n"
            f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}\n"
            f"Hints used: {self.game.hints_used}\n"
            f"Mistakes: {self.game.mistakes}\n"
            f"Score: {score}\n\n"
            f"Well done!"
        )
        
        messagebox.showinfo("Puzzle Complete", message)
    
    def calculate_score(self):
        """Calculate a score based on performance"""
        # Base score for completing
        score = 1000
        
        # Deductions
        time_penalty = min(self.game.elapsed_time // 60, 500)  # 1 point per minute
        hint_penalty = self.game.hints_used * 50
        mistake_penalty = self.game.mistakes * 25
        
        # Difficulty multiplier
        multipliers = {
            "Easy": 1,
            "Medium": 2,
            "Hard": 3,
            "Expert": 4,
            "Master": 5
        }
        
        multiplier = multipliers.get(self.game.difficulty, 1)
        
        final_score = max(0, (score - time_penalty - hint_penalty - mistake_penalty) * multiplier)
        
        return final_score
    
    def save_game(self):
        """Save the current game"""
        if not self.game.game_active:
            messagebox.showinfo("Save Game", "No active game to save!")
            return
            
        filename = f"sudoku_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.game.save_game(filename)
        messagebox.showinfo("Save Game", f"Game saved as {filename}")
    
    def load_game(self):
        """Load a saved game"""
        # Note: This is a simplified version
        # In a full implementation, you'd use filedialog
        response = messagebox.askyesno(
            "Load Game",
            "This will load the last saved game. Continue?"
        )
        
        if response:
            # Try to load the most recent save
            import glob
            saves = glob.glob("sudoku_save_*.json")
            if saves:
                latest = max(saves, key=os.path.getctime)
                if self.game.load_game(latest):
                    self.selected_cell = None
                    self.update_board_display()
                    self.start_timer()
                    messagebox.showinfo("Load Game", f"Game loaded from {latest}")
                else:
                    messagebox.showerror("Load Game", "Failed to load game!")
            else:
                messagebox.showinfo("Load Game", "No saved games found!")


def main():
    """Main function to run the Sudoku game"""
    root = tk.Tk()
    
    # Set window icon and title
    root.title("Advanced Sudoku")
    
    # Create and run the game
    game = SudokuUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    root.geometry(f"{max(width, 900)}x{max(height, 700)}+{x}+{y}")
    
    # Bind keyboard shortcuts
    root.bind("<Key>", lambda event: game.number_click(int(event.char)) if event.char.isdigit() else None)
    root.bind("<Delete>", lambda event: game.clear_selected())
    root.bind("<BackSpace>", lambda event: game.clear_selected())
    root.bind("<Escape>", lambda event: root.quit())
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()