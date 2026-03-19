import pygame
from sys import exit
from pygame.locals import *
from gameRole import *
import random
import math
import os

pygame.init()

# ================== SCREEN ==================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SkyFire Legacy')

# ================== GIF ANIMATION CLASS ==================
class AnimatedGIF:
    def __init__(self, path, scale_to=None):
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        
        try:
            from PIL import Image
            pil_image = Image.open(path)
            
            # Extract frames from GIF
            frame_num = 0
            while True:
                try:
                    pil_image.seek(frame_num)
                    # Convert PIL image to pygame surface
                    frame = pil_image.convert('RGBA')
                    data = frame.tobytes()
                    size = frame.size
                    
                    # Create pygame surface
                    py_surface = pygame.image.fromstring(data, size, 'RGBA').convert_alpha()
                    
                    # Scale if needed
                    if scale_to:
                        py_surface = pygame.transform.scale(py_surface, scale_to)
                    
                    self.frames.append(py_surface)
                    
                    # Get frame duration (in milliseconds)
                    try:
                        duration = pil_image.info['duration']
                    except:
                        duration = 100  # Default duration
                    
                    if duration < 20:  # Some GIFs have 0 duration
                        duration = 100
                    
                    self.durations.append(duration)
                    
                    frame_num += 1
                except EOFError:
                    break
        except ImportError:
            print("PIL not installed. Install with: pip install Pillow")
            # Fallback to static image
            try:
                static_img = pygame.image.load(path).convert_alpha()
                if scale_to:
                    static_img = pygame.transform.scale(static_img, scale_to)
                self.frames = [static_img]
                self.durations = [100]
            except:
                print(f"Could not load image: {path}")
                # Create a placeholder surface
                placeholder = pygame.Surface(scale_to if scale_to else (800, 600))
                placeholder.fill((255, 0, 255))  # Magenta for missing texture
                self.frames = [placeholder]
                self.durations = [100]
        
        if not self.frames:
            # Create a placeholder surface if no frames loaded
            placeholder = pygame.Surface(scale_to if scale_to else (800, 600))
            placeholder.fill((255, 0, 255))  # Magenta for missing texture
            self.frames = [placeholder]
            self.durations = [100]
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.durations[self.current_frame]:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time
    
    def get_current_frame(self):
        return self.frames[self.current_frame]

# ================== LOAD SOUND ==================
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

# ================== LOAD IMAGES ==================
def load_scaled(path):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        # Create placeholder if image not found
        placeholder = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        placeholder.fill((100, 100, 100))
        return placeholder

