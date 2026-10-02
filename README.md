# SecureBank – Streamlit Banking Management System

A Python + Streamlit banking management simulation with JSON-based persistence. It turns a console banking project into a small, minimal dashboard with login, deposits, withdrawals and profile management.

> **Important:** This project is an educational banking simulation and should not be used for real financial transactions.

> **Demo version:** This is a demo for learning and portfolio purposes. **Do not enter your real name, email, PIN or any other personal information.** Use dummy data only. On the hosted demo, accounts are stored in a plain `data.json` file that is shared by all visitors and may be reset at any time.

## Features

- Account creation (account number is generated automatically)
- Secure login flow with account number and 4-digit PIN
- Deposit and withdrawal with validation and a ₹25,000 withdrawal limit
- Balance management
- Account details with masked account number and email
- Profile updates (name, email, PIN)
- Account deletion with confirmation and PIN check
- Session-based authentication
- JSON persistence

## Tech Stack

- Python
- Streamlit
- JSON
- Object-Oriented Programming

## Project Structure

```text
securebank-streamlit
├── app.py              # Streamlit UI and session management
├── bank.py             # Bank class: validation, rules, authentication, JSON storage
├── data.json           # Account data (created automatically, ignored by Git)
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Light theme and accent color
├── .gitignore
└── README.md
```

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

- `bank.py` owns every rule. The UI only calls `Bank` methods, so validation cannot be bypassed from the frontend.
- After login, only the account number is kept in `st.session_state`. The PIN is never stored, and every page loads the account fresh from the backend.
- Sensitive actions (profile update, account deletion) ask for the PIN again.

## Known Limitations

- PINs are stored as plain text in `data.json`. A real system would hash them.
- The withdrawal limit is applied per transaction, not tracked per day.
- There is no transaction history.
- Anyone with access to the files can read `data.json`.
