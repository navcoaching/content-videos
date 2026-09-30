"""Resolve + download the licensed Mixkit clips used by the split reel (best available quality).
Usage: python3 split/fetch.py           -> downloads into split/src/<id>.mp4 and writes split/sources.json
Mixkit Stock Video Free License: commercial use + modification allowed, attribution appreciated (we credit it on screen)."""
import json, re, subprocess, os, sys, concurrent.futures as cf
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36"
HERE = os.path.dirname(os.path.abspath(__file__))
IDS = json.load(open(os.path.join(HERE, "clips_needed.json")))
os.makedirs(os.path.join(HERE, "src"), exist_ok=True)

def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, timeout=k.get("t", 60))

def status(url):
    r = sh("curl", "-sS", "-m", "25", "-A", UA, "-r", "0-1", "-o", "/dev/null", "-w", "%{http_code}", url)
    return r.stdout.decode()

def resolve(cid):
    # find the item page via Mixkit search-free path: slug unknown -> use meta from earlier scan
    meta = json.load(open(os.path.join(HERE, "meta.json")))[cid]
    page = sh("curl", "-sS", "-m", "30", "-L", "-A", UA, meta["url"]).stdout.decode("utf8", "ignore")
    m = re.search(r'"contentUrl":"(https://assets\.mixkit\.co/[^"]+?720\.mp4)"', page)
    base = m.group(1).replace("\\/", "/")
    best = None
    for q in ("2160", "1080", "720"):
        u = base.replace("720.mp4", f"{q}.mp4")
        if status(u) in ("200", "206"):
            best = (q, u); break
    lic = re.findall(r'"license":"https://mixkit.co/license/#(\w+)"', page)
    title = re.findall(r"<title>([^<]*)</title>", page)[0].replace(" - Free Stock Video", "")
    return cid, dict(quality=best[0], url=best[1], page=meta["url"], title=title, license=lic[0] if lic else None)

def download(cid, info):
    out = os.path.join(HERE, "src", f"{cid}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        return cid, True
    r = sh("curl", "-sS", "-m", "300", "-L", "-A", UA, "-o", out, "-w", "%{http_code}", info["url"], t=320)
    return cid, r.stdout.decode() == "200"

if __name__ == "__main__":
    res = {}
    with cf.ThreadPoolExecutor(6) as ex:
        for cid, info in ex.map(resolve, IDS):
            res[cid] = info
            print(cid, info["quality"], info["license"], info["title"][:60])
    json.dump(res, open(os.path.join(HERE, "sources.json"), "w"), ensure_ascii=False, indent=1)
    bad = [c for c, i in res.items() if i["license"] != "videoFree"]
    assert not bad, f"non-free license: {bad}"
    with cf.ThreadPoolExecutor(4) as ex:
        for cid, ok in ex.map(lambda kv: download(*kv), res.items()):
            print("downloaded", cid, ok)
