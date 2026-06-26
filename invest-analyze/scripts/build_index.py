# -*- coding: utf-8 -*-
"""
扫描 references/corpus/{manager}/*.md，解析 YAML frontmatter，
为每位经理生成 _index.json + 汇总 corpus_index.json。

用法：  python scripts/build_index.py
"""
import os, re, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.path.join(ROOT, "references", "corpus")


def parse_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    fm = {"title": "", "date": "", "source": "", "type": "", "body_chars": 0}
    if text.startswith("---"):
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if m:
            for line in m.group(1).strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    k, v = k.strip(), v.strip()
                    if k in fm:
                        fm[k] = v
    body = re.sub(r"^---.*?---\s*", "", text, 1, re.DOTALL)
    fm["body_chars"] = len(body.strip())
    if not fm["title"]:
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m:
            fm["title"] = m.group(1).strip()
    return fm


def main():
    EXCLUDE = {"基金经理手记", "媒体报道", "定期报告", "_archive"}
    managers = sorted([
        d for d in os.listdir(CORPUS)
        if os.path.isdir(os.path.join(CORPUS, d))
        and not d.startswith("_")
        and d not in EXCLUDE
    ])

    for manager in managers:
        mdir = os.path.join(CORPUS, manager)
        md_files = sorted(glob.glob(os.path.join(mdir, "*.md")))
        docs = []
        for path in md_files:
            fm = parse_frontmatter(path)
            docs.append({
                "type": fm.get("type", ""),
                "title": fm.get("title", ""),
                "date": fm.get("date", ""),
                "source": fm.get("source", ""),
                "body_chars": fm["body_chars"],
                "path": os.path.relpath(path, ROOT).replace("\\", "/"),
            })
        docs.sort(key=lambda d: d["date"] or "")
        idx_path = os.path.join(mdir, "_index.json")
        existing = {}
        if os.path.exists(idx_path):
            existing = json.load(open(idx_path, encoding="utf-8"))
        existing["documents"] = docs
        existing.setdefault("manager", manager)
        existing.setdefault("counts", {})
        existing["counts"]["语料"] = len(docs)
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"  [{manager}] {len(docs)} 篇 → _index.json")

    print(f"\n共 {len(managers)} 位经理，索引更新完成。")


if __name__ == "__main__":
    main()
