# Public media repository rules

- This repository is public. Never add access tokens, personal data, paid-note content, unpublished drafts, source projects, or editing files.
- Store final Instagram JPG or MP4 files as assets on the `instagram-media` GitHub Release. Do not commit delivery media to Git history.
- Only upload media that the user has selected for publication.
- Do not upload explicit sexual imagery, underwear-focused imagery, depictions of sexual acts, or media involving anyone who could appear underage.
- Keep filenames unique and derived from a post ID plus a random suffix. Do not put personal information in filenames.
- Do not claim that MP4 storage means Reels publishing is implemented. Reels publishing currently belongs to the future roadmap.
- When changing cleanup behavior, run `python -m unittest discover -s tests -v`.
- Do not manually delete media outside the documented retention policy unless the user explicitly requests the exact deletion.
