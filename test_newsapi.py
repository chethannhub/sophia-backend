"""
Quick inspection script — run with:
  env/bin/python test_newsapi.py
"""
import sys, json, time
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv('.env')

from News_api.fetch_news import get_unified_news

print("=" * 60)
print("Calling get_unified_news() — fetches 3 categories")
print("=" * 60)
t0 = time.time()
result = get_unified_news("ai", "aiml")
elapsed = time.time() - t0

articles = result.get("Articles", [])
print(f"\nDone in {elapsed:.1f}s — {len(articles)} articles total\n")

# Show field completeness summary
fields = ["id", "title", "brief", "image", "content", "label", "author", "publishedAt", "source", "urls"]
print(f"{'Field':12} {'present':>8} {'missing':>8}")
print("-" * 32)
for f in fields:
    present = sum(1 for a in articles if a.get(f))
    missing = len(articles) - present
    print(f"{f:12} {present:>8} {missing:>8}")

# Show first article from each category
print()
seen_labels = set()
for a in articles:
    label = a.get("label")
    if label not in seen_labels:
        seen_labels.add(label)
        print(f"=== First article in [{label}] ===")
        print(json.dumps(a, indent=2))
        print()
