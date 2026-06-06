# Razorpay Payment Integration Plan

This plan introduces a payment checkout flow using the Razorpay API. It allows buyers to pay for their orders online, tracks payment status in the database, and provides a polished checkout experience, including a fallback simulated/mock payment screen when using test keys.

## User Review Required

> [!IMPORTANT]
> - **Dependency**: We will install the Python `razorpay` library.
> - **Database Migrations**: We will modify the `Order` model in `orders/models.py` to add payment tracking fields. Running migrations is required.
> - **Testing Keys**: By default, we use dummy test keys. If you want to use your actual Razorpay keys, you can specify them in `settings.py` or as environment variables.

---

## Proposed Changes

### Component 1: Dependencies & Settings
- Install the `razorpay` Python library.
- Configure Razorpay API credentials in `settings.py` with dummy defaults.

#### [MODIFY] [settings.py](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/kisaan_mandi/settings.py)
Add Razorpay keys and default config:
```python
# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_dummy12345')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'dummysecret12345')
```

---

### Component 2: Models & Migrations
- Modify `Order` model in the `orders` app to track payment status and Razorpay identifiers.

#### [MODIFY] [models.py](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/orders/models.py)
- Add choices for payment status (`pending`, `paid`, `failed`).
- Add fields: `payment_status`, `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`.

---

### Component 3: Views, URLs & Admin
- Add backend logic to create Razorpay orders, verify signatures, and handle success/failure states.
- Expose payment details in Django Admin.

#### [MODIFY] [views.py](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/orders/views.py)
- Update `place_order`: If payment method is `online` or `upi`, redirect to the new payment gateway view.
- Create `payment_checkout(request, order_id)`: Initialize Razorpay client, create Razorpay Order, handle fallback/mock mode if keys are dummy or API fails.
- Create `payment_verify(request, order_id)`: Verify signature using Razorpay client (or skip if mock/dummy key) and update payment status to `paid` and order status to `confirmed`.
- Create `payment_success(request, order_id)`: Render a success page.
- Create `payment_failed(request, order_id)`: Render a failure page.

#### [MODIFY] [urls.py](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/orders/urls.py)
Add routes:
- `path('<int:order_id>/payment/', views.payment_checkout, name='payment_checkout'),`
- `path('<int:order_id>/payment/verify/', views.payment_verify, name='payment_verify'),`
- `path('<int:order_id>/payment/success/', views.payment_success, name='payment_success'),`
- `path('<int:order_id>/payment/failed/', views.payment_failed, name='payment_failed'),`

#### [MODIFY] [admin.py](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/orders/admin.py)
- Include `payment_status`, `razorpay_order_id`, and `razorpay_payment_id` in `list_display` and `list_filter`.

---

### Component 4: Templates & Styling
- Add premium templates matching the trilingual design of Kisaan Mandi.

#### [NEW] [payment.html](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/templates/orders/payment.html)
- Display order billing summary.
- Standard Integration: Render Razorpay Checkout button and scripts.
- Mock Mode fallback: Render a beautiful interactive simulated checkout screen (with tabs for Cards, UPI, Netbanking) and options to "Simulate Payment Success" or "Simulate Payment Failure".

#### [NEW] [payment_success.html](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/templates/orders/payment_success.html)
- A highly polished trilingual success page featuring a checkmark animation, transaction summary, and redirect options.

#### [NEW] [payment_failed.html](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/templates/orders/payment_failed.html)
- A failure screen with error illustration and an option to retry checkout.

#### [MODIFY] [order_detail.html](file:///c:/Users/dell/OneDrive/Desktop/kisaan_mandi_trilingual/kisaan_mandi/templates/orders/order_detail.html)
- Display `Payment Status` alongside payment method.
- Show a prominent "Pay Now / भुगतान करें" button for buyers if `payment_status` is not `'paid'` and payment method is `online`/`upi`.

---

## Verification Plan

### Automated Tests
- Run Django database checks to ensure migrations are applied correctly:
  ```bash
  python manage.py check
  ```

### Manual Verification
1. Log in as a buyer (e.g., `demo_buyer`).
2. Go to the marketplace and select a product.
3. Choose **Online Payment** or **UPI** as the payment method and confirm order.
4. Verify redirection to `/orders/<id>/payment/`.
5. On the checkout page, verify:
   - Payment summary, amount, and address details are shown.
   - If using mock mode: Test cards, UPI tabs work, and trigger "Simulate Payment Success".
6. Confirm payment redirects to the success page with a green checkmark animation.
7. Return to "My Orders" -> Order details and confirm:
   - Payment Status displays as "Paid / भुगतान हो गया" (green badge).
   - Order Status updates to "Confirmed".
8. Test payment failure path and confirm the retry button redirects back to checkout.
