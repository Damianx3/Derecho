import React, { useState } from 'react';

export default function App() {
  const [language, setLanguage] = useState('English');
  const [targetLanguage, setTargetLanguage] = useState('Spanish');
  const [currentScreen, setCurrentScreen] = useState('START');
  const [isRecording, setIsRecording] = useState(false);
  const [activeSpeaker, setActiveSpeaker] = useState(1);

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
      Back
    </button>
  );

  const handleSwapLanguages = () => {
    const temp = language;
    setLanguage(targetLanguage);
    setTargetLanguage(temp);
  };

  // Simulate finishes speaking and adds messages to chat history
  const handleMicRelease = () => {
    if (isRecording) {
      setIsRecording(false);
      setCurrentScreen('PROCESSING');

      const isSpeakerOne = activeSpeaker === 1;
      const speakerLabel = isSpeakerOne ? `Speaker 1 (${language})` : `Speaker 2 (${targetLanguage})`;
      const sampleOriginal = isSpeakerOne ? "Hello, I need help with my document." : "Hola, puedo ayudarte con eso.";
      const sampleTranslated = isSpeakerOne ? "Hola, necesito ayuda con mi documento." : "Hello, I can help you with that.";

      const newBubbles = {
        id: Date.now(),
        speaker: activeSpeaker,
        speakerLabel: speakerLabel,
        originalText: sampleOriginal,
        translatedText: sampleTranslated
      };

      // Simulated AI processing time (1.8s)
      setTimeout(() => {
        setMessages((prev) => [...prev, newBubbles]);
        setCurrentScreen('RESULTS');
      }, 1800);
    }
  };

  const handleTakeTurn = () => {
    handleSwapLanguages();
    setActiveSpeaker(activeSpeaker === 1 ? 2 : 1);
    setCurrentScreen('TRANSLATION');
  };

  const handleSpeakAgain = () => {
    setCurrentScreen('TRANSLATION');
  };

  const handleDone = () => {
    setMessages([]);
    setActiveSpeaker(1);
    setShowVolumeModal(false);
    setCurrentScreen('START');
  };

  // Touch-friendly volume step control
  const adjustVolume = (delta) => {
    setVolume((prev) => Math.min(100, Math.max(0, prev + delta)));
    if (isMuted) setIsMuted(false);
  };

  // -------------------------------------------------------------
  // SCREEN 1: START SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'START') {
    return (
      <div style={containerStyle}>
        <div style={contentStyle}>
          
          <header style={{ textAlign: 'center' }}>
            <h1 style={{ fontSize: '2.2rem', fontWeight: '800', color: '#1c1917', margin: '0 0 4px 0', letterSpacing: '-0.025em' }}>
              [ Derecho ]
            </h1>
            <p style={{ color: '#57534e', fontSize: '0.95rem', margin: 0, fontWeight: '500' }}>
              Select your language & mode
            </p>
          </header>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxWidth: '380px', margin: '0 auto', width: '100%' }}>
            <label htmlFor="language-select" style={{ fontSize: '0.9rem', fontWeight: '700', color: '#292524', textAlign: 'center' }}>
              Interface Language
            </label>
            <select
              id="language-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
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
              <option value="English">English</option>
              <option value="Spanish">Español (Spanish)</option>
              <option value="French">Français (French)</option>
              <option value="Kinyarwanda">Kinyarwanda</option>
              <option value="Arabic">العربية (Arabic)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'row', gap: '16px', marginTop: '12px', width: '100%' }}>
            <button onClick={() => setCurrentScreen('TRANSLATION')} style={buttonStyle}>
              <div>
                <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#1c1917', marginBottom: '6px' }}>
                  Translation Mode
                </div>
                <div style={{ fontSize: '0.8rem', color: '#57534e', fontWeight: '500', lineHeight: '1.3' }}>
                  Two-way real-time speech translation
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#78716c' }}>SELECT ➔</div>
            </button>

            <button onClick={() => setCurrentScreen('LEGAL_RIGHTS')} style={buttonStyle}>
              <div>
                <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#1c1917', marginBottom: '6px' }}>
                  Legal Rights Mode
                </div>
                <div style={{ fontSize: '0.8rem', color: '#57534e', fontWeight: '500', lineHeight: '1.3' }}>
                  Inform or be informed regarding legal protections
                </div>
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#78716c' }}>SELECT ➔</div>
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
              Translation Mode
            </h1>
            <p style={{ color: '#57534e', fontSize: '0.9rem', margin: 0, fontWeight: '500' }}>
              Active Speaker: <strong>Speaker {activeSpeaker}</strong>
            </p>
          </header>

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
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: '800', color: '#78716c', marginBottom: '4px', textTransform: 'uppercase' }}>
                Speaker 1
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
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
                <option value="English">English</option>
                <option value="Spanish">Español</option>
                <option value="French">Français</option>
                <option value="Kinyarwanda">Kinyarwanda</option>
                <option value="Arabic">العربية</option>
              </select>
            </div>

            <button
              onClick={handleSwapLanguages}
              title="Swap Languages"
              style={{
                backgroundColor: '#ffffff',
                border: '2px solid #292524',
                borderRadius: '50%',
                width: '38px',
                height: '38px',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 0px #292524',
                marginTop: '16px'
              }}
            >
              ⇆
            </button>

            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: '800', color: '#78716c', marginBottom: '4px', textTransform: 'uppercase' }}>
                Speaker 2
              </label>
              <select
                value={targetLanguage}
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
                <option value="Spanish">Español</option>
                <option value="English">English</option>
                <option value="French">Français</option>
                <option value="Kinyarwanda">Kinyarwanda</option>
                <option value="Arabic">العربية</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: '12px', textAlign: 'center' }}>
            <button
              onMouseDown={() => setIsRecording(true)}
              onMouseUp={handleMicRelease}
              onTouchStart={() => setIsRecording(true)}
              onTouchEnd={handleMicRelease}
              style={{
                width: '100%',
                minHeight: '170px',
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
                {isRecording ? 'Listening...' : 'Hold to Speak'}
              </div>
              <div style={{ fontSize: '0.8rem', fontWeight: '600', opacity: 0.8 }}>
                {isRecording ? 'Release to translate' : 'Press and hold down to record audio'}
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
        {renderBackButton('TRANSLATION')}

        <div style={{ textAlign: 'center', maxWidth: '400px', padding: '0 16px' }}>
          <h1 style={{ 
            fontSize: '2.5rem', 
            fontWeight: '900', 
            color: '#1c1917', 
            margin: '0 0 12px 0',
            letterSpacing: '0.05em'
          }}>
            PROCESSING...
          </h1>

          <p style={{ 
            fontSize: '1rem', 
            fontWeight: '600', 
            color: '#57534e', 
            margin: 0 
          }}>
            Transcribing your speech and translating
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
        minHeight: '100vh',
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
            <span>{isMuted ? 'Muted' : `${volume}%`}</span>
          </button>

          {/* Top Right "Done" Button */}
          <button
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
            Done
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

            {/* Current Level Display */}
            <div style={{ fontSize: '1rem', fontWeight: '800', minWidth: '48px', textAlign: 'center' }}>
              {isMuted ? '0%' : `${volume}%`}
            </div>

            {/* Big Plus Button */}
            <button
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
              onClick={() => setIsMuted(!isMuted)}
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
              {isMuted ? 'Unmute' : 'Mute'}
            </button>
          </div>
        )}

        {/* --- SCROLLABLE CHAT CONVERSATION AREA --- */}
        <div style={{
          flex: 1,
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
                  {item.speakerLabel}
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
                    Translation
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
            onClick={() => alert(`Replaying AI voice at ${isMuted ? 0 : volume}% volume...`)}
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
            🔊 Replay
          </button>

          {/* Bottom Center: Take Turn */}
          <button
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
            Take Turn ⇆
          </button>

          {/* Bottom Right: Speak Again */}
          <button
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
            Speak Again 🎙️
          </button>
        </div>

      </div>
    );
  }

  // Placeholder for Legal Rights Screen
  return (
    <div style={containerStyle}>
      {renderBackButton('START')}
      <h2>Legal Rights Mode Screen Coming Soon!</h2>
    </div>
  );
}