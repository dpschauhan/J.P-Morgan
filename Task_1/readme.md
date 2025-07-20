# Natural Gas Price Estimation & Forecasting

This project analyzes historical monthly natural gas prices, visualizes trends, trains a regression model, and forecasts future prices for 12 months using Python and Jupyter Notebook.

## Files

- `Nat_Gas.ipynb`: Main notebook for data analysis, visualization, regression modeling, and forecasting.
- `Nat_Gas.csv`: Dataset containing historical natural gas prices.

## Steps Performed

1. **Import Libraries**: Utilizes pandas, matplotlib, scikit-learn, and datetime for data handling, visualization, and modeling.
2. **Load Data**: Reads and preprocesses the natural gas price data.
3. **Visualize Data**: Plots historical price trends.
4. **Train Model**: Fits a linear regression model to the historical data.
5. **Forecast Prices**: Predicts natural gas prices for the next 12 months.
6. **Plot Forecast**: Visualizes both historical and forecasted prices.
7. **Estimate Price Function**: Provides a function to estimate the price for any given date.

## Example Usage

- Run the notebook cells sequentially to reproduce the analysis and forecasts.
- Use the `estimate_price('YYYY-MM-DD')` function to estimate the price for a specific date.

## Requirements

- Python 3.x
- pandas
- matplotlib
- scikit-learn
- numpy

Install dependencies with:
```sh
pip install pandas matplotlib scikit-learn numpy