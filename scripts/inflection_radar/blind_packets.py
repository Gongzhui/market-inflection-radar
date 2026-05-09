from pathlib import Path


PACKET_DIR = Path(__file__).resolve().parents[2] / "references" / "golden-packets"


def packet_ids() -> list[str]:
    if not PACKET_DIR.exists():
        return []
    return sorted(path.stem for path in PACKET_DIR.glob("*.md"))


def render_packet(case_id: str) -> str:
    path = _packet_path(case_id)
    body = path.read_text(encoding="utf-8").strip()
    return f"<!-- case_id: {case_id}; source: references/golden-packets/{path.name} -->\n\n{body}\n"


def write_packets(case_id: str, output_dir: str) -> list[Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    selected = packet_ids() if case_id == "all" else [case_id]
    paths: list[Path] = []
    for selected_id in selected:
        content = render_packet(selected_id)
        path = target_dir / f"{selected_id}.md"
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return paths


def _packet_path(case_id: str) -> Path:
    path = PACKET_DIR / f"{case_id}.md"
    if path.exists():
        return path
    valid = ", ".join(packet_ids())
    suffix = f" valid cases: {valid}, all" if valid else " no packet files found"
    raise KeyError(f"unknown case '{case_id}'.{suffix}")
