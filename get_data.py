import pandas as pd
import warnings
from vnstock import Listing, Quote, Finance
from ta.momentum import RSIIndicator
import time
from utils.connection import get_connection
warnings.filterwarnings("ignore")

engine = get_connection()

def insert_to_db(df, engine, table_name):
    df.to_sql(table_name, con=engine, if_exists="append", index=False)

def get_list_symbol(group):
    listing = Listing(source="VCI")
    list_symbol = listing.all_symbols()
    list_symbol_group = listing.symbols_by_group(group)
    df_group = pd.merge(list_symbol_group, list_symbol, on=["symbol"])
    insert_to_db(df_group, engine, "symbol")
    print(f"Lấy thành công danh sách cổ phiếu thuộc nhóm {group}")
    return df_group["symbol"].to_list()

def get_history_price(list_symbol, start_date, end_date):
    for symbol in list_symbol:
        time.sleep(2)
        try:
            quote = Quote(symbol=symbol, source="vci")
            price = quote.history(start=start_date, end=end_date, interval="1D")
            # Chuyển cột time về dạng DATE
            price['time'] = pd.to_datetime(price['time']).dt.date

            # Thêm thông tin
            price["symbol"] = symbol

            # Moving Averages
            ma_windows = [20, 50, 100]
            for w in ma_windows:
                price[f"ma{w}"] = price["close"].rolling(window=w).mean().round(2)
                price[f"ema{w}"] = price["close"].ewm(span=w, adjust=False).mean().round(2)

            # Bollinger Bands (window=20, k=2)
            bb_window = 20
            price['bb_middle'] = price['close'].rolling(window=bb_window).mean().round(2)
            price['bb_std'] = price['close'].rolling(window=bb_window).std().round(2)
            price['bb_upper'] = (price['bb_middle'] + 2 * price['bb_std']).round(2)
            price['bb_lower'] = (price['bb_middle'] - 2 * price['bb_std']).round(2)

            # RSI (14)
            rsi = RSIIndicator(close=price['close'], window=14)
            price['rsi14'] = rsi.rsi().round(2)
            price = price.drop_duplicates()
            price = price.dropna() 
            insert_to_db(price.sort_values(by="time", ascending=False), engine, "price")
            print(f"Lấy thành công giá cổ phiếu {symbol}!")
        except Exception as e:
            print(e)

def get_company_quarterly_financials(list_symbol):
    for symbol in list_symbol:
        time.sleep(10)
        try:
            fin = Finance(symbol=symbol, period="quarter", source="VCI")
            income_statement = fin.income_statement()
            balance_sheet = fin.balance_sheet()
            cashflow = fin.cash_flow()
            ratio = fin.ratio()
            ratio.columns = ratio.columns.droplevel(0)

            # Gộp toàn bộ 4 bảng lại 1 lần
            company_data = (
                income_statement
                .merge(balance_sheet, on=["ticker", "yearReport", "lengthReport"], how="inner")
                .merge(cashflow, on=["ticker", "yearReport", "lengthReport"], how="inner")
                .merge(ratio, on=["ticker", "yearReport", "lengthReport"], how="inner")
            )
            company_data = company_data[[
                # Nhận dạng doanh nghiệp
                'ticker', 'yearReport', 'lengthReport',

                # Sinh lời
                'ROE (%)', 'ROA (%)', 'Net Profit Margin (%)', 'EPS (VND)',
                'Net Profit For the Year', 'Profit before tax',
                'Attribute to parent company (Bn. VND)',
                'Attribute to parent company YoY (%)',

                # Tài chính và đòn bẩy
                'Financial Leverage',
                "Owners' Equity/Charter Capital", 'Fixed Asset-To-Equity',

                # Định giá
                'P/E', 'P/B', 'P/Cash Flow',

                # Hiệu quả và quy mô hoạt động
                'Revenue (Bn. VND)', 'Revenue YoY (%)',
                'TOTAL ASSETS (Bn. VND)', 'LIABILITIES (Bn. VND)',
                "OWNER'S EQUITY(Bn.VND)", 'TOTAL RESOURCES (Bn. VND)',
                'Fixed assets (Bn. VND)', 'Paid-in capital (Bn. VND)',
                'Undistributed earnings (Bn. VND)',
                'General & Admin Expenses',
                'Purchase of fixed assets',
                'Proceeds from disposal of fixed assets',

                # Dòng tiền
                'Net cash inflows/outflows from operating activities',
                'Net Cash Flows from Investing Activities',
                'Cash flows from financial activities',
                'Net increase/decrease in cash and cash equivalents',
                'Cash and cash equivalents (Bn. VND)',
                'Cash and Cash Equivalents at the end of period',

                # Cổ đông
                'BVPS (VND)', 'Market Capital (Bn. VND)',
                'Outstanding Share (Mil. Shares)'
            ]]
            company_data["Debt/Equity"] = company_data['LIABILITIES (Bn. VND)'] / company_data["OWNER'S EQUITY(Bn.VND)"]
            insert_to_db(company_data, engine, "quarterly_financials")
            print(f"Lấy thành công báo cáo tài chính theo quý cổ phiếu {symbol}!")
        except Exception as e:
            print(f"[COMPANY_INFO_QUARTERLY_FETCH_ERROR] Symbol: {symbol} | Exception: {e}")


