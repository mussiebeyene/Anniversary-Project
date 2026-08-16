import pandas as pd
import re

TAPBACK_PREFIXES = ["Loved ", "Liked ", "Disliked ", "Laughed at ", "Emphasized ", "Questioned "]

def is_tapback(text):
    if not isinstance(text, str):
        return True
    return any(text.startswith(prefix) for prefix in TAPBACK_PREFIXES)

def clean_data():
    df = pd.read_csv("data/our_chat_history.csv")
    initial_count = len(df)
    
    # 1. Drop missing rows & filter out system tapbacks
    df = df.dropna(subset=['message'])
    df = df[~df['message'].apply(is_tapback)]
    
    # 2. Trim whitespace and strip standalone URLs
    df['message'] = df['message'].str.strip()
    url_pattern = r'http[s]?://\S+'
    df['message'] = df['message'].apply(lambda x: re.sub(url_pattern, '', x).strip())
    df = df[df['message'] != '']
    
    output_path = "data/cleaned_chat_history.csv"
    df.to_csv(output_path, index=False)
    print(f"Scrubbing complete! Reduced from {initial_count} to {len(df)} clean messages.")

if __name__ == "__main__":
    clean_data()