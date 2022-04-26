# most of this is blatantly copied from:
# https://github.com/Fogapod/KiwiBot/blob/master/modules/images/module_fly.py

import random
import time

from math import cos, pi, sin
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import PIL

from PIL import Image

from src.cogs.utils.errorhandler import PINKError
from src.decorators import in_executor

DEG_TO_RAD_RATIO = pi / 180

# fly image side (square)
FLY_SIDE = 60

# degrees to first digit of file name, approximately
DIRECTIONS = {
    120: "1",
    75: "2",
    30: "3",
    345: "4",
    300: "5",
    255: "6",
    210: "7",
    165: "8",
}

# state of legs
FIRST_STATE = 1
FINAL_STATE = 6

# max allowed side of input image
MAX_SIDE = 512


class Fly:
    def __init__(self, speed: float = 1.0):
        self.speed = speed

        self.pos_x = 0
        self.pos_y = 0

        self.bounds_x = (0, 0)
        self.bounds_y = (0, 0)

        self.angle = list(DIRECTIONS.keys())[0]
        self.state = FIRST_STATE

        self._modified = True

    def _rand_pos(self) -> Tuple[int, int]:
        return (random.randint(*self.bounds_x), random.randint(*self.bounds_y))

    def _move_forward(self) -> None:
        angle = self.angle * DEG_TO_RAD_RATIO
        new_x = self.pos_x + round(cos(angle) * self.speed)
        new_y = self.pos_y - round(sin(angle) * self.speed)

        if not ((self.bounds_x[0] <= new_x <= self.bounds_x[1]) and (self.bounds_y[0] <= new_y <= self.bounds_y[1])):

            new_x = min(self.bounds_x[1], max(self.bounds_x[0], new_x))
            new_y = min(self.bounds_y[1], max(self.bounds_y[0], new_y))
            if self.angle > 270:
                self.angle = list(DIRECTIONS.keys())[0]
            else:
                self.angle += 90

        elif (new_x, new_y) != (self.pos_x, self.pos_y):
            self._modifieed = True

        self.pos_x, self.pos_y = new_x, new_y

    def _rand_angle(self) -> int:
        return random.choice(list(DIRECTIONS.keys()) + [self.angle])

    def _increment_state(self) -> None:
        if self.state >= FINAL_STATE:
            self.state = FIRST_STATE
        else:
            self.state += 1

        self._modified = True

    def spawn(self, bounds_x: Tuple[int, int], bounds_y: Tuple[int, int]) -> None:
        self.bounds_x, self.bounds_y = bounds_x, bounds_y

        self.pos_x, self.pos_y = self._rand_pos()
        self.angle = self._rand_angle()
        self.state = FIRST_STATE

        self._modified = True

    def do_step(self) -> None:
        # actions:
        #   0: do not move
        #   1: rotate to target
        #   2: move

        actions = (0, 1, 2)
        weights = (0.15, 0.15, 0.7)

        action = random.choices(actions, weights)[0]
        if action == 0:
            return
        elif action == 1:
            self.angle = self._rand_angle()
        elif action == 2:
            self._move_forward()

        self._increment_state()

        self._modified = True


class FlyDrawer:
    def __init__(
        self,
        src: Image,
        flies: Sequence[Fly],
        steps: int = 100,
        fly_src: PIL.Image = None,
    ):
        self.src = src.convert("RGBA")
        self.src.thumbnail((MAX_SIDE, MAX_SIDE), Image.ANTIALIAS)

        if fly_src:
            self.fly_src = fly_src.convert("RGBA")
            self.fly_src.thumbnail((FLY_SIDE, FLY_SIDE), Image.ANTIALIAS)
        else:
            self.fly_src = None

        for coordinate in self.src.size:
            if FLY_SIDE > coordinate:
                raise PINKError("image is too small", formatted=False)

        self.flies = flies
        self.steps = steps

        bounds_x = (0, self.src.size[0] - FLY_SIDE)
        bounds_y = (0, self.src.size[1] - FLY_SIDE)
        for fly in self.flies:
            fly.spawn(bounds_x, bounds_y)

        self._cached_flies: Dict[str, Image] = {}
        self._frames: List[Image] = []

    def _get_fly_image(self, angle: int, state: int) -> Image:
        name = f"{DIRECTIONS[angle]}_{state if not self.fly_src else 0}"
        if name in self._cached_flies:
            img = self._cached_flies[name]
        else:
            if self.fly_src:
                img = self.fly_src.rotate(angle, expand=True)
            else:
                img = Image.open(Path(__file__).parent / "templates" / "flies" / f"{name}.png")

            self._cached_flies[name] = img

        return img

    def make_frame(self) -> None:
        modified = False
        for fly in self.flies:
            if fly._modified:
                modified = True
                break

        if not modified:
            self._frames.append(self._frames[-1].copy())
            return

        overlay = self.src.copy()

        for fly in self.flies:
            fly._modified = False
            img = self._get_fly_image(fly.angle, fly.state)
            overlay.alpha_composite(img, (fly.pos_x, fly.pos_y))

        self._frames.append(overlay)

    def cleanup(self) -> None:
        for frame in self._frames:
            frame.close()

        for image in self._cached_flies.values():
            image.close()

        self.src.close()
        if self.fly_src:
            self.fly_src.close()

    def run(self) -> str:
        for _ in range(self.steps):
            for fly in self.flies:
                fly.do_step()

            self.make_frame()

        filename = f"/tmp/fly_{time.time()}.gif"
        self._frames[0].save(
            filename,
            format="GIF",
            optimize=True,
            save_all=True,
            append_images=self._frames[1:],
            loop=0,
            # there are some issues with transparency
            # https://github.com/python-pillow/Pillow/issues/4644
            # disposal=3,
        )

        self.cleanup()

        return filename


@in_executor()
def draw_flies(
    src: PIL.Image,
    fly_src: PIL.Image,
    steps: int,
    speed: int,
    amount: int,
) -> str:
    flies = []
    for _ in range(amount):
        flies.append(Fly(speed=speed))

    filename = FlyDrawer(src, flies, steps=steps, fly_src=fly_src).run()
    src.close()
    if fly_src:
        fly_src.close()

    return filename
