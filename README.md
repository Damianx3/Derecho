# Derecho

**Derecho: A Privacy-First Offline Multilingual Translator and Immigration Rights Voice Assistant**

Derecho is a senior design project focused on building a standalone voice assistant that performs multilingual speech translation and provides source-grounded immigration-rights information without relying on cloud processing.

The final prototype will run locally on a Raspberry Pi 5 with 8GB of RAM.

## Modes

### Translator Mode

Speech Input  
→ Automatic Speech Recognition  
→ Language Detection  
→ Machine Translation  
→ Text Display  
→ Text-to-Speech

### Know Your Rights Mode

Speech Input  
→ Automatic Speech Recognition  
→ Hybrid Information Retrieval  
→ Trusted Source Passages  
→ Local Language Model  
→ Grounded Response + Citations  
→ Text-to-Speech

Know Your Rights Mode is intended to provide general educational information and is not a substitute for individualized legal advice.

## Project Goals

- Fully offline normal operation
- Multilingual speech translation
- English and Spanish immigration-rights questions
- Trusted local knowledge base
- Hybrid keyword and semantic retrieval
- Source-grounded responses
- Citations
- Refusal when supporting evidence is insufficient
- Spoken input and output
- Raspberry Pi deployment
- Privacy-focused design
- No intentional permanent storage of user conversations

## Hardware

- Raspberry Pi 5 8GB
- Microphone
- Speaker
- Display
- Push-to-talk control
- Portable power source

## Technology

Current and planned technologies include:

- Python
- Whisper using the whisper.cpp implementation
- Local machine translation models
- Local language models
- BM25 keyword retrieval
- Vector embeddings
- FAISS or similar local vector search
- Local text-to-speech
- Raspberry Pi GPIO
- Git and GitHub

Final model and runtime choices may change based on accuracy, latency, memory usage, and Raspberry Pi performance.

## Repository Structure

```text
backend/      AI and application logic
frontend/     Local user interface
data/         Legal sources and evaluation data
hardware/     Raspberry Pi and GPIO-related code
docs/         Architecture, testing plans, and technical decisions
scripts/      Setup, benchmark, deployment, and utility scripts
