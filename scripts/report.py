import requests
import os
from datetime import datetime, timedelta
from pathlib import Path

TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query{
  viewer {
    projectV2(number:1){
      title

      items(first:100){
        nodes{

          content{
            __typename

            ... on Issue{
              title
              url
              updatedAt
            }

            ... on PullRequest{
              title
              url
              updatedAt
            }
          }

          fieldValues(first:20){
            nodes{

              ... on ProjectV2ItemFieldSingleSelectValue{
                name

                field{
                  ... on ProjectV2SingleSelectField{
                    name
                  }
                }
              }

            }
          }

        }
      }

    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

r = requests.post(
    "https://api.github.com/graphql",
    json={"query": QUERY},
    headers=headers
)

data = r.json()

items = (
    data["data"]["viewer"]
    ["projectV2"]
    ["items"]["nodes"]
)

week_ago = datetime.utcnow() - timedelta(days=7)

done = []
progress = []
todo = []

for item in items:

    content = item.get("content")

    if not content:
        continue

    title = content["title"]

    updated = datetime.fromisoformat(
        content["updatedAt"]
        .replace("Z","+00:00")
    )

    status = "Unknown"

    for fv in item["fieldValues"]["nodes"]:

        if (
            fv.get("field", {})
            .get("name")
            == "Status"
        ):
            status = fv["name"]

    line = f"- {title}"

    if status == "Done":
        done.append(line)

    elif status == "In Progress":
        progress.append(line)

    else:
        todo.append(line)

today = datetime.now().strftime(
    "%Y-%m-%d"
)

report = f"""
# Weekly Work Report

Generated: {today}

## Completed

{"\n".join(done)}

## In Progress

{"\n".join(progress)}

## Pending

{"\n".join(todo)}

## Summary

Done: {len(done)}

In Progress: {len(progress)}

Pending: {len(todo)}
"""

Path("reports").mkdir(
    exist_ok=True
)

with open(
    f"reports/{today}.md",
    "w"
) as f:
    f.write(report)

print("done")
