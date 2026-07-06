from deploylens.cost import parse_cpu, parse_memory_gib


def test_parse_cpu_millicores() -> None:
    assert parse_cpu("250m") == 0.25


def test_parse_memory_mebibytes() -> None:
    assert parse_memory_gib("512Mi") == 0.5
