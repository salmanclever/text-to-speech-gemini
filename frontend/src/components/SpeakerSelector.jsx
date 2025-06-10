import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, Typography, Box } from '@mui/material';

const SpeakerSelector = ({ speakers, selectedSpeaker, onSpeakerChange, disabled }) => {
  return (
    <Box>
      <Typography variant="h6" component="label" htmlFor="speaker-select-label" gutterBottom sx={{ display: 'block', mb: 1.5 }}>
        انتخاب گوینده:
      </Typography>
      <FormControl fullWidth disabled={disabled}>
        <InputLabel id="speaker-select-label">گوینده</InputLabel>
        <Select
          labelId="speaker-select-label"
          id="speaker-select"
          value={selectedSpeaker}
          label="گوینده"
          onChange={(e) => onSpeakerChange(e.target.value)}
          sx={{ fontFamily: 'Vazirmatn, Roboto, Arial' }}
        >
          {Object.entries(speakers).map(([displayName, speakerId]) => (
            <MenuItem key={speakerId} value={speakerId} sx={{ fontFamily: 'Vazirmatn, Roboto, Arial' }}>
              {displayName}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default SpeakerSelector;
