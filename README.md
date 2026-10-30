# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

This project classifies posts from the `comp.sys.ibm.pc.hardware` Usenet community. It separates requests to fix a current hardware problem from general hardware information requests and technical explanations or experience reports. The hardest boundary is whether a question is about a present malfunction or asks for general specs, compatibility, or buying advice.

## Label Taxonomy

### `troubleshooting_request`

**Definition:** Asks for help diagnosing or fixing a current hardware fault or malfunction.

**Example 1:** “I have a 386/40 motherboard with AMI BIOS… suddenly it's giving me 10 beeps when I turn the power on. It was working fine this morning… Anybody know what 10 beeps means?”

**Example 2:** “I have a WANGTEK tape controller card … and need to know the DMA, IRQ and address.”

### `information_request`

**Definition:** Asks for hardware instructions, specifications, compatibility, recommendations, or reference information without centering on a current fault.

**Example 1:** “Is there any book that show you how to fix your own PC?”

**Example 2:** “How much space will DoubleSpace allow me to have?”

### `technical_response_report`

**Definition:** Explains, answers, evaluates, argues about, or reports hardware experience without making a primary request for help.

**Example 1:** “I think it's simply because DOS doesn't use the IRQ for anything. OS/2 does…”

**Example 2:** “The joystick reads in analog values through a digital port. You send a command to the port to read it…”

### The hardest boundary

**Which two labels:** `troubleshooting_request` and `information_request`.

**The decision rule I used every time:** If the writer is trying to fix a fault that is happening to their current system, label it `troubleshooting_request`. If they want general specifications, compatibility, instructions, or product advice, label it `information_request` even if they mention their computer.

## The Dataset

**Where the posts came from:** The 20 Newsgroups archive, `comp.sys.ibm.pc.hardware` group. The preview contains 20 posts; `candidate_posts.csv` contains 200 sampled candidate posts. Posts were fetched with scikit-learn's `fetch_20newsgroups` (training split, `remove=("headers", "footers", "quotes")`), filtered to posts of at least 40 characters, de-duplicated, and sampled with `random_state=42`.

**How I labelled them:** Rows 1–20 and 41–200 were AI pre-labelled under the definitions above, and every one is marked `AI pre-label` in the `note` column. I labelled rows 21–40 myself without help (cold), and they are marked `cold; labelled unaided`. `labels.csv` holds all 200 rows.

**Counts per label (`labels.csv`, 200 rows):**

| Label | Count | Share |
|---|---:|---:|
| `troubleshooting_request` | 52 | 26% |
| `information_request` | 71 | 36% |
| `technical_response_report` | 77 | 38% |
| **Total** | **200** | **100%** |

No label is above the 70% cap, and every label is inside the 20–60% band in criterion 4. Before my review, `troubleshooting_request` was only 14%: the AI pre-labels had filed 23 posts about a present fault as `information_request`. I moved them because my decision rule says so, not to hit the target.

**Off-topic posts:** For-sale ads were labelled `technical_response_report` because they make no request. "Wanted to buy" posts were labelled `information_request`.

**Three hard cases**

**1.**
> *The post:* A user describes a RAM upgrade and asks whether an expansion board would work.
>
> *Could have been:* `troubleshooting_request` or `information_request`
>
> *I chose:* `information_request`, because the computer is not failing; the writer asks about compatibility and an upgrade path.

**2.**
> *The post:* A reply explains the lines visible on Trinitron monitors and comments on a specific display.
>
> *Could have been:* `information_request` or `technical_response_report`
>
> *I chose:* `technical_response_report`, because it provides an explanation and experience without asking for information.

**3.**
> *The post:* A user is trying to restore a system from a tape controller but lacks its settings.
>
> *Could have been:* `information_request` or `troubleshooting_request`
>
> *I chose:* `troubleshooting_request`, because the missing settings block a current recovery task.

## The Training Run

**Status:** Retrained on the reviewed `labels.csv` (200 rows, after the 45 label changes described below) with notebook sections 1–5. The run wrote `results.json` and `test_split.csv`, replacing the earlier run on the pre-review labels.

