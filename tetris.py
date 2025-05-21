import random

# Game board dimensions
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Tetrimino shapes and their rotations
TETROMINOES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]]
    ],
    'J': [
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[0, 1], [0, 1], [1, 1]]
    ],
    'L': [
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]]
    ]
}

# Game board initialization
def create_board():
    """Creates an empty game board."""
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

# Function to generate a new random Tetrimino
def new_tetrimino():
    """Generates a new random Tetrimino."""
    shape = random.choice(list(TETROMINOES.keys()))
    piece_data = {
        'shape_name': shape, # Store the name for easy lookup
        'shape': TETROMINOES[shape],
        'rotation': 0,
        'x': BOARD_WIDTH // 2 - len(TETROMINOES[shape][0][0]) // 2,
        'y': 0
    }
    return piece_data

def get_piece_shape(piece):
    """Returns the actual shape (2D list) of the piece based on its current rotation."""
    return piece['shape'][piece['rotation'] % len(piece['shape'])]

def check_collision(board, piece_obj, new_x=None, new_y=None, new_rotation=None):
    """
    Checks if the piece_obj collides with board boundaries or existing blocks
    at the given new_x, new_y, and new_rotation.
    If new_x, new_y, or new_rotation are None, they default to the piece_obj's current values.
    """
    x = new_x if new_x is not None else piece_obj['x']
    y = new_y if new_y is not None else piece_obj['y']
    
    # Determine the shape to check
    if new_rotation is not None:
        shape_to_check = piece_obj['shape'][new_rotation % len(piece_obj['shape'])]
    else:
        shape_to_check = get_piece_shape(piece_obj)

    for r, row_data in enumerate(shape_to_check):
        for c, cell in enumerate(row_data):
            if cell:  # If this part of the Tetrimino shape is solid
                board_r, board_c = y + r, x + c
                # Check boundaries
                if not (0 <= board_r < BOARD_HEIGHT and 0 <= board_c < BOARD_WIDTH):
                    return True  # Out of bounds
                # Check collision with existing blocks on the board
                if board[board_r][board_c] != 0:
                    return True  # Collision with another block
    return False

def fix_piece_to_board(board, piece_obj):
    """Fixes the current piece onto the board."""
    shape = get_piece_shape(piece_obj)
    for r, row_data in enumerate(shape):
        for c, cell in enumerate(row_data):
            if cell:
                board[piece_obj['y'] + r][piece_obj['x'] + c] = 1 # Mark with 1, or piece_obj['shape_name'] for colors

# Function to clear completed lines
def clear_lines(board):
    """Clears completed lines and shifts blocks down."""
    lines_cleared = 0
    new_board = [row for row in board if not all(cell != 0 for cell in row)]
    lines_cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])
    return new_board, lines_cleared

