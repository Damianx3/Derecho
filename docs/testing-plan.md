# DERECHO Testing Plan

## Speech Recognition

Evaluate Whisper recognition using:

- English speech
- Spanish speech
- different speakers
- different noise conditions
- selected Spanglish examples

Primary metric:

- Word Error Rate (WER)

## Translation

Evaluate translation using:

- English to Spanish
- Spanish to English
- selected additional supported languages

Measurements include:

- automated translation metrics
- bilingual human evaluation
- latency

## Retrieval

Evaluate:

- keyword retrieval
- semantic retrieval
- hybrid retrieval

Possible metrics:

- Recall
- Mean Reciprocal Rank

## Grounded Responses

Evaluate whether:

- generated claims are supported by retrieved sources
- citations point to relevant evidence
- responses remain within the available evidence

## Unsupported Questions

Test questions that cannot be answered using the available knowledge base.

The system should abstain rather than generate unsupported answers.

## Performance

Measure:

- ASR latency
- translation latency
- retrieval latency
- language-model latency
- TTS latency
- total end-to-end latency
- RAM usage
- CPU usage
- device temperature

## Privacy

Verify:

- normal operation works without internet access
- inference does not require external network connections
- conversations are not permanently stored
