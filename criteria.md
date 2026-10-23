# Acceptance criteria — Unit 5 draft

Community: `comp.sys.ibm.pc.hardware` from the 20 Newsgroups archive.
Taxonomy: `troubleshooting_request`, `information_request`, and `technical_response_report`.

These are draft targets based on the taxonomy and the 20-post preview. Review them against the final 200 labeled posts **before training**; do not lower a target after seeing model results.

## 1. Overall accuracy

The model has at least **0.65 accuracy on each of the three seeds**.

**Why this target:** There are three labels, so a uniform guess is about 0.33. A 0.65 target requires the model to distinguish current hardware failures from general information questions and technical responses.

---

## 2. Macro F1

The model has at least **0.60 macro F1 on each seed**.

**Why this target:** Macro F1 gives each label equal weight. That matters because the preview has more information requests than troubleshooting posts, and accuracy alone could hide weak performance on the smaller class.

---

## 3. Per-label performance

Each label has an F1 of at least **0.50 on each seed**.

**Why this target:** The hardest distinction is between a request for help with a current fault and a general request for specifications or recommendations. A floor for every label checks that the model learned more than the most common category.

---

## 4. Label balance

In the final 200 rows, each label represents at least **20%** and no more than **60%** of the dataset.

**Why this target:** The 20-post preview is 50% information requests, 40% technical responses, and 10% troubleshooting requests. The final set needs more troubleshooting examples to meet this target; keeping all three labels within the stated range prevents one from dominating and leaves useful support in the stratified test split.

---

## 5. Confidence

Among test predictions with confidence of **0.80 or higher**, at least **70%** are correct.

**Why this target:** Confident predictions should be dependable enough to distinguish from uncertain cases. This is especially useful when the post describes both an existing fault and a request for general information.
