# Day88
Python project for day 88

Solution
Below is the enhanced Python code using Flask to create a REST API and serve a dynamic website. The frontend will use Tailwind CSS for styling, and JavaScript will handle API interactions for a smooth user experience.
Project Structure
project/
├── app.py
├── cafes.db  # Your existing SQLite database
├── static/
│   └── script.js
├── templates/
│   ├── index.html
│   ├── add_cafe.html
│   └── layout.html
Step 1: Python Code (app.py)
This Flask application creates REST API endpoints and serves the website. It connects to your cafes.db database and includes routes for viewing, adding, and deleting cafes.
python
# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('cafes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database (if needed, ensures table exists)
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

# Web: Home page (list cafes)
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

# Run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
Step 2: HTML Templates
Create a templates folder with the following files. These use Tailwind CSS for a modern, clean design inspired by LaptopFriendly.co.
Base Layout (layout.html)
html
<!-- templates/layout.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cafes for Remote Work</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body class="bg-gray-100 font-sans">
    <nav class="bg-white shadow p-4">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold text-gray-800">RemoteWork Cafes</h1>
            <a href="{{ url_for('add_cafe') }}" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Add Cafe</a>
        </div>
    </nav>
    <div class="container mx-auto p-4">
        {% block content %}{% endblock %}
    </div>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
