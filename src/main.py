"""
Don't Touch Me -- a simple arcade proof-of-concept.

Blue ball player dodges red enemies that chase slowly.
Arrow keys shoot projectiles in 8 directions (combining gives diagonals).
WASD moves the player. ESC hold to quit.
"""

import math
import os
import random

import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = "Don't Touch Me"

PLAYER_RADIUS = 18
PLAYER_SPEED = 300
PLAYER_COLOR = arcade.color.DODGER_BLUE

ENEMY_RADIUS = 14
ENEMY_SPEED = 80
ENEMY_COLOR = arcade.color.RED
SPAWN_INTERVAL = 2.0
MAX_ENEMIES = 30

BULLET_RADIUS = 5
BULLET_SPEED = 500
BULLET_COLOR = arcade.color.YELLOW
BULLET_LIFETIME = 1.5

ESC_HOLD_DURATION = 1.0


class Bullet:
    __slots__ = ("x", "y", "dx", "dy", "life")

    def __init__(self, x: float, y: float, dx: float, dy: float):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.life = BULLET_LIFETIME


class Enemy:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_x = SCREEN_WIDTH / 2
        self.player_y = SCREEN_HEIGHT / 2

        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.spawn_timer = 0.0
        self.score = 0

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.shoot_up = False
        self.shoot_down = False
        self.shoot_left = False
        self.shoot_right = False

        self.esc_pressed = False
        self.esc_held = 0.0
        self._game_over = False

        self._score_text = arcade.Text("Score: 0", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        self._game_over_text = arcade.Text(
            "GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 15,
            arcade.color.RED, 36, anchor_x="center", anchor_y="center", bold=True,
        )
        self._game_over_hint = arcade.Text(
            "Score: 0  |  ESC to quit", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 25,
            arcade.color.WHITE, 16, anchor_x="center", anchor_y="center",
        )

    def on_show_view(self):
        arcade.set_background_color((10, 10, 20))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.move_up = True
        elif key == arcade.key.S:
            self.move_down = True
        elif key == arcade.key.A:
            self.move_left = True
        elif key == arcade.key.D:
            self.move_right = True
        elif key == arcade.key.UP:
            self.shoot_up = True
        elif key == arcade.key.DOWN:
            self.shoot_down = True
        elif key == arcade.key.LEFT:
            self.shoot_left = True
        elif key == arcade.key.RIGHT:
            self.shoot_right = True
        elif key == arcade.key.ESCAPE:
            self.esc_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.move_up = False
        elif key == arcade.key.S:
            self.move_down = False
        elif key == arcade.key.A:
            self.move_left = False
        elif key == arcade.key.D:
            self.move_right = False
        elif key == arcade.key.UP:
            self.shoot_up = False
        elif key == arcade.key.DOWN:
            self.shoot_down = False
        elif key == arcade.key.LEFT:
            self.shoot_left = False
        elif key == arcade.key.RIGHT:
            self.shoot_right = False
        elif key == arcade.key.ESCAPE:
            self.esc_pressed = False
            self.esc_held = 0.0

    def on_update(self, delta_time):
        if self._game_over:
            return

        if self.esc_pressed:
            self.esc_held += delta_time
            if self.esc_held >= ESC_HOLD_DURATION:
                self.window.close()
                return

        self._update_player(delta_time)
        self._update_shooting(delta_time)
        self._update_enemies(delta_time)
        self._update_bullets(delta_time)
        self._check_collisions()

    def _update_player(self, dt):
        dx = 0.0
        dy = 0.0
        if self.move_up:
            dy += 1
        if self.move_down:
            dy -= 1
        if self.move_left:
            dx -= 1
        if self.move_right:
            dx += 1

        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.player_x += dx * PLAYER_SPEED * dt
            self.player_y += dy * PLAYER_SPEED * dt

        self.player_x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, self.player_x))
        self.player_y = max(PLAYER_RADIUS, min(SCREEN_HEIGHT - PLAYER_RADIUS, self.player_y))

    def _update_shooting(self, dt):
        dx = 0.0
        dy = 0.0
        if self.shoot_up:
            dy += 1
        if self.shoot_down:
            dy -= 1
        if self.shoot_left:
            dx -= 1
        if self.shoot_right:
            dx += 1

        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.bullets.append(Bullet(
                self.player_x, self.player_y,
                dx * BULLET_SPEED, dy * BULLET_SPEED,
            ))
            # Only fire once per press -- clear after firing
            self.shoot_up = False
            self.shoot_down = False
            self.shoot_left = False
            self.shoot_right = False

    def _update_enemies(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= SPAWN_INTERVAL and len(self.enemies) < MAX_ENEMIES:
            self.spawn_timer = 0.0
            self._spawn_enemy()

        for e in self.enemies:
            dx = self.player_x - e.x
            dy = self.player_y - e.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                e.x += (dx / dist) * ENEMY_SPEED * dt
                e.y += (dy / dist) * ENEMY_SPEED * dt

    def _spawn_enemy(self):
        side = random.randint(0, 3)
        if side == 0:
            x = random.uniform(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + ENEMY_RADIUS
        elif side == 1:
            x = random.uniform(0, SCREEN_WIDTH)
            y = -ENEMY_RADIUS
        elif side == 2:
            x = -ENEMY_RADIUS
            y = random.uniform(0, SCREEN_HEIGHT)
        else:
            x = SCREEN_WIDTH + ENEMY_RADIUS
            y = random.uniform(0, SCREEN_HEIGHT)
        self.enemies.append(Enemy(x, y))

    def _update_bullets(self, dt):
        alive = []
        for b in self.bullets:
            b.x += b.dx * dt
            b.y += b.dy * dt
            b.life -= dt
            if b.life > 0 and 0 <= b.x <= SCREEN_WIDTH and 0 <= b.y <= SCREEN_HEIGHT:
                alive.append(b)
        self.bullets = alive

    def _check_collisions(self):
        # Bullet vs enemy
        surviving_enemies = []
        for e in self.enemies:
            hit = False
            for b in self.bullets:
                dist = math.hypot(e.x - b.x, e.y - b.y)
                if dist < ENEMY_RADIUS + BULLET_RADIUS:
                    hit = True
                    b.life = 0
                    self.score += 1
                    break
            if not hit:
                surviving_enemies.append(e)
        self.enemies = surviving_enemies

        # Enemy vs player
        for e in self.enemies:
            dist = math.hypot(e.x - self.player_x, e.y - self.player_y)
            if dist < ENEMY_RADIUS + PLAYER_RADIUS:
                self._game_over = True
                break

    def on_draw(self):
        self.clear()

        # Bullets
        for b in self.bullets:
            arcade.draw_circle_filled(b.x, b.y, BULLET_RADIUS, BULLET_COLOR)

        # Enemies
        for e in self.enemies:
            arcade.draw_circle_filled(e.x, e.y, ENEMY_RADIUS, ENEMY_COLOR)

        # Player
        arcade.draw_circle_filled(self.player_x, self.player_y, PLAYER_RADIUS, PLAYER_COLOR)

        self._score_text.text = f"Score: {self.score}"
        self._score_text.draw()

        if self._game_over:
            overlay = arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 400, 120)
            arcade.draw_rect_filled(overlay, (0, 0, 0, 180))
            self._game_over_text.draw()
            self._game_over_hint.text = f"Score: {self.score}  |  ESC to quit"
            self._game_over_hint.draw()

        if self.esc_held > 0:
            bar_w = 200 * (self.esc_held / ESC_HOLD_DURATION)
            esc_bar = arcade.XYWH(SCREEN_WIDTH / 2, 20, bar_w, 8)
            arcade.draw_rect_filled(esc_bar, arcade.color.ORANGE)


def main():
    fullscreen = os.environ.get("LANDUS_FULLSCREEN", "0") == "1"
    window = arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, fullscreen=fullscreen)
    view = GameView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
