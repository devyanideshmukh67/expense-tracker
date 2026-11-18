import os
import tempfile
import unittest

from expense_tracker import ExpenseDB


class TestExpenseDB(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db = ExpenseDB(self.tmp.name)

    def tearDown(self):
        self.db.conn.close()
        os.unlink(self.tmp.name)

    def test_add_and_list(self):
        self.db.add(100, "Food", "lunch", "2026-11-01")
        rows = self.db.list()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "food")

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.db.add(-5, "food")

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            self.db.add(10, "food", spent_on="01-11-2026")

    def test_filter_by_month_and_category(self):
        self.db.add(50, "food", spent_on="2026-10-05")
        self.db.add(70, "travel", spent_on="2026-11-05")
        self.assertEqual(len(self.db.list(month="2026-11")), 1)
        self.assertEqual(len(self.db.list(category="food")), 1)

    def test_summary(self):
        self.db.add(50, "food", spent_on="2026-11-01")
        self.db.add(25, "food", spent_on="2026-11-02")
        self.db.add(10, "travel", spent_on="2026-11-03")
        s = self.db.summary()
        self.assertEqual(s[0]["category"], "food")
        self.assertEqual(s[0]["total"], 75)

    def test_delete(self):
        i = self.db.add(10, "food")
        self.assertTrue(self.db.delete(i))
        self.assertFalse(self.db.delete(i))

    def test_export_csv(self):
        self.db.add(10, "food", spent_on="2026-11-01")
        out = self.tmp.name + ".csv"
        self.assertEqual(self.db.export_csv(out), 1)
        os.unlink(out)


if __name__ == "__main__":
    unittest.main()
