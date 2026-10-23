#!/usr/bin/env python3
"""Publish a factory release to GitHub AND the walker's forge, or copy GitHub's releases to the forge.

The walker, 2026-10-23: the packages on github.com/siliconight/gabagool_factory/releases should be on
forge.internal.vaultinteractive.net/BMONEY/gabagool_factory/releases as well. A Forgejo pull mirror keeps a repo's
code and tags in step but not its releases, so the forge repo is an ordinary repo and every release is published to
both from here: the same tag, the same notes, the same zip.

    python tools/publish_release.py factory-v1.42.0 --zip <zip> --notes docs/releases/factory-v1.42.0.md [--dry-run]
    python tools/publish_release.py --backfill [--dry-run]     # every GitHub release the forge lacks

A NEW RELEASE: main and the tag pushed to `origin` (GitHub) and to the forge; `gh release create` as before; then the
forge's release made through its API with the zip attached. BACKFILL: each GitHub release not on the forge, its zip
downloaded from GitHub into `_scratch/release_backfill/`, its title and notes read from GitHub, its tag pushed to the
forge, then published there the same way. Either way the forge's copy of the zip is downloaded back and held to the
local file's sha256 -- and for a backfill to GitHub's own digest -- and a mismatch FAILS.

THE FORGE CREDENTIAL IS THE WALKER'S, never this script's: it is read from Git Credential Manager (`git credential
fill` for the forge's host), where the walker's first push to the forge stored it, and it is only ever sent in an
Authorization header. Nothing prints it. Without one the script refuses and says how to store it.

HTTP goes through `curl.exe`, which on Windows reads the system's certificate store (schannel), as git does here
(`http.sslBackend=schannel`, the AVG interception): Python's own TLS would not trust the same chain.

Prints what it did and stops; exit 1 on any failure.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

FACTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITHUB_REPO = "siliconight/gabagool_factory"
FORGE_HOST = "forge.internal.vaultinteractive.net"
FORGE_REPO = "BMONEY/gabagool_factory"
FORGE_URL = "https://%s/%s.git" % (FORGE_HOST, FORGE_REPO)
API = "https://%s/api/v1/repos/%s" % (FORGE_HOST, FORGE_REPO)
BACKFILL_DIR = os.path.join(FACTORY, "_scratch", "release_backfill")


class Failed(Exception):
    pass


def run(cmd, dry, what, capture=False, cwd=FACTORY):
    print("  %s%s" % ("[dry] " if dry else "", what))
    if dry:
        return ""
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise Failed("%s: exit %d: %s" % (what, r.returncode, (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout if capture else ""


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def forge_token():
    """The walker's forge credential from Git Credential Manager, or a refusal saying how to store it."""
    r = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=%s\n\n" % FORGE_HOST,
                       capture_output=True, text=True, env=dict(os.environ, GIT_TERMINAL_PROMPT="0",
                                                                GCM_INTERACTIVE="never"))
    fields = dict(l.split("=", 1) for l in r.stdout.splitlines() if "=" in l)
    if r.returncode != 0 or not fields.get("password"):
        raise Failed("no forge credential in Git Credential Manager for %s. Store it once by pushing to the forge "
                     "yourself: git push %s main -- the username and an access token with repository write access "
                     "as the password" % (FORGE_HOST, FORGE_URL))
    return fields["password"]


def token_for(dry):
    """The credential; a dry run goes on without one, saying so, and reads nothing from the forge."""
    try:
        return forge_token()
    except Failed as e:
        if not dry:
            raise
        print("  [dry] %s -- going on as if the forge had no releases" % e)
        return None


def curl(token, method, url, *, data=None, form_file=None, out=None):
    """(status, body) from curl.exe; the token goes in a header read from a temp config, never on the command line."""
    cfg = tempfile.NamedTemporaryFile("w", suffix=".curlrc", delete=False, encoding="utf-8")
    try:
        cfg.write('header = "Authorization: token %s"\n' % token)
        cfg.close()
        cmd = ["curl.exe", "-sS", "-K", cfg.name, "-X", method, "-w", "\n%{http_code}", url]
        if data is not None:
            cmd += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
        if form_file is not None:
            cmd += ["-F", "attachment=@%s" % form_file]
        if out is not None:
            cmd += ["-L", "-o", out]
        r = subprocess.run(cmd, input=json.dumps(data) if data is not None else None, capture_output=True,
                           text=True)
        if r.returncode != 0:
            raise Failed("curl %s %s: exit %d: %s" % (method, url.split("?")[0], r.returncode, r.stderr.strip()))
        body, _sep, code = r.stdout.rpartition("\n")
        return int(code), body
    finally:
        os.unlink(cfg.name)


def forge_release(token, tag):
    if token is None:                               # a dry run with no credential stored yet: assume none there
        return None
    code, body = curl(token, "GET", "%s/releases/tags/%s" % (API, urllib.parse.quote(tag)))
    if code == 404:
        return None
    if code != 200:
        raise Failed("forge: reading release %s: HTTP %d" % (tag, code))
    return json.loads(body)


