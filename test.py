import unittest
import sqlite3
from datetime import datetime, timedelta
from main import init_db, execute_query, fetch_all, fetch_one, DB_NAME

class TestAirlineManagementSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup the test database schema before running tests."""
        init_db()
        cls.conn = sqlite3.connect(DB_NAME)

        # Insert default admin
        cls.conn.execute("INSERT INTO admins (username, password) VALUES ('test_admin', 'admin123')")
        
        # Insert sample user
        cls.conn.execute("""
            INSERT INTO users (username, password, email, role) 
            VALUES ('test_user', 'user123', 'test_user@example.com', 'user')
        """)
        
        # Insert sample flights
        cls.conn.execute("""
            INSERT INTO flights (flight_number, destination, departure, price, seats_available, status) 
            VALUES 
            ('FL101', 'New York', '2024-12-15 08:00:00', 500.00, 20, 'On Time'),
            ('FL102', 'London', '2024-12-16 10:00:00', 450.00, 15, 'On Time'),
            ('FL103', 'Paris', '2024-12-17 13:00:00', 400.00, 10, 'On Time')
        """)
        
        # Insert sample promotion
        cls.conn.execute("""
            INSERT INTO promotions (code, discount, expiration_date)
            VALUES ('PROMO20', 20, ?)
        """, ((datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),))

        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test database after running tests."""
        cls.conn.execute("DELETE FROM admins")
        cls.conn.execute("DELETE FROM users")
        cls.conn.execute("DELETE FROM flights")
        cls.conn.execute("DELETE FROM promotions")
        cls.conn.execute("DELETE FROM passengers")
        cls.conn.execute("DELETE FROM transactions")
        cls.conn.execute("DELETE FROM logs")
        cls.conn.commit()
        cls.conn.close()

    def test_admin_login(self):
        """Test admin login functionality."""
        admin = fetch_one("SELECT * FROM admins WHERE username = 'test_admin' AND password = 'admin123'")
        self.assertIsNotNone(admin, "Admin login test failed. Admin not found in database.")

    def test_user_registration(self):
        """Test user registration functionality."""
        execute_query("""
            INSERT INTO users (username, password, email, role) 
            VALUES ('new_user', 'newpass123', 'new_user@example.com', 'user')
        """)
        user = fetch_one("SELECT * FROM users WHERE username = 'new_user'")
        self.assertIsNotNone(user, "User registration test failed. User not found in database.")

    def test_flight_creation(self):
        """Test flight creation functionality."""
        execute_query("""
            INSERT INTO flights (flight_number, destination, departure, price, seats_available, status) 
            VALUES ('FL104', 'Tokyo', '2024-12-20 14:00:00', 600.00, 25, 'On Time')
        """)
        flight = fetch_one("SELECT * FROM flights WHERE flight_number = 'FL104'")
        self.assertIsNotNone(flight, "Flight creation test failed. Flight not found in database.")

    def test_promotion_creation(self):
        """Test promotion creation functionality."""
        execute_query("""
            INSERT INTO promotions (code, discount, expiration_date)
            VALUES ('DISCOUNT10', 10, ?)
        """, ((datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),))
        promo = fetch_one("SELECT * FROM promotions WHERE code = 'DISCOUNT10'")
        self.assertIsNotNone(promo, "Promotion creation test failed. Promotion not found in database.")

    def test_ticket_booking(self):
        """Test ticket booking functionality."""
        # Assume user 1 books flight 1
        ticket_id = f"TID{datetime.now().strftime('%Y%m%d%H%M%S')}"
        execute_query("""
            INSERT INTO passengers (user_id, name, age, passport_number, ticket_id, flight_id)
            VALUES (1, 'John Doe', 30, 'P12345', ?, 1)
        """, (ticket_id,))
        passenger = fetch_one("SELECT * FROM passengers WHERE ticket_id = ?", (ticket_id,))
        self.assertIsNotNone(passenger, "Ticket booking test failed. Passenger not found in database.")

    def test_apply_promotion(self):
        """Test applying a promotion to a transaction."""
        promo = fetch_one("SELECT * FROM promotions WHERE code = 'PROMO20'")
        self.assertIsNotNone(promo, "Promotion test failed. Promotion not found in database.")
        self.assertGreater(promo[2], 0, "Promotion discount should be greater than 0.")

    def test_dynamic_pricing(self):
        """Test dynamic pricing functionality."""
        flight_id = 1  # Test flight ID
        before_price = fetch_one("SELECT price FROM flights WHERE flight_id = ?", (flight_id,))[0]

        # Simulate reducing seats to trigger dynamic pricing
        execute_query("UPDATE flights SET seats_available = 10 WHERE flight_id = ?", (flight_id,))
        flight = fetch_one("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
        new_price = flight[4]  # Get updated price
        self.assertGreater(new_price, before_price, "Dynamic pricing test failed. Price did not increase.")

    def test_log_creation(self):
        """Test that user actions are logged."""
        execute_query("""
            INSERT INTO logs (user_id, action, details)
            VALUES (1, 'Test Action', 'Performed a test action.')
        """)
        log = fetch_one("SELECT * FROM logs WHERE action = 'Test Action'")
        self.assertIsNotNone(log, "Log creation test failed. Log not found in database.")

    def test_archiving_flights(self):
        """Test archiving of past flights."""
        # Add a flight in the past
        execute_query("""
            INSERT INTO flights (flight_number, destination, departure, price, seats_available, status) 
            VALUES ('ARCHIVE01', 'Past Destination', '2023-01-01 00:00:00', 200.00, 0, 'On Time')
        """)
        execute_query("""
            INSERT INTO archived_flights (flight_id, flight_number, destination, departure, price, seats_available, status, created_at)
            SELECT flight_id, flight_number, destination, departure, price, seats_available, status, created_at
            FROM flights WHERE departure < ?
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        archived_flight = fetch_one("SELECT * FROM archived_flights WHERE flight_number = 'ARCHIVE01'")
        self.assertIsNotNone(archived_flight, "Flight archiving test failed. Flight not found in archive.")

    def test_notification_creation(self):
        """Test that notifications are created for users."""
        execute_query("""
            INSERT INTO notifications (user_id, flight_id, message, is_read, created_at)
            VALUES (1, 1, 'Test notification message.', 0, ?)
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        notification = fetch_one("SELECT * FROM notifications WHERE message = 'Test notification message.'")
        self.assertIsNotNone(notification, "Notification creation test failed. Notification not found in database.")


if __name__ == "__main__":
    unittest.main()
