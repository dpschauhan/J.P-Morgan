import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Union
import matplotlib.pyplot as plt

class GasStoragePricer:
    """
    A pricing model for gas storage contracts with multiple injection/withdrawal dates.
    
    The model considers:
    - Multiple injection and withdrawal opportunities
    - Storage capacity constraints
    - Injection/withdrawal rate limits
    - Storage costs over time
    - Market price volatility
    """
    
    def __init__(self, price_data: pd.DataFrame, storage_cost_per_unit_per_day: float = 0.01):
        """
        Initialize the pricing model with historical price data.
        
        Args:
            price_data: DataFrame with 'Dates' and 'Prices' columns
            storage_cost_per_unit_per_day: Daily storage cost per unit of gas
        """
        self.price_data = price_data.copy()
        self.price_data['Dates'] = pd.to_datetime(self.price_data['Dates'])
        self.price_data = self.price_data.sort_values('Dates')
        self.storage_cost_per_unit_per_day = storage_cost_per_unit_per_day
        
    def interpolate_price(self, date: datetime) -> float:
        """
        Interpolate price for a given date using linear interpolation.
        
        Args:
            date: Target date for price interpolation
            
        Returns:
            Interpolated price for the given date
        """
        if date <= self.price_data['Dates'].min():
            return self.price_data.iloc[0]['Prices']
        if date >= self.price_data['Dates'].max():
            return self.price_data.iloc[-1]['Prices']
        
        # Find surrounding dates
        before = self.price_data[self.price_data['Dates'] <= date].iloc[-1]
        after = self.price_data[self.price_data['Dates'] > date].iloc[0]
        
        # Linear interpolation
        days_total = (after['Dates'] - before['Dates']).days
        days_from_before = (date - before['Dates']).days
        
        if days_total == 0:
            return before['Prices']
        
        weight = days_from_before / days_total
        return before['Prices'] * (1 - weight) + after['Prices'] * weight
    
    def calculate_storage_costs(self, inventory_schedule: List[Tuple[datetime, float]]) -> float:
        """
        Calculate total storage costs based on inventory levels over time.
        
        Args:
            inventory_schedule: List of (date, inventory_level) tuples
            
        Returns:
            Total storage costs
        """
        total_cost = 0.0
        
        for i in range(len(inventory_schedule) - 1):
            current_date, current_inventory = inventory_schedule[i]
            next_date, _ = inventory_schedule[i + 1]
            
            days = (next_date - current_date).days
            daily_cost = current_inventory * self.storage_cost_per_unit_per_day
            total_cost += daily_cost * days
            
        return total_cost
    
    def optimize_storage_strategy(self, 
                                injection_dates: List[datetime],
                                withdrawal_dates: List[datetime],
                                injection_withdrawal_rate: float,
                                max_storage_volume: float,
                                contract_start: datetime,
                                contract_end: datetime) -> Dict:
        """
        Optimize the storage strategy to maximize contract value.
        
        This is a simplified optimization that considers all possible injection/withdrawal
        combinations and selects the most profitable strategy.
        
        Args:
            injection_dates: List of possible injection dates
            withdrawal_dates: List of possible withdrawal dates
            injection_withdrawal_rate: Maximum rate of injection/withdrawal per day
            max_storage_volume: Maximum storage capacity
            contract_start: Contract start date
            contract_end: Contract end date
            
        Returns:
            Dictionary with optimal strategy details
        """
        
        # Get prices for all relevant dates
        all_dates = sorted(set(injection_dates + withdrawal_dates + [contract_start, contract_end]))
        price_map = {date: self.interpolate_price(date) for date in all_dates}
        
        # Simple greedy strategy: inject when prices are low, withdraw when high
        injection_prices = [(date, price_map[date]) for date in injection_dates]
        withdrawal_prices = [(date, price_map[date]) for date in withdrawal_dates]
        
        # Sort by price (ascending for injection, descending for withdrawal)
        injection_prices.sort(key=lambda x: x[1])
        withdrawal_prices.sort(key=lambda x: x[1], reverse=True)
        
        # Build optimal strategy
        strategy = []
        current_inventory = 0.0
        total_cash_flow = 0.0
        
        # Combine and sort all operations by date
        all_operations = []
        
        # Add profitable injection opportunities
        for inj_date, inj_price in injection_prices:
            # Check if there are withdrawal opportunities at higher prices
            profitable_withdrawals = [w for w in withdrawal_prices if w[1] > inj_price and w[0] > inj_date]
            if profitable_withdrawals and current_inventory < max_storage_volume:
                volume_to_inject = min(injection_withdrawal_rate, max_storage_volume - current_inventory)
                if volume_to_inject > 0:
                    all_operations.append((inj_date, 'inject', volume_to_inject, inj_price))
        
        # Add profitable withdrawal opportunities
        for with_date, with_price in withdrawal_prices:
            # Check if we have inventory from previous injections
            prior_injections = [op for op in all_operations if op[0] < with_date and op[1] == 'inject']
            if prior_injections:
                # Find the lowest cost injection that hasn't been withdrawn yet
                available_volume = sum(op[2] for op in prior_injections)
                if available_volume > 0:
                    volume_to_withdraw = min(injection_withdrawal_rate, available_volume)
                    all_operations.append((with_date, 'withdraw', volume_to_withdraw, with_price))
        
        # Sort operations by date
        all_operations.sort(key=lambda x: x[0])
        
        # Execute strategy and track inventory
        inventory_schedule = [(contract_start, 0.0)]
        current_inventory = 0.0
        
        for date, operation, volume, price in all_operations:
            if operation == 'inject':
                if current_inventory + volume <= max_storage_volume:
                    current_inventory += volume
                    total_cash_flow -= volume * price  # Cash outflow for purchase
                    strategy.append({
                        'date': date,
                        'operation': 'inject',
                        'volume': volume,
                        'price': price,
                        'cash_flow': -volume * price,
                        'inventory_after': current_inventory
                    })
            elif operation == 'withdraw':
                if current_inventory >= volume:
                    current_inventory -= volume
                    total_cash_flow += volume * price  # Cash inflow from sale
                    strategy.append({
                        'date': date,
                        'operation': 'withdraw',
                        'volume': volume,
                        'price': price,
                        'cash_flow': volume * price,
                        'inventory_after': current_inventory
                    })
            
            inventory_schedule.append((date, current_inventory))
        
        # Add final inventory liquidation at contract end if needed
        if current_inventory > 0:
            end_price = self.interpolate_price(contract_end)
            total_cash_flow += current_inventory * end_price
            strategy.append({
                'date': contract_end,
                'operation': 'liquidate',
                'volume': current_inventory,
                'price': end_price,
                'cash_flow': current_inventory * end_price,
                'inventory_after': 0.0
            })
        
        inventory_schedule.append((contract_end, 0.0))
        
        # Calculate storage costs
        storage_costs = self.calculate_storage_costs(inventory_schedule)
        
        # Calculate final contract value
        contract_value = total_cash_flow - storage_costs
        
        return {
            'strategy': strategy,
            'inventory_schedule': inventory_schedule,
            'total_cash_flow': total_cash_flow,
            'storage_costs': storage_costs,
            'contract_value': contract_value,
            'price_map': price_map
        }
    
    def price_contract(self,
                      injection_dates: List[Union[str, datetime]],
                      withdrawal_dates: List[Union[str, datetime]],
                      injection_withdrawal_rate: float,
                      max_storage_volume: float,
                      contract_start: Union[str, datetime],
                      contract_end: Union[str, datetime],
                      storage_cost_per_unit_per_day: float = None) -> Dict:
        """
        Main function to price the storage contract.
        
        Args:
            injection_dates: List of possible injection dates
            withdrawal_dates: List of possible withdrawal dates
            injection_withdrawal_rate: Maximum injection/withdrawal rate per day
            max_storage_volume: Maximum storage capacity
            contract_start: Contract start date
            contract_end: Contract end date
            storage_cost_per_unit_per_day: Override default storage cost
            
        Returns:
            Dictionary with contract valuation and strategy details
        """
        
        # Convert string dates to datetime objects
        if isinstance(contract_start, str):
            contract_start = datetime.strptime(contract_start, '%Y-%m-%d')
        if isinstance(contract_end, str):
            contract_end = datetime.strptime(contract_end, '%Y-%m-%d')
        
        injection_dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d 
                          for d in injection_dates]
        withdrawal_dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d 
                           for d in withdrawal_dates]
        
        # Override storage cost if provided
        if storage_cost_per_unit_per_day is not None:
            self.storage_cost_per_unit_per_day = storage_cost_per_unit_per_day
        
        # Optimize storage strategy
        result = self.optimize_storage_strategy(
            injection_dates=injection_dates,
            withdrawal_dates=withdrawal_dates,
            injection_withdrawal_rate=injection_withdrawal_rate,
            max_storage_volume=max_storage_volume,
            contract_start=contract_start,
            contract_end=contract_end
        )
        
        return result
    
    def print_valuation_summary(self, result: Dict):
        """Print a formatted summary of the contract valuation."""
        print("=" * 60)
        print("GAS STORAGE CONTRACT VALUATION SUMMARY")
        print("=" * 60)
        print(f"Contract Value: ${result['contract_value']:,.2f}")
        print(f"Total Cash Flow: ${result['total_cash_flow']:,.2f}")
        print(f"Storage Costs: ${result['storage_costs']:,.2f}")
        print()
        print("OPTIMAL STRATEGY:")
        print("-" * 40)
        
        for i, action in enumerate(result['strategy']):
            print(f"{i+1}. {action['date'].strftime('%Y-%m-%d')}: "
                  f"{action['operation'].upper()} {action['volume']:.1f} units "
                  f"at ${action['price']:.2f} -> Cash flow: ${action['cash_flow']:,.2f}")
        
        print()
        print(f"Total Operations: {len(result['strategy'])}")


