# FICO Score Binning & Loan Default Analysis

This project analyzes the relationship between FICO scores and loan default rates using optimal binning and log-likelihood maximization. It demonstrates how to segment credit scores to better understand risk and inform lending decisions.

## Files

- `Loan.ipynb`: Jupyter Notebook containing the full workflow for data loading, binning, and log-likelihood calculations.
- `Task 3 and 4_Loan_Data.csv`: Dataset with customer loan and financial information.

## Features

- **Optimal Binning**: Segments FICO scores into bins to maximize the log-likelihood of default prediction.
- **Log-Likelihood Calculation**: Uses statistical methods to evaluate the quality of each binning strategy.
- **Interpretability**: Outputs the optimal bin edges and the associated log-likelihood value.

## Example Usage

Open and run the notebook cells in `Loan.ipynb` to reproduce the analysis and results. The notebook includes code for:

- Loading and preprocessing the data
- Calculating cumulative defaults and totals by FICO score
- Performing dynamic programming to find optimal bins
- Printing the optimal bin edges and log-likelihood

## Requirements

- Python 3.x
- pandas
- numpy

Install dependencies with:
```sh
pip install pandas numpy