#!/usr/bin/env python3
"""Generate per-role holder pages + the ladder grid from the curriculum manifest.

Reads the structural manifest produced by the content generator
(`ai-infra-content-generator/manifest/curriculum.manifest.json`) for module
outlines, exercise/project counts, and repo URLs, and pairs it with the
hand-authored ROLE metadata below (clean display names, blurbs, grouping).

Outputs:
  roles/<slug>.html           one page per non-junior role
  _ladder-grid.html           the grouped ladder grid snippet (for index.html)

Static site, absolute paths (served at the domain root). Idempotent.
"""
from __future__ import annotations

import json
import html
from pathlib import Path

REPO = Path(__file__).resolve().parent
MANIFEST = REPO.parent / "ai-infra-content-generator" / "manifest" / "curriculum.manifest.json"

# Hand-authored display metadata. Module outlines/counts come from the manifest.
ROLES: dict[str, dict] = {
    "junior-engineer": {"name": "Junior AI Infrastructure Engineer", "blurb": "The on-ramp: ship one production-shaped ML service over 16 weeks — containers, Kubernetes, CI/CD, monitoring, and a real capstone.", "page": "/junior.html"},
    "engineer": {"name": "AI Infrastructure Engineer", "blurb": "The core production role: containerize, deploy, and operate ML services on Kubernetes with CI/CD, monitoring, and cost control. The deepest, most hands-on track in the ladder."},
    "senior-engineer": {"name": "Senior AI Infrastructure Engineer", "blurb": "Run ML infrastructure at scale: SLOs, on-call, capacity planning, multi-tenant platforms, and the judgment calls that keep production healthy under load."},
    "principal-engineer": {"name": "Principal AI Infrastructure Engineer", "blurb": "Set technical direction across teams: reference architectures, platform strategy, and the hard trade-offs that shape how an org builds and runs AI infrastructure."},
    "architect": {"name": "AI Infrastructure Architect", "blurb": "Design the systems: end-to-end ML platform architecture, data and serving layers, reliability and cost as first-class constraints, and the diagrams that align teams."},
    "senior-architect": {"name": "Senior AI Infrastructure Architect", "blurb": "Architect across the enterprise: multi-region, multi-tenant platforms, governance, and the long-horizon decisions that outlive any single project."},
    "principal-architect": {"name": "Principal AI Infrastructure Architect", "blurb": "Own the architectural vision org-wide: standards, paved roads, and the strategy that turns scattered ML work into a coherent platform."},
    "team-lead": {"name": "AI Infrastructure Team Lead", "blurb": "Lead an AI infrastructure team: delivery, mentorship, planning, and translating between engineers and the business without losing the technical thread."},
    "chief-ai-officer": {"name": "Chief AI Officer", "blurb": "The executive view: AI strategy, governance, risk, build-vs-buy, and turning AI capability into business outcomes and defensible org structure."},
    "mlops": {"name": "MLOps Engineer", "blurb": "Own the ML lifecycle in production: pipelines, experiment tracking, model registries, CI/CD for models, monitoring, and progressive rollout."},
    "ml-platform": {"name": "ML Platform Engineer", "blurb": "Build the internal platform other ML teams build on: paved roads, self-service, feature and serving infra, GPU scheduling, and cost levers."},
    "performance": {"name": "AI Performance Engineer", "blurb": "Make ML systems fast and cheap: profiling, quantization and compression, batching, CUDA-level optimization, and serving economics."},
    "security": {"name": "AI Infrastructure Security Engineer", "blurb": "Secure the AI stack: threat modeling, supply-chain and model security, secrets, access control, and the controls that keep ML systems and data safe."},
    "agentic-ai-developer": {"name": "Agentic AI Developer", "blurb": "Entry rung of the agentic track: LLM APIs, prompt engineering, structured output, tool and function calling, retrieval basics, and shipping a first LLM-powered app."},
    "agentic-ai-engineer": {"name": "Agentic AI Engineer", "blurb": "Build real agentic systems: multi-step agents, tool use, retrieval, evaluation, and the production patterns behind reliable LLM applications."},
    "senior-agentic-ai-engineer": {"name": "Senior Agentic AI Engineer", "blurb": "Lead agentic engineering: complex multi-agent systems, orchestration, evaluation at scale, safety, and the architecture of production agent platforms."},
    "agentic-systems-architect": {"name": "Agentic Systems Architect", "blurb": "Architect agentic platforms: multi-agent orchestration, memory and context systems, evaluation and safety infrastructure, and enterprise-grade agent systems."},
}

# Ordered groups for the ladder grid.
GROUPS: list[tuple[str, list[str]]] = [
    ("Engineering ladder", ["junior-engineer", "engineer", "senior-engineer", "principal-engineer"]),
    ("Architecture ladder", ["architect", "senior-architect", "principal-architect"]),
    ("Platform & specialties", ["mlops", "ml-platform", "performance", "security"]),
    ("Leadership", ["team-lead", "chief-ai-officer"]),
    ("Agentic track", ["agentic-ai-developer", "agentic-ai-engineer", "senior-agentic-ai-engineer", "agentic-systems-architect"]),
]

GH_ICON = ('<svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" aria-hidden="true">'
           '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>')


def clean_title(raw: str) -> str:
    return raw.split(": ", 1)[1] if ": " in raw else raw


def role_url(slug: str) -> str:
    return ROLES[slug].get("page", f"/roles/{slug}.html")


def nav() -> str:
    return f"""<nav class="nav" aria-label="Main navigation">
  <div class="nav__inner">
    <a class="nav__brand" href="/">ai-infra-curriculum<strong>.</strong></a>
    <div class="nav__links">
      <a href="/#ladder">The ladder</a>
      <a href="/junior.html">First cohort</a>
      <a href="/teams.html">Teams</a>
      <a class="nav__github" href="https://github.com/ai-infra-curriculum" target="_blank" rel="noopener" aria-label="AI Infrastructure Curriculum on GitHub">{GH_ICON} GitHub</a>
    </div>
  </div>
</nav>"""


