import json, os, re
from .prompt_generator import examples

class Transformer:
    def __init__(self, c):
        self.raw = c['output']['raw_dir']
        self.out = c['output']['final_output']

    def clean(self, t):
        """Clean HTML tags, code blocks, and trim whitespace."""
        if not t:
            return ""
        t = re.sub("<[^>]+>", "", t)
        t = re.sub(r"{code.*?}.*?{code}", "[CODE]", t, flags=re.S)
        return t.strip()

    def run(self):
        all_ex = []
        bad_files = []

        files = os.listdir(self.raw)
        print(f"Found {len(files)} raw files to process...")

        for fname in files:
            try:
                with open(os.path.join(self.raw, fname), "r", encoding="utf-8") as j:
                    issue = json.load(j)
                    f = issue.get("fields", {})

                    meta = {
                        "title": f.get("summary", "(No title)"),
                        "description": self.clean(f.get("description", "")),
                        "status": f.get("status", {}).get("name", "Unknown"),
                        "comments": [
                            self.clean(c.get("body", ""))
                            for c in f.get("comment", {}).get("comments", [])
                        ],
                    }

                    
                    all_ex.extend(examples(meta))

            except Exception as e:
                bad_files.append((fname, str(e)))

 
        os.makedirs(os.path.dirname(self.out), exist_ok=True)
        with open(self.out, "w", encoding="utf-8") as out_f:
            for e in all_ex:
                out_f.write(json.dumps(e, ensure_ascii=False) + "\n")

        print(f"✅ Transformer completed: {len(all_ex)} examples → {self.out}")

        if bad_files:
            print(f"⚠️ Skipped {len(bad_files)} files due to errors (logged below):")
            for fname, err in bad_files[:10]:
                print(f"   - {fname}: {err}")
            if len(bad_files) > 10:
                print(f"   ...and {len(bad_files) - 10} more.")
