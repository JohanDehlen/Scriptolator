from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = PROJECT_ROOT / "src" / "scriptalator" / "resources"
INSTALLER_DIR = PROJECT_ROOT / "installer"
BRANDING_DIR = INSTALLER_DIR / "branding"

LOGO_CANDIDATES = (
    RESOURCES_DIR / "scriptolator.png",
    RESOURCES_DIR / "scriptolator_icon.png",
    PROJECT_ROOT / "Scriptolator Icon.png",
)

WIZARD_SIZE = (492, 942)
SMALL_SIZE = (300, 300)

NAVY = (4, 8, 35)
DEEP_BLUE = (10, 15, 64)
PURPLE = (42, 12, 120)
ELECTRIC_BLUE = (0, 164, 255)
CYAN = (82, 226, 255)
WHITE = (248, 249, 255)
MUTED_WHITE = (218, 224, 245)


def find_logo() -> Path:
    """Return the first available Scriptolator logo."""

    for candidate in LOGO_CANDIDATES:
        if candidate.is_file():
            return candidate

    searched = "\n".join(f"  {path}" for path in LOGO_CANDIDATES)
    raise FileNotFoundError(
        "Could not find the Scriptolator logo.\n\n"
        f"Searched:\n{searched}"
    )


def load_font(
    size: int,
    *,
    bold: bool = False,
    italic: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a polished Windows serif font with fallbacks."""

    windows_fonts = Path(Path.home().drive + r"\Windows\Fonts")

    if bold and italic:
        candidates = (
            windows_fonts / "georgiaz.ttf",
            windows_fonts / "timesbi.ttf",
        )
    elif bold:
        candidates = (
            windows_fonts / "georgiab.ttf",
            windows_fonts / "timesbd.ttf",
        )
    elif italic:
        candidates = (
            windows_fonts / "georgiai.ttf",
            windows_fonts / "timesi.ttf",
        )
    else:
        candidates = (
            windows_fonts / "georgia.ttf",
            windows_fonts / "times.ttf",
        )

    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)

    return ImageFont.load_default()


def load_sans_font(
    size: int,
    *,
    bold: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a readable Windows sans-serif font."""

    windows_fonts = Path(Path.home().drive + r"\Windows\Fonts")
    candidates = (
        windows_fonts / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        windows_fonts / ("arialbd.ttf" if bold else "arial.ttf"),
    )

    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)

    return ImageFont.load_default()


def vertical_gradient(
    size: tuple[int, int],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> Image.Image:
    """Create a vertical RGB gradient."""

    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()

    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(
            round(top[channel] * (1 - ratio) + bottom[channel] * ratio)
            for channel in range(3)
        )
        for x in range(width):
            pixels[x, y] = color

    return image


def draw_glow_line(
    image: Image.Image,
    points: list[tuple[int, int]],
    color: tuple[int, int, int],
    width: int,
) -> None:
    """Draw a softly glowing line."""

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for extra_width, alpha in ((18, 35), (10, 65), (4, 120)):
        glow_draw.line(
            points,
            fill=(*color, alpha),
            width=width + extra_width,
            joint="curve",
        )

    glow = glow.filter(ImageFilter.GaussianBlur(8))
    image.alpha_composite(glow)

    draw = ImageDraw.Draw(image)
    draw.line(
        points,
        fill=(*color, 220),
        width=width,
        joint="curve",
    )


def draw_waveform(
    image: Image.Image,
    *,
    center_y: int,
    left: int,
    right: int,
) -> None:
    """Draw a branded blue-purple waveform."""

    width = right - left
    amplitudes = (
        0, 4, -8, 14, -20, 34, -50, 72, -44, 28,
        -18, 56, -84, 112, -70, 42, -24, 16, -8, 4, 0,
    )
    step = width / (len(amplitudes) - 1)
    points = [
        (round(left + index * step), center_y + amplitude)
        for index, amplitude in enumerate(amplitudes)
    ]

    draw_glow_line(image, points, ELECTRIC_BLUE, width=4)
    mirrored = [(x, center_y - (y - center_y)) for x, y in points]
    draw_glow_line(image, mirrored, (105, 55, 255), width=2)


def contain(image: Image.Image, bounds: tuple[int, int]) -> Image.Image:
    """Scale an image to fit within bounds."""

    copy = image.copy()
    copy.thumbnail(bounds, Image.Resampling.LANCZOS)
    return copy


def centered_x(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    canvas_width: int,
) -> int:
    """Return the x position needed to center text."""

    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return (canvas_width - (right - left)) // 2


def create_wizard_image(logo_path: Path) -> Path:
    """Create the tall Welcome/Finish wizard image."""

    image = vertical_gradient(WIZARD_SIZE, NAVY, (8, 4, 48)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    logo = contain(Image.open(logo_path).convert("RGBA"), (320, 320))
    logo_x = (WIZARD_SIZE[0] - logo.width) // 2
    image.alpha_composite(logo, (logo_x, 52))

    title_font = load_font(66, bold=True, italic=True)
    tagline_font = load_sans_font(28)
    body_font = load_sans_font(25)
    small_font = load_sans_font(21, bold=True)

    title = "Scriptolator"
    draw.text(
        (centered_x(draw, title, title_font, WIZARD_SIZE[0]), 355),
        title,
        font=title_font,
        fill=WHITE,
        stroke_width=1,
        stroke_fill=(140, 160, 255),
    )

    for y, line in ((444, "Transform scripts into"), (481, "professional AI narration")):
        draw.text(
            (centered_x(draw, line, tagline_font, WIZARD_SIZE[0]), y),
            line,
            font=tagline_font,
            fill=CYAN,
        )

    draw_waveform(
        image,
        center_y=650,
        left=55,
        right=WIZARD_SIZE[0] - 55,
    )

    descriptor = "Professional narration for creators"
    draw.text(
        (centered_x(draw, descriptor, body_font, WIZARD_SIZE[0]), 760),
        descriptor,
        font=body_font,
        fill=MUTED_WHITE,
    )

    version = "VERSION 1.0.0"
    draw.text(
        (centered_x(draw, version, small_font, WIZARD_SIZE[0]), 845),
        version,
        font=small_font,
        fill=(160, 175, 230),
    )

    output_path = BRANDING_DIR / "wizard.png"
    image.save(output_path, format="PNG")
    return output_path


def create_small_image(logo_path: Path) -> Path:
    """Create the square wizard header image."""

    image = vertical_gradient(SMALL_SIZE, DEEP_BLUE, PURPLE).convert("RGBA")
    logo = contain(Image.open(logo_path).convert("RGBA"), (260, 260))
    x = (SMALL_SIZE[0] - logo.width) // 2
    y = (SMALL_SIZE[1] - logo.height) // 2
    image.alpha_composite(logo, (x, y))

    output_path = BRANDING_DIR / "wizard_small.png"
    image.save(output_path, format="PNG")
    return output_path


def main() -> int:
    """Generate all installer branding assets."""

    try:
        BRANDING_DIR.mkdir(parents=True, exist_ok=True)
        logo_path = find_logo()
        wizard_path = create_wizard_image(logo_path)
        small_path = create_small_image(logo_path)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1

    print("Installer branding created successfully.")
    print(f"Logo source: {logo_path}")
    print(f"Wizard image: {wizard_path}")
    print(f"Small image: {small_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())