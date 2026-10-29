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

  // Legal Rights Specific States
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [legalQueryText, setLegalQueryText] = useState('');
  const [legalAnswerText, setLegalAnswerText] = useState('');

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

  // Handles mic release on Legal Rights mode specifically
  const handleLegalMicRelease = () => {
    if (isRecording) {
      setIsRecording(false);
      setCurrentScreen('LEGAL_PROCESSING');

      // Sample placeholders for prompt & response
      setLegalQueryText("What are my rights if law enforcement stops me on the street or asks for identification?");
      setLegalAnswerText("You have the right to remain silent. You do not have to answer questions about where you were born, whether you are a U.S. citizen, or how you entered the country. You may ask 'Am I free to go?' If yes, you may calmly walk away.");

      // Simulated AI processing time
      setTimeout(() => {
        setCurrentScreen('LEGAL_RESPONSE');
      }, 2000);
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
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#78716c' }}>SELECT</div>
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
              <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#78716c' }}>SELECT</div>
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
                fontSize: '0.9rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 0px #292524',
                marginTop: '16px'
              }}
            >
              ⇄
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
  // SCREEN 3: PROCESSING SCREEN (TRANSLATION)
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
            <span>Volume:</span>
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

        {/* --- POPUP TOUCH VOLUME PANEL FOR SCREEN --- */}
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

            <div style={{ fontSize: '1rem', fontWeight: '800', minWidth: '48px', textAlign: 'center' }}>
              {isMuted ? '0%' : `${volume}%`}
            </div>

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
                <div style={{
                  fontSize: '0.7rem',
                  fontWeight: '800',
                  color: '#78716c',
                  marginBottom: '2px',
                  padding: '0 4px'
                }}>
                  {item.speakerLabel}
                </div>

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
              boxShadow: '0 3px 0px #292524'
            }}
          >
            Replay
          </button>

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
            Take Turn
          </button>

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
            Speak Again
          </button>
        </div>

      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 5: LEGAL RIGHTS MODE (MAIN RECORDING & DISCLAIMER)
  // -------------------------------------------------------------
  if (currentScreen === 'LEGAL_RIGHTS') {
    return (
      <div style={containerStyle}>
        {renderBackButton('START')}

        <div style={contentStyle}>
          <header style={{ textAlign: 'center', marginTop: '20px' }}>
            <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#1c1917', margin: '0 0 2px 0' }}>
              Legal Rights Mode
            </h1>
            <p style={{ color: '#57534e', fontSize: '0.9rem', margin: 0, fontWeight: '500' }}>
              Ask legal questions in {language}
            </p>
          </header>

          {/* Disclaimer Button Trigger */}
          <button
            onClick={() => setShowDisclaimer(true)}
            style={{
              width: '100%',
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '3px solid #292524',
              borderRadius: '14px',
              padding: '12px 16px',
              fontSize: '1rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 4px 0px #292524',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            Disclaimer (Read First)
          </button>

          {/* Main Hold-To-Record Audio Button */}
          <div style={{ marginTop: '8px', textAlign: 'center' }}>
            <button
              onMouseDown={() => setIsRecording(true)}
              onMouseUp={handleLegalMicRelease}
              onTouchStart={() => setIsRecording(true)}
              onTouchEnd={handleLegalMicRelease}
              style={{
                width: '100%',
                minHeight: '190px',
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
              <div style={{ fontSize: '1.4rem', fontWeight: '800', textTransform: 'uppercase' }}>
                {isRecording ? 'Listening...' : 'Hold to Ask Question'}
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: '600', opacity: 0.8 }}>
                {isRecording ? 'Release to process question' : 'Press and hold down to record your voice'}
              </div>
            </button>
          </div>
        </div>

        {/* --- DISCLAIMER OVERLAY MODAL --- */}
        {showDisclaimer && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            zIndex: 100
          }}>
            <div style={{
              backgroundColor: '#ffffff',
              border: '4px solid #292524',
              borderRadius: '20px',
              padding: '20px',
              maxWidth: '520px',
              width: '100%',
              boxShadow: '0 8px 0px #292524',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '1.4rem', fontWeight: '900', color: '#1c1917', margin: 0 }}>
                  LEGAL DISCLAIMER
                </h3>
                <button
                  onClick={() => setShowDisclaimer(false)}
                  style={{
                    backgroundColor: '#fffbeb',
                    border: '2px solid #292524',
                    borderRadius: '50%',
                    width: '36px',
                    height: '36px',
                    fontWeight: '900',
                    cursor: 'pointer'
                  }}
                >
                  X
                </button>
              </div>

              {/* Placeholder text area for user customization */}
              <div style={{
                maxHeight: '220px',
                overflowY: 'auto',
                backgroundColor: '#fffbeb',
                border: '2px solid #292524',
                borderRadius: '12px',
                padding: '14px',
                fontSize: '0.9rem',
                color: '#292524',
                lineHeight: '1.5',
                fontWeight: '500'
              }}>
                <div>
                <strong>[ DISCLAIMER ]</strong>
                <br /><br />
                <strong>Informational Purposes Only:</strong> The material provided—including Federal legal facts—is for general educational purposes only and does not constitute legal advice. No attorney-client relationship is created in any way by the use of our product, and we make no guarantees regarding its accuracy/completeness.
                <br /><br />
                <strong>Limitation of Liability:</strong> Use of this product is entirely at your own risk. You are solely responsible for all actions and decisions you take with the information provided, and we assume no legal or financial liability for any resulting consequences or losses.
                <br /><br />
                <strong>No Confidentiality:</strong> Unsolicited communications are not confidential or protected by attorney-client privilege. Consult a licensed attorney in your jurisdiction for situation-specific professional legal advice.

              </div>
              </div>

              <button
                onClick={() => setShowDisclaimer(false)}
                style={{
                  width: '100%',
                  backgroundColor: '#ffffff',
                  color: '#1c1917',
                  border: '3px solid #292524',
                  borderRadius: '12px',
                  padding: '12px',
                  fontSize: '1rem',
                  fontWeight: '800',
                  cursor: 'pointer',
                  boxShadow: '0 3px 0px #292524'
                }}
              >
                I Understand
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 6: LEGAL RIGHTS PROCESSING SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'LEGAL_PROCESSING') {
    return (
      <div style={containerStyle}>
        {renderBackButton('LEGAL_RIGHTS')}

        <div style={{ textAlign: 'center', maxWidth: '400px', padding: '0 16px' }}>
          <h1 style={{ 
            fontSize: '2.5rem', 
            fontWeight: '900', 
            color: '#1c1917', 
            margin: '0 0 12px 0',
            letterSpacing: '0.05em'
          }}>
            ANALYZING...
          </h1>

          <p style={{ 
            fontSize: '1rem', 
            fontWeight: '600', 
            color: '#57534e', 
            margin: 0 
          }}>
            Processing your question and retrieving legal guidance
          </p>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 7: LEGAL RIGHTS AI RESPONSE SCREEN
  // -------------------------------------------------------------
  if (currentScreen === 'LEGAL_RESPONSE') {
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
        {/* --- TOP BAR --- */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          backgroundColor: '#fffbeb',
          borderBottom: '2px solid #e7e5e4'
        }}>
          <button
            onClick={() => setCurrentScreen('LEGAL_RIGHTS')}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '8px 14px',
              fontSize: '0.9rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 2px 0px #292524'
            }}
          >
            Back
          </button>

          <button
            onClick={handleDone}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '8px 16px',
              fontSize: '0.9rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 2px 0px #292524'
            }}
          >
            Done
          </button>
        </div>

        {/* --- CONTENT AREA --- */}
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
          {/* User's Question */}
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#78716c', marginBottom: '4px', textTransform: 'uppercase' }}>
              Your Question
            </div>
            <div style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '3px solid #292524',
              borderRadius: '16px',
              padding: '14px',
              fontSize: '1rem',
              fontWeight: '600',
              boxShadow: '0 3px 0px #292524'
            }}>
              "{legalQueryText}"
            </div>
          </div>

          {/* Clickable AI Legal Answer with Source Indicator */}
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#78716c', marginBottom: '4px', textTransform: 'uppercase' }}>
              Legal Information Response (Tap to view source document)
            </div>
            <button
              onClick={() => setCurrentScreen('LEGAL_SOURCE_VIEWER')}
              style={{
                width: '100%',
                backgroundColor: '#fef08a',
                color: '#1c1917',
                border: '3px solid #292524',
                borderRadius: '16px',
                padding: '16px',
                fontSize: '1.05rem',
                fontWeight: '700',
                lineHeight: '1.5',
                boxShadow: '0 4px 0px #292524',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}
            >
              <div>
                {legalAnswerText}
              </div>

              {/* Source Document Indicator Badge */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '2px dashed #292524',
                paddingTop: '10px',
                fontSize: '0.85rem',
                fontWeight: '900'
              }}>
                <span>📄 Source: NILC Rights Guide (PDF)</span>
                <span style={{
                  backgroundColor: '#ffffff',
                  border: '2px solid #292524',
                  padding: '4px 10px',
                  borderRadius: '8px',
                  boxShadow: '0 2px 0px #292524'
                }}>
                  View File &rarr;
                </span>
              </div>
            </button>
          </div>
        </div>

        {/* --- BOTTOM CONTROLS --- */}
        <div style={{
          padding: '12px 16px 16px 16px',
          backgroundColor: '#fffbeb',
          borderTop: '2px solid #e7e5e4',
          display: 'flex',
          gap: '10px',
          maxWidth: '680px',
          width: '100%',
          margin: '0 auto',
          boxSizing: 'border-box'
        }}>
          <button
            onClick={() => alert('Reading legal response aloud...')}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '12px',
              fontSize: '0.9rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 3px 0px #292524'
            }}
          >
            Read Aloud
          </button>

          <button
            onClick={() => setCurrentScreen('LEGAL_RIGHTS')}
            style={{
              flex: 1,
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '3px solid #292524',
              borderRadius: '12px',
              padding: '12px',
              fontSize: '0.95rem',
              fontWeight: '900',
              cursor: 'pointer',
              boxShadow: '0 3px 0px #292524',
              textAlign: 'center'
            }}
          >
            Ask Another Question
          </button>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------
  // SCREEN 8: LEGAL SOURCE DOCUMENT VIEWER (PLACEHOLDER)
  // -------------------------------------------------------------
  if (currentScreen === 'LEGAL_SOURCE_VIEWER') {
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
        {/* --- TOP BAR --- */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          backgroundColor: '#fffbeb',
          borderBottom: '2px solid #e7e5e4'
        }}>
          <button
            onClick={() => setCurrentScreen('LEGAL_RESPONSE')}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '8px 14px',
              fontSize: '0.9rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 2px 0px #292524'
            }}
          >
            Back
          </button>

          <button
            onClick={handleDone}
            style={{
              backgroundColor: '#ffffff',
              color: '#1c1917',
              border: '2px solid #292524',
              borderRadius: '12px',
              padding: '8px 16px',
              fontSize: '0.9rem',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 2px 0px #292524'
            }}
          >
            Done
          </button>
        </div>

        {/* --- CONTENT AREA --- */}
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
          <header style={{ textAlign: 'center', marginTop: '10px' }}>
            <h1 style={{ fontSize: '1.6rem', fontWeight: '800', color: '#1c1917', margin: '0 0 2px 0' }}>
              Source Document Viewer
            </h1>
            <p style={{ color: '#57534e', fontSize: '0.85rem', margin: 0, fontWeight: '500' }}>
              Retrieved from your local legal knowledge base
            </p>
          </header>

          <div style={{
            backgroundColor: '#ffffff',
            border: '3px solid #292524',
            borderRadius: '16px',
            padding: '20px',
            boxShadow: '0 5px 0px #292524',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px'
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#78716c', textTransform: 'uppercase' }}>
              File Reference
            </div>
            
            <div style={{ fontSize: '1rem', fontWeight: '900', color: '#1c1917', wordBreak: 'break-all' }}>
              📂 /data/legal_sources/es/nilc_confronted_by_ice_es.pdf
            </div>

            <p style={{ fontSize: '0.9rem', color: '#44403c', lineHeight: '1.5', margin: 0 }}>
              Placeholder screen for source document. Later integrate a PDF reader view or display chunk text.
            </p>

            <div style={{
              backgroundColor: '#fffbeb',
              border: '2px solid #292524',
              borderRadius: '10px',
              padding: '12px',
              fontSize: '0.85rem',
              fontWeight: '600',
              fontStyle: 'italic',
              color: '#292524'
            }}>
              "{legalAnswerText}"
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}