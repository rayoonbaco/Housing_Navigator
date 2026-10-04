#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import shutil
import subprocess
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

required_files = ["index.html", "styles.css", "app.js", "README.md"]
check("required UI files exist", all((ROOT / f).is_file() for f in required_files), ", ".join(required_files))

manifest = load_json(FIX / "manifest.json")
required_manifest = {"contract_version","mode","default_as_of","addresses_url","rules_url","provenance_url","jurisdictions_url","snapshots"}
check("fixture manifest contract/version", manifest.get("contract_version") == "1" and manifest.get("mode") == "fixture")
check("fixture manifest required fields", required_manifest.issubset(manifest))

relative_values = [manifest.get(k) for k in ["addresses_url","rules_url","provenance_url","jurisdictions_url","report_url"] if k in manifest]
for snap in manifest.get("snapshots", []):
    relative_values.extend([snap.get("lookups_url"), snap.get("changes_url")])
rel_ok = all(isinstance(v, str) and v and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", v) and not v.startswith(("/", "//")) for v in relative_values)
check("manifest resources are relative", rel_ok)

dates = [s.get("as_of") for s in manifest.get("snapshots", [])]
check("snapshot dates unique and default generated", len(dates) == len(set(dates)) and manifest.get("default_as_of") in dates, str(dates))

addresses = load_json(ROOT / manifest["addresses_url"])
rules = load_json(ROOT / manifest["rules_url"])
provenance = load_json(ROOT / manifest["provenance_url"])
jurisdictions = load_json(ROOT / manifest["jurisdictions_url"])
address_ids = {a.get("address_id") for a in addresses}
rule_ids = {r.get("team_rule_id") for r in rules}
prov_ids = {p.get("team_rule_id") for p in provenance}

expected_categories = {"rent_increase_limits","just_cause_eviction","security_deposits","application_screening_fees","screening_restrictions","algorithmic_rent_setting"}
check("all six challenge categories represented", expected_categories.issubset({r.get("category") for r in rules}))
check("matched and unknown geography fixtures exist", {"matched_geography","unknown"}.issubset({j.get("jurisdiction_result") for j in jurisdictions}))
check("intentional provenance gap exists", bool(rule_ids - prov_ids), f"missing={sorted(rule_ids - prov_ids)}")
check("intentional manifest hash mismatch exists", any(p.get("manifest_hash_match") is False for p in provenance))
check("failed proposal fixture exists", any(r.get("status") == "failed" for r in rules))

statuses = set()
malformed_lookup_seen = False
probe_seen = False
for snap in manifest["snapshots"]:
    lp = ROOT / snap["lookups_url"]
    cp = ROOT / snap["changes_url"]
    check(f"snapshot files exist {snap['as_of']}", lp.is_file() and cp.is_file())
    lookup = load_json(lp)
    changes = load_json(cp)
    check(f"lookup as_of matches manifest {snap['as_of']}", lookup.get("as_of") == snap["as_of"])
    check(f"lookup covers fixture address keys {snap['as_of']}", address_ids.issubset(set(lookup.get("lookups", {}))))
    for aid, entries in lookup.get("lookups", {}).items():
        if not isinstance(entries, list):
            malformed_lookup_seen = True
            continue
        for entry in entries:
            statuses.add(entry.get("result"))
            if "<img src=x onerror=alert(1)>" in str(entry.get("explanation", "")):
                probe_seen = True
    check(f"change cases T1-T5 present {snap['as_of']}", set(changes) == {"T1","T2","T3","T4","T5"})
    check(f"T5 affected set empty {snap['as_of']}", changes.get("T5", {}).get("affected_address_ids") == [])

check("all applicability display states represented", {"applies","unknown","superseded","not_yet_effective","pending"}.issubset(statuses), str(sorted(statuses)))
check("malformed lookup fixture retained", malformed_lookup_seen)
check("untrusted text probe retained", probe_seen)

app = (ROOT / "app.js").read_text(encoding="utf-8")
html = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "styles.css").read_text(encoding="utf-8")
unsafe_patterns = [".innerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function("]
check("no trusted-HTML/eval rendering patterns", not any(p in app for p in unsafe_patterns), str([p for p in unsafe_patterns if p in app]))
check("dynamic text path uses textContent", "node.textContent = String(text)" in app)
check("persistent fixture banner present", "FIXTURE MODE - SYNTHETIC DATA - NOT LIVE RESULTS" in html)
check("not-legal-advice disclosure present", html.lower().count("not legal advice") >= 2)
check("answer-level as-of indicator present", "answerDatePill" in html and "As of ${" in app)
check("focus-visible treatment present", ":focus-visible" in css)
check("independent snapshot loading present", "Promise.allSettled" in app and "lookupError" in app and "changeError" in app)
check("lookup as_of mismatch guard present", "does not match selected snapshot" in app)
check("manifest mode mismatch guard present", "does not match requested" in app)
check("required base JSON type guards present", "expected a JSON list" in app)
check("structured null/object display helper present", "function structuredValue" in app)
check("malformed lookup message is mode-neutral", "lookup record for this address is malformed" in app and "lookup record for this fixture is malformed" not in app)
check("evidence-to-change navigation present", "View supplied change cases" in app)
check("stale snapshot request guard present", "snapshotRequestId" in app and "requestId !== state.snapshotRequestId" in app)
check("ARIA tab keyboard pattern present", 'role="tablist"' in html and html.count('role="tab"') == 3 and "ArrowRight" in app and "ArrowLeft" in app)
check("skip target is programmatically focusable", '<main id="main" tabindex="-1">' in html)

# No external runtime dependencies in HTML/CSS. Fixture source URLs are evidence and are intentionally excluded.
external_html = re.findall(r"(?:src|href)=[\"']https?://", html, flags=re.I)
external_css = re.findall(r"url\(\s*[\"']?https?://", css, flags=re.I)
check("no external HTML/CSS runtime dependency", not external_html and not external_css)

node = shutil.which("node")
if node:
    proc = subprocess.run([node, "--check", str(ROOT / "app.js")], capture_output=True, text=True)
    check("JavaScript syntax via node --check", proc.returncode == 0, (proc.stderr or proc.stdout).strip())
else:
    check("JavaScript syntax via node --check", False, "node unavailable")

# Serve the UI with Python stdlib and fetch representative files. This proves static-server compatibility, not browser execution.
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

cwd = Path.cwd()
try:
    import os
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/?fixture=1", timeout=5) as r:
        body = r.read().decode("utf-8")
        check("stdlib HTTP preview serves index", r.status == 200 and "Housing Navigator" in body)
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/fixtures/manifest.json", timeout=5) as r:
        served_manifest = json.loads(r.read().decode("utf-8"))
        check("stdlib HTTP preview serves fixture manifest", r.status == 200 and served_manifest.get("mode") == "fixture")
finally:
    try: server.shutdown()
    except Exception: pass
    try: os.chdir(cwd)
    except Exception: pass

failed = [c for c in checks if not c[1]]
for name, ok, detail in checks:
    suffix = f" - {detail}" if detail else ""
    print(f"{'PASS' if ok else 'FAIL'}: {name}{suffix}")
print(f"\nSUMMARY: {len(checks)-len(failed)}/{len(checks)} checks passed")
if failed:
    sys.exit(1)
