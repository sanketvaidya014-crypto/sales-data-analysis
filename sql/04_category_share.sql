SELECT category, ROUND(SUM(revenue),2) revenue, ROUND(100.0*SUM(revenue)/NULLIF(SUM(SUM(revenue)) OVER (),0),2) share_pct FROM sales GROUP BY category ORDER BY SUM(revenue) DESC;
