import json
import re
import os
import matplotlib.pyplot as plt

results = []

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
                    jsons.append([json.load(file), filename.split(".")[0]])
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return jsons


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


# Function to load JSON and calculate the average of 'rating'
def calculate_average_rating(json_data, atribute):
    ratings = []
    
    # Iterate through each item in the JSON data
    for item in json_data:
        # Check if the 'rating' key exists
        if atribute in item:
            a = rating_from_message(item[atribute])
            if a != None and a != 0:
                ratings.append(a)
    
    # Calculate the average if there are ratings
    if ratings:
        print(len(ratings))
        average_rating = sum(ratings) / len(ratings)
        return average_rating
    else:
        return None

# Load the JSON from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def plot_scatter(x_values, y_values, title="Reddit political map", x_label="left to right", y_label="libertarian to autoritative"):
    # Create a scatter plot
    plt.scatter(x_values, y_values)
    
    # Set the title and labels
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    plt.xlim(-9, 9)
    plt.ylim(-9, 9)
    
    # Show the plot
    plt.show()


# Example Usage:
if __name__ == "__main__":
    jsons = open_json_files_in_directory(os.path.join(os.getcwd(), ""))

    for data in jsons:
        # Calculate and print the average rating
        avg_authoritarian = calculate_average_rating(data[0], "libertarian_to_authoritarian_rating")
        avg_left = calculate_average_rating(data[0], "left_to_right_rating")

        results.append([data[1] ,avg_authoritarian, avg_left])
    auth_vals = []
    left_vals = []
    for result in results:
        auth_vals.append(result[1])
        left_vals.append(result[2])
    plot_scatter(left_vals, auth_vals)

    print(results)