# Load and process the natural gas price data
def load_nat_gas_data():
    """Load the natural gas price data from the CSV."""
    data = {
        'Dates': [
            '10/31/20', '11/30/20', '12/31/20', '1/31/21', '2/28/21', '3/31/21',
            '4/30/21', '5/31/21', '6/30/21', '7/31/21', '8/31/21', '9/30/21',
            '10/31/21', '11/30/21', '12/31/21', '1/31/22', '2/28/22', '3/31/22',
            '4/30/22', '5/31/22', '6/30/22', '7/31/22', '8/31/22', '9/30/22',
            '10/31/22', '11/30/22', '12/31/22', '1/31/23', '2/28/23', '3/31/23',
            '4/30/23', '5/31/23', '6/30/23', '7/31/23', '8/31/23', '9/30/23',
            '10/31/23', '11/30/23', '12/31/23', '1/31/24', '2/29/24', '3/31/24',
            '4/30/24', '5/31/24', '6/30/24', '7/31/24', '8/31/24', '9/30/24'
        ],
        'Prices': [
            10.1, 10.3, 11.0, 10.9, 10.9, 10.9, 10.4, 9.84, 10.0, 10.1,
            10.3, 10.2, 10.1, 11.2, 11.4, 11.5, 11.8, 11.5, 10.7, 10.7,
            10.4, 10.5, 10.4, 10.8, 11.0, 11.6, 11.6, 12.1, 11.7, 12.0,
            11.5, 11.2, 10.9, 11.4, 11.1, 11.5, 11.8, 12.2, 12.8, 12.6,
            12.4, 12.7, 12.1, 11.4, 11.5, 11.6, 11.5, 11.8
        ]
    }
    
    df = pd.DataFrame(data)
    df['Dates'] = pd.to_datetime(df['Dates'])
    return df

