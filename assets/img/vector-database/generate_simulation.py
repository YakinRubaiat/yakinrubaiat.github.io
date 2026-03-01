#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Iterable


OUT_DIR = Path(__file__).parent


def fmt(value: float) -> str:
    return f"{value:.2f}"


def write_svg(path: Path, width: int, height: int, body: Iterable[str], title: str) -> None:
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        "  <defs>",
        '    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#f8fbff" />',
        '      <stop offset="100%" stop-color="#edf3ff" />',
        "    </linearGradient>",
        '    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.16"/>',
        "    </filter>",
        "  </defs>",
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#bg)" />',
    ]
    svg.extend(body)
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")


def generate_vector_search_simulation() -> None:
    width, height = 1400, 880
    rng = random.Random(42)
    clusters = [
        {"name": "AI Research", "center": (310, 240), "spread": (70, 55), "count": 42, "color": "#4f46e5"},
        {"name": "Databases", "center": (560, 520), "spread": (85, 65), "count": 46, "color": "#0ea5e9"},
        {"name": "Backend Systems", "center": (360, 620), "spread": (75, 60), "count": 40, "color": "#16a34a"},
        {"name": "Search", "center": (780, 300), "spread": (80, 62), "count": 44, "color": "#f59e0b"},
        {"name": "Product Docs", "center": (980, 580), "spread": (70, 55), "count": 38, "color": "#ef4444"},
    ]

    def rand_points(center_x: float, center_y: float, std_x: float, std_y: float, count: int) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        for _ in range(count):
            x = min(max(rng.gauss(center_x, std_x), 120), 1160)
            y = min(max(rng.gauss(center_y, std_y), 120), 740)
            points.append((x, y))
        return points

    all_points: list[dict[str, object]] = []
    for cluster in clusters:
        points = rand_points(
            cluster["center"][0], cluster["center"][1], cluster["spread"][0], cluster["spread"][1], cluster["count"]
        )
        cluster["points"] = points
        for point in points:
            all_points.append({"point": point, "cluster": cluster["name"], "color": cluster["color"]})

    query = (860, 430)
    nearest = sorted(all_points, key=lambda item: math.dist(item["point"], query))[:7]  # type: ignore[arg-type]

    body: list[str] = [
        '  <rect x="80" y="80" width="1120" height="700" rx="20" fill="none" stroke="#b8c7dd" stroke-width="2"/>',
        '  <text x="100" y="55" font-size="36" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#111827">Semantic Search Simulation</text>',
        '  <text x="100" y="88" font-size="20" font-family="Inter, Arial, sans-serif" fill="#334155">Embedding clusters and nearest-neighbor retrieval for one query vector.</text>',
    ]

    for x in range(100, 1180, 50):
        body.append(f'  <line x1="{x}" y1="100" x2="{x}" y2="760" stroke="#dbe4f3" stroke-width="1" />')
    for y in range(100, 761, 50):
        body.append(f'  <line x1="100" y1="{y}" x2="1180" y2="{y}" stroke="#dbe4f3" stroke-width="1" />')

    for cluster in clusters:
        cx, cy = cluster["center"]
        color = cluster["color"]
        body.append(
            f'  <circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="120" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.45" stroke-width="2" />'
        )
        for px, py in cluster["points"]:
            body.append(f'  <circle cx="{fmt(px)}" cy="{fmt(py)}" r="4.6" fill="{color}" fill-opacity="0.82" />')
        body.append(
            f'  <text x="{fmt(cx - 56)}" y="{fmt(cy - 132)}" font-size="16" font-family="Inter, Arial, sans-serif" font-weight="600" fill="{color}">{cluster["name"]}</text>'
        )

    for index, item in enumerate(nearest):
        px, py = item["point"]  # type: ignore[misc]
        color = item["color"]  # type: ignore[assignment]
        width_line = 3 if index < 3 else 2
        opacity = 0.85 if index < 3 else 0.55
        dash = "" if index < 3 else ' stroke-dasharray="6 6"'
        body.append(
            f'  <line x1="{fmt(query[0])}" y1="{fmt(query[1])}" x2="{fmt(px)}" y2="{fmt(py)}" stroke="{color}" stroke-width="{width_line}" stroke-opacity="{opacity}" stroke-linecap="round"{dash} />'
        )
        body.append(f'  <circle cx="{fmt(px)}" cy="{fmt(py)}" r="7.3" fill="none" stroke="{color}" stroke-width="2.5" />')

    body.extend(
        [
            f'  <circle cx="{fmt(query[0])}" cy="{fmt(query[1])}" r="12" fill="#111827" filter="url(#shadow)" />',
            f'  <circle cx="{fmt(query[0])}" cy="{fmt(query[1])}" r="22" fill="none" stroke="#111827" stroke-opacity="0.25" stroke-width="2"/>',
            f'  <text x="{fmt(query[0] + 20)}" y="{fmt(query[1] + 6)}" font-size="17" font-family="Inter, Arial, sans-serif" fill="#111827" font-weight="600">Query embedding</text>',
        ]
    )

    panel_x, panel_y = 1220, 120
    body.extend(
        [
            f'  <rect x="{panel_x}" y="{panel_y}" width="160" height="420" rx="14" fill="#ffffff" stroke="#c9d6ea" stroke-width="1.5" filter="url(#shadow)" />',
            f'  <text x="{panel_x + 15}" y="{panel_y + 35}" font-size="18" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#0f172a">Pipeline</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 70}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">1. Encode query</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 100}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">2. ANN search</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 130}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">3. Rerank</text>',
            f'  <text x="{panel_x + 15}" y="{panel_y + 160}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">4. Return top-k</text>',
            f'  <line x1="{panel_x + 15}" y1="{panel_y + 184}" x2="{panel_x + 145}" y2="{panel_y + 184}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{panel_x + 15}" y="{panel_y + 212}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="600">Nearest neighbors</text>',
        ]
    )

    rank_y = panel_y + 238
    for index, item in enumerate(nearest[:5], start=1):
        color = item["color"]  # type: ignore[assignment]
        label = item["cluster"]  # type: ignore[assignment]
        point = item["point"]  # type: ignore[assignment]
        score = 1 / (1 + math.dist(point, query))
        body.extend(
            [
                f'  <circle cx="{panel_x + 23}" cy="{rank_y}" r="6" fill="{color}" />',
                f'  <text x="{panel_x + 36}" y="{rank_y + 5}" font-size="12.5" font-family="Inter, Arial, sans-serif" fill="#334155">#{index} {label}</text>',
                f'  <text x="{panel_x + 145}" y="{rank_y + 5}" text-anchor="end" font-size="12" font-family="Inter, Arial, sans-serif" fill="#64748b">sim {score:.3f}</text>',
            ]
        )
        rank_y += 34

    body.append('  <text x="100" y="820" font-size="15" font-family="Inter, Arial, sans-serif" fill="#475569">Generated from Python with deterministic random seed.</text>')
    write_svg(OUT_DIR / "vector-search-simulation.svg", width, height, body, "Vector search simulation")


