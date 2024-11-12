import stripe 
stripe.api_key = "sk_test_51IsaJzJK7wwywY1K08oalOKH7UWogsWBOp4BsbTeKLPwdFYF3VpKORZcdZZYqsUdiivOvRUhKzrs73m1CKTCJnMC00ZnAbrrtU"


''' Stripe Customer '''
class Customer:
    def __init__(self):
        self.customers = []  # List to keep track of customer data

    @staticmethod
    def create_customer(name, email):
        if '@' in email and name:
            customer = stripe.Customer.create(name=name, email=email)
            if customer:
                return customer.id, customer
        return None, None

    @staticmethod
    def update_customer(customer, metadata):
        if isinstance(metadata, dict):
            customer = stripe.Customer.modify(customer, metadata=metadata)
            if customer:
                return customer.id, customer
        return None, None

    @staticmethod
    def retrieve_customer(customer):
        try:
            customer = stripe.Customer.retrieve(customer)
        except:
            customer = {}
        return customer

    @staticmethod
    def listout_customer(length=3):
        customers = stripe.Customer.list(limit=length)
        return customers

    @staticmethod
    def delete_customers(customer):
        customer = stripe.Customer.delete(customer)
        return customer

    @staticmethod
    def search_customer(query="name:'Jane Doe' AND metadata['foo']:'bar'"):
        customer = stripe.Customer.search(query=query)
        return customer

''' Payment Methods'''
class PaymentMethods:
    def __init__(self):
        self.payment = []  # List to keep track of customer data

    @staticmethod
    def paymentmethod_exists(customer):
        # Retrieve the list of payment methods
        payment_methods = stripe.PaymentMethod.list(
        customer=customer,
        type='card'  # You can specify the type of payment method, e.g., 'card'
        )
        # Check if the customer has any payment methods
        if payment_methods.data:
            return True
        else:
            return True
        
    @staticmethod
    def retrieve_paymentmethod(cus,payment):
        payment_method=stripe.Customer.retrieve_payment_method(
        cus,
        payment,
        )
        return payment_method

    @staticmethod
    def retrieve_paymentmethod(payment):
        payment = stripe.PaymentMethod.retrieve(payment)
        return payment

    @staticmethod
    def attach_paymentmethod_to_customer(cus,paymentmethod):
        payment = stripe.PaymentMethod.attach(
            paymentmethod,
            customer=cus,
            )
        return payment
    
''' Checkout Session '''
class Session:
    def __init__(self):
        self.session_id = []
    
    @staticmethod
    def create_session(obj):
        customer = obj.get('customer')
        client_id = obj.get('client_reference_id')
        cus_email = obj.get('customer_email')
        line_items = obj.get('line_items')
        meta_data = obj.get('meta_data')
        plan_name = obj.get('plan_name')
        mode = obj.get('mode')
        final_cancel_url = cancel_url
        print("modeee",mode)
        if len(plan_name)> 0:
            a = plan_name[0]
            current_plan = a.split('.')
            find_api_id = math.floor(int(current_plan[0]))
            final_cancel_url = f'{final_cancel_url}/{find_api_id}'
        if customer:
            if mode == 'payment':
                checkout_session = stripe.checkout.Session.create(
                    success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=final_cancel_url,
                    customer=customer,
                    client_reference_id=client_id,
                    billing_address_collection="required",
                    mode=mode,
                    payment_intent_data={'setup_future_usage':'off_session'},
                    allow_promotion_codes=True,
                    line_items=line_items,
                    metadata=meta_data,
                    invoice_creation =  {"enabled" : True},
                    payment_method_types=PAYMENT_METHOD_TYPES
                    )
            else:  
                checkout_session = stripe.checkout.Session.create(
                    success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=final_cancel_url,
                    customer=customer,
                    client_reference_id=client_id,
                    billing_address_collection="required",
                    mode=mode,
                    allow_promotion_codes=True,
                    line_items=line_items,
                    metadata=meta_data,
                    payment_method_types=PAYMENT_METHOD_TYPES
                    )
        if cus_email:
            if mode == 'payment':
                checkout_session = stripe.checkout.Session.create(
                    success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=final_cancel_url,
                    customer_email=cus_email,
                    client_reference_id=client_id,
                    billing_address_collection="required",
                    mode=mode,
                    payment_intent_data={'setup_future_usage':'off_session'},
                    allow_promotion_codes=True,
                    line_items=line_items,
                    metadata=meta_data,
                    invoice_creation =  {"enabled" : True},
                    payment_method_types=PAYMENT_METHOD_TYPES
                    )
            else:
                checkout_session = stripe.checkout.Session.create(
                    success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=final_cancel_url,
                    customer_email=cus_email,
                    client_reference_id=client_id,
                    billing_address_collection="required",
                    mode=mode,
                    allow_promotion_codes=True,
                    line_items=line_items,
                    metadata=meta_data,
                    payment_method_types=PAYMENT_METHOD_TYPES
                    )
        return checkout_session
    
    @staticmethod
    def update_session(session_id,meta_data):
        checkout_session = stripe.checkout.Session.modify(
        session_id,
        metadata=meta_data
        )
        return checkout_session
    
    @staticmethod
    def retrieve_session(session):
        session = stripe.checkout.Session.retrieve(session)
        return session
    
    @staticmethod
    def listof_checkout_session(limit= 3):
        session = stripe.checkout.Session.list(limit=limit)
        return session
    
    @staticmethod
    def session_lineitems(session):
        session = stripe.checkout.Session.list_line_items(session)
        return session
    
    @staticmethod
    def session_expire(session):
        session = stripe.checkout.Session.expire(session)
        return session

