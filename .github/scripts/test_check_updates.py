import unittest
from bs4 import BeautifulSoup
from check_updates import get_website_content, check_updates, update_file_content
from config import CONSULATES
import os

class TestCheckUpdates(unittest.TestCase):
    def setUp(self):
        self.sample_html = """
        <html>
            <body>
                <div class="address">
                    <p>Office Address: 16300 Redmond Way NE, Suite 201, Redmond, WA 98052</p>
                </div>
                <div class="contact">
                    <p>Phone: +1 (206) 324-9000</p>
                    <span>Email: info@nepalconsulatewa.us</span>
                    <script>var x = 'test';</script>
                </div>
                <div class="hours">
                    <p>Office Hours: Monday to Friday 9:00 AM - 5:00 PM</p>
                    <style>.test{color:red;}</style>
                </div>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.sample_html, 'html.parser')
        self.consulate_info = CONSULATES['washington-state']
        
        # Create test data directory if it doesn't exist
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Create a test markdown file
        self.test_md = os.path.join(test_data_dir, 'test_consulate.md')
        with open(self.test_md, 'w') as f:
            f.write("""---
title: Test
layout: default
nav_order: 4
parent: Consulates
---

# Test Consulate Office

## Location and Contact Information

*Address:*  
Old Address
WA 98001

*Phone:*  
+1 (555) 123-4567

*Email:*  
old@nepalconsulatewa.us

*Office Hours:*  
Monday-Friday: 8:00 AM - 4:00 PM

*Page last updated: May 1, 2025*
""")

    def test_check_consulate_updates(self):
        changes = check_consulate_updates(self.soup, self.consulate_info)
        self.assertTrue(isinstance(changes, dict))
        self.assertIn('address', changes)
        self.assertIn('Redmond Way', changes['address'])
        self.assertIn('hours', changes)
        self.assertIn('Monday to Friday', changes['hours'])

    def test_get_website_content_handles_error(self):
        with patch('requests.Session.get') as mock_get:
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

    def test_clean_text(self):
        """Test that text cleaning works correctly"""
        input_text = "  This is  a\n\n test  with\textra   spaces  "
        expected = "This is a test with extra spaces"
        self.assertEqual(clean_text(input_text), expected)

    def test_smoke(self):
        """Simple smoke test to verify basic functionality"""
        # Test that we can create soup object
        html = "<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIsNotNone(soup)

        # Test that we can check for updates
        consulate_info = CONSULATES['washington-state']
        changes = check_updates(soup, consulate_info)
        self.assertIsInstance(changes, dict)

        # Test that we can update content
        content = "# Test\n*Address:*\nOld Address\n*Page last updated: Old Date*"
        updated = update_file_content(content, {"address": "New Address"}, "May 24, 2025")
        self.assertIsInstance(updated, str)

if __name__ == '__main__':
    unittest.main()
