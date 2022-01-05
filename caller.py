from dotenv.main import load_dotenv
from sgqlc.endpoint.http import HTTPEndpoint
from pathlib import Path
import os

# Get data as dictionary from EBS's private cardano graphql endpoint based on the query filename
# stored under src/queries/ directory
def getDataFromCardanoNode(queryName, variables={}):
    load_dotenv(override=True)
    url = os.environ.get("GRAPHQL_URL")
    # get query file path and read the query as bytes
    try:
        query = Path(
            Path(__file__).parent, "src", "query", f"{queryName}.graphql"
        ).read_bytes()
    except FileNotFoundError:
        print(f"Query file {queryName} not found")
        return None

    # create endpoint object and execute query with given variables
    endpoint = HTTPEndpoint(url)
    data = endpoint(query, variables)

    # returns data as dictionary
    return data


if __name__ == "__main__":
    # sample query for getting stake pool details about EBS stake pool
    EBS_pool = "pool1ndtsklata6rphamr6jw2p3ltnzayq3pezhg0djvn7n5js8rqlzh"
    print(getDataFromCardanoNode("stakePoolById", {"id": EBS_pool}))
