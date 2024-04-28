import pandas as pd

def get_sm_assumptions():
    
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption, sheet_name="S&M EXPENSES")
    
    df_assumption.fillna(0, inplace=True)
    
    assumption_json = df_assumption.to_json(orient = 'records')
    return assumption_json


def sm_expenses(assumption_dict: dict, df_sm: pd.DataFrame, last_year: int) -> pd.DataFrame:
    
    ga_dict = df_sm.to_dict(orient='records')
    
    for assumption in assumption_dict:
        for index, ga in enumerate(ga_dict):
            if ga['SELLING & MARKETING EXPENSES'] == assumption['COMPONENT']:
                for key, value in assumption.items():
                    if key.isdigit():
                        if int(key) > last_year:
                            if assumption['BASE'] == 'YoY %':
                                try:
                                    ga[key] = ga[str(int(key) - 1)] * (1 + value)
                                except:
                                    ga[key] = ga[int(key) - 1] * (1 + value)
                                
    
    df_sm = pd.DataFrame(ga_dict)
    df_sm.fillna(0, inplace=True)
    
    return df_sm