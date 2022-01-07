import httpx

import sys
import json
from pathlib import Path
import zipfile
from glob import glob


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
    zip_path = tmp_dir / f"{name}.zip"
    with open(zip_path, "wb") as f:
        f.write(req.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)

    zip_path.unlink()

files = glob(str(tmp_dir / "*"))
client.delete("https://api.github.com/repos/redfuck/fucc/git/refs/tags/kebab")

print("\n".join(files))