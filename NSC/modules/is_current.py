import pandas as pd

def isCurrent(df_fs: pd.DataFrame, df_assumption: pd.DataFrame, predicted_year: int):
    
    year_fs = df_fs['year'].to_list()
    last_year = int(year_fs[-1])
    
    df_fs_last_year = df_fs[df_fs['year'] == last_year]
    
    new_row_list = []
    
    for no_year in range(predicted_year):
        new_row = {}
        df_assumption_last_year = df_assumption[df_assumption['year'] == last_year]
        df_assumption_current_year = df_assumption[df_assumption['year'] == last_year + 1]
        
        if not df_assumption_last_year.empty and not df_assumption_current_year.empty:
            
            for i in df_fs.columns.to_list():
                if i == 'year':
                    value = last_year + 1
                else:
                    value = 0
                    
                if no_year == 0:    
                    if i in df_assumption_last_year.columns.to_list():
                        
                        if i == 'revenue' or i == 'general and administrative expenses':
                            value = (1 + df_assumption_current_year[i].values[0]) * df_fs_last_year[i].values[0]
                        
                        elif i == 'selling and marketing expenses':
                            value =  -1 + df_assumption_current_year[i].values[0] * df_fs_last_year[i].values[0]
                        
                    elif i == 'cost of revenues':
                        value = -1 * (1 - df_assumption_current_year['gp margin'].values[0]) * df_fs_last_year[i].values[0]
                            
                else:
                    if i in list(new_row_list[-1].keys()):
                        
                        if i == 'revenue' or i == 'general and administrative expenses':
                            value = (1 + df_assumption_current_year[i].values[0]) * new_row_list[-1][i]
                        
                        elif i == 'selling and marketing expenses':
                            value =  -1 + df_assumption_current_year[i].values[0] * new_row_list[-1][i]
                        
                        elif i == 'cost of revenues':
                            value = -1 * (1 + df_assumption_current_year['gp margin'].values[0]) * new_row_list[-1][i]
                
                new_row[i] = value
        else:
            break
        
        last_year = last_year + 1
        new_row['gross profit'] = new_row['revenue'] + new_row['cost of revenues']
        new_row['profit from operations'] = new_row['gross profit'] + new_row['selling and marketing expenses'] + new_row['general and administrative expenses']
        new_row_list.append(new_row)
    
    # Assuming 'new_row_list' and 'df_fs' are defined earlier in your code
    df = pd.DataFrame(new_row_list)
    
    # Concatenate df_fs with the new DataFrame. Ensure that the indexes are ignored to avoid duplicate indexes.
    df = pd.concat([df_fs, df], ignore_index=True)

    # Fill NaN values with 0
    df = df.fillna(0)
    
    df['year'] = df['year'].astype('str')
    df_copy = df.rename(columns={df.columns[0]: 'components'})
    
    # Now, transpose the DataFrame
    df_copy = df_copy.transpose().reset_index()

    new_header = df_copy.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()

    df_copy = df_copy[1:]
    df_copy.columns = new_header
    df_copy.set_index(df_copy.columns[0], inplace=True)
    
    return df