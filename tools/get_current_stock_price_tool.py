from datetime import datetime, timedelta
from langchain_core.tools import tool
import requests
import yfinance as yf
import os
from typing import Optional
from bs4 import BeautifulSoup
from vnstock import Vnstock

def get_vn_direct_price(symbol: str) -> Optional[float]:
    """Get stock price by scraping VNDirect website.
    Args:
        symbol (str): Stock symbol without .VN suffix
    Returns:
        Optional[float]: Current stock price or None if not found
    """
    try:
        url = f'https://dchart.vndirect.com.vn/general?symbol={symbol}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                return float(data['data'][0]['last'])
    except Exception:
        return None
    return None

def get_alpha_vantage_price(symbol: str) -> Optional[float]:
    """Get stock price using Alpha Vantage API as fallback.
    Args:
        symbol (str): Stock symbol
    Returns:
        Optional[float]: Current stock price or None if not found
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        return None
        
    # Remove .VN suffix for Alpha Vantage
    symbol = symbol.replace('.VN', '')
    
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            return float(data['Global Quote']['05. price'])
    except Exception:
        return None
    return None

def get_vnstock_price(symbol: str) -> Optional[float]:
    """Get stock price using VnStock API.
    Args:
        symbol (str): Stock symbol without .VN suffix
    Returns:
        Optional[float]: Current stock price or None if not found
    """
    try:
        # Create VnStock client
        client = Vnstock().stock(source="TCBS",symbol=symbol)
        # Get latest price data
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        df = client.quote.history(symbol=symbol,start=start, end=end, interval="1D")
        if not df.empty:
            # Get the most recent close price
            return int(float(df.iloc[-1]['close'])*1000)
    except Exception as e:
        print(f"Error getting price for {symbol}: {str(e)}")
        return None
    return None

def retrieve_current_stock_price(symbol: str) -> float:
    """Get the current stock price of a given symbol.
    Args:
        symbol (str): The symbol of the stock to get the current price for.
    Returns:
        float: The current stock price of the given symbol.
    Raises:
        ValueError: If unable to get the price from any available source.
    """
    original_symbol = symbol
    
    # Add .VN suffix for Vietnam stocks if not present
    if not symbol.endswith('.VN'):
        symbol = f"{symbol}.VN"
    
    try:
        # First try VnStock API for Vietnam stocks
        vnstock_price = get_vnstock_price(original_symbol)
        if vnstock_price is not None:
            print(f"VnStock price for {original_symbol}: {vnstock_price}")
            return vnstock_price
            
        # Then try yfinance
        stock = yf.Ticker(symbol)
        try:
            current_price = stock.info.get('regularMarketPrice')
            if current_price is not None and current_price > 0:
                return current_price
        except Exception:
            pass
            
        # Try VNDirect API
        vnd_price = get_vn_direct_price(original_symbol)
        if vnd_price is not None:
            print(f"VNDirect price for {original_symbol}: {vnd_price}")
            return vnd_price
            
        # If all else fails, try Alpha Vantage
        alpha_price = get_alpha_vantage_price(symbol)
        if alpha_price is not None:
            print(f"Alpha Vantage price for {original_symbol}/{symbol}: {alpha_price}")
            return alpha_price
            
        raise ValueError(f"Could not get price for {symbol} using any available API")
            
    except Exception as e:
        raise ValueError(f"Error getting price for {symbol}: {str(e)}")


@tool
def get_current_stock_price(symbol: str) -> float:
    """Get the current stock price of a given symbol.
    Args:
        symbol (str): The symbol of the stock to get the current price for.
    Returns:
        float: The current stock price of the given symbol.
    """
    return get_vnstock_price(symbol)

if __name__ == "__main__":
    # Test with multiple stocks
    test_symbols = ["FPT", "VNM", "VIC"]
    for symbol in test_symbols:
        try:
            print(f"Getting price for {symbol}")
            price = get_vnstock_price(symbol)
            print(f"{symbol}: {price}")
        except ValueError as e:
            print(f"Error for {symbol}: {str(e)}")