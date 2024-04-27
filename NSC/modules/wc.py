import pandas as pd

def working_capital_indicators(is_crnt_df, workingCapital_df):
    last_year = workingCapital_df.columns.to_list()[-1]
        
    revenue = is_crnt_df.loc[[0, 1, 4], :str(last_year)]  # Access using string indexer
    
    key_indicators_list = []
    key_indicators_dict = {}
    
    workingCapital_dict = workingCapital_df.to_dict(orient='records')
    checklist = revenue.columns.to_list()
    checklist = checklist[1:]
    
    for i in workingCapital_dict:
        
        key_indicators_dict = {}
        
        for j, k in i.items():
            
            if i['Notes'] == "Sales":
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = float(k) / float(revenue[str(j)].to_list()[0]) * 365
                        key_indicators_dict[j] = float(value)
                    except Exception as e:
                        pass
            
            elif i['Notes'] == "COGS":
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = float(k) / (-1 * float(revenue[str(j)].to_list()[1])) * 365
                        key_indicators_dict[j] = float(value)
                    except Exception as e:
                        pass
            elif i['Notes'] == "Exp":
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = float(k) / (-1 * float(revenue[str(j)].to_list()[2])) * 365
                        key_indicators_dict[j] = float(value)
                    except Exception as e:
                        pass
            else:
                key_indicators_dict[j] = k
                
                if str(j) in checklist:
                    try:
                        value = 0
                        key_indicators_dict[j] = float(value)
                    except Exception as e:
                        pass

        key_indicators_list.append(key_indicators_dict)
    
    key_indicators_df = pd.DataFrame(key_indicators_list)
    
    key_indicators_df.to_csv('key_indicators_df.csv', index=False)
    
    return key_indicators_df


def working_capital(workingCapital_df, key_indicators_df, is_crnt_df, prediction_year):
    
    last_year = workingCapital_df.columns.to_list()[-1]
    # Exclude the two column ('component') in the mean calculation
    temp_columns = key_indicators_df[['SAR', 'Notes']]
    key_indicators_df = key_indicators_df.drop('SAR', axis=1)
    key_indicators_df = key_indicators_df.drop('Notes', axis=1)
    avg = key_indicators_df.iloc[:, :].mean(axis=1)

    # Prepare new data for future years
    new_data = {}
    for i in range(1, prediction_year + 1):  # Assuming you want to add 5 years of data
        new_year = str(last_year + i)
        new_data[new_year] = avg.values  # Use avg.values to directly assign the array to the new year

    # Create a DataFrame from the new data
    new_df = pd.DataFrame(new_data)

    # Concatenate the original DataFrame with the new DataFrame along columns (axis=1)
    key_indicators_df = pd.concat([temp_columns, key_indicators_df, new_df], axis=1)
    
    
    """
        Now Start working on WC predictive data
    """
    key_indicators_for_prediction_df = key_indicators_df.loc[:, str(last_year+1): ]
    key_indicators_for_prediction_df = pd.concat([key_indicators_df.iloc[:, : 2], key_indicators_for_prediction_df], axis=1)
    
    predicted_revenue = is_crnt_df.loc[[0, 1, 4], str(last_year + 1): ]

    workingCapital_predicted_list = []
    
    key_indicators_for_prediction_dict = key_indicators_for_prediction_df.to_dict(orient='records')
    
    for i in key_indicators_for_prediction_dict:
        workingCapital_predicted_dict = {}
        if i['Notes'] == 'Sales':
            for key, val in i.items():
                if key.isnumeric():
                    try:
                        value = (val / 365) * predicted_revenue[key].to_list()[0]
                        workingCapital_predicted_dict[key] = value
                    except:
                        pass
        elif i['Notes'] == 'COGS':
            for key, val in i.items():
                if key.isnumeric():
                    try:
                        value = ((-1 * val) / 365) * predicted_revenue[key].to_list()[1]
                        workingCapital_predicted_dict[key] = value
                    except:
                        pass
        else:
            for key, val in i.items():
                if key.isnumeric():
                    try:
                        value = 0
                        workingCapital_predicted_dict[key] = value
                    except:
                        pass
        
        workingCapital_predicted_list.append(workingCapital_predicted_dict)
    
    workingCapital_predicted_df = pd.DataFrame(workingCapital_predicted_list)
    
    workingCapital_predicted_df = pd.concat([workingCapital_df, workingCapital_predicted_df], axis=1)
    return workingCapital_predicted_df