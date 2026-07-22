import matplotlib.pyplot as plt
import pandas as pd

def generate_portfolio_visualization():
    # Sample data representing network performance or data metrics
    data = {
        'Module': ['Basics', 'Structures', 'Fundamentals', 'Data', 'APIs', 'Visualizations'],
        'Completion_Score': [95, 90, 92, 88, 94, 96]
    }
    
    df = pd.DataFrame(data)
    
    # Plotting the data
    plt.figure(figsize=(10, 5))
    plt.bar(df['Module'], df['Completion_Score'], color='#1f77b4')
    plt.xlabel('Portfolio Modules')
    plt.ylabel('Score / Proficiency (%)')
    plt.title('Master Engineering Portfolio - Module Progression')
    plt.ylim(0, 100)
    
    # Save the plot as an image asset for your portfolio
    plt.savefig('portfolio_progress.png')
    print("Visualization generated and saved successfully as 'portfolio_progress.png'!")

if __name__ == "__main__":
    generate_portfolio_visualization()