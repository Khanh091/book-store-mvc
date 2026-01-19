START TRANSACTION;

-- 1) Customer
INSERT INTO store_customer (id, name, email, password)
VALUES
  (1, 'Nguyen Van A', 'a@example.com', '123456'),
  (2, 'Tran Thi B', 'b@example.com', '123456');

-- 2) Payment methods
INSERT INTO store_payment (id, method_name, status)
VALUES
  (1, 'COD (Cash on Delivery)', 'active'),
  (2, 'Bank Transfer', 'active'),
  (3, 'Momo', 'active');

-- 3) Shipping methods
INSERT INTO store_shipping (id, method_name, fee)
VALUES
  (1, 'Standard', 15000.00),
  (2, 'Express', 30000.00);

-- 4) Books
INSERT INTO store_book (id, title, author, price, stock_quantity)
VALUES
  (1, 'Clean Code', 'Robert C. Martin', 250000.00, 50),
  (2, 'Design Patterns', 'GoF', 300000.00, 30),
  (3, 'Refactoring', 'Martin Fowler', 280000.00, 20),
  (4, 'Python Crash Course', 'Eric Matthes', 220000.00, 40);

-- 5) Cart (active) + items for customer 1
INSERT INTO store_cart (id, is_active, customer_id)
VALUES (1, 1, 1);

INSERT INTO store_cartitem (id, quantity, book_id, cart_id)
VALUES
  (1, 2, 1, 1), -- 2 x Clean Code
  (2, 1, 4, 1); -- 1 x Python Crash Course

-- 6) Order + OrderItems (ví dụ đã đặt hàng)
INSERT INTO store_order (id, total_price, created_at, customer_id, payment_id, shipping_id)
VALUES
  (1, 250000.00 * 2 + 220000.00 * 1 + 15000.00, NOW(6), 1, 1, 1);

INSERT INTO store_orderitem (id, quantity, price, book_id, order_id)
VALUES
  (1, 2, 250000.00, 1, 1),
  (2, 1, 220000.00, 4, 1);

-- 7) Ratings (để có dữ liệu gợi ý)
INSERT INTO store_rating (id, score, book_id, customer_id)
VALUES
  (1, 5, 1, 1),
  (2, 4, 4, 1),
  (3, 5, 1, 2),
  (4, 4, 2, 2);

COMMIT;