from celery import shared_task
from datetime import datetime
import requests


@shared_task
def generate_crm_report():
    """
    Weekly CRM report:
    - Total customers
    - Total orders
    - Total revenue
    Logs report to /tmp/crm_report_log.txt
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    query = """
    {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
            edges {
                node {
                    totalamount
                }
            }
        }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            headers={"Content-Type": "application/json"},
        )
        data = response.json()

        if "errors" in data:
            raise Exception(data["errors"])

        result = data["data"]

        total_customers = result["allCustomers"]["totalCount"]
        total_orders = result["allOrders"]["totalCount"]
        total_revenue = sum(
            float(order["node"]["totalamount"]) for order in result["allOrders"]["edges"]
        )

        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"

        with open(log_file, "a") as f:
            f.write(report + "\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