**Hardware:** Apple Silicon GPU (`mps`), torch 2.14.1.

**Base model:** `distilbert-base-uncased`

**Settings:** 5 epochs, learning rate `5e-5`, batch size 16, max length 128, seed 42.

**What I changed from the defaults, and why:** I raised the epochs from 3 to 5 and the learning rate from `2e-5` to `5e-5`. A first run with the defaults on an earlier 180-row version of the data predicted almost every post as `information_request`. With only about 140 training posts, the default settings left the model too few update steps to learn the smaller labels.

**Split sizes (stratified 70/15/15):** train 139 · validation 31 · test 30.

| Label | Train | Val | Test |
|---|---:|---:|---:|
| `troubleshooting_request` | 36 | 8 | 8 |
| `information_request` | 49 | 11 | 11 |
| `technical_response_report` | 54 | 12 | 11 |

The review doubled `troubleshooting_request` in the test split from 4 posts to 8. That is still few enough that its F1 will move a lot between seeds.

**Results (seed 42, test split of 30):**

| Measure | Value |
|---|---:|
| Accuracy | 0.467 |
| Macro F1 | 0.357 |
| F1 — `troubleshooting_request` (n=8) | 0.000 |
| F1 — `information_request` (n=11) | 0.545 |
| F1 — `technical_response_report` (n=11) | 0.526 |
| Accuracy, most-confident third | 0.500 |
| Accuracy, least-confident third | 0.300 |

**What happened:** This run scored lower than the run on the pre-review labels (accuracy 0.733, macro F1 0.644). The model never predicted `troubleshooting_request`: 7 of the 8 test posts in that label went to `information_request`, and 6 of the 11 `technical_response_report` posts went there too. The training loss was still falling at epoch 5 (1.09 → 0.72, validation 1.06 → 0.84), so the model is underfitting rather than overfitting. My review moved 23 posts from `information_request` to `troubleshooting_request`, which put the hardest boundary into all three splits. The earlier score was higher partly because that boundary was mostly absent from the old test split. I am leaving the diagnosis and the fix for unit 6.

## How I Used AI

**Moment 1**

- *What I asked for:* Labels for a 20-post preview from `comp.sys.ibm.pc.hardware`.
- *What came back:* Suggested labels and reasons under the three draft definitions.
- *What I changed:* I marked every suggestion as AI pre-labelled and left it for my review; none is counted as cold.

**Moment 2**

- *What I asked for:* Clear definitions, boundary rules, and numeric acceptance criteria.
- *What came back:* Draft criteria for accuracy, macro F1, per-label F1, class balance, and confidence.
- *What I changed:* I tied the boundary rule to current hardware faults versus general information requests and noted that the final dataset needs more troubleshooting examples.

**Moment 3 (unit 6)**

- *What I asked for:* Help running the Unit 6 steps and drafting the write-up.
- *What came back:* Claude Code ran `baseline.py` (with my definitions, and with bare names) and the notebook's three-seed section before and after the fix, then drafted the Unit 6 sections from the result files.
- *What I changed:* I wrote my baseline prediction and committed it before the baseline ran. Claude showed me the 30 staff-set posts one at a time, and I chose every label without suggestions and before the staff file was opened. For each disagreement I decided who was right and which pile it belongs in, and Claude drafted the written reasoning from my decisions and the staff rules. I reviewed that wording.

**Pre-labelling disclosure:** 180 of the 200 rows in `labels.csv` are AI pre-labels (`candidate_posts.csv` rows 1–20 and 41–200), and I reviewed every one of them. I kept 135 and changed 45, and the `note` column records which (`AI pre-label; reviewed, kept` or `AI pre-label; reviewed, changed from <label>`). Most changes were on the hardest boundary: 23 `information_request` → `troubleshooting_request`, plus 9 `technical_response_report` → `information_request`, 6 `information_request` → `technical_response_report`, 4 `technical_response_report` → `troubleshooting_request`, 2 `troubleshooting_request` → `information_request`, and 1 `troubleshooting_request` → `technical_response_report`. The other 20 rows (21–40) are my own cold labels, marked `cold; labelled unaided`.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

