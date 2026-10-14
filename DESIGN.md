# Design System: DevOps Engineer Profile

<!-- impeccable:design-schema 1 -->

## Overview

A high-craft, credible engineering identity system for Phan Trinh Tien Dat's GitHub profile. Designed to balance high-concurrency Java backend expertise with automated cloud infrastructure practices (AWS, Kubernetes, Terraform, CI/CD). Replaces generic badge walls and ill-placed raw data with an executive narrative: Identity & Bio → Featured Projects Showcase → Technical Stack → Architecture Blueprint → Certification Milestones → Empirical Telemetry & Verified Activity.

---

## Colors

```yaml
colors:
  canvas-deep: "#0B1120"
  canvas-subtle: "#0F172A"
  surface-card: "#132333"
  surface-border: "#1E3447"
  text-primary: "#F8FAFC"
  text-secondary: "#94A3B8"
  text-muted: "#64748B"
  accent-cyan: "#38BDF8"
  accent-teal: "#2DD4BF"
  accent-emerald: "#10B981"
  accent-amber: "#F59E0B"
  accent-purple: "#A855F7"
```

### Color Roles & Meaning
- **Deep Canvas (`#0B1120`, `#0F172A`):** Terminal and modern IDE depth, establishing focused technical immersion without glare.
- **Electric Cyan (`#38BDF8`):** Primary branding accent for cloud connectivity, platform orchestration, and primary links.
- **Mint Teal (`#2DD4BF`):** Secondary accent for runtime components, container instances, and infrastructure status.
- **Emerald Green (`#10B981`):** Active status, verified data markers, and passing pipeline states.
- **Amber (`#F59E0B`):** Milestone goals, planned certifications, and intentional learning roadmaps.
- **Slate (`#94A3B8`, `#64748B`):** Supporting technical metadata, methodology notes, and secondary documentation.

---

## Typography

- **Display & Headings:** Clean sans-serif hierarchy (`Segoe UI`, `-apple-system`, `BlinkMacSystemFont`, `Roboto`, `Helvetica Neue`, sans-serif) for high legibility across GitHub web and mobile clients.
- **Code & Telemetry:** Monospace (`JetBrains Mono`, `Consolas`, `ui-monospace`, `Menlo`, monospace) for commit SHAs, file paths, repository identifiers, and terminal commands.
- **Reading Measure:** 65–85 characters per line for technical narrative paragraphs to maintain comfortable reading rhythm.

---

## Layout & Information Architecture

The profile layout follows an intentional recruiter and engineering lead decision funnel:

1. **Hero & Kinetic Topology:** Immersive 3D perspective topology visualization establishing immediate technical craft.
2. **About Me (Executive Summary):** Clear title, location, engineering philosophy, bulleted strengths, and high-contrast social badges.
3. **Featured Projects Showcase:** Responsive 2-column card grid (`<table>`) presenting real repos (`morph3d-ai`, `identity-service`, `java-core-mastery`, `devops-platform-lab`) with problem statements and technology tags.
4. **Technical Stack:** Categorized into 6 specialized disciplines (Backend, Cloud, CI/CD, IaC, Observability, Security) clearly distinguishing production practice from roadmap goals.
5. **Hands-on Architecture Blueprint:** Interactive Mermaid flowchart demonstrating continuous delivery and GitOps topology.
6. **Certification Roadmap:** Transparent, honest milestones (`[GOAL]`, `[PLANNED]`) with official exam syllabus references.
7. **Empirical Activity & Telemetry:** Verified recent commits and codebase language volume distribution backing up claims with verifiable evidence.
8. **Connect & Collaborate:** Professional closing contact channels.

---

## Components

### 1. Social & Profile Badges
- Style: `for-the-badge` (Shields.io)
- Height: 28px
- Logos: Official brand SVG logos (`gmail`, `github`, `facebook`, `instagram`, `googlemaps`, `statuspage`)
- Contrast: WCAG AAA compliant against badge background fills.

### 2. Featured Project Cards
- Container: HTML `<table>` with two `50%` width cells per row for responsive desktop and tablet rendering.
- Card Header: Emoji icon + Markdown hyperlink to the repository.
- Card Subtitle: Bold role / architecture focus in concise phrasing.
- Card Body: 2–3 sentences highlighting actual engineering implementations.
- Card Footer: Stack badges using `style=flat-square` with official technology colors.

### 3. Empirical Verification Badges & Widgets
- Status Pill: Emerald badge (`LIVE COMMITS` / `VERIFIED COMMITS`) with pulse styling.
- Commit Links: Monospace commit SHA linking directly to GitHub commit diffs.
- Language Volume: Verified percentage distribution strictly excluding forks.

---

## Do's and Don'ts

### Do
- Lead with who you are and what you build (Featured Projects) before showing raw telemetry data.
- Maintain total transparency regarding certification status (clearly marked as `[GOAL]` / `[PLANNED]`).
- Use high-contrast, official brand-colored badges for direct social channels.
- Keep the commit activity and language breakdown as empirical verification at the bottom.

### Don't
- Don't place raw commit tables and commit log listings above projects or tech stacks.
- Don't use third-party dynamic badges that frequently return 502/504 Bad Gateway errors.
- Don't claim certifications that have not been officially passed.
- Don't clutter the page with uncurated, repetitive icon matrices without contextual explanation.