''' Invoices '''
class Invoice:
    def __init__(self):
        self.invoice = []
    
    @staticmethod
    def create_invoice(customer):
        invoice = stripe.Invoice.create(customer=customer)
        return invoice
    
    @staticmethod
    def preview_invoice(customer_id):
        invoice = stripe.Invoice.create_preview(customer=customer_id)
        return invoice
    
    @staticmethod
    def update_invoice(invoice,meta_data):
        invoice = stripe.Invoice.modify(invoice,metadata=meta_data)
        return invoice
    
    @staticmethod
    def retrieve_invoice(invoice):
        invoice = stripe.Invoice.retrieve(invoice)
        return invoice
    
    @staticmethod
    def upcoming_invoice(customer_id):
        invoice = stripe.Invoice.upcoming(customer=customer_id)
        return invoice

    @staticmethod
    def invoice_list(limit=3):
        invoice = stripe.Invoice.list(limit=limit)
        return invoice
    
    @staticmethod
    def delete_draft_invoice(invoice):
        invoice = stripe.Invoice.delete(invoice)
        return invoice
    
    def finalize_invoice(invoice):
        invoice = stripe.Invoice.finalize_invoice(invoice)
        return invoice
    
    @staticmethod
    def pay_invoice(invoice):
        invoice = stripe.Invoice.pay(invoice)
        return invoice
    
    @staticmethod
    def send_invoice(invoice):
        invoice = stripe.Invoice.send_invoice(invoice)
        return invoice
    
    @staticmethod
    def void_invoice(invoice):
        invoice = stripe.Invoice.void_invoice(invoice)
        return invoice
    
    
''' Subscriptions'''
class Subscription:
    def __init__(self):
        self.subscription = []


    @staticmethod
    def create_subscription(customer,items):
        subscription = stripe.Subscription.create(customer=customer,items=items,proration_behavior="always_invoice")
        return subscription

    @staticmethod
    def update_subscription(subscription,obj):
        proration_date = obj.get('proration_date')
        coupon = obj.get('coupon')
        line_items = obj.get('line_items')
        meta_data = obj.get('meta_data')
        # subscription = stripe.Subscription.modify(subscription,metadata=meta_data)
        subscription = stripe.Subscription.modify(
                      subscription,
                      cancel_at_period_end=False,
                      proration_behavior='always_invoice',
                      proration_date=proration_date,
                      items=line_items,  
                      billing_cycle_anchor='now',
                      coupon=coupon,
                      metadata=meta_data
                    )
        return subscription

    @staticmethod
    def retrieve_subcription(subscription):
        subscription = stripe.Subscription.retrieve(subscription)
        return subscription

    @staticmethod
    def subscriptions_list(limit=3):
        subscription = stripe.Subscription.list(limit=limit)
        return subscription

    @staticmethod
    def cancel_subsription(subscription):
        subscription = stripe.Subscription.cancel(subscription)
        return subscription

    @staticmethod
    def modify_cancel_subsription(subscription):
        subscription = stripe.Subscription.modify(subscription,cancel_at_period_end=True)
        return subscription

    @staticmethod
    def resume_subscription(subscription):
        subscription = stripe.Subscription.resume(subscription,billing_cycle_anchor="now")
        return subscription
    
    @staticmethod
    def renew_subscription(subscription,obj):
        line_items = obj.get('line_items')
        subscription = stripe.Subscription.modify(
                subscription,
                cancel_at_period_end=False,
                proration_behavior="always_invoice",
                billing_cycle_anchor="now",
                items=line_items,
            )
        return subscription


