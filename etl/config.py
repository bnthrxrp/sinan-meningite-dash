from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_PARQUET = RAW_DIR / "meningite_sinan.parquet"
LEGACY_CSV = RAW_DIR / "meningite_sinan.csv"
METADATA_FILE = PROCESSED_DIR / "metadata.json"

DEFAULT_START_YEAR = int(os.environ.get("SINAN_START_YEAR", "2025"))
DEFAULT_END_YEAR = int(os.environ.get("SINAN_END_YEAR", str(pd.Timestamp.today().year)))
SINAN_DISEASE = os.environ.get("SINAN_DISEASE", "MENI")

IBGE_PARA_UF = {
    11: "RO",
    12: "AC",
    13: "AM",
    14: "RR",
    15: "PA",
    16: "AP",
    17: "TO",
    21: "MA",
    22: "PI",
    23: "CE",
    24: "RN",
    25: "PB",
    26: "PE",
    27: "AL",
    28: "SE",
    29: "BA",
    31: "MG",
    32: "ES",
    33: "RJ",
    35: "SP",
    41: "PR",
    42: "SC",
    43: "RS",
    50: "MS",
    51: "MT",
    52: "GO",
    53: "DF",
}

TIPO_MENING = {
    1: "Meningococcemia",
    2: "Meningite Meningococica",
    3: "Mening. Meningococica c/ Meningococcemia",
    4: "Meningite Tuberculosa",
    5: "Outras Bacterias",
    6: "Meningite Nao Especificada",
    7: "Meningite Asseptica",
    8: "Outra Etiologia",
    9: "Meningite por Hemofilo",
    10: "Meningite por Pneumococo",
}

