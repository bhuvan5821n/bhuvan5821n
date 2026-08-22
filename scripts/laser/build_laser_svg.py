"""Generate a self-contained, animated 0/1 laser portrait for the README."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parents[2]
# Sampled only for luminance; no raster image is embedded in the resulting SVG.
SOURCE = ROOT / "assets" / "laser" / "bhuvan-binary-laser-portrait.png"
OUTPUT = ROOT / "assets" / "laser" / "bhuvan-laser.svg"
WIDTH, HEIGHT = 840, 540
FRAME_X, FRAME_Y, FRAME_W, FRAME_H = 16, 50, 808, 450
# A larger centered region gives the face, sunglasses, and hand more presence.
PORTRAIT_X, PORTRAIT_W = 75, 690
COLUMNS, ROWS = 128, 80
TOTAL_DURATION, ROW_DURATION = 3.2, 0.11
FONT_SIZE = 8.0
FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace"
TONES = ((172, "#ff5a6e", 1.00), (132, "#ff3b55", .92), (96, "#ff1744", .84), (65, "#b30026", .74), (39, "#7a0018", .64), (22, "#4b0010", .54))


def sample_tone(value: int) -> tuple[str, float, float] | None:
    for threshold, colour, opacity in TONES:
        if value >= threshold:
            return colour, opacity, min(1.0, .40 + value / 205)
    return None


def create_binary_rows() -> list[str]:
    """Map image luminance to visible 0/1 glyphs, with deterministic sparseness."""
    image = Image.open(SOURCE).convert("L")
    image = image.crop((320, 0, 1210, 940))
    # Preserve the already-dark background so isolated source noise stays invisible.
    image = ImageEnhance.Brightness(ImageEnhance.Contrast(image).enhance(1.80)).enhance(1.22)
    image = image.resize((COLUMNS, ROWS), Image.Resampling.LANCZOS)
    pixels, randomizer, result = image.load(), random.Random(5821), []
    row_height = FRAME_H / ROWS

    for y in range(ROWS):
        runs: list[tuple[str, float, str]] = []
        active: tuple[str, float] | None = None
        chars: list[str] = []
        for x in range(COLUMNS):
            tone = sample_tone(pixels[x, y])
            style = (tone[0], tone[1]) if tone and randomizer.random() <= tone[2] else None
            char = ("1" if randomizer.getrandbits(1) else "0") if style else " "
            if style != active:
                if chars:
                    colour, opacity = active if active else ("#0d1117", 0.0)
                    runs.append((colour, opacity, "".join(chars)))
                active, chars = style, [char]
            else:
                chars.append(char)
        if chars:
            colour, opacity = active if active else ("#0d1117", 0.0)
            runs.append((colour, opacity, "".join(chars)))
        glyphs = "".join(f'<tspan fill="{colour}" fill-opacity="{opacity:.2f}">{text}</tspan>' for colour, opacity, text in runs)
        baseline = FRAME_Y + (y + .79) * row_height
        result.append(f'<text x="{PORTRAIT_X}" y="{baseline:.3f}" textLength="{PORTRAIT_W}" lengthAdjust="spacingAndGlyphs" font-family="{FONT}" font-size="{FONT_SIZE}" xml:space="preserve">{glyphs}</text>')
    return result


def laser(index: int, start: float, row_height: float) -> str:
    y = FRAME_Y + (index + .5) * row_height
    return f'''<g class="laser-head" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.86;1" begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="{PORTRAIT_X} {y:.3f}" to="{PORTRAIT_X + PORTRAIT_W} {y:.3f}" begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze"/>
<line x1="-58" x2="-8" stroke="#4b0010" stroke-width="1.5" opacity=".9"/><line x1="-30" x2="-7" stroke="#ff1744" stroke-width="1.65" filter="url(#trail)"/><circle r="10" fill="#ff003c" opacity=".44" filter="url(#laser-glow)"/><circle r="4.4" fill="#ff1744"/><circle r="1.45" fill="#ff5a6e"/><circle cx="-6" cy="-5" r=".75" fill="#ff3b55"/><circle cx="6" cy="4" r=".65" fill="#ff3b55"/><path d="M7 -5l2 -2M-5 6l-2 2" stroke="#ff3b55" stroke-width=".8" stroke-linecap="round"/></g>'''


def build_svg(rows: list[str]) -> str:
    row_height, delay = FRAME_H / ROWS, (TOTAL_DURATION - ROW_DURATION) / (ROWS - 1)
    clips, revealed, lasers = [], [], []
    for index, row in enumerate(rows):
        y, start = FRAME_Y + index * row_height, index * delay
        clips.append(f'<clipPath id="row-{index}" clipPathUnits="userSpaceOnUse"><rect x="{PORTRAIT_X}" y="{y:.3f}" width="0" height="{row_height + .25:.3f}"><animate attributeName="width" from="0" to="{PORTRAIT_W}" begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze"/></rect></clipPath>')
        revealed.append(f'<g clip-path="url(#row-{index})">{row}</g>')
        lasers.append(laser(index, start, row_height))
    final_rows = "".join(rows)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Bhuvan animated binary laser-scan portrait</title><desc id="desc">A portrait of Bhuvan made from binary zero and one characters is drawn row by row by a red laser.</desc>
<defs><linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#12070b"/><stop offset=".55" stop-color="#090306"/><stop offset="1" stop-color="#050203"/></linearGradient><filter id="laser-glow" x="-300%" y="-300%" width="700%" height="700%"><feGaussianBlur stdDeviation="3.4"/></filter><filter id="trail" x="-120%" y="-400%" width="340%" height="900%"><feGaussianBlur stdDeviation="1.3"/></filter>{''.join(clips)}</defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#surface)"/><rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="11.5" fill="none" stroke="#3a0a12"/><path d="M1 34h838" stroke="#3a0a12"/><circle cx="18" cy="17" r="3.4" fill="#ff1744"/><circle cx="30" cy="17" r="3.4" fill="#7a0018"/><circle cx="42" cy="17" r="3.4" fill="#240008"/>
<text x="58" y="21" fill="#7a0018" font-family="{FONT}" font-size="10.5">bhuvan@github: ~/identity-scan</text><text x="791" y="21" fill="#ff3b55" font-family="{FONT}" font-size="11" text-anchor="end">&gt; 01</text><rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="5" fill="#050203" stroke="#3a0a12"/>
{''.join(revealed)}<g opacity="0"><set attributeName="opacity" to="1" begin="{TOTAL_DURATION:.3f}s" fill="freeze"/>{final_rows}</g><rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="5" fill="none" stroke="#3a0a12"/>{''.join(lasers)}
<path d="M16 518h808" stroke="#3a0a12"/><text x="16" y="533" fill="#7a0018" font-family="{FONT}" font-size="10">&gt; binary-render.exe --subject bhuvan --status: COMPLETE</text></svg>'''


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Portrait source not found: {SOURCE}")
    rows = create_binary_rows()
    OUTPUT.write_text(build_svg(rows), encoding="utf-8")
    print(f"source={SOURCE}\ngrid={COLUMNS}x{ROWS}\nrows={ROWS}\nduration={TOTAL_DURATION:.2f}s\nsvg={WIDTH}x{HEIGHT}\noutput={OUTPUT}\nsize={OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