# Main game loop structure
def main():
    board = create_board()
    current_piece = new_tetrimino()
    game_over = False
    score = 0

    # Basic game timer / speed
    import time
    fall_time = 0
    fall_speed = 0.5  # seconds per drop

    # Game display function
    def draw_board(board_state, piece=None, current_score=0):
        # Screen clearing (ANSI escape sequence)
        print("\033c", end="") 
        # Alternatively, for wider compatibility if ANSI fails:
        # import os
        # os.system('cls' if os.name == 'nt' else 'clear')
        # Or print many newlines:
        # print('\n' * 50)

        header = "Tetris! Controls: a=left, d=right, w=rotate, s=down, q=quit"
        score_display = f"Score: {current_score}"
        
        display_board = [row[:] for row in board_state]
        if piece:
            shape = get_piece_shape(piece)
            for r_idx, row_data in enumerate(shape):
                for c_idx, cell_val in enumerate(row_data):
                    if cell_val: # Part of the Tetrimino
                        # Check bounds before trying to draw on display_board
                        if 0 <= piece['y'] + r_idx < BOARD_HEIGHT and \
                           0 <= piece['x'] + c_idx < BOARD_WIDTH:
                            display_board[piece['y'] + r_idx][piece['x'] + c_idx] = '□' # Current piece
                        # else: part of piece is out of bounds (e.g. during rotation near edge)
        
        print(header)
        print("="*(BOARD_WIDTH*2 + 2))
        for r in range(BOARD_HEIGHT):
            row_str = "|"
            for c in range(BOARD_WIDTH):
                cell = display_board[r][c]
                if cell == 0:
                    row_str += "・" # Empty cell
                elif cell == '□': # Current falling piece
                     row_str += "□ "
                else: # Fixed piece (should be 1 from fix_piece_to_board)
                    row_str += "■ " 
            row_str += "|"
            print(row_str)
        print("="*(BOARD_WIDTH*2 + 2))
        print(score_display)

    last_time = time.time()

    # Initial draw
    draw_board(board, current_piece, score)

    while not game_over:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        fall_time += delta_time

        # --- Player Input (simple non-blocking for console) ---
        # This input method is very basic and blocking.
        # For a real game, you'd use a library like pygame for event handling.
        # We'll simulate a tick-based input for now.
        action = '' # Get input here if using a proper input library

        # --- Automatic Piece Dropping ---
        if fall_time >= fall_speed:
            fall_time = 0
            if not check_collision(board, current_piece, new_y=current_piece['y'] + 1):
                current_piece['y'] += 1
            else:
                fix_piece_to_board(board, current_piece)
                board, lines_cleared_count = clear_lines(board)
                score += lines_cleared_count * 100 # Basic scoring
                current_piece = new_tetrimino()
                if check_collision(board, current_piece):
                    game_over = True
                    print("GAME OVER!")
                    break
        
        # --- Manual Player Controls (Example - needs better input handling) ---
        # This is just a placeholder to show where controls would go.
        # In a real console game, you might use select() or curses.
        # For now, we will process one action per "frame" if available
        # from a hypothetical input queue or a very quick input()
        
        # Re-draw the board for every major event or periodically
        # For this console version, we might draw less frequently or after each action.
        # For now, let's assume we get one input per "tick" or an empty string
        
        # --- Player Input Handling ---
        # This section simulates non-blocking input for a console application.
        # In a real GUI application, event handling would be different.
        # For this console version, we'll use a simple input prompt.
        # To make it feel more like a game, we'll process input quickly
        # and then let the automatic drop handle the passage of time.
        # A more advanced console version might use `select` or `curses`.

        # Instead of blocking input() inside the main loop's time-sensitive part,
        # we are currently using time.sleep(0.1) and the automatic drop.
        # For manual control, we will rely on the user typing commands quickly.
        # This is a limitation of standard console input.
        # The previously commented out input block is a better place for interactive control,
        # but it makes the game turn-based rather than real-time.

        # Let's try to integrate a simple, quick input check.
        # For a better experience, one would typically use a library like `pygame` for input and graphics.
        # The following is a conceptual placeholder for where real input handling would go.
        # To make the provided code runnable and testable without complex input setup,
        # the game relies on automatic drop. Player actions would be manually triggered
        # by uncommenting and adapting an input method.

        # For now, to test player controls, we can temporarily uncomment the blocking input,
        # but it's not ideal for the final game feel.
        # Let's assume for this subtask, the logic for player actions is the focus.

        # --- Automatic Piece Dropping --- (This part is fine)
        if fall_time >= fall_speed:
            fall_time = 0
            if not check_collision(board, current_piece, new_y=current_piece['y'] + 1):
                current_piece['y'] += 1
            else:
                fix_piece_to_board(board, current_piece)
                board, lines_cleared_count = clear_lines(board)
                
                # Update score based on lines cleared
                if lines_cleared_count == 1:
                    score += 100
                elif lines_cleared_count == 2:
                    score += 300
                elif lines_cleared_count == 3:
                    score += 500
                elif lines_cleared_count >= 4: # Tetris or more
                    score += 800
                
                if lines_cleared_count > 0:
                    # Potentially increase speed or score multiplier here
                    pass
                current_piece = new_tetrimino()
                if check_collision(board, current_piece): # Check collision for the new piece
                    game_over = True
                    draw_board(board, None, score) # Draw final board state without current piece
                    print("GAME OVER!")
                    break # Exit main loop
        
        # Draw the board and current piece state before asking for input
        if not game_over:
            draw_board(board, current_piece, score)

        # --- Process Player Input ---
        # Using blocking input() for console playability.
        if not game_over: # Only ask for input if game is still running
            action = input("Action: ").lower()

            if action == 'q':
                game_over = True
                print("Quitting game.")
                # break # Will be caught by the loop condition
            elif action == 'a': # Move Left
                if not check_collision(board, current_piece, new_x=current_piece['x'] - 1):
                    current_piece['x'] -= 1
            elif action == 'd': # Move Right
                if not check_collision(board, current_piece, new_x=current_piece['x'] + 1):
                    current_piece['x'] += 1
            elif action == 'w': # Rotate
                new_rot = (current_piece['rotation'] + 1) % len(current_piece['shape'])
                if not check_collision(board, current_piece, new_rotation=new_rot):
                    current_piece['rotation'] = new_rot
                elif not check_collision(board, current_piece, new_x=current_piece['x']-1, new_rotation=new_rot): # Wall kick left
                    current_piece['x'] -=1
                    current_piece['rotation'] = new_rot
                elif not check_collision(board, current_piece, new_x=current_piece['x']+1, new_rotation=new_rot): # Wall kick right
                    current_piece['x'] +=1
                    current_piece['rotation'] = new_rot

            elif action == 's': # Soft drop
                if not check_collision(board, current_piece, new_y=current_piece['y'] + 1):
                    current_piece['y'] += 1
                    score += 1 # Score for soft drop
                else: # If soft drop causes collision, fix the piece
                    fix_piece_to_board(board, current_piece)
                    board, lines_cleared_count = clear_lines(board)
                    # Update score based on lines cleared
                    if lines_cleared_count == 1:
                        score += 100
                    elif lines_cleared_count == 2:
                        score += 300
                    elif lines_cleared_count == 3:
                        score += 500
                    elif lines_cleared_count >= 4:
                        score += 800

                    if lines_cleared_count > 0:
                        pass # Speed increase could happen here
                    current_piece = new_tetrimino()
                    if check_collision(board, current_piece):
                        game_over = True
                        draw_board(board, None, score) # Draw final state
                        print("GAME OVER!")
                        # break # Will be caught by loop condition
            
            # After player action, redraw immediately if game not over
            if not game_over:
                draw_board(board, current_piece, score)
        
        # Small pause to make the game playable in console, adjust as needed
        # This also makes the input prompt more readable as it won't fight with auto-drop render
        if not game_over: # Avoid sleep if game just ended
            time.sleep(0.05) 

    # Final score display, happens after loop termination
    # draw_board(board, None, score) # Ensure final board is shown
    print(f"Final Score: {score}")

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
