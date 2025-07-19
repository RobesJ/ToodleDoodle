import React, {use, useEffect, useState} from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { authAPI } from "../api";
import "./login.css"

const Login = () => {
    const [credentials, setCredentials] = useState({
        email: '',
        password: ''
    });

    const location = useLocation();
    const navigate = useNavigate();
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if(location.state?.message){
            setSuccess(location.state.message);
            //setTimeout(() => {
            //    setSuccess('');
            //}, 5000);
        }
    }, [location]);

    const handleSignUpClick = () => {
        navigate("/register");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess(''); // Clear previous success

        try {
            const response = await authAPI.login(credentials);
            if(response.data && response.data.access_token) {
                localStorage.setItem("access_token", response.data.access_token);
                setSuccess("Login successful!");
                //setTimeout(() => {
                    navigate("/user_page");
                //}, 2000);

            }
            else{
                console.log("No access_token in response");
                setError("Login response missing access token");
            }
        }
        catch (err) {
            console.error('Login error:', err);
            setError(err.response?.data?.detail || "Login failed");
        }
        finally {
            setLoading(false);
        }
    };

    return (
        <div>
          <h2>Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="container">
                <div className="input">
                    <input
                    type="email"
                    placeholder="Email"
                    value={credentials.email}
                    onChange={(e) => setCredentials({...credentials, email: e.target.value})}
                    required
                  />
                </div>
                <div className="input">
                  <input
                    type="password"
                    placeholder="Password"
                    value={credentials.password}
                    onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                    required
                  />
                </div>
                <div className="button">
                    <button type="submit" disabled={loading}>
                    {loading ? 'Logging in...' : 'Login'}
                    </button>
                </div>
                <div className="signUp-link">
                    Don't have an account? 
                    <button
                      type="button" 
                      onClick={handleSignUpClick}
                      className="link-button"
                    >
                      Sign up here
                    </button>
                </div>
            </div>
          </form>
          {success && <p style={{ color: 'green', marginTop: '10px' }}>{success}</p>}
          {error && <p style={{color: 'red'}}>{error}</p>}
        </div>
    );
};

export default Login;