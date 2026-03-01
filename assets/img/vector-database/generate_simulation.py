#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path


WIDTH = 1400
HEIGHT = 880
OUTPUT_FILE = Path(__file__).with_name("vector-search-simulation.svg")


def fmt(num: float) -> str:
    return f"{num:.2f}"


def distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    return math.dist(point_a, point_b)


def svg_header() -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Vector search simulation">',
        "  <defs>",
        '    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#f8fbff" />',
        '      <stop offset="100%" stop-color="#edf3ff" />',
        "    </linearGradient>",
        '    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.18"/>',
        "    </filter>",
        "  </defs>",
        '  <rect x="0" y="0" width="1400" height="880" fill="url(#bg)" />',
    ]


def grid_lines(step: int = 50) -> list[str]:
    lines = []
    for x in range(100, 1180, step):
        lines.append(
            f'  <line x1="{x}" y1="100" x2="{x}" y2="760" stroke="#dbe4f3" stroke-width="1" />'
        )
    for y in range(100, 761, step):
        lines.append(
            f'  <line x1="100" y1="{y}" x2="1180" y2="{y}" stroke="#dbe4f3" stroke-width="1" />'
        )
    return lines


def generate_points(
    center_x: float,
    center_y: float,
    std_x: float,
    std_y: float,
    count: int,
    rng: random.Random,
) -> list[tuple[float, float]]:
    points = []
    for _ in range(count):
        x = rng.gauss(center_x, std_x)
        y = rng.gauss(center_y, std_y)
        x = min(max(x, 120), 1160)
        y = min(max(y, 120), 740)
        points.append((x, y))
    return points


