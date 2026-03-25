import datetime
from typing import Dict, List, Optional, Union

def get_share_price(symbol: str) -> float:
    """Returns the current price of a share.
    Test implementation that returns fixed prices for AAPL, TSLA, GOOGL.
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        """Initialize a new account with an ID and initial deposit.
        
        Args:
            account_id: Unique identifier for the account
            initial_deposit: Amount initially deposited when creating the account
        """
        if initial_deposit <= 0:
            raise ValueError("Initial deposit must be positive")
            
        self.account_id = account_id
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Dict[str, Union[str, int, float, datetime.datetime]]] = []
        
        # Record the initial deposit as a transaction
        self._add_transaction('deposit', None, None, initial_deposit)
    
    def deposit(self, amount: float) -> None:
        """Add funds to the account balance.
        
        Args:
            amount: Amount to deposit
        
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self._add_transaction('deposit', None, None, amount)
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw funds from the account balance.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            bool: True if withdrawal was successful, False otherwise
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.balance:
            return False
        
        self.balance -= amount
        self._add_transaction('withdraw', None, None, amount)
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """Buy shares of a specified symbol.
        
        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy
            
        Returns:
            bool: True if purchase was successful, False otherwise
            
        Raises:
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        price = get_share_price(symbol)
        if price == 0.0:
            return False  # Symbol not found
        
        total_cost = price * quantity
        
        if total_cost > self.balance:
            return False  # Insufficient funds
        
        # Update balance
        self.balance -= total_cost
        
        # Update holdings
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        
        # Record transaction
        self._add_transaction('buy', symbol, quantity, price)
        
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """Sell shares of a specified symbol.
        
        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell
            
        Returns:
            bool: True if sale was successful, False otherwise
            
        Raises:
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if user has enough shares
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False
        
        price = get_share_price(symbol)
        if price == 0.0:
            return False  # Symbol not found
        
        total_revenue = price * quantity
        
        # Update balance
        self.balance += total_revenue
        
        # Update holdings
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # Record transaction
        self._add_transaction('sell', symbol, quantity, price)
        
        return True
    
    def portfolio_value(self) -> float:
        """Calculate the total value of the portfolio.
        
        Returns:
            float: Total value of cash balance plus all holdings
        """
        holdings_value = sum(get_share_price(symbol) * quantity 
                           for symbol, quantity in self.holdings.items())
        return self.balance + holdings_value
    
    def profit_loss(self) -> float:
        """Calculate profit or loss since initial deposit.
        
        Returns:
            float: Current portfolio value minus initial deposit
        """
        return self.portfolio_value() - self.initial_deposit
    
    def get_holdings(self) -> Dict[str, int]:
        """Return a copy of the holdings dictionary.
        
        Returns:
            Dict[str, int]: Dictionary mapping stock symbols to quantities
        """
        return self.holdings.copy()
    
    def get_transactions(self) -> List[Dict[str, Union[str, int, float, datetime.datetime]]]:
        """Return a list of all transactions.
        
        Returns:
            List[Dict]: List of transaction records
        """
        return self.transactions.copy()
    
    def get_profit_loss_at_point(self) -> float:
        """Calculate profit or loss at current point in time.
        
        Returns:
            float: Current profit or loss
        """
        return self.profit_loss()
    
    def _add_transaction(self, transaction_type: str, symbol: Optional[str], 
                         quantity: Optional[int], price: float) -> None:
        """Add a transaction to the transaction history.
        
        Args:
            transaction_type: Type of transaction (deposit, withdraw, buy, sell)
            symbol: Stock symbol (None for deposit/withdraw)
            quantity: Number of shares (None for deposit/withdraw)
            price: Price per share or amount for deposit/withdraw
        """
        transaction = {
            'type': transaction_type,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.datetime.now()
        }
        self.transactions.append(transaction)