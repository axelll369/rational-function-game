import random
import time
from typing import List

class Obstacle:
    """Represents an obstacle in the game"""
    def __init__(self, x_pos: float):
        self.x_pos = x_pos
        self.height = random.uniform(1.0, 3.0)
        self.width = random.uniform(0.5, 1.5)
        # Different cactus types for visual variety
        self.cactus_types = ['🌵', '🌴', '🌲', '🌳']
        self.cactus_type = random.choice(self.cactus_types)
    
    def update(self, speed: float):
        """Update obstacle position"""
        self.x_pos -= speed

class GameState:
    """Manages the overall game state"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset game to initial state"""
        self.score = 0
        self.distance = 0.0
        self.speed = 1.0
        self.is_jumping = False
        self.jump_timer = 0
        self.game_over = False
        self.obstacles: List[Obstacle] = []
        self.last_obstacle_time = time.time()  # Set to current time so first obstacle waits full interval
        self.last_update_time = time.time()
        self.game_start_time = time.time()  # Track when game started for countdown
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update distance and speed
        self.distance += self.speed * dt
        self.speed = min(3.0, 1.0 + self.distance / 100)  # Gradually increase speed
        
        # Update score based on distance
        self.score += int(self.speed * dt)
        
        # Handle jumping
        if self.is_jumping:
            self.jump_timer -= dt
            if self.jump_timer <= 0:
                self.is_jumping = False
        
        # Spawn new obstacles (first obstacle after 60 seconds, then 45-60 second intervals)
        if len(self.obstacles) == 0 and current_time - self.last_obstacle_time > 60.0:
            # First obstacle after exactly 60 seconds
            self.obstacles.append(Obstacle(50.0))
            self.last_obstacle_time = current_time
        elif len(self.obstacles) > 0 and current_time - self.last_obstacle_time > random.uniform(45.0, 60.0):
            # Subsequent obstacles with random intervals
            self.obstacles.append(Obstacle(50.0))
            self.last_obstacle_time = current_time
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.speed * dt * 10)  # Scale for visual effect
            
            # Remove obstacles that are off screen
            if obstacle.x_pos < -5:
                self.obstacles.remove(obstacle)
            
            # Check collision (if not jumping)
            elif obstacle.x_pos <= 5 and obstacle.x_pos >= -2 and not self.is_jumping:
                self.game_over = True
    
    def jump(self):
        """Make the player jump"""
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_timer = 1.0  # Jump duration
    
    def can_jump(self) -> bool:
        """Check if player can jump"""
        return not self.is_jumping
