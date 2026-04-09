import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import OnboardingForm from './components/OnboardingForm';
import './App.css';

// Temporary Home component for initial route
function Home() {
  const navigate = useNavigate();
  
  const handleStartOnboarding = () => {
    navigate('/onboarding');
  };

  return (
    <header className="App-header">
      <h1>Welcome to LevelUp!</h1>
      <p>Your personalized 90-day upskilling program.</p>
      <button 
        onClick={handleStartOnboarding}
        style={{
          padding: '10px 20px',
          backgroundColor: '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontSize: '1.1em'
        }}
      >
        Start Your Journey
      </button>
    </header>
  );
}

function App() {
  const navigate = useNavigate();

  const handleOnboardingComplete = (planId) => {
    // Ideally, navigate to a dashboard or status page after plan generation
    console.log(`Plan ${planId} generated. Navigating to dashboard (future).`);
    // For now, let's navigate back to home or a simple message
    navigate('/'); 
  };

  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route 
          path="/onboarding" 
          element={<OnboardingForm onSubmit={handleOnboardingComplete} />} 
        />
        {/* Future routes for Dashboard, Insights, etc. */}
      </Routes>
    </div>
  );
}

// Wrapper for Router to be used in index.js
function AppWrapper() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default AppWrapper;
