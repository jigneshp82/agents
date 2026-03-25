import unittest
import datetime
import sys
from unittest.mock import patch, MagicMock

# Import the module we want to test
import accounts

class TestGetSharePrice(unittest.TestCase):
    def test_known_symbols(self):
        # Test a few known symbols to make sure they return expected prices
        self.assertEqual(accounts.get_share_price("AAPL"), 150.0)
        self.assertEqual(accounts.get_share_price("TSLA"), 800.0)
        self.assertEqual(accounts.get_share_price("GOOGL"), 2500.0)
        
    def test_unknown_symbol(self):
        # Test that unknown symbols return 0.0
        self.assertEqual(accounts.get_share_price("UNKNOWN"), 0.0)

class TestAccount(unittest.TestCase):
    def test_init_with_valid_deposit(self):
        # Test initializing with a valid deposit amount
        account = accounts.Account("test123", 1000.0)
        self.assertEqual(account.account_id, "test123")
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(len(account.transactions), 1)  # Initial deposit should be recorded
        
    def test_init_with_invalid_deposit(self):
        # Test initializing with an invalid (non-positive) deposit amount
        with self.assertRaises(ValueError):
            accounts.Account("test123", 0.0)
        with self.assertRaises(ValueError):
            accounts.Account("test123", -100.0)
        
    def test_deposit_valid_amount(self):
        # Test depositing a valid amount
        account = accounts.Account("test123", 1000.0)
        initial_balance = account.balance
        account.deposit(500.0)
        self.assertEqual(account.balance, initial_balance + 500.0)
        self.assertEqual(len(account.transactions), 2)  # Initial deposit + new deposit
        
    def test_deposit_invalid_amount(self):
        # Test depositing an invalid amount
        account = accounts.Account("test123", 1000.0)
        with self.assertRaises(ValueError):
            account.deposit(0.0)
        with self.assertRaises(ValueError):
            account.deposit(-100.0)
        
    def test_withdraw_valid_amount(self):
        # Test withdrawing a valid amount
        account = accounts.Account("test123", 1000.0)
        initial_balance = account.balance
        result = account.withdraw(500.0)
        self.assertTrue(result)
        self.assertEqual(account.balance, initial_balance - 500.0)
        self.assertEqual(len(account.transactions), 2)  # Initial deposit + withdrawal
        
    def test_withdraw_invalid_amount(self):
        # Test withdrawing an invalid amount
        account = accounts.Account("test123", 1000.0)
        with self.assertRaises(ValueError):
            account.withdraw(0.0)
        with self.assertRaises(ValueError):
            account.withdraw(-100.0)
        
    def test_withdraw_insufficient_funds(self):
        # Test withdrawing more than the balance
        account = accounts.Account("test123", 1000.0)
        result = account.withdraw(1500.0)
        self.assertFalse(result)
        self.assertEqual(account.balance, 1000.0)  # Balance should not change
        self.assertEqual(len(account.transactions), 1)  # No new transaction should be recorded
        
    def test_buy_shares_valid(self):
        # Test buying shares with sufficient funds
        account = accounts.Account("test123", 10000.0)
        initial_balance = account.balance
        result = account.buy_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertEqual(account.balance, initial_balance - (150.0 * 10))  # 150.0 is the price of AAPL
        self.assertEqual(account.holdings["AAPL"], 10)
        self.assertEqual(len(account.transactions), 2)  # Initial deposit + buy
        
    def test_buy_shares_invalid_quantity(self):
        # Test buying shares with invalid quantity
        account = accounts.Account("test123", 10000.0)
        with self.assertRaises(ValueError):
            account.buy_shares("AAPL", 0)
        with self.assertRaises(ValueError):
            account.buy_shares("AAPL", -5)
        
    def test_buy_shares_insufficient_funds(self):
        # Test buying shares with insufficient funds
        account = accounts.Account("test123", 100.0)  # Not enough for even 1 AAPL share
        result = account.buy_shares("AAPL", 10)
        self.assertFalse(result)
        self.assertEqual(account.balance, 100.0)  # Balance should not change
        self.assertEqual(len(account.holdings), 0)  # No shares should be bought
        self.assertEqual(len(account.transactions), 1)  # No new transaction should be recorded
        
    def test_buy_shares_unknown_symbol(self):
        # Test buying shares with unknown symbol
        account = accounts.Account("test123", 10000.0)
        result = account.buy_shares("UNKNOWN", 10)
        self.assertFalse(result)
        self.assertEqual(account.balance, 10000.0)  # Balance should not change
        self.assertEqual(len(account.holdings), 0)  # No shares should be bought
        self.assertEqual(len(account.transactions), 1)  # No new transaction should be recorded
        
    def test_sell_shares_valid(self):
        # Test selling shares that the account has
        account = accounts.Account("test123", 10000.0)
        account.buy_shares("AAPL", 10)  # Buy 10 shares first
        initial_balance = account.balance
        result = account.sell_shares("AAPL", 5)  # Sell 5 shares
        self.assertTrue(result)
        self.assertEqual(account.balance, initial_balance + (150.0 * 5))  # 150.0 is the price of AAPL
        self.assertEqual(account.holdings["AAPL"], 5)  # Should have 5 shares left
        self.assertEqual(len(account.transactions), 3)  # Initial deposit + buy + sell
        
    def test_sell_all_shares(self):
        # Test selling all shares of a symbol
        account = accounts.Account("test123", 10000.0)
        account.buy_shares("AAPL", 10)  # Buy 10 shares first
        initial_balance = account.balance
        result = account.sell_shares("AAPL", 10)  # Sell all 10 shares
        self.assertTrue(result)
        self.assertEqual(account.balance, initial_balance + (150.0 * 10))
        self.assertNotIn("AAPL", account.holdings)  # AAPL should be removed from holdings
        
    def test_sell_shares_invalid_quantity(self):
        # Test selling shares with invalid quantity
        account = accounts.Account("test123", 10000.0)
        account.buy_shares("AAPL", 10)  # Buy 10 shares first
        with self.assertRaises(ValueError):
            account.sell_shares("AAPL", 0)
        with self.assertRaises(ValueError):
            account.sell_shares("AAPL", -5)
        
    def test_sell_shares_insufficient_shares(self):
        # Test selling more shares than the account has
        account = accounts.Account("test123", 10000.0)
        account.buy_shares("AAPL", 5)  # Buy 5 shares first
        result = account.sell_shares("AAPL", 10)  # Try to sell 10 shares
        self.assertFalse(result)
        self.assertEqual(account.holdings["AAPL"], 5)  # Should still have 5 shares
        self.assertEqual(len(account.transactions), 2)  # Initial deposit + buy, no sell transaction
        
    def test_sell_shares_unknown_symbol(self):
        # Test selling shares with unknown symbol
        account = accounts.Account("test123", 10000.0)
        result = account.sell_shares("UNKNOWN", 10)
        self.assertFalse(result)
        self.assertEqual(len(account.transactions), 1)  # No new transaction should be recorded
        
    def test_sell_shares_not_owned(self):
        # Test selling shares that the account does not own
        account = accounts.Account("test123", 10000.0)
        result = account.sell_shares("AAPL", 10)  # Try to sell shares we don't have
        self.assertFalse(result)
        self.assertEqual(len(account.transactions), 1)  # No new transaction should be recorded
        
    @patch("accounts.get_share_price")
    def test_portfolio_value(self, mock_get_price):
        # Test calculating the portfolio value
        # Set up mock return values for get_share_price
        mock_get_price.side_effect = lambda symbol: {"AAPL": 150.0, "TSLA": 800.0}.get(symbol, 0.0)
        
        account = accounts.Account("test123", 10000.0)
        account.buy_shares("AAPL", 10)  # 10 shares at 150.0 each = 1500.0
        account.buy_shares("TSLA", 5)   # 5 shares at 800.0 each = 4000.0
        
        # Calculate expected portfolio value: balance + value of holdings
        expected_value = account.balance + (10 * 150.0) + (5 * 800.0)
        self.assertEqual(account.portfolio_value(), expected_value)
        
    @patch("accounts.get_share_price")
    def test_profit_loss(self, mock_get_price):
        # Test calculating the profit/loss
        # Set up mock return values for get_share_price
        mock_get_price.side_effect = lambda symbol: {"AAPL": 200.0, "TSLA": 900.0}.get(symbol, 0.0)
        
        account = accounts.Account("test123", 10000.0)
        initial_deposit = account.initial_deposit
        
        # Buy shares at fixed prices (from the original get_share_price function)
        with patch("accounts.get_share_price", side_effect=lambda symbol: {"AAPL": 150.0, "TSLA": 800.0}.get(symbol, 0.0)):
            account.buy_shares("AAPL", 10)  # 10 shares at 150.0 each = 1500.0
            account.buy_shares("TSLA", 5)   # 5 shares at 800.0 each = 4000.0
        
        # Now the prices have changed (as per our mock)
        # AAPL: 10 shares * (200.0 - 150.0) = 500.0 profit
        # TSLA: 5 shares * (900.0 - 800.0) = 500.0 profit
        # Total profit = 1000.0
        
        expected_profit_loss = account.portfolio_value() - initial_deposit
        self.assertEqual(account.profit_loss(), expected_profit_loss)
        
    def test_get_holdings(self):
        # Test getting the holdings
        account = accounts.Account("test123", 10000.0)
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 5)
        
        holdings = account.get_holdings()
        self.assertEqual(holdings, {"AAPL": 10, "TSLA": 5})
        
        # Verify that the returned holdings are a copy, not a reference
        holdings["AAPL"] = 100
        self.assertEqual(account.holdings["AAPL"], 10)  # Original should be unchanged
        
    def test_get_transactions(self):
        # Test getting the transactions
        account = accounts.Account("test123", 10000.0)
        account.deposit(500.0)
        account.buy_shares("AAPL", 10)
        
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 3)  # Initial deposit + deposit + buy
        
        # Verify types and keys
        for transaction in transactions:
            self.assertIsInstance(transaction, dict)
            self.assertIn("type", transaction)
            self.assertIn("timestamp", transaction)
            self.assertIsInstance(transaction["timestamp"], datetime.datetime)
        
        # Verify that the returned transactions are a copy, not a reference
        transactions[0]["type"] = "modified"
        self.assertEqual(account.transactions[0]["type"], "deposit")  # Original should be unchanged

if __name__ == "__main__":
    unittest.main()