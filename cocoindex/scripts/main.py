"""汎用コードベースインデクサー

使い方:
  uv run python main.py <source_path> [--patterns "**/*.rb,**/*.py"] [--exclude "**/tmp/**"]
  uv run python main.py <source_path> --live  # 常駐モード（FlowLiveUpdater）

プロジェクト名は --name で指定する。
共通設定は ~/.config/cocoindex/.env で管理:
  COCOINDEX_DATABASE_URL, VOYAGE_API_KEY
"""
import argparse
import os
import re
import signal
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import cocoindex

CONFIG_DIR = Path.home() / ".config" / "cocoindex"
PID_DIR = Path.home() / ".claude" / "tmp"
load_dotenv(dotenv_path=CONFIG_DIR / ".env")


def get_project_name(name: str | None, source_path: str) -> str:
    """プロジェクト名を取得（--name 指定時はそれを使用、未指定時は source_path の親ディレクトリ名）"""
    if name:
        return name
    return Path(source_path).resolve().parent.name


def derive_flow_name(name: str) -> str:
    """インデックス名からフロー名を生成"""
    sanitized = re.sub(r"[^a-zA-Z0-9]", "_", name)
    return f"CodeIndex_{sanitized}"


def create_flow(source_path: str, index_name: str, included_patterns: list[str], excluded_patterns: list[str]):
    flow_name = derive_flow_name(index_name)

    @cocoindex.flow_def(name=flow_name)
    def code_index_flow(flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope):
        source_opts = {"path": source_path, "included_patterns": included_patterns}
        if excluded_patterns:
            source_opts["excluded_patterns"] = excluded_patterns

        data_scope["files"] = flow_builder.add_source(cocoindex.sources.LocalFile(**source_opts))

        code_chunks_collector = data_scope.add_collector()

        with data_scope["files"].row() as file:
            file["language"] = file["filename"].transform(
                cocoindex.functions.DetectProgrammingLanguage()
            )
            file["chunks"] = file["content"].transform(
                cocoindex.functions.SplitRecursively(),
                chunk_size=800,
                chunk_overlap=200,
            )
            with file["chunks"].row() as chunk:
                chunk["embedding"] = chunk["text"].transform(
                    cocoindex.functions.EmbedText(
                        api_type=cocoindex.LlmApiType.VOYAGE,
                        model="voyage-code-3",
                        task_type="document",
                    )
                )
                code_chunks_collector.collect(
                    filename=file["filename"],
                    language=file["language"],
                    chunk_text=chunk["text"],
                    embedding=chunk["embedding"],
                    generated_id=cocoindex.GeneratedField.UUID,
                )

        code_chunks_collector.export(
            "code_chunks",
            cocoindex.targets.Postgres(
                column_options={
                    "embedding": cocoindex.targets.PostgresColumnOptions(type="halfvec"),
                },
            ),
            primary_key_fields=["generated_id"],
            vector_indexes=[
                cocoindex.VectorIndexDef(
                    field_name="embedding",
                    metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
                )
            ],
        )

    return code_index_flow, flow_name


def write_pid_file(name: str) -> Path:
    """PIDファイルを書き出す"""
    pid_path = PID_DIR / f".pid_{name}"
    pid_path.write_text(str(os.getpid()))
    return pid_path


def remove_pid_file(name: str) -> None:
    """PIDファイルを削除する"""
    pid_path = PID_DIR / f".pid_{name}"
    try:
        pid_path.unlink(missing_ok=True)
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="コードベースのベクトルインデックスを構築")
    parser.add_argument("source_path", help="インデックス対象ディレクトリ（絶対パス）")
    parser.add_argument("--patterns", default="**/*.rb", help="対象ファイルパターン（カンマ区切り）")
    parser.add_argument("--exclude", default="", help="除外パターン（カンマ区切り）")
    parser.add_argument("--name", default=None, help="プロジェクト名（未指定時は source_path の親ディレクトリ名）")
    parser.add_argument("--live", action="store_true", help="FlowLiveUpdater で常駐モード起動")
    args = parser.parse_args()

    name = get_project_name(args.name, args.source_path)
    source_path = str(Path(args.source_path).resolve())
    included = [p.strip() for p in args.patterns.split(",")]
    excluded = [p.strip() for p in args.exclude.split(",") if p.strip()]

    cocoindex.init()
    flow, flow_name = create_flow(source_path, name, included, excluded)
    flow.setup()

    if args.live:
        sanitized = re.sub(r"[^a-zA-Z0-9]", "_", name)
        pid_path = write_pid_file(sanitized)

        shutdown = False

        def handle_sigterm(signum, frame):
            nonlocal shutdown
            shutdown = True

        signal.signal(signal.SIGTERM, handle_sigterm)

        try:
            print(f"Live updater started: {flow_name} (PID: {os.getpid()})")
            while not shutdown:
                flow.update()
                for _ in range(60):
                    if shutdown:
                        break
                    time.sleep(1)
        finally:
            remove_pid_file(sanitized)
            print(f"Live updater stopped: {flow_name}")
    else:
        flow.update()
        table_name = f"{flow_name}__code_chunks".lower()
        print(f"Done: {flow_name}")
        print(f"Table: {table_name}")


if __name__ == "__main__":
    main()
