from io import BytesIO
from pathlib import Path

from rembg import remove
from PIL import Image, ImageFilter


CANVAS_SIZE = 1000
PRODUCT_MAX_SIZE = 850
BACKGROUND_COLOR = "WHITE"
ADD_SHADOW = False


def make_product_card(input_path: Path, output_path: Path):
    with open(input_path, "rb") as file:
        image_bytes = file.read()

    output_bytes = remove(image_bytes)
    product = Image.open(BytesIO(output_bytes)).convert("RGBA")

    # Обрезаем прозрачные края вокруг объекта
    bbox = product.getbbox()
    if bbox:
        product = product.crop(bbox)

    MAX_UPSCALE = 1.8

    ratio = min(
        PRODUCT_MAX_SIZE / product.width,
        PRODUCT_MAX_SIZE / product.height
        )

    ratio = min(ratio, MAX_UPSCALE)

    new_width = int(product.width * ratio)
    new_height = int(product.height * ratio)

    product = product.resize((new_width, new_height), Image.LANCZOS)

    product = product.filter(ImageFilter.UnsharpMask(
    radius=1.2,
    percent=120,
    threshold=3
    ))

    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR)

    x = (CANVAS_SIZE - product.width) // 2
    y = (CANVAS_SIZE - product.height) // 2

    if ADD_SHADOW:
        alpha = product.getchannel("A")

        shadow = Image.new("RGBA", product.size, (0, 0, 0, 0))
        shadow.putalpha(alpha)
        shadow = shadow.filter(ImageFilter.GaussianBlur(35))

        shadow_layer = Image.new(
            "RGBA",
            (CANVAS_SIZE, CANVAS_SIZE),
            (0, 0, 0, 0)
        )

        shadow_layer.paste(shadow, (x + 8, y + 12), shadow)

        shadow_alpha = shadow_layer.getchannel("A")
        shadow_alpha = shadow_alpha.point(lambda p: p * 0.25)
        shadow_layer.putalpha(shadow_alpha)

        canvas = Image.alpha_composite(canvas, shadow_layer)

    canvas.paste(product, (x, y), product)
    canvas.convert("RGB").save(output_path, quality=95)