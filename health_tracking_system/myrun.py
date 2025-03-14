import pandas as pd

df = pd.read_csv(r"D:\Sonie Muthoni\ai_based_personal_health_tracking_system_in_django\health_tracking_system\datasets\Training.csv")
print(df.columns)  # Check if 'coughing' is correctly listed
