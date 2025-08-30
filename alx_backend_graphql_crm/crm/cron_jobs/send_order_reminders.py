#!/usr/bin/env python3

import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range (last 7 days)
today = datetime.now().date()
seven_days_ago = today - timedelta(days=7)

query = gql(
    """
    query GetRecentOrders($fromDate: Date!) {
      orders(filter: {orderDate_Gte: $fromDate}) {
        id
        customer {
          email
        }
      }
    }
    """
)

try:
    result = client.execute(query, variable_values={"fromDate": seven_days_ago.isoformat()})
    orders = result.get("orders", [])

    for order in orders:
        order_id = order["id"]
        email = order["customer"]["email"]
        logging.info(f"Reminder: Order {order_id} for customer {email}")

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"Error processing reminders: {e}")
    sys.exit(1)
