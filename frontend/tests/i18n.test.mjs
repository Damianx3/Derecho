import test from 'node:test';
import assert from 'node:assert/strict';
import { STRINGS, UI_LOCALES, translate, translateError } from '../src/i18n.mjs';

test('every interface language covers all strings and preserves placeholders', () => {
  const keys = Object.keys(STRINGS.English).sort();
  for (const locale of UI_LOCALES) {
    assert.deepEqual(Object.keys(STRINGS[locale.name]).sort(), keys);
    for (const key of keys) {
      assert.ok(STRINGS[locale.name][key].trim());
      assert.deepEqual(STRINGS[locale.name][key].match(/\{\w+\}/g), STRINGS.English[key].match(/\{\w+\}/g));
    }
  }
});
test('labels and errors switch language and interpolate speaker numbers', () => {
  assert.equal(translate('Spanish','speaker',{n:2}), 'Hablante 2');
  assert.equal(translate('French','translationMode'), 'Mode traduction');
  assert.equal(translate('Portuguese','done'), 'Concluir');
  assert.equal(translate('German','back'), 'Zurück');
  assert.equal(translateError('Spanish','Microphone recording failed'), STRINGS.Spanish.recordingError);
  assert.equal(translateError('German','Cannot reach Derecho'), STRINGS.German.connectionError);
});
test('unknown locales use English without breaking text interpolation', () => {
  assert.equal(translate('Unknown','speaker',{n:1}), 'Speaker 1');
});
