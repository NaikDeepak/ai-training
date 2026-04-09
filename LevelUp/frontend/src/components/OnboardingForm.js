import React, { useState } from 'react';

function OnboardingForm({ onSubmit }) {
  const [userGoal, setUserGoal] = useState('');
  const [timePerDayMinutes, setTimePerDayMinutes] = useState(60);
  const [skillLevel, setSkillLevel] = useState('intermediate');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/plan/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_goal: userGoal,
          time_per_day_minutes: parseInt(timePerDayMinutes, 10),
          skill_level: skillLevel,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Success: ${data.message} Plan ID: ${data.plan_id}`);
        onSubmit(data.plan_id); // Notify parent of successful submission
      } else {
        setMessage(`Error: ${data.detail || 'Failed to generate plan.'}`);
      }
    } catch (error) {
      console.error('Error initiating plan generation:', error);
      setMessage('Network error or server unreachable.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '500px', margin: 'auto', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>Set Your Learning Goal</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="userGoal" style={{ display: 'block', marginBottom: '5px' }}>
            Your Learning Goal:
          </label>
          <input
            type="text"
            id="userGoal"
            value={userGoal}
            onChange={(e) => setUserGoal(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="timePerDay" style={{ display: 'block', marginBottom: '5px' }}>
            Minutes per day:
          </label>
          <input
            type="number"
            id="timePerDay"
            value={timePerDayMinutes}
            onChange={(e) => setTimePerDayMinutes(e.target.value)}
            min="10"
            max="240"
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="skillLevel" style={{ display: 'block', marginBottom: '5px' }}>
            Current Skill Level:
          </label>
          <select
            id="skillLevel"
            value={skillLevel}
            onChange={(e) => setSkillLevel(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Generating Plan...' : 'Generate My 90-Day Plan'}
        </button>
      </form>

      {message && <p style={{ marginTop: '20px', color: message.startsWith('Error') ? 'red' : 'green' }}>{message}</p>}
    </div>
  );
}

export default OnboardingForm;
