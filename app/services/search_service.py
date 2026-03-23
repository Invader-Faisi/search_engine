from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.highlight import Formatter, get_text
from flask import current_app
from app.services.cache_service import cached_search


class GreenBoldFormatter(Formatter):
    def format_token(self, text, token, is_last=False):
        ttext = get_text(text, token, True)
        return f'<span class="highlight-keyword">{ttext}</span>'


def _perform_search(query_str):
    """Actual search function (without caching)"""
    index_dir = current_app.config['WHOOSH_INDEX']
    ix = open_dir(index_dir)

    results_list = []

    with ix.searcher() as searcher:
        parser = MultifieldParser(["title", "content"], schema=ix.schema)
        query = parser.parse(query_str)

        results = searcher.search(query, limit=10)

        results.formatter = GreenBoldFormatter()

        for r in results:
            snippet = r.highlights("content")

            if not snippet:
                snippet = r['content'][:200] + "..."

            results_list.append({
                "title": r['title'],
                "path": r['path'],
                "snippet": snippet,
                "score": round(r.score, 2)
            })

    return results_list


def search_documents(query_str):
    """Search documents with caching"""
    if not query_str or not query_str.strip():
        return []
    
    # Use cached search
    return cached_search(_perform_search, query_str.strip())


def clear_search_cache():
    """Clear search cache"""
    from app.services.cache_service import clear_search_cache as clear_cache
    clear_cache()


def get_search_cache_stats():
    """Get search cache statistics"""
    from app.services.cache_service import get_cache_stats
    return get_cache_stats()
