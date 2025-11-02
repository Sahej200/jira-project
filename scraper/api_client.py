import requests, time, backoff, logging
logging.basicConfig(level=logging.INFO)

class JiraAPIClient:
    def __init__(self, base, delay=1):
        self.base, self.delay = base, delay
        self.s = requests.Session()

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
    def get(self, ep, **kw):
        time.sleep(self.delay)
        r = self.s.get(f"{self.base}/{ep}", params=kw, timeout=10)
        if r.status_code==429:
            time.sleep(int(r.headers.get("Retry-After",60)))
            return self.get(ep,**kw)
        r.raise_for_status()
        return r.json()