def get_company_yearly_financials(list_symbol):
    for symbol in list_symbol:
        time.sleep(10)
        try:
            fin = Finance(symbol=symbol, period="year", source="VCI")
            income_statement = fin.income_statement()
            balance_sheet = fin.balance_sheet()
            cashflow = fin.cash_flow()
            ratio = fin.ratio()
            ratio.columns = ratio.columns.droplevel(0)

            # Gộp toàn bộ 4 bảng lại 1 lần
            company_data = (
                income_statement
                .merge(balance_sheet, on=["ticker", "yearReport"], how="inner")
                .merge(cashflow, on=["ticker", "yearReport"], how="inner")
                .merge(ratio, on=["ticker", "yearReport"], how="inner")
            )
            company_data = company_data[[
                # Nhận dạng doanh nghiệp
                'ticker', 'yearReport', 'lengthReport',

                # Sinh lời
                'ROE (%)', 'ROA (%)', 'Net Profit Margin (%)', 'EPS (VND)',
                'Net Profit For the Year', 'Profit before tax',
                'Attribute to parent company (Bn. VND)',
                'Attribute to parent company YoY (%)',

                # Tài chính và đòn bẩy
                'Financial Leverage',
                "Owners' Equity/Charter Capital", 'Fixed Asset-To-Equity',

                # Định giá
                'P/E', 'P/B', 'P/Cash Flow',

                # Hiệu quả và quy mô hoạt động
                'Revenue (Bn. VND)', 'Revenue YoY (%)',
                'TOTAL ASSETS (Bn. VND)', 'LIABILITIES (Bn. VND)',
                "OWNER'S EQUITY(Bn.VND)", 'TOTAL RESOURCES (Bn. VND)',
                'Fixed assets (Bn. VND)', 'Paid-in capital (Bn. VND)',
                'Undistributed earnings (Bn. VND)',
                'General & Admin Expenses',
                'Purchase of fixed assets',
                'Proceeds from disposal of fixed assets',

                # Dòng tiền
                'Net cash inflows/outflows from operating activities',
                'Net Cash Flows from Investing Activities',
                'Cash flows from financial activities',
                'Net increase/decrease in cash and cash equivalents',
                'Cash and cash equivalents (Bn. VND)',
                'Cash and Cash Equivalents at the end of period',

                # Cổ đông
                'BVPS (VND)', 'Market Capital (Bn. VND)',
                'Outstanding Share (Mil. Shares)'
            ]]
            company_data["Debt/Equity"] = company_data['LIABILITIES (Bn. VND)'] / company_data["OWNER'S EQUITY(Bn.VND)"]
            insert_to_db(company_data, engine, "yearly_financials")
            print(f"Lấy thành công báo cáo tài chính theo năm cổ phiếu {symbol}!")
        except Exception as e:
            print(f"[COMPANY_INFO_YEARLY_FETCH_ERROR] Symbol: {symbol} | Exception: {e}")

def main():
    list_symbol = get_list_symbol("VN30")
    get_history_price(list_symbol, "2000-01-01", "2025-11-27")
    get_company_quarterly_financials(list_symbol)
    get_company_yearly_financials(list_symbol)

if __name__ == "__main__":
    main()