Both columns are scored on the same 30 held-out posts in `test_split.csv`. The baseline is `facebook/bart-large-mnli` zero-shot, prompted with my three definitions from `label_definitions.txt`. The trained column is my Unit 5 `results.json` (seed 42, 5 epochs). Difference is Trained − Baseline.

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.433 | 0.467 | +0.033 |
| Macro F1 | 0.404 | 0.357 | -0.047 |
| F1 — `information_request` | 0.222 | 0.545 | +0.323 |
| F1 — `technical_response_report` | 0.615 | 0.526 | -0.089 |
| F1 — `troubleshooting_request` | 0.375 | 0.000 | -0.375 |

I also ran the baseline once with bare label names and no definitions (`baseline_results_bare_names.json`): accuracy **0.500**, macro F1 **0.451**.

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

The zero-shot baseline will beat my trained model. My Unit 5 model scored 0.467 accuracy and 0.357 macro F1 and never predicted `troubleshooting_request`, so a general model reading my three definitions should at least pick up posts that describe a current fault.

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->

My prediction was half right. The baseline beat the trained model on macro F1 (0.404 vs. 0.357) only because it found some `troubleshooting_request` posts (F1 0.375 vs. 0.000). The trained model still won on accuracy by one post (0.467 vs. 0.433). Its only clear win was `information_request`, and that comes from predicting `information_request` for 22 of the 30 posts, not from learning the label. **At 5 epochs, fine-tuning added nothing.** Both models are close to each other and not far above a uniform guess on three labels.

The bare-names run is the bigger surprise: it beat both. My definitions made the baseline *worse* overall (0.433 vs. 0.500). They doubled `troubleshooting_request` F1 (0.182 → 0.375) but wrecked `information_request` (0.545 → 0.222): with the definitions, 9 of the 11 real `information_request` posts were sent to another label (5 to `technical_response_report`, 4 to `troubleshooting_request`). My `information_request` definition lists so many things (instructions, specifications, compatibility, recommendations, reference information) that a general model doesn't recognise any single post as matching it.

---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

5 epochs, the Unit 5 settings. Seed 42 reproduces my Unit 5 `results.json` exactly. Trained on the Mac's Apple Silicon GPU (`mps`), as recorded in `results_three_seeds_before.json`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 on each seed | 0.467 | 0.467 | 0.533 | MISSED |
| 2. Macro F1 | ≥ 0.60 on each seed | 0.357 | 0.332 | 0.515 | MISSED |
| 3. Lowest per-label F1 | ≥ 0.50 for every label | 0.000 (`troubleshooting`) | 0.000 (`troubleshooting`) | 0.429 (`troubleshooting`) | MISSED |
| 4. Label balance | each label 20–60% | 26.0 / 35.5 / 38.5% | same | same | MET |
| 5. Confidence (most-confident third, accuracy) | ≥ 70% correct when confident | 0.50 | 0.80 | 0.70 | MISSED |

The notebook's spread table:

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.467 | 0.467 | 0.533 | 0.067 |
| Macro F1 | 0.357 | 0.332 | 0.515 | 0.183 |
| F1 — `troubleshooting_request` | 0.000 | 0.000 | 0.429 | 0.429 |
| F1 — `information_request` | 0.545 | 0.400 | 0.476 | 0.145 |
| F1 — `technical_response_report` | 0.526 | 0.595 | 0.640 | 0.114 |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

Seed 42, before:

| true \ predicted | troubleshooting_request | information_request | technical_response_report |
|---|---|---|---|
| **troubleshooting_request** | 0 | 7 | 1 |
| **information_request** | 0 | 9 | 2 |
| **technical_response_report** | 0 | 6 | 5 |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->

7 of the 8 real `troubleshooting_request` posts were called `information_request`, and 0 went the other way. The model didn't learn my hardest boundary at all: a post about a fault happening now gets filed as a general information request. The direction is entirely one way because the model never predicts `troubleshooting_request` on this seed. The other seeds fail differently: seed 7 sent 7 of 8 `troubleshooting_request` and 8 of 11 `information_request` posts to `technical_response_report`. When the model hasn't learned a boundary, it falls back to whichever label it happens to lean towards on that seed. The bare-names baseline made the same 7-of-8 `troubleshooting_request` → `information_request` mistake on these posts without any training.

