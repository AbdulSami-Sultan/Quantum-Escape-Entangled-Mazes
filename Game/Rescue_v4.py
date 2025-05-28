import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Bubble Burst")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUBBLE_COLORS = {
    '0': (0, 100, 255),    # Blue for |0>
    '1': (255, 50, 50),    # Red for |1>
    '+': (180, 0, 180),    # Purple for |+>
    '-': (255, 180, 0)     # Orange for |->
}

FPS = 60
CLOCK = pygame.time.Clock()

# Bubble grid parameters
ROWS = 10
COLS = 10
BUBBLE_RADIUS = 20
GRID_TOP = 50
GRID_LEFT = (WIDTH - (COLS * 2 * BUBBLE_RADIUS)) // 2

# Quantum states
STATES = ['0', '1', '+', '-']

def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

class Bubble:
    def __init__(self, row, col, state):
        self.row = row
        self.col = col
        self.state = state
        self.x = GRID_LEFT + col * 2 * BUBBLE_RADIUS + BUBBLE_RADIUS
        self.y = GRID_TOP + row * 2 * BUBBLE_RADIUS + BUBBLE_RADIUS
        self.popped = False
        self.superposition_timer = 0  # For superposition state random flip timer

    def draw(self):
        if self.popped:
            return
        color = BUBBLE_COLORS[self.state]
        pygame.draw.circle(screen, color, (self.x, self.y), BUBBLE_RADIUS)
        # Draw state symbol inside bubble
        draw_text(self.state, 24, WHITE, self.x - 8, self.y - 12)

    def update(self):
        # If superposition, randomly flip between + and - every 2 seconds approx.
        if self.state in ['+', '-']:
            self.superposition_timer += 1
            if self.superposition_timer > FPS * 2:
                self.superposition_timer = 0
                # Flip superposition state
                self.state = '+' if self.state == '-' else '-'

class Cannon:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.angle = 90  # degrees (straight up)
        self.speed = 8
        self.bubble_state = random.choice(STATES)
        self.bubble_pos = (self.x, self.y)
        self.is_shooting = False
        self.shoot_x = self.x
        self.shoot_y = self.y
        self.dx = 0
        self.dy = 0

    def draw(self):
        # Draw cannon base
        pygame.draw.rect(screen, BLACK, (self.x - 20, self.y, 40, 20))
        # Draw barrel as a line rotating with angle
        barrel_length = 40
        end_x = self.x + barrel_length * math.cos(math.radians(self.angle))
        end_y = self.y - barrel_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 6)
        # Draw loaded bubble
        if not self.is_shooting:
            pygame.draw.circle(screen, BUBBLE_COLORS[self.bubble_state], (self.x, self.y), BUBBLE_RADIUS)
            draw_text(self.bubble_state, 24, WHITE, self.x - 8, self.y - 12)

    def aim(self, dir):
        # dir: 'left' or 'right'
        if dir == 'left':
            self.angle = min(170, self.angle + 2)
        elif dir == 'right':
            self.angle = max(10, self.angle - 2)

    def shoot(self):
        if not self.is_shooting:
            self.is_shooting = True
            rad = math.radians(self.angle)
            self.dx = self.speed * math.cos(rad)
            self.dy = -self.speed * math.sin(rad)
            self.shoot_x = self.x
            self.shoot_y = self.y

    def update(self):
        if self.is_shooting:
            self.shoot_x += self.dx
            self.shoot_y += self.dy
            # Bounce from side walls
            if self.shoot_x < BUBBLE_RADIUS:
                self.shoot_x = BUBBLE_RADIUS
                self.dx = -self.dx
            elif self.shoot_x > WIDTH - BUBBLE_RADIUS:
                self.shoot_x = WIDTH - BUBBLE_RADIUS
                self.dx = -self.dx

    def draw_shot(self):
        if self.is_shooting:
            pygame.draw.circle(screen, BUBBLE_COLORS[self.bubble_state], (int(self.shoot_x), int(self.shoot_y)), BUBBLE_RADIUS)
            draw_text(self.bubble_state, 24, WHITE, int(self.shoot_x) - 8, int(self.shoot_y) - 12)

    def reset_bubble(self):
        self.bubble_state = random.choice(STATES)
        self.is_shooting = False
        self.shoot_x = self.x
        self.shoot_y = self.y

    def apply_gate(self, gate):
        # Apply quantum gate on loaded bubble state before shooting
        if gate == 'X':
            # X gate flips |0> <-> |1>, superpositions unchanged
            if self.bubble_state == '0':
                self.bubble_state = '1'
            elif self.bubble_state == '1':
                self.bubble_state = '0'
        elif gate == 'Z':
            # Z gate flips phase of superpositions: + <-> -
            if self.bubble_state == '+':
                self.bubble_state = '-'
            elif self.bubble_state == '-':
                self.bubble_state = '+'
        elif gate == 'H':
            # Hadamard gate switches between basis and superposition
            if self.bubble_state == '0':
                self.bubble_state = '+'
            elif self.bubble_state == '1':
                self.bubble_state = '-'
            elif self.bubble_state == '+':
                self.bubble_state = '0'
            elif self.bubble_state == '-':
                self.bubble_state = '1'

