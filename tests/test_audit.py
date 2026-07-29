from disastertwin.audit import append_record, verify_log


def test_hash_chained_audit_log(tmp_path):
    path = tmp_path / "audit.jsonl"
    append_record(path, {"run": 1})
    append_record(path, {"run": 2})
    result = verify_log(path)
    assert result["valid"] is True
    assert result["record_count"] == 2
