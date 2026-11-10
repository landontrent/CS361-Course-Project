# FitFinder (Milestone #1)

A community web app where shoppers post how clothing fits their bodies (height, build, size, fit rating) and browse and filter reviews from people with a similar body type before they buy.

Built with Python and Flask. Reviews are saved in `data/reviews.json`.

## Run it (VS Code terminal)

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
python seed.py                  # load 6 sample reviews (optional)
python app.py
```

Open http://127.0.0.1:5000

## Useful commands

| Command | What it does |
|---|---|
| `python seed.py` | Replace all reviews with the 6 sample reviews |
| `python seed.py --bulk 100` | Replace all reviews with 100 generated reviews (for the Responsiveness demo) |
| `python seed.py --clear` | Delete all reviews |
| `python -m unittest -v` | Run the automated acceptance-criteria tests (15 tests) |

## User stories and acceptance criteria

**Submit Fit Review.** As a shopper, I want to submit a review of how a clothing item fit me, so that other shoppers can learn from my experience.
Given I am on the Submit Review page with brand, item, size, height in cm, build, and fit rating filled in, when I click "Submit Review," then the review is saved and "Review submitted" appears.

**Browse Fit Reviews.** As a shopper, I want to browse reviews from other users, so that I can see how clothing fits real people before I buy.
Given at least 3 reviews have been submitted, when I open the Browse page, then I see each review's brand, item, size, height, build, and fit rating.

**Filter by Similar Build.** As a shopper, I want to filter reviews by height and build, so that I only see people with a body type similar to mine.
Given the Browse page shows reviews of different heights and builds, when I enter a height range of 160 to 170 cm, select "Athletic," and click "Apply Filter," then only reviews matching both are shown.

## Inclusivity Heuristics: where each one is

| IH | Where to find it |
|---|---|
| 1 Benefits | Banner on Browse ("See how clothes fit people with bodies like yours..."), and "Your review helps other shoppers choose with confidence." on the form |
| 2 Costs | Note under the form buttons: "Takes about 2 minutes and is free. Your height and build will be shown publicly, but we never ask for your name or email." |
| 3 Gather or avoid info | "What do these mean?" link next to Build opens the build guide; "Hide guide" closes it. Closed by default |
| 4 Familiar features | Retail-style layout: top bar, filter sidebar, grid of review cards, standard buttons and labels throughout |
| 5 Undo / backtrack | Clear Filter, Clear Form, Cancel, plus the notes "You can clear filters anytime." and "Clear or cancel anytime." |
| 6 Explicit path | "Four steps to finish" list on the form, and the "How to filter" 3-step list in the sidebar |
| 7 Different approaches | No-match view: widen the height range, or click "Clear Filter and browse all reviews" |
| 8 Tinker mindfully | "(required)" labels, "100 to 250 cm" height hint, inline red error messages that say what to fix |

## Quality attributes and non-functional criteria

- **Usability:** Each Inclusivity Heuristic is reflected, and every form field has a visible text label.
- **Confidentiality:** The form never asks for a name, email, or address, and every review is shown as "Posted by Anonymous."
- **Responsiveness:** With 100 saved reviews, the Browse page loads within 2 seconds. Run `python seed.py --bulk 100`, then open Browse. The footer shows the server build time, and the browser's developer tools (F12, Network tab) show the full load time.

## Demo script for the video (about 4 minutes)

Run `python seed.py` first so Browse has 6 reviews. Keep this script open while recording.

1. **Story 1, Submit Fit Review.** Read the story and its Given/When/Then. Click Write a Review, fill in Levi's / 501 Original Jeans / 30 / 168 / Athletic / Runs small, click Submit Review, and show "Review submitted." Click Back to reviews and show the new review at the top.
2. **Story 2, Browse Fit Reviews.** Read the story and criterion. Point at the cards: brand, item, size, height, build, fit rating.
3. **Story 3, Filter by Similar Build.** Read the story and criterion. Enter 160 to 170, choose Athletic, click Apply Filter, and show only the matching reviews. Click Clear Filter.
4. **IH 1 to 8.** Point at each element in the table above while you say what it does. Do IH7 by filtering 190 to 200 and Petite. Do IH8 by submitting the form with the brand empty and the height 30.
5. **Quality attributes.** State each attribute and its criterion, then show it:
   - Usability: say the IH demo covered it, and point out the labels on every field.
   - Confidentiality: show the form has no name, email, or address field, and the reviews say Anonymous.
   - Responsiveness: run `python seed.py --bulk 100`, reload Browse, and show the load time.
6. **GitHub release.** Open the repository's Releases page and show the release (for example v1.0.0).

## Create the GitHub release

1. Commit and push all the code. Check that `data/reviews.json` is not in the repo (it is in `.gitignore`).
2. On GitHub, open the repo, click **Releases** on the right, then **Create a new release**.
3. Click **Choose a tag**, type `v1.0.0`, and choose **Create new tag**.
4. Title it `Milestone #1`, then click **Publish release**.
