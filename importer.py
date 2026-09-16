"""Messy CSV contribution importer for FairShare.

The importer is deliberately deterministic: it normalizes names and rupee
amounts, rejects unsafe rows, detects duplicate rows, and conservatively
merges obvious name variants. It does not use AI for financial data cleaning.
"""

import csv
import io
import re
from difflib import SequenceMatcher
from typing import Optional


NAME_HEADERS = {"name", "participant", "person", "payer", "paid by", "contributor"}
AMOUNT_HEADERS = {"amount", "paid", "payment", "contribution", "value", "amount paid"}
NOTE_HEADERS = {"note", "notes", "description", "remark", "remarks"}


def clean_name(value: object) -> str:
    """Trim/collapse whitespace while preserving the user's display casing."""
    return re.sub(r"\s+", " ", str(value or "")).strip()


def name_key(value: object) -> str:
    """Create a comparison key for a person's name."""
    text = clean_name(value).casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _name_similarity(a: str, b: str) -> float:
    """Conservative similarity score for obvious spelling variants."""
    ka, kb = name_key(a), name_key(b)
    if not ka or not kb:
        return 0.0
    if ka == kb:
        return 1.0

    seq = SequenceMatcher(None, ka, kb).ratio()
    at, bt = ka.split(), kb.split()
    if len(at) != len(bt) or len(at) == 0:
        return seq

    # Require the first-name initial and final-token initial to agree before
    # allowing fuzzy merging. This avoids merging unrelated people such as
    # "Riya Sharma" and "Riya Singh".
    if at[0][0] != bt[0][0] or at[-1][0] != bt[-1][0]:
        return 0.0

    token_scores = [SequenceMatcher(None, x, y).ratio() for x, y in zip(at, bt)]
    return 0.55 * seq + 0.45 * (sum(token_scores) / len(token_scores))


def parse_amount(value: object) -> Optional[float]:
    """Parse common rupee formats and return a positive amount."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    # Remove currency symbols/labels and thousands separators.
    text = re.sub(r"(?i)^(?:rs\.?|inr)\s*", "", text)
    text = text.replace("₹", "").replace(",", "").strip()
    text = text.replace(" ", "")

    # Reject anything that isn't a simple non-negative decimal number.
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", text):
        return None

    amount = round(float(text), 2)
    if amount <= 0:
        return None
    return amount


def _pick_column(fieldnames: list[str], candidates: set[str]) -> Optional[str]:
    normalized = {re.sub(r"\s+", " ", f.strip().casefold()): f for f in fieldnames}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def _canonical_for(raw_name: str, known_names: list[str]) -> tuple[str, Optional[dict]]:
    """Return canonical display name and merge metadata, if any."""
    key = name_key(raw_name)
    for existing in known_names:
        if name_key(existing) == key:
            return existing, {"raw": raw_name, "canonical": existing, "reason": "case/spacing normalization"}

    best_name = None
    best_score = 0.0
    for existing in known_names:
        score = _name_similarity(raw_name, existing)
        if score > best_score:
            best_name, best_score = existing, score

    if best_name is not None and best_score >= 0.90:
        return best_name, {
            "raw": raw_name,
            "canonical": best_name,
            "reason": f"close spelling match ({best_score:.0%})",
        }

    return raw_name, None


def parse_csv(text: str, existing_names: list[str] | None = None) -> dict:
    """Clean a CSV and return rows ready for insertion plus an audit report.

    Duplicate detection is intentionally based on normalized person + amount
    + note. Two separate payments by the same person for the same amount are
    therefore allowed when their notes differ (or they occur as separate
    legitimate rows).
    """
    existing_names = list(existing_names or [])
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))

    if not reader.fieldnames:
        return {
            "rows_found": 0,
            "imported": 0,
            "duplicates": 0,
            "merged": 0,
            "rejected": 0,
            "import_rows": [],
            "duplicates_detail": [],
            "merged_detail": [],
            "rejected_detail": [{"row": 1, "reason": "CSV has no header row"}],
        }

    name_col = _pick_column(reader.fieldnames, NAME_HEADERS)
    amount_col = _pick_column(reader.fieldnames, AMOUNT_HEADERS)
    note_col = _pick_column(reader.fieldnames, NOTE_HEADERS)

    if not name_col or not amount_col:
        return {
            "rows_found": 0,
            "imported": 0,
            "duplicates": 0,
            "merged": 0,
            "rejected": 0,
            "import_rows": [],
            "duplicates_detail": [],
            "merged_detail": [],
            "rejected_detail": [{
                "row": 1,
                "reason": "CSV must contain a name column and an amount column",
            }],
        }

    known_names = list(existing_names)
    seen = set()
    import_rows = []
    duplicates_detail = []
    merged_detail = []
    rejected_detail = []
    rows_found = 0

    for row_number, row in enumerate(reader, start=2):
        # Completely blank lines aren't meaningful data rows.
        if not any(str(v or "").strip() for v in row.values()):
            continue
        rows_found += 1

        raw_name = clean_name(row.get(name_col, ""))
        raw_amount = str(row.get(amount_col, "") or "").strip()
        note = clean_name(row.get(note_col, "")) if note_col else ""

        if not raw_name:
            rejected_detail.append({"row": row_number, "reason": "missing name"})
            continue

        amount = parse_amount(raw_amount)
        if amount is None:
            rejected_detail.append({
                "row": row_number,
                "name": raw_name,
                "reason": f"invalid amount: {raw_amount or '(empty)'}",
            })
            continue

        canonical, merge = _canonical_for(raw_name, known_names)
        if merge and name_key(raw_name) != name_key(canonical):
            merged_detail.append({"row": row_number, **merge})
        elif merge:
            # Exact case/spacing normalization is useful to report too.
            merged_detail.append({"row": row_number, **merge})

        duplicate_key = (name_key(canonical), round(amount, 2), note.casefold())
        if duplicate_key in seen:
            duplicates_detail.append({
                "row": row_number,
                "name": canonical,
                "amount": amount,
                "reason": "duplicate contribution row",
            })
            continue

        seen.add(duplicate_key)
        import_rows.append({"name": canonical, "amount": amount, "note": note})
        if not any(name_key(n) == name_key(canonical) for n in known_names):
            known_names.append(canonical)

    return {
        "rows_found": rows_found,
        "imported": len(import_rows),
        "duplicates": len(duplicates_detail),
        "merged": len(merged_detail),
        "rejected": len(rejected_detail),
        "import_rows": import_rows,
        "duplicates_detail": duplicates_detail,
        "merged_detail": merged_detail,
        "rejected_detail": rejected_detail,
    }
