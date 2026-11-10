"""Automated checks for the Given/When/Then acceptance criteria.

Run with:  python -m unittest -v
"""
import tempfile
import time
import unittest
from pathlib import Path

import app as fitfinder
from seed import build_reviews

VALID = {"brand": "Levi's", "item": "501 Original Jeans", "size": "30",
         "height": "168", "build": "Athletic", "fit": "Runs small"}


class FitFinderTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        fitfinder.app.config["DATA_FILE"] = str(Path(self.tmp.name) / "reviews.json")
        fitfinder.app.config["TESTING"] = True
        self.client = fitfinder.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def load_samples(self):
        fitfinder.save_reviews(build_reviews())

    def get(self, url):
        return self.client.get(url).data.decode()


class SubmitFitReview(FitFinderTestCase):
    """Story 1: Submit Fit Review"""

    def test_valid_review_is_saved_and_confirmed(self):
        resp = self.client.post("/submit", data=VALID, follow_redirects=True)
        self.assertIn(b"Review submitted", resp.data)
        self.assertEqual(len(fitfinder.load_reviews()), 1)

    def test_missing_brand_is_rejected(self):
        resp = self.client.post("/submit", data={**VALID, "brand": ""})
        self.assertIn(b"Brand is required", resp.data)
        self.assertEqual(fitfinder.load_reviews(), [])

    def test_bad_height_is_rejected(self):
        for height in ["30", "251", "abc", "", "99"]:
            with self.subTest(height=height):
                resp = self.client.post("/submit", data={**VALID, "height": height})
                self.assertIn(b"Enter a height between 100 and 250 cm", resp.data)
                self.assertEqual(fitfinder.load_reviews(), [])

    def test_errors_keep_what_the_user_typed(self):
        resp = self.client.post("/submit", data={**VALID, "brand": ""})
        self.assertIn(b'value="501 Original Jeans"', resp.data)


class BrowseFitReviews(FitFinderTestCase):
    """Story 2: Browse Fit Reviews"""

    def test_browse_lists_every_review_with_details(self):
        self.load_samples()
        page = self.get("/")
        self.assertIn("Showing all 6 reviews", page)
        self.assertIn("Levi&#39;s 501 Original Jeans", page)
        self.assertIn("Size 30, 168 cm, Athletic", page)
        self.assertIn("Fit: Runs small", page)

    def test_browse_with_no_reviews_shows_empty_message(self):
        self.assertIn("No reviews yet", self.get("/"))


class FilterBySimilarBuild(FitFinderTestCase):
    """Story 3: Filter by Similar Build"""

    def test_filter_by_height_range(self):
        self.load_samples()
        # heights 168, 165, 162, 170 fall in 160-170
        self.assertIn("Showing 4 of 6 reviews", self.get("/?min=160&max=170"))

    def test_filter_by_height_and_build(self):
        self.load_samples()
        page = self.get("/?min=160&max=170&build=Athletic")
        self.assertIn("Showing 2 of 6 reviews", page)
        self.assertIn("Levi&#39;s 501 Original Jeans", page)
        self.assertIn("Adidas Track Pants", page)
        self.assertNotIn("Zara", page)

    def test_filter_with_no_matches_offers_a_way_out(self):
        self.load_samples()
        page = self.get("/?min=190&max=200&build=Petite")
        self.assertIn("No reviews match your filter", page)
        self.assertIn("Clear Filter and browse all reviews", page)

    def test_clear_filter_shows_everything_again(self):
        self.load_samples()
        self.assertIn("Showing all 6 reviews", self.get("/"))

    def test_bad_filter_input_shows_message_instead_of_crashing(self):
        self.load_samples()
        self.assertIn("Enter heights as whole numbers", self.get("/?min=abc&max=170"))


class QualityAttributes(FitFinderTestCase):
    def test_confidentiality_form_never_asks_for_identity(self):
        page = self.get("/submit").lower()
        page = page.replace("we never ask for your name or email", "")
        for word in ("email", "your name", 'name="name"', "address", "phone"):
            with self.subTest(word=word):
                self.assertNotIn(word, page)

    def test_confidentiality_reviews_are_anonymous(self):
        self.load_samples()
        self.assertEqual(self.get("/").count("Posted by Anonymous"), 6)

    def test_responsiveness_100_reviews_load_within_2_seconds(self):
        fitfinder.save_reviews(build_reviews(100))
        start = time.perf_counter()
        page = self.get("/")
        elapsed = time.perf_counter() - start
        self.assertIn("Showing all 100 reviews", page)
        self.assertLess(elapsed, 2.0)

    def test_usability_every_form_field_has_a_visible_label(self):
        page = self.get("/submit")
        for field_id in ("brand", "height", "item", "build", "size"):
            with self.subTest(field=field_id):
                self.assertIn(f'for="{field_id}"', page)


if __name__ == "__main__":
    unittest.main()
