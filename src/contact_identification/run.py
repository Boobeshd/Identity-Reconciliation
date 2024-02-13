from app import app
import os

if __name__ == '__main__':
    if not os.path.exists('contacts.db'):
        os.system('sqlite3 contacts.db < contacts.sql')
    app.run(debug=True)
