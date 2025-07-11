import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import json
from game_logic import GameState, Obstacle
from question_generator import QuestionGenerator
from score_manager import ScoreManager
from math_utils import RationalFunction

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = GameState()
if 'question_gen' not in st.session_state:
    st.session_state.question_gen = QuestionGenerator()
if 'score_manager' not in st.session_state:
    st.session_state.score_manager = ScoreManager()
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'show_leaderboard' not in st.session_state:
    st.session_state.show_leaderboard = False

def reset_game():
    """Reset the game state"""
    st.session_state.game_state = GameState()
    st.session_state.current_question = None
    st.session_state.game_started = False

def start_game():
    """Start a new game"""
    if st.session_state.player_name.strip():
        st.session_state.game_started = True
        st.session_state.game_state.reset()
        st.session_state.current_question = st.session_state.question_gen.generate_question()
        st.rerun()

def render_game_canvas():
    """Create a visual ASCII representation of the game"""
    canvas_width = 60
    canvas_height = 8
    
    # Initialize canvas with spaces
    canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]
    
    # Draw ground
    for i in range(canvas_width):
        canvas[canvas_height - 1][i] = '─'
    
    # Draw dinosaur with emoji
    dino_pos = 5  # Fixed position for dinosaur
    if st.session_state.game_state.is_jumping:
        # Jumping dinosaur
        canvas[canvas_height - 4][dino_pos] = '🦕'
        canvas[canvas_height - 3][dino_pos] = '↑'
    else:
        # Running dinosaur with simple animation
        animation_frame = int(st.session_state.game_state.distance) % 2
        if animation_frame == 0:
            canvas[canvas_height - 2][dino_pos] = '🦕'
            canvas[canvas_height - 1][dino_pos] = '‾'
        else:
            canvas[canvas_height - 2][dino_pos] = '🦕'
            canvas[canvas_height - 1][dino_pos] = '¯'
    
    # Draw obstacles (emoji cactuses)
    for obstacle in st.session_state.game_state.obstacles:
        if 0 <= obstacle.x_pos <= canvas_width - 5:
            obstacle_screen_pos = int(obstacle.x_pos)
            if obstacle_screen_pos < canvas_width - 2:
                # Draw cactus using the obstacle's cactus type
                canvas[canvas_height - 2][obstacle_screen_pos] = obstacle.cactus_type
                canvas[canvas_height - 3][obstacle_screen_pos] = '|'
    
    # Add distance markers
    for i in range(0, canvas_width, 10):
        if i < canvas_width:
            canvas[canvas_height - 1][i] = '+'
    
    # Add some clouds for atmosphere
    cloud_positions = [15, 35, 50]
    for pos in cloud_positions:
        if pos < canvas_width - 3:
            canvas[1][pos] = '☁'
            canvas[1][pos + 1] = '☁'
            canvas[2][pos] = '☁'
    
    # Convert canvas to string
    canvas_str = '\n'.join([''.join(row) for row in canvas])
    
    return canvas_str

def handle_answer(answer):
    """Handle player's answer to the question"""
    if st.session_state.current_question:
        is_correct = st.session_state.current_question.check_answer(answer)
        if is_correct:
            st.session_state.game_state.jump()
            st.session_state.game_state.score += 10
            st.success("Correct! You jumped over the obstacle!")
        else:
            st.session_state.game_state.game_over = True
            st.error(f"Incorrect! The correct answer was: {st.session_state.current_question.correct_answer}")
            st.session_state.score_manager.add_score(st.session_state.player_name, st.session_state.game_state.score)
        
        # Generate new question for next obstacle
        st.session_state.current_question = st.session_state.question_gen.generate_question()
        time.sleep(1)  # Brief pause
        st.rerun()

