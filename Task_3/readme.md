# Loan Default Prediction Model

This project implements a logistic regression model in Python to predict loan default risk using customer financial data. It demonstrates feature engineering, model training, and evaluation for credit risk assessment.

## Files

- `loan.ipynb`: Jupyter Notebook containing the full workflow for data loading, feature engineering, model training, and evaluation.
- `Task 3 and 4_Loan_Data.csv`: Dataset with customer loan and financial information.

## Features

- **Feature Engineering**: Calculates key ratios such as payment-to-income and debt-to-income.
- **Model Training**: Fits a logistic regression model to predict the probability of loan default.
- **Evaluation**: Computes accuracy and ROC AUC to assess model performance.
- **Interpretability**: Outputs model coefficients for insight into feature importance.

## Example Usage

Open and run the notebook cells in `loan.ipynb` to reproduce the analysis and results. The notebook includes code for:

- Loading and preprocessing the data
- Engineering features
- Training the logistic regression model
- Evaluating predictions and model performance

## Requirements

- Python 3.x
- pandas
- numpy
- scikit-learn

Install dependencies with:
```sh
pip install pandas numpy scikit-learn