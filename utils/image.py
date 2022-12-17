from os.path import join
from io import BytesIO

from PIL import Image, ImageDraw
from utils._base import root

__all__ = ("make_bars",)

_image = Image.open(join(root, "media", "chart.png"))


def make_bars(bar1: int | float, bar2: int | float, bar3: int | float) -> BytesIO:
    buf = BytesIO()
    with _image.copy() as image:
        i = ImageDraw.Draw(image)

        if bar1 > 0:
            i.rectangle(
                fill="#ff0000",
                xy=(
                    (200, 500),  # down left
                    (300, (500 - bar1 * 400))  # up right
                )
            )
        if bar2 > 0:
            i.rectangle(
                fill="#ff0000",
                xy=(
                    (390, 500),  # down left
                    (490, (500 - bar2 * 400))  # up right
                )
            )
        if bar3 > 0:
            i.rectangle(
                fill="#ff0000",
                xy=(
                    (580, 500),  # down left
                    (680, (500 - bar3 * 400))  # up right
                )
            )

        image.save(buf, format="PNG")

    buf.seek(0)
    return buf
