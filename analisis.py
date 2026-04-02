import pandas as pd

df = pd.read_csv('data/Disease_symptom_and_patient_profile_dataset.csv')

print(df.head())

print(df.info())

print(df.describe())