def footer() -> str:
    return """<footer>
  <div class="wrap">
    <p>
      ai-infra-curriculum · built by <a href="https://github.com/JoshuaAFerguson">Joshua Ferguson</a>
      (<a href="https://joshua-ferguson.com">joshua-ferguson.com</a> · <a href="https://www.linkedin.com/in/joshuaaferguson/">LinkedIn</a>)<br>
      Curriculum source: <a href="https://github.com/ai-infra-curriculum">github.com/ai-infra-curriculum</a><br>
      Questions: <a href="mailto:contact@joshua-ferguson.com">contact@joshua-ferguson.com</a>
    </p>
  </div>
</footer>"""


def role_page(track: dict, group: str) -> str:
    slug = track["slug"]
    meta = ROLES[slug]
    name = meta["name"]
    blurb = meta["blurb"]
    mods = track["modules"]
    n_ex = sum(len(m.get("exercises", [])) for m in mods)
    n_proj = len(track.get("projects", []))
    learn_url = track.get("learning_repo_url") or f"https://github.com/ai-infra-curriculum/{track['learning_repo']}"
    sol_url = track.get("solutions_repo_url") or f"https://github.com/ai-infra-curriculum/{track['solutions_repo']}"
    subj = name.replace(" ", "%20")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)} — AI Infrastructure Curriculum</title>
<meta name="description" content="{html.escape(blurb)} Free and open-source curriculum on GitHub; live cohort planned.">
<meta property="og:title" content="{html.escape(name)} — AI Infrastructure Curriculum">
<meta property="og:description" content="{html.escape(blurb)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/styles.css">
</head>
<body>

{nav()}

<main>

<header class="hero">
  <div class="wrap">
    <div class="hero__eyebrow"><a href="/#ladder" style="color:var(--c-ink-dim);border:none;">{group}</a> · <span class="badge-dev">In development</span></div>
    <h1>{html.escape(name)}<span class="period">.</span></h1>
    <p class="hero__sub">{html.escape(blurb)}</p>

    <a href="{learn_url}" class="hero__cta" target="_blank" rel="noopener">
      Follow the build on GitHub
      <span class="arrow">→</span>
    </a>

    <div class="hero__meta">
      <span><span class="dot"></span>Under active development</span>
      <span><span class="dot"></span>Open-source on GitHub</span>
      <span><span class="dot"></span>Live cohort planned</span>
    </div>
  </div>
</header>

<section class="teams-callout-section">
  <div class="wrap">
    <div class="teams-callout__inner">
      <div class="teams-callout__copy">
        <div class="section__eyebrow">Status</div>
        <h2>This track is under development.</h2>
        <p>
          The curriculum and reference solutions for this role are being built in the open on
          GitHub — follow along as they take shape. A live, instructor-led cohort (a focused
          version of the material) is planned; join the waitlist and you'll hear first when it's
          ready.
        </p>
      </div>
      <a href="mailto:contact@joshua-ferguson.com?subject=Notify%20me%20%E2%80%94%20{subj}%20cohort" class="hero__cta">Join the waitlist <span class="arrow">→</span></a>
    </div>

    <div class="role-links">
      <a href="{learn_url}" target="_blank" rel="noopener">{GH_ICON} Curriculum repo</a>
      <a href="{sol_url}" target="_blank" rel="noopener">{GH_ICON} Solutions repo</a>
    </div>

    <p class="role-crosssell">
      The first live cohort — <a href="/junior.html">Junior AI Infrastructure Engineer</a> — is
      enrolling now. It's the on-ramp to this track. <a href="/#ladder">See the full ladder →</a>
    </p>
  </div>
</section>

</main>

{footer()}

</body>
</html>
"""


def ladder_grid(by_slug: dict[str, dict]) -> str:
    out = ['<div class="ladder__groups">']
    for group, slugs in GROUPS:
        out.append(f'  <div class="ladder__group">')
        out.append(f'    <h3 class="ladder__group-title">{group}</h3>')
        out.append('    <div class="ladder__grid">')
        for slug in slugs:
            track = by_slug.get(slug)
            if not track:
                continue
            meta = ROLES[slug]
            is_junior = slug == "junior-engineer"
            status = "Cohort 1 · live" if is_junior else "In development"
            cls = "rung rung--live" if is_junior else "rung rung--dev"
            out.append(f'      <a class="{cls}" href="{role_url(slug)}">')
            out.append(f'        <div class="rung__status">{status}</div>')
            out.append(f'        <h3>{html.escape(meta["name"])}</h3>')
            out.append(f'        <p>{html.escape(meta["blurb"])}</p>')
            out.append('      </a>')
        out.append('    </div>')
        out.append('  </div>')
    out.append('</div>')
    return "\n".join(out)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    by_slug = {t["slug"]: t for t in manifest["tracks"]}
    group_of = {slug: g for g, slugs in GROUPS for slug in slugs}

    roles_dir = REPO / "roles"
    roles_dir.mkdir(exist_ok=True)
    written = 0
    for slug, track in by_slug.items():
        if slug == "junior-engineer":
            continue  # keeps its full cohort page at /junior.html
        if slug not in ROLES:
            print(f"  skip (no metadata): {slug}")
            continue
        (roles_dir / f"{slug}.html").write_text(role_page(track, group_of.get(slug, "")))
        written += 1

    (REPO / "_ladder-grid.html").write_text(ladder_grid(by_slug))
    print(f"Wrote {written} role pages to {roles_dir} + _ladder-grid.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
