import requests
from bs4 import BeautifulSoup

import pandas as pd


def retrieve_sector(df_anagrafica: pd.DataFrame) -> pd.DataFrame:
    # filter only specified url
    df_anagrafica = df_anagrafica[df_anagrafica["sector_url"] != '']
    # filter only Equity
    df_anagrafica = df_anagrafica[df_anagrafica["macro_asset_class"] == "Equity"]

    # retrieve page
    df_anagrafica["page_content"] = df_anagrafica["sector_url"].apply(retrieve_page)

    # based on macro asset class trigger the right function. Use switch case
    df_sector = pd.concat([
        df_anagrafica.apply(
            lambda x: retrieve_etf_sector_data(x) if x["macro_asset_class"] == "Equity" else None,
            axis=1,
        )
    ])

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

    sector_data = pd.Series(sector_data)
    asset_name = pd.Series(etf_anagrafica["ticker_yf"], index=["ticker_yf"])

    sector_data = pd.concat([asset_name, sector_data])
    return sector_data

