import React from 'react';

const URL = 'http://localhost:8000';
const LoginPage = () => {

    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        // Handle login logic here
        const res = await fetch(`${URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.access);
            window.location.href = '/chat';
        } else {
            alert('Login failed: ' + data.detail);
        }
    }
    return ( 
        <div className='flex flex-col gap-4 p-4 justify-center items-center h-screen'>
            Login Page
            <div className='flex flex-col gap-4'>
                <input value={username} type="text" placeholder="Username" onChange={(e) => setUsername(e.target.value)}/>
                <input value={password} type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)}/>
                <button onClick={(e) => handleSubmit(e)}>Login</button>
            </div>
        </div>
     );
}
 
export default LoginPage;
