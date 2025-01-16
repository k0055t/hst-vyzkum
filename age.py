import json
import matplotlib.pyplot as plt
import numpy as np
import re
import os
from collections import defaultdict

results = defaultdict(lambda: defaultdict(list))

# Load the JSON data (replace this with your actual json file loading code)
with open('askreddit.json', 'r') as file:
    data = json.load(file)


def open_json_files_in_directory(directory_path):
    jsons = []

    # List all files in the given directory
    for filename in os.listdir(directory_path):
        # Check if the file ends with .json
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            try:
                # Open and load the JSON file
                with open(file_path, 'r') as file:
                    jsons.append(json.load(file))
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return jsons

# Extract the relevant data
def rating_from_message(input_str):
    # Find all numbers in the string using regex
    numbers = re.findall(r'-?\d+', input_str)
    
    # Check if any number is found and if it's within the valid range
    if numbers:
        # Convert the first matched number to an integer
        number = int(numbers[0])
        
        # Check if the number is within the range from -9 to 9
        if -9 <= number <= 9:
            return number
        else:
            return None
    else:
        return None
    

jsons = open_json_files_in_directory(os.path.join(os.getcwd(), ""))


for subreddit in jsons:
    for entry in subreddit:
        col = entry['author']['account_age_days']
        a = rating_from_message(entry['left_to_right_rating'])
        b = rating_from_message(entry["libertarian_to_authoritarian_rating"])
        if col != None and a != None and b != None and col != 0:
            results[a][b].append(col)

x = []
y = []
colors = []

for i in results:
    for j in results[i]:
        x.append(i)
        y.append(j)
        colors.append(np.average(results[i][j]).item())




    # Normalize the color data (so it's between 0 and 1 for coloring)
norm = plt.Normalize(min(colors), max(colors))

# Create the scatter plot
plt.figure(figsize=(10, 6))
scatter = plt.scatter(x, y, c=colors, cmap='RdYlGn', norm=norm)

# Add color bar for reference
plt.colorbar(scatter, label='Account Age (Days)')

# Set labels and title
plt.xlabel('Left to Right')
plt.ylabel('Libertarian to Authoritarian')
plt.title('Scatter plot of Ratings with Account Age Color Mapping')

# Show the plot
plt.show()