from decimal import Decimal, InvalidOperation
import json
import os


class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = Decimal(str(balance))

    def deposit(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            print("Deposit amount must be positive")
            return False
        self.balance += amount
        print(f"Added {amount} to the balance")
        return True

    def withdraw(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            print("Withdrawal amount must be positive")
            return False
        if amount > self.balance:
            return False
        self.balance -= amount
        print(f"Withdrew {amount} from the balance")
        return True

    def show_balance(self):
        print(f"{self.owner}'s balance is: {self.balance}")

    def transfer(self, other_account, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            print("Transfer amount must be positive")
            return False
        if amount > self.balance:
            return False
        self.balance -= amount
        other_account.balance += amount
        print(f"Transferred {amount} to {other_account.owner}'s account")
        return True


def save_accounts(accounts, filename):
    payload = {}
    for name, account in accounts.items():
        payload[name] = {
            "owner": account.owner,
            "balance": str(account.balance),
        }
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def load_accounts(filename):
    if not os.path.exists(filename):
        return {}

    with open(filename, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    accounts = {}
    for name, data in raw_data.items():
        accounts[name] = BankAccount(data["owner"], data["balance"])
    return accounts


def interactive_loop(account, accounts=None, filename="accounts.json"):
    """Run input handling outside the BankAccount class.

    If `accounts` is provided, allow transfers to existing accounts and
    optionally create new target accounts.
    """
    while True:
        options = input("Choose an option: deposit, withdraw, show_balance, transfer, exit: ").strip().lower()
        if options == "deposit":
            try:
                amount = Decimal(input("Enter the amount to deposit: "))
            except (ValueError, InvalidOperation):
                print("Invalid amount")
                continue
            if account.deposit(amount) and accounts is not None:
                save_accounts(accounts, filename)
        elif options == "withdraw":
            try:
                amount = Decimal(input("Enter the amount to withdraw: "))
            except (ValueError, InvalidOperation):
                print("Invalid amount")
                continue
            if account.withdraw(amount):
                if accounts is not None:
                    save_accounts(accounts, filename)
            else:
                print("Insufficient funds")
        elif options == "show_balance":
            account.show_balance()
        elif options == "transfer":
            try:
                amount = Decimal(input("Enter the amount to transfer: "))
            except (ValueError, InvalidOperation):
                print("Invalid amount")
                continue
            other_owner = input("Enter the owner of the account to transfer to: ").strip().capitalize()
            other_account = None
            if accounts is not None and other_owner in accounts:
                other_account = accounts[other_owner]
            else:
                create_new = input(f"Account '{other_owner}' not found. Create new? (y/n): ").strip().lower()
                if create_new == 'y':
                    try:
                        start_bal = Decimal(input("Starting balance for new account: "))
                    except (ValueError, InvalidOperation):
                        print("Invalid amount; transfer cancelled.")
                        continue
                    other_account = BankAccount(other_owner, start_bal)
                    if accounts is not None:
                        accounts[other_owner] = other_account
                else:
                    print("Transfer cancelled.")
                    continue
            if account.transfer(other_account, amount):
                if accounts is not None:
                    save_accounts(accounts, filename)
            else:
                print("Insufficient funds for transfer")
        elif options == "exit":
            print("Goodbye.")
            break
        else:
            print("Unknown option. Please choose deposit, withdraw, show_balance, transfer, or exit.")


if __name__ == "__main__":
    filename = "accounts.json"
    accounts = load_accounts(filename)
    if not accounts:
        accounts = {
            "Ariel": BankAccount("Ariel", Decimal("500")),
            "Twix": BankAccount("Twix", Decimal("300")),
        }
        save_accounts(accounts, filename)

    while True:
        name = input("Select account (Ariel/Twix) or type 'new': ").strip().capitalize()
        if name == "new":
            n = input("Name: ").strip().capitalize()
            try:
                bal = Decimal(input("Starting balance: "))
            except (ValueError, InvalidOperation):
                print("Invalid amount")
                continue
            accounts[n] = BankAccount(n, bal)
            save_accounts(accounts, filename)
            account = accounts[n]
        elif name in accounts:
            account = accounts[name]
        else:
            print("Unknown account")
            continue
        interactive_loop(account, accounts, filename)
        if input("Switch accounts? (y/n): ").strip().lower() != "y":
            break
