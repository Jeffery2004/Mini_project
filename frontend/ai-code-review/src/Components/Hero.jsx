import React from "react";
import "./Hero.scss";
const Hero = () => {
  
  return (
    <div className="hero-container">
      <div className="hero-text">
        <h1>AI-Powered Code<br></br> <span>Review</span> &<br></br><span>Optimization</span></h1>
      </div>
      <div className="hero-bt">
        <a href="/codearea">Get Started !!</a>
      </div>
    </div>
  );
};

export default Hero;
