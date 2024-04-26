import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rich.progress import Progress

def tally_severities(file_path):
    severities = Counter()
    with open(file_path, 'r') as file:
        data = json.load(file)
        for vulnerability in data['issues']['vulnerabilities']:
            severity = vulnerability['severity']
            severities[severity] += 1

    return severities

# Convert the iterator to a list so it's not exhausted after first use
json_files = list(Path('output/audits').glob('*.json'))

severities = Counter()
with Progress() as progress:
    task = progress.add_task('Tallying severities', total=len(json_files))
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(tally_severities, file) for file in json_files
        ]
        for future in as_completed(futures):
            severities += future.result()
            progress.advance(task)

# Example usage
with open('severities.txt', 'w') as file:
    for k, v in severities.items():
        file.write(f'{k}: {v}\n')
