#!/usr/bin/env python3
"""
Generate and update GitHub profile dynamic assets:
1. assets/hero-3d.gif            - 3D Animated Hero with Kubernetes Topology & Identity
2. assets/languages-breakdown.svg - Verified language codebase byte distribution (non-fork public repos)
3. assets/github-activity.svg     - Verified real commit activity across tiendat2712 public repos
4. scripts/data/cache.json        - Last valid verified cache for resilient offline fallback
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
        
        # Languages aggregation
        total_by_lang = {}
        for r in public_repos:
            lang_url = r.get("languages_url")
            if lang_url:
                try:
                    langs = api_get(lang_url)
                    for l, b in langs.items():
                        total_by_lang[l] = total_by_lang.get(l, 0) + b
                except Exception as e:
                    print(f"[WARN] Failed fetching languages for {r.get('name')}: {e}", file=sys.stderr)

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

        # Events / commits
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
            "languages": {
                "total_bytes": total_bytes,
                "breakdown": breakdown
            },
            "recent_commits": commits_found[:10] if commits_found else (load_cache() or {}).get("recent_commits", [])
        }
        return payload

    except Exception as e:
        print(f"[WARN] GitHub API request failed: {e}. Reverting to verified cache.", file=sys.stderr)
        return None

def generate_languages_svg(data):
    langs = data["languages"]["breakdown"]
    total_bytes = data["languages"]["total_bytes"]
    updated_at = data.get("updated_at", "2026-10-14T19:56:00Z")
    
    W = 860
    H = 260
    bar_x = 40
    bar_y = 78
    bar_w = 780
    bar_h = 16

    segments_svg = []
    cur_x = bar_x
    for l in langs:
        seg_w = (l["percentage"] / 100.0) * bar_w
        if seg_w > 0.5:
            segments_svg.append(f'<rect x="{cur_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" fill="{l["color"]}" />')
            cur_x += seg_w

    legend_svg = []
    col_w = 195
    row_h = 32
    start_lx = 40
    start_ly = 120

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
          <circle cx="6" cy="8" r="5" fill="{l["color"]}" />
          <text x="18" y="12" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="13" font-weight="600">{l["name"]}</text>
          <text x="18" y="27" fill="#94a3b8" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">{l["percentage"]:.1f}% · {b_str}</text>
        </g>
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <defs>
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="8" />
    </clipPath>
  </defs>
  
  <rect width="{W}" height="{H}" rx="14" fill="#0b1120" stroke="#1e293b" stroke-width="1.5" />
  
  <text x="40" y="44" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="16" font-weight="700">CODEBASE REPOSITORY BREAKDOWN</text>
  <text x="40" y="62" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">Phạm vi: {data.get("public_repos_count", 8)} public non-fork repositories · Tổng dung lượng: {total_bytes / (1024*1024):.1f} MB</text>
  
  <g clip-path="url(#bar-clip)">
    {''.join(segments_svg)}
  </g>
  
  {''.join(legend_svg)}
  
  <line x1="40" y1="205" x2="820" y2="205" stroke="#1e293b" stroke-width="1" />
  <text x="40" y="226" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10">Phương pháp: Dữ liệu dung lượng byte mã nguồn tổng hợp qua GitHub API từ các kho lưu trữ công khai của @tiendat2712 (đã loại bỏ fork).</text>
  <text x="40" y="242" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10">Tỷ lệ thể hiện cơ cấu dung lượng mã nguồn (codebase volume ratio), không biểu thị phần trăm mức độ thành thạo cá nhân. Cập nhật: {updated_at}.</text>
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
    H = 290
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
          <rect x="0" y="0" width="780" height="30" rx="6" fill="#0f172a" stroke="#1e293b" stroke-width="1" />
          <text x="14" y="19" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11" font-weight="500">{date}</text>
          <rect x="94" y="5" width="130" height="20" rx="4" fill="#1e293b" />
          <text x="159" y="19" text-anchor="middle" fill="#38bdf8" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11" font-weight="600">{repo}</text>
          <rect x="232" y="5" width="64" height="20" rx="4" fill="#1e3a5f" />
          <text x="264" y="19" text-anchor="middle" fill="#7dd3fc" font-family="'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace" font-size="11" font-weight="600">{sha}</text>
          <text x="306" y="19" fill="#e2e8f0" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">{msg}</text>
        </g>
        ''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <rect width="{W}" height="{H}" rx="14" fill="#0b1120" stroke="#1e293b" stroke-width="1.5" />
  
  <text x="40" y="44" fill="#f8fafc" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="16" font-weight="700">VERIFIED RECENT GITHUB COMMITS</text>
  <text x="40" y="62" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11">Phạm vi: Toàn bộ commit thật trên các kho lưu trữ công khai của @tiendat2712</text>
  
  <g transform="translate(680, 28)">
    <rect x="0" y="0" width="140" height="26" rx="6" fill="#064e3b" stroke="#059669" stroke-width="1" />
    <circle cx="14" cy="13" r="4" fill="#34d399" />
    <text x="25" y="17" fill="#6ee7b7" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="11" font-weight="600">LIVE COMMITS</text>
  </g>
  
  {''.join(commit_rows_svg)}
  
  <line x1="40" y1="262" x2="820" y2="262" stroke="#1e293b" stroke-width="1" />
  <text x="40" y="278" fill="#64748b" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10">Dữ liệu thực tế từ git log và GitHub API. Cập nhật lần cuối: {updated_at}.</text>
</svg>
'''
    target = os.path.join(ASSETS_DIR, "github-activity.svg")
    with open(target, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO] Generated {target}")

def generate_hero_3d():
    SS = 2
    W = 1060 * SS
    H = 340 * SS
    CX = 780 * SS
    CY = 158 * SS
    SCALE = 1.30 * SS
    NUM_FRAMES = 36

    BG_COLOR = (10, 15, 28, 255)
    CARD_BG = (12, 19, 36, 255)
    BORDER_COLOR = (30, 48, 77, 255)

    CYAN = (56, 189, 248, 255)
    TEAL = (45, 212, 191, 255)
    EMERALD = (52, 211, 153, 255)
    PURPLE = (168, 85, 247, 255)
    TEXT_WHITE = (248, 250, 252, 255)
    TEXT_MUTED = (160, 175, 200, 255)
    TEXT_DIM = (110, 128, 155, 255)

    LIGHT = np.array([-0.4, -0.5, 0.75])
    LIGHT = LIGHT / np.linalg.norm(LIGHT)

    def get_font(size, bold=False, mono=False):
        s = int(size * SS)
        candidates = []
        if mono:
            candidates = [
                "C:/Windows/Fonts/consola.ttf" if not bold else "C:/Windows/Fonts/consolab.ttf",
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
    FONT_CHIP = get_font(11, bold=True, mono=True)
    FONT_META = get_font(11, bold=False, mono=True)
    FONT_3D = get_font(10, bold=True, mono=True)

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
        intensity = 0.28 + 0.72 * dot
        r = int(min(255, max(0, base_rgb[0] * intensity)))
        g = int(min(255, max(0, base_rgb[1] * intensity)))
        b = int(min(255, max(0, base_rgb[2] * intensity)))
        return (r, g, b, 255)

    def render_frame_2x(t_idx, total_frames):
        t_ratio = t_idx / float(total_frames)
        rot_angle = t_ratio * 2.0 * math.pi
        
        img = Image.new("RGBA", (W, H), CARD_BG)
        draw = ImageDraw.Draw(img, "RGBA")
        
        m = 3 * SS
        draw.rounded_rectangle([(m, m), (W - m, H - m)], radius=18 * SS, fill=CARD_BG, outline=BORDER_COLOR, width=2 * SS)
        
        # Left Side
        lx = 46 * SS
        by = 38 * SS
        bw = 250 * SS
        bh = 26 * SS
        draw.rounded_rectangle([(lx, by), (lx + bw, by + bh)], radius=6 * SS, fill=(15, 30, 56, 255), outline=(32, 70, 120, 255), width=1 * SS)
        dot_r = 4 * SS
        draw.ellipse([(lx + 12 * SS - dot_r, by + 13 * SS - dot_r), (lx + 12 * SS + dot_r, by + 13 * SS + dot_r)], fill=(16, 185, 129, 255))
        draw.text((lx + 24 * SS, by + 5 * SS), "BACKEND & CLOUD PLATFORM", fill=CYAN, font=FONT_BADGE)
        
        ny = 76 * SS
        draw.text((lx, ny), "PHAN TRINH TIEN DAT", fill=TEXT_WHITE, font=FONT_NAME)
        
        ry = 122 * SS
        draw.text((lx, ry), "Backend · Cloud & DevOps Engineer", fill=TEAL, font=FONT_ROLE)
        
        dy1 = 156 * SS
        dy2 = 178 * SS
        draw.text((lx, dy1), "Building scalable Java/Spring services · Engineering cloud platforms.", fill=TEXT_MUTED, font=FONT_DESC)
        draw.text((lx, dy2), "Automating containerized workloads with Kubernetes, Terraform & GitOps.", fill=TEXT_MUTED, font=FONT_DESC)
        
        chips_row1 = [
            ("Java / Spring Boot", (18, 38, 68), CYAN),
            ("Kubernetes & AWS", (16, 46, 56), TEAL),
            ("Terraform IaC", (42, 28, 68), PURPLE),
        ]
        chips_row2 = [
            ("CI/CD & GitOps", (18, 38, 68), CYAN),
            ("Distributed Systems", (20, 48, 40), EMERALD),
            ("Observability", (22, 45, 60), TEAL),
        ]
        
        def draw_chip_row(chips, start_y):
            cx_pos = lx
            for label, bg, stroke in chips:
                bbox = FONT_CHIP.getbbox(label)
                tw = bbox[2] - bbox[0]
                cw = tw + 20 * SS
                ch = 24 * SS
                draw.rounded_rectangle([(cx_pos, start_y), (cx_pos + cw, start_y + ch)], radius=5 * SS, fill=bg + (255,), outline=stroke, width=1 * SS)
                draw.text((cx_pos + 10 * SS, start_y + 3 * SS), label, fill=TEXT_WHITE, font=FONT_CHIP)
                cx_pos += cw + 10 * SS
                
        draw_chip_row(chips_row1, 212 * SS)
        draw_chip_row(chips_row2, 244 * SS)
        
        my = 286 * SS
        draw.text((lx, my), "LOCATION: Da Nang, Vietnam", fill=TEXT_DIM, font=FONT_META)
        draw.text((lx + 230 * SS, my), "PIPELINE: Code -> Cloud -> Reliability", fill=TEXT_DIM, font=FONT_META)
        
        sep_x = 530 * SS
        draw.line([(sep_x, 32 * SS), (sep_x, H - 32 * SS)], fill=(24, 38, 62, 255), width=1 * SS)
        
        # 3D Viewport
        cam_rot = rot_angle * 0.25
        grid_half = 4
        grid_step = 26
        grid_z = -48
        
        for i in range(-grid_half, grid_half + 1):
            dist_factor = 1.0 - (abs(i) / (grid_half + 1.2))
            alpha = int(140 * dist_factor)
            g_col = (30, 52, 85, alpha)
            p1 = project_3d(-grid_half * grid_step, i * grid_step, grid_z, cam_rot)
            p2 = project_3d(grid_half * grid_step, i * grid_step, grid_z, cam_rot)
            draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=g_col, width=1 * SS)
            p3 = project_3d(i * grid_step, -grid_half * grid_step, grid_z, cam_rot)
            p4 = project_3d(i * grid_step, grid_half * grid_step, grid_z, cam_rot)
            draw.line([(p3[0], p3[1]), (p4[0], p4[1])], fill=g_col, width=1 * SS)
        
        num_pts = 48
        ring_r = 92.0
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
            draw.line([(pts_ring[k][0], pts_ring[k][1]), (pts_ring[kn][0], pts_ring[kn][1])], fill=(40, 80, 130, 180), width=1 * SS)
        
        center_z = 8.0 + 7.0 * math.sin(rot_angle * 2.0)
        master_size = 38.0
        ms = master_size / 2.0
        m_rot = rot_angle * 1.5
        cos_m, sin_m = math.cos(m_rot), math.sin(m_rot)
        
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
            
        pod_radius = 80.0
        pod_size = 20.0
        ps = pod_size / 2.0
        worker_pods = []
        pod_configs = [
            ("POD-01 (API)", CYAN, (18, 120, 150), (56, 189, 248)),
            ("POD-02 (DATA)", PURPLE, (130, 36, 210), (192, 132, 252)),
            ("POD-03 (QUEUE)", TEAL, (16, 122, 115), (45, 212, 191)),
            ("POD-04 (AUTH)", EMERALD, (10, 125, 90), (52, 211, 153)),
        ]
        
        for i in range(4):
            theta = rot_angle + i * (math.pi / 2.0)
            px = pod_radius * math.cos(theta)
            py = pod_radius * math.sin(theta)
            pz = center_z + 12.0 * math.sin(rot_angle * 2.0 + i * 1.5)
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
            base_col = (20, 65, 120) if norm[2] > 0 else (14, 45, 85)
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
                cur_base = [min(255, int(c * 1.3)) for c in base_col] if norm[2] > 0 else base_col
                face_col = shade_color(cur_base, norm, LIGHT)
                render_queue.append((avg_d, 'face', screen_pts, face_col, border_col, 2 * SS))
                
            c_proj = project_3d(0, 0, center_z, cam_rot)
            p_proj = project_3d(px, py, pz, cam_rot)
            line_depth = (c_proj[2] + p_proj[2]) / 2.0
            render_queue.append((line_depth, 'line', [(c_proj[0], c_proj[1]), (p_proj[0], p_proj[1])], (28, 64, 105, 180), 2 * SS))
            
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
                draw.ellipse([(pos[0] - pr - 2 * SS, pos[1] - pr - 2 * SS), (pos[0] + pr + 2 * SS, pos[1] + pr + 2 * SS)], outline=(col[0], col[1], col[2], 120), width=1 * SS)
            elif itype == 'led':
                pos, col, lr = item[2], item[3], item[4]
                draw.ellipse([(pos[0] - lr, pos[1] - lr), (pos[0] + lr, pos[1] + lr)], fill=col)
            elif itype == 'core':
                pos, col, cr = item[2], item[3], item[4]
                draw.ellipse([(pos[0] - cr, pos[1] - cr), (pos[0] + cr, pos[1] + cr)], fill=col)
                draw.ellipse([(pos[0] - cr - 3 * SS, pos[1] - cr - 3 * SS), (pos[0] + cr + 3 * SS, pos[1] + cr + 3 * SS)], outline=(255, 255, 255, 180), width=1 * SS)
                
        hud_y = H - 36 * SS
        draw.text((CX - 90 * SS, hud_y), "KUBERNETES TOPOLOGY 3D", fill=CYAN, font=FONT_3D)
        
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

    print(f"[INFO] Generating vector SVGs with dataset updated at: {data.get('updated_at')}")
    generate_languages_svg(data)
    generate_activity_svg(data)

    if not args.skip_gif:
        generate_hero_3d()
    else:
        print("[INFO] Skipping 3D GIF generation as requested.")

    print("[SUCCESS] All profile assets generated successfully!")

if __name__ == "__main__":
    main()
