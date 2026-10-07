#!/usr/bin/env python3
"""
Render an 860px wide terminal-themed vector SVG for about_me.md (about.svg).
Matches the dark-mode GitHub terminal design system:
- Background: #0D1117
- Border: #30363D
- Header: #161B22
- Accent Colors: #58A6FF, #7EE787, #FFA657, #D2A8FF
- Monospace Typography: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
"""

import argparse
import html
import os
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(description="Render 860px wide about-me terminal SVG.")
    parser.add_argument(
        "--output",
        default="about.svg",
        help="Output path for SVG (default: about.svg)"
    )
    parser.add_argument(
        "--user",
        default="yuvraj",
        help="Terminal prompt username (default: yuvraj)"
    )
    return parser.parse_args()


def render_about_svg(user: str = "yuvraj") -> str:
    width = 860
    height = 295

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="About Me Terminal Window">
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
    .quote-box {{
      fill: rgba(110, 118, 129, 0.08);
      stroke: #30363D;
      stroke-width: 1;
    }}
    .circle-red {{ fill: #FF5F56; }}
    .circle-yellow {{ fill: #FFBD2E; }}
    .circle-green {{ fill: #27C93F; }}
  </style>

  <!-- Container Box -->
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />

  <!-- Window Header Bar -->
  <path class="header-bar" d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L {width - 8.5} 0.5 A 8 8 0 0 1 {width - 0.5} 8.5 L {width - 0.5} 30.5 L 0.5 30.5 Z" />
  <line x1="0.5" y1="30.5" x2="{width - 0.5}" y2="30.5" stroke="#30363D" stroke-width="1" />

  <!-- Terminal Window Controls -->
  <circle cx="18" cy="15.5" r="4.5" class="circle-red" />
  <circle cx="32" cy="15.5" r="4.5" class="circle-yellow" />
  <circle cx="46" cy="15.5" r="4.5" class="circle-green" />

  <!-- Terminal Command Prompt -->
  <text x="64" y="19" class="mono" font-size="11.5">
    <tspan fill="#58A6FF">{user}@github</tspan><tspan fill="#8B949E">:</tspan><tspan fill="#D2A8FF">~</tspan><tspan fill="#8B949E">$ </tspan><tspan fill="#C9D1D9">cat ~/about_me.md</tspan>
  </text>
  <rect x="255" y="9.5" width="6" height="12" fill="#7EE787">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>

  <!-- Identity Block -->
  <g transform="translate(26, 60)">
    <!-- Quote Bar -->
    <line x1="0" y1="-12" x2="0" y2="28" stroke="#58A6FF" stroke-width="3" stroke-linecap="round" />
    
    <text x="14" y="3" class="mono" font-size="15" font-weight="700" fill="#F0F6FC">
      Yuvraj Singh Chauhan
    </text>
    <text x="14" y="24" class="mono" font-size="12.5" font-weight="500" fill="#FFA657">
      Full Stack Engineer &amp; AI Engineer
    </text>
  </g>

  <!-- Philosophy Callout Box -->
  <g transform="translate(24, 108)">
    <rect class="quote-box" width="812" height="58" rx="6" />
    <text x="18" y="25" class="mono" font-size="12" fill="#C9D1D9">
      I like taking complex systems apart to understand how they work beneath the abstractions,
    </text>
    <text x="18" y="44" class="mono" font-size="12" fill="#7EE787" font-weight="500">
      then rebuilding them faster, cleaner, and more resilient.
    </text>
  </g>

  <!-- Engineering Focus Section -->
  <g transform="translate(26, 196)">
    <!-- Section Title -->
    <text x="0" y="0" class="mono" font-size="12.5" font-weight="700" fill="#D2A8FF">
      Current Engineering Focus:
    </text>

    <!-- Item 1: Gen-AI & Agents -->
    <g transform="translate(0, 22)">
      <circle cx="5" cy="-4" r="3.5" fill="#7EE787" />
      <text x="18" y="0" class="mono" font-size="12">
        <tspan fill="#F0F6FC" font-weight="600">Generative AI &amp; Autonomous Agent Architectures</tspan>
        <tspan fill="#8B949E"> (</tspan><tspan fill="#79C0FF">LangGraph, LangChain, MCP, RAG</tspan><tspan fill="#8B949E">)</tspan>
      </text>
    </g>

    <!-- Item 2: Backends & Systems -->
    <g transform="translate(0, 46)">
      <circle cx="5" cy="-4" r="3.5" fill="#58A6FF" />
      <text x="18" y="0" class="mono" font-size="12">
        <tspan fill="#F0F6FC" font-weight="600">High-Performance Backends &amp; Distributed Systems</tspan>
        <tspan fill="#8B949E"> (</tspan><tspan fill="#79C0FF">Node.js, FastAPI, WebSockets</tspan><tspan fill="#8B949E">)</tspan>
      </text>
    </g>

    <!-- Item 3: Full-Stack & Systems -->
    <g transform="translate(0, 70)">
      <circle cx="5" cy="-4" r="3.5" fill="#BC8CFF" />
      <text x="18" y="0" class="mono" font-size="12">
        <tspan fill="#F0F6FC" font-weight="600">Full-Stack &amp; Systems Engineering</tspan>
        <tspan fill="#8B949E"> (</tspan><tspan fill="#79C0FF">Next.js, React, PostgreSQL, Docker, Redis</tspan><tspan fill="#8B949E">)</tspan>
      </text>
    </g>
  </g>
</svg>
"""
    return svg.strip() + "\n"


def main():
    args = parse_arguments()
    content = render_about_svg(user=args.user)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] About Me SVG rendered: {args.output} (width: 860px)")


if __name__ == "__main__":
    main()
