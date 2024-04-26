# Define your proxies
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
proxies = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTP_PROXY"),
}

vulnerability_summary_list = []


def snyk_audit(file: Path):

    attempt = 0
    max_attempts = 5
    json_text = open(file, "r").read()

    # if json_text is empty, skip the file
    if len(json_text) == 0:
        raise ValueError(f"File {file.name} is empty.")

    while attempt < max_attempts:

        response = requests.post(
            "https://api.snyk.io/v1/test/npm",
            headers={
                "Content-Type": "application/json",
                "Authorization": os.getenv("SNYK_API_KEY"),
            },
            json={
                "encoding": "plain",
                "files": {"target": {"contents": open(file, "r").read()}},
            },
        )

        if response.status_code == 429:
            print("Rate limited. Waiting 5 seconds before retrying.")
            time.sleep(90)
            attempt += 1
        else:
            break

    if response.status_code == 429:
        raise f"Failed with status code: {response.status_code}"
    elif response.status_code != 200:
        raise f"Failed with status code: {response.status_code}"

    else:
        # Process successful response
        with open(f"output/audits/{file.name}", "w") as snykoutput:
            snykoutput.write(json.dumps(response.json(), indent=4))


Path("output/audits").mkdir(parents=True, exist_ok=True)
with tqdm(total=len(list(Path("output").iterdir()))) as pbar:
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(snyk_audit, file) for file in list(Path("output").iterdir())
        ]

        for future in as_completed(futures):
            try:
                result = future.result()

            except Exception as exc:
                tqdm.write(f"Generated an exception: {exc}")
            pbar.update(1)
