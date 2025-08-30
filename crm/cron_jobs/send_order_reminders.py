#!/usr/bin/env python3
import sys
import asyncio
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

async def main():
    # GraphQL endpoint
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Calculate cutoff date (7 days ago)
    cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # GraphQL query to get pending orders in last 7 days
    query = gql(
        """
        query GetRecentOrders($cutoff: Date!) {
            orders(orderDate_Gte: $cutoff, status: "PENDING") {
                id
                customer {
                    email
                }
            }
        }
        """
    )

    # Execute query
    try:
        result = await client.execute_async(query, variable_values={"cutoff": cutoff_date})
        orders = result.get("orders", [])
    except Exception as e:
        print(f"Error fetching orders: {e}", file=sys.stderr)
        return

    # Log results
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        for order in orders:
            log_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Order {order['id']} reminder sent to {order['customer']['email']}\n"
            log_file.write(log_line)

    print("Order reminders processed!")

if __name__ == "__main__":
    asyncio.run(main())