import React from 'react';

const flask_port = "http://localhost:5000";

export function Login() {
    const handleRegister = async () => {
        try {
            const response = await fetch(flask_port + '/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({}) // Currently, no data is required in the request body
            });

            if (response.ok) {
                const data = await response.json();
                const token = data.access_token;

                localStorage.setItem("jwt_token", token)

                alert('User registered successfully!');
            } else {
                alert('Failed to register user.');
                console.error('Register request failed with status:', response.status);
            }
        } catch (error) {
            alert('An error occurred during registration.');
            console.error('Error registering user:', error);
        }
    }; 

    const handleLogout = async () => {
        const token = localStorage.getItem("jwt_token");

    if (token) {
        try {
            await fetch(`${flask_port}/logout`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
        } catch (error) {
            console.error("Error logging out:", error);
        }
    }

        localStorage.removeItem("jwt_token");
        window.location.href = "/login"
    }

    return (
        <div className="register-container">
            <nav className="register-nav">
                <a href="/" className="link">Home</a>
                <a href="/pricing" className="link">Pricing</a>
            </nav>
            
            <h2>Register</h2>
            <button onClick={handleRegister}>Register</button>
            <button onClick={handleLogout}>Logout</button>
        </div>
    );
}

export default Login;
