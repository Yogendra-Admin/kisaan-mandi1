from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from marketplace.models import Product, Category
from orders.models import Cart, Order, Notification

User = get_user_model()

class CartCheckoutTests(TestCase):
    def setUp(self):
        # Create users
        self.farmer = User.objects.create_user(
            username='farmer1', password='Password123!', role='farmer', first_name='Farmer'
        )
        self.buyer = User.objects.create_user(
            username='buyer1', password='Password123!', role='buyer', first_name='Buyer'
        )
        
        # Create category
        self.category = Category.objects.create(name='Fruits', slug='fruits')
        
        # Create products
        self.product1 = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Apple',
            price_per_unit=120.00,
            quantity_available=100.0,
            status='active'
        )
        self.product2 = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Banana',
            price_per_unit=40.00,
            quantity_available=150.0,
            status='active'
        )
        
        # Log in buyer client
        self.client = Client()
        self.client.login(username='buyer1', password='Password123!')

    def test_cart_subtotal_property(self):
        cart_item = Cart.objects.create(buyer=self.buyer, product=self.product1, quantity=3.0)
        self.assertEqual(cart_item.subtotal, 360.00)

    def test_place_cart_order_cod(self):
        # Add products to cart
        Cart.objects.create(buyer=self.buyer, product=self.product1, quantity=2.0)
        Cart.objects.create(buyer=self.buyer, product=self.product2, quantity=5.0)
        
        url = reverse('place_cart_order')
        
        # Submit place cart order form with COD
        data = {
            'payment_method': 'cod',
            'delivery_address': '123 Mandi Street, Delhi',
            'notes': 'Deliver in evening'
        }
        
        response = self.client.post(url, data=data)
        
        # Verify redirect to my orders page
        self.assertRedirects(response, reverse('my_orders'))
        
        # Verify cart is cleared
        self.assertFalse(Cart.objects.filter(buyer=self.buyer).exists())
        
        # Verify Orders are created
        orders = Order.objects.filter(buyer=self.buyer)
        self.assertEqual(orders.count(), 2)
        
        order1 = orders.get(product=self.product1)
        self.assertEqual(order1.quantity, 2.0)
        self.assertEqual(order1.total_price, 240.00)
        self.assertEqual(order1.payment_method, 'cod')
        self.assertEqual(order1.delivery_address, '123 Mandi Street, Delhi')
        self.assertEqual(order1.notes, 'Deliver in evening')
        self.assertEqual(order1.payment_status, 'pending')
        
        order2 = orders.get(product=self.product2)
        self.assertEqual(order2.quantity, 5.0)
        self.assertEqual(order2.total_price, 200.00)

    def test_place_cart_order_online_payment(self):
        # Add products to cart
        Cart.objects.create(buyer=self.buyer, product=self.product1, quantity=2.0) # total = 240
        Cart.objects.create(buyer=self.buyer, product=self.product2, quantity=5.0) # total = 200
        # Combined total = 440
        
        url = reverse('place_cart_order')
        data = {
            'payment_method': 'online',
            'delivery_address': '456 Farm Road, Kathmandu',
            'notes': ''
        }
        
        response = self.client.post(url, data=data)
        
        # Verify cart items are NOT cleared yet for online payment checkout
        self.assertTrue(Cart.objects.filter(buyer=self.buyer).exists())
        
        # Should redirect to payment checkout with the first order id
        orders = Order.objects.filter(buyer=self.buyer)
        self.assertEqual(orders.count(), 2)
        first_order = orders.order_by('id').first()
        
        # Both orders should share the temporary group ID in razorpay_order_id initially
        group_id = first_order.razorpay_order_id
        self.assertTrue(group_id.startswith('cart_'))
        for o in orders:
            self.assertEqual(o.razorpay_order_id, group_id)
            self.assertEqual(o.payment_method, 'online')
            self.assertEqual(o.payment_status, 'pending')

        self.assertRedirects(response, reverse('payment_checkout', kwargs={'order_id': first_order.id}))
            
        # Verify checkout view loads combined totals
        checkout_url = reverse('payment_checkout', kwargs={'order_id': first_order.id})
        checkout_response = self.client.get(checkout_url)
        self.assertEqual(checkout_response.status_code, 200)
        self.assertEqual(checkout_response.context['total_price'], 440.00)
        self.assertEqual(checkout_response.context['amount_paise'], 44000)
        
        # Verify orders are updated with a Razorpay order ID in test mode
        for o in orders:
            o.refresh_from_db()
            self.assertTrue(o.razorpay_order_id.startswith('order_'))
            
        first_order.refresh_from_db()
        mock_razorpay_order_id = first_order.razorpay_order_id
        
        # Verify payment verification verifies all orders in the group
        verify_url = reverse('payment_verify', kwargs={'order_id': first_order.id})
        verify_data = {
            'razorpay_payment_id': 'pay_mock_12345',
            'razorpay_order_id': mock_razorpay_order_id,
            'razorpay_signature': 'signature_mock_12345',
            'is_mocked': 'true'
        }
        
        verify_response = self.client.post(verify_url, data=verify_data)
        self.assertRedirects(verify_response, reverse('payment_success', kwargs={'order_id': first_order.id}))
        
        # Verify cart is now cleared after successful payment verification
        self.assertFalse(Cart.objects.filter(buyer=self.buyer).exists())
        
        # Both orders should now be updated to paid and confirmed
        for o in orders:
            o.refresh_from_db()
            self.assertEqual(o.payment_status, 'paid')
            self.assertEqual(o.status, 'confirmed')
            self.assertEqual(o.razorpay_payment_id, 'pay_mock_12345')

    def test_add_to_cart_with_quantity_get(self):
        # Adding with quantity via GET parameter
        url = reverse('add_to_cart', kwargs={'product_id': self.product1.id})
        response = self.client.get(url + '?quantity=5.5')
        self.assertRedirects(response, reverse('cart'))
        
        cart_item = Cart.objects.get(buyer=self.buyer, product=self.product1)
        self.assertEqual(float(cart_item.quantity), 5.5)

    def test_add_to_cart_with_quantity_post(self):
        # Adding with quantity via POST data
        url = reverse('add_to_cart', kwargs={'product_id': self.product1.id})
        response = self.client.post(url, data={'quantity': '12.5'})
        self.assertRedirects(response, reverse('cart'))
        
        cart_item = Cart.objects.get(buyer=self.buyer, product=self.product1)
        self.assertEqual(float(cart_item.quantity), 12.5)

    def test_add_to_cart_exceeds_available(self):
        # Quantity available for product1 is 100.0. Try to add 150.0.
        url = reverse('add_to_cart', kwargs={'product_id': self.product1.id})
        response = self.client.post(url, data={'quantity': '150.0'})
        self.assertRedirects(response, reverse('cart'))
        
        cart_item = Cart.objects.get(buyer=self.buyer, product=self.product1)
        # Should be capped at product's maximum available quantity (100.0)
        self.assertEqual(float(cart_item.quantity), 100.0)

    def test_buy_now_prepopulates_quantity(self):
        # User clicks Buy Now with quantity 4.5
        url = reverse('place_order', kwargs={'product_id': self.product1.id})
        response = self.client.get(url + '?quantity=4.5')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.initial.get('quantity'), '4.5')

    def test_place_order_with_upi(self):
        # Place a single order using UPI payment method
        url = reverse('place_order', kwargs={'product_id': self.product1.id})
        data = {
            'quantity': '3.0',
            'payment_method': 'upi',
            'delivery_address': '789 UPI Street, Mumbai',
            'notes': 'Fast delivery please'
        }
        response = self.client.post(url, data=data)
        
        order = Order.objects.filter(buyer=self.buyer, product=self.product1).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_method, 'upi')
        self.assertEqual(float(order.quantity), 3.0)
        self.assertEqual(float(order.total_price), 360.00)
        
        # Verify redirect to payment checkout page
        self.assertRedirects(response, reverse('payment_checkout', kwargs={'order_id': order.id}))
        
        # Verify payment page context is prefilled for UPI
        checkout_url = reverse('payment_checkout', kwargs={'order_id': order.id})
        checkout_response = self.client.get(checkout_url)
        self.assertEqual(checkout_response.status_code, 200)
        self.assertEqual(checkout_response.context['order'].payment_method, 'upi')

    def test_verify_direct_upi_utr(self):
        # Create a test UPI order
        order = Order.objects.create(
            buyer=self.buyer,
            product=self.product1,
            quantity=2.0,
            total_price=240.00,
            payment_method='upi',
            payment_status='pending',
            status='pending',
            delivery_address='456 Mandi Lane'
        )
        
        # Add products to cart to ensure they are cleared upon payment verification
        Cart.objects.create(buyer=self.buyer, product=self.product1, quantity=2.0)
        
        # Verify submitting UTR number works and marks order as paid
        verify_url = reverse('payment_verify', kwargs={'order_id': order.id})
        response = self.client.post(verify_url, data={'utr_number': '987654321012'})
        
        self.assertRedirects(response, reverse('payment_success', kwargs={'order_id': order.id}))
        
        # Verify cart is cleared
        self.assertFalse(Cart.objects.filter(buyer=self.buyer).exists())
        
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(order.status, 'confirmed')
        self.assertEqual(order.razorpay_payment_id, '987654321012')
        self.assertEqual(order.razorpay_signature, 'utr_verified_987654321012')

    def test_notifications_flow(self):
        # 1. Verify placing an order creates notifications for both buyer and farmer
        url = reverse('place_order', kwargs={'product_id': self.product1.id})
        data = {
            'quantity': '2.0',
            'payment_method': 'cod',
            'delivery_address': '123 Test Road',
            'notes': ''
        }
        self.client.post(url, data=data)
        
        # Check notifications count
        self.assertTrue(Notification.objects.filter(user=self.buyer).exists())
        self.assertTrue(Notification.objects.filter(user=self.farmer).exists())
        
        # 2. Verify status update creates notifications
        order = Order.objects.filter(buyer=self.buyer, product=self.product1).first()
        
        # Log in as farmer to update status
        self.client.login(username='farmer1', password='Password123!')
        status_url = reverse('update_order_status', kwargs={'pk': order.id})
        self.client.post(status_url, data={'status': 'dispatched'})
        
        # Buyer should have a notification about status update to dispatched
        buyer_notif = Notification.objects.filter(user=self.buyer).order_by('-created_at').first()
        self.assertIn("Dispatched", buyer_notif.message_en)
        
        # 3. Mark notification as read
        self.client.login(username='buyer1', password='Password123!')
        read_url = reverse('mark_notification_read', kwargs={'pk': buyer_notif.pk})
        response = self.client.get(read_url)
        self.assertEqual(response.status_code, 302) # redirect back
        
        buyer_notif.refresh_from_db()
        self.assertTrue(buyer_notif.is_read)
        
        # 4. Clear notifications
        clear_url = reverse('clear_notifications')
        self.client.get(clear_url)
        self.assertFalse(Notification.objects.filter(user=self.buyer).exists())

    def test_my_orders_filtering(self):
        # Create different orders with different statuses
        Order.objects.create(
            buyer=self.buyer, product=self.product1, quantity=1, total_price=120, status='pending'
        )
        Order.objects.create(
            buyer=self.buyer, product=self.product1, quantity=1, total_price=120, status='delivered'
        )
        Order.objects.create(
            buyer=self.buyer, product=self.product1, quantity=1, total_price=120, status='cancelled'
        )
        
        # Test unfiltered My Orders
        self.client.login(username='buyer1', password='Password123!')
        response = self.client.get(reverse('my_orders'))
        self.assertEqual(len(response.context['orders']), 3)
        
        # Filter by pending
        response = self.client.get(reverse('my_orders') + '?status=pending')
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0].status, 'pending')
        
        # Filter by delivered
        response = self.client.get(reverse('my_orders') + '?status=delivered')
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0].status, 'delivered')

    def test_buyer_cancel_order(self):
        # Buyer cancels pending order
        order = Order.objects.create(
            buyer=self.buyer, product=self.product1, quantity=1, total_price=120, status='pending'
        )
        self.client.login(username='buyer1', password='Password123!')
        url = reverse('update_order_status', kwargs={'pk': order.id})
        
        response = self.client.post(url, {'status': 'cancelled'})
        self.assertRedirects(response, reverse('order_detail', kwargs={'pk': order.id}))
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

        # Buyer attempts to cancel dispatched order (should fail)
        order2 = Order.objects.create(
            buyer=self.buyer, product=self.product1, quantity=1, total_price=120, status='dispatched'
        )
        url2 = reverse('update_order_status', kwargs={'pk': order2.id})
        response = self.client.post(url2, {'status': 'cancelled'})
        order2.refresh_from_db()
        self.assertEqual(order2.status, 'dispatched') # should remain unchanged

    def test_buyer_accept_product_and_cod_autopay(self):
        # COD order in dispatched state
        order = Order.objects.create(
            buyer=self.buyer,
            product=self.product1,
            quantity=1,
            total_price=120,
            status='dispatched',
            payment_method='cod',
            payment_status='pending'
        )
        self.client.login(username='buyer1', password='Password123!')
        url = reverse('update_order_status', kwargs={'pk': order.id})
        
        # Buyer accepts product (Confirm Delivery)
        response = self.client.post(url, {'status': 'delivered'})
        self.assertRedirects(response, reverse('order_detail', kwargs={'pk': order.id}))
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')
        self.assertEqual(order.payment_status, 'paid') # COD automatically marks as paid upon delivery

        # Verify notification created
        buyer_notif = Notification.objects.filter(user=self.buyer).order_by('-created_at').first()
        self.assertIn("delivered", buyer_notif.message_en.lower())

    def test_unauthorized_user_cannot_update_status(self):
        order = Order.objects.create(
            buyer=self.buyer, product=self.product1, quantity=1, total_price=120, status='pending'
        )
        # Create a completely separate user
        other_user = User.objects.create_user(
            username='otheruser', password='Password123!', role='buyer'
        )
        self.client.login(username='otheruser', password='Password123!')
        url = reverse('update_order_status', kwargs={'pk': order.id})
        
        # Try to post status update (should return 404)
        response = self.client.post(url, {'status': 'cancelled'})
        self.assertEqual(response.status_code, 404)


class FarmerPanelTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='farmer_test', password='Password123!', role='farmer', first_name='Farmer'
        )
        self.buyer = User.objects.create_user(
            username='buyer_test', password='Password123!', role='buyer', first_name='Buyer'
        )
        self.category = Category.objects.create(name='Vegetables', slug='vegetables')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Potato',
            price_per_unit=30.00,
            quantity_available=200.0,
            status='active'
        )
        self.client = Client()

    def test_sales_report_restricted_to_farmer(self):
        # Unauthenticated user redirects to login
        url = reverse('sales_report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Buyer user redirects to home
        self.client.login(username='buyer_test', password='Password123!')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

        # Farmer user gets 200 OK
        self.client.login(username='farmer_test', password='Password123!')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders', response.context)
        self.assertIn('sales_data', response.context)
        self.assertIn('svg_points', response.context)

    def test_notifications_list_requires_auth(self):
        # Unauthenticated redirects to login
        url = reverse('notifications_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        # Authenticated user (buyer or farmer) gets 200 OK
        self.client.login(username='buyer_test', password='Password123!')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('notifications', response.context)

    def test_farmer_dashboard_stats(self):
        # Create a pending COD order, a delivered COD order (paid), and a confirmed paid online order
        Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=5.0,
            total_price=150.00,
            status='pending',
            payment_method='cod',
            payment_status='pending',
            delivery_address='Test Address'
        )
        Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=10.0,
            total_price=300.00,
            status='delivered',
            payment_method='cod',
            payment_status='paid',
            delivery_address='Test Address'
        )
        Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=2.0,
            total_price=60.00,
            status='confirmed',
            payment_method='online',
            payment_status='paid',
            delivery_address='Test Address'
        )
        # Create a cancelled paid online order (should be excluded from sales & earnings)
        Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=8.0,
            total_price=240.00,
            status='cancelled',
            payment_method='online',
            payment_status='paid',
            delivery_address='Test Address'
        )

        self.client.login(username='farmer_test', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_products'], 1)
        self.assertEqual(response.context['total_orders'], 4) # still counted as placed order
        self.assertEqual(response.context['pending_orders'], 1)
        self.assertEqual(response.context['completed_orders'], 1)
        self.assertEqual(response.context['total_sales'], 510.00) # 150 + 300 + 60 (excluding 240 cancelled)
        self.assertEqual(response.context['total_earnings'], 360.00) # 300 + 60 (excluding 240 cancelled)

    def test_auto_translation_on_save(self):
        # Create a new product without name_hi and name_ne (should auto-translate)
        p = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Banana',
            price_per_unit=40.00,
            quantity_available=100.0,
            status='active'
        )
        p.refresh_from_db()
        self.assertEqual(p.name_hi, 'केला')
        self.assertEqual(p.name_ne, 'केरा')

    def test_farmer_cannot_mark_as_delivered(self):
        # Create a dispatched order
        order = Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=5.0,
            total_price=150.00,
            status='dispatched',
            payment_method='cod',
            payment_status='pending',
            delivery_address='Test Address'
        )
        # Log in as farmer
        self.client.login(username='farmer_test', password='Password123!')
        url = reverse('update_order_status', kwargs={'pk': order.id})
        
        # Farmer attempts to mark as delivered (should fail)
        response = self.client.post(url, {'status': 'delivered'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'dispatched') # should remain unchanged

    def test_buyer_confirm_delivery_sends_notifications(self):
        from django.core import mail
        mail.outbox.clear()
        
        # Set email addresses so email sending is not skipped
        self.buyer.email = 'buyer_test@example.com'
        self.buyer.save()
        self.farmer.email = 'farmer_test@example.com'
        self.farmer.save()
        
        # Create a dispatched order
        order = Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=5.0,
            total_price=150.00,
            status='dispatched',
            payment_method='cod',
            payment_status='pending',
            delivery_address='Test Address'
        )
        # Log in as buyer
        self.client.login(username='buyer_test', password='Password123!')
        url = reverse('update_order_status', kwargs={'pk': order.id})
        
        # Buyer accepts product (Confirm Delivery)
        response = self.client.post(url, {'status': 'delivered'})
        self.assertRedirects(response, reverse('order_detail', kwargs={'pk': order.id}))
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')
        
        # Verify 2 emails sent (one to buyer, one to farmer)
        self.assertEqual(len(mail.outbox), 2)
        
        # Verify email contents
        buyer_email = mail.outbox[0]
        farmer_email = mail.outbox[1]
        self.assertEqual(buyer_email.to, [self.buyer.email])
        self.assertEqual(farmer_email.to, [self.product.farmer.email])
        self.assertIn("delivered", buyer_email.body.lower())
        self.assertIn("delivered", farmer_email.body.lower())


