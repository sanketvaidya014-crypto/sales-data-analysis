SELECT product, SUM(quantity) units, ROUND(SUM(revenue),2) revenue FROM sales GROUP BY product ORDER BY SUM(revenue) DESC, product LIMIT 10;
