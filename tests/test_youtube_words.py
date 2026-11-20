"""YouTube's own transcript is taken in the language actually spoken, never a translation, and never the
wrong language when a video has more than one audio track. The network is replaced by stand-ins, so
nothing leaves this machine."""
import contextlib, json, os, sys, tempfile
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-ytwords-"); os.environ["DATABASE_URL"] = ""
sys.path.insert(0, ".")
from unittest import mock
from studio import media
fails = []
def check(n, ok, x=""):
    print(("PASS " if ok else "FAIL ") + n + (f"  {x}" if x and not ok else "")); ok or fails.append(n)

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
PAYLOAD = json.dumps({"events": [{"tStartMs": 0, "dDurationMs": 1000,
                                  "segs": [{"utf8": "hello world"}]}]}).encode()

class FakeResp:
    def __init__(self, data):
        self._data = data
    def read(self, n=-1):
        return self._data

class FakeYDL:
    def __init__(self, info):
        self._info = info
        self.fetched = []
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False
    def extract_info(self, url, download=False):
        return self._info
    def urlopen(self, url):
        self.fetched.append(url)
        return FakeResp(PAYLOAD)

@contextlib.contextmanager
def fake_guard(url):
    yield

def run_case(info):
    fake = FakeYDL(info)
    with mock.patch.object(media, "_ydl", lambda opts: fake), \
         mock.patch.object(media, "_youtube_guard", fake_guard):
        return media.youtube_words(URL), fake.fetched

def track(key, ext="json3"):
    return {"ext": ext, "url": f"https://example.invalid/{key}.{ext}"}

# ---- the Batch 2 bug: Arabic first in dict order, English spoken
info = {"language": "en-US", "automatic_captions": {
    "ar-orig": [track("ar-orig")], "en-orig": [track("en-orig")],
    "en": [track("en")], "ar": [track("ar")]}}
out, fetched = run_case(info)
check("multi-audio video: the English original is fetched, not the Arabic one first in the dict",
      fetched == ["https://example.invalid/en-orig.json3"], str(fetched))
check("...and the language comes back as the short code 'en'",
      out is not None and out[1] == "en", str(out[1] if out else None))
check("...and the words are the English transcript",
      out is not None and [w["w"] for w in out[0]] == ["hello", "world"],
      str([w["w"] for w in out[0]] if out else None))

# ---- a bare regional key: "en-US" with no "-orig" at all
info = {"language": "en-US", "automatic_captions": {"en-US": [track("en-US")]}}
out, fetched = run_case(info)
check("bare 'en-US' key is used, and the language is still 'en'",
      out is not None and out[1] == "en" and fetched == ["https://example.invalid/en-US.json3"],
      str((out[1] if out else None, fetched)))

# ---- only a regional variant of the base language exists
info = {"language": "en-US", "automatic_captions": {"en-GB-orig": [track("en-GB-orig")]}}
out, fetched = run_case(info)
check("'en-GB-orig'-only video: that track is used, and the language is still 'en'",
      out is not None and out[1] == "en" and fetched == ["https://example.invalid/en-GB-orig.json3"],
      str((out[1] if out else None, fetched)))

# ---- the best key has no json3 track: fall through to the next key that does
info = {"language": "en-US", "automatic_captions": {
    "en-orig": [track("en-orig", "vtt")], "ar-orig": [track("ar-orig")]}}
out, fetched = run_case(info)
check("best key without a json3 track is skipped, the next key with one is used",
      fetched == ["https://example.invalid/ar-orig.json3"] and out is not None and out[1] == "ar",
      str((fetched, out[1] if out else None)))

# ---- nothing usable: no transcript at all
info = {"language": "en-US", "automatic_captions": {}}
out, fetched = run_case(info)
check("no captions at all returns None", out is None and fetched == [], str((out, fetched)))
info = {"language": "en-US", "automatic_captions": {"en-orig": [track("en-orig", "vtt")]}}
out, fetched = run_case(info)
check("keys with no json3 track anywhere return None", out is None and fetched == [], str((out, fetched)))

print("ALL PASSED" if not fails else f"{len(fails)} failed")
import shutil; shutil.rmtree(os.environ["PEAKCUT_DATA"], ignore_errors=True)
sys.exit(1 if fails else 0)
