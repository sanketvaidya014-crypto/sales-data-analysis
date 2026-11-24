SELECT customer_id, COUNT(DISTINCT order_id) orders, ROUND(SUM(revenue),2) revenue FROM sales WHERE customer_id IS NOT NULL GROUP BY customer_id ORDER BY SUM(revenue) DESC, customer_id LIMIT 10;
