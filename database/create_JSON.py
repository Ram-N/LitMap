import csv
import json
import os

def csv_to_json(in_file, out_file):

    print(os.getcwd())
    # Open your CSV file
    with open(in_file, mode='r') as csv_file:
        # Read the CSV file using the DictReader to get column headers as keys
        csv_reader = csv.DictReader(csv_file)
        
        # Convert the data into a list of dictionaries
        data = list(csv_reader)

    # Convert the list of dictionaries to a JSON string
    json_data = json.dumps(data, indent=4)

    # Write the JSON data to a file
    with open(out_file, 'w') as json_file:
        json_file.write(json_data)

    # Print the JSON data if you want to see it
    print(json_data)


if __name__ == "__main__":
    csv_to_json("travel-writers-books.csv", "test.json")
