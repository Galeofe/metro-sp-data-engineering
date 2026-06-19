"""
Qualidade de Dados — Validações entre camadas
Verifica completude, unicidade, ranges e tipos esperados.
Retorna um relatório consolidado por fonte e camada.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import pandas as pd
from utils.logger import get_logger

log = get_logger("quality")


@dataclass
class QualityResult:
    fonte:          str
    camada:         str
    total_registros: int
    checks:         List[dict] = field(default_factory=list)

    @property
    def passou(self) -> bool:
        return all(c["ok"] for c in self.checks if c.get("critico", False))

    def add(self, nome: str, ok: bool, detalhe: str = "", critico: bool = True):
        self.checks.append({"nome": nome, "ok": ok, "detalhe": detalhe, "critico": critico})
        icon = "OK" if ok else ("ERR" if critico else "WRN")
        log.info("  [%s] %s — %s", icon, nome, detalhe)


def check_completude(result: QualityResult, df: pd.DataFrame,
                     colunas: List[str], max_null_pct: float = 0.05):
    for col in colunas:
        if col not in df.columns:
            result.add(f"completude:{col}", False, f"coluna ausente", critico=True)
            continue
        null_pct = df[col].isna().mean()
        ok = null_pct <= max_null_pct
        result.add(
            f"completude:{col}", ok,
            f"{null_pct:.1%} nulos (limite={max_null_pct:.0%})",
            critico=True,
        )


def check_unicidade(result: QualityResult, df: pd.DataFrame, colunas: List[str]):
    dup = df.duplicated(subset=colunas).sum()
    ok  = dup == 0
    result.add("unicidade", ok, f"{dup} duplicatas em {colunas}", critico=True)


def check_range(result: QualityResult, df: pd.DataFrame,
                coluna: str, min_v: Optional[float], max_v: Optional[float]):
    if coluna not in df.columns:
        return
    serie = pd.to_numeric(df[coluna], errors="coerce").dropna()
    viola = 0
    if min_v is not None:
        viola += (serie < min_v).sum()
    if max_v is not None:
        viola += (serie > max_v).sum()
    ok = viola == 0
    result.add(
        f"range:{coluna}", ok,
        f"{viola} valores fora de [{min_v}, {max_v}]",
        critico=False,
    )


def check_enum(result: QualityResult, df: pd.DataFrame, coluna: str, valores: List[str]):
    if coluna not in df.columns:
        return
    invalidos = (~df[coluna].isin(valores)).sum()
    ok = invalidos == 0
    result.add(
        f"enum:{coluna}", ok,
        f"{invalidos} valores fora de {valores}",
        critico=True,
    )


# ── Validações específicas por fonte ────────────────────────────────────────

def validate_silver_traffic(df: pd.DataFrame) -> QualityResult:
    r = QualityResult("IoT Tráfego", "Silver", len(df))
    log.info("=== Validando Silver — Tráfego (%d reg) ===", len(df))
    check_completude(r, df, ["sensor_id", "timestamp_utc", "via", "qualidade"])
    check_unicidade(r, df, ["sensor_id", "timestamp_utc"])
    check_range(r, df, "velocidade_kmh", 0, 200)
    check_range(r, df, "ocupacao_pct",   0, 100)
    check_enum(r, df, "qualidade", ["OK", "SENSOR_MANUTENCAO", "VELOCIDADE_INFERIDA"])
    return r


def validate_silver_air(df: pd.DataFrame) -> QualityResult:
    r = QualityResult("Qualidade do Ar", "Silver", len(df))
    log.info("=== Validando Silver — Qualidade do Ar (%d reg) ===", len(df))
    check_completude(r, df, ["estacao_id", "timestamp_utc", "iqar"])
    check_unicidade(r, df, ["estacao_id", "timestamp_utc"])
    check_range(r, df, "iqar",     0, 400)
    check_range(r, df, "mp25",     0, 500)
    check_range(r, df, "umidade_pct", 0, 100)
    check_enum(r, df, "faixa_iqar",
               ["BOA", "MODERADA", "RUIM", "MUITO_RUIM", "PESSIMA", "INDISPONIVEL"])
    return r


def validate_silver_gps(df: pd.DataFrame) -> QualityResult:
    r = QualityResult("GPS Ônibus", "Silver", len(df))
    log.info("=== Validando Silver — GPS Ônibus (%d reg) ===", len(df))
    check_completude(r, df, ["prefixo", "linha", "timestamp_utc", "ativo"])
    check_range(r, df, "velocidade", 0, 120)
    check_enum(r, df, "lotacao", ["VAZIA", "MEIA", "CHEIA", "LOTADA", "DESCONHECIDA"])
    # motorista_id não deve existir (LGPD)
    tem_pii = "motorista_id" in df.columns
    r.add("lgpd:motorista_id_removido", not tem_pii,
          "motorista_id presente!" if tem_pii else "PII removido", critico=True)
    return r


def validate_silver_ouvidoria(df: pd.DataFrame) -> QualityResult:
    r = QualityResult("Ouvidoria", "Silver", len(df))
    log.info("=== Validando Silver — Ouvidoria (%d reg) ===", len(df))
    check_completude(r, df, ["id", "protocolo", "categoria", "lat", "lon"])
    check_unicidade(r, df, ["protocolo"])
    check_range(r, df, "prioridade", 1, 5)
    check_enum(r, df, "status", ["ABERTA", "EM_ANDAMENTO", "FECHADA"])
    # PII: nenhum CPF deve restar no texto
    if "descricao_anonimizada" in df.columns:
        import re
        tem_cpf = df["descricao_anonimizada"].dropna().apply(
            lambda t: bool(re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", t))
        ).sum()
        r.add("lgpd:cpf_removido", tem_cpf == 0,
              f"{tem_cpf} CPFs ainda visíveis", critico=True)
    return r


def print_report(resultados: List[QualityResult]):
    print()
    print("=" * 70)
    print("  RELATÓRIO DE QUALIDADE DE DADOS")
    print("=" * 70)
    for r in resultados:
        status = "PASSOU" if r.passou else "FALHOU"
        print(f"\n  [{status}] {r.fonte} — {r.camada}  ({r.total_registros:,} registros)")
        for c in r.checks:
            icon = "OK" if c["ok"] else ("ERR" if c.get("critico") else "WRN")
            print(f"         {icon} {c['nome']:<35} {c['detalhe']}")
    print()
    total = len(resultados)
    passaram = sum(1 for r in resultados if r.passou)
    print(f"  Resultado: {passaram}/{total} fontes dentro do SLA")
    print("=" * 70)
