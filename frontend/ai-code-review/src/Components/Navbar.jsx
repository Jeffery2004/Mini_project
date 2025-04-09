import { React, useState } from 'react';
import './Navbar.scss';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Navbar = () => {
  const token = localStorage.getItem('token');
  const navigate = useNavigate();
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const [userDetails, setUserDetails] = useState(null);

  async function handleLogout() {
    localStorage.removeItem('token');
    navigate('/login');
  }

  const fetchUserProfile = async () => {
    try {
      const response = await axios.post('http://localhost:3000/user/profile',{token});
      return response.data;
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  };

  const handleProfileClick = async (e) => {
    e.preventDefault();
    if (!token) {
      alert('Please log in first!');
      return;
    }

    setShowProfilePopup(true);

    try {
      const data = await fetchUserProfile();
      setUserDetails(data);
    } catch (error) {
      console.error('Failed to fetch profile details');
      setShowProfilePopup(false);
    }
  };

  return (
    <div className='nav-container'>
      <div className='logo'>
        <b><a href="/">Code<span>Review</span></a></b>
      </div>
      <div className='side-list'>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/" onClick={handleProfileClick}>Profile</a></li>
          {token ? (
            <li><a href="/login" onClick={handleLogout}>Logout</a></li>
          ) : (
            <li><a href="/login">Login</a></li>
          )}
        </ul>
      </div>
      {showProfilePopup && userDetails && (
        <div className='profile-popup'>
          <h2>User Profile</h2>
          <p><strong>Name:</strong> {userDetails.name}</p>
          <p><strong>Email:</strong> {userDetails.email}</p>
          <p><strong>Github:</strong> {userDetails.link}</p>
          <button onClick={() => setShowProfilePopup(false)}>Close</button>
        </div>
      )}
    </div>
  );
};

export default Navbar;