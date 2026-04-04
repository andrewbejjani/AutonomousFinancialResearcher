from src.tools.stock_price import get_stock_price

def test_get_stock_price_integration():
    # just a simple test to make sure we can fetch live data from yahoo finance without blowing up
    # we use aapl since it's almost always available
    price_str = get_stock_price("AAPL")
    
    # check that it didnt return the error string
    assert "Error fetching price" not in price_str
    
    # make sure the string is actually a number
    try:
        price_val = float(price_str)
        assert price_val > 0
    except ValueError:
        assert False, f"Expected a numeric string, but got: {price_str}"