def publish_to_forge(token, tag, title, notes, zip_path, dry, want_sha=None):
    """The forge's release for `tag` with `zip_path` attached, its download held to the local sha256."""
    local = sha256(zip_path)
    if want_sha and local != want_sha:
        raise Failed("%s: the local zip's sha256 %s is not GitHub's %s" % (tag, local, want_sha))
    name = os.path.basename(zip_path)
    run(["git", "push", FORGE_URL, "refs/tags/%s:refs/tags/%s" % (tag, tag)], dry, "push tag %s to the forge" % tag)
    rel = None if dry else forge_release(token, tag)
    if rel is None:
        print("  %screate the forge release %s (%s)" % ("[dry] " if dry else "", tag, title))
        if not dry:
            code, body = curl(token, "POST", "%s/releases" % API,
                              data={"tag_name": tag, "name": title, "body": notes, "draft": False,
                                    "prerelease": False})
            if code != 201:
                raise Failed("forge: creating release %s: HTTP %d %s" % (tag, code, body[:300]))
            rel = json.loads(body)
    have = {a["name"]: a for a in (rel or {}).get("assets") or []}
    if name not in have:
        print("  %supload %s (%d bytes) to the forge" % ("[dry] " if dry else "", name, os.path.getsize(zip_path)))
        if not dry:
            code, body = curl(token, "POST", "%s/releases/%d/assets?name=%s" % (API, rel["id"],
                                                                                 urllib.parse.quote(name)),
                              form_file=zip_path)
            if code != 201:
                raise Failed("forge: uploading %s: HTTP %d %s" % (name, code, body[:300]))
            have[name] = json.loads(body)
    if dry:
        return
    back = os.path.join(tempfile.mkdtemp(prefix="forge_check_"), name)
    try:
        code, _ = curl(token, "GET", have[name]["browser_download_url"], out=back)
        got = sha256(back) if code == 200 and os.path.exists(back) else None
    finally:
        shutil.rmtree(os.path.dirname(back), ignore_errors=True)
    if got != local:
        raise Failed("%s: the forge's %s reads sha256 %s, the local zip %s" % (tag, name, got, local))
    print("  the forge's %s is the local zip, sha256 %s" % (name, local))


def new_release(a):
    zip_path = os.path.abspath(a.zip)
    notes_path = os.path.join(FACTORY, a.notes) if not os.path.isabs(a.notes) else a.notes
    for p in (zip_path, notes_path):
        if not os.path.isfile(p):
            raise Failed("no such file: %s" % p)
    title = "Gabagool Factory %s" % a.tag[len("factory-v"):]
    notes = open(notes_path, encoding="utf-8").read()
    token = token_for(a.dry_run)
    print("%s: GitHub" % a.tag)
    run(["git", "push", "origin", "main"], a.dry_run, "push main to GitHub")
    run(["git", "push", "origin", "refs/tags/%s" % a.tag], a.dry_run, "push tag %s to GitHub" % a.tag)
    run(["gh", "release", "create", a.tag, zip_path, "-R", GITHUB_REPO, "--title", title, "--notes-file",
         notes_path], a.dry_run, "gh release create %s" % a.tag)
    print("%s: the forge" % a.tag)
    run(["git", "push", FORGE_URL, "main"], a.dry_run, "push main to the forge")
    publish_to_forge(token, a.tag, title, notes, zip_path, a.dry_run)


def backfill(a):
    out = run(["gh", "release", "list", "-R", GITHUB_REPO, "--limit", "100", "--json", "tagName"], False,
              "list GitHub's releases", capture=True)
    tags = [r["tagName"] for r in json.loads(out)]
    token = token_for(a.dry_run)
    run(["git", "push", FORGE_URL, "main"], a.dry_run, "push main to the forge")
    done = 0
    for tag in reversed(tags):                      # oldest first, so the forge lists them in GitHub's order
        rel = forge_release(token, tag)
        if rel is not None and rel.get("assets"):
            print("%s: on the forge already, %d asset(s)" % (tag, len(rel["assets"])))
            continue
        view = json.loads(run(["gh", "release", "view", tag, "-R", GITHUB_REPO, "--json",
                               "name,body,assets"], False, "read %s from GitHub" % tag, capture=True))
        zips = [x for x in view["assets"] if x["name"].endswith(".zip")]
        if len(zips) != 1:
            raise Failed("%s: GitHub has %d zip assets, not one" % (tag, len(zips)))
        z = zips[0]
        d = os.path.join(BACKFILL_DIR, tag)
        path = os.path.join(d, z["name"])
        print("%s: %s, %d bytes" % (tag, z["name"], z["size"]))
        if not os.path.isfile(path) or os.path.getsize(path) != z["size"]:
            os.makedirs(d, exist_ok=True)
            run(["gh", "release", "download", tag, "-R", GITHUB_REPO, "-p", z["name"], "-D", d, "--clobber"],
                a.dry_run, "download it from GitHub")
        want = (z.get("digest") or "").replace("sha256:", "") or None
        if a.dry_run and not os.path.isfile(path):
            print("  [dry] publish it to the forge, held to GitHub's sha256 %s" % want)
            continue
        publish_to_forge(token, tag, view["name"], view["body"], path, a.dry_run, want_sha=want)
        done += 1
    print("backfill: %d release(s) published to the forge%s" % (done, " -- dry run, nothing sent" if a.dry_run
                                                                  else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tag", nargs="?")
    ap.add_argument("--zip")
    ap.add_argument("--notes")
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.backfill:
            backfill(a)
        elif a.tag and a.zip and a.notes and a.tag.startswith("factory-v"):
            new_release(a)
        else:
            ap.error("a factory-v tag with --zip and --notes, or --backfill")
    except Failed as e:
        print("FAILED: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
