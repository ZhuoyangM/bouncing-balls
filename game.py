"""
    Bouncing ball game - version 1.0
"""
import pygame
import random
import math

# Initialize pygame
pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bouncing Balls Game")
        self.collector_width = 100
        self.collector_height = 20
        self.balls = []
        self.running_time = 90  # Total running time for one round (90s)
        self.start_time = pygame.time.get_ticks()  # Start time
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Ball colors
        self.ball_count = [5, 5, 5]  # Fixed number of balls for each color
        self.collector_pos = 350
        self.collector_speed = 8  # Collector movement speed
        self.moving_left = False
        self.moving_right = False
        self.score = [0, 0, 0]  # To keep track of collected balls
        self.font = pygame.font.Font(None, 36)  # Font for displaying text
        self.result_font = pygame.font.Font(None, 50)
        self.create_balls()
        self.game_over = False
        self.result_message = ""

    def create_balls(self):
        """Creates balls with random initial positions, velocities, and sizes"""
        for i, color in enumerate(self.colors):
            for _ in range(self.ball_count[i]):
                radius = random.randint(10, 20)
                x = random.randint(radius, 800 - radius)
                y = random.randint(radius, 300)
                velocity_x = random.choice([-2, 2])
                velocity_y = random.choice([-2, 2])
                ball = {'color': color, 'radius': radius, 'x': x, 'y': y,
                        'velocity_x': velocity_x, 'velocity_y': velocity_y}
                self.balls.append(ball)

    def check_collision(self, ball1, ball2):
        """Check and resolve collision between two balls"""
        dx = ball1['x'] - ball2['x']
        dy = ball1['y'] - ball2['y']
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < ball1['radius'] + ball2['radius']:
            angle = math.atan2(dy, dx)
            overlap = ball1['radius'] + ball2['radius'] - distance
            ball1['x'] += math.cos(angle) * overlap / 2
            ball1['y'] += math.sin(angle) * overlap / 2
            ball2['x'] -= math.cos(angle) * overlap / 2
            ball2['y'] -= math.sin(angle) * overlap / 2

            # Exchange velocities
            ball1['velocity_x'], ball2['velocity_x'] = ball2['velocity_x'], ball1['velocity_x']
            ball1['velocity_y'], ball2['velocity_y'] = ball2['velocity_y'], ball1['velocity_y']

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if not self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.moving_left = True
                        if event.key == pygame.K_RIGHT:
                            self.moving_right = True
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            self.moving_left = False
                        if event.key == pygame.K_RIGHT:
                            self.moving_right = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reset_game()

            if not self.game_over:
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
                remaining_time = max(0, self.running_time - elapsed_time)
                time_text = self.font.render(f"Time left: {int(remaining_time)}", True, (255, 255, 255))
                self.screen.blit(time_text, (600, 10))

                # Check if all balls are collected
                if all(self.score[i] >= self.ball_count[i] for i in range(len(self.colors))):
                    self.result_message = "Success!"
                    self.game_over = True

                # Check if time is up
                if remaining_time <= 0:
                    self.result_message = "Fail!"
                    self.game_over = True

                # Display balls left to collect
                collect_text = self.font.render(
                    f"Red: {self.ball_count[0] - self.score[0]} "
                    f"Green: {self.ball_count[1] - self.score[1]} "
                    f"Blue: {self.ball_count[2] - self.score[2]}",
                    True, (255, 255, 255)
                )
                self.screen.blit(collect_text, (10, 10))

                # Move the collector
                if self.moving_left:
                    self.collector_pos -= self.collector_speed
                if self.moving_right:
                    self.collector_pos += self.collector_speed
                self.collector_pos = max(0, min(self.collector_pos, 800 - self.collector_width))

                # Draw the collector
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 (self.collector_pos, 580, self.collector_width, self.collector_height))

                # Update and draw the balls
                for ball in self.balls[:]:
                    ball['x'] += ball['velocity_x']
                    ball['y'] += ball['velocity_y']

                    # Ball bouncing off the walls
                    if ball['x'] - ball['radius'] <= 0 or ball['x'] + ball['radius'] >= 800:
                        ball['velocity_x'] *= -1
                        ball['x'] = max(ball['radius'], min(ball['x'], 800 - ball['radius']))  # Correct ball position
                    if ball['y'] - ball['radius'] <= 0:
                        ball['velocity_y'] *= -1
                    if ball['y'] + ball['radius'] >= 600:
                        ball['y'] = 600 - ball['radius']  # Correct ball position at bottom
                        ball['velocity_y'] *= -0.8  # Reverse vertical velocity for bouncing

                    # Ensure balls do not move purely horizontally or vertically
                    if abs(ball['velocity_x']) > 2 and ball['velocity_y'] == 0:
                        ball['velocity_y'] = random.choice([-1, 1])  # Add some vertical movement
                    if abs(ball['velocity_y']) > 2 and ball['velocity_x'] == 0:
                        ball['velocity_x'] = random.choice([-1, 1])  # Add some horizontal movement

                    # Check for collector collision
                    if (self.collector_pos < ball['x'] < self.collector_pos + self.collector_width and
                            580 - ball['radius'] < ball['y'] < 580 + ball['radius']):
                        index = self.colors.index(ball['color'])
                        self.score[index] += 1
                        self.balls.remove(ball)

                    # Check ball-to-ball collisions
                    for other_ball in self.balls:
                        if ball != other_ball:
                            self.check_collision(ball, other_ball)

                    # Draw the ball
                    pygame.draw.circle(self.screen, ball['color'], (int(ball['x']), int(ball['y'])), ball['radius'])

            # If game over, display the result screen
            if self.game_over:
                self.display_result_screen()

            pygame.display.flip()
            clock.tick(60)

    def display_result_screen(self):
        result_text = self.result_font.render(self.result_message, True, (255, 255, 255))
        enter_text = self.font.render("Press Enter to start a new game", True, (255, 255, 255))
        self.screen.blit(result_text, (350, 250))
        self.screen.blit(enter_text, (300, 300))

    def reset_game(self):
        """Reset the game state for a new round"""
        self.balls = []
        self.score = [0, 0, 0]
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self.create_balls()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()