---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy | ≥ 0.65 on each seed | MISSED | 0.467 / 0.467 / 0.533. Even the best seed is 0.117 short. |
| 2 | Macro F1 | ≥ 0.60 on each seed | MISSED | 0.357 / 0.332 / 0.515. No seed reaches it. |
| 3 | Per-label F1 | ≥ 0.50 for every label on each seed | MISSED | `troubleshooting_request` is 0.000 on two seeds and 0.429 on the third. |
| 4 | Label balance | each label 20–60% of the 200 rows | MET | 52 / 71 / 77 rows = 26.0 / 35.5 / 38.5%. This is a property of the dataset, so it is the same on every seed. |
| 5 | Confidence | ≥ 70% correct among predictions with confidence ≥ 0.80 | MISSED | The notebook records confidence by thirds, not at a 0.80 cut-off, so I used the most-confident third as the nearest measure: 0.50 / 0.80 / 0.70. It fails on seed 42. Mean confidence was only 0.40–0.55, so very few predictions can have reached 0.80 at all. |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->

**Criteria 1–3: an undertrained model, measured on too few posts, on a boundary that may be labelled inconsistently.**

1. **Not enough training (model problem).** Training loss was still falling at epoch 5 (1.09 → 0.72). Mean confidence was 0.40–0.55, barely above the 0.33 of a uniform guess over three labels. Seed 7 put almost everything into one label. A model that had learned the boundaries and still got them wrong would be confident and wrong; this one is unsure about everything. This is the cause I tested in Milestone 5.
2. **Too few posts to measure reliably (data problem).** The test split is 30 posts, with 8 `troubleshooting_request`. One post is 3.3 points of accuracy and can move that label's F1 by more than 0.1. After the fix, accuracy spread across seeds grew to 0.267. That means my criteria can't be called reliably from a 200-post dataset, whatever the model does.
3. **The `troubleshooting_request` / `information_request` boundary (labelling or genuinely hard — not yet settled).** The evidence points at this pair:
   - 23 of the 45 labels I changed during review moved from `information_request` to `troubleshooting_request`, so this is where the AI pre-labeller and I disagreed most.
   - The zero-shot model, with no training on my labels, made the same 7-of-8 error as my trained model.
   - Many troubleshooting posts are worded as questions, and my rule depends on whether the fault is happening *now*, which the wording doesn't always show.

   **What the agreement report adds: this is at least partly a labelling problem.** On the staff set I applied a written rule loosely on 5 of 30 posts (pile a). In every case I went by surface wording instead of the judgement the rule asked for. My own boundary needs exactly that kind of judgement, since the wording of a troubleshooting post and a general question often looks the same. So I expect some of my 200 labels on this pair are inconsistent. The 23 posts I moved across it during review are where that would show.
   - **Supporting this:** at 5 epochs the matrix was lopsided (7 → `information_request`, 0 back), and the notebook notes that lopsided usually points at labelling.
   - **Against it being *only* labelling:** at 15 epochs the confusion became roughly symmetric (3 one way, 5 the other), and the untrained baseline makes the same error. Both suggest the pair is also genuinely hard to separate from the wording alone.
   - **Limit:** the staff set uses a different taxonomy, so this is indirect evidence about how I label, not a re-check of my own 200 posts.

**Criterion 5: confidence that doesn't track correctness (model problem).** Before the fix, the model was unsure about everything. After 15 epochs, mean confidence rose to 0.80–0.89, but on seed 42 the model was *more* confident when wrong (0.878) than when right (0.797). Its most-confident third was correct only 30% of the time. With 140 training posts, more training made the model more confident without making it more accurate.

---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** 20 / 30 = 67%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

