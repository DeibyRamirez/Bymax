import pandas as pd

df = pd.read_csv('data/Disease_symptom_and_patient_profile_dataset.csv')

print(f"filas: {df.shape[0]}, columnas: {df.shape[1]}")
print("-" * 20)

print(df.columns.tolist())
print("-" * 20)

print(df.head())
print("-" * 20)

print(df.isnull().sum())
print("-" * 20)

print(df['Disease'].value_counts())
print("-" * 20)

print(df['Fever'].unique())