#!/usr/bin/env python3
"""
Generate a Neofetch-style terminal info card as an SVG (info-card.svg).
Features:
- Neofetch shell aesthetic (user@github, separator, key-value fields, color bar).
- Staggered CSS line-by-line fade & slide-in transitions with animation-fill-mode: forwards.
- STATIC=1 environment flag or --static CLI flag for headless testing.
- Dimensions: 490px wide x 390px high (pairs with 370px ASCII art for 860px total).
"""

import argparse
import html
import os
import sys


DEFAULT_FIELDS = [
    ("OS", "Arch Linux x86_64 / Fedora", "#58A6FF"),
    ("Kernel", "Linux 6.12.8 / Node.js 22.x / Py 3.13", "#A5D6FF"),
    ("Uptime", "Always running, rebuilding better", "#7EE787"),
    ("Role", "Full Stack Engineer & AI Agent Architect", "#FFA657"),
    ("Focus", "LangChain, LangGraph, RAG & AI Agents (MCP)", "#D2A8FF"),
    ("Stack", "Python, TypeScript, React, Next.js, FastAPI", "#79C0FF"),
    ("Contact", "ys0609392@gmail.com", "#58A6FF"),
    ("Status", "Active // Breaking & rebuilding", "#7EE787"),
]

COLOR_BLOCKS = [
    "#484F58",  # Black
    "#FF7B72",  # Red
    "#7EE787",  # Green
    "#F2CC60",  # Yellow
    "#58A6FF",  # Blue
    "#BC8CFF",  # Magenta
    "#39C5CF",  # Cyan
    "#B1BAC4",  # White
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Render Neofetch-style SVG info card.")
    parser.add_argument(
        "--output",
        default="info-card.svg",
        help="Output SVG path (default: info-card.svg)"
    )
    parser.add_argument(
        "--user",
        default="yuvraj",
        help="Username for prompt (default: yuvraj)"
    )
    parser.add_argument(
        "--host",
        default="github",
        help="Hostname for prompt (default: github)"
    )
    parser.add_argument(
        "--static",
        action="store_true",
        default=os.getenv("STATIC", "0") in ("1", "true", "True"),
        help="Disable CSS animation for headless testing"
    )
    return parser.parse_args()


def render_info_card_svg(user: str, host: str, is_static: bool = False) -> str:
    width = 490
    height = 390
    prompt_header = f"{user}@{host}"
    separator = "-" * len(prompt_header)

    animation_css = """
      .line-anim {
        opacity: 0;
        transform: translateX(-10px);
        animation: lineFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }
      @keyframes lineFadeIn {
        from {
          opacity: 0;
          transform: translateX(-10px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
    """ if not is_static else ""

    lines_svg = []
    y_start = 72
    line_height = 26
    curr_y = y_start

    # Header line: user@host
    delay_idx = 0
    delay_ms = delay_idx * 50
    style_attr = "" if is_static else f'style="animation-delay: {delay_ms}ms;"'
    class_attr = "" if is_static else 'class="line-anim"'
    lines_svg.append(
        f'  <g {class_attr} {style_attr}>\n'
        f'    <text x="24" y="{curr_y}" class="mono font-bold" font-size="14.5">\n'
        f'      <tspan fill="#58A6FF">{user}</tspan><tspan fill="#8B949E">@</tspan><tspan fill="#7EE787">{host}</tspan>\n'
        f'    </text>\n'
        f'  </g>'
    )
    curr_y += 18
    delay_idx += 1

    # Separator line
    delay_ms = delay_idx * 50
    style_attr = "" if is_static else f'style="animation-delay: {delay_ms}ms;"'
    class_attr = "" if is_static else 'class="line-anim"'
    lines_svg.append(
        f'  <g {class_attr} {style_attr}>\n'
        f'    <text x="24" y="{curr_y}" class="mono" fill="#484F58" font-size="12">{separator}</text>\n'
        f'  </g>'
    )
    curr_y += 24
    delay_idx += 1

    # Key-value fields
    for key, val, val_color in DEFAULT_FIELDS:
        delay_ms = delay_idx * 50
        style_attr = "" if is_static else f'style="animation-delay: {delay_ms}ms;"'
        class_attr = "" if is_static else 'class="line-anim"'
        escaped_key = html.escape(f"{key:8s}")
        escaped_val = html.escape(val)
        lines_svg.append(
            f'  <g {class_attr} {style_attr}>\n'
            f'    <text x="24" y="{curr_y}" class="mono" font-size="12.5">\n'
            f'      <tspan fill="#79C0FF" font-weight="600">{escaped_key}</tspan>\n'
            f'      <tspan fill="#8B949E">: </tspan>\n'
            f'      <tspan fill="{val_color}">{escaped_val}</tspan>\n'
            f'    </text>\n'
            f'  </g>'
        )
        curr_y += line_height
        delay_idx += 1

    # Color Blocks Palette Bar
    curr_y += 12
    delay_ms = delay_idx * 50
    style_attr = "" if is_static else f'style="animation-delay: {delay_ms}ms;"'
    class_attr = "" if is_static else 'class="line-anim"'
    color_rects = []
    block_w = 24
    block_h = 13
    block_x0 = 24
    for i, col in enumerate(COLOR_BLOCKS):
        bx = block_x0 + i * (block_w + 5)
        color_rects.append(
            f'<rect x="{bx}" y="{curr_y}" width="{block_w}" height="{block_h}" rx="2" fill="{col}" />'
        )

    lines_svg.append(
        f'  <g {class_attr} {style_attr}>\n'
        f'    {" ".join(color_rects)}\n'
        f'  </g>'
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Neofetch Terminal Card">
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
    .font-bold {{
      font-weight: 700;
    }}
    .circle-red {{ fill: #FF5F56; }}
    .circle-yellow {{ fill: #FFBD2E; }}
    .circle-green {{ fill: #27C93F; }}
{animation_css}
  </style>

  <!-- Container Window Box -->
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />

  <!-- Terminal Header Bar -->
  <path class="header-bar" d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L {width - 8.5} 0.5 A 8 8 0 0 1 {width - 0.5} 8.5 L {width - 0.5} 30.5 L 0.5 30.5 Z" />
  <line x1="0.5" y1="30.5" x2="{width - 0.5}" y2="30.5" stroke="#30363D" stroke-width="1" />

  <!-- Window Control Buttons -->
  <circle cx="18" cy="15.5" r="4.5" class="circle-red" />
  <circle cx="32" cy="15.5" r="4.5" class="circle-yellow" />
  <circle cx="46" cy="15.5" r="4.5" class="circle-green" />

  <!-- Terminal Title Prompt -->
  <text x="64" y="19" class="mono" font-size="11.5" fill="#8B949E">
    <tspan fill="#58A6FF">{user}@{host}</tspan><tspan fill="#8B949E">:</tspan><tspan fill="#D2A8FF">~</tspan><tspan fill="#8B949E">$ neofetch --terminal-style</tspan>
  </text>

  <!-- Card Lines -->
{chr(10).join(lines_svg)}
</svg>
"""
    return svg.strip() + "\n"


def main():
    args = parse_arguments()
    svg_content = render_info_card_svg(args.user, args.host, is_static=args.static)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[+] Neofetch Info Card rendered: {args.output} ({args.static=})")


if __name__ == "__main__":
    main()
