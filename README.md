# Personal Finance for Newbies (PFN)

## What is that?
A web app that, from a file of (buy/sell) financial asset transactions, produces near real-time statistics (updated to the last closing) on your investment portfolio

## How can I run it?

### Streamlit
Install dependencies via poetry

- `poetry install`

Launch the app

- `streamlit run 0_🏠_Home.py`

### Docker
To build the app's docker image

- `docker build -t personal-finance-for-newbies .`

To run the docker image and expose it on a preferred port (for example 8080)

- `docker run -p 8080:8501 personal-finance-for-newbies`

To run the docker image using the host's network (which will make the app accessible on port 8501)

- `docker run --network host personal-finance-for-newbies`

### To-Do list
We always look for pull requests, if you know better!
Here's an hopefully up-to-date list of things to build:
- Correlation map between assets
- Improve Sharpe Ratio calculation, to take into account a time-varying:
    - risk-free rate
    - asset allocation
- Rolling Sharpe ratio chart
- Max Drawdown evaluation
- Sortino and Calmar ratios
- Time slicing (1yr, 3yrs, 5yrs, ..., All) as a global filter
- Docker compose, with these services:
    - `jupyter notebook` for prototyping
    - `streamlit` to launch the web-app