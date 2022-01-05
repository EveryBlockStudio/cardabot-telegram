from typing import Dict
from dotenv.main import load_dotenv
from sgqlc.endpoint.http import HTTPEndpoint
from pathlib import Path
import os


def get_data_from_node(query_name: str, variables={}) -> Dict:
    """Request data from EBS's private cardano graphql endpoint.

    Query text is obtained from file `query_name` stored under the `src/queries/` dir.

    """
    try:
        query = Path(
            Path(__file__).parent, "src", "query", f"{query_name}.graphql"
        ).read_bytes()  # get query file path and read the query as bytes

    except FileNotFoundError:
        print(f"Query file {query_name} not found")  # TODO: maybe use logging instead?
        return None

    # create endpoint object and execute query with given variables
    endpoint = HTTPEndpoint(os.environ.get("GRAPHQL_URL"))
    data = endpoint(query, variables)

    # returns data as dictionary
    return data


if __name__ == "__main__":
    # sample query for getting stake pool details about EBS stake pool
    load_dotenv(override=True)
    EBS_pool = "pool1ndtsklata6rphamr6jw2p3ltnzayq3pezhg0djvn7n5js8rqlzh"
    print(get_data_from_node("stakePoolById", {"id": EBS_pool}))
