"""
FileOrganizer - 파일 자동 분류 스크립트
input/ 폴더의 파일을 config.json 규칙에 따라 output/ 폴더로 이동합니다.
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ── 경로 상수 ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
INPUT_DIR   = BASE_DIR / "input"
OUTPUT_DIR  = BASE_DIR / "output"


# ── 설정 로드 ─────────────────────────────────────────────
def load_config(path: Path) -> dict:
    """config.json을 읽어 규칙과 설정을 반환합니다."""
    if not path.exists():
        print(f"[ERROR] 설정 파일을 찾을 수 없습니다: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── 분류 로직 ─────────────────────────────────────────────
def classify_file(filename: str, rules: list) -> tuple[str, str]:
    """
    파일명을 규칙에 맞게 분류합니다.
    반환: (output_folder, matched_rule_name)
    """
    name = filename.lower()
    stem = Path(filename).stem.lower()
    ext  = Path(filename).suffix.lower()

    for rule in rules:
        rule_type = rule["type"]
        patterns  = [p.lower() for p in rule["patterns"]]

        if rule_type == "extension":
            if ext in patterns:
                return rule["output_folder"], rule["name"]

        elif rule_type == "prefix":
            if any(stem.startswith(p) or name.startswith(p) for p in patterns):
                return rule["output_folder"], rule["name"]

    return None, None  # 미분류


# ── 파일 이동 ─────────────────────────────────────────────
def move_file(src: Path, dest_dir: Path, overwrite: bool, dry_run: bool) -> tuple[bool, str]:
    """
    파일을 목적지 폴더로 이동합니다.
    반환: (성공 여부, 메시지)
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    # 중복 파일 처리
    if dest.exists() and not overwrite:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = dest_dir / f"{src.stem}_{timestamp}{src.suffix}"

    if dry_run:
        return True, f"[DRY-RUN] {src.name}  →  {dest_dir.name}/"

    try:
        shutil.move(str(src), str(dest))
        return True, f"  ✔  {src.name}  →  {dest_dir.name}/"
    except Exception as e:
        return False, f"  ✘  {src.name}  →  이동 실패 ({e})"


# ── 결과 리포트 ────────────────────────────────────────────
def print_report(stats: dict, errors: list, elapsed: float, dry_run: bool):
    """처리 결과를 보기 좋게 출력합니다."""
    total   = sum(stats.values())
    divider = "─" * 50

    print()
    print(divider)
    print("  📊  FileOrganizer 결과 리포트" + ("  [DRY-RUN]" if dry_run else ""))
    print(divider)

    if stats:
        print("  폴더별 이동 현황:")
        for folder, count in sorted(stats.items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 30)
            print(f"    {folder:<15}  {bar}  {count}개")
    else:
        print("  이동된 파일이 없습니다.")

    print(divider)
    print(f"  총 처리 파일  : {total}개")
    print(f"  성공         : {total - len(errors)}개")
    print(f"  실패         : {len(errors)}개")
    print(f"  소요 시간    : {elapsed:.3f}초")
    print(divider)

    if errors:
        print("  ⚠  오류 목록:")
        for err in errors:
            print(f"    {err}")
        print(divider)
    print()


# ── 메인 ──────────────────────────────────────────────────
def main():
    start = datetime.now()

    # 1. 설정 읽기
    config   = load_config(CONFIG_PATH)
    rules    = config.get("rules", [])
    settings = config.get("settings", {})

    overwrite        = settings.get("overwrite", False)
    dry_run          = settings.get("dry_run", False)
    unmatched_folder = settings.get("unmatched_folder", "others")

    # 2. input/ 폴더 확인
    if not INPUT_DIR.exists():
        INPUT_DIR.mkdir(parents=True)
        print(f"[INFO] input/ 폴더가 없어 생성했습니다: {INPUT_DIR}")

    files = [f for f in INPUT_DIR.iterdir() if f.is_file()]
    if not files:
        print("[INFO] input/ 폴더에 파일이 없습니다.")
        return

    print(f"\n[INFO] {len(files)}개 파일 처리 시작..." + (" (DRY-RUN 모드)" if dry_run else ""))
    print()

    # 3 ~ 5. 분류 → 폴더 생성 → 파일 이동
    stats  = defaultdict(int)
    errors = []

    for file in sorted(files):
        folder, rule_name = classify_file(file.name, rules)

        if folder is None:
            folder    = unmatched_folder
            rule_name = "미분류"

        dest_dir = OUTPUT_DIR / folder
        success, msg = move_file(file, dest_dir, overwrite, dry_run)

        print(msg)

        if success:
            stats[folder] += 1
        else:
            errors.append(msg)

    # 6. 결과 리포트
    elapsed = (datetime.now() - start).total_seconds()
    print_report(dict(stats), errors, elapsed, dry_run)


if __name__ == "__main__":
    main()
