import stripe

# Set your Stripe secret key
stripe.api_key = 'sk_test_51IsaJzJK7wwywY1K08oalOKH7UWogsWBOp4BsbTeKLPwdFYF3VpKORZcdZZYqsUdiivOvRUhKzrs73m1CKTCJnMC00ZnAbrrtU'

# The customer ID for which you want to retrieve subscriptions
customer_id = 'cus_QbvNh86JdRSEOE'

# Retrieve all subscriptions for the customer
customer_details = stripe.Customer.retrieve(customer_id)
subscriptions = stripe.Subscription.list(customer=customer_id)
print(f"Customer:{customer_details.email}")

from datetime import datetime
def get_stripedate(timestamp : int):
    if timestamp:
        # Convert Unix timestamp to a datetime object in UTC
        invoice_date = datetime.utcfromtimestamp(timestamp)
        return invoice_date
    return None

# Print subscription details
for subscription in subscriptions.auto_paging_iter():
    print(f"Subscription ID: {subscription.id}")
    print(f"Status: {subscription.status}")
    print(f"Items: {[item.plan.id for item in subscription['items']['data']]}")
    print(f"Start Date: {get_stripedate(subscription.start_date)}")
    print(f"Current Period Start: {get_stripedate(subscription.current_period_start)}")
    print(f"Current Period End: {get_stripedate(subscription.current_period_end)}")
    print(f"Billing Cycle Anchor: {get_stripedate(subscription.billing_cycle_anchor)}")
    print(f"Plan Details: {subscription.get('plan')}")
    print('-' * 40)
