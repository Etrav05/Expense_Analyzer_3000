from FileScrape import price_categorization, debit_finder, vendor_finder, process_csv


# --- price_categorization: check each boundary ---
def test_price_categories():
    assert price_categorization(9.99) == "Small"
    assert price_categorization(10.00) == "Medium"
    assert price_categorization(100.00) == "Large"
    assert price_categorization(1000.00) == "Extreme"
    assert price_categorization(10000.00) == "Massive"


# --- debit_finder ---
def test_debit_finder():
    assert debit_finder("INTERNET DEPOSIT from payroll") == "Debit"
    assert debit_finder("POINT OF SALE PURCHASE Walmart") == "Credit"


# --- vendor_finder ---
def test_vendor_special_cases():
    assert vendor_finder("ATM WITHDRAWAL 123 Main St") == "ATM WITHDRAWAL"
    assert vendor_finder("Branch Transaction deposit") == "BANK"


def test_vendor_skips_long_number_and_keywords():
    assert vendor_finder("INTERAC PURCHASE 12345678 Walmart") == "Walmart"


def test_vendor_strips_store_numbers():
    assert vendor_finder("PURCHASE Tim Hortons#1234") == "Tim Hortons"
    assert vendor_finder("PURCHASE Costco C123") == "Costco"


def test_vendor_keeps_trailing_c():  # regression test for the regex fix
    assert vendor_finder("PURCHASE ABC") == "ABC"


def test_vendor_unknown():
    assert vendor_finder("") == "UNKNOWN"


# --- process_csv with a fake database ---
class FakeDB:
    def __init__(self):
        self.expenses = []
        self.imports = []

    def add_expense(self, *args):
        self.expenses.append(args)

    def log_import(self, path, count):
        self.imports.append((path, count))


def test_process_csv(tmp_path):
    csv = tmp_path / "statement.csv"
    csv.write_text(
        "2024-03-15,POINT OF SALE PURCHASE Walmart,25.50,\n"
        "2024-04-01,INTERNET DEPOSIT,,100.00\n"
        "2024-05-01,No amount row,,\n"
    )
    db = FakeDB()

    assert process_csv(str(csv), db) == 2  # third row skipped
    assert db.expenses[0] == ("2024-03", 25.50, "Medium", "Debit", "Walmart")
    assert db.expenses[1][3] == "Credit"
    assert db.imports == [(str(csv), 2)]