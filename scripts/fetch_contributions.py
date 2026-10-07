#!/usr/bin/env python3
"""
Fetch GitHub contributions calendar data without requiring an API token.
Parses the public HTML endpoint: https://github.com/users/<USERNAME>/contributions
Computes contribution stats: total, current streak, longest streak, record day.
Outputs data/contributions.json.
"""

import argparse
import datetime
import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup


def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape public GitHub contribution calendar.")
    parser.add_argument(
        "--username",
        default=os.getenv("GITHUB_ACTOR", "RgbGuy-Yx"),
        help="GitHub username to scrape (default: RgbGuy-Yx or GITHUB_ACTOR env)"
    )
    parser.add_argument(
        "--output",
        default="data/contributions.json",
        help="Output path for JSON data (default: data/contributions.json)"
    )
    return parser.parse_args()


def fetch_contribution_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def parse_contributions(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # 1. Total count from header
    header_total = None
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        text = heading.get_text(separator=" ", strip=True)
        m = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", text, re.I)
        if m:
            header_total = int(m.group(1).replace(",", ""))
            break

    # Build mapping of tooltips by target ID
    tooltips = {}
    for tip in soup.find_all("tool-tip"):
        target_id = tip.get("for")
        if target_id:
            tooltips[target_id] = tip.get_text(strip=True)

    day_cells = soup.find_all("td", class_="ContributionCalendar-day")
    days_data = []

    for cell in day_cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue

        level_str = cell.get("data-level", "0")
        try:
            level = int(level_str)
        except ValueError:
            level = 0

        cell_id = cell.get("id", "")
        tip_text = tooltips.get(cell_id, "")
        
        # Determine exact count
        count = 0
        if tip_text:
            m = re.search(r"(\d+)\s+contribution", tip_text)
            if m:
                count = int(m.group(1))
            elif "No contribution" in tip_text or "0 contribution" in tip_text:
                count = 0
            else:
                count = 1 if level > 0 else 0
        else:
            count = 1 if level > 0 else 0

        days_data.append({
            "date": date_str,
            "level": level,
            "count": count,
        })

    # Sort chronologically
    days_data.sort(key=lambda d: d["date"])

    # Deduplicate dates if needed
    seen_dates = set()
    deduped_days = []
    for d in days_data:
        if d["date"] not in seen_dates:
            seen_dates.add(d["date"])
            deduped_days.append(d)
    days_data = deduped_days

    # Compute metrics
    total_count = sum(d["count"] for d in days_data)
    if header_total is not None and header_total > total_count:
        total_count = header_total

    # Streaks calculation
    longest_streak = 0
    current_streak = 0
    running_streak = 0
    record_day = {"date": None, "count": 0}

    for d in days_data:
        if d["count"] > record_day["count"]:
            record_day = {"date": d["date"], "count": d["count"]}

        if d["count"] > 0:
            running_streak += 1
            if running_streak > longest_streak:
                longest_streak = running_streak
        else:
            running_streak = 0

    # Calculate current streak ending today or yesterday
    if days_data:
        reversed_days = list(reversed(days_data))
        # If the very latest day is 0, allow looking back 1 day (today might not be over)
        start_idx = 0
        if reversed_days and reversed_days[0]["count"] == 0 and len(reversed_days) > 1:
            if reversed_days[1]["count"] > 0:
                start_idx = 1

        curr = 0
        for i in range(start_idx, len(reversed_days)):
            if reversed_days[i]["count"] > 0:
                curr += 1
            else:
                break
        current_streak = curr

    return {
        "total_contributions": total_count,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "record_day": record_day,
        "days": days_data,
        "start_date": days_data[0]["date"] if days_data else None,
        "end_date": days_data[-1]["date"] if days_data else None,
    }


def main():
    args = parse_arguments()
    print(f"[*] Fetching GitHub contributions for user: '{args.username}'...")
    html = fetch_contribution_html(args.username)
    data = parse_contributions(html)
    data["username"] = args.username
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[+] Contributions saved to {args.output}:")
    print(f"    - Total Contributions: {data['total_contributions']}")
    print(f"    - Current Streak:      {data['current_streak']} days")
    print(f"    - Longest Streak:      {data['longest_streak']} days")
    print(f"    - Record Day:          {data['record_day']['date']} ({data['record_day']['count']} contribs)")
    print(f"    - Days parsed:         {len(data['days'])}")


if __name__ == "__main__":
    main()
