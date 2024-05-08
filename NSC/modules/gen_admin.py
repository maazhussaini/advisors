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

def key_indicators(df_is_crnt, df_ga):
    
    # KEY INDICATORS
    
    df_dict = df_is_crnt.to_dict(orient="records")
    ga_dict = df_ga.to_dict(orient="records")
    
    rev_dict = [rev for rev in df_dict if rev["components"] == "revenue"][0]
    total_dict = [ga for ga in ga_dict if ga["G&A"] == "total"][0]
    
    temp_dict = [{"KEY INDICATORS": "Annual growth %"}]
    value = 0
    for index, key in enumerate(total_dict):
        
        if key == "G&A":
            continue
        
        try:
            value = total_dict[str(int(key)-1)]
            value = total_dict[key] / (value - 1)
        except:
            pass
        
        temp_dict[0][key] = value
    
    temp_dict.append({"KEY INDICATORS" : "% of revenue"})
    
    for index, key in enumerate(total_dict):
        
        if key == "G&A":
            continue
        
        try:
            value = total_dict[key] / rev_dict[key]
        except:
            print(key)
        
        temp_dict[1][key] = value
        
    key_indicator = pd.DataFrame(temp_dict)
    return key_indicator.to_json(orient="records")
    
def annual_growth(df_ga):
    # ANNUAL GROWTH
    # ga_dict = df_ga.to_dict(orient="records")
    ga_dict = df_ga
    temp_lst = []
    for index in ga_dict:
        temp_dict = {}
        value = 0
        for ind, key in enumerate(index):
            
            try:
                value = index[str(int(key)-1)]
                value = index[key] / (value - 1)
                temp_dict[key] = value
            except:
                try:
                    int(key)
                    temp_dict[key] = value
                except:
                    temp_dict[key] = index[key]
            
        temp_lst.append(temp_dict)
    
    df_annual = pd.DataFrame(temp_lst)
    
    return df_annual.to_json(orient="records")

def per_of_rev(df_ga, df_is_crnt):
    # % OF REVENUE
    
    df_dict = df_is_crnt
    ga_dict = df_ga
    rev_dict = [rev for rev in df_dict if rev["components"] == "revenue"][0]

    temp_lst = []
    for index in ga_dict:
        temp_dict = {}
        for ind, key in enumerate(index):
            
            try:
                temp_dict[key] = index[key] / rev_dict[key]
            except:
                temp_dict[key] = index[key]
            
        temp_lst.append(temp_dict)
        
    df_per_of_rev = pd.DataFrame(temp_lst)
    
    return df_per_of_rev.to_json(orient="records")

