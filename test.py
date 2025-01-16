import matplotlib.pyplot as plt
import numpy as np

# Sample data
x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([10, 20, 25, 30, 15, 35])
labels = ['Point A', 'Point B', 'Point C', 'Point D', 'Point E', 'Point F']

# Create scatter plot
plt.scatter(x, y, c='blue', label='Data Points')

# Add labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Scatter Plot with Labels and Legend')

# Create custom legends for each point
for i in range(len(x)):
    plt.scatter(x[i], y[i], label=f'{labels[i]}: ({x[i]}, {y[i]})')

# Display the legend outside the plot
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title='Point Labels')

# Adjust layout to make room for the legend
plt.tight_layout()

# Show the plot
plt.show()