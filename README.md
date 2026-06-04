# ai-infra-curriculum.github.io

The landing page for the **AI Infrastructure Bootcamp** — 16-week live cohort,
Founding Cohort priced at $199 / Standard $399.

Serves at: <https://ai-infra-curriculum.github.io/>

## Tech

- Plain HTML + CSS. No build step.
- Dark editorial theme mirroring the cohort's slide-deck palette.
- Inter + JetBrains Mono via Google Fonts.
- Single page; smooth-scroll nav.

## Editing

Almost all edits happen in `index.html`. Search for the `TODO:` comments
before launch:

- `TODO: wire action to an email-capture provider` — application form
  (currently no-op, action="#")
- Optional: add a LinkedIn link to the Instructor card once the canonical
  URL is verified
- Optional: add an `og:image` for nicer social previews

## Email-capture form

The form currently has `action="#"` as a no-op placeholder. To wire it:

| Provider | What to change |
|---|---|
| Formspree | `action="https://formspree.io/f/YOUR_ID"` |
| ConvertKit | Embed code from a ConvertKit form |
| Buttondown | `action="https://buttondown.email/api/emails/embed-subscribe/SLUG"` |
| Tally.so | Replace the `<form>` block with a Tally `<iframe>` |
| Google Forms | Use the GForms embed |

If you want the simplest path: Formspree free tier is fine for a waitlist.

## Local preview

```bash
# Any static file server works
python3 -m http.server 8000
# then open http://localhost:8000/
```

## Pre-launch checklist

- [ ] Wire the form `action` to a real provider
- [ ] Set Cohort 1 start date (search for "Dates TBA")
- [ ] Verify LinkedIn URL and add to Instructor card
- [ ] Add Discord invite once the moderation bot has provisioned
- [ ] Add OG image (`og:image` meta tag — currently missing)
- [ ] Verify metadata via <https://www.opengraph.xyz/>
- [ ] In repo settings → Pages → confirm deployed from `main` branch root

## Notes

- Repo is named `ai-infra-curriculum.github.io` so the org's GitHub Pages
  serve it at the bare URL (no `/repo-name/` suffix)
- The repo must be **public** for GitHub Pages on a free plan
- No Jekyll. The `_config.yml`-less setup ships HTML as-is.
