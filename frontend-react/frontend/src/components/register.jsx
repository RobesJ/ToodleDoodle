import React, {useState} from "react";
import { authAPI } from "../api";
import { useNavigate } from "react-router-dom";
import "./login.css"

const Register = () => {
    const [userData, setUserData] = useState({
        email: '',
        name: '',
        password: '',
        confirmPassword: ''
    });

    const navigate = useNavigate();
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    //change only field which is currently inputed
    const handleInputChange = (field, value) => {
        setUserData(prev => ({
            ...prev,
            [field]: value
        }));
        if (error) setError('');
    }

    // function to check if two passwords fields match
    const validateForm = () => {
        if (userData.password != userData.confirmPassword){
            setError ("Passwords do not match!");
            return false;
        }
        return true;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        if(!validateForm()) return;
        setLoading(true);
        setError('');

        try {
            const registrationData = {
                email: userData.email,
                name: userData.name,
                password: userData.password
            };

            const response = await authAPI.register(registrationData);
            console.log("Registration response:", response);
            if(response.status == 200 || response.status == 201) {

                setUserData({
                    email: '',
                    name: '',
                    password: '',
                    confirmPassword: ''
                });

                // Redirect to login after 2 seconds
                setTimeout(() => {
                    navigate('/login', {
                    state: { 
                        message: 'Registration successful! Please login to continue.' 
                    } 
                });
                }, 200);

            }
            else{
                setError("Registration failed! Please try it again");
            }
        }
        catch (err) {
            console.error('Registration error:', err);
            if (err.response?.status === 400) {
                setError(err.response.data?.detail || "Invalid registration data");
            } else if (err.response?.status === 409) {
                setError("Email already exists. Please use a different email.");
            } else {
                setError(err.response?.data?.detail || "Registration failed. Please try again.");
            }
        }
        finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container">
        <div className="register-page">
          <h2>Sign Up</h2>
          <form onSubmit={handleSubmit}>
          <div className="container">
                <div className="input">
                  <input
                    type="email"
                    placeholder="Email"
                    value={userData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    required
                  />
                </div>
                <div className="input">
                  <input
                    type="name"
                    placeholder="User Name"
                    value={userData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    required
                  />
                </div>
                <div className="input">
                  <input
                    type="password"
                    placeholder="Password"
                    value={userData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    required
                  />
                </div>
                <div className="input">
                  <input
                    type="password"
                    placeholder="Password"
                    value={userData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                    required
                  />
                </div>
                <div className="button">
                    <button type="submit" disabled={loading}>
                    {loading ? 'Processing...' : 'Sign Up'}
                    </button>
                </div>
            </div>
          </form>
          {error && <p style={{color: 'red'}}>{error}</p>}
          </div>
          <div className="brand-section">
            <h1 className="brand-name">CreaDo</h1>
            <p className="brand-tagline">Create. Organize. Achieve.</p>
        </div>
    </div>
    );
};

export default Register;