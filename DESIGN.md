# Backend / DevOps GitHub Profile

## Direction

Use an animated title, compact introduction, recognizable tool logos, contribution visuals, statistics. Preserve Phan Trinh Tien Dat's own stack and identity. Do not copy another user's data, projects, social links, or personal artwork.

## Visual system

- Navy asset background: #0b1120.
- Main text: #f8fafc; secondary text: #cbd5e1; small metadata: #94a3b8.
- Primary accents: cyan #38bdf8 and #67e8f9.
- Calendar levels: #142434, #155e75, #0891b2, #22d3ee, #a5f3fc.
- Decorative calendar trail: #facc15.
- Body typography and page background follow native GitHub Markdown.
- Individual technology icons are 42px and wrap independently. No layout tables.

## Reading order

1. Locally hosted animated name and short role/contact header.
2. Concise Backend / DevOps introduction and actual contribution calendar.
3. Four named technology groups; secondary tools in a native disclosure.
4. Statistics and language cards, followed by an expandable 3D contribution skyline.
6. Existing 36-frame cloud GIF and expandable target architecture.
7. Six explicitly unearned certification goals.

## Data and animation

`scripts/update_profile.py` fetches the public GitHub contribution calendar, owned public non-fork repositories, language byte totals. It renders statistics assets without reading or writing README.md. The workflow refreshes daily and supports manual dispatch. An initial push changing the script or workflow also triggers it.

All fetches complete before output generation. A fetch failure fails the workflow and preserves the prior snapshot and timestamps. Token values are never saved. No new Python dependencies are required.

The calendar trail is decorative; calendar cells and skyline heights represent observed activity levels. Heights are not exact commit counts. Language percentages measure code bytes, not skill. The 3D cloud pipeline is illustrative, not a claim of production ownership.

Existing `generate_assets.py` and its earlier assets are retained for manual regeneration of the cloud illustrations. The scheduled workflow now uses `update_profile.py`.

## Validation

New SVGs parsed successfully; their static rendering was visually inspected. README has no tables and all local images exist. All 36 referenced remote images responded successfully during validation. Existing hero has 36 frames. Live GitHub rendering and animation playback are not claimed as verified.
