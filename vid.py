import concurrent
import csv
def process_row(row):
    file_url = row["File URL"].replace("blob", "raw")
    repo_name = row["Repository"].split("/")[-1]

    response = requests.get(file_url, proxies=proxies)

    # Write the response content to a file
    with open(f"output/{repo_name}.json", "w") as file:
        file.write(response.text)
# # Load input CSV
input_file = csv.DictReader(open("sg.csv"))

# Use ThreadPoolExecutor to process rows in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks to the executor
    futures = [executor.submit(process_row, row) for row in input_file]

    # Wait for all futures to complete, if needed, you can handle results here
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()  # You can use this to handle results or exceptions
        except Exception as exc:
            print(f'Generated an exception: {exc}')

print("All tasks completed.")