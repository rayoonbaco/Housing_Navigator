# Publication steps

This directory is the repository root. Upload its **contents**, preserving the `ui`, `engine` and `audit` directories. Do not upload the enclosing package ZIP as the website.

## GitHub

Create a public repository named `Housing_Navigator` at https://github.com/new. Use description “Plain-language rental housing rules with inspectable evidence.” An empty repository avoids creating duplicate initial files. Choose the new repository, then **uploading an existing file** (or **Add file → Upload files**). Drag all contents of this publication directory into the upload area. Commit with “Add evaluated Housing Navigator release candidate and evidence.”

The publication package contains fewer than 100 files and every file is below 25 MiB, GitHub's browser file limit. The canonical challenge JSON is archived, keeping large pretty-printed snapshots out of browser uploads. Official upload instructions: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

Send the repository URL to the coordinator for verification. Check its README, `ui/index.html`, compressed lookup resources, source code and audit archives are present. Do not replace an earlier unrelated repository.

## Render

Create **New → Static Site**, connect this repository and select its committed branch. Use:

| Setting | Value |
|---|---|
| Name | `housing-navigator` (or an available variant) |
| Root directory | Leave blank |
| Build command | `true` |
| Publish directory | `ui` |
| Environment variables | None required |

The included `render.yaml` expresses the same configuration. Deploy as a static site, not a Python web service. Official static-site documentation: https://render.com/docs/static-sites

Once Render reports the deployment live, send its URL to the coordinator. Then check the public URL while signed out: address selection, each topic, one evidence drawer, all four dates, T1–T5, mobile layout and downloaded JSON. These interaction checks are separate from a successful build.

## Submission

Use only verified GitHub/demo links. Record three separate videos, each at most 60 seconds, as shown in the supplied HackOS screenshots. Complete HackOS and the separate Google Form, saving both receipts. The coordinator will reconcile live form requirements before final submission. Avoid new features during the final 90 minutes.
