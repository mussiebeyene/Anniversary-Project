import sqlite3
import pandas as pd
import os

# 1. Path to local hidden iMessage database
db_path = os.path.expanduser("~/Library/Messages/chat.db")

# 2. Target contact phone number or email exactly as formatted in Contacts
HER_CONTACT_ID = "+14243554979"  

def export_chat():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # SQL Query: Joins message table with handle table and converts Apple epoch time
        query = f'''
        SELECT 
            COALESCE(h.id, 'Me') as sender, 
            m.text as message, 
            datetime(m.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') as date 
        FROM message m 
        LEFT JOIN handle h ON m.handle_id = h.ROWID 
        WHERE h.id = '{HER_CONTACT_ID}' 
        AND m.text IS NOT NULL 
        AND m.text != '' 
        ORDER BY m.date ASC;
        '''
        
        # Load query result directly into Pandas DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Export to CSV
        output_file = "data/our_chat_history.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print(f"Success! Exported {{len(df)}} messages to {{output_file}}.")
        
    except sqlite3.OperationalError as e:
        print("Database error. Did you forget to grant Full Disk Access to your Terminal?")
        print(f"Error details: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    export_chat()