def generate_cosine_geometry_simulation() -> None:
    width, height = 1200, 700
    ox, oy = 260, 520
    ux, uy = 640, 0
    angle_deg = 34
    vx = 560 * math.cos(math.radians(angle_deg))
    vy = -560 * math.sin(math.radians(angle_deg))

    dot = ux * vx + uy * vy
    u_norm = math.sqrt(ux**2 + uy**2)
    v_norm = math.sqrt(vx**2 + vy**2)
    cos_sim = dot / (u_norm * v_norm)

    body = [
        '  <text x="70" y="72" font-size="34" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#111827">Cosine Similarity Geometry</text>',
        '  <text x="70" y="104" font-size="19" font-family="Inter, Arial, sans-serif" fill="#334155">Similarity is based on angle, not just length.</text>',
        f'  <rect x="50" y="130" width="780" height="500" rx="18" fill="#ffffff" stroke="#cad7ea" stroke-width="1.6" filter="url(#shadow)" />',
        f'  <line x1="{ox}" y1="{oy}" x2="{ox + 650}" y2="{oy}" stroke="#c6d3e7" stroke-width="2" />',
        f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - 410}" stroke="#c6d3e7" stroke-width="2" />',
        f'  <line x1="{ox}" y1="{oy}" x2="{fmt(ox + ux)}" y2="{fmt(oy + uy)}" stroke="#0ea5e9" stroke-width="7" stroke-linecap="round" />',
        f'  <line x1="{ox}" y1="{oy}" x2="{fmt(ox + vx)}" y2="{fmt(oy + vy)}" stroke="#f97316" stroke-width="7" stroke-linecap="round" />',
        f'  <path d="M {ox + 90} {oy} A 90 90 0 0 0 {fmt(ox + 90 * math.cos(math.radians(angle_deg)))} {fmt(oy - 90 * math.sin(math.radians(angle_deg)))}" fill="none" stroke="#111827" stroke-width="2.2" />',
        f'  <text x="{ox + ux - 30}" y="{oy + 35}" font-size="22" font-family="Inter, Arial, sans-serif" fill="#0ea5e9" font-weight="700">u</text>',
        f'  <text x="{fmt(ox + vx + 18)}" y="{fmt(oy + vy - 14)}" font-size="22" font-family="Inter, Arial, sans-serif" fill="#f97316" font-weight="700">v</text>',
        f'  <text x="{ox + 108}" y="{oy - 27}" font-size="20" font-family="Inter, Arial, sans-serif" fill="#111827">θ = {angle_deg}°</text>',
        '  <text x="870" y="200" font-size="22" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#0f172a">Formula</text>',
        '  <text x="870" y="245" font-size="20" font-family="Inter, Arial, sans-serif" fill="#334155">cos(u, v) = (u · v) / (||u|| ||v||)</text>',
        '  <text x="870" y="315" font-size="22" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#0f172a">This example</text>',
        f'  <text x="870" y="352" font-size="18" font-family="Inter, Arial, sans-serif" fill="#334155">angle = {angle_deg}°</text>',
        f'  <text x="870" y="382" font-size="18" font-family="Inter, Arial, sans-serif" fill="#334155">cos(θ) = {cos_sim:.3f}</text>',
        '  <text x="870" y="426" font-size="17" font-family="Inter, Arial, sans-serif" fill="#475569">Smaller angle means higher semantic similarity.</text>',
        '  <text x="70" y="664" font-size="15" font-family="Inter, Arial, sans-serif" fill="#475569">For normalized embeddings, cosine similarity and dot product are equivalent.</text>',
    ]
    write_svg(OUT_DIR / "cosine-geometry-simulation.svg", width, height, body, "Cosine similarity geometry")