class BubbleGrid:
    def __init__(self):
        # Grid is 2D list with either None or Bubble objects
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.populate_initial()

    def populate_initial(self):
        # Fill first 5 rows with random bubbles (avoiding superpositions for now)
        for r in range(5):
            for c in range(COLS):
                state = random.choice(['0', '1'])
                self.grid[r][c] = Bubble(r, c, state)

    def draw(self):
        for row in self.grid:
            for bubble in row:
                if bubble:
                    bubble.draw()

    def update(self):
        for row in self.grid:
            for bubble in row:
                if bubble:
                    bubble.update()

    def get_grid_pos(self, x, y):
        # Convert pixel position to grid row,col if inside grid
        col = (x - GRID_LEFT) // (2 * BUBBLE_RADIUS)
        row = (y - GRID_TOP) // (2 * BUBBLE_RADIUS)
        if 0 <= row < ROWS and 0 <= col < COLS:
            return int(row), int(col)
        return None, None

    def can_place(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS and self.grid[row][col] is None

    def place_bubble(self, x, y, state):
        # Place bubble in nearest free grid position near x,y
        row, col = self.get_grid_pos(x, y)
        if row is None or col is None:
            return None
        # If spot taken, try adjacent spots around (row, col)
        if not self.can_place(row, col):
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if self.can_place(nr, nc):
                        row, col = nr, nc
                        break
        if self.can_place(row, col):
            new_bubble = Bubble(row, col, state)
            self.grid[row][col] = new_bubble
            return new_bubble
        return None

    def get_adjacent(self, row, col):
        # Return list of adjacent bubbles (up, down, left, right)
        adj = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc]:
                adj.append(self.grid[nr][nc])
        return adj

    def find_matches(self, bubble):
        # BFS to find all connected bubbles with the same state
        if not bubble:
            return []
        state = bubble.state
        to_visit = [(bubble.row, bubble.col)]
        visited = set()
        matches = []
        while to_visit:
            r, c = to_visit.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            current = self.grid[r][c]
            if current and current.state == state:
                matches.append(current)
                for neighbor in self.get_adjacent(r, c):
                    if (neighbor.row, neighbor.col) not in visited:
                        to_visit.append((neighbor.row, neighbor.col))
        return matches

    def pop_bubbles(self, bubbles):
        for bubble in bubbles:
            self.grid[bubble.row][bubble.col] = None
            bubble.popped = True

    def collapse_superpositions(self):
        # If any superposition bubbles remain, randomly flip their states sometimes
        for row in self.grid:
            for bubble in row:
                if bubble and bubble.state in ['+', '-']:
                    bubble.update()

def main():
    running = True
    cannon = Cannon()
    grid = BubbleGrid()
    score = 0
    font = pygame.font.SysFont("Arial", 24)

    while running:
        screen.fill(WHITE)
        grid.draw()
        cannon.draw()
        cannon.draw_shot()

        # Display score
        draw_text(f"Score: {score}", 24, BLACK, 10, 10)
        # Display instructions
        draw_text("Arrows: Aim Left/Right | Space: Shoot", 18, BLACK, 10, HEIGHT - 60)
        draw_text("Gates: X, Z, H to change bubble state", 18, BLACK, 10, HEIGHT - 40)
        draw_text(f"Loaded Bubble State: {cannon.bubble_state}", 18, BLACK, 10, HEIGHT - 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    cannon.aim('left')
                elif event.key == pygame.K_RIGHT:
                    cannon.aim('right')
                elif event.key == pygame.K_SPACE:
                    cannon.shoot()
                elif event.key == pygame.K_x:
                    cannon.apply_gate('X')
                elif event.key == pygame.K_z:
                    cannon.apply_gate('Z')
                elif event.key == pygame.K_h:
                    cannon.apply_gate('H')

        cannon.update()
        if cannon.is_shooting:
            # Check collision with top grid or other bubbles
            # If y < GRID_TOP + BUBBLE_RADIUS * 2, stick bubble at top row
            if cannon.shoot_y <= GRID_TOP + BUBBLE_RADIUS * 2:
                new_bubble = grid.place_bubble(cannon.shoot_x, cannon.shoot_y, cannon.bubble_state)
                if new_bubble:
                    # Check for matches
                    matches = grid.find_matches(new_bubble)
                    if len(matches) >= 3:
                        grid.pop_bubbles(matches)
                        score += len(matches)
                    cannon.reset_bubble()

            else:
                # Check collision with existing bubbles nearby
                # If close to any bubble (distance < 2*radius), stick there
                stuck = False
                for r in range(ROWS):
                    for c in range(COLS):
                        b = grid.grid[r][c]
                        if b:
                            dist = math.hypot(b.x - cannon.shoot_x, b.y - cannon.shoot_y)
                            if dist <= 2 * BUBBLE_RADIUS:
                                new_bubble = grid.place_bubble(cannon.shoot_x, cannon.shoot_y, cannon.bubble_state)
                                if new_bubble:
                                    matches = grid.find_matches(new_bubble)
                                    if len(matches) >= 3:
                                        grid.pop_bubbles(matches)
                                        score += len(matches)
                                    cannon.reset_bubble()
                                    stuck = True
                                    break
                    if stuck:
                        break

        grid.update()
        grid.collapse_superpositions()

        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