# ================== CREATE BOSS IMAGES ==================
def create_boss_images():
    """Create boss images with proper scaling and visibility"""
    boss_img_raw = None
    
    # Try multiple possible boss image locations
    possible_paths = [
        'resources/image/boss.png',
        'resources/image/BOSS.png',
        'resources/image/boss.PNG',
        'resources/image/BOSS.PNG',
        'resources/image/hellfire_drake.png',
        'resources/image/hellfire.png'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                boss_img_raw = pygame.image.load(path).convert_alpha()
                print(f"Successfully loaded boss image from: {path}")
                break
        except:
            continue
    
    if boss_img_raw is None:
        print("WARNING: Could not find boss.png - using placeholder dragon")
        # Create a more detailed placeholder boss (Hellfire Drake)
        boss_img_raw = pygame.Surface((250, 180), pygame.SRCALPHA)
        
        # Body (dark red with gradient)
        for y in range(30, 130):
            color_val = 100 + int((y - 30) * 0.8)
            pygame.draw.ellipse(boss_img_raw, (color_val, 20, 20), (50, y, 150, 100 - (y-30)//2))
        
        # Main body
        pygame.draw.ellipse(boss_img_raw, (180, 30, 30), (50, 30, 150, 100))
        pygame.draw.ellipse(boss_img_raw, (200, 50, 50), (55, 35, 140, 90))
        
        # Head
        pygame.draw.ellipse(boss_img_raw, (200, 40, 40), (170, 40, 60, 50))
        pygame.draw.ellipse(boss_img_raw, (220, 60, 60), (175, 45, 50, 40))
        
        # Eyes (glowing)
        pygame.draw.circle(boss_img_raw, (255, 200, 0), (205, 60), 8)
        pygame.draw.circle(boss_img_raw, (255, 100, 0), (215, 60), 5)
        pygame.draw.circle(boss_img_raw, (255, 255, 200), (208, 58), 3)
        
        # Horns
        pygame.draw.polygon(boss_img_raw, (150, 30, 30), [(190, 30), (180, 10), (200, 15)])
        pygame.draw.polygon(boss_img_raw, (150, 30, 30), [(210, 30), (200, 5), (220, 12)])
        
        # Wings
        pygame.draw.polygon(boss_img_raw, (120, 20, 20), [(100, 50), (60, 10), (30, 30), (70, 60)])
        pygame.draw.polygon(boss_img_raw, (140, 25, 25), [(120, 50), (80, 5), (40, 25), (80, 60)])
        
        # Fire effect (for hellfire)
        for i in range(5):
            fire_x = 220 + i * 8
            fire_y = 70 + i * 3
            fire_size = 15 - i
            fire_color = (255, 100 + i * 30, 20)
            pygame.draw.circle(boss_img_raw, fire_color, (fire_x, fire_y), fire_size)
            
        # Spikes along back
        for i in range(5):
            spike_x = 80 + i * 25
            pygame.draw.polygon(boss_img_raw, (100, 10, 10), 
                               [(spike_x, 35), (spike_x - 10, 20), (spike_x + 10, 20)])
    
    # Scale the boss image
    boss_img = pygame.transform.scale(boss_img_raw, (250, 180))
    
    # Create damaged version (MORE VISIBLE)
    boss_damaged_img = boss_img.copy()
    # Make damaged boss image more visible with red glow
    for x in range(250):
        for y in range(180):
            try:
                color = boss_damaged_img.get_at((x, y))
                if color.a > 0:
                    # Make it more red and add visible damage
                    new_r = min(255, color.r + 150)
                    new_g = max(0, color.g - 80)
                    new_b = max(0, color.b - 80)
                    boss_damaged_img.set_at((x, y), (new_r, new_g, new_b, color.a))
            except:
                pass
    
    # Add visible damage cracks
    for _ in range(15):
        start_pos = (random.randint(50, 200), random.randint(30, 150))
        end_pos = (start_pos[0] + random.randint(-40, 40), 
                   start_pos[1] + random.randint(-30, 30))
        pygame.draw.line(boss_damaged_img, (255, 50, 50), start_pos, end_pos, 3)
        pygame.draw.line(boss_damaged_img, (255, 200, 0), start_pos, end_pos, 1)
    
    # Create enraged boss version (phase 3) - VERY VISIBLE
    boss_enraged_img = pygame.Surface((250, 180), pygame.SRCALPHA)
    boss_enraged_img.blit(boss_img, (0, 0))
    
    # Add intense hellfire glow and rage effects
    for x in range(250):
        for y in range(180):
            try:
                color = boss_enraged_img.get_at((x, y))
                if color.a > 0:
                    # Make it fiery orange-red with maximum visibility
                    new_r = min(255, color.r + 200)
                    new_g = max(0, color.g - 150)
                    new_b = max(0, color.b - 150)
                    boss_enraged_img.set_at((x, y), (new_r, new_g, new_b, color.a))
            except:
                pass
    
    # Add pulsing aura
    for i in range(5):
        aura_color = (255, 100 - i*20, 0, 100 - i*15)
        pygame.draw.ellipse(boss_enraged_img, aura_color, 
                           (10 - i*2, 10 - i, 230 + i*4, 160 + i*2), 3)
    
    # Add flame particles around boss
    for _ in range(20):
        flame_x = random.randint(0, 250)
        flame_y = random.randint(0, 180)
        flame_size = random.randint(3, 8)
        flame_color = (255, random.randint(100, 200), 0, 200)
        pygame.draw.circle(boss_enraged_img, flame_color, (flame_x, flame_y), flame_size)
    
    # Create destruction animation frames (MUCH MORE VISIBLE)
    boss_destroyed_frames = []
    for i in range(15):  # More frames for better animation
        destroyed_surf = pygame.Surface((250, 180), pygame.SRCALPHA)
        # Copy boss image with fade effect
        if i < 8:
            # First half of animation - show boss with explosions
            destroyed_surf.blit(boss_enraged_img if i > 4 else boss_img, (0, 0))
            
            # Add explosion particles
            alpha = 255 - i * 20
            for j in range(20 + i * 5):
                x = random.randint(0, 250)
                y = random.randint(0, 180)
                size = random.randint(8, 25)
                
                # Bigger, brighter explosions
                if random.random() > 0.5:
                    color = (255, random.randint(200, 255), 0, alpha)
                else:
                    color = (255, random.randint(100, 150), 0, alpha)
                
                pygame.draw.circle(destroyed_surf, color, (x, y), size)
                
                # Add secondary explosions
                if j % 3 == 0:
                    pygame.draw.circle(destroyed_surf, (255, 255, 200, alpha), 
                                     (x - 5, y - 5), size // 2)
        else:
            # Second half - just explosions
            alpha = 255 - (i - 8) * 30
            for j in range(30 + (i-8) * 3):
                x = random.randint(0, 250)
                y = random.randint(0, 180)
                size = random.randint(10, 30)
                
                # Bright yellow/orange explosions
                color = (255, random.randint(200, 255), 0, alpha)
                pygame.draw.circle(destroyed_surf, color, (x, y), size)
                
                # Inner white core
                pygame.draw.circle(destroyed_surf, (255, 255, 255, alpha), 
                                 (x - 3, y - 3), size // 2)
        
        boss_destroyed_frames.append(destroyed_surf)
    
    return boss_img, boss_damaged_img, boss_enraged_img, boss_destroyed_frames

# ================== BOSS BULLET CLASS ==================
class BossBullet:
    def __init__(self, x, y, pattern=0):
        self.rect = pygame.Rect(x, y, 15, 25)
        self.speed = 3
        self.color = (255, 100, 0)
        self.speed_x = 0
        self.speed_y = 0
        self.pattern = pattern
        self.age = 0
        
    def move(self):
        self.age += 1
        
        if hasattr(self, 'speed_x') and self.speed_x != 0:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            
            if self.pattern == 2:
                self.rect.x += math.sin(self.age * 0.1) * 1
        else:
            self.rect.y += self.speed
            
            if self.pattern == 1:
                self.rect.x += math.sin(self.age * 0.2) * 2
        
    def draw(self, surface):
        if self.pattern == 0:
            color = (255, 100, 0)
        elif self.pattern == 1:
            color = (255, 50, 50)
        else:
            color = (255, 200, 0)
            
        # Draw hellfire bullet (more detailed)
        pygame.draw.circle(surface, color, self.rect.center, 10)
        pygame.draw.circle(surface, (255, 255, 200), 
                          (self.rect.centerx - 2, self.rect.centery - 2), 4)
        # Fire trail
        for i in range(3):
            trail_pos = (self.rect.centerx - i * 3, self.rect.centery)
            # Ensure color components don't go below 0
            trail_r = max(0, color[0] - i * 50)
            trail_g = max(0, color[1] - i * 30)
            trail_b = max(0, color[2])
            trail_color = (trail_r, trail_g, trail_b)
            pygame.draw.circle(surface, trail_color, trail_pos, 5 - i)

# ================== SCREEN SHAKE ==================
shake_intensity = 0
shake_duration = 0

def apply_shake(surface, offset):
    if shake_duration > 0:
        offset[0] = random.randint(-shake_intensity, shake_intensity)
        offset[1] = random.randint(-shake_intensity, shake_intensity)

# ================== UI DRAWING FUNCTIONS ==================
def draw_player_health(surface, x, y, width, height, player, font_small):
    # Background
    pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
    pygame.draw.rect(surface, (60, 60, 60), (x, y, width, height), 2)
    
    # Health fill
    health_width = int((player.health / player.max_health) * width)
    if health_width > 0:
        if player.health < player.max_health * 0.3:
            health_color = (255, 50, 50)
        elif player.health < player.max_health * 0.6:
            health_color = (255, 255, 50)
        else:
            health_color = (50, 255, 50)
        
        # Draw main health
        pygame.draw.rect(surface, health_color, (x, y, health_width, height))
        
        # Add highlight
        highlight = pygame.Surface((health_width, height//2))
        highlight.set_alpha(50)
        highlight.fill((255, 255, 255))
        surface.blit(highlight, (x, y))
    
    # Health text
    health_text = font_small.render(f"HP: {player.health}/{player.max_health}", True, (255, 255, 255))
    text_rect = health_text.get_rect(midleft=(x + width + 10, y + height//2))
    surface.blit(health_text, text_rect)

def draw_boss_health(surface, x, y, width, height, boss_hp, boss_max_hp, boss_phase, font_medium, font_small):
    # Background with gradient effect
    for i in range(height):
        color_value = 40 + int((i / height) * 20)
        pygame.draw.line(surface, (color_value, color_value, color_value), 
                        (x, y + i), (x + width, y + i))
    
    pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height), 2)
    
    # Health bar with gradient
    health_width = int((boss_hp / boss_max_hp) * width)
    if health_width > 0:
        if boss_hp < boss_max_hp * 0.3:
            color = (255, 50, 50)
            # Pulsing effect for low health
            if pygame.time.get_ticks() % 500 < 250:
                color = (255, 150, 150)
        elif boss_hp < boss_max_hp * 0.6:
            color = (255, 165, 0)
        else:
            color = (50, 255, 50)
        
        # Draw main health with gradient
        for i in range(health_width):
            color_factor = 1.0 - (i / health_width) * 0.3
            adjusted_color = tuple(int(c * color_factor) for c in color)
            pygame.draw.line(surface, adjusted_color, 
                           (x + i, y), (x + i, y + height))
        
        # Add highlight
        highlight = pygame.Surface((health_width, height//3))
        highlight.set_alpha(50)
        highlight.fill((255, 255, 255))
        surface.blit(highlight, (x, y))
    else:
        # Draw empty health bar with warning when boss HP is 0
        warning_text = font_small.render("BOSS DEFEATED!", True, (255, 50, 50))
        warning_rect = warning_text.get_rect(center=(x + width//2, y + height//2))
        surface.blit(warning_text, warning_rect)
    
    # Border with glow effect
    border_color = (255, 215, 0)
    if boss_phase == 3:
        border_color = (255, 50, 50)
        # Add extra glow for enraged with pulsing
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100 + 50
        glow_rect = pygame.Rect(x-3, y-3, width+6, height+6)
        for i in range(3):
            glow_color = (255, int(pulse), 0, 100 - i*30)
            pygame.draw.rect(surface, glow_color, glow_rect.inflate(i*2, i*2), 2)
    
    pygame.draw.rect(surface, border_color, (x, y, width, height), 3)
    
    # Boss name and HP text
    boss_name = font_medium.render("HELLFIRE DRAKE", True, (255, 215, 0))
    name_shadow = font_medium.render("HELLFIRE DRAKE", True, (50, 50, 50))
    surface.blit(name_shadow, (x + 101, y - 28))
    surface.blit(boss_name, (x + 100, y - 30))
    
    # HP percentage (only show if boss is alive)
    if boss_hp > 0:
        hp_percent = int((boss_hp / boss_max_hp) * 100)
        hp_text = font_medium.render(f"{hp_percent}%", True, (255, 255, 255))
        hp_rect = hp_text.get_rect(center=(x + width//2, y + height//2))
        surface.blit(hp_text, hp_rect)
    
    # Phase indicator
    phase_text = f"PHASE {boss_phase}"
    if boss_phase == 3:
        phase_text = "⚡ ENRAGED ⚡"
        phase_color = (255, 50, 50)
        # Pulsing effect
        if pygame.time.get_ticks() % 300 < 150:
            phase_color = (255, 200, 0)
    else:
        phase_color = (255, 215, 0)
        
    boss_phase_display = font_small.render(phase_text, True, phase_color)
    phase_rect = boss_phase_display.get_rect(center=(x + width//2, y + height + 15))
    surface.blit(boss_phase_display, phase_rect)

def draw_bombs(surface, x, y, player, font_medium):
    bomb_icon = font_medium.render("💣", True, (255, 200, 0))
    bomb_count = font_medium.render(f"x {player.bombs}", True, (255, 255, 255))
    
    surface.blit(bomb_icon, (x, y))
    surface.blit(bomb_count, (x + 35, y + 5))

def draw_boss_progress(surface, x, y, width, height, score, BOSS_SPAWN_SCORE, font_small):
    progress = min(score / BOSS_SPAWN_SCORE, 1.0)
    
    # Background
    pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
    pygame.draw.rect(surface, (60, 60, 60), (x, y, width, height), 2)
    
    # Progress fill with gradient
    fill_width = int(width * progress)
    if fill_width > 0:
        color = (255, 100 + int(155 * progress), 0)
        pygame.draw.rect(surface, color, (x, y, fill_width, height))
        
        # Add highlight
        highlight = pygame.Surface((fill_width, height//2))
        highlight.set_alpha(30)
        highlight.fill((255, 255, 255))
        surface.blit(highlight, (x, y))
    
    # Progress text
    needed = max(0, BOSS_SPAWN_SCORE - score)
    if needed > 0:
        progress_text = font_small.render(f"BOSS: {int(progress * 100)}% ({needed} to go)", True, (255, 255, 255))
    else:
        progress_text = font_small.render("BOSS APPROACHING!", True, (255, 50, 50))
        # Pulsing effect
        if pygame.time.get_ticks() % 500 < 250:
            progress_text = font_small.render("BOSS APPROACHING!", True, (255, 200, 0))
    
    surface.blit(progress_text, (x + width + 10, y - 2))

# ================== BOSS ATTACK PATTERNS ==================
def boss_shoot_pattern_1(boss, boss_bullets):
    """Hellfire spread shot"""
    for i in range(-3, 4):
        bullet = BossBullet(boss.centerx + i * 25, boss.bottom, pattern=1)
        bullet.speed = 3.5 + abs(i) * 0.3
        boss_bullets.append(bullet)

def boss_shoot_pattern_2(boss, boss_bullets):
    """Hellfire circle shot"""
    for angle in range(0, 360, 30):
        bullet = BossBullet(boss.centerx, boss.bottom, pattern=2)
        bullet.speed_x = math.cos(math.radians(angle)) * 3
        bullet.speed_y = math.sin(math.radians(angle)) * 3
        boss_bullets.append(bullet)

def boss_shoot_pattern_3(boss, boss_bullets, player):
    """Aimed hellfire shot"""
    dx = player.rect.centerx - boss.centerx
    dy = player.rect.centery - boss.centery
    distance = math.sqrt(dx**2 + dy**2)
    if distance > 0:
        dx /= distance
        dy /= distance
        
        for i in range(5):
            bullet = BossBullet(boss.centerx + (i-2)*15, boss.bottom, pattern=0)
            bullet.speed_x = dx * (4 + i * 0.5)
            bullet.speed_y = dy * (4 + i * 0.5)
            boss_bullets.append(bullet)

def boss_phase_3_attack(boss, boss_bullets, player):
    """Phase 3 (enraged) hellfire attacks - MUCH MORE INTENSE"""
    # Massive spread shot
    for i in range(-6, 7):
        bullet = BossBullet(boss.centerx + i * 20, boss.bottom, pattern=1)
        bullet.speed = 6 + abs(i) * 0.5
        boss_bullets.append(bullet)
    
    # Double circle shot
    for angle in range(0, 360, 20):
        bullet = BossBullet(boss.centerx, boss.bottom, pattern=2)
        bullet.speed_x = math.cos(math.radians(angle)) * 5
        bullet.speed_y = math.sin(math.radians(angle)) * 5
        boss_bullets.append(bullet)
        
        # Second circle with offset
        bullet2 = BossBullet(boss.centerx, boss.bottom, pattern=2)
        bullet2.speed_x = math.cos(math.radians(angle + 10)) * 4
        bullet2.speed_y = math.sin(math.radians(angle + 10)) * 4
        boss_bullets.append(bullet2)
    
    # Triple aimed shot
    dx = player.rect.centerx - boss.centerx
    dy = player.rect.centery - boss.centery
    distance = math.sqrt(dx**2 + dy**2)
    if distance > 0:
        dx /= distance
        dy /= distance
        
        for i in range(3):
            for j in range(-1, 2):
                bullet = BossBullet(boss.centerx + j*30, boss.bottom, pattern=0)
                bullet.speed_x = dx * (5 + i) + j * 0.5
                bullet.speed_y = dy * (5 + i)
                boss_bullets.append(bullet)

# ================== MAIN GAME FUNCTION ==================
def main_game():
    # Global variables that need to be accessible
    global screen, shake_intensity, shake_duration
    
    # ================== LOAD SOUND ==================
    bullet_sound = load_sound('resources/sound/bullet.wav')
    enemy1_down_sound = load_sound('resources/sound/enemy1_down.wav')
    game_over_sound = load_sound('resources/sound/game_over.wav')
    bomb_sound = load_sound('resources/sound/bomb.wav')
    boss_appear_sound = load_sound('resources/sound/bomb.wav')
    boss_hit_sound = load_sound('resources/sound/enemy1_down.wav')
    player_hit_sound = load_sound('resources/sound/game_over.wav')

    # Game music (plays during gameplay)
    try:
        pygame.mixer.music.load('resources/sound/game_music.wav')
    except:
        pass

    # Menu music
    try:
        menu_music = pygame.mixer.Sound('resources/sound/Menu_music.mp3')
    except:
        try:
            menu_music = pygame.mixer.Sound('resources/sound/Menu_music.wav')
        except:
            menu_music = None

    # ================== LOAD IMAGES ==================
    # Static backgrounds
    background = load_scaled('resources/image/background.png')
    game_over_img = load_scaled('resources/image/gameover.png')
    you_win_img = load_scaled('resources/image/youwin.png')

    # Animated GIFs
    menu_bg = AnimatedGIF('resources/image/Menu2.gif', (SCREEN_WIDTH, SCREEN_HEIGHT))
    credit_img = AnimatedGIF('resources/image/creditscene2.gif', (SCREEN_WIDTH, SCREEN_HEIGHT))

    try:
        plane_img = pygame.image.load('resources/image/shoot.png').convert_alpha()
    except:
        # Create placeholder if image not found
        plane_img = pygame.Surface((1000, 1000), pygame.SRCALPHA)
        plane_img.fill((100, 100, 100))

    # ================== CREATE BOSS IMAGES ==================
    boss_img, boss_damaged_img, boss_enraged_img, boss_destroyed_frames = create_boss_images()

    # ================== PLAYER ==================
    player_rects = [
        pygame.Rect(0, 99, 102, 126),
        pygame.Rect(165, 360, 102, 126),
        pygame.Rect(165, 234, 102, 126),
        pygame.Rect(330, 624, 102, 126),
        pygame.Rect(330, 498, 102, 126),
        pygame.Rect(432, 624, 102, 126)
    ]

    player = Player(plane_img, player_rects, [SCREEN_WIDTH//2, SCREEN_HEIGHT-100])
    player.bombs = 9999999999999
    player.max_health = 150
    player.health = player.max_health
    player.speed = 8

    bullet_img = plane_img.subsurface(pygame.Rect(1004, 987, 9, 21)) if plane_img.get_size() != (1000, 1000) else pygame.Surface((9, 21))

    # ================== ENEMY ==================
    enemy_img = plane_img.subsurface(pygame.Rect(534, 612, 57, 43)) if plane_img.get_size() != (1000, 1000) else pygame.Surface((57, 43))
    enemy_down_imgs = [
        plane_img.subsurface(pygame.Rect(267, 347, 57, 43)) if plane_img.get_size() != (1000, 1000) else pygame.Surface((57, 43)),
        plane_img.subsurface(pygame.Rect(873, 697, 57, 43)) if plane_img.get_size() != (1000, 1000) else pygame.Surface((57, 43)),
        plane_img.subsurface(pygame.Rect(267, 296, 57, 43)) if plane_img.get_size() != (1000, 1000) else pygame.Surface((57, 43)),
        plane_img.subsurface(pygame.Rect(930, 697, 57, 43)) if plane_img.get_size() != (1000, 1000) else pygame.Surface((57, 43))
    ]

    # ================== FONTS ==================
    title_font = pygame.font.Font(None, 100)
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 20)

    # ================== MUSIC FUNCTIONS ==================
    menu_music_playing = False
    
    def play_menu_music():
        nonlocal menu_music_playing
        if sound_enabled and menu_music and not menu_music_playing:
            pygame.mixer.music.stop()
            menu_music.play(-1)  # Loop indefinitely
            menu_music_playing = True

    def stop_menu_music():
        nonlocal menu_music_playing
        if menu_music:
            menu_music.stop()
        menu_music_playing = False

    def play_game_music():
        if sound_enabled:
            stop_menu_music()
            try:
                pygame.mixer.music.play(-1)
            except:
                pass

    # ================== GROUPS ==================
    enemies = pygame.sprite.Group()
    enemies_down = pygame.sprite.Group()

    # ================== VARIABLES ==================
    clock = pygame.time.Clock()
    shoot_cd = 0
    enemy_timer = 0
    score = 0
    running = True
    game_win = False
    show_menu = True
    show_credit = False
    show_options = False

    menu_selection = 0
    options_selection = 0
    credit_scroll_y = SCREEN_HEIGHT
    credit_scroll_speed = 1

    sound_enabled = True
    sfx_enabled = True

    invincible_frames = 0
    invincible_duration = 60

    BOSS_SPAWN_SCORE = 150000  # Boss spawns at 150000 score

    # Boss variables
    boss = pygame.Rect(SCREEN_WIDTH//2 - 125, 50, 250, 180)
    boss_hp = 500  # Increased HP for longer fight
    boss_max_hp = 500
    boss_active = False
    boss_entering = False
    boss_bullets = []
    boss_shoot_timer = 0
    boss_attack_pattern = 0
    boss_pattern_timer = 0
    boss_phase = 1
    boss_invulnerable = False
    boss_invulnerable_timer = 0
    boss_hit_cooldown = 0
    boss_destroyed_animation = False
    boss_destroyed_timer = 0
    boss_destroyed_index = 0
    boss_just_defeated = False  # New flag to prevent multiple victory screens

    # ================== MENU FUNCTIONS ==================
    def draw_menu(selection):
        # Update and draw animated menu background
        menu_bg.update()
        screen.blit(menu_bg.get_current_frame(), (0, 0))
        
        # Title with glow effect
        title_text = title_font.render("SKYFIRE LEGACY", True, (255, 215, 0))
        
        for i in range(5):
            glow_surf = title_font.render("SKYFIRE LEGACY", True, (255, 255, 100))
            glow_surf.set_alpha(50 - i*10)
            screen.blit(glow_surf, (SCREEN_WIDTH//2 - 320 - i, 80 - i))
        
        title_shadow = title_font.render("SKYFIRE LEGACY", True, (50, 50, 50))
        screen.blit(title_shadow, (SCREEN_WIDTH//2 - 318, 82))
        screen.blit(title_text, (SCREEN_WIDTH//2 - 320, 80))
        
        # Menu options
        options = ["PLAY", "OPTIONS", "CREDITS", "QUIT"]
        colors = [(255, 255, 255) for _ in range(4)]
        colors[selection] = (255, 215, 0)
        
        y_positions = [250, 330, 410, 490]
        rects = []
        
        for i, (option, color) in enumerate(zip(options, colors)):
            if i == selection:
                arrow = font_large.render(">", True, (255, 215, 0))
                screen.blit(arrow, (SCREEN_WIDTH//2 - 150, y_positions[i]))
            
            text = font_large.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, y_positions[i]))
            
            # Add hover effect with animation
            if rect.collidepoint(pygame.mouse.get_pos()):
                # Pulsing glow effect
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50
                glow_rect = rect.inflate(40 + pulse, 20 + pulse//2)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_surf.fill((255, 215, 0, 30))
                screen.blit(glow_surf, glow_rect)
            
            screen.blit(text, rect)
            rects.append(rect)
        
        # Add floating particles for effect
        for i in range(3):
            particle_x = SCREEN_WIDTH//2 + math.sin(pygame.time.get_ticks() * 0.002 + i) * 50
            particle_y = 300 + math.cos(pygame.time.get_ticks() * 0.003 + i) * 30
            pygame.draw.circle(screen, (255, 215, 0, 100), (int(particle_x), int(particle_y)), 3)
        
        return rects

    def draw_options(selection):
        nonlocal options_selection
        
        # Update and draw animated menu background
        menu_bg.update()
        screen.blit(menu_bg.get_current_frame(), (0, 0))
        
        title_text = font_large.render("OPTIONS", True, (255, 215, 0))
        screen.blit(title_text, (SCREEN_WIDTH//2 - 120, 100))
        
        options = [f"SOUND: {'ON' if sound_enabled else 'OFF'}", 
                   f"SFX: {'ON' if sfx_enabled else 'OFF'}",
                   "BACK TO MENU"]
        
        colors = [(255, 255, 255) for _ in range(3)]
        colors[selection] = (255, 215, 0)
        
        y_positions = [220, 300, 420]
        rects = []
        
        for i, (option, color) in enumerate(zip(options, colors)):
            if i == selection:
                arrow = font_medium.render(">", True, (255, 215, 0))
                screen.blit(arrow, (SCREEN_WIDTH//2 - 200, y_positions[i]))
            
            text = font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, y_positions[i]))
            
            # Add hover effect
            if rect.collidepoint(pygame.mouse.get_pos()) and i != selection:
                options_selection = i
            
            screen.blit(text, rect)
            rects.append(rect)
        
        return rects

    def draw_credits():
        # Update and draw animated credit background
        credit_img.update()
        screen.blit(credit_img.get_current_frame(), (0, 0))
        
        credit_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        credit_surface.set_colorkey((0, 0, 0))
        credit_surface.set_alpha(200)
        
        credits_data = [
            ("DEVELOPER", "Revilla, Sean Benedict C. Developer"),
            ("SOUND DESIGN", "Sugse, Ron"),
            ("MUSIC", "Hamor, Christian"),
            ("ART", "Mugas, John Patrick M"),
            ("Assets", "Siason, Mark Anthony L."),
            ("SPECIAL THANKS", "All Beta Testers"),
            ("ENGINE", "Pygame")
        ]
        
        y_offset = credit_scroll_y
        
        for title, name in credits_data:
            title_text = font_large.render(title, True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            credit_surface.blit(title_text, title_rect)
            
            name_text = font_medium.render(name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, y_offset + 50))
            credit_surface.blit(name_text, name_rect)
            
            y_offset += 120
        
        back_text = font_medium.render("PRESS B OR CLICK HERE TO RETURN", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, 550))
        
        pygame.draw.rect(credit_surface, (100, 100, 100), back_rect.inflate(30, 15))
        pygame.draw.rect(credit_surface, (255, 215, 0), back_rect.inflate(30, 15), 3)
        credit_surface.blit(back_text, back_rect)
        
        screen.blit(credit_surface, (0, 0))
        
        return back_rect

    # ================== MENU LOOP ==================
    # Start playing menu music
    play_menu_music()

    while show_menu:
        if not show_options and not show_credit:
            menu_rects = draw_menu(menu_selection)
        elif show_options:
            options_rects = draw_options(options_selection)
        elif show_credit:
            back_rect = draw_credits()
            credit_scroll_y -= credit_scroll_speed
            if credit_scroll_y < -500:
                credit_scroll_y = SCREEN_HEIGHT
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            
            if event.type == KEYDOWN:
                if not show_options and not show_credit:
                    if event.key == K_UP:
                        menu_selection = (menu_selection - 1) % 4
                    elif event.key == K_DOWN:
                        menu_selection = (menu_selection + 1) % 4
                    elif event.key == K_RETURN:
                        if menu_selection == 0:
                            show_menu = False
                            play_game_music()  # Switch to game music
                        elif menu_selection == 1:
                            show_options = True
                            options_selection = 0
                        elif menu_selection == 2:
                            show_credit = True
                            credit_scroll_y = SCREEN_HEIGHT
                        elif menu_selection == 3:
                            pygame.quit()
                            exit()
                
                elif show_options:
                    if event.key == K_UP:
                        options_selection = (options_selection - 1) % 3
                    elif event.key == K_DOWN:
                        options_selection = (options_selection + 1) % 3
                    elif event.key == K_RETURN:
                        if options_selection == 0:
                            sound_enabled = not sound_enabled
                            if sound_enabled:
                                # Restart menu music if we're in menu
                                if show_menu and not show_credit:
                                    play_menu_music()
                            else:
                                stop_menu_music()
                                pygame.mixer.music.stop()
                        elif options_selection == 1:
                            sfx_enabled = not sfx_enabled
                        elif options_selection == 2:
                            show_options = False
                    elif event.key == K_ESCAPE:
                        show_options = False
                
                elif show_credit:
                    if event.key == K_b or event.key == K_ESCAPE:
                        show_credit = False
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if not show_options and not show_credit:
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mouse_pos):
                            if i == 0:
                                show_menu = False
                                play_game_music()  # Switch to game music
                            elif i == 1:
                                show_options = True
                                options_selection = 0
                            elif i == 2:
                                show_credit = True
                                credit_scroll_y = SCREEN_HEIGHT
                            elif i == 3:
                                pygame.quit()
                                exit()
                
                elif show_options:
                    for i, rect in enumerate(options_rects):
                        if rect.collidepoint(mouse_pos):
                            if i == 0:
                                sound_enabled = not sound_enabled
                                if sound_enabled:
                                    if show_menu and not show_credit:
                                        play_menu_music()
                                else:
                                    stop_menu_music()
                                    pygame.mixer.music.stop()
                            elif i == 1:
                                sfx_enabled = not sfx_enabled
                            elif i == 2:
                                show_options = False
                
                elif show_credit:
                    if back_rect.collidepoint(mouse_pos):
                        show_credit = False

    # ================== GAME LOOP ==================
    # Reset game variables
    running = True
    game_win = False
    score = 0
    boss_active = False
    boss_entering = False
    boss_phase = 1
    boss_hp = boss_max_hp
    boss_destroyed_animation = False
    boss_just_defeated = False
    boss_bullets.clear()
    enemies.empty()
    enemies_down.empty()
    player.health = player.max_health
    player.rect.center = [SCREEN_WIDTH//2, SCREEN_HEIGHT-100]
    invincible_frames = 0
    shoot_cd = 0
    enemy_timer = 0
    boss_shoot_timer = 0
    boss_pattern_timer = 0
    boss_invulnerable = False
    boss_hit_cooldown = 0
    
    while running:
        clock.tick(60)
        
        # Update invincibility frames
        if invincible_frames > 0:
            invincible_frames -= 1
        
        # Update boss hit cooldown
        if boss_hit_cooldown > 0:
            boss_hit_cooldown -= 1

        # -------- SPAWN ENEMY --------
        if not boss_active and not boss_destroyed_animation:
            spawn_rate = max(20, 50 - (score // 1000))
            if enemy_timer % spawn_rate == 0:
                enemies.add(Enemy(enemy_img, enemy_down_imgs,
                                  [random.randint(0, SCREEN_WIDTH - 57), 0]))
            enemy_timer = (enemy_timer + 1) % 100

        # -------- SPAWN BOSS --------
        if score >= BOSS_SPAWN_SCORE and not boss_active and not boss_destroyed_animation and not boss_just_defeated:
            boss_active = True
            boss_entering = True
            boss_phase = 1
            boss_hp = boss_max_hp
            enemies.empty()
            shake_intensity = 20
            shake_duration = 60
            if sfx_enabled and boss_appear_sound:
                boss_appear_sound.play()
            print("BOSS SPAWNED - HELLFIRE DRAKE APPEARS!")  # Debug message

        # -------- BOSS ENTRANCE ANIMATION --------
        if boss_entering:
            boss.y += 1
            if boss.y >= 50:
                boss_entering = False
                boss_shoot_timer = 90

        # -------- BOSS ATTACKS --------
        if boss_active and not boss_entering and not boss_destroyed_animation:
            boss_pattern_timer += 1
            
            if boss_pattern_timer % 180 == 0:  # Faster pattern changes
                boss_attack_pattern = random.randint(0, 2)
                
                # Check for phase change
                if boss_hp < boss_max_hp * 0.3 and boss_phase == 2:
                    boss_phase = 3
                    shake_intensity = 30
                    shake_duration = 120
                    print("BOSS PHASE 3 - ENRAGED!")  # Debug message
                elif boss_hp < boss_max_hp * 0.6 and boss_phase == 1:
                    boss_phase = 2
                    print("BOSS PHASE 2")  # Debug message
            
            boss_shoot_timer -= 1
            if boss_shoot_timer <= 0:
                if boss_phase == 3:  # Enraged - more frequent attacks
                    if boss_attack_pattern == 0:
                        boss_shoot_pattern_1(boss, boss_bullets)
                        boss_shoot_timer = 20
                    elif boss_attack_pattern == 1:
                        boss_shoot_pattern_2(boss, boss_bullets)
                        boss_shoot_timer = 30
                    elif boss_attack_pattern == 2:
                        boss_shoot_pattern_3(boss, boss_bullets, player)
                        boss_shoot_timer = 15
                    else:
                        boss_phase_3_attack(boss, boss_bullets, player)
                        boss_shoot_timer = 40
                elif boss_phase == 2:
                    if boss_attack_pattern == 0:
                        boss_shoot_pattern_1(boss, boss_bullets)
                        boss_shoot_timer = 35
                    elif boss_attack_pattern == 1:
                        boss_shoot_pattern_2(boss, boss_bullets)
                        boss_shoot_timer = 45
                    else:
                        boss_shoot_pattern_3(boss, boss_bullets, player)
                        boss_shoot_timer = 25
                else:  # Phase 1
                    if boss_attack_pattern == 0:
                        boss_shoot_pattern_1(boss, boss_bullets)
                        boss_shoot_timer = 45
                    elif boss_attack_pattern == 1:
                        boss_shoot_pattern_2(boss, boss_bullets)
                        boss_shoot_timer = 60
                    else:
                        boss_shoot_pattern_3(boss, boss_bullets, player)
                        boss_shoot_timer = 30
                
                if sfx_enabled and boss_hit_sound:
                    boss_hit_sound.play()
            
            # Move boss bullets
            for bullet in list(boss_bullets):
                bullet.move()
                
                if invincible_frames <= 0 and bullet.rect.colliderect(player.rect):
                    # More damage in enrage mode
                    damage = 8 if boss_phase < 3 else 15
                    player.health -= damage
                    boss_bullets.remove(bullet)
                    shake_intensity = 8 + (5 if boss_phase == 3 else 0)
                    shake_duration = 10 + (5 if boss_phase == 3 else 0)
                    invincible_frames = invincible_duration
                    if sfx_enabled and player_hit_sound:
                        player_hit_sound.play()
                    
                    if player.health <= 0:
                        player.is_hit = True
                        running = False
                
                if (bullet.rect.top > SCREEN_HEIGHT or bullet.rect.bottom < 0 or
                    bullet.rect.right < 0 or bullet.rect.left > SCREEN_WIDTH):
                    boss_bullets.remove(bullet)

        # -------- MOVE BULLETS --------
        for bullet in list(player.bullets):
            bullet.move()
            if bullet.rect.bottom < 0:
                player.bullets.remove(bullet)

        # -------- MOVE ENEMIES --------
        if not boss_active:
            for enemy in list(enemies):
                enemy.move()
                if invincible_frames <= 0 and pygame.sprite.collide_rect(enemy, player):
                    player.health -= 15
                    enemies.remove(enemy)
                    shake_intensity = 8
                    shake_duration = 10
                    invincible_frames = invincible_duration
                    if sfx_enabled and player_hit_sound:
                        player_hit_sound.play()
                    
                    if player.health <= 0:
                        player.is_hit = True
                        running = False
                if enemy.rect.top > SCREEN_HEIGHT:
                    enemies.remove(enemy)

        # -------- HIT ENEMY --------
        hits = pygame.sprite.groupcollide(enemies, player.bullets, True, True)
        for h in hits:
            enemies_down.add(h)

        # -------- BOSS HIT --------
        if boss_active and not boss_entering and not boss_invulnerable and boss_hit_cooldown <= 0 and not boss_destroyed_animation:
            bullet_hit = False
            for bullet in list(player.bullets):
                if boss.colliderect(bullet.rect):
                    player.bullets.remove(bullet)
                    # Damage based on phase (easier to kill when enraged)
                    if boss_phase == 3:
                        damage = 3  # Actually easier to kill in phase 3 (game balance)
                    elif boss_phase == 2:
                        damage = 2
                    else:
                        damage = 1
                    boss_hp -= damage
                    bullet_hit = True
                    
                    # Extra damage for bombs
                    if hasattr(bullet, 'is_bomb') and bullet.is_bomb:
                        boss_hp -= 10
                    
                    print(f"BOSS HIT! HP: {boss_hp}/{boss_max_hp}")  # Debug message
            
            if bullet_hit:
                shake_intensity = 3 + (5 if boss_phase == 3 else 0)
                shake_duration = 3 + (5 if boss_phase == 3 else 0)
                boss_invulnerable = True
                boss_invulnerable_timer = 8
                boss_hit_cooldown = 3
                    
                if sfx_enabled and boss_hit_sound:
                    boss_hit_sound.play()
                    
                if boss_hp <= 0:
                    print("BOSS HP REACHED 0 - STARTING DESTRUCTION ANIMATION")  # Debug message
                    boss_destroyed_animation = True
                    boss_destroyed_timer = 0
                    boss_destroyed_index = 0
                    shake_intensity = 30
                    shake_duration = 120
                    boss_active = False  # Deactivate boss when destroyed
                    boss_bullets.clear()  # Clear all boss bullets
            
            if boss_invulnerable:
                boss_invulnerable_timer -= 1
                if boss_invulnerable_timer <= 0:
                    boss_invulnerable = False

        # -------- UPDATE SCREEN SHAKE --------
        shake_offset = [0, 0]
        if shake_duration > 0:
            apply_shake(screen, shake_offset)
            shake_duration -= 1
        else:
            shake_intensity = 0

        # -------- DRAW (with shake offset) --------
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_surface.blit(background, (0, 0))

        # Player (with invincibility blink effect)
        if not player.is_hit:
            if invincible_frames <= 0 or invincible_frames % 6 < 3:
                game_surface.blit(player.images[player.img_index], player.rect)
            player.img_index = (player.img_index + 1) % len(player.images)

        # Draw bullets
        player.bullets.draw(game_surface)
        
        # Draw enemies
        enemies.draw(game_surface)

        # Draw explosions
        for e in list(enemies_down):
            if e.down_index < 8:
                game_surface.blit(e.down_imgs[e.down_index // 2], e.rect)
                e.down_index += 1
            else:
                enemies_down.remove(e)
                score += 1000
                if sfx_enabled and enemy1_down_sound:
                    enemy1_down_sound.play()

        # -------- DRAW BOSS AND BULLETS --------
        if boss_active or boss_destroyed_animation:
            if boss_destroyed_animation:
                # Draw destruction animation (MUCH MORE VISIBLE)
                if boss_destroyed_index < len(boss_destroyed_frames):
                    frame = boss_destroyed_frames[boss_destroyed_index]
                    game_surface.blit(frame, (boss.x, boss.y))
                    
                    # Add extra screen shake during destruction
                    shake_intensity = 15
                    shake_duration = 5
                    
                    # Draw "BOSS DEFEATED" text during animation
                    defeated_text = font_large.render("HELLFIRE DRAKE DEFEATED!", True, (255, 215, 0))
                    defeated_rect = defeated_text.get_rect(center=(SCREEN_WIDTH//2, boss.y - 50))
                    game_surface.blit(defeated_text, defeated_rect)
                    
                    boss_destroyed_timer += 1
                    if boss_destroyed_timer > 3:  # Faster animation for more visibility
                        boss_destroyed_timer = 0
                        boss_destroyed_index += 1
                        print(f"Destruction frame: {boss_destroyed_index}/{len(boss_destroyed_frames)}")  # Debug message
                else:
                    print("DESTRUCTION ANIMATION COMPLETE - SHOWING VICTORY SCREEN")  # Debug message
                    boss_destroyed_animation = False
                    boss_just_defeated = True
                    game_win = True
                    running = False
            else:
                # Draw boss with invincibility blink and phase-based appearance
                if not boss_invulnerable or boss_invulnerable_timer % 4 < 2:
                    # Use appropriate image based on phase
                    if boss_phase == 3:
                        game_surface.blit(boss_enraged_img, boss)
                        
                        # Draw rage aura (MORE VISIBLE)
                        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100
                        aura_alpha = int(150 + pulse)
                        
                        # Multiple aura layers
                        for i in range(5):
                            aura_color = (255, 100 - i*20, 0, aura_alpha // (i+1))
                            pygame.draw.ellipse(game_surface, aura_color, 
                                              (boss.x - 25 + i*3, boss.y - 20 + i*2, 
                                               300 - i*8, 220 - i*4), 3)
                        
                        # Add flame particles
                        for _ in range(8):
                            flame_x = boss.x + random.randint(0, 250)
                            flame_y = boss.y + random.randint(0, 180)
                            flame_size = random.randint(8, 20)
                            flame_alpha = random.randint(150, 255)
                            pygame.draw.circle(game_surface, (255, 150, 0, flame_alpha), 
                                             (flame_x, flame_y), flame_size)
                    elif boss_hp < boss_max_hp * 0.3:
                        game_surface.blit(boss_damaged_img, boss)
                    else:
                        game_surface.blit(boss_img, boss)
                
                # Add phase indicators
                if boss_phase == 3:
                    # Draw rage text (MORE VISIBLE)
                    rage_text = font_medium.render("⚡ ENRAGED ⚡", True, (255, 50, 50))
                    rage_rect = rage_text.get_rect(center=(boss.centerx, boss.y - 30))
                    game_surface.blit(rage_text, rage_rect)
                    
                    # Pulsing effect
                    if pygame.time.get_ticks() % 300 < 150:
                        rage_text2 = font_medium.render("⚡ ENRAGED ⚡", True, (255, 200, 0))
                        game_surface.blit(rage_text2, rage_rect)
            
            # Draw boss bullets (only if not in destruction animation)
            if not boss_destroyed_animation:
                for bullet in boss_bullets:
                    bullet.draw(game_surface)
            
            # Draw boss health bar (only if not in destruction animation and boss is active)
            if not boss_destroyed_animation and boss_active:
                bar_width = 400
                bar_height = 30
                bar_x = (SCREEN_WIDTH - bar_width) // 2
                bar_y = 20
                draw_boss_health(game_surface, bar_x, bar_y, bar_width, bar_height, 
                                boss_hp, boss_max_hp, boss_phase, font_medium, font_small)

        # -------- DRAW UI --------
        # Score
        score_text = font_medium.render(f"SCORE: {score}", True, (255, 255, 100))
        score_shadow = font_medium.render(f"SCORE: {score}", True, (100, 100, 0))
        game_surface.blit(score_shadow, (12, 12))
        game_surface.blit(score_text, (10, 10))
        
        # Boss progress bar
        if not boss_active and not boss_destroyed_animation and not boss_just_defeated:
            draw_boss_progress(game_surface, 10, 50, 200, 15, score, BOSS_SPAWN_SCORE, font_small)
        
        # Player health bar
        draw_player_health(game_surface, 10, 80, 200, 20, player, font_small)
        
        # Bombs
        draw_bombs(game_surface, 10, 110, player, font_medium)

        # Draw target score warning
        if not boss_active and not boss_destroyed_animation and score > BOSS_SPAWN_SCORE * 0.8 and not boss_just_defeated:
            warning_text = font_small.render(f"{BOSS_SPAWN_SCORE - score} TO BOSS!", True, (255, 100, 100))
            game_surface.blit(warning_text, (SCREEN_WIDTH - 200, 50))

        # Draw debug info
        debug_text = font_tiny.render(f"BOSS HP: {boss_hp} | PHASE: {boss_phase} | DESTROYED: {boss_destroyed_animation}", True, (255, 255, 255))
        game_surface.blit(debug_text, (10, SCREEN_HEIGHT - 20))

        # Draw to screen with shake
        screen.blit(game_surface, shake_offset)
        pygame.display.update()

        # -------- EVENTS --------
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        # -------- CONTROLS --------
        keys = pygame.key.get_pressed()

        if not player.is_hit:
            move_speed = player.speed
            if keys[K_LSHIFT] or keys[K_RSHIFT]:
                move_speed = 4
            
            if keys[K_w] and player.rect.top > 0:
                player.rect.y -= move_speed
            if keys[K_s] and player.rect.bottom < SCREEN_HEIGHT:
                player.rect.y += move_speed
            if keys[K_a] and player.rect.left > 0:
                player.rect.x -= move_speed
            if keys[K_d] and player.rect.right < SCREEN_WIDTH:
                player.rect.x += move_speed

            if keys[K_j] and shoot_cd == 0:
                player.shoot(bullet_img)
                if sfx_enabled and bullet_sound:
                    bullet_sound.play()
                shoot_cd = 8

            if keys[K_k] and player.bombs > 0:
                if boss_active:
                    # Bombs do more damage in enrage mode
                    bomb_damage = 30 if boss_phase < 3 else 20
                    boss_hp -= bomb_damage
                    shake_intensity = 15 + (10 if boss_phase == 3 else 0)
                    shake_duration = 25 + (15 if boss_phase == 3 else 0)
                    # Clear some boss bullets
                    for i in range(min(8 + (4 if boss_phase == 3 else 0), len(boss_bullets))):
                        if boss_bullets:
                            boss_bullets.pop(random.randint(0, len(boss_bullets)-1))
                else:
                    # Clear all enemies
                    for enemy in list(enemies):
                        enemies_down.add(enemy)
                    enemies.empty()
                
                player.bombs -= 1
                if sfx_enabled and bomb_sound:
                    bomb_sound.play()

        if shoot_cd > 0:
            shoot_cd -= 1

    # ================== END SCREEN ==================
    # Stop game music
    pygame.mixer.music.stop()

    if game_win:
        # Clear the screen
        screen.blit(background, (0, 0))
        
        # Draw victory screen
        screen.blit(you_win_img, (0, 0))
        
        # Add victory text with glow
        victory_text = font_large.render("HELLFIRE DRAKE DEFEATED!", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        # Add glow effect
        for i in range(5):
            glow_surf = font_large.render("HELLFIRE DRAKE DEFEATED!", True, (255, 255, 100))
            glow_surf.set_alpha(50 - i*10)
            screen.blit(glow_surf, (victory_rect.x - i, victory_rect.y - i))
        
        screen.blit(victory_text, victory_rect)
        
        # Add instructions
        continue_text = font_medium.render("Press any key to continue...", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        screen.blit(continue_text, continue_rect)
        
        pygame.display.update()
        
        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    waiting = False
                if event.type == MOUSEBUTTONDOWN:
                    waiting = False
    else:
        screen.blit(game_over_img, (0, 0))
        pygame.display.update()
        pygame.time.delay(3000)

    if sfx_enabled and game_over_sound:
        game_over_sound.play()

    # ================== CREDIT SCENE AFTER GAME ==================
    show_credit = True
    credit_scroll_y = SCREEN_HEIGHT

    # Play menu music for credits
    play_menu_music()

    while show_credit:
        # Update and draw animated credit background
        credit_img.update()
        screen.blit(credit_img.get_current_frame(), (0, 0))
        
        credit_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        credit_surface.set_colorkey((0, 0, 0))
        credit_surface.set_alpha(200)
        
        credits_data = [
            ("DEVELOPER", "Revilla, Sean Benedict C. Developer"),
            ("SOUND DESIGN", "Sugse, Ron"),
            ("MUSIC", "Hamor, Christian"),
            ("ART", "Mugas, John Patrick M"),
            ("Assets", "Siason, Mark Anthony L."),
            ("SPECIAL THANKS", "All Beta Testers"),
            ("ENGINE", "Pygame"),
            ("", ""),
            ("THANK YOU FOR PLAYING!", "")
        ]
        
        y_offset = credit_scroll_y
        
        for title, name in credits_data:
            if title:
                title_text = font_large.render(title, True, (255, 215, 0))
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                credit_surface.blit(title_text, title_rect)
            
            if name:
                name_text = font_medium.render(name, True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, y_offset + (50 if title else 0)))
                credit_surface.blit(name_text, name_rect)
            
            y_offset += 100
        
        back_text = font_medium.render("PRESS B OR CLICK HERE TO RETURN TO MENU", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, 550))
        
        pygame.draw.rect(credit_surface, (100, 100, 100), back_rect.inflate(30, 15))
        pygame.draw.rect(credit_surface, (255, 215, 0), back_rect.inflate(30, 15), 3)
        credit_surface.blit(back_text, back_rect)
        
        screen.blit(credit_surface, (0, 0))
        
        credit_scroll_y -= credit_scroll_speed
        if credit_scroll_y < -600:
            credit_scroll_y = SCREEN_HEIGHT
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_b or event.key == K_ESCAPE:
                    show_credit = False
            if event.type == MOUSEBUTTONDOWN:
                if back_rect.collidepoint(pygame.mouse.get_pos()):
                    show_credit = False

    stop_menu_music()

# ================== MAIN PROGRAM LOOP ==================
while True:
    main_game()