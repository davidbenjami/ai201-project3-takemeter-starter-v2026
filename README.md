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

**Pre-labelling disclosure:** 180 of the 200 rows in `labels.csv` are AI pre-labels (`candidate_posts.csv` rows 1–20 and 41–200), and I reviewed every one of them. I kept 135 and changed 45, and the `note` column records which (`AI pre-label; reviewed, kept` or `AI pre-label; reviewed, changed from <label>`). Most changes were on the hardest boundary: 23 `information_request` → `troubleshooting_request`, plus 9 `technical_response_report` → `information_request`, 6 `information_request` → `technical_response_report`, 4 `technical_response_report` → `troubleshooting_request`, 2 `troubleshooting_request` → `information_request`, and 1 `troubleshooting_request` → `technical_response_report`. The other 20 rows (21–40) are my own cold labels, marked `cold; labelled unaided`.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

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

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



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
