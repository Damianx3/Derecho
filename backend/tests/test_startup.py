"""Exercise the actual launcher against fake local services, not Pi hardware."""
from pathlib import Path
import os
import shutil
import signal
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[2] / 'start-derecho.sh'
class StartupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.cleanup)
        self.home=Path(self.temp.name)
        self.repo=self.home/'Projects/Derecho'
        self.bin=self.home/'bin'
        self.bin.mkdir()
        self.repo.mkdir(parents=True)
        shutil.copyfile(SCRIPT,self.repo/'start-derecho.sh')
        files=['backend/derecho/api.py','backend/derecho/languages.py',
               'backend/derecho/asr/live_transcription.py','backend/derecho/tts/piper_worker.py',
               'frontend/package.json','frontend/src/App.jsx','frontend/src/style.css','frontend/src/i18n.mjs']
        for name in files:
            path=self.repo/name; path.parent.mkdir(parents=True,exist_ok=True);path.touch()
        (self.repo/'frontend/node_modules').mkdir()
        self.env={**os.environ,'HOME':str(self.home),'PATH':str(self.bin)+':/usr/bin:/bin',
                  'DERECHO_WHISPER_SERVER':'http://should-not-be-used','DERECHO_LIVE_STT':'1',
                  'DERECHO_PIPER_PERSISTENT':'1'}
        self.executable(self.bin/'curl','''#!/bin/bash
for arg in "$@"; do url="$arg"; done
case "$url" in
  *9379*) test -f "$HOME/stub_gemma";;
  */api/health) test -f "$HOME/stub_api";;
  */api/languages) test -f "$HOME/stub_api" && test ! -f "$HOME/stub_old_api";;
  *5173*) test -f "$HOME/stub_ui";;
  *) exit 22;;
esac
''')
        for command in ['arecord','aplay','firefox']:
            self.executable(self.bin/command,'#!/bin/bash\necho "stub '+command+'"\n')
        self.service(self.home/'Projects/gemma-translator/venv/bin/litert-lm','gemma')
        self.service(self.repo/'.venv/bin/python','api')
        self.service(self.bin/'npm','ui')

    def executable(self,path,text):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text);path.chmod(0o755)

    def service(self,path,name):
        self.executable(path, '#!/bin/bash\n'+('''if [ -f "$HOME/fail_api" ]; then echo 'API import failed' >&2; exit 1; fi
printf '%s,%s,%s' "$DERECHO_WHISPER_SERVER" "$DERECHO_LIVE_STT" "$DERECHO_PIPER_PERSISTENT" > "$HOME/backend_environment"
''' if name=='api' else '')+f'''echo $$ >> "$HOME/test_pids"
echo {name} >> "$HOME/started_services"
touch "$HOME/stub_{name}"
exec /bin/sleep 60
''')

    def run_launcher(self):
        return subprocess.run(['/bin/bash',str(self.repo/'start-derecho.sh')],env=self.env,
                              capture_output=True,text=True,timeout=15)

    def cleanup(self):
        pids=self.home/'test_pids'
        if pids.exists():
            for pid in pids.read_text().splitlines():
                try: os.kill(int(pid),signal.SIGTERM)
                except ProcessLookupError: pass
        self.temp.cleanup()

    def test_starts_all_services_and_reuses_them_on_second_launch(self):
        first=self.run_launcher()
        self.assertEqual(first.returncode,0,first.stdout+first.stderr)
        self.assertIn('Derecho ready',first.stdout)
        self.assertEqual((self.home/'backend_environment').read_text(),',0,0')
        self.assertIn('Microphone inventory',(self.home/'derecho-audio-devices.log').read_text())
        second=self.run_launcher()
        self.assertEqual(second.returncode,0,second.stdout+second.stderr)
        self.assertEqual((self.home/'started_services').read_text().splitlines(),['gemma','api','ui'])

    def test_missing_code_explains_complete_bundle_needed(self):
        (self.repo/'backend/derecho/languages.py').unlink()
        result=self.run_launcher()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('complete code bundle',result.stderr)
        self.assertFalse((self.home/'started_services').exists())

    def test_old_backend_is_reported_instead_of_launching_duplicates(self):
        for name in ['stub_gemma','stub_api','stub_old_api']:(self.home/name).touch()
        result=self.run_launcher()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('older backend',result.stderr)

    def test_backend_startup_failure_shows_log_and_does_not_open_ui(self):
        (self.home/'stub_gemma').touch();(self.home/'fail_api').touch()
        result=self.run_launcher()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('API import failed',result.stderr)
        self.assertFalse((self.home/'stub_ui').exists())

if __name__ == '__main__': unittest.main()
