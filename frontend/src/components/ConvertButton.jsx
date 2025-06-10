import React from 'react';
import { Button, Box } from '@mui/material';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline'; // Example Icon

const ConvertButton = ({ onConvert, isLoading }) => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%'}}>
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={onConvert}
        disabled={isLoading}
        startIcon={!isLoading ? <PlayCircleOutlineIcon /> : null}
        sx={{ minWidth: '200px', py: 1.5, textTransform: 'none', fontSize: '1.1rem' }}
      >
        {isLoading ? 'در حال پردازش...' : 'تبدیل به گفتار'}
      </Button>
    </Box>
  );
};

export default ConvertButton;