''' Subscription Items'''
class SubscriptionItems:
    def __init__(self):
        self.subscription = []
        
    @staticmethod
    def create_subscription_items(subscription,price_id,quantity):
        sub_items = stripe.SubscriptionItem.create(subscription=subscription,price=price_id,quantity=quantity)
        return sub_items

    @staticmethod
    def update_subscription_items(subsciption_item,meta_data):
        sub_items = stripe.SubscriptionItem.modify(subsciption_item,metadata=meta_data)
        return sub_items

    @staticmethod
    def retrieve_subscription_items(subscriptions_item):
        sub_items = stripe.SubscriptionItem.retrieve(subscriptions_item)
        return sub_items

    @staticmethod
    def subscription_items_list(subscription,limit=3):
        sub_items = stripe.SubscriptionItem.list(imit=3,subscription=subscription)
        return sub_items
    
    @staticmethod
    def delete_subscription_items(subscriptions_item):
        sub_items = stripe.SubscriptionItem.delete(subscriptions_item)
        return sub_items

'''Billing Portal '''
class BillingPortal:
    def __init__(self):
        self.invoice = []

    @staticmethod
    def create_billing_portal(customer,url = None):
        if url == None:
            url = success_url
        billing_portal =stripe.billing_portal.Session.create(
            customer=customer,
            return_url=url,
            )
        return billing_portal
    

''' Customer Balance Transcations'''
class BalanceTransaction:
    def __init__(self):
        self.invoice = []

    @staticmethod
    def create_transaction(customer,amount):
        transaction = stripe.Customer.create_balance_transaction(customer,amount=amount,currency="usd")
        return transaction
    
    @staticmethod
    def update_transaction(customer,trans_id,obj):
        meta_data = obj.get('meta_data')
        transaction = stripe.Customer.modify_balance_transaction(
            customer,trans_id,
            metadata=meta_data)
        return transaction
    
    @staticmethod
    def retrieve_transaction(customer_id,trans_id):
        transaction = stripe.Customer.retrieve_balance_transaction(customer_id,trans_id)
        return transaction
    
    @staticmethod
    def list_customer_transaction(customer_id):
        transaction = stripe.Customer.list_balance_transactions(customer_id)
        return transaction


''' Payment Indent'''
class PaymentIndent:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def create_paymentintent():
        paymentindent = stripe.PaymentIntent.create(
        amount=2000,
        currency="usd",
        automatic_payment_methods={"enabled": True},
        )
        return paymentindent

    @staticmethod    
    def update_paymentindent(payment_id):
        paymentindent = stripe.PaymentIntent.modify(payment_id,metadata={"order_id": "6735"})
        return paymentindent
    
    @staticmethod
    def retrieve_paymentindent(payment_id):
        paymentindent = stripe.PaymentIntent.retrieve(payment_id)
        return paymentindent

    @staticmethod
    def list_of_paymentindent():
        paymentindent = stripe.PaymentIntent.list(limit=3)
        return paymentindent
    
    @staticmethod
    def cancel_paymentindent(payment_id):
        paymentindent = stripe.PaymentIntent.cancel(payment_id)
        return paymentindent

''' Identify the Stripe Keys and Values'''
class StripeKeys:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def get_stripekey_details(key):
        details = stripe.Product.retrieve(key)
        print(f'API Name {details.name}')
        return details
    
    @staticmethod
    def stripekey_list(product_id):
        prices = stripe.Price.list(product=product_id)

        # Print the price details
        for price in prices.data:
            print(f"Price ID: {price.id}")
            print(f"Currency: {price.currency}")
            print(f"Unit amount: {price.unit_amount / 100} {price.currency.upper()}")
            print(f"Recurring: {price.recurring}\n")
            if price.recurring:
                interval = price.recurring['interval']  # e.g., 'month', 'day'
                interval_count = price.recurring['interval_count']  # The number of intervals
                print(f"Subscription is valid for {interval_count} {interval}(s) per billing cycle.")

                # Check if it's a daily interval and count
                if interval == 'day':
                    print(f"This subscription is valid for {interval_count} days.")
                elif interval == 'month':
                    print(f"This subscription renews on a monthly basis, billing on the same day each month.")
            else:
                print("This price does not have a recurring interval.")

''' Describe Products'''
class Products:
    def __init(self):
        self.subscription = []

    @staticmethod
    def create_product(name):
        products = stripe.Product.create(name=name)
        return products

    @staticmethod
    def update_product(product_id,meta_data):
        products = stripe.Product.modify(
            product_id,
            metadata=meta_data)

    @staticmethod
    def retrieve_product(product):
        products = stripe.Product.retrieve(product)
        return products

    @staticmethod
    def list_of_products(limit=3):
        products = stripe.Product.list(limit=limit)
        return products

    @staticmethod
    def delete_product(product_id):
        products = stripe.Product.delete(product_id)
        return products

    @staticmethod
    def search_products(query="active:'true' AND metadata['order_id']:'6735'"):
        products = stripe.Product.search(query=query)
        return products

