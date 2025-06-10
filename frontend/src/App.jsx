import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';
import TextInput from './components/TextInput';
import SpeakerSelector from './components/SpeakerSelector';
import AudioPlayerWrapper from './components/AudioPlayerWrapper';
import ConvertButton from './components/ConvertButton';
import axios from 'axios';

function App() {
  const [text, setText] = useState('');
  const [selectedSpeaker, setSelectedSpeaker] = useState('');
  const [speakers, setSpeakers] = useState({});
  const [audioUrls, setAudioUrls] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(''); // General errors or API errors
  const [statusMessage, setStatusMessage] = useState('');
  const [playbackError, setPlaybackError] = useState(''); // Specific for audio playback errors

  useEffect(() => {
    const fetchSpeakers = async () => {
      // setIsLoading(true); // Already handled by main loading state if desired
      setError(''); // Clear previous errors
      setPlaybackError(''); // Clear playback errors
      try {
        const response = await axios.get('/api/speakers');
        if (response.data && response.data.speakers && typeof response.data.speakers === 'object') {
          setSpeakers(response.data.speakers);
          const speakerValues = Object.values(response.data.speakers);
          if (speakerValues.length > 0) {
            setSelectedSpeaker(speakerValues[0]);
          }
        } else {
          setError('لیست گویندگان دریافت نشد یا فرمت پاسخ نامعتبر است.');
          setSpeakers({});
        }
      } catch (err) {
        console.error("Error fetching speakers:", err);
        let errorMsg = 'خطا در دریافت لیست گویندگان از سرور.';
        if (err.response && err.response.data && err.response.data.detail) {
            errorMsg += ` جزئیات: ${err.response.data.detail}`;
        } else if (err.message) {
            errorMsg += ` (${err.message})`;
        }
        setError(errorMsg);
        setSpeakers({});
      } finally {
        // setIsLoading(false); // Handled by main loading state
      }
    };
    fetchSpeakers();
  }, []);

  const handleTextChange = (newText) => {
    setText(newText);
  };

  const handleSpeakerChange = (speakerValue) => {
    setSelectedSpeaker(speakerValue);
  };

  const handleConvert = async () => {
    // Clear all previous messages/errors before starting a new conversion
    setError('');
    setPlaybackError('');
    setStatusMessage('');
    setAudioUrls([]);


    if (!text.trim()) {
      setError('متن ورودی نمی‌تواند خالی باشد.');
      return;
    }
    if (!selectedSpeaker) {
      setError('لطفاً یک گوینده انتخاب کنید.');
      return;
    }

    setIsLoading(true);
    setStatusMessage('در حال ارسال درخواست به سرور...');

    try {
      const payload = { text: text, speaker_id: selectedSpeaker };
      // Update status message for actual processing step
      // setTimeout(() => { if(isLoading) setStatusMessage('در حال تبدیل متن به گفتار توسط سرور Gemini...'); }, 500);
      // More direct approach:
      setStatusMessage('در حال تبدیل متن به گفتار توسط سرور...');


      const response = await axios.post('/api/tts', payload);

      if (response.data && response.data.audio_urls) {
        setAudioUrls(response.data.audio_urls);
        setStatusMessage(response.data.message || 'تبدیل با موفقیت انجام شد!');
      } else {
        // If backend returns a specific error structure with 'detail'
        setError(response.data.detail || 'پاسخ نامعتبر از سرور پس از تبدیل.');
        setStatusMessage('');
      }
    } catch (err) {
      console.error("Error during TTS conversion:", err);
      let errorMsg = 'خطا در فرآیند تبدیل متن به گفتار.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = `خطای سرور: ${err.response.data.detail}`;
      } else if (err.request) {
        errorMsg = 'پاسخی از سرور دریافت نشد. لطفاً از اجرای صحیح سرور پشتیبان و پراکسی اطمینان حاصل کنید.';
      } else {
        errorMsg = `خطای پیش‌بینی نشده در درخواست: ${err.message}`;
      }
      setError(errorMsg);
      setStatusMessage('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAudioPlaybackError = (errorMessage) => {
    setPlaybackError(errorMessage);
    // Optionally clear other messages or keep them for context
    // setError('');
    setStatusMessage(''); // Clear general status messages when a playback error occurs
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 3, fontWeight: 'medium' }}>
          مبدل متن به گفتار فارسی (React & FastAPI)
        </Typography>

        <Grid container spacing={3}>
          {/* Input and Speaker Selection */}
          <Grid item xs={12} md={7}>
            <TextInput text={text} onTextChange={handleTextChange} disabled={isLoading} />
          </Grid>
          <Grid item xs={12} md={5}>
            <SpeakerSelector speakers={speakers} selectedSpeaker={selectedSpeaker} onSpeakerChange={handleSpeakerChange} disabled={isLoading || Object.keys(speakers).length === 0} />
          </Grid>
          {/* Convert Button */}
          <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <ConvertButton onConvert={handleConvert} isLoading={isLoading} />
          </Grid>

          {/* Loading, Status, and Error Messages */}
          {isLoading && (
            <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'center', my: 2, alignItems: 'center', flexDirection: 'column' }}>
              <CircularProgress sx={{mb: 1}} />
              {statusMessage && <Typography variant="body2">{statusMessage}</Typography>}
            </Grid>
          )}
          {error && !isLoading && ( // Show general/API errors only if not loading
            <Grid item xs={12}>
              <Alert severity="error" sx={{ my: 2 }} onClose={() => setError('')}>{error}</Alert>
            </Grid>
          )}
          {playbackError && !isLoading && ( // Show specific audio playback errors only if not loading
            <Grid item xs={12}>
              <Alert severity="warning" sx={{ my: 2 }} onClose={() => setPlaybackError('')}>{playbackError}</Alert>
            </Grid>
          )}
          {statusMessage && !isLoading && !error && !playbackError && ( // Info/success messages
            <Grid item xs={12}>
              <Alert severity="info" sx={{ my: 2 }} onClose={() => setStatusMessage('')}>{statusMessage}</Alert>
            </Grid>
          )}

          {/* Audio Player Area */}
          {audioUrls.length > 0 && !isLoading && (
            <Grid item xs={12} sx={{ mt: 3 }}>
              <Typography variant="h6" component="h2" gutterBottom>
                فایل‌های صوتی تولید شده:
              </Typography>
              <AudioPlayerWrapper audioUrls={audioUrls} onPlaybackError={handleAudioPlaybackError} />
            </Grid>
          )}
        </Grid>
      </Paper>
    </Container>
  );
}

export default App;
