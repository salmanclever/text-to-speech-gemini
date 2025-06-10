import React from 'react';
import AudioPlayer from 'react-h5-audio-player';
import 'react-h5-audio-player/lib/styles.css';
import { Box, Typography, Paper } from '@mui/material';

const AudioPlayerWrapper = ({ audioUrls, onPlaybackError }) => {
  if (!audioUrls || audioUrls.length === 0) {
    return null;
  }

  const handlePlayError = (e, url, index) => {
    const errorMsg = `خطا در پخش قطعه صوتی ${index + 1}. ممکن است فایل خراب باشد یا مشکلی در شبکه وجود داشته باشد.`;
    console.error('Audio Play Error:', e, 'URL:', url);
    if (onPlaybackError) {
      onPlaybackError(errorMsg);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      {audioUrls.map((url, index) => (
        <Paper key={index} elevation={2} sx={{ mb: 2, p: 2 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'medium' }}>
            قطعه صوتی {index + 1}
          </Typography>
          <AudioPlayer
            src={url}
            onPlayError={(e) => handlePlayError(e, url, index)}
            // autoPlayAfterSrcChange={index === 0} // Optional: autoplay first track
          />
        </Paper>
      ))}
    </Box>
  );
};

export default AudioPlayerWrapper;
