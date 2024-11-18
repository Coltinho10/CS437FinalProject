fetch('http://localhost:5000/data')
    .then(response => response.json())
    .then(data => {
        console.log(data); // Handle the fetched data
    })
    .catch(error => console.error('Error fetching data:', error));