import pygame
import math

# --- 常量 ---
# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
BROWN = (165, 42, 42)

# 窗口尺寸
WIDTH, HEIGHT = 800, 800

# --- Pygame 初始化 ---
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太阳系模拟")

# --- 天体类 ---
class CelestialBody:
    # 天文单位 (米)
    AU = 149.6e6 * 1000
    # 万有引力常数
    G = 6.67428e-11
    # 比例尺: 1 AU = 100 像素
    SCALE = 250 / AU
    # 时间步长 (1天)
    TIMESTEP = 3600 * 24

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.is_sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                px, py = point
                px = px * self.SCALE + WIDTH / 2
                py = py * self.SCALE + HEIGHT / 2
                updated_points.append((px, py))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        pygame.draw.circle(win, self.color, (x, y), self.radius)

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.is_sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, bodies):
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue

            fx, fy = self.attraction(body)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

# --- 主函数 ---
def main():
    run = True
    clock = pygame.time.Clock()

    # 创建太阳和行星
    sun = CelestialBody(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.is_sun = True

    mercury = CelestialBody(0.387 * CelestialBody.AU, 0, 8, DARK_GREY, 3.30 * 10**23)
    mercury.y_vel = -47.4 * 1000

    venus = CelestialBody(0.723 * CelestialBody.AU, 0, 12, WHITE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000

    earth = CelestialBody(-1 * CelestialBody.AU, 0, 16, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000

    mars = CelestialBody(-1.524 * CelestialBody.AU, 0, 12, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000

    bodies = [sun, mercury, venus, earth, mars]

    frame_count = 0
    max_frames = 1000 # 模拟运行的帧数

    while run:
        clock.tick(60)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for body in bodies:
            body.update_position(bodies)
            body.draw(WIN)

        pygame.display.update()

        frame_count += 1
        if frame_count >= max_frames:
            pygame.image.save(WIN, "solar_system.png")
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()