I labelled all 30 under `data/staff_taxonomy.md` before opening `data/staff_labels.csv`. Staff flagged 7 of the 30 as hard; 3 of my 10 disagreements (sp_005, sp_010, sp_014) are among them. Full output in `agreement_results.json`.

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.** `sp_002`
> *The post:* "I tracked sleep against session quality for eleven weeks. Under seven hours the next day's intervals were 6-8 seconds per mile slower, every time bar one. Small sample, one runner, but it's consistent enough that I've stopped scheduling hard days after late shifts."
>
> *Staff said / I said:* `analysis` / `reaction`
>
> *My call, and why:* **Staff is right.** The numbers (eleven weeks, 6–8 seconds per mile, every time bar one) are the whole reason for the conclusion, so the fact is load-bearing (rule 1). I read it as `reaction` because it is about the writer's own running. But the taxonomy never says whether a writer's private log counts as a "checkable" fact, when only the writer can check it.
>
> *Which pile:* (b): the definitions don't say whether a writer's own logged data counts as checkable.

**2.** `sp_003`
> *The post:* "The club championship scoring changed in 2019 from top-6 to top-10. Since then our B team has finished above the A team twice. That's not depth improving, it's the scoring rewarding turnout."
>
> *Staff said / I said:* `analysis` / `hot_take`
>
> *My call, and why:* **Staff is right.** A named date, a named rule change and a named result are all checkable, and the conclusion rests on them: without the 2019 change there is no argument. I treated "twice" as too small a number to carry anything, but rule 1 asks whether the fact does the work, not whether it is large.
>
> *Which pile:* (a): rule 1 covered it and I applied it loosely.

**3.** `sp_004`
> *The post:* "Everyone blames the hill at 18 miles. I split the field into people who ran the first half under 1:45 and over, and the slowdown after 18 was almost identical for both groups. If the hill were the problem the fast starters would fall apart harder."
>
> *Staff said / I said:* `analysis` / `hot_take`
>
> *My call, and why:* **I think my reading is defensible.** The `analysis` definition requires "a specific, checkable fact". The only number here, 1:45, just defines the two groups. The finding the argument rests on, that the slowdown was "almost identical", is given with no figure, so a reader can't check it. That is a confident conclusion resting on a result the writer asserts rather than shows, which matches `hot_take` ("a confident claim with no support offered"). Staff credit the method ("sets up a test"), but the definition asks for a checkable fact, not a sound method.
>
> *Which pile:* (c): the rule is ambiguous about a described test whose result isn't given as a number.

**4.** `sp_005`
> *The post:* "Carbon plates aren't the whole story. My times dropped 2% in the shoes and another 2% the following year in the same pair, when the only thing that changed was going from 35 to 50 miles a week."
>
> *Staff said / I said:* `analysis` / `reaction`
>
> *My call, and why:* **Staff is right.** The second sentence does the arguing: two comparable 2% drops, with mileage as the one variable that changed. That's rule 1's load-bearing fact. As with sp_002, I read one runner's own times as personal experience rather than evidence, and the taxonomy doesn't say which it is.
>
> *Which pile:* (b): the definitions don't say whether one runner's own data counts as checkable.

**5.** `sp_007`
> *The post:* "Ran the same loop in 4C and in 24C within a fortnight, same effort by heart rate. 90 seconds slower in the heat over six miles. People keep saying heat costs you 'a bit' and it's more than that."
>
> *Staff said / I said:* `analysis` / `reaction`
>
> *My call, and why:* **Staff is right.** The post reports a run, but it is a controlled comparison: same loop, same effort, two temperatures. Its point, that heat costs "more than a bit", rests on the 90 seconds. Rule 3 says the personal, recent framing doesn't outrank a load-bearing fact, and I let it.
>
> *Which pile:* (a): rule 3 covered it and I applied it loosely.

**6.** `sp_008`
> *The post:* "Went back through the club results going back to 2012. Every single year the number of people who enter the spring marathon and don't start it sits between 18 and 23 percent. It's not a bad-luck year, it's the base rate."
>
> *Staff said / I said:* `analysis` / `hot_take`
>
> *My call, and why:* **Staff is right.** The 18–23% range across thirteen years is exactly what argues against the "bad-luck year" explanation. Take the range away and nothing is left. I reacted to the confident closing line and missed that the number carries it.
>
> *Which pile:* (a): rule 1 covered it and I applied it loosely.

