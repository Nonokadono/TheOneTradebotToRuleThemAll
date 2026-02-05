from ibkr_adapter.client import IBKRClient
from risk.account_state_ibkr import fetch_account_state

if __name__ == "__main__":
    client = IBKRClient()
    state = fetch_account_state(client)
    print("Connected. Equity:", state.equity, "Balance:", state.balance)
    client.disconnect()
