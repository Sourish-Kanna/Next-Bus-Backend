import json

# Replace 'service-account' with your actual file path without the .json extension
input_filename = 'service-account'

try:
    # 1. Read the JSON file
    with open(f"{input_filename}.json", 'r') as file:
        data = json.load(file)

    # 2. Dump to string with no whitespace
    # separators=(',', ':') removes the default spaces after separators
    single_line_json = json.dumps(data, separators=(',', ':'))

    # 3. Output the result
    print("Copy the string below for your environment variable:")
    print("-" * 20)
    print(single_line_json)
    print("-" * 20)

    # Optional: Save it to a text file for easy copying
    with open(f'{input_filename}.txt', 'w') as outfile:
        outfile.write(single_line_json)
        print(f"Also saved to '{input_filename}.txt'")

except FileNotFoundError:
    print(f"Error: The file '{input_filename}.json' was not found.")
except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from '{input_filename}.json'.")