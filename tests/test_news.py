from src.tools.news import get_news

def test_get_news_integration():
    # test news fetching to make sure it actually brings back articles
    # we just need 1 to verify the core functionality
    articles = get_news("AAPL", max_articles=1)
    
    # ensure it's returning a list
    assert isinstance(articles, list)
    
    # assert the list is not empty
    assert len(articles) > 0
    
    # check if the dictionary contains the correct keys we structured
    article = articles[0]
    assert "headline" in article
    assert "summary" in article
    assert "url" in article
    assert "published_at" in article
    assert "source" in article
    
    # make sure headline is a string and not empty just to be safe
    assert isinstance(article["headline"], str)
    assert len(article["headline"]) > 0
