import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from main import AutoClicker


class TestAutoClicker(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AutoClicker(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('pyautogui.position')
    def test_add_location_first_time(self, mock_position):
        mock_position.return_value = (100, 200)
        self.app.local_interval_var.set("1.0")
        self.app.add_location()
        self.assertEqual(len(self.app.locations), 1)
        self.assertEqual(self.app.locations[0], (100, 200, 1.0))

    @patch('pyautogui.position')
    def test_add_location_duplicate(self, mock_position):
        mock_position.return_value = (100, 200)
        self.app.local_interval_var.set("1.0")
        self.app.add_location()  # First time
        self.assertEqual(len(self.app.locations), 1)
        # With lock, duplicate calls are ignored without message
        self.app.add_location()  # Duplicate - should be ignored
        self.assertEqual(len(self.app.locations), 1)  # Should not add again

    @patch('pyautogui.position')
    def test_add_location_different_positions(self, mock_position):
        mock_position.side_effect = [(100, 200), (150, 250)]
        self.app.local_interval_var.set("1.0")
        self.app.add_location()
        self.app.add_location()
        self.assertEqual(len(self.app.locations), 2)
        self.assertEqual(self.app.locations[0], (100, 200, 1.0))
        self.assertEqual(self.app.locations[1], (150, 250, 1.0))

    def test_clear_locations(self):
        self.app.locations = [(100, 200, 1.0), (150, 250, 2.0)]
        self.app.clear_locations()
        self.assertEqual(len(self.app.locations), 0)

    def test_remove_location(self):
        self.app.locations = [(100, 200, 1.0), (150, 250, 2.0)]
        self.app.update_locations_listbox()
        self.app.locations_listbox.select_set(0)
        self.app.remove_location()
        self.assertEqual(len(self.app.locations), 1)
        self.assertEqual(self.app.locations[0], (150, 250, 2.0))

    def test_remove_location_no_selection(self):
        self.app.locations = [(100, 200, 1.0)]
        self.app.remove_location()  # No selection
        self.assertEqual(len(self.app.locations), 1)

    @patch('pyautogui.position')
    def test_start_no_locations(self, mock_position):
        mock_position.return_value = (100, 200)
        with patch('tkinter.messagebox.askyesno', return_value=True):
            with patch.object(self.app, '_worker'):
                self.app.start()
                self.assertEqual(len(self.app.locations), 1)

    def test_update_locations_listbox(self):
        self.app.locations = [(100, 200, None), (150, 250, 2.0)]
        self.app.update_locations_listbox()
        items = self.app.locations_listbox.get(0, tk.END)
        self.assertEqual(items[0], "1. 100, 200  @ padrão")
        self.assertEqual(items[1], "2. 150, 250  @ 2.00s")

    @patch('pyautogui.position')
    def test_add_location_invalid_interval(self, mock_position):
        mock_position.return_value = (100, 200)
        self.app.local_interval_var.set("invalid")
        with patch('tkinter.messagebox.showerror') as mock_error:
            self.app.add_location()
            mock_error.assert_called_once()
        self.assertEqual(len(self.app.locations), 0)


if __name__ == '__main__':
    unittest.main()