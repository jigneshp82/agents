import gradio as gr
import accounts
import datetime

# Create a global account variable
current_account = None

def create_account(account_id, initial_deposit):
    """Create a new trading account."""
    global current_account
    try:
        initial_deposit = float(initial_deposit)
        current_account = accounts.Account(account_id, initial_deposit)
        return f"Account {account_id} created with initial deposit of ${initial_deposit:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit(amount):
    """Deposit funds into the account."""
    global current_account
    if current_account is None:
        return "No account exists. Please create an account first."
    
    try:
        amount = float(amount)
        current_account.deposit(amount)
        return f"${amount:.2f} deposited successfully. New balance: ${current_account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def withdraw(amount):
    """Withdraw funds from the account."""
    global current_account
    if current_account is None:
        return "No account exists. Please create an account first."
    
    try:
        amount = float(amount)
        success = current_account.withdraw(amount)
        if success:
            return f"${amount:.2f} withdrawn successfully. New balance: ${current_account.balance:.2f}"
        else:
            return f"Withdrawal failed. Insufficient funds. Current balance: ${current_account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    """Buy shares of a stock."""
    global current_account
    if current_account is None:
        return "No account exists. Please create an account first."
    
    try:
        quantity = int(quantity)
        price = accounts.get_share_price(symbol)
        
        if price == 0.0:
            return f"Error: Symbol '{symbol}' not found."
        
        success = current_account.buy_shares(symbol, quantity)
        if success:
            total_cost = price * quantity
            return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} each. Total cost: ${total_cost:.2f}. New balance: ${current_account.balance:.2f}"
        else:
            return f"Purchase failed. Insufficient funds. Current balance: ${current_account.balance:.2f}, Required: ${price * quantity:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    """Sell shares of a stock."""
    global current_account
    if current_account is None:
        return "No account exists. Please create an account first."
    
    try:
        quantity = int(quantity)
        price = accounts.get_share_price(symbol)
        
        if price == 0.0:
            return f"Error: Symbol '{symbol}' not found."
        
        success = current_account.sell_shares(symbol, quantity)
        if success:
            total_revenue = price * quantity
            return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} each. Total revenue: ${total_revenue:.2f}. New balance: ${current_account.balance:.2f}"
        else:
            holdings = current_account.get_holdings()
            current_qty = holdings.get(symbol, 0)
            return f"Sale failed. You own {current_qty} shares of {symbol}, but tried to sell {quantity}."
    except ValueError as e:
        return f"Error: {str(e)}"

def get_portfolio_value():
    """Get the total value of the portfolio."""
    global current_account
    if current_account is None:
        return "No account exists. Please create an account first."
    
    value = current_account.portfolio_value()
    profit_loss = current_account.profit_loss()
    pl_sign = "+" if profit_loss >= 0 else ""
    
    holdings_info = "Holdings:\n"
    for symbol, quantity in current_account.get_holdings().items():
        price = accounts.get_share_price(symbol)
        holdings_info += f"{symbol}: {quantity} shares at ${price:.2f} each, total value: ${price * quantity:.2f}\n"
    
    return f"Cash Balance: ${current_account.balance:.2f}\n{holdings_info}\nTotal Portfolio Value: ${value:.2f}\nProfit/Loss: {pl_sign}${profit_loss:.2f}"

def get_transactions():
    """Get a list of all transactions."""
    global current_account
    if current_account is None:
        return "No account exists. Please create an account first."
    
    transactions = current_account.get_transactions()
    if not transactions:
        return "No transactions found."
    
    transaction_list = "Transaction History:\n"
    for t in transactions:
        timestamp = t['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        if t['type'] == 'deposit':
            transaction_list += f"{timestamp} - DEPOSIT: ${t['price']:.2f}\n"
        elif t['type'] == 'withdraw':
            transaction_list += f"{timestamp} - WITHDRAW: ${t['price']:.2f}\n"
        elif t['type'] == 'buy':
            transaction_list += f"{timestamp} - BUY: {t['quantity']} shares of {t['symbol']} at ${t['price']:.2f} each\n"
        elif t['type'] == 'sell':
            transaction_list += f"{timestamp} - SELL: {t['quantity']} shares of {t['symbol']} at ${t['price']:.2f} each\n"
    
    return transaction_list

def get_share_price_info(symbol):
    """Get the current price of a share."""
    if not symbol:
        return "Please enter a symbol."
    
    price = accounts.get_share_price(symbol)
    if price == 0.0:
        return f"Symbol '{symbol}' not found. Available symbols are: AAPL, TSLA, GOOGL"
    else:
        return f"Current price of {symbol}: ${price:.2f}"

# Create the Gradio interface
with gr.Blocks(title="Trading Account Simulator") as demo:
    gr.Markdown("# Trading Account Simulator")
    
    with gr.Tab("Create Account"):
        gr.Markdown("### Create a New Account")
        with gr.Row():
            account_id_input = gr.Textbox(label="Account ID")
            initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
        create_btn = gr.Button("Create Account")
        create_output = gr.Textbox(label="Result")
        create_btn.click(create_account, inputs=[account_id_input, initial_deposit_input], outputs=create_output)
    
    with gr.Tab("Deposit/Withdraw"):
        gr.Markdown("### Deposit or Withdraw Funds")
        with gr.Row():
            deposit_input = gr.Textbox(label="Deposit Amount ($)")
            deposit_btn = gr.Button("Deposit")
            deposit_output = gr.Textbox(label="Deposit Result")
        
        with gr.Row():
            withdraw_input = gr.Textbox(label="Withdraw Amount ($)")
            withdraw_btn = gr.Button("Withdraw")
            withdraw_output = gr.Textbox(label="Withdraw Result")
        
        deposit_btn.click(deposit, inputs=deposit_input, outputs=deposit_output)
        withdraw_btn.click(withdraw, inputs=withdraw_input, outputs=withdraw_output)
    
    with gr.Tab("Buy/Sell Shares"):
        gr.Markdown("### Buy or Sell Shares")
        
        with gr.Row():
            symbol_info_input = gr.Textbox(label="Check Share Price (Symbol)")
            price_check_btn = gr.Button("Check Price")
            price_info_output = gr.Textbox(label="Price Information")
        
        with gr.Row():
            buy_symbol_input = gr.Textbox(label="Buy Symbol")
            buy_quantity_input = gr.Textbox(label="Buy Quantity")
            buy_btn = gr.Button("Buy Shares")
            buy_output = gr.Textbox(label="Buy Result")
        
        with gr.Row():
            sell_symbol_input = gr.Textbox(label="Sell Symbol")
            sell_quantity_input = gr.Textbox(label="Sell Quantity")
            sell_btn = gr.Button("Sell Shares")
            sell_output = gr.Textbox(label="Sell Result")
        
        price_check_btn.click(get_share_price_info, inputs=symbol_info_input, outputs=price_info_output)
        buy_btn.click(buy_shares, inputs=[buy_symbol_input, buy_quantity_input], outputs=buy_output)
        sell_btn.click(sell_shares, inputs=[sell_symbol_input, sell_quantity_input], outputs=sell_output)
    
    with gr.Tab("Portfolio & Transactions"):
        gr.Markdown("### View Portfolio and Transaction History")
        
        with gr.Row():
            portfolio_btn = gr.Button("View Portfolio")
            portfolio_output = gr.Textbox(label="Portfolio Information", lines=10)
        
        with gr.Row():
            transactions_btn = gr.Button("View Transactions")
            transactions_output = gr.Textbox(label="Transaction History", lines=15)
        
        portfolio_btn.click(get_portfolio_value, outputs=portfolio_output)
        transactions_btn.click(get_transactions, outputs=transactions_output)

if __name__ == "__main__":
    demo.launch()