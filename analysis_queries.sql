-- Bangladesh Inflation & Banking Analysis (SQLite). Table: economy (built from src/bdlib.py, 16 rows, 2010-2025)

-- Q1. Top 5 inflation years (RANK)
SELECT Year, ROUND(cpi,2) AS inflation, RANK() OVER (ORDER BY cpi DESC) AS rnk
FROM economy ORDER BY cpi DESC LIMIT 5;

-- Q2. Food inflation vs overall inflation: which years was food worse?
SELECT Year, ROUND(cpi,2) AS overall, ROUND(food,2) AS food, ROUND(food_gap,2) AS gap,
       CASE WHEN food_gap > 0 THEN 'Food worse' ELSE 'Food milder' END AS verdict
FROM economy WHERE food IS NOT NULL ORDER BY gap DESC;

-- Q3. Real lending rate (lending rate - inflation). Deposit rate column is EMPTY in source, so this is the substitute.
SELECT Year, ROUND(cpi,2) AS inflation, ROUND(lending_rate,2) AS lending_rate, ROUND(real_lending_rate,2) AS real_lending_rate
FROM economy ORDER BY real_lending_rate LIMIT 6;

-- Q4. Real deposit growth: did deposits grow slower than prices? (negative = deposits lost value in real terms)
SELECT Year, ROUND(deposit_growth,2) AS deposit_growth, ROUND(cpi,2) AS inflation, ROUND(real_deposit_growth,2) AS real_growth
FROM economy WHERE deposit_growth IS NOT NULL ORDER BY real_growth LIMIT 5;

-- Q5. Two eras compared (CTE + CASE). Better than the source High_Inflation_Flag, which is dominated by one NPL outlier
WITH e AS (SELECT *, CASE WHEN Year >= 2022 THEN '2022-2025' ELSE '2010-2021' END AS era FROM economy)
SELECT era, COUNT(*) AS years, ROUND(AVG(cpi),2) AS avg_inflation, ROUND(AVG(npl),2) AS avg_npl,
       ROUND(AVG(credit_growth),2) AS avg_credit_growth, ROUND(AVG(deposit_growth),2) AS avg_deposit_growth,
       ROUND(AVG(m2_growth),2) AS avg_m2_growth, ROUND(AVG(depreciation),2) AS avg_depreciation,
       ROUND(AVG(real_lending_rate),2) AS avg_real_lending
FROM e GROUP BY era ORDER BY era;

-- Q6. High-inflation years (>= 8%) vs others, NPL shown with and without the 2024 outlier
SELECT CASE WHEN cpi >= 8 THEN 'High (>=8%)' ELSE 'Normal' END AS grp, COUNT(*) AS years,
       ROUND(AVG(npl),2) AS avg_npl_all, ROUND(AVG(CASE WHEN Year <> 2024 THEN npl END),2) AS avg_npl_ex_2024
FROM economy GROUP BY grp;

-- Q7. Year-on-year change in inflation (LAG) and biggest accelerations
SELECT Year, ROUND(cpi,2) AS inflation, ROUND(cpi - LAG(cpi) OVER (ORDER BY Year),2) AS change_pts
FROM economy ORDER BY change_pts DESC LIMIT 5;

-- Q8. Does depreciation lead inflation? Depreciation this year vs inflation NEXT year (LEAD)
SELECT Year, ROUND(depreciation,2) AS depreciation, ROUND(LEAD(cpi) OVER (ORDER BY Year),2) AS next_year_inflation
FROM economy WHERE depreciation IS NOT NULL ORDER BY depreciation DESC LIMIT 6;

-- Q9. Bank funding tightness: private credit as % of deposits, with 3-year moving average
SELECT Year, ROUND(loan_to_deposit,1) AS credit_to_deposit,
       ROUND(AVG(loan_to_deposit) OVER (ORDER BY Year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),1) AS moving_avg_3y
FROM economy ORDER BY Year;

-- Q10. Data quality: years with missing key values
SELECT Year, npl IS NULL AS npl_missing, food IS NULL AS food_missing, credit_growth IS NULL AS credit_missing
FROM economy WHERE npl IS NULL OR food IS NULL OR credit_growth IS NULL;
