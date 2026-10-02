"""SecureBank - Streamlit frontend for the Bank class in bank.py."""

import html
import logging

import streamlit as st

from bank import WITHDRAWAL_LIMIT, Bank, BankError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securebank")

st.set_page_config(page_title="SecureBank", layout="wide")

bank = Bank()

PAGES = [
    "Dashboard",
    "Deposit Money",
    "Withdraw Money",
    "Account Details",
    "Update Profile",
    "Delete Account",
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Font is set on text elements only, so Streamlit's icon font keeps working.
   Text colors are inherited from the active theme so light and dark mode both work. */
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: 'Inter', 'Segoe UI', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-stale="true"] { opacity: 1 !important; }
.block-container { max-width: 1000px; padding-top: 2.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.25); }

/* Typography */
.sb-title { font-size: 1.8rem; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 0.2rem; }
.sb-subtitle { opacity: 0.75; margin-bottom: 1.5rem; }
.sb-brand { font-size: 1.3rem; font-weight: 700; color: #3B82F6; margin-bottom: 1rem; }

/* Cards */
.sb-card { border: 1px solid rgba(128, 128, 128, 0.35); border-radius: 14px;
           padding: 1.1rem 1.25rem; margin-bottom: 1rem; }
.sb-label { font-size: 0.85rem; font-weight: 500; opacity: 0.75; }
.sb-value { font-size: 1.4rem; font-weight: 600; margin-top: 0.2rem; overflow-wrap: anywhere; }
.sb-value.small { font-size: 1.05rem; }
.sb-pill { display: inline-block; background: #DCFCE7; color: #166534; border-radius: 999px;
           padding: 0.15rem 0.75rem; font-size: 0.85rem; font-weight: 600; }

/* Balance card: the one strong accent block */
.sb-balance { background: #1E40AF; border-radius: 16px; padding: 1.5rem 1.75rem;
              margin-bottom: 1rem; min-height: 190px; }
.sb-balance-label { color: #DBEAFE; font-weight: 500; }
.sb-balance-amount { color: #FFFFFF; font-size: 2.6rem; font-weight: 700; margin: 0.25rem 0 0.75rem; }
.sb-balance-note { color: #DBEAFE; font-size: 0.95rem; }

/* Key-value list */
.sb-list { padding: 0.25rem 1.25rem; }
.sb-row { display: flex; justify-content: space-between; gap: 1rem; padding: 0.85rem 0;
          border-bottom: 1px solid rgba(128, 128, 128, 0.25); }
.sb-row:last-child { border-bottom: none; }
.sb-row-label { opacity: 0.75; }
.sb-row-value { font-weight: 600; text-align: right; overflow-wrap: anywhere; }

/* Avatar / user */
.sb-user { display: flex; gap: 0.75rem; align-items: center; margin: 0.25rem 0 1.25rem; }
.sb-avatar { width: 40px; height: 40px; border-radius: 50%; background: #1E40AF; color: #FFFFFF;
             display: flex; align-items: center; justify-content: center; font-weight: 700; flex: none; }
.sb-avatar.big { width: 56px; height: 56px; font-size: 1.4rem; }
.sb-user-name { font-weight: 600; }
.sb-user-sub { font-size: 0.85rem; opacity: 0.75; }
.sb-profile { display: flex; gap: 1rem; align-items: center; margin-bottom: 1.25rem; }

/* Login / register side panel */
.sb-panel { background: #1E40AF; border-radius: 16px; padding: 2.25rem; display: flex;
            flex-direction: column; justify-content: space-between; }
.sb-panel-brand { color: #FFFFFF; font-size: 1.5rem; font-weight: 700; }
.sb-panel-title { color: #FFFFFF; font-size: 2rem; font-weight: 700; line-height: 1.2; margin-bottom: 0.6rem; }
.sb-panel-tagline { color: #E0E7FF; font-weight: 500; }
.sb-panel-point { color: #FFFFFF; padding: 0.55rem 0; border-top: 1px solid rgba(255, 255, 255, 0.25); }

/* Inputs and buttons */
[data-baseweb="input"], [data-baseweb="base-input"] { border-radius: 8px !important; }
[data-testid="stForm"] { border: 1px solid rgba(128, 128, 128, 0.35); border-radius: 14px; padding: 1.25rem; }
.stButton > button, [data-testid="stFormSubmitButton"] > button { border-radius: 8px; font-weight: 600; }
[data-testid="stSidebar"] .stButton > button { justify-content: flex-start; text-align: left;
                                               border-color: transparent; }

/* Primary buttons use the app accent whatever the theme's primary color is */
button[kind="primary"], button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
    background-color: #1E40AF; border-color: #1E40AF; color: #FFFFFF; }
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover,
button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background-color: #1D4ED8; border-color: #1D4ED8; color: #FFFFFF; }
</style>
"""


# ---------- helpers ----------

def esc(value):
    return html.escape(str(value))


def format_inr(amount):
    """Format a number with Indian digit grouping, e.g. 1234567 -> ₹12,34,567."""
    digits = str(abs(int(amount)))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        digits = ",".join(groups + [tail])
    return f"₹{digits}"


def mask_account(account_no):
    return "•" * (len(account_no) - 4) + account_no[-4:]


def mask_email(email):
    local, _, domain = email.partition("@")
    return f"{local[:1]}•••@{domain}"


def safe_call(action, *args, **kwargs):
    """Run a Bank method. Returns (True, result) or (False, message for the user)."""
    try:
        return True, action(*args, **kwargs)
    except BankError as err:
        return False, str(err)
    except Exception:
        logger.exception("Unexpected error in %s", getattr(action, "__name__", action))
        return False, "Something went wrong. Please try again."


def flash(kind, message):
    """Queue a message to show after the next rerun (kind: success, error, info)."""
    st.session_state["flash"] = (kind, message)


def show_flash():
    message = st.session_state.pop("flash", None)
    if message:
        kind, text = message
        getattr(st, kind)(text)


def init_state():
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("account_number", None)
    st.session_state.setdefault("view", "login")


def reset_session():
    """Clear everything, including the logged-in account."""
    st.session_state.clear()
    init_state()


def logout():
    reset_session()
    flash("info", "You have been logged out.")


def go_to(view):
    st.session_state["view"] = view
    st.session_state.pop("new_account_no", None)


def set_page(page):
    st.session_state["page"] = page


def set_amount(key, amount):
    st.session_state[key] = amount


# ---------- reusable UI pieces ----------
# User-provided text is always escaped because this HTML is rendered unsafely.

def page_header(title, subtitle):
    st.markdown(
        f'<div class="sb-title">{esc(title)}</div><div class="sb-subtitle">{esc(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def card(label, value, small=False):
    size = " small" if small else ""
    st.markdown(
        f'<div class="sb-card"><div class="sb-label">{esc(label)}</div>'
        f'<div class="sb-value{size}">{esc(value)}</div></div>',
        unsafe_allow_html=True,
    )


def status_card():
    st.markdown(
        '<div class="sb-card"><div class="sb-label">Account status</div>'
        '<div style="margin-top:0.5rem"><span class="sb-pill">Active</span></div></div>',
        unsafe_allow_html=True,
    )


def balance_card(label, amount, note=""):
    st.markdown(
        f'<div class="sb-balance"><div class="sb-balance-label">{esc(label)}</div>'
        f'<div class="sb-balance-amount">{esc(amount)}</div>'
        f'<div class="sb-balance-note">{esc(note)}</div></div>',
        unsafe_allow_html=True,
    )


def info_card(rows):
    """rows: (label, value) tuples, or (label, value, True) to show the value as a pill."""
    parts = []
    for row in rows:
        is_pill = len(row) > 2 and row[2]
        shown = f'<span class="sb-pill">{esc(row[1])}</span>' if is_pill else esc(row[1])
        parts.append(
            f'<div class="sb-row"><span class="sb-row-label">{esc(row[0])}</span>'
            f'<span class="sb-row-value">{shown}</span></div>'
        )
    st.markdown(f'<div class="sb-card sb-list">{"".join(parts)}</div>', unsafe_allow_html=True)


def quick_amounts(key, amounts=(500, 1000, 5000, 10000)):
    st.caption("Quick amounts")
    for column, amount in zip(st.columns(len(amounts)), amounts):
        column.button(
            format_inr(amount), key=f"{key}_{amount}", on_click=set_amount,
            args=(key, amount), use_container_width=True,
        )


def auth_layout(min_height):
    """Brand panel on the left; returns the right column for the form."""
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        st.markdown(
            f'<div class="sb-panel" style="min-height:{min_height}px">'
            '<div class="sb-panel-brand">SecureBank</div>'
            '<div><div class="sb-panel-title">Banking that stays out of your way.</div>'
            '<div class="sb-panel-tagline">Simple. Secure. Reliable.</div></div>'
            '<div><div class="sb-panel-point">Deposit and withdraw in seconds</div>'
            '<div class="sb-panel-point">Update your details whenever you need</div>'
            '<div class="sb-panel-point">Your PIN is never shown on screen</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )
    return right


# ---------- logged-out screens ----------

def show_login():
    with auth_layout(470):
        page_header("Log in", "Enter your account number and PIN to continue.")
        show_flash()

        with st.form("login_form"):
            account_no = st.text_input("Account number")
            pin = st.text_input("PIN", type="password", placeholder="4-digit PIN")
            submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)

        if submitted:
            ok, result = safe_call(bank.Login, account_no, pin)
            if ok:
                # Only the account number is kept in session state, never the PIN
                st.session_state["logged_in"] = True
                st.session_state["account_number"] = result
                st.session_state["page"] = PAGES[0]
                st.rerun()
            else:
                st.error(result)

        st.caption("Don't have an account?")
        st.button("Create one", on_click=go_to, args=("register",))


def show_register():
    with auth_layout(640):
        new_account_no = st.session_state.get("new_account_no")
        if new_account_no:
            page_header("Account Created Successfully", "Your SecureBank account is ready.")
            st.markdown("**Your Account Number**")
            st.code(new_account_no, language=None)
            st.info("Save this account number. You need it, along with your PIN, to log in.")
            st.button("Go to Login", type="primary", on_click=go_to, args=("login",))
            return

        page_header("Create your account", "It takes less than a minute.")

        with st.form("register_form"):
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=1, max_value=120, value=18, step=1)
            email = st.text_input("Email")
            pin = st.text_input("PIN", type="password", placeholder="Exactly 4 digits")
            confirm_pin = st.text_input("Confirm PIN", type="password")
            submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

        if submitted:
            if pin != confirm_pin:
                st.error("PINs do not match.")
            else:
                ok, result = safe_call(bank.CreateAccount, name, int(age), email, pin)
                if ok:
                    st.session_state["new_account_no"] = result
                    st.rerun()
                else:
                    st.error(result)

        st.caption("Already have an account?")
        st.button("Log in", on_click=go_to, args=("login",))


# ---------- logged-in screens ----------

def show_dashboard(account):
    page_header(f"Welcome back, {account['Name']}", "Here is a summary of your account.")

    left, right = st.columns([1.7, 1])
    with left:
        balance_card("Available balance", format_inr(account["Balance"]),
                     f"Account {mask_account(account['AccountNo'])}")
    with right:
        card("Account number", account["AccountNo"], small=True)
        status_card()

    st.markdown("#### Quick actions")
    col1, col2, col3 = st.columns(3)
    col1.button("Deposit money", on_click=set_page, args=("Deposit Money",), use_container_width=True)
    col2.button("Withdraw money", on_click=set_page, args=("Withdraw Money",), use_container_width=True)
    col3.button("View account details", on_click=set_page, args=("Account Details",), use_container_width=True)

    st.markdown("#### Account Overview")
    info_card([
        ("Name", account["Name"]),
        ("Email", account["email"]),
        ("Age", account["age"]),
        ("Account number", account["AccountNo"]),
    ])


def show_deposit(account):
    page_header("Deposit Money", "Add money securely to your bank account.")
    form_col, side_col = st.columns([1.3, 1], gap="large")

    with side_col:
        balance_card("Current balance", format_inr(account["Balance"]))

    with form_col:
        quick_amounts("deposit_amount")
        with st.form("deposit_form", clear_on_submit=True):
            amount = st.number_input("Amount (₹)", min_value=0, step=100, key="deposit_amount")
            submitted = st.form_submit_button("Deposit Money", type="primary")

        if submitted:
            ok, result = safe_call(bank.depositMoney, account["AccountNo"], int(amount))
            if ok:
                flash("success", f"{format_inr(amount)} deposited successfully.")
                st.rerun()
            else:
                st.error(result)


def show_withdraw(account):
    page_header("Withdraw Money", "Take money out of your account.")
    form_col, side_col = st.columns([1.3, 1], gap="large")

    with side_col:
        balance_card("Available Balance", format_inr(account["Balance"]),
                     f"Withdrawal limit: {format_inr(WITHDRAWAL_LIMIT)} per day")

    with form_col:
        quick_amounts("withdraw_amount")
        with st.form("withdraw_form", clear_on_submit=True):
            amount = st.number_input("Withdrawal amount (₹)", min_value=0, step=100, key="withdraw_amount")
            submitted = st.form_submit_button("Withdraw Money", type="primary")

        if submitted:
            ok, result = safe_call(bank.withdrawMoney, account["AccountNo"], int(amount))
            if ok:
                flash("success", f"{format_inr(amount)} withdrawn successfully.")
                st.rerun()
            else:
                st.error(result)


def show_account_details(account):
    page_header("Account Details", "Your personal and account information.")

    st.markdown(
        f'<div class="sb-profile"><div class="sb-avatar big">{esc(account["Name"][:1].upper())}</div>'
        f'<div><div class="sb-value">{esc(account["Name"])}</div>'
        '<div style="margin-top:0.3rem"><span class="sb-pill">Active</span></div></div></div>',
        unsafe_allow_html=True,
    )
    reveal = st.checkbox("Show full account number and email")

    account_no = account["AccountNo"] if reveal else mask_account(account["AccountNo"])
    email = account["email"] if reveal else mask_email(account["email"])

    info_card([
        ("Full name", account["Name"]),
        ("Age", account["age"]),
        ("Email", email),
        ("Account number", account_no),
        ("Current balance", format_inr(account["Balance"])),
        ("Account status", "Active", True),
    ])


def show_update_profile(account):
    page_header("Update Profile", "Change your name, email or PIN.")

    form_col, _ = st.columns([1.5, 1])
    with form_col:
        with st.form("profile_form"):
            name = st.text_input("Full name", value=account["Name"])
            email = st.text_input("Email", value=account["email"])
            new_pin = st.text_input("New PIN", type="password", placeholder="Leave blank to keep your current PIN")
            current_pin = st.text_input("Current PIN", type="password", placeholder="Required to save changes")
            submitted = st.form_submit_button("Save Changes", type="primary")

        if submitted:
            ok, result = safe_call(
                bank.UpdateDetails, account["AccountNo"], current_pin,
                name=name, email=email, new_pin=new_pin,
            )
            if ok:
                flash("success", "Your profile has been updated successfully.")
                st.rerun()
            else:
                st.error(result)


def show_delete_account(account):
    page_header("Delete Account", "This action cannot be undone.")
    st.error(
        "Deleting your account permanently removes your banking profile and "
        "associated account data, including any remaining balance."
    )

    form_col, _ = st.columns([1.5, 1])
    with form_col:
        with st.form("delete_form"):
            confirmed = st.checkbox("I understand that this is permanent")
            pin = st.text_input("PIN", type="password", placeholder="Enter your PIN to confirm")
            submitted = st.form_submit_button("Delete Account", type="primary")

        if submitted:
            if not confirmed:
                st.warning("Please tick the confirmation box to continue.")
                return
            ok, result = safe_call(bank.DeleteAccount, account["AccountNo"], pin)
            if ok:
                reset_session()
                flash("success", "Your account has been deleted.")
                st.rerun()
            else:
                st.error(result)


PAGE_VIEWS = {
    "Dashboard": show_dashboard,
    "Deposit Money": show_deposit,
    "Withdraw Money": show_withdraw,
    "Account Details": show_account_details,
    "Update Profile": show_update_profile,
    "Delete Account": show_delete_account,
}


def show_sidebar(account):
    current = st.session_state["page"]
    with st.sidebar:
        st.markdown('<div class="sb-brand">SecureBank</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sb-user"><div class="sb-avatar">{esc(account["Name"][:1].upper())}</div>'
            f'<div><div class="sb-user-name">{esc(account["Name"])}</div>'
            f'<div class="sb-user-sub">{esc(mask_account(account["AccountNo"]))}</div></div></div>',
            unsafe_allow_html=True,
        )
        for page in PAGES:
            st.button(
                page, key=f"nav_{page}", on_click=set_page, args=(page,),
                type="primary" if page == current else "secondary", use_container_width=True,
            )
        st.divider()
        st.button("Logout", on_click=logout, use_container_width=True)


# ---------- entry point ----------

def main():
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()

    if not st.session_state["logged_in"]:
        if st.session_state["view"] == "register":
            show_register()
        else:
            show_login()
        return

    # Always load the account fresh from the backend using the session's account number
    ok, account = safe_call(bank.Details, st.session_state["account_number"])
    if not ok:
        reset_session()
        flash("error", account)
        st.rerun()

    st.session_state.setdefault("page", PAGES[0])
    show_sidebar(account)
    show_flash()
    PAGE_VIEWS[st.session_state["page"]](account)


main()
