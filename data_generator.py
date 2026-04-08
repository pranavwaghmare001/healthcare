import pandas as pd
import os

def generate_synthetic_data(num_samples=2000):
    """
    Downloads the real Kaggle Disease Prediction dataset from a public GitHub mirror
    instead of generating synthetic data.
    """
    print("Downloading real Kaggle dataset (132 symptoms, 41 diseases)...")
    url = "https://raw.githubusercontent.com/anujdutt9/Disease-Prediction-from-Symptoms/master/dataset/training_data.csv"
    
    # Load real dataset
    df = pd.read_csv(url)
    
    # Rename the target column 'prognosis' to 'Disease' to maintain compatibility with our AI model
    if 'prognosis' in df.columns:
        df = df.rename(columns={'prognosis': 'Disease'})
        
    # Clean up empty trailing columns if they exist (common in CSVs)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Make symptoms readable (e.g. 'chest_pain' -> 'chest pain')
    df.columns = [col.replace('_', ' ') if col != 'Disease' else col for col in df.columns]
    
    return df

if __name__ == "__main__":
    df = generate_synthetic_data()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"Real Kaggle dataset saved to: {output_path}")
    print(f"Dataset shape: {df.shape}")

