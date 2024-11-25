import requests
from bs4 import BeautifulSoup

import pandas as pd


def retrieve_sector(df_anagrafica: pd.DataFrame) -> pd.DataFrame:
    # retrieve page
    df_anagrafica["page_content"] = df_anagrafica["page_url"].apply(retrieve_page)

    # filter only Equity
    df_anagrafica = df_anagrafica[df_anagrafica["macro_asset_class"] == "Equity"]

    # based on macro asset class trigger the right function. Use switch case
    df_anagrafica["sector_data"] = (
        df_anagrafica.apply(
            lambda x: retrieve_etf_sector_data(x) if x["macro_asset_class"] == "Equity" else None,
            axis=1,
        )
    )

    # build a dataframe with the sector data
    df_sector = pd.DataFrame(
        df_anagrafica["sector_data"].apply(pd.Series).stack().reset_index(level=1, drop=True),
        columns=["sector_weight"],
    )

    return df_sector

def retrieve_page(url: str) -> bytes:
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
    )

    return response.content


def retrieve_etf_sector_data(etf_anagrafica: pd.Series) -> pd.Series:
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(etf_anagrafica["page_content"], "html.parser")

    # Initialize dictionary to hold sector data
    sector_data = {}

    # Locate the section containing sector weightings
    sector_section = soup.find("section", {"data-testid": "etf-sector-weightings-overview"})

    # Extract sector names and their corresponding weightings
    if sector_section:
        for content_div in sector_section.find_all("div", class_="content"):
            sector_name = content_div.find("a", class_="primary-link").text.strip()
            allocation = content_div.find("span", class_="data").text.strip()
            sector_data[sector_name] = allocation

    # add the sector data to the etf_anagrafica Series
    etf_anagrafica["sector_data"] = sector_data

    return etf_anagrafica

