import stripe
from stripe_service import *

# Set your Stripe secret key
stripe.api_key = 'sk_test_51IsaJzJK7wwywY1K08oalOKH7UWogsWBOp4BsbTeKLPwdFYF3VpKORZcdZZYqsUdiivOvRUhKzrs73m1CKTCJnMC00ZnAbrrtU'


name = "JD10"
duration = 'once'
percentage = 100
coupon_obj = Coupon.create_coupon(duration,percentage,name)
print("coupon_obj",coupon_obj)
# coupon_details = Session.retrieve_session("cs_test_b1f2l7HIKuzfWe6O5s2ugaT4fZQrxwo0bOmeUU7mA7BwD56Zsb7RRoN61F")
# price_id = Prices.retrieve_prices("price_1OH135JK7wwywY1KrnjbVejL")

# apply_products = [price_id.product]
# promo_details  = PromoCode.listof_promocode(limit=1000)
# promo_details = [i.get('coupon').get('name') for i in promo_details if i.get('coupon')]
# # promo_creation = PromoCode.create_promocode("9MymRmkq")
# # print(promo_details)
# # promo_details = PromoCode.listof_promocode()
# # coupon_details = Coupon.retrieve_coupon("9MymRmkq")
# print(promo_details)

"9MymRmkq"


