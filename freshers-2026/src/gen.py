"""Generate the poster hero artwork with Bria FIBO and download it."""
import json
import os
import sys
import time
import urllib.request

BASE = "https://engine.prod.bria-api.com"
UA = "BriaSkills/1.3.7"
HERE = os.path.dirname(os.path.abspath(__file__))


def api_key():
    p = os.path.expanduser("~/.bria/credentials")
    kv = dict(l.strip().split("=", 1) for l in open(p) if "=" in l)
    return kv["api_token"]


def post(path, payload, key):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"api_token": key, "Content-Type": "application/json",
                 "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def get(url, key):
    req = urllib.request.Request(url, headers={"api_token": key, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def generate(prompt, negative, out, aspect="4:3", resolution="4MP", seed=None,
             style="photoreal"):
    key = api_key()
    payload = {"prompt": prompt, "negative_prompt": negative,
               "aspect_ratio": aspect, "resolution": resolution,
               "style_id": style}
    if seed is not None:
        payload["seed"] = seed
    r = post("/v2/image/generate", payload, key)
    status_url = r.get("status_url")
    if not status_url:
        print("unexpected:", r)
        return None
    for _ in range(120):
        time.sleep(3)
        s = get(status_url, key)
        st = s.get("status")
        if st == "COMPLETED":
            url = s["result"]["image_url"]
            path = os.path.join(HERE, out)
            urllib.request.urlretrieve(url, path)
            print("SEED", s["result"].get("seed"))
            print("SAVED", path)
            return path
        if st in ("ERROR", "UNKNOWN"):
            print("FAILED:", json.dumps(s)[:600])
            return None
    print("TIMEOUT")
    return None


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    generate(spec["prompt"], spec.get("negative_prompt", ""), spec["out"],
             aspect=spec.get("aspect", "4:3"),
             resolution=spec.get("resolution", "4MP"),
             seed=spec.get("seed"), style=spec.get("style", "photoreal"))
