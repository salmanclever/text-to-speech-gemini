import React from 'react';
import { TextField, Typography, Box } from '@mui/material';

const TextInput = ({ text, onTextChange, disabled }) => {
  return (
    <Box>
      <Typography variant="h6" component="label" htmlFor="text-input-field" gutterBottom sx={{ display: 'block', mb: 1.5 }}>
        متن فارسی برای تبدیل:
      </Typography>
      <TextField
        id="text-input-field"
        multiline
        rows={10}
        fullWidth
        variant="outlined"
        value={text}
        onChange={(e) => onTextChange(e.target.value)}
        placeholder="متن خود را اینجا وارد کنید..."
        disabled={disabled}
        sx={{ '& .MuiInputBase-root': { fontFamily: 'Vazirmatn, Roboto, Arial' } }}
      />
    </Box>
  );
};

export default TextInput;
