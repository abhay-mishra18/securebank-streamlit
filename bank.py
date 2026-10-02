"""Business logic for SecureBank.

The Bank class owns all rules (validation, limits, authentication) and all
reads/writes to data.json. The Streamlit UI only calls these methods, so the
rules cannot be bypassed from the frontend.
"""

import hmac
import json
import logging
import random
import re
import string
from pathlib import Path

logger = logging.getLogger(__name__)

WITHDRAWAL_LIMIT = 25000
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PIN_PATTERN = re.compile(r"[0-9]{4}")


class BankError(Exception):
    """An error whose message is safe to show to the user."""


class Bank:
    database = Path(__file__).with_name("data.json")
    data = []

    # ---------- persistence ----------

    @staticmethod
    def _load():
        """Read data.json into Bank.data (empty list if the file doesn't exist yet)."""
        if not Bank.database.exists() or Bank.database.stat().st_size == 0:
            Bank.data = []
            return
        try:
            with open(Bank.database, encoding="utf-8") as fs:
                loaded = json.load(fs)
            if not isinstance(loaded, list):
                raise ValueError("data.json must contain a list of accounts")
            Bank.data = loaded
        except (OSError, ValueError) as err:
            logger.error("Could not read %s: %s", Bank.database, err)
            raise BankError("Could not read account data. Please try again.") from err

    @staticmethod
    def _update():
        """Write Bank.data to data.json (temp file + replace, so a crash can't corrupt it)."""
        temp_file = Bank.database.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as fs:
                json.dump(Bank.data, fs, indent=4)
            temp_file.replace(Bank.database)
        except OSError as err:
            logger.error("Could not write %s: %s", Bank.database, err)
            raise BankError("Could not save your changes. Please try again.") from err

    # ---------- helpers ----------

    @staticmethod
    def _accountgenerate():
        alpha = random.choices(string.ascii_uppercase, k=4)
        num = random.choices(string.digits, k=6)
        id = alpha + num
        random.shuffle(id)
        return "".join(id)

    @staticmethod
    def _find(account_no):
        account_no = (account_no or "").strip().upper()
        return next((a for a in Bank.data if a["AccountNo"] == account_no), None)

    @staticmethod
    def _authenticate(account_no, pin):
        """Return the stored account if the account number and PIN match."""
        account = Bank._find(account_no)
        stored_pin = account["pin"] if account else ""
        pin_ok = hmac.compare_digest(str(stored_pin), str(pin or ""))
        if account is None or not pin_ok:
            # Same message for both cases so nobody can probe which account numbers exist
            raise BankError("Invalid account number or PIN.")
        return account

    @staticmethod
    def _public(account):
        """A copy of the account without the PIN."""
        return {key: value for key, value in account.items() if key != "pin"}

    @staticmethod
    def _check_name(name):
        name = (name or "").strip()
        if len(name) < 2:
            raise BankError("Please enter your full name.")
        return name

    @staticmethod
    def _check_email(email):
        email = (email or "").strip()
        if not EMAIL_PATTERN.match(email):
            raise BankError("Please enter a valid email address.")
        return email

    @staticmethod
    def _check_pin(pin):
        if not PIN_PATTERN.fullmatch(pin or ""):
            raise BankError("PIN must be exactly 4 digits.")
        return pin

    @staticmethod
    def _check_amount(amount):
        if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
            raise BankError("Please enter an amount greater than ₹0.")
        return amount

    # ---------- account operations ----------

    def CreateAccount(self, name, age, email, pin):
        """Validate everything first; nothing is saved unless all checks pass."""
        name = Bank._check_name(name)
        if not isinstance(age, int) or age < 18:
            raise BankError("You must be at least 18 years old to open an account.")
        if age > 120:
            raise BankError("Please enter a valid age.")
        email = Bank._check_email(email)
        pin = Bank._check_pin(pin)

        Bank._load()
        account_no = Bank._accountgenerate()
        while Bank._find(account_no):
            account_no = Bank._accountgenerate()

        Bank.data.append({
            "Name": name,
            "age": age,
            "email": email,
            "AccountNo": account_no,
            "pin": pin,
            "Balance": 0,
        })
        Bank._update()
        return account_no

    def Login(self, account_no, pin):
        Bank._load()
        account = Bank._authenticate(account_no, pin)
        return account["AccountNo"]

    def Details(self, account_no):
        """Account data without the PIN."""
        Bank._load()
        account = Bank._find(account_no)
        if account is None:
            raise BankError("Account not found.")
        return Bank._public(account)

    def depositMoney(self, account_no, amount):
        amount = Bank._check_amount(amount)
        Bank._load()
        account = Bank._find(account_no)
        if account is None:
            raise BankError("Account not found.")
        account["Balance"] += amount
        Bank._update()
        return account["Balance"]

    def withdrawMoney(self, account_no, amount):
        amount = Bank._check_amount(amount)
        if amount > WITHDRAWAL_LIMIT:
            raise BankError(f"Daily withdrawal limit is ₹{WITHDRAWAL_LIMIT:,}.")
        Bank._load()
        account = Bank._find(account_no)
        if account is None:
            raise BankError("Account not found.")
        if amount > account["Balance"]:
            raise BankError("Insufficient balance.")
        account["Balance"] -= amount
        Bank._update()
        return account["Balance"]

    def UpdateDetails(self, account_no, current_pin, name=None, email=None, new_pin=None):
        """Update name, email and/or PIN. The current PIN is required."""
        Bank._load()
        account = Bank._authenticate(account_no, current_pin)

        new_values = {}
        if name is not None:
            new_values["Name"] = Bank._check_name(name)
        if email is not None:
            new_values["email"] = Bank._check_email(email)
        if new_pin:
            new_values["pin"] = Bank._check_pin(new_pin)

        account.update(new_values)
        Bank._update()

    def DeleteAccount(self, account_no, pin):
        Bank._load()
        account = Bank._authenticate(account_no, pin)
        Bank.data.remove(account)
        Bank._update()
