from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.highlight import Formatter, get_text
from flask import current_app


class GreenBoldFormatter(Formatter):
    def format_token(self, text, token, is_last=False):
        ttext = get_text(text, token, True)
        return f'<span class="highlight-keyword">{ttext}</span>'


def search_documents(query_str):
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
