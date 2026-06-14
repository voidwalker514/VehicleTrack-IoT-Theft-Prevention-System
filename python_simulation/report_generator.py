# ============================================================
# report_generator.py — Location History Report (CSV + PDF)
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# PURPOSE : Reads the location history CSV and generates:
#           1. A filtered/enriched CSV summary report
#           2. A PDF report (using fpdf2 library)
#
# Install : pip install fpdf2
# ============================================================

import csv
import os
from datetime import datetime
from config import CSV_LOG_PATH, PDF_REPORT_PATH


def _ensure_dir(path: str) -> None:
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)


def read_location_csv() -> list[dict]:
    """Read the location history CSV and return as list of dicts."""
    if not os.path.exists(CSV_LOG_PATH):
        print(f"[ReportGen] CSV not found: {CSV_LOG_PATH}")
        return []
    with open(CSV_LOG_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_summary_csv(records: list[dict]) -> str:
    """
    Write a human-friendly summary CSV to reports/ folder.
    Returns the output file path.
    """
    _ensure_dir("reports/")
    ts_tag  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"reports/summary_{ts_tag}.csv"

    fields = ["timestamp", "latitude", "longitude",
              "speed_kmph", "scenario", "alert_level",
              "alert_type", "alert_message", "maps_url"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print(f"[ReportGen] Summary CSV saved -> {out_path}")
    return out_path


def generate_pdf_report(records: list[dict]) -> str:
    """
    Generate a PDF location history report using fpdf2.
    Falls back gracefully if fpdf2 is not installed.

    Returns the output file path (or empty string on failure).
    """
    try:
        from fpdf import FPDF   # fpdf2 library
    except ImportError:
        print("[ReportGen] WARNING: fpdf2 not installed. Run: pip install fpdf2")
        print("[ReportGen] Skipping PDF generation.")
        return ""

    _ensure_dir(os.path.dirname(PDF_REPORT_PATH))

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Title ─────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_fill_color(30, 30, 60)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "IoT Vehicle Tracking & Theft Prevention System", ln=True, fill=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Location History Report - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.cell(0, 8, f"Total Records: {len(records)}", ln=True, align="C")
    pdf.ln(6)

    # ── Stats block ───────────────────────────────────────
    safe_n     = sum(1 for r in records if r.get("alert_level") == "SAFE")
    warning_n  = sum(1 for r in records if r.get("alert_level") == "WARNING")
    critical_n = sum(1 for r in records if r.get("alert_level") == "CRITICAL")

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Alert Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 7, f"  SAFE     : {safe_n}",     ln=True)
    pdf.cell(60, 7, f"  WARNING  : {warning_n}",  ln=True)
    pdf.cell(60, 7, f"  CRITICAL : {critical_n}", ln=True)
    pdf.ln(6)

    # ── Table header ──────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(50, 50, 120)
    pdf.set_text_color(255, 255, 255)
    col_w = [38, 22, 22, 20, 28, 22, 38]
    headers= ["Timestamp","Lat","Lon","Speed","Scenario","Level","Alert Type"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, h, border=1, fill=True, align="C")
    pdf.ln()

    # ── Table rows ────────────────────────────────────────
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    for idx, r in enumerate(records):
        fill = (idx % 2 == 0)
        pdf.set_fill_color(240, 240, 255) if fill else pdf.set_fill_color(255, 255, 255)
        level = r.get("alert_level", "")
        if   level == "CRITICAL": pdf.set_text_color(180, 0, 0)
        elif level == "WARNING" : pdf.set_text_color(160, 100, 0)
        else                    : pdf.set_text_color(0, 120, 0)

        row_vals = [
            r.get("timestamp",   "")[:19],
            r.get("latitude",    ""),
            r.get("longitude",   ""),
            r.get("speed_kmph",  ""),
            r.get("scenario",    "")[:18],
            r.get("alert_level", ""),
            r.get("alert_type",  ""),
        ]
        for i, val in enumerate(row_vals):
            pdf.cell(col_w[i], 6, str(val), border=1, fill=fill, align="C")
        pdf.ln()

    # ── Footer ────────────────────────────────────────────
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Generated by IoT Vehicle Tracking & Theft Prevention System | For academic use.", ln=True, align="C")

    pdf.output(PDF_REPORT_PATH)
    print(f"[ReportGen] PDF report saved -> {PDF_REPORT_PATH}")
    return PDF_REPORT_PATH


def generate_all_reports() -> None:
    """Master function: reads CSV and generates both CSV and PDF reports."""
    print("\n[ReportGen] Starting report generation...")
    records = read_location_csv()
    if not records:
        print("[ReportGen] No data to report. Run the simulation first.")
        return
    generate_summary_csv(records)
    generate_pdf_report(records)
    print("[ReportGen] SUCCESS: All reports generated.\n")


# --- Standalone test ---------------------------------------
if __name__ == "__main__":
    generate_all_reports()
