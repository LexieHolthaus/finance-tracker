from __future__ import annotations
import os
import re
from pathlib import Path

import pandas as pd
import pdfplumber
import datetime as dt



def parse_boh_statement(path: str, account: str = "BoH Checking", institution: str = "Bank of Hawaii") -> pd.DataFrame:
    with pdfplumber.open(path) as pdf:
        # BoH transactions are in first 2 pages (DEBITS on p1, more + CREDITS on p2)
        text = "\n".join([(p.extract_text() or "") for p in pdf.pages[:2]])

        m = re.search(r"This statement:\s+([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text)
        if not m:
            raise ValueError("Could not find statement closing date in BoH PDF")
        stmt_month = dt.datetime.strptime(m.group(1), "%B").month
        stmt_year = int(m.group(3))

        lines = []
        for p in pdf.pages[:2]:
            t = p.extract_text() or ""
            lines.extend([ln.strip() for ln in t.splitlines() if ln.strip()])

    date_line = re.compile(r"^(\d{2})-(\d{2})\s+(.+?)\s+([\d,]+\.\d{2})$")
    rows = []
    i = 0
    while i < len(lines):
        mm = dd = None
        m = date_line.match(lines[i])
        if m:
            mm = int(m.group(1))
            dd = int(m.group(2))
            kind = m.group(3)
            amt = float(m.group(4).replace(",", ""))

            # Description continuation lines until next date record
            desc_parts = []
            j = i + 1
            while j < len(lines) and not date_line.match(lines[j]):
                # Skip obvious page markers/noise
                if not re.match(r"^PPaaggee\s+\d+\s+ooff\s+\d+$", lines[j]):
                    desc_parts.append(lines[j])
                # Stop if we hit section headers (some PDFs repeat letters)
                if "CREDITS" in lines[j] or "DEBITS" in lines[j]:
                    break
                j += 1

            desc = " ".join(desc_parts).strip()

            # Infer year: December entries may belong to previous year if statement is January
            year = stmt_year - 1 if (mm > stmt_month) else stmt_year
            date = dt.date(year, mm, dd)

            # Cashflow sign
            if "Debit" in kind or "POS Purchase" in kind:
                cashflow = -amt
            else:
                cashflow = amt

            rows.append(
                {
                    "date": pd.to_datetime(date),
                    "amount": cashflow,
                    "description": f"{kind} {desc}".strip(),
                    "institution": institution,
                    "account": account,
                    "source_file": os.path.basename(path),
                }
            )
            i = j
        else:
            i += 1

    return pd.DataFrame(rows)


_LINE = re.compile(
    r"^(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.+?)\s+(\d{4})\s+(\d{4})\s+(-?\d[\d,]*\.\d{2})$"
)

def _year_from_header(header_text: str) -> int | None:
    """
    Try to infer year from header. Prefer explicit dates like 02/07/26.
    Fall back to plausible 4-digit years (avoid last-4 like 7302).
    """
    # 1) Look for a statement date with 2-digit year
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{2})\b", header_text)
    if m:
        yy = int(m.group(3))
        return 2000 + yy if yy < 70 else 1900 + yy

    # 2) Look for plausible 4-digit years
    candidates = [int(x) for x in re.findall(r"\b(\d{4})\b", header_text)]
    candidates = [y for y in candidates if 2000 <= y <= 2100]
    return candidates[0] if candidates else None

def _year_from_filename(path: str) -> int | None:
    """
    Infer year from filenames like:
      eStmt_2026-02-07.pdf
      statement_2026_02.pdf
      boa-2026.pdf
    """
    name = Path(path).name

    # Common patterns: 2026-02-07, 2026_02_07, 2026.02.07
    m = re.search(r"\b(20\d{2})[-_.](\d{2})[-_.](\d{2})\b", name)
    if m:
        return int(m.group(1))

    # Year-month: 2026-02 / 2026_02
    m = re.search(r"\b(20\d{2})[-_.](\d{2})\b", name)
    if m:
        return int(m.group(1))

    # Just a year somewhere
    m = re.search(r"\b(20\d{2})\b", name)
    if m:
        return int(m.group(1))

    return None

def parse_boa_statement(path: str, account: str = "BoA Visa", institution: str = "Bank of America") -> pd.DataFrame:
    rows = []
    with pdfplumber.open(path) as pdf:
        header = (pdf.pages[0].extract_text() or "")

        year_file = _year_from_filename(path)
        year_head = _year_from_header(header)

        # Prefer filename year when available (it's not going to randomly be "7302" or "2050")
        if year_file is not None:
            # Only accept header year if it matches the filename year (or is off by 1 for weird statement cycles)
            if year_head is not None and abs(year_head - year_file) <= 1:
                year = year_head
            else:
                year = year_file
        else:
            year = year_head or 2026

        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                m = _LINE.match(line)
                if not m:
                    continue

                trans_date, post_date, desc, _ref, _acct_last4, amt = m.groups()

                # Use posting date for consistency
                date = pd.to_datetime(f"{post_date}/{year}", format="%m/%d/%Y", errors="coerce")
                statement_amt = float(amt.replace(",", ""))

                # Charges should be negative cashflow; credits/payments positive.
                # The statement amount is typically positive for charges; keep this convention:
                cashflow = -statement_amt

                rows.append(
                    {
                        "date": date,
                        "amount": cashflow,
                        "description": desc,
                        "institution": institution,
                        "account": account,
                        "source_file": os.path.basename(path),
                    }
                )

    return pd.DataFrame(rows).dropna(subset=["date"])