**7.** `sp_010`
> *The post:* "Three of us ran the same session on the same day, different shoes, within 10 seconds of each other over 5 miles. I'm not saying shoes do nothing, but whatever they do was smaller than the noise between three people."
>
> *Staff said / I said:* `analysis` / `reaction`
>
> *My call, and why:* **Staff is right.** The sample is tiny and the conclusion is hedged, but the observation (within 10 seconds over 5 miles) is checkable, and it is the only thing the claim rests on. Nothing in the definition says a small sample stops a fact being load-bearing. I treated "three of us" as a personal story.
>
> *Which pile:* (a): rule 1 covered it and I applied it loosely.

**8.** `sp_013`
> *The post:* "The club needs to stop pretending the Tuesday session is for everyone. It isn't and it never has been."
>
> *Staff said / I said:* `hot_take` / `reaction`
>
> *My call, and why:* **Staff is right.** Nothing just happened to the writer, so `reaction` doesn't fit. It is a confident, unsupported claim about the club. I read it as `reaction` because it sounds like frustration about the writer's own club, and rule 2 contrasts "the writer" with "the world" without saying where a local grievance falls.
>
> *Which pile:* (b): rule 2 doesn't say where a complaint about the writer's own club falls.

**9.** `sp_014`
> *The post:* "Times are down about 3% since the shoe rules changed, so obviously the shoes are the whole story and the sport has a problem."
>
> *Staff said / I said:* `hot_take` / `analysis`
>
> *My call, and why:* **Staff is right, and this is my clearest miss.** It is almost word-for-word the rule-1 worked example in `data/staff_taxonomy.md`: "so obviously" does the work, and the 3% is decoration on a conclusion already reached. I labelled it `analysis` because it contains a statistic, which is exactly the surface cue rule 1 warns against.
>
> *Which pile:* (a): rule 1 covered it, with a worked example, and I applied it loosely.

**10.** `sp_015`
> *The post:* "Marathon training plans are all the same plan with different fonts."
>
> *Staff said / I said:* `hot_take` / `reaction`
>
> *My call, and why:* **Staff is right.** It is a general claim about the world with no support, and nothing happened to the writer, so it can't be `reaction`. I took the joking tone as a feeling. The definitions don't say how to treat humour or sarcasm, but rule 2 still settles it once you ask whether the post is about the writer or the world.
>
> *Which pile:* (b): the definitions don't say how to treat a joke or aphorism.

**What the pattern in my disagreements tells me:**

- **Direction.** Seven of my ten disagreements are posts staff called `analysis` that I called something else. I used `analysis` only 4 times against staff's 10, and `reaction` 16 times against their 10. All 10 of their `reaction` posts I also called `reaction`. My mistakes run one way: I under-call the label that needs a judgement about whether a fact carries the argument. Instead I go by surface cues: first-person wording → `reaction`, a confident tone → `hot_take`, a number → `analysis` (sp_014).
- **Piles.** Five are pile (a): sp_003, sp_007, sp_008, sp_010 and sp_014. On those, a written rule covered the post, sp_014 even with a worked example, and I didn't apply it. Four are pile (b): sp_002, sp_005, sp_013 and sp_015. The real gap in the definitions is whether a writer's own measured data counts as "checkable". Only sp_004 is a win I would argue (c).
- **One honest caveat on my own piles.** sp_002, sp_005, sp_007 and sp_010 are the same kind of post: the writer's own measurements carrying the conclusion. I put two in (a) and two in (b). Even my adjudication isn't fully consistent on this type, which supports the main finding.

**What this means for my own 200 labels:** Five pile-(a) misses in 30 posts mean that, even with a written rule in front of me, I sometimes label by how a post *sounds* rather than what the rule asks. My own hardest rule is the same kind of judgement made beneath the surface: is the fault happening now, or is this a general question? That is where I expect the same slippage. It is consistent with my review moving 23 posts across exactly that boundary. See Diagnosis 3.

---

## The Improvement

**What I changed:** One setting: `EPOCHS` from 5 to 15 in `takemeter.ipynb`. Everything else is the same: labels, model, learning rate (5e-5), batch size (16), max length and seeds.

