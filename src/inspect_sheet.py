import csv
from collections import Counter

with open("CS412 - Affective Computing Final PIT - Sheet.csv", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in sheet: {len(rows)}")
unique_urls = {}
for r in rows:
    u = (r.get("Source URL") or "").strip()
    p = (r.get("Platform") or "").strip()
    t = (r.get("Comment Text") or "").strip()
    cid = (r.get("Comment ID") or "").strip()
    if u and u.startswith("http"):
        if u not in unique_urls:
            unique_urls[u] = {"platform": p, "count": 0, "rows_with_text": 0, "first_id": cid}
        unique_urls[u]["count"] += 1
        if t:
            unique_urls[u]["rows_with_text"] += 1

print(f"Unique URLs found: {len(unique_urls)}")
platform_counts = Counter(d["platform"].lower() for d in unique_urls.values())
print("Platform counts of unique URLs:", platform_counts)

print("\nSample URLs by platform:")
for plat in ["reddit", "youtube", "facebook", "tiktok", "twitter"]:
    matches = [(u, d) for u, d in unique_urls.items() if d["platform"].lower() == plat]
    print(f"\n--- {plat.upper()} ({len(matches)} URLs) ---")
    for u, d in matches[:10]:
        print(f"  [{d['first_id']}] {u} (rows: {d['count']}, has text: {d['rows_with_text']})")
