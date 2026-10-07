#!/usr/bin/env python3
"""
Render an 860px wide animated SVG contribution heatmap from data/contributions.json.
Features:
- Pure SVG + CSS keyframes with diagonal entry wave animation.
- Terminal-themed styling (#0D1117 background, #30363D borders, monospace typography).
- Interactive/annotated cell metadata and legend.
- Outputs contrib-heatmap.svg in repository root.
"""

import argparse
import datetime
import json
import os
import sys


PALETTE = [
    "#161b22",  # Level 0: zero contributions
    "#0e4429",  # Level 1: low
    "#006d32",  # Level 2: medium-low
    "#26a641",  # Level 3: medium
    "#39d353",  # Level 4: high
    "#69f0a0",  # Level 5: peak
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS = [
    (1, "Mon"),
    (3, "Wed"),
    (5, "Fri")
]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Render animated SVG contribution heatmap.")
    parser.add_argument(
        "--input",
        default="data/contributions.json",
        help="Input JSON path (default: data/contributions.json)"
    )
    parser.add_argument(
        "--output",
        default="contrib-heatmap.svg",
        help="Output SVG path (default: contrib-heatmap.svg)"
    )
    parser.add_argument(
        "--user",
        default="yuvraj",
        help="Username for CLI header prompt (default: yuvraj)"
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Disable animation for headless static export"
    )
    return parser.parse_args()


def get_color_for_day(day_info: dict, max_count: int) -> str:
    level = day_info.get("level", 0)
    count = day_info.get("count", 0)
    if count == 0 or level == 0:
        return PALETTE[0]
    if count >= max(10, int(max_count * 0.8)):
        return PALETTE[5]  # Peak accent
    if level == 4:
        return PALETTE[4]
    if level == 3:
        return PALETTE[3]
    if level == 2:
        return PALETTE[2]
    return PALETTE[1]


def render_svg(data: dict, is_static: bool = False, user: str = "yuvraj") -> str:
    username = user or data.get("username", "yuvraj")
    total = data.get("total_contributions", 0)
    curr_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    record_day = data.get("record_day", {"date": "N/A", "count": 0})
    record_date = record_day.get("date") or "N/A"
    record_count = record_day.get("count", 0)
    days = data.get("days", [])

    # Map days by date
    days_by_date = {d["date"]: d for d in days}
    max_count = max((d.get("count", 0) for d in days), default=1)

    if not days:
        start_date = datetime.date.today() - datetime.timedelta(days=364)
    else:
        start_date = datetime.date.fromisoformat(days[0]["date"])

    # Align start date to previous Sunday if not already Sunday
    # Python weekday(): Monday=0 ... Sunday=6
    days_since_sunday = (start_date.weekday() + 1) % 7
    first_sunday = start_date - datetime.timedelta(days=days_since_sunday)

    # 53 weeks x 7 days grid
    cols = 53
    cell_size = 10.5
    cell_gap = 3.5
    step = cell_size + cell_gap  # 14.0px

    grid_x0 = 56
    grid_y0 = 62

    # Collect month label positions
    month_positions = []
    last_month = None
    curr_date = first_sunday

    for c in range(cols):
        # Check date of first day in week or middle of week
        week_mid_date = curr_date + datetime.timedelta(days=3)
        month_idx = week_mid_date.month - 1
        if month_idx != last_month and c < cols - 1:
            month_positions.append((grid_x0 + c * step, MONTH_NAMES[month_idx]))
            last_month = month_idx
        curr_date += datetime.timedelta(days=7)

    # Build cell elements
    cell_rects = []
    curr_date = first_sunday

    for c in range(cols):
        for r in range(7):
            d_str = curr_date.isoformat()
            day_info = days_by_date.get(d_str, {"count": 0, "level": 0, "date": d_str})
            color = get_color_for_day(day_info, max_count)
            count = day_info.get("count", 0)

            x = grid_x0 + c * step
            y = grid_y0 + r * step

            # Diagonal animation delay
            delay_ms = int((c * 1.0 + r * 2.2) * 16)

            title_text = f"{count} contributions on {d_str}"
            style_attr = "" if is_static else f'style="animation-delay: {delay_ms}ms;"'
            class_name = "" if is_static else "class=\"heat-cell\""

            rect = (
                f'  <rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" '
                f'rx="2" fill="{color}" {class_name} {style_attr}>'
                f'<title>{title_text}</title></rect>'
            )
            cell_rects.append(rect)
            curr_date += datetime.timedelta(days=1)

    # Day labels (Mon, Wed, Fri)
    day_label_elements = []
    for row_idx, label in DAY_LABELS:
        ly = grid_y0 + row_idx * step + 8.5
        day_label_elements.append(
            f'  <text x="{grid_x0 - 12}" y="{ly:.1f}" class="label day-lbl" text-anchor="end">{label}</text>'
        )

    # Month labels
    month_label_elements = []
    for mx, mname in month_positions:
        month_label_elements.append(
            f'  <text x="{mx:.1f}" y="{grid_y0 - 10}" class="label month-lbl">{mname}</text>'
        )

    # Legend swatches
    legend_elements = []
    legend_x0 = 712
    legend_y = 176
    legend_elements.append(f'  <text x="{legend_x0 - 8}" y="{legend_y + 8}" class="label legend-lbl" text-anchor="end">Less</text>')
    for i, col in enumerate(PALETTE[:5]):
        lx = legend_x0 + i * (cell_size + 3)
        legend_elements.append(
            f'  <rect x="{lx:.1f}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{col}" />'
        )
    legend_elements.append(f'  <text x="{legend_x0 + 5 * (cell_size + 3) + 4}" y="{legend_y + 8}" class="label legend-lbl">More</text>')

    animation_css = """
      .heat-cell {
        transform-origin: center;
        opacity: 0;
        animation: waveIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }
      @keyframes waveIn {
        0% {
          opacity: 0;
          transform: scale(0.4);
        }
        70% {
          transform: scale(1.15);
        }
        100% {
          opacity: 1;
          transform: scale(1);
        }
      }
    """ if not is_static else ""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 206" width="860" height="206" role="img" aria-label="GitHub Contributions Heatmap for {username}">
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
    .cmd-prompt {{
      font-size: 11.5px;
      fill: #7EE787;
      font-weight: 600;
    }}
    .cmd-host {{
      fill: #58A6FF;
    }}
    .cmd-text {{
      fill: #C9D1D9;
      font-weight: 400;
    }}
    .label {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
      font-size: 9.5px;
      fill: #7D8590;
    }}
    .month-lbl {{
      font-size: 9.5px;
      fill: #8B949E;
    }}
    .stat-val {{
      font-weight: 700;
      fill: #58A6FF;
    }}
    .stat-lbl {{
      fill: #8B949E;
      font-size: 10px;
    }}
    .stat-sep {{
      fill: #30363D;
    }}
    .circle-red {{ fill: #FF5F56; }}
    .circle-yellow {{ fill: #FFBD2E; }}
    .circle-green {{ fill: #27C93F; }}
{animation_css}
  </style>

  <!-- Container Box -->
  <rect class="bg" x="0.5" y="0.5" width="859" height="205" rx="8" />

  <!-- Window Header Bar -->
  <path class="header-bar" d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L 851.5 0.5 A 8 8 0 0 1 859.5 8.5 L 859.5 30.5 L 0.5 30.5 Z" />
  <line x1="0.5" y1="30.5" x2="859.5" y2="30.5" stroke="#30363D" stroke-width="1" />

  <!-- Terminal Window Controls -->
  <circle cx="18" cy="15.5" r="4.5" class="circle-red" />
  <circle cx="32" cy="15.5" r="4.5" class="circle-yellow" />
  <circle cx="46" cy="15.5" r="4.5" class="circle-green" />

  <!-- Terminal Command Prompt -->
  <text x="64" y="19" class="mono cmd-prompt">
    <tspan class="cmd-host">{username}@github</tspan><tspan fill="#8B949E">:</tspan><tspan fill="#D2A8FF">~</tspan><tspan fill="#8B949E">$ </tspan><tspan class="cmd-text">git log --contributions --year=recent --graph</tspan>
  </text>

  <!-- Month Labels -->
{chr(10).join(month_label_elements)}

  <!-- Day-of-Week Labels -->
{chr(10).join(day_label_elements)}

  <!-- Heatmap Grid Cells -->
  <g class="mono">
{chr(10).join(cell_rects)}
  </g>

  <!-- Bottom Divider Line -->
  <line x1="16" y1="163" x2="844" y2="163" stroke="#21262D" stroke-width="1" />

  <!-- Bottom Stats Metadata -->
  <g class="mono stat-lbl" transform="translate(18, 184)">
    <text x="0" y="0">
      <tspan class="stat-lbl">Contributions (yr): </tspan><tspan class="stat-val">{total}</tspan>
      <tspan class="stat-sep">  │  </tspan>
      <tspan class="stat-lbl">Streak: </tspan><tspan class="stat-val">{curr_streak}d</tspan>
      <tspan class="stat-sep">  │  </tspan>
      <tspan class="stat-lbl">Longest: </tspan><tspan class="stat-val">{longest_streak}d</tspan>
      <tspan class="stat-sep">  │  </tspan>
      <tspan class="stat-lbl">Peak: </tspan><tspan class="stat-val">{record_count} ({record_date})</tspan>
    </text>
  </g>

  <!-- Legend -->
{chr(10).join(legend_elements)}
</svg>
"""
    return svg.strip() + "\n"


def main():
    args = parse_arguments()
    if not os.path.exists(args.input):
        print(f"[-] Input file not found: {args.input}. Run scripts/fetch_contributions.py first.")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    svg_content = render_svg(data, is_static=args.static, user=args.user)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[+] Heatmap SVG rendered successfully: {args.output} (width: 860px)")


if __name__ == "__main__":
    main()