# Test the pricing model
if __name__ == "__main__":
    # Load price data
    price_data = load_nat_gas_data()
    
    # Initialize the pricer
    pricer = GasStoragePricer(price_data, storage_cost_per_unit_per_day=0.01)
    
    # Test Case 1: Simple seasonal strategy
    print("TEST CASE 1: Seasonal Storage Strategy")
    print("=" * 50)
    
    result1 = pricer.price_contract(
        injection_dates=['2021-05-31', '2021-06-30', '2021-07-31'],  # Summer (lower prices)
        withdrawal_dates=['2021-12-31', '2022-01-31', '2022-02-28'],  # Winter (higher prices)
        injection_withdrawal_rate=50.0,  # 50 units per day max
        max_storage_volume=100.0,  # 100 units max capacity
        contract_start='2021-05-01',
        contract_end='2022-03-31',
        storage_cost_per_unit_per_day=0.01
    )
    
    pricer.print_valuation_summary(result1)
    
    print("\n" + "=" * 80 + "\n")
    
    # Test Case 2: Multiple injection/withdrawal opportunities
    print("TEST CASE 2: Multiple Opportunities Strategy")
    print("=" * 50)
    
    result2 = pricer.price_contract(
        injection_dates=['2022-04-30', '2022-05-31', '2022-06-30', '2022-07-31'],
        withdrawal_dates=['2022-11-30', '2022-12-31', '2023-01-31', '2023-02-28'],
        injection_withdrawal_rate=25.0,
        max_storage_volume=75.0,
        contract_start='2022-04-01',
        contract_end='2023-03-31',
        storage_cost_per_unit_per_day=0.015
    )
    
    pricer.print_valuation_summary(result2)
    
    print("\n" + "=" * 80 + "\n")
    
    # Test Case 3: High storage capacity, low injection rate
    print("TEST CASE 3: High Capacity, Low Rate Strategy")
    print("=" * 50)
    
    result3 = pricer.price_contract(
        injection_dates=['2023-06-30', '2023-07-31', '2023-08-31'],
        withdrawal_dates=['2023-12-31', '2024-01-31'],
        injection_withdrawal_rate=20.0,
        max_storage_volume=200.0,
        contract_start='2023-06-01',
        contract_end='2024-02-29',
        storage_cost_per_unit_per_day=0.008
    )
    
    pricer.print_valuation_summary(result3)
    
    print("\n" + "=" * 80 + "\n")
    
    # Price sensitivity analysis
    print("PRICE SENSITIVITY ANALYSIS")
    print("=" * 50)
    print("Testing different storage cost rates...")
    
    storage_costs = [0.005, 0.01, 0.015, 0.02, 0.025]
    base_params = {
        'injection_dates': ['2022-06-30', '2022-07-31'],
        'withdrawal_dates': ['2022-12-31', '2023-01-31'],
        'injection_withdrawal_rate': 30.0,
        'max_storage_volume': 80.0,
        'contract_start': '2022-06-01',
        'contract_end': '2023-02-28'
    }
    
    print(f"{'Storage Cost':<15} {'Contract Value':<15} {'Storage Costs':<15} {'Net Cash Flow':<15}")
    print("-" * 65)
    
    for cost in storage_costs:
        result = pricer.price_contract(storage_cost_per_unit_per_day=cost, **base_params)
        print(f"{cost:<15.3f} ${result['contract_value']:<14.2f} ${result['storage_costs']:<14.2f} ${result['total_cash_flow']:<14.2f}")
