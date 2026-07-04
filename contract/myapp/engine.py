"""
Core processing engine for the AI-Powered Contract Risk Analysis System.

Separated from views.py so that the deterministic rule-based risk logic
stays independent of the web layer, and can be unit tested / swapped out
(e.g. replacing the keyword matcher with a trained NER model) without
touching the views.
"""

import os
import re

from .models import ClauseRule

# -------------------------------------------------
# TEXT EXTRACTION
# -------------------------------------------------

def extract_text_from_file(file_path, file_type):
    """
    Extracts raw text (and page count where applicable) from an
    uploaded PDF, DOCX, or TXT file.
    """

    text = ""
    page_count = None

    if file_type == "pdf":

        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    elif file_type == "docx":

        import docx

        doc = docx.Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
        page_count = None

    elif file_type == "txt":

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    return text, page_count


# -------------------------------------------------
# CLAUSE DETECTION (NLP + RULE-BASED KEYWORD MATCHING)
# -------------------------------------------------

def detect_clauses(text):
    """
    Scans the extracted contract text for each known clause type using
    active ClauseRule keyword sets. Returns a list of clause result
    dicts, one per clause type, indicating whether it was found and an
    initial risk assessment.
    """

    results = []
    text_lower = text.lower() if text else ""

    # Clause types are now entirely admin-defined — pull the distinct
    # active types straight from ClauseRule instead of a hardcoded list.
    clause_types = list(
        ClauseRule.objects
        .filter(is_active=True)
        .values_list("clause_type", flat=True)
        .distinct()
    )

    for clause_type in clause_types:

        rules = ClauseRule.objects.filter(
            clause_type=clause_type,
            is_active=True
        )

        matched_snippet = None
        matched_rule = None

        # Keep a reference to a rule for this clause type even when no
        # keyword matches — needed so the "missing" branch can still
        # report the admin's configured risk_level_if_missing instead
        # of silently falling back to a hardcoded default.
        fallback_rule = rules.first()

        for rule in rules:

            # A rule's keyword field may hold a single term or a
            # comma-separated list (e.g. "confidentiality, nda, trade secret").
            # Match on ANY of them.
            keyword_variants = [
                kw.strip().lower()
                for kw in rule.keyword.split(",")
                if kw.strip()
            ]

            match = None

            for variant in keyword_variants:
                pattern = r"\b" + re.escape(variant) + r"\b"
                match = re.search(pattern, text_lower)
                if match:
                    break

            if match:
                start = max(match.start() - 100, 0)
                end = min(match.end() + 200, len(text))
                matched_snippet = text[start:end].strip()
                matched_rule = rule
                break

        if matched_snippet:

            risk_level, risk_reason, recommendation = assess_clause_risk(
                clause_type,
                matched_snippet
            )

            results.append({
                "clause_type": clause_type,
                "is_present": True,
                "clause_text": matched_snippet,
                "risk_level": risk_level,
                "risk_reason": risk_reason,
                "recommendation": recommendation
            })

        else:

            effective_rule = matched_rule or fallback_rule

            results.append({
                "clause_type": clause_type,
                "is_present": False,
                "clause_text": None,
                "risk_level": effective_rule.risk_level_if_missing if effective_rule else "high",
                "risk_reason": "Clause not found in contract text",
                "recommendation": f"Add a clearly defined {clause_type} clause."
            })

    return results


def assess_clause_risk(clause_type, clause_text):
    """
    Applies simple heuristic checks (vague language, missing figures,
    one-sided terms) to a detected clause and assigns Low / Medium /
    High risk. This is intentionally deterministic so results are
    reproducible and explainable to the user.
    """

    vague_terms = ["reasonable", "as needed", "from time to time", "may"]
    text_lower = clause_text.lower()

    vague_hits = sum(1 for term in vague_terms if term in text_lower)
    has_numbers = bool(re.search(r"\d", clause_text))

    if vague_hits >= 2 or not has_numbers:
        return (
            "medium",
            "Clause language is vague or lacks specific figures/timelines.",
            f"Clarify the {clause_type} clause with specific terms, durations, or amounts."
        )

    return (
        "low",
        "Clause appears clearly defined.",
        "No immediate action required; review periodically."
    )


