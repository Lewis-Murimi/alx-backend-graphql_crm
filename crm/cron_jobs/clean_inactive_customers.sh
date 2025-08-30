#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")/../.."

# Run Django shell command to delete inactive customers (no orders since 1 year ago)
deleted_count=$(python3 manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

cutoff = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log result with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt