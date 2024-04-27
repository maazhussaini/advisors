import pandas as pd

def working_Capital(balanceSheet_df, workingCapital_df):
    
    workingCapital_df.to_csv("workingCapital_df.csv", index=False)
    
    balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
    
    last_year = balanceSheet_df.columns.to_list()[-1]
    
    """
        Working with WC
    """
    temp_columns = workingCapital_df[['SAR', 'Notes']]
    workingCapital_df = workingCapital_df.drop('SAR', axis=1)
    workingCapital_df = workingCapital_df.drop('Notes', axis=1)
    
    
    workingCapital_predicted_df = workingCapital_df.loc[:, str(last_year+1): ]
    
    workingCapital_predicted_df = pd.concat([temp_columns, workingCapital_predicted_df], axis=1)
    workingCapital_predicted_dict = workingCapital_predicted_df.to_dict(orient='records')
    
    for i in workingCapital_predicted_dict:
        for j in balanceSheet_dict:
            try:
                if i['SAR'] == j['BALANCE SHEET']:
                    my_dict = i
                    if 'SAR' in my_dict:
                        del my_dict['SAR']
                    
                    j.update(my_dict)
            except:
                pass
    workingCapital_predicted_df = pd.DataFrame(workingCapital_predicted_dict)
    workingCapital_predicted_df.to_csv("workingCapital_predicted_df.csv", index=False)
    
    return workingCapital_predicted_dict