# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS 
import sqlite3
from scraper import scrape_laptopfriendly, scrape_mock_data

app = Flask(__name__)
CORS(app)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('cafes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cafes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     address TEXT NOT NULL,
                     wifi_speed TEXT,
                     power_outlets TEXT,
                     rating REAL)''')
        conn.commit()

# API: Get all cafes
@app.route('/api/cafes', methods=['GET'])
def get_cafes():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM cafes')
    cafes = c.fetchall()
    conn.close()
    return jsonify([dict(cafe) for cafe in cafes])

# API: Get single cafe by ID
@app.route('/api/cafes/<int:id>', methods=['GET'])
def get_cafe(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM cafes WHERE id = ?', (id,))
    cafe = c.fetchone()
    conn.close()
    if cafe is None:
        return jsonify({'error': 'Cafe not found'}), 404
    return jsonify(dict(cafe))

# API: Add a new cafe
@app.route('/api/cafes', methods=['POST'])
def add_cafe_api():
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    wifi_speed = data.get('wifi_speed')
    power_outlets = data.get('power_outlets')
    rating = float(data.get('rating'))

    if not all([name, address, wifi_speed, power_outlets, rating]):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO cafes (name, address, wifi_speed, power_outlets, rating) VALUES (?, ?, ?, ?, ?)',
              (name, address, wifi_speed, power_outlets, rating))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Cafe added successfully'}), 201

# API: Delete a cafe
@app.route('/api/cafes/<int:id>', methods=['DELETE'])
def delete_cafe(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM cafes WHERE id = ?', (id,))
    if c.fetchone() is None:
        conn.close()
        return jsonify({'error': 'Cafe not found'}), 404
    c.execute('DELETE FROM cafes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Cafe deleted successfully'})

# New route: Scrape cafes
@app.route('/scrape', methods=['GET'])
def scrape_cafes():
    try:
        # Use scrape_laptopfriendly() for real scraping (check ToS first)
        # For testing, use scrape_mock_data()
        count = scrape_mock_data()  # Switch to scrape_laptopfriendly() after verifying ToS
        return jsonify({'message': f'Successfully added {count} cafes to the database'})
    except Exception as e:
        return jsonify({'error': f'Scraping failed: {str(e)}'}), 500

# Web: Home page
@app.route('/')
def index():
    return render_template('index.html')

# Web: Add cafe page
@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        wifi_speed = request.form['wifi_speed']
        power_outlets = request.form['power_outlets']
        rating = float(request.form['rating'])

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO cafes (name, address, wifi_speed, power_outlets, rating) VALUES (?, ?, ?, ?, ?)',
                  (name, address, wifi_speed, power_outlets, rating))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_cafe.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    