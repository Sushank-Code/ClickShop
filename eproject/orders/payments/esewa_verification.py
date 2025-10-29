import base64,requests
import json
from orders.models import Order,Payment


def verify_esewa_payment(request,data_encoded,order_number):

    try:
        decoded_bytes = base64.b64decode(data_encoded)      # base64 text to raw bytes
        decoded_str = decoded_bytes.decode('utf-8')          # bytes to string
        payment_info = json.loads(decoded_str)               # string with json text to python dictionary

        transaction_uuid = payment_info.get("transaction_uuid")         # accessing dictionary
        product_code = payment_info.get("product_code")
        total_amount = payment_info.get("total_amount")

        verify_url = "https://rc.esewa.com.np/api/epay/transaction/status/"
        payload = {
            "product_code": product_code,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
        }

        response = requests.post(verify_url, json=payload)
        result = response.json()                              # http text to python dict

        if result.get("status") ==  "COMPLETE":
            order = Order.objects.get(user = request.user , is_ordered = False,order_number=order_number)
            if order:
                order.payment = payment
                order.is_ordered = True
                order.save()
            payment = Payment(
               user = request.user,
               payment_id = result.get("ref_id"),
               transaction_uuid = result.get("transaction_uuid"),
               payment_method = order.payment_option,
               amount_paid = result.get("total_amount"),
               status = result.get("status")
            )
            payment.save()
    except Exception as e:
        raise e