def generate_hnsw_simulation() -> None:
    width, height = 1400, 900
    rng = random.Random(9)
    layers = [
        {"name": "Layer 3 (sparse routing)", "y": 170, "count": 8, "color": "#7c3aed"},
        {"name": "Layer 2", "y": 340, "count": 14, "color": "#2563eb"},
        {"name": "Layer 1", "y": 520, "count": 22, "color": "#0891b2"},
        {"name": "Layer 0 (full graph)", "y": 710, "count": 34, "color": "#0f766e"},
    ]

    body: list[str] = [
        '  <text x="70" y="70" font-size="34" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#111827">HNSW Search Simulation</text>',
        '  <text x="70" y="102" font-size="19" font-family="Inter, Arial, sans-serif" fill="#334155">Top-down greedy routing, then candidate refinement in Layer 0.</text>',
    ]

    for layer in layers:
        y = layer["y"]
        color = layer["color"]
        body.extend(
            [
                f'  <rect x="70" y="{y - 56}" width="1120" height="112" rx="15" fill="#ffffff" stroke="#d2ddee" stroke-width="1.5" />',
                f'  <text x="90" y="{y - 20}" font-size="18" font-family="Inter, Arial, sans-serif" fill="{color}" font-weight="700">{layer["name"]}</text>',
            ]
        )

    layer_nodes: list[list[tuple[float, float]]] = []
    for layer in layers:
        y = layer["y"]
        count = layer["count"]
        xs = sorted(rng.uniform(150, 1130) for _ in range(count))
        nodes = [(x, y + rng.uniform(-22, 22)) for x in xs]
        layer_nodes.append(nodes)

    for layer_idx, nodes in enumerate(layer_nodes):
        color = layers[layer_idx]["color"]
        for i in range(len(nodes) - 1):
            if i % 2 == 0:
                x1, y1 = nodes[i]
                x2, y2 = nodes[i + 1]
                body.append(
                    f'  <line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{color}" stroke-opacity="0.25" stroke-width="1.6"/>'
                )
        for x, y in nodes:
            body.append(f'  <circle cx="{fmt(x)}" cy="{fmt(y)}" r="6.2" fill="{color}" fill-opacity="0.85" />')

    path_indices = [1, 4, 10, 18]
    path_points = [layer_nodes[i][path_indices[i]] for i in range(4)]
    for i in range(3):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i + 1]
        body.append(
            f'  <line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="#111827" stroke-width="3.6" stroke-linecap="round"/>'
        )

    for x, y in path_points:
        body.append(f'  <circle cx="{fmt(x)}" cy="{fmt(y)}" r="10.5" fill="none" stroke="#111827" stroke-width="2.6" />')

    query_x, query_y = 1240, 710
    body.extend(
        [
            f'  <circle cx="{query_x}" cy="{query_y}" r="12" fill="#dc2626" filter="url(#shadow)" />',
            f'  <text x="{query_x + 18}" y="{query_y + 6}" font-size="18" font-family="Inter, Arial, sans-serif" fill="#7f1d1d" font-weight="700">Query</text>',
        ]
    )

    candidates = sorted(layer_nodes[-1], key=lambda p: abs(p[0] - query_x))[:8]
    for x, y in candidates:
        body.append(
            f'  <line x1="{query_x}" y1="{query_y}" x2="{fmt(x)}" y2="{fmt(y)}" stroke="#dc2626" stroke-opacity="0.45" stroke-width="2" stroke-dasharray="6 6"/>'
        )
        body.append(f'  <circle cx="{fmt(x)}" cy="{fmt(y)}" r="9" fill="none" stroke="#dc2626" stroke-width="2"/>')

    panel_x, panel_y = 1210, 170
    body.extend(
        [
            f'  <rect x="{panel_x}" y="{panel_y}" width="170" height="390" rx="14" fill="#ffffff" stroke="#cbd7ea" stroke-width="1.5" filter="url(#shadow)" />',
            f'  <text x="{panel_x + 14}" y="{panel_y + 34}" font-size="18" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#0f172a">HNSW steps</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 72}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">1. Enter top layer</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 102}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">2. Greedy descent</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 132}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">3. Reach Layer 0</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 162}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">4. Explore candidates</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 192}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">5. Return top-k</text>',
            f'  <line x1="{panel_x + 14}" y1="{panel_y + 214}" x2="{panel_x + 156}" y2="{panel_y + 214}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{panel_x + 14}" y="{panel_y + 246}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#475569">Main knobs</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 274}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#334155">M</text>',
            f'  <text x="{panel_x + 64}" y="{panel_y + 274}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#334155">graph degree</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 300}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#334155">efConstruction</text>',
            f'  <text x="{panel_x + 14}" y="{panel_y + 326}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#334155">efSearch</text>',
        ]
    )
    write_svg(OUT_DIR / "hnsw-search-simulation.svg", width, height, body, "HNSW layered search simulation")


