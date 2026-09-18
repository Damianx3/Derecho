# DERECHO System Architecture

## Overview

DERECHO is a privacy-first offline voice assistant running on a Raspberry Pi 5.

The system contains two primary modes.

## Translator Mode

Audio Input
→ Whisper using whisper.cpp
→ Language Detection
→ Machine Translation
→ Text Display
→ Text-to-Speech
→ Audio Output

## Know Your Rights Mode

Audio Input
→ Whisper using whisper.cpp
→ Hybrid Retrieval
→ Relevant Trusted Sources
→ Local Language Model
→ Grounded Response
→ Citation Verification
→ Text-to-Speech
→ Audio Output

## Main Components

### ASR
Converts spoken audio into text using Whisper through the whisper.cpp implementation.

### Translation
Translates recognized speech between supported languages.

### Retrieval
Searches trusted immigration-rights material using keyword and semantic retrieval.

### Legal AI
Uses retrieved evidence to generate educational, source-grounded responses.

### TTS
Converts generated or translated text into speech.

### User Interface
Allows users to select modes, speak, view text, view sources, replay responses, and handle errors.

### Hardware Integration
Handles Raspberry Pi deployment, microphone, speaker, display, push-to-talk input, and power.

## Privacy

Normal system operation will not require internet access.

User speech, transcripts, questions, and generated responses will not be intentionally retained after an interaction is complete.

## Development Principle

Individual components may be developed separately, but integration will occur throughout the semester rather than waiting until the end.
