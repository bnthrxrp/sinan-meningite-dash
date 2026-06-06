from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import pandas as pd

from .config import BASE_DIR, LEGACY_CSV, RAW_DIR, RAW_PARQUET, SINAN_DISEASE

LOGGER = logging.getLogger(__name__)


def carregar_raw_local() -> pd.DataFrame:
    if RAW_PARQUET.exists():
        LOGGER.info("Carregando bruto local em parquet: %s", RAW_PARQUET)
        return pd.read_parquet(RAW_PARQUET)

    if LEGACY_CSV.exists():
        LOGGER.info("Carregando bruto legado em CSV: %s", LEGACY_CSV)
        try:
            return pd.read_csv(LEGACY_CSV, encoding="utf-8", low_memory=False, on_bad_lines="skip")
        except Exception:
            return pd.read_csv(LEGACY_CSV, encoding="latin1", low_memory=False, on_bad_lines="skip")

    raise FileNotFoundError(
        "Nenhuma base bruta local encontrada. Procurei por "
        f"{RAW_PARQUET.name} e {LEGACY_CSV.name}."
    )


def _criar_db_path_temporario() -> str:
    tmp_dir = Path(tempfile.gettempdir()) / "pysus"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return str(tmp_dir / f"pysus_{os.getpid()}_{uuid4().hex}.db")


def tentar_extrair_com_pysus(anos: Iterable[int]) -> pd.DataFrame:
    try:
        from pysus.api import PySUSClient
    except Exception:
        PySUSClient = None

    if PySUSClient is None:  # pragma: no cover - depende do ambiente
        raise RuntimeError("PySUS nao esta instalado no ambiente.")

    async def _extrair() -> pd.DataFrame:
        cliente = PySUSClient(db_path=_criar_db_path_temporario())
        ftp = await cliente.get_ftp()
        datasets = await ftp.datasets()
        sinan = next((ds for ds in datasets if ds.name == "SINAN"), None)
        if sinan is None:
            raise RuntimeError("Dataset SINAN nao encontrado no PySUS.")

        frames: list[pd.DataFrame] = []
        for ano in anos:
            LOGGER.info("Baixando SINAN/Meningite via PySUS para o ano %s...", ano)
            arquivos = await sinan.search(year=int(ano))
            arquivos = [
                arquivo
                for arquivo in arquivos
                if getattr(getattr(arquivo, "group", None), "name", None) == SINAN_DISEASE
            ]

            if not arquivos:
                raise RuntimeError(f"Nenhum arquivo MENI encontrado para o ano {ano}.")

            for arquivo in arquivos:
                parquet = await cliente.download_to_parquet(arquivo)
                df_ano = await parquet.load()
                if not df_ano.empty:
                    df_ano["__ano_extracao"] = int(ano)
                    frames.append(df_ano)

        if not frames:
            raise RuntimeError("PySUS nao retornou dados para os anos solicitados.")

        return pd.concat(frames, ignore_index=True)

    return asyncio.run(_extrair())


def obter_base_bruta(anos: Iterable[int]) -> tuple[pd.DataFrame, dict]:
    anos = list(anos)
    try:
        df = tentar_extrair_com_pysus(anos)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(RAW_PARQUET, index=False)
        LOGGER.info("Bruto atualizado salvo em %s", RAW_PARQUET)
        return df, {
            "source": "pysus",
            "disease": SINAN_DISEASE,
            "years": anos,
            "raw_file": str(RAW_PARQUET.relative_to(BASE_DIR)),
        }
    except Exception as exc:
        LOGGER.warning("Extracao via PySUS falhou: %s", exc)
        LOGGER.info("Usando base bruta local como fallback.")
        df = carregar_raw_local()
        return df, {
            "source": "local",
            "disease": SINAN_DISEASE,
            "years": anos,
            "raw_file": str((RAW_PARQUET if RAW_PARQUET.exists() else LEGACY_CSV).relative_to(BASE_DIR)),
        }
