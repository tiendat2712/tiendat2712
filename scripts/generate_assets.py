#!/usr/bin/env python3
"""
Generate and update GitHub profile 3D & visual dynamic assets (100% English):
1. assets/hero-3d.gif            - 3D Animated Hero with App Icon Tiles & 3D Cluster Topology
2. assets/architecture-3d.svg    - Animated 3D Isometric Cloud & App Delivery Pipeline
3. assets/languages-breakdown.svg - 3D-styled Verified Codebase Volume Breakdown (non-fork repos)
4. assets/github-activity.svg     - 3D-styled Verified Live Commit Activity Stream
5. scripts/data/cache.json        - Last valid verified cache for resilient offline fallback
"""

import sys
import os
import json
import math
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
DATA_DIR = os.path.join(SCRIPTS_DIR, "data")
CACHE_FILE = os.path.join(DATA_DIR, "cache.json")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

USERNAME = "tiendat2712"
LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#F7DF1E",
    "CSS": "#563D7C",
    "HTML": "#E34C26",
    "TypeScript": "#3178C6",
    "Tcl": "#E4CC98",
    "Java": "#B07219",
    "C": "#555555",
    "C++": "#F34B7D",
    "Shell": "#89E051",
    "PowerShell": "#012456",
    "Dockerfile": "#384D54",
    "Makefile": "#427819",
    "Others": "#64748B"
}


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Error reading cache file: {e}", file=sys.stderr)
    return None


def save_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Cache successfully saved to {CACHE_FILE}")
    except Exception as e:
        print(f"[WARN] Error saving cache: {e}", file=sys.stderr)