def render_game():
    """Render the main game interface"""
    st.title("🦕 Rational Function Runner")
    
    # Game info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Score", st.session_state.game_state.score)
    with col2:
        st.metric("Distance", f"{st.session_state.game_state.distance:.1f}m")
    with col3:
        st.metric("Speed", f"{st.session_state.game_state.speed:.1f}")
    with col4:
        # Show countdown to next obstacle
        current_time = time.time()
        time_since_start = current_time - st.session_state.game_state.game_start_time
        if len(st.session_state.game_state.obstacles) == 0:
            time_to_first_obstacle = max(0, 60.0 - time_since_start)
            st.metric("Next Obstacle", f"{time_to_first_obstacle:.1f}s")
        else:
            time_since_last = current_time - st.session_state.game_state.last_obstacle_time
            time_to_next = max(0, 45.0 - time_since_last)  # Minimum time to next
            st.metric("Next Obstacle", f"{time_to_next:.1f}s")
    
    # Create visual game canvas
    st.subheader("Game Area")
    
    # Create a visual representation of the game
    game_canvas = render_game_canvas()
    st.markdown(f"```\n{game_canvas}\n```")
    
    # Show helpful timing message if no obstacles yet
    if len(st.session_state.game_state.obstacles) == 0:
        current_time = time.time()
        time_since_start = current_time - st.session_state.game_state.game_start_time
        if time_since_start < 60:
            st.info(f"🕐 Get ready! Your first question will appear in {60 - time_since_start:.1f} seconds. You'll have plenty of time to answer!")
    
    # Show current question if there's an obstacle approaching (increased distance for more time)
    if st.session_state.current_question and st.session_state.game_state.obstacles:
        next_obstacle = min(st.session_state.game_state.obstacles, key=lambda x: x.x_pos)
        if next_obstacle.x_pos < 50:  # Show question when obstacle is much farther away
            st.subheader("🚨 Obstacle Approaching! Answer to Jump!")
            
            # Create two columns - question on left, graph on right
            question_col, graph_col = st.columns([2, 1])
            
            with question_col:
                # Display the rational function
                st.write("**Rational Function:**")
                st.latex(st.session_state.current_question.function.to_latex())
                
                # Display the question
                st.write(f"**Question:** {st.session_state.current_question.question}")
                
                # Answer input
                if st.session_state.current_question.question_type == "multiple_choice":
                    answer = st.radio("Choose your answer:", st.session_state.current_question.options)
                    if st.button("Submit Answer"):
                        handle_answer(answer)
                else:
                    answer = st.text_input("Enter your answer:")
                    if st.button("Submit Answer"):
                        handle_answer(answer)
            
            with graph_col:
                # Show the graph - smaller size
                st.write("**Graph:**")
                fig, ax = plt.subplots(figsize=(5, 4))
                st.session_state.current_question.function.plot(ax)
                st.pyplot(fig)
    
    # Game controls
    st.subheader("Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Game"):
            reset_game()
    with col2:
        if st.button("🏆 Show Leaderboard"):
            st.session_state.show_leaderboard = True
            st.rerun()
    
    # Auto-update game state
    if not st.session_state.game_state.game_over:
        st.session_state.game_state.update()
        time.sleep(0.1)
        st.rerun()

def render_game_over():
    """Render game over screen"""
    st.title("🦕 Game Over!")
    st.subheader(f"Final Score: {st.session_state.game_state.score}")
    st.write(f"Distance Traveled: {st.session_state.game_state.distance:.1f}m")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Play Again"):
            reset_game()
    with col2:
        if st.button("🏆 View Leaderboard"):
            st.session_state.show_leaderboard = True
            st.rerun()

def render_leaderboard():
    """Render the leaderboard"""
    st.title("🏆 Leaderboard")
    
    scores = st.session_state.score_manager.get_top_scores()
    
    if scores:
        for i, (name, score) in enumerate(scores, 1):
            if i == 1:
                st.write(f"🥇 {i}. {name} - {score} points")
            elif i == 2:
                st.write(f"🥈 {i}. {name} - {score} points")
            elif i == 3:
                st.write(f"🥉 {i}. {name} - {score} points")
            else:
                st.write(f"{i}. {name} - {score} points")
    else:
        st.write("No scores yet! Be the first to play!")
    
    if st.button("🔙 Back to Game"):
        st.session_state.show_leaderboard = False
        st.rerun()

def main():
    """Main application function"""
    st.set_page_config(
        page_title="Rational Function Runner",
        page_icon="🦕",
        layout="wide"
    )
    
    # Show leaderboard if requested
    if st.session_state.show_leaderboard:
        render_leaderboard()
        return
    
    # Game not started - show start screen
    if not st.session_state.game_started:
        st.title("🦕 Rational Function Runner")
        st.subheader("Learn rational functions while running!")
        
        st.write("""
        **How to Play:**
        1. Enter your name below
        2. As you run, obstacles will appear
        3. Answer rational function questions correctly to jump over obstacles
        4. Wrong answers end the game
        5. Your score increases with distance and correct answers
        
        **Topics Covered:**
        - Horizontal and vertical asymptotes
        - Holes in rational functions
        - X and Y intercepts
        - End behavior and limits
        """)
        
        # Player name input
        st.session_state.player_name = st.text_input("Enter your name:", value=st.session_state.player_name)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎮 Start Game", disabled=not st.session_state.player_name.strip()):
                start_game()
        with col2:
            if st.button("🏆 View Leaderboard"):
                st.session_state.show_leaderboard = True
                st.rerun()
    
    # Game is running
    elif st.session_state.game_started and not st.session_state.game_state.game_over:
        render_game()
    
    # Game over
    else:
        render_game_over()

if __name__ == "__main__":
    main()
