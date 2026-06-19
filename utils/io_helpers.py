from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from utils.logger import get_logger

log = get_logger("io_helpers")


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Escrita monolítica — compatível com todos os leitores."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    log.info("Salvo  %-55s  %6d linhas  %3d colunas", path.name, len(df), len(df.columns))


def write_parquet_partitioned(df: pd.DataFrame, base_dir: Path,
                               partition_cols: list[str]) -> None:
    """
    Escrita particionada usando PyArrow Dataset API.

    Produz estrutura Hive-style:
        base_dir/
          partition_col=valor_A/
            part-0.parquet
          partition_col=valor_B/
            part-1.parquet

    Vantagens:
    - Leitura com push-down de predicado (ex: WHERE data='2024-06-01')
    - Cada partição pode ser atualizada/deletada independentemente
    - Escalável para bilhões de linhas
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_to_dataset(
        table,
        root_path=str(base_dir),
        partition_cols=partition_cols,
        existing_data_behavior="overwrite_or_ignore",
    )
    n_parts = sum(1 for _ in base_dir.rglob("*.parquet"))
    log.info("Particionado %-45s  %6d linhas  %d partições  cols=%s",
             base_dir.name, len(df), n_parts, partition_cols)


def read_parquet(path: Path) -> pd.DataFrame:
    """Lê arquivo único ou diretório particionado."""
    if path.is_dir():
        df = pd.read_parquet(path)
    else:
        df = pd.read_parquet(path)
    log.info("Lido   %-55s  %6d linhas  %3d colunas", path.name, len(df), len(df.columns))
    return df
