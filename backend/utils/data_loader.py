import pandas as pd
import os

def load_datasets(base_path='../'):
    """Load all datasets"""
    datasets = {}
    
    try:
        datasets['progress'] = pd.read_csv(os.path.join(base_path, 'dataset2.csv'))
        print(f"✓ Loaded progress data: {len(datasets['progress'])} rows")
    except Exception as e:
        print(f"⚠ Error loading dataset2.csv: {e}")
        datasets['progress'] = None
    
    try:
        datasets['dietary'] = pd.read_csv(os.path.join(base_path, 'dataset6.csv'))
        print(f"✓ Loaded dietary data: {len(datasets['dietary'])} rows")
    except Exception as e:
        print(f"⚠ Error loading dataset6.csv: {e}")
        datasets['dietary'] = None
    
    try:
        datasets['exercises'] = pd.read_csv(os.path.join(base_path, 'dataset8.csv'))
        print(f"✓ Loaded exercises data: {len(datasets['exercises'])} rows")
    except Exception as e:
        print(f"⚠ Error loading dataset8.csv: {e}")
        datasets['exercises'] = None
    
    try:
        datasets['stretches'] = pd.read_csv(os.path.join(base_path, 'stretch_exercise_dataset.csv'))
        print(f"✓ Loaded stretches data: {len(datasets['stretches'])} rows")
    except Exception as e:
        print(f"⚠ Error loading stretch_exercise_dataset.csv: {e}")
        datasets['stretches'] = None
    
    try:
        datasets['powerlifting'] = pd.read_csv(os.path.join(base_path, 'powerlifting_dataset.csv'))
        print(f"✓ Loaded powerlifting data: {len(datasets['powerlifting'])} rows")
    except Exception as e:
        print(f"⚠ Error loading powerlifting_dataset.csv: {e}")
        datasets['powerlifting'] = None
    
    return datasets
