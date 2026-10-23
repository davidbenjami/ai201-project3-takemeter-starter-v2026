"""
Labelling helper for the 200 candidate posts.

Shows one post at a time, records your key press, writes back to
candidate_posts.csv after every single label so nothing is lost if you stop.

    python label_helper.py --rows 1-20    --mode review   # check the AI's work
    python label_helper.py --rows 21-40   --mode cold     # your unaided 20
    python label_helper.py --rows 41-200  --mode review   # after pre-labelling
    python label_helper.py --status                       # counts, no prompting
    python label_helper.py --export                       # write labels.csv

In cold mode the running tally is hidden on purpose: those 20 are meant to be
your unaided read of each post, not a balancing exercise.
"""

import argparse
import csv
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

CANDIDATES = Path("candidate_posts.csv")
DEFINITIONS = Path("label_definitions.txt")
EXPORT = Path("labels.csv")

MIN_ROWS = 150
MAX_SHARE = 0.70          # the brief's hard cap
BALANCE_MIN, BALANCE_MAX = 0.20, 0.60   # your criteria.md criterion 4


def load_labels():
    """Read the taxonomy from label_definitions.txt so there is one source of truth."""
    labels = {}
    for line in DEFINITIONS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        name, definition = line.split(":", 1)
        labels[name.strip()] = definition.strip()
    if not labels:
        sys.exit(f"No 'label: definition' lines found in {DEFINITIONS}.")
    return labels


def load_rows():
    with CANDIDATES.open(newline="") as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    """Write atomically — a crash mid-write must not eat the labels so far."""
    tmp = CANDIDATES.with_suffix(".csv.tmp")
    with tmp.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "note"])
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(CANDIDATES)


def source_id(note):
    """Keep the 'source post N' trace that every row carries."""
    match = re.search(r"source post \d+", note or "")
    return match.group(0) if match else ""


def parse_range(spec, total):
    match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", spec.strip())
    if not match:
        sys.exit("--rows wants something like 21-40")
    start, end = int(match.group(1)), int(match.group(2))
    if not (1 <= start <= end <= total):
        sys.exit(f"--rows must sit inside 1-{total}")
    return start, end


def show(row, number, total_in_range, mode, labels):
    width = min(shutil.get_terminal_size((80, 24)).columns, 100)
    print("\n" + "=" * width)
    print(f"  Row {number}   ({total_in_range} left in this pass)   {source_id(row['note'])}")
    print("=" * width)
    print(row["text"].strip())
    print("-" * width)
    if mode == "review" and row["label"]:
        print(f"  Suggested: {row['label']}   —  press Enter to accept it\n")
    for i, (name, definition) in enumerate(labels.items(), 1):
        print(f"  [{i}] {name}")
        print(f"      {definition}")
    print("  [s] skip   [q] save and quit")


def run_pass(rows, start, end, mode, labels):
    names = list(labels)
    targets = [i for i in range(start - 1, end) if mode == "review" or not rows[i]["label"]]
    if not targets:
        print(f"Nothing to do in rows {start}-{end}.")
        return

    print(f"\n{len(targets)} posts to label in rows {start}-{end}, mode: {mode}.")
    if mode == "cold":
        print("Unaided pass — no suggestions shown, no running tally.")

    done = 0
    for position, index in enumerate(targets):
        row = rows[index]
        show(row, index + 1, len(targets) - position, mode, labels)

        while True:
            choice = input("  > ").strip().lower()
            if choice == "q":
                print(f"\nSaved. {done} labelled this pass.")
                return
            if choice == "s":
                break
            if choice == "" and mode == "review" and row["label"]:
                choice = str(names.index(row["label"]) + 1)
            if choice in {str(i) for i in range(1, len(names) + 1)}:
                picked = names[int(choice) - 1]
                was = row["label"]
                row["label"] = picked
                trace = source_id(row["note"])
                if mode == "cold":
                    row["note"] = f"cold; labelled unaided; {trace}".rstrip("; ")
                elif was and was == picked:
                    row["note"] = f"AI pre-label; reviewed, kept; {trace}".rstrip("; ")
                elif was:
                    row["note"] = f"AI pre-label; reviewed, changed from {was}; {trace}".rstrip("; ")
                else:
                    row["note"] = f"labelled by me; {trace}".rstrip("; ")
                save_rows(rows)
                done += 1
                if mode != "cold":
                    tally = Counter(r["label"] for r in rows if r["label"])
                    print("  so far: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
                break
            print("  Pick a number, or s to skip, or q to quit.")

    print(f"\nPass complete. {done} labelled.")


def report(rows, labels):
    labelled = [r for r in rows if r["label"].strip()]
    total = len(labelled)
    print(f"\n{total} of {len(rows)} rows labelled.")
    if not total:
        return [], []

    counts = Counter(r["label"] for r in labelled)
    print("\n  label                      count   share")
    for name in labels:
        count = counts.get(name, 0)
        print(f"  {name:<26} {count:>5}   {count / total:>5.0%}")

    problems, warnings = [], []
    unknown = set(counts) - set(labels)
    if unknown:
        problems.append(f"Labels not in label_definitions.txt: {sorted(unknown)}")

    for name, count in counts.items():
        share = count / total
        if share > MAX_SHARE:
            problems.append(f"'{name}' is {share:.0%} — over the brief's 70% cap.")
        elif not (BALANCE_MIN <= share <= BALANCE_MAX):
            warnings.append(
                f"'{name}' is {share:.0%} — outside the 20-60% band in criteria.md criterion 4."
            )
    for name in labels:
        if counts.get(name, 0) < 20:
            warnings.append(f"Only {counts.get(name, 0)} examples of '{name}' — its test split will be tiny.")

    blank = sum(1 for r in labelled if not r["text"].strip())
    if blank:
        problems.append(f"{blank} rows have empty text.")
    duplicates = len(labelled) - len({r["text"] for r in labelled})
    if duplicates:
        warnings.append(f"{duplicates} duplicate posts — that is leakage across splits.")
    if total < MIN_ROWS:
        problems.append(f"{total} rows — the submission floor is {MIN_ROWS}.")

    for p in problems:
        print(f"\n  [FIX ME]  {p}")
    for w in warnings:
        print(f"  [look at] {w}")
    if not problems and not warnings:
        print("\n  Clean.")
    return problems, warnings


def export(rows, labels):
    problems, _ = report(rows, labels)
    if problems:
        sys.exit("\nNot exporting while there are [FIX ME] items above.")
    labelled = [r for r in rows if r["label"].strip()]
    with EXPORT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "note"])
        writer.writeheader()
        writer.writerows(labelled)
    print(f"\nWrote {EXPORT}: {len(labelled)} rows. Commit it.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rows", help="inclusive 1-based range, e.g. 21-40")
    parser.add_argument("--mode", choices=["cold", "review"], default="review")
    parser.add_argument("--status", action="store_true", help="counts and checks only")
    parser.add_argument("--export", action="store_true", help="write labels.csv")
    args = parser.parse_args()

    if not CANDIDATES.exists():
        sys.exit(f"{CANDIDATES} not found. Run this from the project folder.")

    labels = load_labels()
    rows = load_rows()

    if args.export:
        export(rows, labels)
    elif args.status or not args.rows:
        report(rows, labels)
        if not args.status:
            print("\nNothing to do. Pass --rows 21-40 --mode cold to start labelling.")
    else:
        start, end = parse_range(args.rows, len(rows))
        run_pass(rows, start, end, args.mode, labels)
        report(rows, labels)


if __name__ == "__main__":
    main()