''' Describe Prices'''
class Prices:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def create_price(name,recurring,amount,usd):
        prices = stripe.Price.create(
            currency=usd,
            unit_amount=amount,
            recurring=recurring,
            product_data=f'{"name":{name}}',
        )
        return prices

    @staticmethod
    def update_prices(price_id,meta_data): 
        prices = stripe.Price.modify(
            price_id,
            metadata=meta_data)
        return prices 

    @staticmethod
    def retrieve_prices(price_id):
        prices = stripe.Price.retrieve(price_id)
        return prices
    
    @staticmethod
    def listof_prices(limit=3):
        prices = stripe.Price.list(limit=limit)
        return prices

    @staticmethod
    def search_prices(query="active:'true' AND metadata['order_id']:'6735'"):
        prices = stripe.Price.search(query=query)
        return prices


''' Describe Coupon'''
class Coupon:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def create_coupon(duration,percentage,name,duration_period = None):

        coupon  = None
        if duration == 'once':
            coupon = stripe.Coupon.create(
                duration=duration,            # Coupon is valid for one redemption
                percent_off=percentage,            # Discount amount in cents ($5.00)
                currency='usd',         # Currency of the coupon 
                name = name            # Unique coupon ID
            )
        if duration == 'forever':
            coupon = stripe.Coupon.create(
                duration=duration,         # Coupon is valid indefinitely
                percent_off=percentage,            # Percentage discount (20%)
                currency='usd',         # Currency of the coupon
                name = name                   # Unique coupon ID
            )
        if duration == 'repeating':
            coupon = stripe.Coupon.create(
                duration=duration,       # Coupon is valid for multiple uses
                duration_in_months=duration_period,      # Valid for 3 months
                percent_off=percentage,            # Percentage discount (10%)
                currency='usd',   # Currency of the coupon 
                name = name            # Unique coupon ID
            )
        return coupon

    @staticmethod
    def update_coupon(coupon_id,apply_products,meta_data = {"order_id": "6735"}):
        coupon = stripe.Coupon.modify(
            coupon_id,
            applies_to=apply_products,
            metadata=meta_data,

        )
        return coupon

    @staticmethod
    def retrieve_coupon(coupon_id):
        coupon = stripe.Coupon.retrieve(coupon_id)
        return coupon

    @staticmethod
    def listof_coupon(limit=3):
        coupon = stripe.Coupon.list(limit=limit)
        return coupon

    @staticmethod
    def delete_coupon(coupon_id):
        coupon = stripe.Coupon.delete(coupon_id)
        return coupon

''' PromoCode'''
class PromoCode:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def create_promocode(coupon):
        promo = stripe.PromotionCode.create(coupon=coupon)
        return promo

    @staticmethod
    def update_promocode(promo_code,meta_data):
        promo = stripe.PromotionCode.modify(
            promo_code,
            metadata=meta_data,
            )
        return promo

    @staticmethod
    def retrieve_promocode(promo_code):
        promo = stripe.PromotionCode.retrieve(promo_code)
        return promo

    @staticmethod
    def listof_promocode(limit=3):
        promo = stripe.PromotionCode.list(limit=limit)
        return promo


''' Discounts'''
class Discounts:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def delete_customer_discounts(customer):
        discounts = stripe.Customer.delete_discount(customer)
        return discounts
    
    @staticmethod
    def delete_subscription_discounts(subscription):
        discounts = stripe.Subscription.delete_discount(subscription)
        return discounts




''' Stripe Function has been Implemented'''
class StripeFunction:
    def __init__(self):
        self.subscription = []

    @staticmethod
    def get_invoice_amount_paid(amount):
        if amount:
            amount_paid = amount
            amount_paid_dollars = amount_paid / 100.0
            return amount_paid_dollars
        return amount
    
    @staticmethod
    def get_stripedate(timestamp : int):
        if timestamp:
            # Convert Unix timestamp to a datetime object in UTC
            invoice_date = datetime.utcfromtimestamp(timestamp)
            return invoice_date
        return None

    @staticmethod
    def get_invoiceitem(invoice:str):
        if invoice:
            # Convert Unix timestamp to a datetime object in UTC
            invoice_obj = Invoice.retrieve_invoice(invoice)
            lines = invoice_obj.get('lines')
            datalist = []
            for i in lines.get('data'):
                if i.get('description') and i.get('invoice_item'):
                    dataobj = {'description':i.get('description'),'invoice_item':i.get('invoice_item')}
                    datalist.append(dataobj)
            return datalist
        return None
