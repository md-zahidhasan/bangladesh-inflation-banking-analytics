
# Bangladesh Inflation & Banking Analytics

An interactive data analytics dashboard for exploring the relationship between **inflation and banking-sector indicators in Bangladesh**.

The project combines economic and banking data with SQL-based analysis and an interactive Streamlit dashboard. It allows users to explore inflation trends, food inflation, lending rates, non-performing loans (NPL), credit growth, deposit growth, exchange-rate depreciation, money supply growth, and bank funding indicators across different years.

## Project Overview

This project provides an interactive analytical view of Bangladesh's inflation and banking-sector dynamics.

The application processes the raw Bangladesh economic dataset, builds derived financial indicators, stores the analytical dataset in an in-memory SQLite database, and uses SQL queries to generate the results displayed in the dashboard.

The dashboard is built with **Streamlit** and uses **Plotly** for interactive visualizations.

## Key Features

* Interactive Bangladesh inflation and banking dashboard
* Annual inflation trend analysis
* Food inflation vs. overall inflation comparison
* Lending rate and real lending rate analysis
* Deposit growth vs. inflation analysis
* Non-performing loan (NPL) analysis
* Private-sector credit growth analysis
* Exchange-rate depreciation analysis
* Broad money (M2) growth calculation
* Credit-to-deposit ratio analysis
* Three-year moving average analysis
* High-inflation vs. normal-inflation comparison
* Year-over-year inflation change analysis
* Exchange-rate depreciation vs. following-year inflation analysis
* Data-quality and missing-value checks
* Adjustable year range
* Adjustable high-inflation threshold
* Adjustable era comparison
* Optional SQL display for each dashboard analysis

## Dashboard

The Streamlit application provides interactive controls for:

* Year range
* Number of rows displayed in top/worst lists
* High-inflation threshold
* Recent-era starting year
* NPL outlier year
* SQL visibility

These controls allow users to explore the dataset from different analytical perspectives.

## Data Analysis

The project creates several derived indicators from the raw dataset.

### Inflation

The dashboard analyzes annual CPI inflation and allows users to identify the highest-inflation years.

### Food Inflation

Food inflation is compared with overall CPI inflation using a calculated food-inflation gap:

```text
Food Inflation Gap = Food Inflation - Overall Inflation
```

### Real Lending Rate

The real lending rate is calculated as:

```text
Real Lending Rate = Lending Rate - Inflation
```

This provides a simple inflation-adjusted view of lending rates.

### Real Deposit Growth

Real deposit growth is calculated as:

```text
Real Deposit Growth = Deposit Growth - Inflation
```

This helps compare deposit growth with the prevailing inflation rate.

### Money Supply Growth

M2 growth is calculated from the change in the broad-money series:

```text
M2 Growth = Percentage Change in M2
```

### Credit-to-Deposit Ratio

The project calculates private-sector credit relative to total deposits:

```text
Credit-to-Deposit Ratio =
Private Sector Claims / Total Deposits × 100
```

A three-year moving average is also calculated for this indicator.

## SQL Analysis

The project includes a dedicated `analysis_queries.sql` file containing 10 analytical queries.

The queries cover:

1. Top inflation years
2. Food inflation vs. overall inflation
3. Real lending rate
4. Real deposit growth
5. Comparison of earlier and recent periods
6. High-inflation vs. normal-inflation periods
7. Year-over-year inflation changes
8. Exchange-rate depreciation vs. following-year inflation
9. Credit-to-deposit ratio and three-year moving average
10. Data-quality and missing-value checks

The SQL analysis uses SQLite window functions such as `RANK()`, `LAG()`, `LEAD()`, and moving averages.

## Project Structure

```text
bangladesh-inflation-banking-analytics/
│
├── app.py
├── analysis_queries.sql
├── bangladesh_master_raw.csv
├── inflation_banking_eda.ipynb
├── config.toml
├── requirements.txt
└── README.md
```

### `app.py`

Main Streamlit application containing:

* Data loading
* Data transformation
* Derived financial metrics
* SQLite setup
* SQL queries
* Interactive dashboard
* Plotly visualizations
* Dashboard styling

The application reads the CSV dataset, constructs the analytical `economy` table, and executes SQL queries against an in-memory SQLite database.

### `analysis_queries.sql`

Contains the project's SQL-based analytical queries.

### `bangladesh_master_raw.csv`

Raw dataset used by the dashboard.

### `inflation_banking_eda.ipynb`

Jupyter Notebook for exploratory data analysis and analytical development.

### `config.toml`

Project configuration file.

### `requirements.txt`

Python dependencies required by the project.

## Technologies Used

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**
* **Plotly**
* **SQLite**
* **SQL**
* **Jupyter Notebook**

The current dependency file specifies Streamlit, Pandas, NumPy, and Plotly.

## Installation

Clone the repository:

```bash
git clone https://github.com/md-zahidhasan/bangladesh-inflation-banking-analytics.git
```

Navigate to the project directory:

```bash
cd bangladesh-inflation-banking-analytics
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

## Methodology

The application first loads the raw CSV dataset using Pandas.

It then constructs an analytical dataset containing the core economic and banking indicators. Several derived metrics are calculated, including food inflation gap, real lending rate, real deposit growth, M2 growth, and loan-to-deposit ratio.

The processed data is loaded into an in-memory SQLite database. SQL queries are then executed to generate analytical results for the dashboard.

The dashboard presents these results through interactive tables and Plotly visualizations.

## Analytical Scope

The project focuses on understanding relationships between:

* Inflation and food prices
* Inflation and lending rates
* Inflation and deposit growth
* Inflation and banking-sector risk indicators
* Exchange-rate depreciation and subsequent inflation
* Credit availability and deposits
* Money supply growth and broader economic conditions

## Data Quality

The project includes a dedicated SQL query for identifying missing values in important indicators such as:

* NPL
* Food inflation
* Credit growth

This helps identify potential limitations in the underlying dataset.

## Future Improvements

Potential future improvements include:

* Adding more macroeconomic indicators
* Adding monthly or quarterly data
* Adding automated data updates
* Adding geographic-level analysis
* Adding forecasting models
* Adding machine-learning-based inflation forecasting
* Adding more banking-sector indicators
* Deploying the Streamlit dashboard online
* Adding automated data validation
* Improving dashboard accessibility and responsiveness

## Author

**Md Zahid Hasan**

GitHub:
https://github.com/md-zahidhasan

## License

This project does not currently specify a license. If you intend to make the project reusable or open source, consider adding an appropriate license file.
