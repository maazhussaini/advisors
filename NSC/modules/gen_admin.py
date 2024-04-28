import pandas as pd

def get_assumption():
    
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption, sheet_name="General and administrative exp")
    
    df_assumption.fillna(0, inplace=True)
    
    assumption_json = df_assumption.to_json(orient = 'records')
    return assumption_json


def general_admin_exp(assumption_dict: dict, df_ga: pd.DataFrame, last_year: int) -> pd.DataFrame:
    ga_dict = df_ga.to_dict(orient='records')
    
    for assumption in assumption_dict:
        for index, ga in enumerate(ga_dict):
            if ga['GENERAL & ADMINISTRATIVE EXPENSES'] == assumption['COMPONENT']:
                for key, value in assumption.items():
                    if key.isdigit():
                        if int(key) > last_year:
                            if assumption['BASE'] == 'YoY %':
                                try:
                                    ga[key] = ga[str(int(key) - 1)] * (1 + value)
                                except:
                                    ga[key] = ga[int(key) - 1] * (1 + value)
                                
    
    df_ga = pd.DataFrame(ga_dict)
    df_ga.fillna(0, inplace=True)
    
    return df_ga