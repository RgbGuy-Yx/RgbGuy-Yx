#!/usr/bin/env python3
"""
Render an 860px wide terminal-themed vector skills matrix SVG (skills.svg).
Matches the dark-mode GitHub terminal design system:
- Background: #0D1117
- Border: #30363D
- Header: #161B22
- Category Tags: #58A6FF
- Separators & Brackets: #8B949E
- Items: #C9D1D9
- Fonts: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace

Dataset: Exactly synchronized with resume / tech stack specification:
- Programming Languages
- Generative AI
- Frameworks & Libraries
- Databases
- Tools & Platforms
- Soft Skills
"""

import argparse
import html
import os
import sys

CATEGORIES = [
    {
        "name": "Programming Languages",
        "skills": [
            "C", "Java", "Python", "JavaScript", "TypeScript", "SQL"
        ],
    },
    {
        "name": "Generative AI",
        "skills": [
            "LangChain", "LangGraph", "RAG", "AI Agents", "MCP",
            "Prompt Engineering", "Embedding Models", "Semantic Search"
        ],
    },
    {
        "name": "Frameworks & Libraries",
        "skills": [
            "React", "Next.js", "Node.js", "Express", "FastAPI",
            "Tailwind CSS", "WebSockets"
        ],
    },
    {
        "name": "Databases",
        "skills": [
            "MongoDB", "Redis", "Supabase", "PostgreSQL", "Pinecone", "ChromaDB"
        ],
    },
    {
        "name": "Tools & Platforms",
        "skills": [
            "Git", "GitHub", "Docker", "Postman", "CI/CD", "GitHub Actions"
        ],
    },
    {
        "name": "Soft Skills",
        "skills": [
            "Communication", "Leadership", "Problem Solving", "Decision Making", "Adaptability"
        ],
    },
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Render 860px wide SVG skills matrix.")
    parser.add_argument(
        "--output",
        default="skills.svg",
        help="Output path for SVG (default: skills.svg)"
    )
    parser.add_argument(
        "--user",
        default="yuvraj",
        help="Username for terminal prompt (default: yuvraj)"
    )
    return parser.parse_args()


def render_skills_svg(user: str = "yuvraj") -> str:
    width = 860
    indent_x = 220
    max_x = 836
    pill_h = 23
    line_h = 28
    cat_spacing = 10
    start_y = 50

    curr_y = start_y
    category_svgs = []

    for cat in CATEGORIES:
        cat_name = cat["name"]
        escaped_cat_name = html.escape(cat_name)

        # Plan lines of pills with auto-wrap
        line_items = [[]]
        curr_line_x = indent_x

        for skill in cat["skills"]:
            tag_w = round(len(skill) * 7.2 + 16, 1)
            if curr_line_x + tag_w > max_x and line_items[-1]:
                line_items.append([])
                curr_line_x = indent_x
            line_items[-1].append((skill, tag_w))
            curr_line_x += tag_w + 6

        cat_start_y = curr_y

        # Render Category Label (Left aligned at x=24)
        cat_label_y = cat_start_y + 16
        cat_elem = (
            f'  <!-- [{escaped_cat_name}] -->\n'
            f'  <text x="24" y="{cat_label_y:.1f}" class="mono cat-label">\n'
            f'    <tspan fill="#8B949E">[</tspan><tspan fill="#58A6FF">{escaped_cat_name}</tspan><tspan fill="#8B949E">]</tspan>\n'
            f'  </text>'
        )

        # Render Pills for each wrapped line
        pills_svg = []
        for line_idx, line in enumerate(line_items):
            y_pos = cat_start_y + line_idx * line_h
            line_x = indent_x
            for skill, tag_w in line:
                escaped_skill = html.escape(skill)
                pills_svg.append(
                    f'    <g transform="translate({line_x:.1f}, {y_pos:.1f})" class="skill-pill">\n'
                    f'      <rect width="{tag_w:.1f}" height="{pill_h}" rx="4" class="pill-bg" />\n'
                    f'      <text x="{tag_w / 2.0:.1f}" y="15" text-anchor="middle" class="mono skill-text">{escaped_skill}</text>\n'
                    f'    </g>'
                )
                line_x += tag_w + 6

        category_svgs.append(
            cat_elem + "\n" + "\n".join(pills_svg)
        )

        # Advance curr_y
        curr_y += len(line_items) * line_h + cat_spacing

    total_height = int(curr_y + 12)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}" width="{width}" height="{total_height}" role="img" aria-label="Technical Skills Matrix">
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
    .cat-label {{
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 0.2px;
    }}
    .skill-text {{
      font-size: 11px;
      font-weight: 500;
      fill: #C9D1D9;
    }}
    .pill-bg {{
      fill: rgba(110, 118, 129, 0.1);
      stroke: #30363D;
      stroke-width: 1;
      transition: all 0.15s ease;
    }}
    .skill-pill:hover .pill-bg {{
      fill: rgba(56, 139, 253, 0.15);
      stroke: #58A6FF;
    }}
    .skill-pill:hover .skill-text {{
      fill: #58A6FF;
    }}
    .circle-red {{ fill: #FF5F56; }}
    .circle-yellow {{ fill: #FFBD2E; }}
    .circle-green {{ fill: #27C93F; }}
  </style>

  <!-- Container Box -->
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{total_height - 1}" rx="8" />

  <!-- Terminal Header Bar -->
  <path class="header-bar" d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L {width - 8.5} 0.5 A 8 8 0 0 1 {width - 0.5} 8.5 L {width - 0.5} 30.5 L 0.5 30.5 Z" />
  <line x1="0.5" y1="30.5" x2="{width - 0.5}" y2="30.5" stroke="#30363D" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="18" cy="15.5" r="4.5" class="circle-red" />
  <circle cx="32" cy="15.5" r="4.5" class="circle-yellow" />
  <circle cx="46" cy="15.5" r="4.5" class="circle-green" />

  <!-- Command Line Header -->
  <text x="64" y="19" class="mono" font-size="11.5">
    <tspan fill="#58A6FF">{user}@github</tspan><tspan fill="#8B949E">:</tspan><tspan fill="#D2A8FF">~</tspan><tspan fill="#8B949E">$ </tspan><tspan fill="#C9D1D9">cat skills.txt</tspan>
  </text>

  <!-- Categories & Skills Grid -->
{chr(10).join(category_svgs)}
</svg>
"""
    return svg.strip() + "\n"


def main():
    args = parse_arguments()
    content = render_skills_svg(user=args.user)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Skills matrix SVG rendered: {args.output} (width: 860px)")


if __name__ == "__main__":
    main()
