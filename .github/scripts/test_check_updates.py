import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from datetime import datetime
import os
from check_updates import check_updates, update_file_content, get_website_content
from config import CONSULATES

class TestCheckUpdates(unittest.TestCase):
    def setUp(self):
        self.sample_html = """
        <html>
            <body>
                <div>
                    <p>Office Address: 2018 156th Ave NE, Suite 126, Bellevue, WA 98007</p>
                    <p>Phone: +1 (206) 324-9000</p>
                    <p>Email: info@nepalconsulate.org</p>
                    <p>Hours: Monday-Friday 9:00 AM - 5:00 PM</p>
                </div>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.sample_html, 'html.parser')
        self.consulate_info = CONSULATES['washington-state']

    def test_check_updates_finds_changes(self):
        changes = check_updates(self.soup, self.consulate_info)
        self.assertTrue(isinstance(changes, dict))
        self.assertIn('hours', changes)
        self.assertIn('Monday-Friday', changes['hours'])

    def test_get_website_content_handles_error(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception('Test error')
            result = get_website_content('http://test.com')
            self.assertIsNone(result)

    def test_update_file_content(self):
        content = """
# Test Consulate

## Location and Contact Information

*Address:* 
Old Address

*Hours:*
Old Hours

*Page last updated: May 1, 2025*
"""
        changes = {
            'address': 'New Address',
            'hours': 'New Hours'
        }
        current_date = 'May 24, 2025'
        
        updated_content = update_file_content(content, changes, current_date)
        
        self.assertIn('New Address', updated_content)
        self.assertIn('New Hours', updated_content)
        self.assertIn('*Page last updated: May 24, 2025*', updated_content)

if __name__ == '__main__':
    unittest.main()