def get_missing_clauses(detected_clauses):
    """
    Filters the clause detection results down to the clauses that were
    not found, along with the risk level and recommendation to
    surface in the report.
    """

    missing = []

    for clause in detected_clauses:
        if not clause["is_present"]:
            missing.append({
                "clause_type": clause["clause_type"],
                "risk_level": clause["risk_level"],
                "recommendation": clause["recommendation"]
            })

    return missing


# -------------------------------------------------
# OVERALL RISK SCORING
# -------------------------------------------------

RISK_WEIGHTS = {
    "low": 1,
    "medium": 5,
    "high": 10
}


def calculate_risk(detected_clauses, missing_clauses):
    """
    Combines per-clause risk levels into a single overall risk score
    (0-100) and Low/Medium/High rating.

    `detected_clauses` already contains one entry per evaluated clause
    type — present ones carry their assessed risk level, missing ones
    carry their configured risk_level_if_missing. `missing_clauses` is
    only used for the summary count; it must NOT be added into the
    weight sum again, since its entries are already included in
    `detected_clauses`.
    """

    total_weight = 0
    max_possible = len(detected_clauses) * RISK_WEIGHTS["high"]

    for clause in detected_clauses:
        total_weight += RISK_WEIGHTS.get(clause["risk_level"], 0)

    score = round((total_weight / max_possible) * 100, 2) if max_possible else 0

    if score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    summary = (
        f"{len(missing_clauses)} clause(s) missing out of "
        f"{len(detected_clauses)} evaluated. Overall risk score: {score}/100 ({level.upper()})."
    )

    return score, level, summary


# -------------------------------------------------
# REPORT GENERATION
# -------------------------------------------------

def generate_report_file(contract, report):
    """
    Renders a downloadable PDF/text summary report for the analyzed
    contract and returns the relative path to store on RiskReport.report_file.
    """

    from django.conf import settings

    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    file_name = f"report_{contract.id}.txt"
    file_path = os.path.join(reports_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Contract Risk Analysis Report\n")
        f.write(f"Contract: {contract.title}\n")
        f.write(f"Overall Risk Score: {report.overall_risk_score}/100\n")
        f.write(f"Overall Risk Level: {report.overall_risk_level.upper()}\n")
        f.write(f"Clauses Detected: {report.total_clauses_detected}\n")
        f.write(f"Missing Clauses: {report.missing_clauses_count}\n\n")
        f.write(f"Summary:\n{report.summary}\n")

    return f"reports/{file_name}"


# -------------------------------------------------
# OFFLINE AI CHATBOT
# -------------------------------------------------

def get_chatbot_response(user_message, contract=None):
    """
    Sends the user's question, along with contract context (extracted
    clauses/risk data), to a locally hosted LLM (e.g. served via
    Ollama / llama.cpp) and returns the generated explanation.

    Kept as a thin wrapper so the local model backend can be swapped
    without changing any view logic.
    """

    context_parts = []

    if contract:

        report = getattr(contract, "risk_report", None)

        if report:
            context_parts.append(
                f"Overall risk level: {report.overall_risk_level}, "
                f"score: {report.overall_risk_score}/100."
            )

        for clause in contract.clauses.filter(is_present=True):
            context_parts.append(
                f"{clause.clause_type}: {clause.risk_level} risk."
            )

    context_text = " ".join(context_parts)

    prompt = (
        "You are a contract-review assistant. Explain clearly and simply. "
        f"Contract context: {context_text}\n"
        f"User question: {user_message}"
    )

    try:
        # Example: local model call via an Ollama-style HTTP endpoint.
        import requests

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get("response", "").strip()

    except Exception:
        pass

    return (
        "I'm currently unable to reach the local AI model. "
        "Please make sure the offline assistant service is running."
    )