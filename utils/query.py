from datetime import datetime, timedelta
import pandas as pd
from utils.connection import get_connection

engine = get_connection()
today = datetime.today()
last_month = today - timedelta(days=30)

start_date = last_month.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

def get_all_symbol():
    df = pd.read_sql("SELECT * FROM symbol", con=engine)
    return df.to_dict(orient="records")

def get_symbol_info(symbol):
    df = pd.read_sql(f"SELECT * FROM symbol WHERE symbol='{symbol}'", con=engine)
    return df.to_dict(orient="records")

def get_latest_quarter_financials(ticker):
    df = pd.read_sql(f"""SELECT * FROM quarterly_financials 
                    WHERE ticker='{ticker}' 
                    ORDER BY "yearReport" DESC, "lengthReport" DESC 
                    LIMIT 4;""", con=engine)
    return df.to_dict(orient="records")

def get_latest_year_financials(ticker):
    df = pd.read_sql(f"""SELECT * FROM  yearly_financials 
                     WHERE ticker='{ticker}' 
                     ORDER BY "yearReport" DESC 
                     LIMIT 4;""", con=engine)
    return df.to_dict(orient="records")

def get_price(symbol, start_date=start_date, end_date=end_date):
    df = pd.read_sql(f"SELECT * FROM price WHERE symbol='{symbol}' AND time BETWEEN '{start_date}' AND '{end_date}' ORDER by time;", con=engine)
    return df.to_dict(orient="records")

def get_latest_price(symbol):
    df = pd.read_sql(f"""SELECT * FROM price 
                     WHERE symbol='{symbol}' 
                     ORDER BY time DESC 
                     LIMIT 150;""", con=engine)
    return df.to_dict(orient="records")


