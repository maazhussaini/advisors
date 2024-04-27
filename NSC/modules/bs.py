import pandas as pd

def working_Capital(balanceSheet_df, workingCapital_df, last_year):
    balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
    
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
                        del my_dict['Notes']
                    
                    j.update(my_dict)
            except:
                pass
    workingCapital_predicted_df = pd.DataFrame(workingCapital_predicted_dict)
    
    
    return workingCapital_predicted_dict, balanceSheet_dict


def debt_checking(debt_df, balanceSheet_dict, last_year):
    
    debt_df = debt_df[debt_df['DEBT'] == 'Closing Balance']
    debt_df = debt_df.loc[:, str(last_year+1): ]
    
    if not debt_df.empty:
        debt_dict = debt_df.to_dict(orient='records')[0]
        
        for data in balanceSheet_dict:
            if data['BALANCE SHEET'] == "Short-term borrowings":
                del debt_dict['DEBT']
                data.update(debt_dict)
                break
            
    return debt_df, balanceSheet_dict

def FA_checking(fixedAsset_df, balanceSheet_dict, last_year):
    
    fixedAsset_df = fixedAsset_df[fixedAsset_df['FA'] == 'Closing Balance - NBV']
    fixedAsset_df = fixedAsset_df.loc[:, str(last_year+1): ]
    
    if not fixedAsset_df.empty:
        fixedAsset_dict = fixedAsset_df.to_dict(orient='records')[0]
        
        for data in balanceSheet_dict:
            if data['BALANCE SHEET'] == "Property and equipment":
                del fixedAsset_dict['FA']
                data.update(fixedAsset_dict)
                break
            
    return fixedAsset_df, balanceSheet_dict


def equity_checking(Equity_df, balanceSheet_dict, last_year):
    Equity_df = Equity_df[Equity_df['EQUITY'].isin(['Share capital','Statutory reserve','Retained earnings'])]
    
    if not Equity_df.empty:
        
        for data in balanceSheet_dict:
            if data['BALANCE SHEET'] == 'Share capital':
                data.update(Equity_df[Equity_df['EQUITY'] == 'Share capital'].loc[:, str(last_year+1): ].to_dict(orient='records')[0])
            
            elif data['BALANCE SHEET'] == 'Statutory reserve':
                data.update(Equity_df[Equity_df['EQUITY'] == 'Statutory reserve'].loc[:, str(last_year+1): ].to_dict(orient='records')[0])
            
            elif data['BALANCE SHEET'] == 'Retained earnings':
                data.update(Equity_df[Equity_df['EQUITY'] == 'Retained earnings'].loc[:, str(last_year+1): ].to_dict(orient='records')[0])
            
            try:
                del data['EQUITY']
            except:
                pass
                
    return Equity_df, balanceSheet_dict