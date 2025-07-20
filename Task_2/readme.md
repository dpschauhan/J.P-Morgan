# Gas Storage Contract Pricing Model

This project implements a gas storage contract pricing model in Python. It allows users to simulate and optimize gas storage strategies based on historical price data, storage constraints, and operational costs.

## Files

- `gas_storage_pricing.py`: Main Python module containing the `GasStoragePricer` class and example test cases.
- `Nat_Gas.csv`: Dataset containing historical natural gas prices (used for price interpolation).

## Features

- **Flexible Storage Strategy**: Supports multiple injection and withdrawal dates, storage capacity limits, and injection/withdrawal rate constraints.
- **Cost Modeling**: Accounts for daily storage costs per unit.
- **Price Interpolation**: Estimates prices for any date using linear interpolation from historical data.
- **Optimization**: Provides a simple greedy optimization to maximize contract value.
- **Valuation Summary**: Prints a detailed summary of the optimal strategy and contract value.
- **Sensitivity Analysis**: Includes examples for analyzing the impact of different storage cost rates.

## Example Usage

Run the script directly to see example test cases and valuation summaries:

```sh
python [gas_storage_pricing.py](http://_vscodecontentref_/0)