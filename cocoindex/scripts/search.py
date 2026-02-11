"""ベクトル検索でコードのエントリーポイントを発見する

使い方:
  uv run python search.py "<query>" [--top N]

テーブル名は --project-dir のベースネームから自動計算される。
共通設定は ~/.config/cocoindex/.env で管理:
  COCOINDEX_DATABASE_URL, VOYAGE_API_KEY
"""
import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
import psycopg2
import voyageai

CONFIG_DIR = Path.home() / ".config" / "cocoindex"
load_dotenv(dotenv_path=CONFIG_DIR / ".env")


def get_table_name(project_dir: str) -> str:
    """プロジェクトディレクトリからテーブル名を計算"""
    name = Path(project_dir).name
    sanitized = re.sub(r"[^a-zA-Z0-9]", "_", name)
    return f"codeindex_{sanitized}__code_chunks".lower()


def main():
    parser = argparse.ArgumentParser(description="ベクトル検索でコードを探索")
    parser.add_argument("query", help="自然言語クエリ")
    parser.add_argument("--project-dir", required=True, help="プロジェクトディレクトリ（絶対パス）")
    parser.add_argument("--top", type=int, default=5, help="表示件数（デフォルト: 5）")
    args = parser.parse_args()

    table_name = get_table_name(args.project_dir)
    db_url = os.environ.get("COCOINDEX_DATABASE_URL", "postgres://postgres:postgres@localhost:15432/postgres")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    client = voyageai.Client()
    result = client.embed([args.query], model="voyage-code-3", input_type="query")
    embedding = result.embeddings[0]
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    cur.execute(f"""
        SELECT DISTINCT ON (filename) filename,
               1 - (embedding::halfvec <=> %s::halfvec) AS similarity,
               chunk_text
        FROM {table_name}
        ORDER BY filename, embedding::halfvec <=> %s::halfvec
    """, (vec_str, vec_str))
    rows = cur.fetchall()
    rows.sort(key=lambda r: r[1], reverse=True)

    for fname, sim, text in rows[:args.top]:
        preview = text[:400].replace("\n", " ")
        print(f"[{sim:.3f}] {fname}")
        print(f"  {preview}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
