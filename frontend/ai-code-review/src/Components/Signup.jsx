import {React,useState} from 'react'
import axios from 'axios';
import './Signup.scss';
import {useNavigate} from 'react-router-dom';
const Signup = () => {
  const[name,setName]=useState('');
  const[email,setEmail]=useState('');
  const[password,setPassword]=useState('');
  const[githublink,setGithublink]=useState('');
  const navigate = useNavigate();
  async function handleSignin(e){
    e.preventDefault();
    try{
      const resp=await axios.post("http://localhost:3000/user/signup",{name,email,password,githublink});
      if(resp.data.message==="incomplete"){
        alert("Enter all details")
      }else if(resp.data.message==="registered"){
        alert("Already registered");
      }
      else if(resp.data.message==="User created successfully"){
        localStorage.setItem('token',resp.data.token);
        navigate("/login");
        alert("Registerd successfully");
      }
    }catch(err){
      alert("Cannot signup");
    }
  }
  return (
    <div className='signup-container'>
      <div className='card'>
        <h1>Signup</h1>
        <label htmlFor='name'>Name</label><br></br>
        <input type='text' id='name'value={name} onChange={(e)=>{setName(e.target.value)}}></input><br></br>
        <label htmlFor='email'>Email</label><br></br>
        <input type='email' id='email' value={email} onChange={(e)=>{setEmail(e.target.value)}}></input><br></br>
        <label htmlFor='password'>Password</label><br></br>
        <input type='password' id='password' value={password} onChange={(e)=>{setPassword(e.target.value)}}></input><br></br>
        <label htmlFor='url'>Github link</label><br></br>
        <input type='text' id='url'value={githublink} onChange={(e)=>{setGithublink(e.target.value)}}></input><br></br>
        <button onClick={handleSignin}>Signup</button><br></br>
        <a href='/login'>Login?</a>
      </div>
    </div>
  )
}

export default Signup
