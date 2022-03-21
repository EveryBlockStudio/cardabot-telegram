import os
import logging
from sgqlc.endpoint.http import HTTPEndpoint


class GraphQLClient:
    def __init__(self, url: str, token: str = "") -> None:
        self.url = url
        self.token = token
        self.endpoint = HTTPEndpoint(url)

    def caller(
        self,
        query_file: str,
        variables: dict = {},
        graphql_queries: str = "graphql_queries",
    ) -> dict:
        """Request data a cardano graphql endpoint (EBS).

        Query text is obtained from `query_file` stored under the `graphql_queries` dir.
        In case `query_file` is missing, it returns an empty dictionary.

        """
        try:
            with open(os.path.join(graphql_queries, query_file)) as f:
                query = f.read()

        except FileNotFoundError as e:
            logging.exception(e)
            return {}

        return self.endpoint(query, variables)