def generate_ivf_simulation() -> None:
    width, height = 1360, 860
    rng = random.Random(17)
    centroids = [
        (240, 220, "#2563eb"),
        (520, 250, "#7c3aed"),
        (840, 240, "#0ea5e9"),
        (280, 520, "#16a34a"),
        (600, 560, "#f59e0b"),
        (920, 540, "#ef4444"),
    ]
    selected = {2, 4}
    query = (1030, 350)

    body = [
        '  <text x="70" y="72" font-size="34" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#111827">IVF Probe Simulation</text>',
        '  <text x="70" y="104" font-size="19" font-family="Inter, Arial, sans-serif" fill="#334155">Coarse centroid routing with selective nprobe cluster search.</text>',
        '  <rect x="60" y="130" width="980" height="660" rx="20" fill="#ffffff" stroke="#ccd9ec" stroke-width="1.5" />',
    ]

    for idx, (cx, cy, color) in enumerate(centroids):
        radius = 130
        is_selected = idx in selected
        stroke_width = 3.8 if is_selected else 2
        opacity = 0.2 if is_selected else 0.12
        stroke = "#111827" if is_selected else color
        body.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{stroke_width}" />'
        )
        body.append(f'  <circle cx="{cx}" cy="{cy}" r="8" fill="{color}" />')
        body.append(
            f'  <text x="{cx - 42}" y="{cy - 144}" font-size="15" font-family="Inter, Arial, sans-serif" fill="{color}" font-weight="700">centroid {idx}</text>'
        )
        for _ in range(32):
            px = min(max(rng.gauss(cx, 48), 90), 1010)
            py = min(max(rng.gauss(cy, 43), 160), 760)
            body.append(f'  <circle cx="{fmt(px)}" cy="{fmt(py)}" r="4.2" fill="{color}" fill-opacity="0.82" />')

    body.extend(
        [
            f'  <circle cx="{query[0]}" cy="{query[1]}" r="11" fill="#111827" filter="url(#shadow)" />',
            f'  <text x="{query[0] + 18}" y="{query[1] + 5}" font-size="17" font-family="Inter, Arial, sans-serif" fill="#111827" font-weight="700">query</text>',
        ]
    )

    for idx in selected:
        cx, cy, _ = centroids[idx]
        body.append(
            f'  <line x1="{query[0]}" y1="{query[1]}" x2="{cx}" y2="{cy}" stroke="#111827" stroke-width="2.6" stroke-linecap="round" />'
        )

    panel_x = 1080
    panel_y = 160
    body.extend(
        [
            f'  <rect x="{panel_x}" y="{panel_y}" width="240" height="560" rx="14" fill="#ffffff" stroke="#c9d6ea" stroke-width="1.6" filter="url(#shadow)" />',
            f'  <text x="{panel_x + 16}" y="{panel_y + 36}" font-size="20" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#0f172a">IVF workflow</text>',
            f'  <text x="{panel_x + 16}" y="{panel_y + 72}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">1. Train nlist centroids</text>',
            f'  <text x="{panel_x + 16}" y="{panel_y + 102}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">2. Assign vectors to lists</text>',
            f'  <text x="{panel_x + 16}" y="{panel_y + 132}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">3. Probe nearest centroids</text>',
            f'  <text x="{panel_x + 16}" y="{panel_y + 162}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">4. Rerank local candidates</text>',
            f'  <line x1="{panel_x + 16}" y1="{panel_y + 188}" x2="{panel_x + 224}" y2="{panel_y + 188}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{panel_x + 16}" y="{panel_y + 220}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">nlist</text>',
            f'  <text x="{panel_x + 80}" y="{panel_y + 220}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">= total clusters</text>',
            f'  <text x="{panel_x + 16}" y="{panel_y + 248}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">nprobe</text>',
            f'  <text x="{panel_x + 80}" y="{panel_y + 248}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">= searched clusters</text>',
            f'  <line x1="{panel_x + 16}" y1="{panel_y + 272}" x2="{panel_x + 224}" y2="{panel_y + 272}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{panel_x + 16}" y="{panel_y + 304}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#475569">Selected clusters in this figure:</text>',
            f'  <text x="{panel_x + 16}" y="{panel_y + 332}" font-size="13" font-family="Inter, Arial, sans-serif" fill="#334155">centroid 2, centroid 4</text>',
        ]
    )
    write_svg(OUT_DIR / "ivf-probe-simulation.svg", width, height, body, "IVF nprobe simulation")


