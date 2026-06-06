from __future__ import annotations

import json
import logging
from datetime import datetime

import pandas as pd

from .config import METADATA_FILE, PROCESSED_DIR

LOGGER = logging.getLogger(__name__)


def salvar_tabelas(tabelas: dict[str, pd.DataFrame], metadata: dict) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    tabelas["visao_geral"].to_parquet(PROCESSED_DIR / "visao_geral.parquet", index=False)
    tabelas["evolucao_semanal"].to_parquet(PROCESSED_DIR / "evolucao_semanal.parquet", index=False)
    tabelas["tendencia_notif"].to_parquet(PROCESSED_DIR / "tendencia_notif.parquet", index=False)
    tabelas["tendencia_conf"].to_parquet(PROCESSED_DIR / "tendencia_conf.parquet", index=False)
    tabelas["tendencia_mening"].to_parquet(PROCESSED_DIR / "tendencia_mening.parquet", index=False)

    metadata = {
        **metadata,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rows_after_filter": int(len(tabelas["evolucao_semanal"])),
        "files": [
            "visao_geral.parquet",
            "evolucao_semanal.parquet",
            "tendencia_notif.parquet",
            "tendencia_conf.parquet",
            "tendencia_mening.parquet",
            "faixa_etaria_*.parquet",
            "sexo_*.parquet",
            "sintomas_*.parquet",
            "evolucao_*.parquet",
        ],
    }

    METADATA_FILE.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Metadata salva em %s", METADATA_FILE)

