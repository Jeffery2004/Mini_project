import './Codearea.scss';
import React, { useState } from 'react';

const Review = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [optimizedCode, setOptimizedCode] = useState('');
  const [securityIssues, setSecurityIssues] = useState([]);

  const handleSubmit = async () => {
    try {
      const response = await fetch('http://localhost:8000/review', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language, code }),
      });
  
      const data = await response.json();
      console.log("API Response:", data);
      setOptimizedCode(data.optimized_code);
      setSecurityIssues(data.security_issues);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  

  return (
    <div className='review-container'>
      <h1>Review Your Code</h1>
      <div className='review-text'>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={15}
          cols={60}
          placeholder="Paste your code here..."
        />
        <label htmlFor='opt'>Language:</label>
        <select id='opt' value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="c">C</option>
          <option value="c++">C++</option>
          <option value="java">Java</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>

      <div className='review-bt'>
        <button onClick={handleSubmit}>Review and Optimize</button>
      </div>

      {optimizedCode && (
        <div className='output'>
          <h2>Optimized Code:</h2>
          <pre>{optimizedCode}</pre>
        </div>
      )}

      {securityIssues.length > 0 && (
        <div className='output'>
          <h2>Security Issues:</h2>
          <ul>
            {securityIssues.map((issue, index) => (
              <li key={issue}>{issue}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Review;