def generate_pq_simulation() -> None:
    width, height = 1400, 840
    body = [
        '  <text x="70" y="72" font-size="34" font-family="Inter, Arial, sans-serif" font-weight="700" fill="#111827">Product Quantization Simulation</text>',
        '  <text x="70" y="104" font-size="19" font-family="Inter, Arial, sans-serif" fill="#334155">Split vector into subspaces, quantize each subspace, store compact codes.</text>',
        '  <rect x="70" y="150" width="1260" height="620" rx="20" fill="#ffffff" stroke="#ccd9ec" stroke-width="1.5" />',
    ]

    left_x, top_y = 120, 220
    segment_width = 85
    gap = 8
    colors = ["#2563eb", "#7c3aed", "#0ea5e9", "#16a34a", "#f59e0b", "#ef4444", "#14b8a6", "#8b5cf6"]
    for i in range(8):
        x = left_x + i * (segment_width + gap)
        body.append(
            f'  <rect x="{x}" y="{top_y}" width="{segment_width}" height="70" rx="8" fill="{colors[i]}" fill-opacity="0.85" />'
        )
        body.append(
            f'  <text x="{x + segment_width/2}" y="{top_y + 42}" text-anchor="middle" font-size="16" font-family="Inter, Arial, sans-serif" fill="#ffffff" font-weight="700">s{i+1}</text>'
        )

    body.extend(
        [
            f'  <text x="{left_x}" y="{top_y - 22}" font-size="18" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">Original vector (example: 768 dims)</text>',
            f'  <text x="{left_x}" y="{top_y + 104}" font-size="15" font-family="Inter, Arial, sans-serif" fill="#475569">Split into m = 8 subspaces, each quantized independently.</text>',
        ]
    )

    codebook_x, codebook_y = 120, 390
    body.append(
        f'  <text x="{codebook_x}" y="{codebook_y - 26}" font-size="18" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">Codebooks (k = 256 centroids each)</text>'
    )
    for row in range(4):
        for col in range(4):
            x = codebook_x + col * 170
            y = codebook_y + row * 78
            idx = row * 4 + col + 1
            body.append(f'  <rect x="{x}" y="{y}" width="150" height="56" rx="8" fill="#f8fbff" stroke="#cbd8ea" stroke-width="1.2" />')
            body.append(
                f'  <text x="{x + 12}" y="{y + 33}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">subspace s{((idx - 1) % 8) + 1} -> c{idx}</text>'
            )

    arrow_y = 575
    body.extend(
        [
            f'  <line x1="760" y1="{arrow_y}" x2="920" y2="{arrow_y}" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>',
            '  <defs>',
            '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
            '      <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155"></path>',
            "    </marker>",
            "  </defs>",
            '  <text x="782" y="550" font-size="15" font-family="Inter, Arial, sans-serif" fill="#334155">store indices</text>',
        ]
    )

    right_x, right_y = 950, 260
    body.extend(
        [
            f'  <rect x="{right_x}" y="{right_y}" width="310" height="410" rx="14" fill="#f8fbff" stroke="#c9d6ea" stroke-width="1.5" filter="url(#shadow)" />',
            f'  <text x="{right_x + 20}" y="{right_y + 36}" font-size="20" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">Compressed code</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 68}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">[12, 201, 7, 44, 99, 3, 221, 56]</text>',
            f'  <line x1="{right_x + 20}" y1="{right_y + 86}" x2="{right_x + 286}" y2="{right_y + 86}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{right_x + 20}" y="{right_y + 122}" font-size="15" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">Memory example</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 152}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">Raw vector: 768 x 4 = 3072 bytes</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 178}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">PQ code: 8 bytes (8 x 1 byte)</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 204}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">Compression: 384x smaller</text>',
            f'  <line x1="{right_x + 20}" y1="{right_y + 228}" x2="{right_x + 286}" y2="{right_y + 228}" stroke="#d8e2f0" stroke-width="1" />',
            f'  <text x="{right_x + 20}" y="{right_y + 262}" font-size="15" font-family="Inter, Arial, sans-serif" fill="#0f172a" font-weight="700">Query-time distance</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 290}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">1. Build lookup table per subspace</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 316}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">2. Read centroid indices</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 342}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">3. Sum lookup distances</text>',
            f'  <text x="{right_x + 20}" y="{right_y + 368}" font-size="14" font-family="Inter, Arial, sans-serif" fill="#334155">4. Rerank top candidates</text>',
        ]
    )
    write_svg(OUT_DIR / "pq-compression-simulation.svg", width, height, body, "Product quantization simulation")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generators = [
        generate_vector_search_simulation,
        generate_cosine_geometry_simulation,
        generate_hnsw_simulation,
        generate_ivf_simulation,
        generate_pq_simulation,
    ]
    for generator in generators:
        generator()
    print("Generated:")
    print("- vector-search-simulation.svg")
    print("- cosine-geometry-simulation.svg")
    print("- hnsw-search-simulation.svg")
    print("- ivf-probe-simulation.svg")
    print("- pq-compression-simulation.svg")


if __name__ == "__main__":
    main()
