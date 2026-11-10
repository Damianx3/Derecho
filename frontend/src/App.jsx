import React, { useState, useEffect, useRef } from 'react';
import { UI_LOCALES, translate, translateError } from './i18n.mjs';

export default function App() {
  const [uiLanguage, setUiLanguage] = useState('English');
  const t = (key, values) => translate(uiLanguage, key, values);
  useEffect(() => {
    document.documentElement.lang = UI_LOCALES.find(item => item.name === uiLanguage).code;
  }, [uiLanguage]);
  const [language, setLanguage] = useState('English');
  const [targetLanguage, setTargetLanguage] = useState('Spanish');
  const [currentScreen, setCurrentScreen] = useState('START');
  const [isRecording, setIsRecording] = useState(false);
  const [activeSpeaker, setActiveSpeaker] = useState(1);
  const [partialTranscript, setPartialTranscript] = useState('');
  const [previewWarning, setPreviewWarning] = useState('');
  const [languages, setLanguages] = useState([]);
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const [audioBusy, setAudioBusy] = useState(false);
  const [hasAudio, setHasAudio] = useState(false);
  const recording = useRef(false);
  const starting = useRef(null);
  const ending = useRef(false);
  const volumeQueue = useRef(Promise.resolve());

  async function api(path, body) {
    let response;
    try {
      response = await fetch(`http://127.0.0.1:8000/api/${path}`, body === undefined ? {} : {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
    } catch {
      throw new Error('Cannot reach Derecho. Check the backend connection and try again.');
    }
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || `Request failed (${response.status})`);
    return result;
  }

  useEffect(() => {
    let active = true;
    Promise.all([api('languages'), api('audio')]).then(([items, audio]) => {
      if (!active) return;
      setLanguages(items); setVolume(audio.volume); setIsMuted(audio.muted);
      setHasAudio(audio.has_audio); setReady(true);
    }).catch(() => active && setError('Cannot connect to Derecho. Check that the backend is running, then reload.'));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!isRecording) return;
    let active = true;
    let timer;
    const poll = async () => {
      try {
        const status = await api('record/status');
        if (active) {
          setPartialTranscript(status.partial_transcript || '');
          setPreviewWarning(status.preview_warning || '');
        }
      } catch { /* The recording endpoints surface connection errors. */ }
      if (active) timer = setTimeout(poll, 1000);
    };
    timer = setTimeout(poll, 1000);
    return () => { active = false; clearTimeout(timer); };
  }, [isRecording]);

  const languageOptions = (other) => languages.map(item => (
    <option key={item.name} value={item.name} disabled={item.enabled === false || item.name === other}>{t(`language${item.name}`)}{item.testing ? ` (${t('testing')})` : ''}</option>
  ));

  const feedback = error && <div className="error-banner" role="alert">{translateError(uiLanguage, error)}</div>;


  // Audio & Volume Modal States
  const [volume, setVolume] = useState(80); // 0 to 100
  const [isMuted, setIsMuted] = useState(false);
  const [showVolumeModal, setShowVolumeModal] = useState(false);

  // Chat History
  const [messages, setMessages] = useState([]);

  // Common Layout Styles
  const containerStyle = {
    backgroundColor: '#fffbeb', // Eggshell yellow
    minHeight: '100vh',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '16px',
    boxSizing: 'border-box',
    position: 'relative'
  };

  const contentStyle = {
    width: '100%',
    maxWidth: '680px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    marginTop: '-10px'
  };

  const buttonStyle = {
    flex: '1',
    minHeight: '140px',
    backgroundColor: '#ffffff',
    color: '#1c1917',
    border: '3px solid #292524',
    borderRadius: '16px',
    padding: '16px',
    textAlign: 'left',
    cursor: 'pointer',
    boxShadow: '0 5px 0px #292524',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    boxSizing: 'border-box'
  };

  // Reusable Thick Back Button Component
  const renderBackButton = (targetScreen) => (
    <button
      disabled={isRecording}
      onClick={() => setCurrentScreen(targetScreen)}
      style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        backgroundColor: '#ffffff',
        color: '#1c1917',
        border: '3px solid #292524',
        borderRadius: '12px',
        padding: '8px 16px',
        fontSize: '1.1rem',
        fontWeight: '800',
        cursor: 'pointer',
        boxShadow: '0 4px 0px #292524',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        zIndex: 10
      }}
    >
      <span style={{ fontSize: '1.3rem', fontWeight: '900', lineHeight: '1' }}>
        {'\u2B05'}
      </span>
      {t('back')}
    </button>
  );

  const handleSwapLanguages = () => {
    const temp = language;
    setLanguage(targetLanguage);
    setTargetLanguage(temp);
  };

  const handleMicPress = () => {
    if (!ready || recording.current || ending.current) return;
    recording.current = true;
    setIsRecording(true);
    setError('');
    setPartialTranscript(''); setPreviewWarning('');
    const source = activeSpeaker === 1 ? language : targetLanguage;
    starting.current = api('record/start', {
      source_language_code: languages.find(item => item.name === source).code
    }).then(() => {
      if (recording.current) setIsRecording(true);
      return true;
    }).catch(err => {
      recording.current = false; setIsRecording(false); setError(err.message);
      return false;
    });
  };

  const handleMicRelease = async () => {
    if (!recording.current || ending.current) return;
    ending.current = true;
    recording.current = false;
    setIsRecording(false);
    setCurrentScreen('PROCESSING');
    const speaker = activeSpeaker;
    const source = speaker === 1 ? language : targetLanguage;
    const target = speaker === 1 ? targetLanguage : language;
    try {
      if (!await starting.current) { setCurrentScreen('TRANSLATION'); return; }
      const result = await api('record/stop', {
        source_language_code: languages.find(item => item.name === source).code,
        source_language_name: source, target_language_name: target
      });
      setMessages(prev => [...prev, {id: Date.now(), speaker,
        sourceLanguage: source, originalText: result.transcript,
        translatedText: result.translation}]);
      setHasAudio(result.has_audio); setCurrentScreen('RESULTS');
    } catch (err) { setError(err.message); setCurrentScreen('TRANSLATION'); }
    finally { ending.current = false; }
  };

  const handleReplay = async () => {
    setAudioBusy(true); setError('');
    try { await volumeQueue.current; await api('audio/replay', {}); }
    catch (err) { setError(err.message); }
    finally { setAudioBusy(false); }
  };

  const handleTakeTurn = () => {
    setActiveSpeaker(activeSpeaker === 1 ? 2 : 1);
    setCurrentScreen('TRANSLATION');
  };

  const handleSpeakAgain = () => {
    setCurrentScreen('TRANSLATION');
  };

  const handleDone = () => {
    setError('');
    setMessages([]);
    setActiveSpeaker(1);
    setShowVolumeModal(false);
    setCurrentScreen('START');
  };

  const updateVolume = (nextVolume, nextMuted) => {
    setVolume(nextVolume); setIsMuted(nextMuted);
    volumeQueue.current = volumeQueue.current.then(async () => {
      try { await api('audio/volume', {volume: nextVolume, muted: nextMuted}); }
      catch (err) {
        setError(`Volume was not applied: ${err.message}`);
        try {
          const audio = await api('audio'); setVolume(audio.volume); setIsMuted(audio.muted);
        } catch { /* Keep the connection error visible. */ }
      }
    });
  };
  const adjustVolume = delta => updateVolume(Math.min(100, Math.max(0, volume + delta)), false);

  // -------------------------------------------------------------
  // SCREEN 1: START SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'START') {
    return (
      <div style={containerStyle}>
        <div style={contentStyle}>
          {feedback}

          <header style={{ textAlign: 'center' }}>
            <h1 style={{ fontSize: '2.2rem', fontWeight: '800', color: '#1c1917', margin: '0 0 4px 0', letterSpacing: '-0.025em' }}>
              [ Derecho ]
            </h1>
            <p style={{ color: '#57534e', fontSize: '0.95rem', margin: 0, fontWeight: '500' }}>
              {t('chooseMode')}
            </p>
          </header>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxWidth: '380px', margin: '0 auto', width: '100%' }}>
            <label htmlFor="language-select" style={{ fontSize: '0.9rem', fontWeight: '700', color: '#292524', textAlign: 'center' }}>
              {t('interfaceLanguage')}
            </label>
            <select
              id="language-select"
              value={uiLanguage}
              disabled={isRecording}
              onChange={e => setUiLanguage(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: '#ffffff',
                color: '#1c1917',
                border: '2px solid #292524',
                borderRadius: '12px',
                padding: '10px 14px',
                fontSize: '1rem',
                fontWeight: '600',
                boxSizing: 'border-box',
                outline: 'none',
                textAlign: 'center'
              }}
            >
              {UI_LOCALES.map(item => <option key={item.name} value={item.name}>{item.label}</option>)}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'row', gap: '16px', marginTop: '12px', width: '100%' }}>
            <button onClick={() => setCurrentScreen('TRANSLATION')} style={buttonStyle}>
              <div>
                <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#1c1917', marginBottom: '6px' }}>
                  {t('translationMode')}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#57534e', fontWeight: '500', lineHeight: '1.3' }}>
                  {t('translationDescription')}
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#78716c' }}>{t('select')} ➔</div>
            </button>

            <button onClick={() => setCurrentScreen('LEGAL_RIGHTS')} style={buttonStyle}>
              <div>
                <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#1c1917', marginBottom: '6px' }}>
                  {t('rightsMode')}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#57534e', fontWeight: '500', lineHeight: '1.3' }}>
                  {t('rightsDescription')}
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#78716c' }}>{t('select')} ➔</div>
            </button>
          </div>

        </div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 2: TRANSLATION MODE SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'TRANSLATION') {
    return (
      <div style={containerStyle}>
        {renderBackButton('START')}

        <div style={contentStyle}>

          <header style={{ textAlign: 'center', marginTop: '20px' }}>
            <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#1c1917', margin: '0 0 2px 0' }}>
              {t('translationMode')}
            </h1>
            <p style={{ color: '#57534e', fontSize: '0.9rem', margin: 0, fontWeight: '500' }}>
              {t('activeSpeaker')} <strong>{t('speaker', { n: activeSpeaker })}</strong>
            </p>
          </header>
          {feedback}

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '10px',
            backgroundColor: '#ffffff',
            padding: '12px',
            borderRadius: '16px',
            border: '3px solid #292524',
            boxShadow: '0 4px 0px #292524'
          }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <label htmlFor="speaker-one" style={{ display: 'block', fontSize: '0.7rem', fontWeight: '800', color: '#78716c', marginBottom: '4px', textTransform: 'uppercase' }}>
                {t('speaker', { n: 1 })}
              </label>
              <select
                id="speaker-one"
                value={language}
                disabled={!ready || isRecording}
              onChange={(e) => { if (e.target.value === targetLanguage) setTargetLanguage(language); setLanguage(e.target.value); }}
                style={{
                  width: '100%',
                  backgroundColor: '#fffbeb',
                  color: '#1c1917',
                  border: '2px solid #292524',
                  borderRadius: '8px',
                  padding: '8px',
                  fontSize: '0.95rem',
                  fontWeight: '700',
                  outline: 'none'
                }}
              >
                {languageOptions(targetLanguage)}
                </select>
            </div>

            <button
              disabled={!ready || isRecording}
              onClick={handleSwapLanguages}
              title={t('swap')}
              aria-label={t('swap')}
              style={{
                backgroundColor: '#ffffff',
                border: '2px solid #292524',
                borderRadius: '50%',
                width: '48px',
                height: '48px',
                flexShrink: 0,
                fontSize: '1.1rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                touchAction: 'none',
                userSelect: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 0px #292524',
                marginTop: '16px'
              }}
            >
              ⇆
            </button>

            <div style={{ flex: 1, minWidth: 0 }}>
              <label htmlFor="speaker-two" style={{ display: 'block', fontSize: '0.7rem', fontWeight: '800', color: '#78716c', marginBottom: '4px', textTransform: 'uppercase' }}>
                {t('speaker', { n: 2 })}
              </label>
              <select
                id="speaker-two"
                value={targetLanguage}
                disabled={!ready || isRecording}
                onChange={(e) => setTargetLanguage(e.target.value)}
                style={{
                  width: '100%',
                  backgroundColor: '#fffbeb',
                  color: '#1c1917',
                  border: '2px solid #292524',
                  borderRadius: '8px',
                  padding: '8px',
                  fontSize: '0.95rem',
                  fontWeight: '700',
                  outline: 'none'
                }}
              >
                {languageOptions(language)}
                </select>
            </div>
          </div>

          {(languages.find(item => item.name === language)?.testing ||
            languages.find(item => item.name === targetLanguage)?.testing) && (
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#57534e', textAlign: 'center' }}>
              {t('testingNote')}
            </p>
          )}

          <div style={{ marginTop: '12px', textAlign: 'center' }}>

            <button
              disabled={!ready}
              onPointerDown={e => {
                if (!e.isPrimary || e.button !== 0) return;
                e.preventDefault(); e.currentTarget.setPointerCapture(e.pointerId); handleMicPress();
              }}
              onPointerUp={handleMicRelease}
              onPointerCancel={handleMicRelease}
              onLostPointerCapture={handleMicRelease}
              onKeyDown={e => {
                if ([' ', 'Enter'].includes(e.key)) { e.preventDefault(); if (!e.repeat) handleMicPress(); }
              }}
              onKeyUp={e => {
                if ([' ', 'Enter'].includes(e.key)) { e.preventDefault(); handleMicRelease(); }
              }}
              onBlur={handleMicRelease}
              onContextMenu={(e) => e.preventDefault()}
              style={{
                width: '100%',
                touchAction: 'none',
                userSelect: 'none',
                minHeight: '150px',
                backgroundColor: isRecording ? '#ef4444' : '#ffffff',
                color: isRecording ? '#ffffff' : '#1c1917',
                border: '4px solid #292524',
                borderRadius: '24px',
                padding: '20px',
                cursor: 'pointer',
                boxShadow: isRecording ? '0 0px 0px #292524' : '0 6px 0px #292524',
                transform: isRecording ? 'translateY(6px)' : 'none',
                transition: 'all 0.1s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <div style={{ fontSize: '2.6rem' }}>🎙️</div>
              <div style={{ fontSize: '1.3rem', fontWeight: '800', textTransform: 'uppercase' }}>
                {isRecording ? t('listening') : t('holdToSpeak')}
              </div>
              <div dir="auto" style={{ fontSize: '0.8rem', fontWeight: '600', opacity: 0.8, maxHeight: '40px', overflow: 'hidden' }}>
                {isRecording ? (previewWarning ? t('previewUnavailable') : partialTranscript ? t('preview', { text: partialTranscript }) : t('release')) : t('holdInstruction')}
              </div>
            </button>
          </div>

        </div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 3: PROCESSING SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'PROCESSING') {
    return (
      <div style={containerStyle}>

        <div role="status" style={{ textAlign: 'center', maxWidth: '400px', padding: '0 16px' }}>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '900',
            color: '#1c1917',
            margin: '0 0 12px 0',
            letterSpacing: '0.05em'
          }}>
            {t('processing')}
          </h1>

          <p style={{
            fontSize: '1rem',
            fontWeight: '600',
            color: '#57534e',
            margin: 0
          }}>
            {t('processingDescription')}
          </p>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 4: RESULTS / TEXT CONVERSATION SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'RESULTS') {
    return (
      <div style={{
        backgroundColor: '#fffbeb',
        height: '100dvh',
        overflow: 'hidden',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        boxSizing: 'border-box',
        position: 'relative'
      }}>

        {/* --- TOP CONTROL BAR --- */}
        <div style={{
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          gap: '10px',
          padding: '12px 16px',
          backgroundColor: '#fffbeb',
          borderBottom: '2px solid #e7e5e4'
        }}>
          {/* Touch-optimized Volume Badge */}
          <button
            aria-label={t('volumeControls')}
            aria-expanded={showVolumeModal}
            onClick={() => setShowVolumeModal(!showVolumeModal)}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '8px 14px',
              fontSize: '0.95rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 2px 0px #292524',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span>{isMuted || volume === 0 ? '🔇' : volume < 50 ? '🔉' : '🔊'}</span>
            <span>{isMuted ? t('muted') : `${volume}%`}</span>
          </button>

          {/* Top Right "Done" Button */}
          <button
            disabled={audioBusy}
            onClick={handleDone}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '8px 16px',
              fontSize: '0.95rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 2px 0px #292524'
            }}
          >
            {t('done')}
          </button>
        </div>

        {/* --- POPUP TOUCH VOLUME PANEL FOR 4.3" SCREEN --- */}
        {showVolumeModal && (
          <div style={{
            position: 'absolute',
            top: '60px',
            right: '16px',
            backgroundColor: '#ffffff',
            border: '3px solid #292524',
            borderRadius: '16px',
            padding: '12px',
            boxShadow: '0 6px 0px #292524',
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            {/* Big Minus Button */}
            <button
              aria-label={t('volumeDown')}
              onClick={() => adjustVolume(-10)}
              style={{
                width: '44px',
                height: '44px',
                fontSize: '1.4rem',
                fontWeight: '900',
                backgroundColor: '#fffbeb',
                border: '2px solid #292524',
                borderRadius: '10px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              -
            </button>

            <label className="volume-slider">
              <span>{t('speechVolume')}</span>
              <input aria-label={t('speechVolume')} type="range" min="0" max="100" step="10"
                value={volume} onChange={e => updateVolume(Number(e.target.value), false)} />
            </label>
            {/* Current Level Display */}
            <div style={{ fontSize: '1rem', fontWeight: '800', minWidth: '48px', textAlign: 'center' }}>
              {isMuted ? '0%' : `${volume}%`}
            </div>

            {/* Big Plus Button */}
            <button
              aria-label={t('volumeUp')}
              onClick={() => adjustVolume(10)}
              style={{
                width: '44px',
                height: '44px',
                fontSize: '1.4rem',
                fontWeight: '900',
                backgroundColor: '#fffbeb',
                border: '2px solid #292524',
                borderRadius: '10px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              +
            </button>

            {/* Big Mute Toggle */}
            <button
              aria-pressed={isMuted}
              onClick={() => updateVolume(volume, !isMuted)}
              style={{
                padding: '8px 12px',
                fontSize: '0.85rem',
                fontWeight: '800',
                backgroundColor: isMuted ? '#ef4444' : '#fffbeb',
                color: isMuted ? '#ffffff' : '#1c1917',
                border: '2px solid #292524',
                borderRadius: '10px',
                cursor: 'pointer'
              }}
            >
              {isMuted ? t('unmute') : t('mute')}
            </button>
          </div>
        )}

        {feedback}
        {/* --- SCROLLABLE CHAT CONVERSATION AREA --- */}
        <div style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          padding: '16px',
          maxWidth: '680px',
          width: '100%',
          margin: '0 auto',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          {messages.map((item) => {
            const isSpeakerOne = item.speaker === 1;

            return (
              <div
                key={item.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isSpeakerOne ? 'flex-start' : 'flex-end',
                  width: '100%'
                }}
              >
                {/* Speaker Label */}
                <div style={{
                  fontSize: '0.7rem',
                  fontWeight: '800',
                  color: '#78716c',
                  marginBottom: '2px',
                  padding: '0 4px'
                }}>
                  {t('speaker', { n: item.speaker })} ({t(`language${item.sourceLanguage}`)})
                </div>

                {/* Original Speech Bubble */}
                <div style={{
                  maxWidth: '85%',
                  backgroundColor: isSpeakerOne ? '#ffffff' : '#292524',
                  color: isSpeakerOne ? '#1c1917' : '#ffffff',
                  border: '3px solid #292524',
                  borderRadius: isSpeakerOne ? '14px 14px 14px 4px' : '14px 14px 4px 14px',
                  padding: '10px 14px',
                  fontSize: '0.95rem',
                  fontWeight: '600',
                  boxShadow: '0 3px 0px #292524',
                  marginBottom: '6px'
                }}>
                  {item.originalText}
                </div>

                {/* Translated Speech Bubble */}
                <div style={{
                  maxWidth: '85%',
                  backgroundColor: isSpeakerOne ? '#fef08a' : '#3b82f6',
                  color: isSpeakerOne ? '#1c1917' : '#ffffff',
                  border: '3px solid #292524',
                  borderRadius: isSpeakerOne ? '14px 14px 14px 4px' : '14px 14px 4px 14px',
                  padding: '10px 14px',
                  fontSize: '0.95rem',
                  fontWeight: '700',
                  boxShadow: '0 3px 0px #292524'
                }}>
                  <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', opacity: 0.8, marginBottom: '2px' }}>
                    {t('translation')}
                  </div>
                  {item.translatedText}
                </div>
              </div>
            );
          })}
        </div>

        {/* --- BOTTOM ACTION CONTROLS (3 BUTTONS) --- */}
        <div style={{
          padding: '12px 16px 16px 16px',
          backgroundColor: '#fffbeb',
          borderTop: '2px solid #e7e5e4',
          display: 'flex',
          justifyContent: 'space-between',
          gap: '8px',
          maxWidth: '680px',
          width: '100%',
          margin: '0 auto',
          boxSizing: 'border-box'
        }}>
          {/* Bottom Left: Replay AI Voice */}
          <button
            onClick={handleReplay}
            disabled={!hasAudio || audioBusy}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '10px 12px',
              fontSize: '0.85rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 3px 0px #292524',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            {audioBusy ? t('playing') : t('replay')}
          </button>

          {/* Bottom Center: Take Turn */}
          <button
            disabled={audioBusy}
            onClick={handleTakeTurn}
            style={{
              flex: 1,
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '3px solid #292524',
              borderRadius: '12px',
              padding: '10px 12px',
              fontSize: '0.95rem',
              fontWeight: '900',
              cursor: 'pointer',
              boxShadow: '0 3px 0px #292524',
              textAlign: 'center'
            }}
          >
            {t('takeTurn')} ⇆
          </button>

          {/* Bottom Right: Speak Again */}
          <button
            disabled={audioBusy}
            onClick={handleSpeakAgain}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '10px 12px',
              fontSize: '0.85rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 3px 0px #292524'
            }}
          >
            {t('speakAgain')} 🎙️
          </button>
        </div>

      </div>
    );
  }

  // Placeholder for Legal Rights Screen
  return (
    <div style={containerStyle}>
      {renderBackButton('START')}
      <h2>{t('rightsComingSoon')}</h2>
    </div>
  );
}