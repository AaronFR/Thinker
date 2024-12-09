import React from 'react';
import './styles/PersonaSelector.css';

const PersonaSelector = ({ selectedPersona, setSelectedPersona, autoDetectedPersona }) => {
  return (
    <div style={{ marginBottom: '20px' }}>
      <label>
        Select Persona:
        <select 
          value={selectedPersona} 
          onChange={(e) => setSelectedPersona(e.target.value)}
          className="dropdown"
        >
          <option value="auto">Auto - {autoDetectedPersona}</option>
          <option value="coder">Coder</option>
          {/* Add more personas as needed */}
        </select>
      </label>
    </div>
  );
};

export default PersonaSelector;
