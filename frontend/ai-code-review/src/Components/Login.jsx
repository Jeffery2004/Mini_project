import {React,useState} from 'react'
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import './Login.scss';
const Login = () => {
  const[email,setEmail]=useState('');
  const[password,setPassword]=useState('');
  const navigate = useNavigate();
  async function handleLogin(e){
    e.preventDefault();
    try{
      const resp=await axios.post('http://localhost:3000/user/login',{email,password});
      if(resp.data.message==="incomplete"){
        alert("Enter all details");
      }
      else if(resp.data.token){
        console.log(localStorage.getItem('token'));
        localStorage.setItem('token',resp.data.token);
        navigate("/");
      }else{
        alert("login failed");
      }
    }catch(err){
      alert("Invalid email or password");
    }
  }
  return (
    <div className='login-container'>
      <div className='card'>
        <h1>Login</h1>
        <label htmlFor='email'>Email</label><br></br>
        <input type='email' id='email' value={email} onChange={(e)=>{setEmail(e.target.value)}}></input><br></br>
        <label htmlFor='password'>Password</label><br></br>
        <input type='password' id='password' value={password} onChange={(e)=>{setPassword(e.target.value)}}></input><br></br>
        <button onClick={handleLogin}>Login</button><br></br>
        <a href='/signup'>Signup?</a>
      </div>
    </div>
  )
}

export default Login
