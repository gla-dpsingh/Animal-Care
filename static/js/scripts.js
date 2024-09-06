document.addEventListener('DOMContentLoaded', function() {
    // Registration form submission
    document.getElementById('registerForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const phone = document.getElementById('phone').value;

        // Send registration request to the backend
        fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password, phone })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Registration successful!');
                window.location.href = 'login.html';
            } else {
                alert('Registration failed: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Login form submission
    document.getElementById('loginForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Send login request to the backend
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Login successful!');
                window.location.href = 'profile.html';
            } else {
                alert('Login failed: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Report form submission
    document.getElementById('reportForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const symptoms = document.getElementById('symptoms').value;
        const image = document.getElementById('image').files[0];

        const formData = new FormData();
        formData.append('symptoms', symptoms);
        formData.append('image', image);

        // Send report request to the backend
        fetch('/api/report', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Report submitted successfully!');
            } else {
                alert('Report submission failed: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

   

    // Video call form submission
    document.getElementById('videoCallForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const vet = document.getElementById('vet').value;

        // Logic for starting a video call
        alert(`Starting a video call with ${vet}`);
        // Implement the actual video call logic here
    });
});

