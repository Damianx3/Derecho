# Contributing to DERECHO

## Workflow

Create a branch from the latest `main` branch.

Examples:

feat/whisper-asr
feat/legal-retrieval
feat/translator-ui
hardware/ptt-button
test/asr-benchmark
docs/architecture
fix/audio-input

## Before Starting Work

Update the local main branch:

git switch main
git pull

Then create a new branch:

git switch -c <branch-name>

## Commits

Use short descriptive commit messages.

Examples:

Add Whisper audio transcription
Implement BM25 retrieval
Add Translator screen
Fix microphone initialization

## Pull Requests

Push your branch and open a pull request into `main`.

At least one other team member should review significant changes before they are merged.

## Main Branch

The `main` branch should represent the latest working integrated version of DERECHO.

Avoid developing major features directly on `main`.

## Definition of Done

A feature is considered complete when it:

- works
- has been reviewed
- is merged
- runs in the intended environment
- has been tested
- is documented when necessary