def main() -> None:
    rng = random.Random(42)
    clusters = [
        {
            "name": "AI Research",
            "center": (310, 240),
            "spread": (70, 55),
            "count": 42,
            "color": "#4f46e5",
        },
        {
            "name": "Databases",
            "center": (560, 520),
            "spread": (85, 65),
            "count": 46,
            "color": "#0ea5e9",
        },
        {
            "name": "Backend Systems",
            "center": (360, 620),
            "spread": (75, 60),
            "count": 40,
            "color": "#16a34a",
        },
        {
            "name": "Search",
            "center": (780, 300),
            "spread": (80, 62),
            "count": 44,
            "color": "#f59e0b",
        },
        {
            "name": "Product Docs",
            "center": (980, 580),
            "spread": (70, 55),
            "count": 38,
            "color": "#ef4444",
        },
    ]

    all_points: list[dict[str, object]] = []
    for cluster in clusters:
        points = generate_points(
            cluster["center"][0],
            cluster["center"][1],
            cluster["spread"][0],
            cluster["spread"][1],
            cluster["count"],
            rng,
        )
        cluster["points"] = points
        for point in points:
            all_points.append({"point": point, "cluster": cluster["name"], "color": cluster["color"]})

    query_point = (860, 430)
    ranked = sorted(
        all_points,
        key=lambda item: distance(item["point"], query_point),  # type: ignore[arg-type]
    )
    nearest = ranked[:7]

    svg = svg_header()
    svg.extend(grid_lines())

    svg.extend(
        [
            '  <rect x="80" y="80" width="1120" height="700" rx="20" fill="none" stroke="#b8c7dd" stroke-width="2"/>',
            '  <text x="100" y="55" font-size="36" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#111827">Vector Search Simulation</text>',
            '  <text x="100" y="88" font-size="20" font-family="Inter, Arial, sans-serif" fill="#334155">Clusters represent semantic neighborhoods in embedding space.</text>',
        ]
    )

    for cluster in clusters:
        center_x, center_y = cluster["center"]
        color = cluster["color"]
        svg.append(
            f'  <circle cx="{fmt(center_x)}" cy="{fmt(center_y)}" r="120" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.45" stroke-width="2" />'
        )
        for point_x, point_y in cluster["points"]:
            svg.append(
                f'  <circle cx="{fmt(point_x)}" cy="{fmt(point_y)}" r="4.6" fill="{color}" fill-opacity="0.82" />'
            )
        svg.append(
            f'  <text x="{fmt(center_x - 55)}" y="{fmt(center_y - 132)}" font-size="16" font-family="Inter, Arial, sans-serif" font-weight="600" fill="{color}">{cluster["name"]}</text>'
        )

    for index, item in enumerate(nearest):
        point_x, point_y = item["point"]  # type: ignore[misc]
        color = item["color"]  # type: ignore[assignment]
        width = 3 if index < 3 else 2
        opacity = 0.85 if index < 3 else 0.55
        dash = "0" if index < 3 else "6 6"
        line_style = (
            f'stroke="{color}" stroke-width="{width}" stroke-opacity="{opacity}" '
            f'stroke-linecap="round"'
        )
        if dash != "0":
            line_style += f' stroke-dasharray="{dash}"'
        svg.append(
            f'  <line x1="{fmt(query_point[0])}" y1="{fmt(query_point[1])}" x2="{fmt(point_x)}" y2="{fmt(point_y)}" {line_style} />'
        )
        svg.append(
            f'  <circle cx="{fmt(point_x)}" cy="{fmt(point_y)}" r="7.3" fill="none" stroke="{color}" stroke-width="2.5" />'
        )

    svg.extend(
        [
            f'  <circle cx="{fmt(query_point[0])}" cy="{fmt(query_point[1])}" r="12" fill="#111827" filter="url(#shadow)" />',
            f'  <circle cx="{fmt(query_point[0])}" cy="{fmt(query_point[1])}" r="22" fill="none" stroke="#111827" stroke-opacity="0.25" stroke-width="2"/>',
            f'  <text x="{fmt(query_point[0] + 20)}" y="{fmt(query_point[1] + 6)}" font-size="17" font-family="Inter, Arial, sans-serif" fill="#111827" font-weight="600">Query embedding</text>',
        ]
    )

    panel_x = 1220
    panel_y = 120
    svg.extend(
        [
            f'  <rect x="{panel_x}" y="{panel_y}" width="160" height="420" rx="14" fill="#ffffff" stroke="#c9d6ea" stroke-width="1.5" filter="url(#shadow)" />',
            f'  <text x="{panel_x + 15}" y="{panel_y + 35}" font-size="18" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#0f172a">Retrieval Steps</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 70}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">1. Embed query</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 100}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">2. ANN candidate search</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 130}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">3. Distance rerank</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 160}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">4. Return top-k</text>',
            f'  <line x1="{panel_x + 15}" y1="{panel_y + 184}" x2="{panel_x + 145}" y2="{panel_y + 184}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{panel_x + 15}" y="{panel_y + 212}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="600">Nearest neighbors</text>',
        ]
    )

    rank_y = panel_y + 238
    for index, item in enumerate(nearest[:5], start=1):
        color = item["color"]  # type: ignore[assignment]
        cluster_name = item["cluster"]  # type: ignore[assignment]
        point = item["point"]  # type: ignore[assignment]
        score = 1 / (1 + distance(point, query_point))
        svg.extend(
            [
                f'  <circle cx="{panel_x + 23}" cy="{rank_y}" r="6" fill="{color}" />',
                f'  <text x="{panel_x + 36}" y="{rank_y + 5}" font-size="12.5" font-family="Inter, Arial, sans-serif" fill="#334155">#{index} {cluster_name}</text>',
                f'  <text x="{panel_x + 145}" y="{rank_y + 5}" text-anchor="end" font-size="12" font-family="Inter, Arial, sans-serif" fill="#64748b">sim {score:.3f}</text>',
            ]
        )
        rank_y += 34

    svg.extend(
        [
            '  <text x="100" y="820" font-size="15" font-family="Inter, Arial, sans-serif" fill="#475569">Generated with Python: semantic clusters + nearest-neighbor lookup visualization.</text>',
            "</svg>",
        ]
    )

    OUTPUT_FILE.write_text("\n".join(svg), encoding="utf-8")
    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
