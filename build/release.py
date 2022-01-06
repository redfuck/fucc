import httpx

import sys
import json
from pathlib import Path


if len(sys.argv) < 2:
    exit("Please put token sir")
token = sys.argv[1]

tmp_dir = Path(".tmp")

headers = {"Authorization": f"Bearer {token}"}
client = httpx.Client(headers=headers)

req = client.get("https://api.github.com/repos/redfuck/fucc/actions/workflows?per_page=100")
data = json.loads(req.text)
workflows = data["workflows"]
tools_workflows_names = [x["name"] for x in workflows if x["html_url"].endswith("-tool.yml")]

# Getting last artifacts IDs
req = client.get(f"https://api.github.com/repos/redfuck/fucc/actions/artifacts?per_page=100")
data = json.loads(req.text)
artifacts = data["artifacts"]

artifacts_ids = {}
for workflow_name in tools_workflows_names:
    for artifact in artifacts:
        if artifact["name"] == workflow_name:
            artifacts_ids[workflow_name] = artifact["id"]
            break

for name, artifact_id in artifacts_ids.items():
    req = client.get(f"https://api.github.com/repos/redfuck/fucc/actions/artifacts/{artifact_id}/zip")
    direct_link = req.headers["location"]
    req = client.get(direct_link)
    with open(tmp_dir / f"{name}.zip", "wb") as f:
        f.write(req.content)

#import pdb; pdb.set_trace()