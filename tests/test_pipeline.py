import json
import subprocess
import sys


def test_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_synthetic_disaster_lab.py",
            "--zones",
            "8",
            "--facilities",
            "5",
            "--seed",
            "17",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)
    assert summary["synthetic_zone_count"] == 8
    assert (output_dir / "results" / "synthetic_disaster_response_summary.json").exists()
    assert (output_dir / "reports" / "synthetic_disaster_response_report.md").exists()
    assert (output_dir / "audit" / "disaster_response_audit_log.jsonl").exists()
    assert (output_dir / "figures" / "synthetic_scenario_comparison.png").exists()
