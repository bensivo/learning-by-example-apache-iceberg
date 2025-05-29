SELECT b.browser, d.day_of_week, count(*) as num_page_loads FROM star.fact_page_load AS pl
    LEFT JOIN star.dim_browser AS b on b.browser_id = pl.browser_id
    LEFT JOIN star.dim_date AS d on d.date_id = pl.date_id
    GROUP BY b.browser, d.day_of_week