from pathlib import Path
from typing import Tuple

import pandas as pd


def load_data(full_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_storico = pd.read_excel(
        full_path,
        sheet_name="Storico",
        dtype={
            "Borsa": str,
            "Ticker": str,
            "Quote": int,
            "Prezzo (€)": float,
            "Commissioni": float,
        },
    ).rename(
        columns={
            "Borsa": "exchange",
            "Ticker": "ticker",
            "Data Operazione": "transaction_date",
            "Quote": "shares",
            "Prezzo (€)": "price",
            "Commissioni (€)": "fees",
        }
    )

    df_anagrafica = pd.read_excel(
        full_path, sheet_name="Anagrafica Titoli", dtype=str
    ).rename(
        columns={
            "Ticker": "ticker",
            "Nome ETF": "name",
            "Tipologia": "asset_class",
            "Macro Tipologia": "macro_asset_class",
        }
    )

    return df_storico, df_anagrafica
