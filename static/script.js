// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const cafeList = document.getElementById('cafeList');
    const searchInput = document.getElementById('search');
    const wifiFilter = document.getElementById('wifiFilter');
    const powerFilter = document.getElementById('powerFilter');
    const sortSelect = document.getElementById('sort');
    const addCafeForm = document.getElementById('addCafeForm');
    const scrapeButton = document.getElementById('scrapeButton');

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

    // Handle scrape button
    if (scrapeButton) {
        scrapeButton.addEventListener('click', (e) => {
            e.preventDefault();
            fetch('/scrape')
                .then(response => response.json())
                .then(data => {
                    alert(data.message || data.error);
                    fetchCafes();  // Refresh cafe list
                })
                .catch(error => {
                    alert('Error during scraping: ' + error);
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
