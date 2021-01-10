import logging
import time
from urllib.error import HTTPError

from SPARQLWrapper import SPARQLWrapper, JSON


class SparqlHandler:
    def __init__(self, endpoint):
        self.sparql_wrapper = SPARQLWrapper(endpoint, agent="wikidata_survey")
        self.sparql_wrapper.setReturnFormat(JSON)
        self.sparql_wrapper.setUseKeepAlive()

    def send_query(self, query, max_tries=5):
        self.sparql_wrapper.setQuery(query)
        tries = 0
        while tries < max_tries:
            tries += 1
            try:
                response = self.sparql_wrapper.query()
                return response.convert()
            except HTTPError as e:
                if e.code == 429:
                    logging.warning(f"wait {5} seconds")
                    time.sleep(5 + 1)
                    continue
        raise RuntimeError("Maximum number of tries reached.")
