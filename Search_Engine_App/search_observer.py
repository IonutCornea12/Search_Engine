# search_observer.py
class SearchObserver:
    def update(self, query: str, results: list):
        raise NotImplementedError()

class SearchObservable:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer: SearchObserver):
        self._observers.append(observer)

    def notify_observers(self, query: str, results: list):
        for obs in self._observers:
            obs.update(query, results)

class QueryLoggerObserver(SearchObserver):
    def __init__(self, db_adapter):
        self.db = db_adapter
        self.last_logged_query = None
        self.last_logged_result_count = None

    def update(self, query: str, results: list):
        if query != self.last_logged_query or len(results) != self.last_logged_result_count:
            print(f"[LoggerObserver] Logging query: {query} with {len(results)} results")
            self.db.insert_search_query(query, result_count=len(results))
            self.last_logged_query = query
            self.last_logged_result_count = len(results)
        else:
            print(f"[LoggerObserver] Skipped duplicate query: {query}")

class SuggestionUpdaterObserver(SearchObserver):
    def __init__(self, combo_box, db_adapter):
        self.combo_box = combo_box
        self.db = db_adapter

    def update(self, query: str, results: list):
        self.combo_box.clear()
        recent_queries = self.db.fetch_recent_queries(limit=5)
        if not recent_queries:
            self.combo_box.addItem("No recent searches.")
        else:
            for q in recent_queries:
                if " | results: " in q:
                    query_text = q.split(" | results: ")[0].strip()
                    results_count = q.split(" | results: ")[1].strip()
                    self.combo_box.addItem(f"{query_text} ({results_count})", userData=query_text)
                else:
                    self.combo_box.addItem(q, userData=q)