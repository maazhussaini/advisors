import pandas as pd
import mysql.connector as sql
from mysql.connector import errorcode
from mysql.connector import Error

def create_connection():
    try:
        connection = sql.connect(host = 'localhost',
                   user = 'root',
                   password = '1234',
                   database = 'advisors')
        
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def fill_empty_strings_with_zero(df):
    # Identify text columns
    text_columns = df.select_dtypes(include='object').columns

    # Identify numeric columns (both int and float)
    numeric_columns = df.select_dtypes(include=['int', 'float']).columns

    # Fill empty strings with 0 in numeric columns
    df[numeric_columns] = df[numeric_columns].fillna(0)

    # Fill empty strings with 0 in text columns
    df[text_columns] = df[text_columns].fillna('')

    return df

# Function to insert data in chunks
def insert_data_in_chunks(connection, data, chunk_size=10000):
    cursor = connection.cursor()
    total_rows = len(data)
    num_chunks = (total_rows // chunk_size) + 1

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk_data = data[start_idx:end_idx]

        if not chunk_data.empty:
            try:
                # Assuming 'your_table' is the table where you want to insert data
                insert_query = """
                    INSERT INTO `advisors`.`nsc_tb`
                    (`Account`, `Description`, `Notes`,`L1`, `L2`,`L3`, `L4`, `L5`, 
                    `Ending Balance`, `Year`, `Source_Name`)
                    VALUES
                    (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """
                # chunk_data.fillna('', inplace=True)
                chunk_data = fill_empty_strings_with_zero(chunk_data)
                values = [tuple(row) for row in chunk_data.values]
                cursor.executemany(insert_query, values)
                connection.commit()
                print(f"Inserted {len(chunk_data)} rows: {i}")
            except Error as e:
                # chunk_data.to_csv(f"../Output/ErrorSample_{i}.csv", index=False)
                print(f"Error: {e}-----{i}")
                connection.rollback()

    cursor.close()

# Read data from CSV file using pandas
data = pd.read_csv("E:\\MaazProducts\\Fiverr\\AME - MOS & MH - Platform\\Code\\Nasco\\Code\\output\\Final\\V1\\NSC-TB-Quaterly.csv")

# Create a MySQL connection
connection = create_connection()

# Check if connection is established
if connection:
    # Insert data in chunks
    insert_data_in_chunks(connection, data)

    # Close the connection
    connection.close()
