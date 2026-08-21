import pandas as pd # Imports the Pandas library, allowing us to read and manipulate tabular data like CSVs.
from datetime import datetime, timedelta # Imports time modules so we can mathematically calculate the time gap between messages.
import json # Imports the JSON module for structuring data (useful for metadata processing).

def group_into_sessions(csv_path="data/cleaned_chat_history.csv", gap_minutes=30): # Defines our function, defaulting to our cleaned CSV and a 30-minute threshold.
    df = pd.read_csv(csv_path) # Reads the cleaned chat CSV file into a Pandas DataFrame.
    df['date'] = pd.to_datetime(df['date']) # Converts the text-based 'date' column into actual datetime objects.
    df = df.sort_values('date') # Sorts all rows chronologically to ensure the conversation flows in order.

    sessions = [] # Initializes an empty list that will hold all of our finalized conversation blocks.
    current_session = [] # Initializes an empty list to temporarily hold messages for the active conversation we are looping through.

    for index, row in df.iterrows(): # Starts a loop iterating over every single row (message) in the DataFrame.
        if not current_session: # Checks if the current session is empty (which it is on the very first message).
            current_session.append(row) # Adds the first message to the current session.
        else: # If there are already messages in the current session...
            prev_time = current_session[-1]['date'] # Grabs the timestamp of the last message we added to the session.
            curr_time = row['date'] # Grabs the timestamp of the current message we are evaluating.
            
            if (curr_time - prev_time) <= timedelta(minutes=gap_minutes): # Calculates if the time difference is 30 minutes or less.
                current_session.append(row) # If it is within 30 minutes, it's the same conversation, so we append it.
            else: # If the time gap is greater than 30 minutes, the conversation died out.
                sessions.append(current_session) # We save the completed conversation block to our main 'sessions' list.
                current_session = [row] # We start a brand new session with the current message.

    if current_session: # After the loop finishes, checks if there is one final session left hanging.
        sessions.append(current_session) # Adds the final session to our main list.

    documents = [] # Initializes a list to hold the formatted text and metadata ready for the vector database.
    for idx, session in enumerate(sessions): # Loops through all our completed sessions, keeping track of an index number.
        start_time = session[0]['date'].strftime("%Y-%m-%d %H:%M") # Formats the start time of the session into a clean string.
        end_time = session[-1]['date'].strftime("%Y-%m-%d %H:%M") # Formats the end time of the last message in the session.
        
        dialogue = [] # Initializes a temporary list to hold the formatted text of the messages.
        for msg in session: # Loops through every individual message inside the current session block.
            sender = "Her" if msg['sender'] != "Me" else "Me" # Standardizes the sender name to either "Her" or "Me".
            dialogue.append(f"{sender}: {msg['message']}") # Formats the string as "Sender: Message Text" and adds it to the dialogue list.
            
        full_text = f"Date: {start_time}\n" + "\n".join(dialogue) # Combines the date header with all the dialogue lines separated by line breaks.
        
        documents.append({ # Appends a dictionary representing the finalized document to our documents list.
            "page_content": full_text, # The actual text content that will be vectorized (embedded) by OpenAI.
            "metadata": { # A dictionary of filterable facts about the text chunk.
                "session_id": idx, # The unique numerical ID for this specific conversation session.
                "start_time": start_time, # The metadata timestamp for when the chat started.
                "end_time": end_time, # The metadata timestamp for when the chat ended.
                "msg_count": len(session) # The total number of back-and-forth messages contained in this chunk.
            } # Closes the metadata dictionary.
        }) # Closes the document dictionary and the append function.

    print(f"Grouped {len(df)} messages into {len(documents)} conversational sessions.") # Prints a summary of how much the data was compressed.
    return documents # Returns the fully processed list of documents to whatever called this function.

if __name__ == "__main__": # Checks if this script is being run directly (rather than imported).
    docs = group_into_sessions() # Executes the function and stores the result in 'docs'.
    print("Sample Session Chunk:\n" + docs[0]['page_content']) # Prints the text of the very first grouped session as a sanity check.