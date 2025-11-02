import os, json
from tqdm import tqdm
from .api_client import JiraAPIClient
from .utils import save_checkpoint, load_checkpoint

class JiraScraper:
    def __init__(self,c):
        self.c=c; self.client=JiraAPIClient(c['api']['base_url'],c['api']['rate_limit_delay'])
        os.makedirs(c['output']['raw_dir'],exist_ok=True)

    def scrape_project(self,p):
        cp=f"data/checkpoints/{p}.json"
        start=load_checkpoint(cp,p)
        total=self.c['scraping']['max_issues_per_project']
        bar=tqdm(total=total,desc=p,initial=start)

        while start<total:
            batch=min(100,total-start)
            data=self.client.get("search",jql=f"project={p} ORDER BY created DESC",
                                startAt=start,maxResults=batch,
                                fields="key")
            for issue in data.get("issues",[]):
                key=issue["key"]
                path=f"{self.c['output']['raw_dir']}/{key}.json"
                if not os.path.exists(path):
                    full=self.client.get(f"issue/{key}",fields="summary,description,status,priority,reporter,comment")
                    with open(path,"w") as f: json.dump(full,f)
                start+=1; bar.update(1)
                save_checkpoint(cp,p,start)
            if len(data["issues"])<batch: break
        bar.close()