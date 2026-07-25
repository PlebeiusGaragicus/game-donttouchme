"""Screen capture: run with `.venv/bin/python tests/test_screens.py`.

Renders each state to tests/screenshots/. Assertions only catch a blank or
frozen frame -- open the PNGs and look at them.
"""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from harness import SCREENSHOT_DIR, Harness, check, image_stats, report  # noqa: E402

import arcade  # noqa: E402


def capture(h, name, failures, min_colors=3, max_uniform=0.999):
    """A blank frame is 1 color at 100%. This game is mostly flat dark
    background, so the bar is only "something was drawn"."""
    path = h.screenshot(name)
    colors, uniform = image_stats(h.image())
    check(f"{name}: rendered something ({colors} colors, {uniform:.0%} most-common)"
          f" -> {path.split('/')[-1]}",
          colors >= min_colors and uniform <= max_uniform, failures)
    return path


def main() -> int:
    failures = []
    shots = []
    print(f"writing to {SCREENSHOT_DIR}")

    h = Harness().game().step(5)
    shots.append(capture(h, "01-start", failures))

    # Let enemies spawn, then shoot: bullets and enemies both on screen.
    h.step(240)
    h.view.on_key_press(arcade.key.RIGHT, 0)
    h.view.on_key_press(arcade.key.W, 0)
    h.step(30)
    h.view.on_key_release(arcade.key.RIGHT, 0)
    h.view.on_key_release(arcade.key.W, 0)
    shots.append(capture(h, "02-shooting", failures))
    check(f"enemies are on screen ({len(h.view.enemies)})", len(h.view.enemies) > 0, failures)
    check(f"bullets are on screen ({len(h.view.bullets)})", len(h.view.bullets) > 0, failures)

    before = h.image().tobytes()
    h.step(30)
    check("the scene animates", before != h.image().tobytes(), failures)

    # Diagonal fire: two shoot keys at once.
    h.view.on_key_press(arcade.key.UP, 0)
    h.view.on_key_press(arcade.key.LEFT, 0)
    h.step(20)
    h.view.on_key_release(arcade.key.UP, 0)
    h.view.on_key_release(arcade.key.LEFT, 0)
    shots.append(capture(h, "03-diagonal-fire", failures))

    # ESC hold bar over live gameplay.
    h.hold(arcade.key.ESCAPE, 25)
    shots.append(capture(h, "04-esc-hold-bar", failures))
    h.release(arcade.key.ESCAPE)
    h.step(1)

    # Game over screen (which now has to keep responding to ESC).
    from src.main import Enemy

    h.view.enemies = [Enemy(h.view.player_x, h.view.player_y)]
    h.step(3)
    shots.append(capture(h, "05-game-over", failures))
    check("game over reached", h.view._game_over, failures)

    h.close()

    print(f"\n{len(shots)} screenshots in tests/screenshots/ -- open them and look")
    return report(failures, "screens")


if __name__ == "__main__":
    sys.exit(main())
