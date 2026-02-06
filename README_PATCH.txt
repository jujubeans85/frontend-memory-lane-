LETFISHFUCK — Patch: Steps 1–3 (single JS source of truth)

What this patch does:
1) Replaces /assets/js/app.js (was a tiny loader) with the FULL engine.
2) Adds a safety-net stub at /js/app.js that forwards to /assets/js/app.js.
   (So old references won't break while you clean up.)
3) Hub New Drop pulls from projects/experiments/notes, notes media supports arrays.

Apply:
- Drop these two files into your repo at the exact paths:
  - letfishfuck_site_v2/assets/js/app.js
  - letfishfuck_site_v2/js/app.js

Optional cleanup (recommended later):
- Update every page to include ONLY:
    <script defer src="/assets/js/app.js"></script>
  and remove any <script src="/js/app.js"> or other JS paths.

If something looks blank:
- Check your page has one of these mounts:
  #projects / #experiments / #notes / #links / #newDrop
  (or data-mount="projects" etc.)
