"""Load test data into FitFinder.

    python seed.py              # replace all reviews with the 6 sample reviews
    python seed.py --bulk 100   # replace all reviews with 100 generated reviews
    python seed.py --clear      # delete all reviews
"""
import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone

from app import BUILDS, FIT_RATINGS, save_reviews

# Listed newest first, as they appear on the Browse page.
SAMPLES = [
    ("Levi's", "501 Original Jeans", "30", 168, "Athletic", "Runs small"),
    ("Adidas", "Track Pants", "S", 165, "Athletic", "True to size"),
    ("Nike", "Dri-FIT Running Tee", "M", 175, "Slim", "True to size"),
    ("Zara", "Wide-Leg Trousers", "8", 162, "Curvy", "Runs large"),
    ("H&M", "Oversized Hoodie", "L", 180, "Average", "Runs large"),
    ("Uniqlo", "Cotton Tee", "XL", 170, "Plus Size", "True to size"),
]

BRANDS = ["Levi's", "Adidas", "Nike", "Zara", "H&M", "Uniqlo", "Gap", "Old Navy", "Patagonia", "Carhartt"]
ITEMS = ["Jeans", "Hoodie", "Running Tee", "Trousers", "Jacket", "Joggers", "Polo Shirt", "Shorts", "Sweater"]
SIZES = ["XS", "S", "M", "L", "XL", "28", "30", "32", "34", "6", "8", "10"]


def make(brand, item, size, height, build, fit, when):
    return {"id": uuid.uuid4().hex, "brand": brand, "item": item, "size": size,
            "height": height, "build": build, "fit": fit, "created": when.isoformat()}


def build_reviews(count=None, seed=361):
    now = datetime.now(timezone.utc)
    reviews = []
    if count is None:
        # Oldest first in the file, so the first sample ends up newest on screen.
        for i, s in enumerate(reversed(SAMPLES)):
            reviews.append(make(*s, now - timedelta(minutes=len(SAMPLES) - i)))
        return reviews
    rng = random.Random(seed)
    for i in range(count):
        reviews.append(make(rng.choice(BRANDS), rng.choice(ITEMS), rng.choice(SIZES),
                            rng.randint(145, 200), rng.choice(BUILDS), rng.choice(FIT_RATINGS),
                            now - timedelta(minutes=count - i)))
    return reviews


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--bulk", type=int, metavar="N", help="generate N random reviews")
    parser.add_argument("--clear", action="store_true", help="delete all reviews")
    args = parser.parse_args()

    if args.clear:
        save_reviews([])
        print("Cleared all reviews.")
    elif args.bulk:
        save_reviews(build_reviews(args.bulk))
        print(f"Saved {args.bulk} generated reviews.")
    else:
        save_reviews(build_reviews())
        print(f"Saved {len(SAMPLES)} sample reviews.")
