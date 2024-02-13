import sqlite3
import datetime
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactTableManager:
    def __init__(self, db_file='contacts.db'):
        self.db_file = db_file
        self.lock = threading.Lock()
        self.local = threading.local()
        self.create_table()

    def get_connection(self):
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.db_file)
        return self.local.conn

    def create_table(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Contact (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phoneNumber TEXT,
                    email TEXT,
                    linkedId INTEGER,
                    linkPrecedence TEXT,
                    createdAt TEXT,
                    updatedAt TEXT,
                    deletedAt TEXT
                )
            ''')
            conn.commit()
            logger.info("Contact table created successfully.")
        except sqlite3.Error as e:
            logger.error("Error creating Contact table: %s", e)

    def get_contacts(self, email, phoneNumber):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM Contact
                WHERE email = ? OR phoneNumber = ?
            ''', (email, phoneNumber))
            contacts = cursor.fetchall()
            logger.info("Contacts fetched successfully.")
            return contacts
        except sqlite3.Error as e:
            logger.error("Error fetching contacts: %s", e)
            return []

    def create_contact(self, email, phoneNumber):
        try:
            logger.info("Creating primary contact...")
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Contact (phoneNumber, email, linkPrecedence, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?)
            ''', (phoneNumber, email, 'primary', datetime.datetime.now(), datetime.datetime.now()))
            conn.commit()
            primary_contact_id = cursor.lastrowid
            logger.info("Primary contact created successfully with ID: %s", primary_contact_id)
            return primary_contact_id
        except sqlite3.Error as e:
            logger.error("Error creating primary contact: %s", e)
            return None

    def update_contact(self, email, phoneNumber, primary_contact_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            existing_secondary_contact_id = None
            matched_contacts = self.get_contacts(email, phoneNumber)

            for contact in matched_contacts:
                if contact[0] != primary_contact_id and contact[2] != email:
                    existing_secondary_contact_id = contact[0]
                    break

            if existing_secondary_contact_id:
                cursor.execute('''
                    UPDATE Contact
                    SET email = ?, updatedAt = ?
                    WHERE id = ?
                ''', (email, datetime.datetime.now(), existing_secondary_contact_id))
                conn.commit()
                logger.info("Existing secondary contact updated successfully.")
            else:
                cursor.execute('''
                    INSERT INTO Contact (phoneNumber, email, linkedId, linkPrecedence, createdAt, updatedAt)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (phoneNumber, email, primary_contact_id, 'secondary', datetime.datetime.now(), datetime.datetime.now()))
                conn.commit()
                logger.info("New secondary contact created successfully.")

                cursor.execute('''
                    UPDATE Contact
                    linkPrecedence = ?
                    WHERE id = ?
                ''', ('primary', primary_contact_id))
                conn.commit()
                logger.info("Primary contact updated successfully.")
        except sqlite3.Error as e:
            logger.error("Error updating or creating secondary contact: %s", e)
