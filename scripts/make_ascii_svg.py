#!/usr/bin/env python3
"""
Generate an animated monochrome ASCII portrait as an SVG (avi-ascii.svg).
Features:
- Downsamples data/source-prepped.png to ~100 cols x 53 rows.
- Maps luminance to density ramp: " .`:-=+*cs#%@".
- Styles with monochrome light-gray (#C9D1D9) on dark background (#0D1117).
- SMIL-based left-to-right wipe animations per line with block cursor indicators.
- Sized to 370px wide x 390px high (pairs with 490px info-card.svg for 860px total).
"""

import argparse
import html
import os
import sys
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate animated ASCII SVG from prepped photo.")
    parser.add_argument(
        "--input",
        default="data/source-prepped.png",
        help="Input image path (default: data/source-prepped.png)"
    )
    parser.add_argument(
        "--output",
        default="avi-ascii.svg",
        help="Output SVG path (default: avi-ascii.svg)"
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=96,
        help="Number of character columns (default: 96)"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=53,
        help="Number of character rows (default: 53)"
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert luminance mapping"
    )
    parser.add_argument(
        "--static",
        action="store_true",
        default=os.getenv("STATIC", "0") in ("1", "true", "True"),
        help="Disable SMIL animations"
    )
    return parser.parse_args()


def image_to_ascii(image_path: str, cols: int, rows: int, invert: bool = False):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")

    img = Image.open(image_path).convert("L")
    resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    arr = np.array(resized)

    ascii_lines = []
    ramp_len = len(RAMP)

    for row in arr:
        chars = []
        for val in row:
            # val is 0 (black) to 255 (white).
            # Background was composited as pure white (255).
            # To make white background empty space ' ', we map (255 - val)
            if invert:
                norm = val / 255.0
            else:
                norm = (255.0 - val) / 255.0

            idx = int(round(norm * (ramp_len - 1)))
            idx = max(0, min(ramp_len - 1, idx))
            chars.append(RAMP[idx])
        ascii_lines.append("".join(chars))

    return ascii_lines


def render_ascii_svg(lines: list, is_static: bool = False) -> str:
    width = 370
    height = 390
    header_h = 31

    num_rows = len(lines)
    num_cols = len(lines[0]) if lines else 96

    # Available character canvas: x: 14 to 356 (w: 342), y: 38 to 380 (h: 342)
    start_x = 14.0
    start_y = 41.0
    char_w = 3.55
    char_h = 6.42
    font_size = 5.95

    defs = []
    text_elements = []
    cursor_elements = []

    # Animation timing: cascade across 53 lines in ~1.2s total
    total_anim_dur = 1.3
    wipe_dur = 0.22
    step_delay = (total_anim_dur - wipe_dur) / max(1, num_rows - 1)

    for i, line in enumerate(lines):
        y = start_y + i * char_h
        escaped_line = html.escape(line)
        line_w = num_cols * char_w

        if is_static:
            text_elements.append(
                f'  <text x="{start_x:.1f}" y="{y:.1f}" class="ascii-font">{escaped_line}</text>'
            )
        else:
            clip_id = f"w_{i}"
            begin_sec = round(0.08 + i * step_delay, 3)

            # SMIL clipPath wipe
            defs.append(
                f'    <clipPath id="{clip_id}">\n'
                f'      <rect x="{start_x:.1f}" y="{y - font_size + 0.8:.1f}" width="0" height="{char_h + 1:.1f}">\n'
                f'        <animate attributeName="width" from="0" to="{line_w:.1f}" '
                f'begin="{begin_sec}s" dur="{wipe_dur}s" fill="freeze" calcMode="linear" />\n'
                f'      </rect>\n'
                f'    </clipPath>'
            )

            # Text with clip-path
            text_elements.append(
                f'  <g clip-path="url(#{clip_id})">\n'
                f'    <text x="{start_x:.1f}" y="{y:.1f}" class="ascii-font">{escaped_line}</text>\n'
                f'  </g>'
            )

            # Block cursor trailing the wipe
            cursor_elements.append(
                f'  <rect x="{start_x:.1f}" y="{y - font_size + 0.8:.1f}" width="4" height="{char_h - 0.5:.1f}" fill="#7EE787" opacity="0">\n'
                f'    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.92;1" '
                f'begin="{begin_sec}s" dur="{wipe_dur}s" fill="freeze" />\n'
                f'    <animate attributeName="x" from="{start_x:.1f}" to="{start_x + line_w:.1f}" '
                f'begin="{begin_sec}s" dur="{wipe_dur}s" fill="freeze" />\n'
                f'  </rect>'
            )

    defs_svg = ""
    if defs:
        defs_svg = "  <defs>\n" + "\n".join(defs) + "\n  </defs>\n"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="ASCII Art Portrait">
  <style>
    .mono {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    }}
    .bg {{
      fill: #0D1117;
      stroke: #30363D;
      stroke-width: 1;
    }}
    .header-bar {{
      fill: #161B22;
    }}
    .ascii-font {{
      font-family: "SF Mono", Menlo, Consolas, "Liberation Mono", Courier, monospace;
      font-size: {font_size}px;
      font-weight: 500;
      fill: #C9D1D9;
      white-space: pre;
      letter-spacing: -0.05px;
    }}
    .circle-red {{ fill: #FF5F56; }}
    .circle-yellow {{ fill: #FFBD2E; }}
    .circle-green {{ fill: #27C93F; }}
  </style>

{defs_svg}
  <!-- Container Box -->
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />

  <!-- Terminal Header Bar -->
  <path class="header-bar" d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L {width - 8.5} 0.5 A 8 8 0 0 1 {width - 0.5} 8.5 L {width - 0.5} 30.5 L 0.5 30.5 Z" />
  <line x1="0.5" y1="30.5" x2="{width - 0.5}" y2="30.5" stroke="#30363D" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="18" cy="15.5" r="4.5" class="circle-red" />
  <circle cx="32" cy="15.5" r="4.5" class="circle-yellow" />
  <circle cx="46" cy="15.5" r="4.5" class="circle-green" />

  <!-- Terminal Header Prompt -->
  <text x="64" y="19" class="mono" font-size="11.5">
    <tspan fill="#58A6FF">yuvraj@github</tspan><tspan fill="#8B949E">:</tspan><tspan fill="#D2A8FF">~</tspan><tspan fill="#8B949E">$ </tspan><tspan fill="#C9D1D9">cat avi.ascii</tspan>
  </text>

  <!-- Blinking Cursor in Header -->
  <rect x="238" y="9.5" width="6" height="12" fill="#7EE787">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>

  <!-- ASCII Portrait Content -->
{chr(10).join(text_elements)}

  <!-- Trailing Block Cursor Indicators -->
{chr(10).join(cursor_elements)}
</svg>
"""
    return svg.strip() + "\n"


def main():
    args = parse_arguments()
    lines = image_to_ascii(args.input, args.cols, args.rows, invert=args.invert)
    svg_content = render_ascii_svg(lines, is_static=args.static)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[+] ASCII SVG generated: {args.output} ({args.cols}x{args.rows}, static={args.static})")


if __name__ == "__main__":
    main()
