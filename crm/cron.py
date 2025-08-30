from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs heartbeat every 5 minutes.
    Also queries GraphQL hello field to verify endpoint responsiveness.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("{ hello }")
        result = client.execute(query)

        if "hello" in result:
            message += f" (GraphQL OK: {result['hello']})"
        else:
            message += " (GraphQL FAIL)"
    except Exception as e:
        message += f" (GraphQL ERROR: {e})"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message + "\n")


def update_low_stock():
    """
    Runs GraphQL mutation to restock products with stock < 10.
    Logs updates to /tmp/low_stock_updates_log.txt
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)

        result = client.execute(mutation)
        data = result["updateLowStockProducts"]

        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] {data['message']}\n")
            for p in data["updatedProducts"]:
                f.write(f" - {p['name']}: {p['stock']}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] GraphQL ERROR: {str(e)}\n")