def fetch_github_data(token=None):
    headers = {"User-Agent": "GitHub-Profile-Sync"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"

    def api_get(endpoint):
        req = urllib.request.Request(endpoint, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        print(f"[INFO] Querying GitHub API for user @{USERNAME}...")
        user_info = api_get(f"https://api.github.com/users/{USERNAME}")

        repos = api_get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed")
        public_repos = [r for r in repos if not r.get("fork")]

        total_by_lang = {}
        lang_errors = 0
        for r in public_repos:
            lang_url = r.get("languages_url")
            if lang_url:
                try:
                    langs = api_get(lang_url)
                    for l, b in langs.items():
                        total_by_lang[l] = total_by_lang.get(l, 0) + b
                except Exception as e:
                    lang_errors += 1
                    print(f"[WARN] Failed fetching languages for {r.get('name')}: {e}", file=sys.stderr)

        cached = load_cache() or {}
        if lang_errors > 0 and cached.get("languages"):
            print("[INFO] Rate limit encountered on language endpoints; preserving verified language cache.")
            languages_payload = cached["languages"]
        else:
            total_bytes = sum(total_by_lang.values())
            sorted_langs = sorted(total_by_lang.items(), key=lambda x: x[1], reverse=True)

            breakdown = []
            accumulated_bytes = 0
            for l, b in sorted_langs[:7]:
                pct = (b / total_bytes * 100.0) if total_bytes > 0 else 0
                breakdown.append({
                    "name": l,
                    "bytes": b,
                    "percentage": round(pct, 2),
                    "color": LANG_COLORS.get(l, "#64748B")
                })
                accumulated_bytes += b

            other_bytes = total_bytes - accumulated_bytes
            if other_bytes > 0:
                other_pct = (other_bytes / total_bytes * 100.0) if total_bytes > 0 else 0
                breakdown.append({
                    "name": "Others",
                    "bytes": other_bytes,
                    "percentage": round(other_pct, 2),
                    "color": LANG_COLORS["Others"]
                })
            languages_payload = {
                "total_bytes": total_bytes,
                "breakdown": breakdown
            }

        commits_found = []
        try:
            events = api_get(f"https://api.github.com/users/{USERNAME}/events/public?per_page=50")
            for ev in events:
                if ev.get("type") == "PushEvent":
                    repo_name = ev.get("repo", {}).get("name")
                    created_at = ev.get("created_at", "")[:10]
                    payload = ev.get("payload", {})
                    for c in payload.get("commits", []):
                        commits_found.append({
                            "repo": repo_name,
                            "sha": c.get("sha", "")[:7],
                            "date": created_at,
                            "message": c.get("message", "").splitlines()[0],
                            "url": f"https://github.com/{repo_name}/commit/{c.get('sha')}"
                        })
        except Exception as e:
            print(f"[WARN] Failed fetching public events: {e}", file=sys.stderr)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        payload = {
            "updated_at": now_iso,
            "username": USERNAME,
            "name": user_info.get("name") or "Phan Trinh Tien Dat",
            "public_repos_count": len(public_repos),
            "languages": languages_payload,
            "recent_commits": commits_found[:10] if commits_found else cached.get("recent_commits", [])
        }
        return payload

    except Exception as e:
        print(f"[WARN] GitHub API request failed: {e}. Reverting to verified cache.", file=sys.stderr)
        return None


def generate_architecture_3d_svg():
    """Generate an interactive/animated 3D Isometric App & Cloud Pipeline SVG."""
    W = 960
    H = 340

    stages = [
        {
            "idx": "01",
            "title": "SOURCE & APPS",
            "sub": "Git · Java · Python",
            "cx": 135,
            "cy": 195,
            "top": "#1e3a8a",
            "left": "#172554",
            "right": "#0f172a",
            "accent": "#38bdf8",
            "glow": "#0284c7",
            "icon": "code"
        },
        {
            "idx": "02",
            "title": "CI & SECURITY",
            "sub": "Actions · Docker · Trivy",
            "cx": 310,
            "cy": 160,
            "top": "#1e1b4b",
            "left": "#312e81",
            "right": "#0f172a",
            "accent": "#a855f7",
            "glow": "#7e22ce",
            "icon": "shield"
        },
        {
            "idx": "03",
            "title": "GITOPS SYNC",
            "sub": "Argo CD · Helm Charts",
            "cx": 485,
            "cy": 195,
            "top": "#064e3b",
            "left": "#065f46",
            "right": "#022c22",
            "accent": "#2dd4bf",
            "glow": "#0d9488",
            "icon": "sync"
        },
        {
            "idx": "04",
            "title": "CLOUD RUNTIME",
            "sub": "AWS EKS · Terraform",
            "cx": 660,
            "cy": 160,
            "top": "#0c4a6e",
            "left": "#075985",
            "right": "#082f49",
            "accent": "#38bdf8",
            "glow": "#0ea5e9",
            "icon": "cloud"
        },
        {
            "idx": "05",
            "title": "OBSERVABILITY",
            "sub": "Prometheus · Grafana",
            "cx": 830,
            "cy": 195,
            "top": "#064e3b",
            "left": "#047857",
            "right": "#022c22",
            "accent": "#10b981",
            "glow": "#059669",
            "icon": "pulse"
        }
    ]

    def iso_slab(cx, cy, rx, ry, h, top_col, left_col, right_col, stroke_col):
        # Diamond top: (cx, cy-ry), (cx+rx, cy), (cx, cy+ry), (cx-rx, cy)
        t_pts = f"{cx},{cy-ry} {cx+rx},{cy} {cx},{cy+ry} {cx-rx},{cy}"
        l_pts = f"{cx-rx},{cy} {cx},{cy+ry} {cx},{cy+ry+h} {cx-rx},{cy+h}"
        r_pts = f"{cx},{cy+ry} {cx+rx},{cy} {cx+rx},{cy+h} {cx},{cy+ry+h}"
        s_pts = f"{cx},{cy-ry+h+14} {cx+rx+6},{cy+h+14} {cx},{cy+ry+h+14} {cx-rx-6},{cy+h+14}"
        return f'''
        <polygon points="{s_pts}" fill="#020617" opacity="0.65" filter="url(#blurShadow)" />
        <polygon points="{l_pts}" fill="{left_col}" stroke="{stroke_col}" stroke-width="1" stroke-opacity="0.55" />
        <polygon points="{r_pts}" fill="{right_col}" stroke="{stroke_col}" stroke-width="1" stroke-opacity="0.35" />
        <polygon points="{t_pts}" fill="{top_col}" stroke="{stroke_col}" stroke-width="1.6" />
        '''

    def iso_cube(cx, cy, r, h, accent):
        t_pts = f"{cx},{cy-r*0.58} {cx+r},{cy} {cx},{cy+r*0.58} {cx-r},{cy}"
        l_pts = f"{cx-r},{cy} {cx},{cy+r*0.58} {cx},{cy+r*0.58+h} {cx-r},{cy+h}"
        r_pts = f"{cx},{cy+r*0.58} {cx+r},{cy} {cx+r},{cy+h} {cx},{cy+r*0.58+h}"
        return f'''
        <polygon points="{l_pts}" fill="{accent}" fill-opacity="0.38" stroke="{accent}" stroke-width="1.2" />
        <polygon points="{r_pts}" fill="{accent}" fill-opacity="0.22" stroke="{accent}" stroke-width="1.2" />
        <polygon points="{t_pts}" fill="{accent}" fill-opacity="0.65" stroke="#f8fafc" stroke-width="1.2" />
        '''

    # Background isometric grid lines
    grid_lines = []
    for i in range(-6, 14):
        x1 = i * 90
        y1 = 55
        x2 = x1 + 420
        y2 = 320
        grid_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1e293b" stroke-width="1" opacity="0.45" />')
        x3 = i * 90 + 200
        y3 = 55
        x4 = x3 - 420
        y4 = 320
        grid_lines.append(f'<line x1="{x3}" y1="{y3}" x2="{x4}" y2="{y4}" stroke="#1e293b" stroke-width="1" opacity="0.45" />')

    # Connecting 3D conduits between stages
    conduits_svg = []
    for i in range(len(stages) - 1):
        s1 = stages[i]
        s2 = stages[i + 1]
        x1, y1 = s1["cx"], s1["cy"] - 10
        x2, y2 = s2["cx"], s2["cy"] - 10
        path_id = f"pipe-{i}"
        conduits_svg.append(f'''
        <path d="M {x1} {y1} L {x2} {y2 + 6}" stroke="#020617" stroke-width="8" stroke-linecap="round" opacity="0.6" />
        <path id="{path_id}" d="M {x1} {y1} L {x2} {y2}" stroke="url(#pipeGrad)" stroke-width="3.5" stroke-dasharray="6 4" stroke-linecap="round" />
        <circle r="4.5" fill="{s2['accent']}" filter="url(#glow)">
          <animateMotion dur="{2.2 + i*0.3:.1f}s" repeatCount="indefinite" path="M {x1} {y1} L {x2} {y2}" />
        </circle>
        ''')

    # Render each 3D stage
    nodes_svg = []
    for idx, st in enumerate(stages):
        cx, cy = st["cx"], st["cy"]
        delay = idx * 0.35
        slab = iso_slab(cx, cy, 72, 38, 22, st["top"], st["left"], st["right"], st["accent"])
        cube = iso_cube(cx, cy - 28, 24, 20, st["accent"])
        nodes_svg.append(f'''
        <g class="float-stage" style="animation-delay: {delay:.2f}s">
          {slab}
          {cube}
          <rect x="{cx - 58}" y="{cy + 48}" width="116" height="40" rx="8" fill="#09101f" stroke="{st['accent']}" stroke-width="1" stroke-opacity="0.7" />
          <text x="{cx}" y="{cy + 65}" text-anchor="middle" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" font-size="10.5" font-weight="700">{st['idx']} · {st['title']}</text>
          <text x="{cx}" y="{cy + 80}" text-anchor="middle" fill="#94a3b8" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" font-size="9.5">{st['sub']}</text>
        </g>
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#070c18" />
      <stop offset="50%" stop-color="#0b1326" />
      <stop offset="100%" stop-color="#070c18" />
    </linearGradient>
    <linearGradient id="pipeGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#a855f7" />
      <stop offset="100%" stop-color="#10b981" />
    </linearGradient>
    <filter id="blurShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="6" />
    </filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <clipPath id="boardClip">
      <rect width="{W}" height="{H}" rx="16" />
    </clipPath>
    <style>
      @keyframes floatIso {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-6px); }}
      }}
      .float-stage {{
        animation: floatIso 3.6s ease-in-out infinite;
      }}
    </style>
  </defs>

  <g clip-path="url(#boardClip)">
    <rect width="{W}" height="{H}" rx="16" fill="url(#bgGrad)" stroke="#1e293b" stroke-width="2" />
    <g>{''.join(grid_lines)}</g>

    <!-- Top Header Bar -->
    <rect x="28" y="20" width="904" height="44" rx="10" fill="#0b1324" fill-opacity="0.88" stroke="#1e293b" stroke-width="1" />
    <circle cx="50" cy="42" r="5" fill="#38bdf8" filter="url(#glow)" />
    <text x="64" y="46" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" font-size="13" font-weight="700" letter-spacing="1">3D ISOMETRIC CLOUD &amp; APP DELIVERY TOPOLOGY</text>
    <text x="912" y="46" text-anchor="end" fill="#38bdf8" font-family="'SFMono-Regular',Consolas,monospace" font-size="11" font-weight="600">GITOPS · EKS · OTEL</text>

    <!-- 3D Conduits & Animated Packets -->
    {''.join(conduits_svg)}

    <!-- 3D Isometric Nodes -->
    {''.join(nodes_svg)}
  </g>
</svg>
'''
    target = os.path.join(ASSETS_DIR, "architecture-3d.svg")
    with open(target, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO] Generated {target}")


def generate_languages_svg(data):
    langs = data["languages"]["breakdown"]
    total_bytes = data["languages"]["total_bytes"]
    updated_at = data.get("updated_at", "2026-10-14T19:56:00Z")

    W = 860
    H = 270
    bar_x = 40
    bar_y = 78
    bar_w = 780
    bar_h = 18

    segments_svg = []
    cur_x = bar_x
    for l in langs:
        seg_w = (l["percentage"] / 100.0) * bar_w
        if seg_w > 0.5:
            segments_svg.append(f'<rect x="{cur_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" fill="{l["color"]}" />')
            cur_x += seg_w

    legend_svg = []
    col_w = 195
    row_h = 42
    start_lx = 40
    start_ly = 116

    for idx, l in enumerate(langs):
        c = idx % 4
        r = idx // 4
        lx = start_lx + c * col_w
        ly = start_ly + r * row_h

        b = l["bytes"]
        if b >= 1024 * 1024:
            b_str = f"{b / (1024*1024):.1f} MB"
        elif b >= 1024:
            b_str = f"{b / 1024:.0f} KB"
        else:
            b_str = f"{b} B"

        legend_svg.append(f'''
        <g transform="translate({lx}, {ly})">
          <!-- 3D Beveled App Tile -->
          <rect x="0" y="2" width="182" height="34" rx="8" fill="#050914" />
          <rect x="0" y="0" width="182" height="33" rx="8" fill="#0f172a" stroke="#1e293b" stroke-width="1" />
          <rect x="8" y="8" width="16" height="17" rx="4" fill="{l["color"]}" opacity="0.22" />
          <circle cx="16" cy="16.5" r="5" fill="{l["color"]}" />
          <text x="32" y="15" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="12" font-weight="700">{l["name"]}</text>
          <text x="32" y="28" fill="#94a3b8" font-family="'SFMono-Regular',Consolas,monospace" font-size="10.5">{l["percentage"]:.1f}% · {b_str}</text>
        </g>
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <defs>
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="9" />
    </clipPath>
    <linearGradient id="barGloss" x1="0" y1="{bar_y}" x2="0" y2="{bar_y + bar_h}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.28" />
      <stop offset="45%" stop-color="#ffffff" stop-opacity="0.0" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.35" />
    </linearGradient>
  </defs>

  <!-- 3D Outer Frame -->
  <rect x="2" y="4" width="{W-4}" height="{H-6}" rx="16" fill="#040812" />
  <rect width="{W}" height="{H-4}" rx="16" fill="#0b1120" stroke="#1e293b" stroke-width="1.5" />

  <text x="40" y="42" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="15" font-weight="700" letter-spacing="0.5">3D CODEBASE VOLUME DISTRIBUTION</text>
  <text x="40" y="60" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">Scope: {data.get("public_repos_count", 8)} public non-fork repositories · Total Volume: {total_bytes / (1024*1024):.1f} MB</text>

  <!-- 3D Extruded Progress Cylinder -->
  <rect x="{bar_x}" y="{bar_y + 3}" width="{bar_w}" height="{bar_h}" rx="9" fill="#030712" />
  <g clip-path="url(#bar-clip)">
    {''.join(segments_svg)}
    <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="url(#barGloss)" />
  </g>

  {''.join(legend_svg)}

  <line x1="40" y1="214" x2="820" y2="214" stroke="#1e293b" stroke-width="1" />
  <text x="40" y="234" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10">Methodology: Verified byte volume aggregated via GitHub REST API across @tiendat2712 public repositories (100% forks excluded).</text>
  <text x="40" y="250" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10">Percentages reflect repository file volume ratio (codebase byte weight), not subjective skill ratings · Last synced: {updated_at}</text>
</svg>
'''
    target = os.path.join(ASSETS_DIR, "languages-breakdown.svg")
    with open(target, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO] Generated {target}")


def generate_activity_svg(data):
    commits = data.get("recent_commits", [])[:5]
    updated_at = data.get("updated_at", "2026-10-14T19:56:00Z")

    W = 860
    H = 294
    commit_rows_svg = []
    start_y = 78
    row_h = 36

    for idx, c in enumerate(commits):
        y = start_y + idx * row_h
        msg = c.get("message", "")
        if len(msg) > 52:
            msg = msg[:49] + "..."
        msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        repo = c.get("repo", "").replace("tiendat2712/", "")
        sha = c.get("sha", "")
        date = c.get("date", "")

        commit_rows_svg.append(f'''
        <g transform="translate(40, {y})">
          <!-- 3D Beveled Row Card -->
          <rect x="0" y="3" width="780" height="30" rx="7" fill="#040812" />
          <rect x="0" y="0" width="780" height="29" rx="7" fill="#0f172a" stroke="#1e293b" stroke-width="1" />
          <text x="14" y="19" fill="#64748b" font-family="'SFMono-Regular',Consolas,monospace" font-size="11" font-weight="500">{date}</text>
          <rect x="96" y="4.5" width="132" height="20" rx="5" fill="#1e293b" />
          <text x="162" y="18.5" text-anchor="middle" fill="#38bdf8" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11" font-weight="600">{repo}</text>
          <rect x="236" y="4.5" width="64" height="20" rx="5" fill="#172554" stroke="#1e3a8a" stroke-width="0.8" />
          <text x="268" y="18.5" text-anchor="middle" fill="#7dd3fc" font-family="'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace" font-size="11" font-weight="600">{sha}</text>
          <text x="312" y="18.5" fill="#e2e8f0" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">{msg}</text>
        </g>
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <rect x="2" y="4" width="{W-4}" height="{H-6}" rx="16" fill="#040812" />
  <rect width="{W}" height="{H-4}" rx="16" fill="#0b1120" stroke="#1e293b" stroke-width="1.5" />

  <text x="40" y="42" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="15" font-weight="700" letter-spacing="0.5">VERIFIED GITHUB COMMIT TELEMETRY</text>
  <text x="40" y="60" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">Scope: Live verified commits pushed across @tiendat2712 public repositories</text>

  <g transform="translate(672, 26)">
    <rect x="0" y="2" width="148" height="26" rx="7" fill="#022c22" />
    <rect x="0" y="0" width="148" height="25" rx="7" fill="#064e3b" stroke="#059669" stroke-width="1" />
    <circle cx="15" cy="12.5" r="4" fill="#34d399" />
    <text x="27" y="16.5" fill="#6ee7b7" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11" font-weight="700">LIVE TELEMETRY</text>
  </g>

  {''.join(commit_rows_svg)}

  <line x1="40" y1="264" x2="820" y2="264" stroke="#1e293b" stroke-width="1" />
  <text x="40" y="280" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10">Empirical commit stream synced via GitHub Actions &amp; REST API · Last updated: {updated_at}</text>
</svg>
'''
    target = os.path.join(ASSETS_DIR, "github-activity.svg")
    with open(target, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO] Generated {target}")


def generate_hero_3d():
    SS = 2
    W = 1060 * SS
    H = 350 * SS
    CX = 785 * SS
    CY = 162 * SS
    SCALE = 1.32 * SS
    NUM_FRAMES = 36

    CARD_BG = (10, 16, 31, 255)
    BORDER_COLOR = (30, 48, 77, 255)

    CYAN = (56, 189, 248, 255)
    TEAL = (45, 212, 191, 255)
    EMERALD = (52, 211, 153, 255)
    PURPLE = (168, 85, 247, 255)
    ORANGE = (251, 146, 60, 255)
    BLUE = (59, 130, 246, 255)
    TEXT_WHITE = (248, 250, 252, 255)
    TEXT_MUTED = (160, 175, 200, 255)
    TEXT_DIM = (110, 128, 155, 255)

    LIGHT = np.array([-0.4, -0.5, 0.78])
    LIGHT = LIGHT / np.linalg.norm(LIGHT)

    def get_font(size, bold=False, mono=False):
        s = int(size * SS)
        if mono:
            candidates = [
                "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
            ]
        else:
            candidates = [
                "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, s)
                except Exception:
                    pass
        return ImageFont.load_default()

    FONT_BADGE = get_font(11, bold=True, mono=True)
    FONT_NAME = get_font(28, bold=True)
    FONT_ROLE = get_font(15, bold=True)
    FONT_DESC = get_font(12, bold=False)
    FONT_APP_SYM = get_font(12, bold=True, mono=True)
    FONT_APP_LBL = get_font(9.5, bold=True, mono=True)
    FONT_META = get_font(10.5, bold=False, mono=True)
    FONT_3D = get_font(10.5, bold=True, mono=True)

    def project_3d(x, y, z, rot_z, elevation=0.62):
        cos_z, sin_z = math.cos(rot_z), math.sin(rot_z)
        x1 = x * cos_z - y * sin_z
        y1 = x * sin_z + y * cos_z
        z1 = z
        cos_el, sin_el = math.cos(elevation), math.sin(elevation)
        y2 = y1 * cos_el - z1 * sin_el
        z2 = y1 * sin_el + z1 * cos_el
        dist = 600.0
        factor = dist / (dist + y2 * 0.40)
        screen_x = CX + x1 * SCALE * factor
        screen_y = CY - z2 * SCALE * factor
        return screen_x, screen_y, y2

    def shade_color(base_rgb, normal, light_vec):
        n = np.array(normal, dtype=float)
        norm = np.linalg.norm(n)
        if norm > 1e-6:
            n = n / norm
        dot = max(0.0, float(np.dot(n, light_vec)))
        intensity = 0.30 + 0.70 * dot
        r = int(min(255, max(0, base_rgb[0] * intensity)))
        g = int(min(255, max(0, base_rgb[1] * intensity)))
        b = int(min(255, max(0, base_rgb[2] * intensity)))
        return (r, g, b, 255)

    # 3D App Icon Dock items for the left hero panel
    app_tiles = [
        ("K8S", "Kubernetes", (18, 45, 92), (50, 108, 229), (96, 165, 250)),
        ("DKR", "Docker", (14, 52, 86), (36, 150, 237), (56, 189, 248)),
        ("AWS", "Cloud", (68, 38, 12), (245, 158, 11), (251, 191, 36)),
        ("TF", "Terraform", (46, 22, 78), (139, 92, 246), (192, 132, 252)),
        ("SPR", "Spring 3", (14, 56, 38), (16, 185, 129), (52, 211, 153)),
        ("GHA", "CI/CD", (18, 42, 78), (56, 189, 248), (125, 211, 252)),
    ]

    def draw_3d_app_dock(draw, start_x, start_y, t_ratio):
        tile_w = 66 * SS
        tile_h = 56 * SS
        gap = 12 * SS
        depth = 5 * SS

        for idx, (sym, lbl, bg_dark, border_col, hi_col) in enumerate(app_tiles):
            bob = int(math.sin(t_ratio * 2.0 * math.pi + idx * 0.9) * 2.5 * SS)
            tx = start_x + idx * (tile_w + gap)
            ty = start_y + bob

            # 3D Extruded Bottom Shadow Base
            draw.rounded_rectangle(
                [(tx, ty + depth), (tx + tile_w, ty + tile_h + depth)],
                radius=12 * SS,
                fill=(4, 8, 18, 255),
                outline=(border_col[0] // 2, border_col[1] // 2, border_col[2] // 2, 255),
                width=1 * SS
            )
            # 3D App Tile Face
            draw.rounded_rectangle(
                [(tx, ty), (tx + tile_w, ty + tile_h)],
                radius=12 * SS,
                fill=bg_dark + (255,),
                outline=border_col + (255,),
                width=2 * SS
            )
            # Inner Specular Top Rim
            draw.line(
                [(tx + 10 * SS, ty + 3 * SS), (tx + tile_w - 10 * SS, ty + 3 * SS)],
                fill=(255, 255, 255, 95),
                width=1 * SS
            )
            # Inner 3D Icon Pill Box
            ip_x = tx + 11 * SS
            ip_y = ty + 7 * SS
            ip_w = tile_w - 22 * SS
            ip_h = 22 * SS
            draw.rounded_rectangle(
                [(ip_x, ip_y), (ip_x + ip_w, ip_y + ip_h)],
                radius=6 * SS,
                fill=(border_col[0] // 3, border_col[1] // 3, border_col[2] // 3, 255),
                outline=hi_col + (210,),
                width=1 * SS
            )
            s_bbox = FONT_APP_SYM.getbbox(sym)
            sw = s_bbox[2] - s_bbox[0]
            draw.text((tx + (tile_w - sw) / 2, ip_y + 3 * SS), sym, fill=hi_col + (255,), font=FONT_APP_SYM)

            l_bbox = FONT_APP_LBL.getbbox(lbl)
            lw = l_bbox[2] - l_bbox[0]
            draw.text((tx + (tile_w - lw) / 2, ty + 35 * SS), lbl, fill=TEXT_WHITE, font=FONT_APP_LBL)

    def render_frame_2x(t_idx, total_frames):
        t_ratio = t_idx / float(total_frames)
        rot_angle = t_ratio * 2.0 * math.pi

        img = Image.new("RGBA", (W, H), CARD_BG)
        draw = ImageDraw.Draw(img, "RGBA")

        m = 3 * SS
        draw.rounded_rectangle([(m, m), (W - m, H - m)], radius=18 * SS, fill=CARD_BG, outline=BORDER_COLOR, width=2 * SS)

        # Left Panel
        lx = 44 * SS
        by = 34 * SS
        bw = 250 * SS
        bh = 26 * SS
        # 3D Bevel Pill
        draw.rounded_rectangle([(lx, by + 3 * SS), (lx + bw, by + bh + 3 * SS)], radius=7 * SS, fill=(4, 9, 20, 255))
        draw.rounded_rectangle([(lx, by), (lx + bw, by + bh)], radius=7 * SS, fill=(15, 30, 56, 255), outline=(45, 95, 160, 255), width=1 * SS)
        dot_r = 4 * SS
        draw.ellipse([(lx + 13 * SS - dot_r, by + 13 * SS - dot_r), (lx + 13 * SS + dot_r, by + 13 * SS + dot_r)], fill=(16, 185, 129, 255))
        draw.text((lx + 25 * SS, by + 5 * SS), "3D CLOUD & APP ECOSYSTEM", fill=CYAN, font=FONT_BADGE)

        # 3D Extruded Title
        ny = 72 * SS
        draw.text((lx + 2 * SS, ny + 3 * SS), "PHAN TRINH TIEN DAT", fill=(6, 12, 26, 255), font=FONT_NAME)
        draw.text((lx, ny), "PHAN TRINH TIEN DAT", fill=TEXT_WHITE, font=FONT_NAME)

        ry = 116 * SS
        draw.text((lx, ry), "Backend · Cloud & DevOps Engineer", fill=TEAL, font=FONT_ROLE)

        dy1 = 148 * SS
        dy2 = 168 * SS
        draw.text((lx, dy1), "Visualizing & automating resilient cloud-native platforms,", fill=TEXT_MUTED, font=FONT_DESC)
        draw.text((lx, dy2), "containerized apps, and high-concurrency backend systems.", fill=TEXT_MUTED, font=FONT_DESC)

        # 3D Floating App Icon Tiles
        draw_3d_app_dock(draw, lx, 204 * SS, t_ratio)

        my = 290 * SS
        draw.text((lx, my), "DA NANG, VIETNAM  ·  3D TOPOLOGY ENGINE  ·  LIVE TELEMETRY", fill=TEXT_DIM, font=FONT_META)

        sep_x = 536 * SS
        draw.line([(sep_x, 28 * SS), (sep_x, H - 28 * SS)], fill=(24, 38, 62, 255), width=1 * SS)

        # Right Panel: 3D Perspective Viewport
        cam_rot = rot_angle * 0.25
        grid_half = 4
        grid_step = 26
        grid_z = -48

        for i in range(-grid_half, grid_half + 1):
            dist_factor = 1.0 - (abs(i) / (grid_half + 1.2))
            alpha = int(145 * dist_factor)
            g_col = (32, 58, 95, alpha)
            p1 = project_3d(-grid_half * grid_step, i * grid_step, grid_z, cam_rot)
            p2 = project_3d(grid_half * grid_step, i * grid_step, grid_z, cam_rot)
            draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=g_col, width=1 * SS)
            p3 = project_3d(i * grid_step, -grid_half * grid_step, grid_z, cam_rot)
            p4 = project_3d(i * grid_step, grid_half * grid_step, grid_z, cam_rot)
            draw.line([(p3[0], p3[1]), (p4[0], p4[1])], fill=g_col, width=1 * SS)

        # Outer 3D Orbital Ring
        num_pts = 48
        ring_r = 94.0
        pts_ring = []
        for k in range(num_pts):
            ang = (k / float(num_pts)) * 2.0 * math.pi
            rx = ring_r * math.cos(ang)
            ry = ring_r * math.sin(ang)
            rz = 8.0 * math.sin(ang * 2.0 + rot_angle)
            p = project_3d(rx, ry, rz, cam_rot)
            pts_ring.append(p)

        for k in range(0, num_pts, 2):
            kn = (k + 1) % num_pts
            draw.line([(pts_ring[k][0], pts_ring[k][1]), (pts_ring[kn][0], pts_ring[kn][1])], fill=(45, 92, 150, 185), width=1 * SS)

        center_z = 10.0 + 7.0 * math.sin(rot_angle * 2.0)
        master_size = 38.0
        ms = master_size / 2.0
        m_rot = rot_angle * 1.5
        cos_m, sin_m = math.cos(m_rot), math.sin(m_rot)

        # Projected shadow of master cube on floor grid
        sh_pts = []
        for vx, vy in [(-ms, -ms), (ms, -ms), (ms, ms), (-ms, ms)]:
            rx = vx * cos_m - vy * sin_m
            ry = vx * sin_m + vy * cos_m
            sp = project_3d(rx, ry, grid_z + 1.0, cam_rot)
            sh_pts.append((sp[0], sp[1]))
        draw.polygon(sh_pts, fill=(4, 10, 22, 170))

        raw_m_verts = [
            [-ms, -ms, -ms], [ms, -ms, -ms], [ms, ms, -ms], [-ms, ms, -ms],
            [-ms, -ms,  ms], [ms, -ms,  ms], [ms, ms,  ms], [-ms, ms,  ms]
        ]
        m_world_verts = []
        for vx, vy, vz in raw_m_verts:
            rx = vx * cos_m - vy * sin_m
            ry = vx * sin_m + vy * cos_m
            rz = vz + center_z
            m_world_verts.append((rx, ry, rz))

        pod_radius = 82.0
        pod_size = 19.0
        ps = pod_size / 2.0
        worker_pods = []
        pod_configs = [
            ("K8S", CYAN, (18, 120, 155), (56, 189, 248)),
            ("TF", PURPLE, (130, 36, 210), (192, 132, 252)),
            ("SPR", TEAL, (16, 128, 118), (45, 212, 191)),
            ("AWS", ORANGE, (165, 85, 20), (251, 146, 60)),
            ("DKR", BLUE, (25, 88, 195), (96, 165, 250)),
            ("OBS", EMERALD, (12, 130, 92), (52, 211, 153)),
        ]

        for i in range(len(pod_configs)):
            theta = rot_angle + i * (2.0 * math.pi / len(pod_configs))
            px = pod_radius * math.cos(theta)
            py = pod_radius * math.sin(theta)
            pz = center_z + 13.0 * math.sin(rot_angle * 2.0 + i * 1.2)

            # Floor shadow for each orbiting 3D app cube
            p_sh = []
            for vx, vy in [(-ps, -ps), (ps, -ps), (ps, ps), (-ps, ps)]:
                sp = project_3d(px + vx, py + vy, grid_z + 1.0, cam_rot)
                p_sh.append((sp[0], sp[1]))
            draw.polygon(p_sh, fill=(4, 10, 22, 140))

            raw_p_verts = [
                [-ps, -ps, -ps], [ps, -ps, -ps], [ps, ps, -ps], [-ps, ps, -ps],
                [-ps, -ps,  ps], [ps, -ps,  ps], [ps, ps,  ps], [-ps, ps,  ps]
            ]
            p_world_verts = [(vx + px, vy + py, vz + pz) for vx, vy, vz in raw_p_verts]
            worker_pods.append((px, py, pz, p_world_verts, pod_configs[i]))

        cube_face_indices = [
            ([0, 1, 2, 3], (0, 0, -1)),
            ([4, 5, 6, 7], (0, 0,  1)),
            ([0, 1, 5, 4], (0, -1, 0)),
            ([2, 3, 7, 6], (0,  1, 0)),
            ([0, 3, 7, 4], (-1, 0, 0)),
            ([1, 2, 6, 5], ( 1, 0, 0))
        ]

        render_queue = []
        for idxs, norm in cube_face_indices:
            nx = norm[0] * cos_m - norm[1] * sin_m
            ny = norm[0] * sin_m + norm[1] * cos_m
            nz = norm[2]
            screen_pts = []
            depths = []
            for vi in idxs:
                wx, wy, wz = m_world_verts[vi]
                sx, sy, d = project_3d(wx, wy, wz, cam_rot)
                screen_pts.append((sx, sy))
                depths.append(d)
            avg_d = sum(depths) / len(depths)
            base_col = (24, 78, 142) if norm[2] > 0 else (15, 48, 92)
            face_col = shade_color(base_col, (nx, ny, nz), LIGHT)
            render_queue.append((avg_d, 'face', screen_pts, face_col, (56, 189, 248, 255), 2 * SS))

        for px, py, pz, p_verts, (p_name, border_col, base_col, highlight_col) in worker_pods:
            for idxs, norm in cube_face_indices:
                screen_pts = []
                depths = []
                for vi in idxs:
                    wx, wy, wz = p_verts[vi]
                    sx, sy, d = project_3d(wx, wy, wz, cam_rot)
                    screen_pts.append((sx, sy))
                    depths.append(d)
                avg_d = sum(depths) / len(depths)
                cur_base = [min(255, int(c * 1.32)) for c in base_col] if norm[2] > 0 else base_col
                face_col = shade_color(cur_base, norm, LIGHT)
                render_queue.append((avg_d, 'face', screen_pts, face_col, border_col, 2 * SS))

            c_proj = project_3d(0, 0, center_z, cam_rot)
            p_proj = project_3d(px, py, pz, cam_rot)
            line_depth = (c_proj[2] + p_proj[2]) / 2.0
            render_queue.append((line_depth, 'line', [(c_proj[0], c_proj[1]), (p_proj[0], p_proj[1])], (34, 75, 122, 185), 2 * SS))

            pack_t = (t_ratio * 3.0 + px * 0.03) % 1.0
            pk_x = px * pack_t
            pk_y = py * pack_t
            pk_z = center_z + (pz - center_z) * pack_t
            pk_proj = project_3d(pk_x, pk_y, pk_z, cam_rot)
            render_queue.append((pk_proj[2] + 2.0, 'packet', (pk_proj[0], pk_proj[1]), highlight_col, 4 * SS))

            led_proj = project_3d(px, py - ps, pz, cam_rot)
            render_queue.append((led_proj[2] + 1.0, 'led', (led_proj[0], led_proj[1]), (16, 185, 129, 255), 2 * SS))

        core_proj = project_3d(0, 0, center_z, cam_rot)
        render_queue.append((core_proj[2] + 1.0, 'core', (core_proj[0], core_proj[1]), CYAN, 6 * SS))

        render_queue.sort(key=lambda item: item[0], reverse=True)

        for item in render_queue:
            itype = item[1]
            if itype == 'face':
                pts, f_col, b_col, lw = item[2], item[3], item[4], item[5]
                draw.polygon(pts, fill=f_col, outline=b_col)
                for i_p in range(len(pts)):
                    p_next = pts[(i_p + 1) % len(pts)]
                    draw.line([pts[i_p], p_next], fill=b_col, width=lw)
            elif itype == 'line':
                pts, col, lw = item[2], item[3], item[4]
                draw.line(pts, fill=col, width=lw)
            elif itype == 'packet':
                pos, col, pr = item[2], item[3], item[4]
                draw.ellipse([(pos[0] - pr, pos[1] - pr), (pos[0] + pr, pos[1] + pr)], fill=col)
                draw.ellipse([(pos[0] - pr - 2 * SS, pos[1] - pr - 2 * SS), (pos[0] + pr + 2 * SS, pos[1] + pr + 2 * SS)], outline=(col[0], col[1], col[2], 125), width=1 * SS)
            elif itype == 'led':
                pos, col, lr = item[2], item[3], item[4]
                draw.ellipse([(pos[0] - lr, pos[1] - lr), (pos[0] + lr, pos[1] + lr)], fill=col)
            elif itype == 'core':
                pos, col, cr = item[2], item[3], item[4]
                draw.ellipse([(pos[0] - cr, pos[1] - cr), (pos[0] + cr, pos[1] + cr)], fill=col)
                draw.ellipse([(pos[0] - cr - 3 * SS, pos[1] - cr - 3 * SS), (pos[0] + cr + 3 * SS, pos[1] + cr + 3 * SS)], outline=(255, 255, 255, 190), width=1 * SS)

        hud_y = H - 38 * SS
        draw.text((CX - 108 * SS, hud_y), "3D CLUSTER & APP MESH ENGINE", fill=CYAN, font=FONT_3D)

        target_w = int(W / SS)
        target_h = int(H / SS)
        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    print(f"[INFO] Rendering 3D Hero Animation ({NUM_FRAMES} frames)...")
    frames = []
    for i in range(NUM_FRAMES):
        fr = render_frame_2x(i, NUM_FRAMES)
        fr_p = fr.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        frames.append(fr_p)

    target_gif = os.path.join(ASSETS_DIR, "hero-3d.gif")
    frames[0].save(
        target_gif,
        save_all=True,
        append_images=frames[1:],
        duration=45,
        loop=0,
        optimize=True
    )
    sz_kb = os.path.getsize(target_gif) / 1024.0
    print(f"[INFO] Generated {target_gif} ({sz_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Generate and update profile assets")
    parser.add_argument("--skip-gif", action="store_true", help="Skip rendering 3D hero GIF")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub Personal Access Token")
    args = parser.parse_args()

    data = fetch_github_data(token=args.token)
    if data is not None:
        save_cache(data)
    else:
        print("[INFO] Loading fallback cache from local data...")
        data = load_cache()
        if not data:
            print("[ERROR] No cache available and GitHub fetch failed.", file=sys.stderr)
            sys.exit(1)

    print(f"[INFO] Generating 3D vector SVGs with dataset updated at: {data.get('updated_at')}")
    generate_architecture_3d_svg()
    generate_languages_svg(data)
    generate_activity_svg(data)

    if not args.skip_gif:
        generate_hero_3d()
    else:
        print("[INFO] Skipping 3D GIF generation as requested.")

    print("[SUCCESS] All profile assets generated successfully!")


if __name__ == "__main__":
    main()