Home Page (index.html)
This page fetches cafe data via the API and allows filtering and deletion.
html
<!-- templates/index.html -->
{% extends "layout.html" %}
{% block content %}
    <h2 class="text-3xl font-semibold text-gray-800 mb-6">Find Cafes for Remote Work</h2>
    
    <!-- Filters -->
    <div class="mb-6 flex flex-wrap gap-4">
        <input type="text" id="search" placeholder="Search by name or address..." class="border p-2 rounded w-full md:w-1/3">
        <select id="wifiFilter" class="border p-2 rounded">
            <option value="">All WiFi Speeds</option>
            <option value="Fast">Fast</option>
            <option value="Moderate">Moderate</option>
            <option value="Slow">Slow</option>
        </select>
        <select id="powerFilter" class="border p-2 rounded">
            <option value="">All Power Outlets</option>
            <option value="Many">Many</option>
            <option value="Few">Few</option>
            <option value="None">None</option>
        </select>
        <select id="sort" class="border p-2 rounded">
            <option value="rating_desc">Sort: Rating (High to Low)</option>
            <option value="rating_asc">Sort: Rating (Low to High)</option>
            <option value="name_asc">Sort: Name (A-Z)</option>
        </select>
    </div>

    <!-- Cafe List -->
    <div id="cafeList" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Cafes will be populated by JavaScript -->
    </div>
{% endblock %}
Add Cafe Page (add_cafe.html)
html
<!-- templates/add_cafe.html -->
{% extends "layout.html" %}
{% block content %}
    <h2 class="text-3xl font-semibold text-gray-800 mb-6">Add a New Cafe</h2>
    <form id="addCafeForm" class="max-w-lg bg-white p-6 rounded shadow">
        <div class="mb-4">
            <label for="name" class="block text-gray-700">Cafe Name</label>
            <input type="text" id="name" name="name" class="w-full border p-2 rounded" required>
        </div>
        <div class="mb-4">
            <label for="address" class="block text-gray-700">Address</label>
            <input type="text" id="address" name="address" class="w-full border p-2 rounded" required>
        </div>
        <div class="mb-4">
            <label for="wifi_speed" class="block text-gray-700">WiFi Speed</label>
            <select id="wifi_speed" name="wifi_speed" class="w-full border p-2 rounded" required>
                <option value="Fast">Fast</option>
                <option value="Moderate">Moderate</option>
                <option value="Slow">Slow</option>
            </select>
        </div>
        <div class="mb-4">
            <label for="power_outlets" class="block text-gray-700">Power Outlets</label>
            <select id="power_outlets" name="power_outlets" class="w-full border p-2 rounded" required>
                <option value="Many">Many</option>
                <option value="Few">Few</option>
                <option value="None">None</option>
            </select>
        </div>
        <div class="mb-4">
            <label for="rating" class="block text-gray-700">Rating (0-5)</label>
            <input type="number" id="rating" name="rating" min="0" max="5" step="0.1" class="w-full border p-2 rounded" required>
        </div>
        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Add Cafe</button>
    </form>
    <a href="{{ url_for('index') }}" class="text-blue-500 mt-4 inline-block">Back to Cafe List</a>
{% endblock %}
Step 3: JavaScript (static/script.js)
This script handles API calls, filtering, sorting, and dynamic updates to the cafe list.
javascript
// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const cafeList = document.getElementById('cafeList');
    const searchInput = document.getElementById('search');
    const wifiFilter = document.getElementById('wifiFilter');
    const powerFilter = document.getElementById('powerFilter');
    const sortSelect = document.getElementById('sort');
    const addCafeForm = document.getElementById('addCafeForm');

    // Fetch and display cafes
    function fetchCafes() {
        fetch('/api/cafes')
            .then(response => response.json())
            .then(cafes => {
                let filteredCafes = cafes;

                // Apply filters
                const searchTerm = searchInput.value.toLowerCase();
                const wifiValue = wifiFilter.value;
                const powerValue = powerFilter.value;

                filteredCafes = cafes.filter(cafe => {
                    const matchesSearch = cafe.name.toLowerCase().includes(searchTerm) || 
                                        cafe.address.toLowerCase().includes(searchTerm);
                    const matchesWifi = !wifiValue || cafe.wifi_speed === wifiValue;
                    const matchesPower = !powerValue || cafe.power_outlets === powerValue;
                    return matchesSearch && matchesWifi && matchesPower;
                });

                // Apply sorting
                const sortValue = sortSelect.value;
                filteredCafes.sort((a, b) => {
                    if (sortValue === 'rating_desc') return b.rating - a.rating;
                    if (sortValue === 'rating_asc') return a.rating - b.rating;
                    if (sortValue === 'name_asc') return a.name.localeCompare(b.name);
                    return 0;
                });

                // Display cafes
                cafeList.innerHTML = '';
                filteredCafes.forEach(cafe => {
                    const cafeCard = document.createElement('div');
                    cafeCard.className = 'bg-white p-6 rounded shadow hover:shadow-lg transition';
                    cafeCard.innerHTML = `
                        <h3 class="text-xl font-semibold text-gray-800">${cafe.name}</h3>
                        <p class="text-gray-600"><i class="fas fa-map-marker-alt"></i> ${cafe.address}</p>
                        <p class="text-gray-600"><i class="fas fa-wifi"></i> WiFi: ${cafe.wifi_speed}</p>
                        <p class="text-gray-600"><i class="fas fa-plug"></i> Power: ${cafe.power_outlets}</p>
                        <p class="text-gray-600"><i class="fas fa-star"></i> Rating: ${cafe.rating}/5</p>
                        <button onclick="deleteCafe(${cafe.id})" class="mt-2 text-red-500 hover:text-red-700">Delete</button>
                    `;
                    cafeList.appendChild(cafeCard);
                });
            });
    }

    // Delete a cafe
    window.deleteCafe = function(id) {
        if (confirm('Are you sure you want to delete this cafe?')) {
            fetch(`/api/cafes/${id}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) {
                        fetchCafes();
                    } else {
                        alert('Failed to delete cafe');
                    }
                });
        }
    };

    // Handle form submission
    if (addCafeForm) {
        addCafeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(addCafeForm);
            const cafeData = {
                name: formData.get('name'),
                address: formData.get('address'),
                wifi_speed: formData.get('wifi_speed'),
                power_outlets: formData.get('power_outlets'),
                rating: parseFloat(formData.get('rating'))
            };

            fetch('/api/cafes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cafeData)
            })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/';
                    } else {
                        alert('Failed to add cafe');
                    }
                });
        });
    }

    // Event listeners for filters and sorting
    searchInput.addEventListener('input', fetchCafes);
    wifiFilter.addEventListener('change', fetchCafes);
    powerFilter.addEventListener('change', fetchCafes);
    sortSelect.addEventListener('change', fetchCafes);

    // Initial fetch
    fetchCafes();
});
Step 4: Setup Instructions
1.Install Dependencies:
bash
pip install flask flask-cors
2.Ensure cafes.db Exists:
•Your existing cafes.db should have a cafes table with columns: id, name, address, wifi_speed, power_outlets, rating.
•The init_db() function in app.py ensures the table exists but won't modify your existing data.
3.Create Project Structure:
•Place app.py in the root directory.
•Place cafes.db in the root directory.
•Create a static folder and add script.js.
•Create a templates folder and add layout.html, index.html, and add_cafe.html.
4.Run the Application:
bash
python app.py
5.Access the Website:
•Open http://127.0.0.1:5000 in your browser.

Features and Improvements
1.REST API:
•Endpoints:
•GET /api/cafes: List all cafes.
•GET /api/cafes/<id>: Get a single cafe.
•POST /api/cafes: Add a new cafe.
•DELETE /api/cafes/<id>: Delete a cafe.
•JSON-based, accessible for future integrations.
2.Frontend Design:
•Uses Tailwind CSS for a modern, responsive design similar to LaptopFriendly.co.
•Clean layout with a navigation bar, filters, and cafe cards.
•Font Awesome icons for WiFi, power, location, and rating.
3.Dynamic Features:
•Filtering: Search by name/address, filter by WiFi speed or power outlets.
•Sorting: Sort by rating (high/low) or name (A-Z).
•Add/Delete: Form to add cafes and buttons to delete cafes with confirmation prompts.
•JavaScript fetches data dynamically via the API, updating the UI without page reloads.
4.Inspired by LaptopFriendly.co:
•Clean, professional design with a focus on usability.
•Card-based layout for cafes, showing key details (name, address, WiFi, power, rating).
•Filters and sorting for easy navigation.
•Simple navigation with an "Add Cafe" button.
5.Database Integration:
•Reuses your cafes.db SQLite database.
•Ensures compatibility with the existing schema.

Potential Enhancements
To make the website even closer to LaptopFriendly.co or add more functionality, consider:
•Map Integration: Use Google Maps or Leaflet to show cafe locations.
•User Authentication: Add login/signup to restrict who can add/delete cafes.
•Cafe Details Page: Create a dedicated page for each cafe with more details (e.g., photos, reviews).
•Reviews and Comments: Allow users to submit reviews or comments for cafes.
•Advanced Filters: Filter by additional criteria (e.g., opening hours, coffee quality).
•Image Upload: Allow users to upload cafe photos when adding a cafe.
•Pagination or Infinite Scroll: Handle large datasets more efficiently.
•SEO Optimization: Add meta tags and structured data for better search engine visibility.

Example Output
•Home Page: Displays a grid of cafe cards with name, address, WiFi speed, power outlets, and rating. Users can filter by search term, WiFi speed, or power outlets and sort by rating or name. Each card has a "Delete" button.
•Add Cafe Page: A form to input cafe details, styled with Tailwind CSS for a clean look.
•API: Accessible at /api/cafes for fetching cafe data, with endpoints for adding and deleting cafes.
