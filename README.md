# Clothez

## Description
This is an eCommerce template that allows for both signed-in and guest add to cart and checkout functionality. Checkout payment is made through PayPal, and empties the cart upon a successful transaction.

### Feature and Functionality Overview
  - Cart
    - add to cart only if item is in stock
    - increase/decrease item quantity
  - Wishlist
    - add to wishlist even if item is out of stock
    - move item from wishlist to cart
  - Search
    - single input in nav bar
    - multi-input on search page (keyword, gender, category, max-price)
  - Admin Dashboard
    - view all users, customers, products, orders, etc.
    - search for customers by last name
    - filter products by category, type, and gender
    - CRUD
      - users, customers, products, orders
      - homepage banner
      - page content (about, contact, privacy-policy)
    - send email to customer when order ships
      - choose between a stock email with pre-written message or compose a new email from scratch
  - Email Confirmation
    - confirm sign-up
    - reset password
  - Customer Account Page
    - change password
    - view orders
  - Product Reviews
    - only if signed-in and have purchase history
    - limit to 1 per customer
    - leave rating and comment
    - show average rating
  - Orders
    - send email to both customer and admin upon transaction completion
