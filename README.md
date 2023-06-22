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