**Which diagnosis pointed at it:** Diagnosis 1, not enough training. Loss was still falling at epoch 5, confidence was close to a uniform guess, and one seed collapsed onto a single label. Of my three diagnoses, this was the only one I could test with a single change and no new labelling.

### Run Log — After

`results_three_seeds_after.json`, 15 epochs, same three seeds and splits, same `mps` device.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 on each seed | 0.367 | 0.567 | 0.633 | MISSED |
| 2. Macro F1 | ≥ 0.60 on each seed | 0.362 | 0.564 | 0.617 | MISSED |
| 3. Lowest per-label F1 | ≥ 0.50 for every label | 0.333 (`troubleshooting`) | 0.471 (`troubleshooting`) | 0.500 (`troubleshooting`) | MISSED |
| 4. Label balance | each label 20–60% | 26.0 / 35.5 / 38.5% | same | same | MET |
| 5. Confidence (most-confident third, accuracy) | ≥ 70% correct when confident | 0.30 | 0.70 | 0.70 | MISSED |

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.367 | 0.567 | 0.633 | 0.267 |
| Macro F1 | 0.362 | 0.564 | 0.617 | 0.255 |
| F1 — `troubleshooting_request` | 0.333 | 0.471 | 0.500 | 0.167 |
| F1 — `information_request` | 0.400 | 0.522 | 0.600 | 0.200 |
| F1 — `technical_response_report` | 0.353 | 0.700 | 0.750 | 0.397 |

Seed 42, after:

| true \ predicted | troubleshooting_request | information_request | technical_response_report |
|---|---|---|---|
| **troubleshooting_request** | 3 | 3 | 2 |
| **information_request** | 5 | 5 | 1 |
| **technical_response_report** | 2 | 6 | 3 |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->

**Partly, but no criterion changed from MISSED to MET.**

- **What improved:** Averaged over the three seeds, accuracy rose from 0.489 to 0.522, macro F1 from 0.401 to 0.514, and `troubleshooting_request` F1 from 0.143 to 0.435. The model now predicts `troubleshooting_request` on every seed instead of never. Seed 2024 meets criteria 2 and 3 and is 0.017 short on accuracy.
- **What got worse:** Seed 42 fell from 0.467 to 0.367 accuracy. The accuracy spread across seeds grew from 0.067 to 0.267, which the notebook flags as too unstable to trust.

So more epochs fixed the *undertraining*: the model now uses all three labels. It didn't fix the *boundary*. On seed 42, the troubleshooting/information confusion now runs both ways (3 one way, 5 the other) instead of 7 one way. A symmetric confusion like that suggests the pair is hard to separate from these posts, not that the model lacks training.

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

- **Criteria 1 and 2 (accuracy, macro F1).** Next I would label about 100 more posts, aimed at the troubleshooting/information boundary, and re-audit the 23 posts I moved across that boundary during review. I'd also report the average over more seeds, because with a 30-post test split one post moves accuracy by 3.3 points. I stopped because Milestone 5 allows one change, and labelling 100 posts is the larger job. The agreement report says re-auditing is worth it: five of my thirty staff-set disagreements were a rule I applied loosely.
- **Criterion 3 (per-label F1).** `troubleshooting_request` is still the weakest label on every seed (0.333–0.500). The fix is the same as for 1 and 2: more examples and a sharper rule. I'd rewrite the decision rule around a visible cue, such as "the writer describes a symptom on their own machine", instead of the writer's intent.
- **Criterion 5 (confidence).** More training made the model overconfident: on seed 42 it was more confident when wrong than when right. I'd stop training at the best validation epoch instead of a fixed count, and add the confidence count at the 0.80 cut-off to the notebook so the criterion can be measured directly. I stopped because that would be a second change.

**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->

I meant `troubleshooting_request` to capture a fault happening to the writer's machine right now, however the post is worded. The model instead learned roughly "is this post a question?": at 5 epochs it sent 7 of 8 troubleshooting posts to `information_request` and none the other way, and even at 15 epochs the two labels still swap 8 posts on seed 42.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
