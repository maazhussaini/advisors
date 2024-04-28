from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import numpy as np
import json
from modules.is_current import isCurrent
from modules.wc import working_capital_indicators, working_capital
from modules.bs import working_Capital, debt_checking, FA_checking, equity_checking
from modules.gen_admin import get_assumption, general_admin_exp

app = Flask(__name__)


def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    try:
        df = df.drop('Note', axis=1)
    except:
        pass
    return df

def process_assumption_sheet(df):
    
    try:
        df = df.drop('Select', axis=1)
        df = df.drop('BASE', axis=1)
    except:
        pass
    df = df.transpose().reset_index()
    
    new_header = df.iloc[-1].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[:-1]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    return df

def process_sheet(df):
    """
        Tranposing
    """
    
    df = df.transpose().reset_index()
    
    new_header = df.iloc[0].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    """
        END Tranposing
    """
    return df

def tranposing(df, column_name):
    df['year'] = df['year'].astype('str')
    df = df.rename(columns={df.columns[0]: column_name})
    
    # Now, transpose the DataFrame
    df = df.transpose().reset_index()

    new_header = df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)
        
    df = df[1:]
    df.columns = new_header
    df.set_index(df.columns[0], inplace=True)
    df = df.reset_index()
    
    return df

@app.route('/assumption_data', methods=['GET'])
def read_assumption_file(sheet_name='Sheet1'):
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption, sheet_name=sheet_name)
    
    new_column_position = 2  # Position after 'A'
    new_column_name = 'Select'
    new_column_values = True

    df_assumption.insert(loc=new_column_position, column=new_column_name, value=new_column_values)

    df_assumption['Select'] = True
    
    return df_assumption.to_json(orient='records')

@app.route('/is_crnt', methods = ['POST'])
def is_crnt():
    
    # df_assumption = read_assumption_file()
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
        
        if not df_assumption.empty:
            predicted_year = 8
                
        
        predicted_year = int(predicted_year)
        df_assumption = process_assumption_sheet(df_assumption)
        
        df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
        
        df_fs = process_sheet(df_fs)
        
        df = isCurrent(df_fs=df_fs, df_assumption=df_assumption, predicted_year=predicted_year)
        
        df = tranposing(df, 'components')
        
        df = df.to_json(orient='records')
        
        return df, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  

@app.route('/workingCapitalIndicators', methods=['POST'])
def workingCapitalIndicators(prediction_year = 4):

    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        
        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        
        is_crnt_df = is_crnt_df.reset_index()
        
        key_indicators_df = working_capital_indicators(is_crnt_df, workingCapital_df)
        key_indicators_df = key_indicators_df.to_json(orient='records')
        return key_indicators_df

@app.route('/workingCapital', methods=['POST'])
def workingCapital(prediction_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        key_indicators_df = data.get('key_indicators_df', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
            key_indicators_df = pd.DataFrame(key_indicators_df)
            
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        is_crnt_df = is_crnt_df.reset_index()
        
        workingCapital_predicted_df = working_capital(workingCapital_df, key_indicators_df, is_crnt_df, prediction_year)
        
        workingCapital_predicted_df = workingCapital_predicted_df.to_json(orient='records')
        
        return workingCapital_predicted_df
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/debt', methods=['GET'])
def debt(predicted_year = 4):
    
    debt_df = read_excel_file(file_path='', sheet_name='DEBT')
    
    last_year = int(debt_df.columns.to_list()[-1])
    
    transformed_debt_df = process_sheet(debt_df)
    
    debt_dict = transformed_debt_df.to_dict(orient='records')
    
    value = debt_dict[-1]['closing balance']
    temp_dict = {}
    temp_list = []
    
    for i in range(1, predicted_year+1):
        temp_dict['year'] = last_year+i
        temp_dict['opening balance'] = value
        temp_dict['loan proceeds - net'] = 0
        temp_dict['repayments - net'] = 0
        temp_dict['closing balance'] = temp_dict['opening balance'] + temp_dict['loan proceeds - net'] + temp_dict['repayments - net']
        value = value
        
        temp_list.append(temp_dict)
        temp_dict = {}
    
    temp_df = pd.DataFrame(temp_list)
    temp_df['year'] = temp_df['year'].astype('str')
    temp_df = temp_df.rename(columns={temp_df.columns[0]: 'DEBT'})
    
    # Now, transpose the DataFrame
    temp_df = temp_df.transpose().reset_index()

    new_header = temp_df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)

    # Assuming temp_df is your DataFrame and you want to remove the first row and reset the index
    temp_df = temp_df.iloc[1:].reset_index(drop=True)

    temp_df.columns = new_header
    
    temp_df.drop('DEBT', axis=1, inplace=True)
    
    debt_df = pd.concat([debt_df, temp_df], axis=1)
    
    debt_df = debt_df.to_json(orient='records')
    
    return debt_df

@app.route('/fixedAsset', methods=['POST'])
def fixedAsset(predicted_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
    
        fixedAsset_df = read_excel_file(file_path='', sheet_name='FA')
        
        transformed_fixedAsset_df = process_sheet(fixedAsset_df)
        
        fixedAsset_dict = transformed_fixedAsset_df.to_dict(orient='records')
        
        last_year = fixedAsset_df.columns.to_list()[-1]
        
        value_openingBalance = fixedAsset_dict[-1]['closing balance - nbv']
        
        temp_list = []
        for i in range(1, predicted_year+1):
            temp_dict = {}
            temp_dict['year'] = last_year + i
            temp_dict['opening balance - nbv'] = value_openingBalance
            value_2 = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * value_openingBalance
            temp_dict['additions during the year - net'] = value_2
            value_depreciation = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * (value_openingBalance + (value_2 * 6 / 12))
            temp_dict['Depreciation charge for the year'] = value_depreciation
            temp_dict['Closing Balance - NBV'] = value_openingBalance + value_2 + value_depreciation
            
            temp_list.append(temp_dict)
            
        temp_df = pd.DataFrame(temp_list)
        temp_df = tranposing(temp_df, 'FA')
        # temp_df = temp_df.reset_index()
        temp_df.drop('FA', axis=1, inplace=True)
        
        fixedAsset_df = pd.concat([fixedAsset_df, temp_df], axis=1)
        
        fixedAsset_df = fixedAsset_df.to_json(orient='records')
        
        return fixedAsset_df

@app.route('/Equity', methods=['GET'])
def Equity(predicted_year = 4):
    
    Equity_df = read_excel_file(file_path='', sheet_name='EQUITY')
    
    transformed_Equity_df = process_sheet(Equity_df)
    
    last_year = Equity_df.columns.to_list()[-1]
    Equity_dict = transformed_Equity_df.to_dict(orient = 'records')
    
    closingBalance_shareCapital_value = Equity_dict[-1]['closing balance - share capital']
    
    openingBalance_statutoryReserve_value = Equity_dict[-1]['closing balance - statutory reserve']
    
    openingBalance_retainedEarnings_value = Equity_dict[-1]['closing balance - retained earnings']
    
    temp_list = []
    for i in range(1, predicted_year+1):
        temp_dict = {}
        
        temp_dict['year'] = last_year + i
        
        """
            SHARE CAPITAL OPENING
        """
        
        temp_dict['opening balance - share capital'] = closingBalance_shareCapital_value
        temp_dict['capital increase/decrease'] = 0
        temp_dict['closing balance - share capital'] = temp_dict['opening balance - share capital'] + temp_dict['capital increase/decrease']
        
        closingBalance_shareCapital_value = temp_dict['closing balance - share capital']
        
        """
            SHARE CAPITAL CLOSING
        """
        
        """
            STATUTORY RESERVE OPENING
        """
        temp_dict['opening balance - statutory reserve'] = openingBalance_statutoryReserve_value
        temp_dict['transfer for the year'] = 0
        temp_dict['closing balance - statutory reserve'] = temp_dict['opening balance - statutory reserve'] + temp_dict['transfer for the year']
        
        openingBalance_statutoryReserve_value = temp_dict['closing balance - statutory reserve']
        
        """
            STATUTORY RESERVE CLOSING
        """
        
        """
            RETAINED EARNING OPENING
        """
        temp_dict['opening balance - retained earnings'] = openingBalance_retainedEarnings_value
        temp_dict['net income'] = 0 #should be drived from IS_CRNT
        temp_dict['dividends & oci movement'] = 0
        temp_dict['statutory reserve transfer'] = 0
        temp_dict['closing balance - retained earnings'] = temp_dict['opening balance - retained earnings'] + temp_dict['net income'] + temp_dict['dividends & oci movement'] + temp_dict['statutory reserve transfer']
        
        openingBalance_retainedEarnings_value = temp_dict['closing balance - retained earnings']
        """
            RETAINED EARNING CLOSING
        """
        
        temp_dict['share capital'] = temp_dict['closing balance - share capital']
        temp_dict['statutory reserve'] = temp_dict['closing balance - statutory reserve']
        temp_dict['retained earnings'] = temp_dict['closing balance - retained earnings']
        temp_dict['closing balance - equity'] = temp_dict['share capital'] + temp_dict['statutory reserve'] + temp_dict['retained earnings']
        
        temp_list.append(temp_dict)
        
    temp_df = pd.DataFrame(temp_list)
    columnList = transformed_Equity_df.columns.to_list()
    
    temp_df = temp_df[columnList]
    temp_df = tranposing(temp_df, 'EQUITY')
    
    temp_df.drop('EQUITY', axis=1, inplace=True)
    
    Equity_df = pd.concat([Equity_df, temp_df], axis=1)
    
    Equity_df = Equity_df.to_json(orient='records')
    
    return Equity_df

@app.route('/BalanceSheet', methods=['POST'])
def balanceSheet():
    
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        workingCapital_df = data.get('workingCapital', None)
        debt_df = data.get('debt', None)
        fixedAsset_df = data.get('fixedAsset', None)
        Equity_df = data.get('equity', None)
        
        if (workingCapital_df is not None) | (debt_df is not None) | (fixedAsset_df is not None) | (Equity_df is not None):
            # Process the df_assumption here
            try:
                workingCapital_df = pd.DataFrame(workingCapital_df)
                debt_df = pd.DataFrame(debt_df)
                fixedAsset_df = pd.DataFrame(fixedAsset_df)
                Equity_df = pd.DataFrame(Equity_df)
            except:
                workingCapital_df = pd.read_json(workingCapital_df)
                debt_df = pd.read_json(debt_df)
                fixedAsset_df = pd.read_json(fixedAsset_df)
                Equity_df = pd.read_json(Equity_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
            
        balanceSheet_df = read_excel_file(file_path='', sheet_name='BALANCESHEET')
        
        balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
        last_year = balanceSheet_df.columns.to_list()[-1]
        
        workingCapital_predicted_dict, balanceSheet_dict = working_Capital(balanceSheet_df, workingCapital_df, last_year)    
        
        """
            Working with Debt
        """
        
        debt_df, balanceSheet_dict = debt_checking(debt_df, balanceSheet_dict, last_year)
        
        """
            Working on Fixed Assets
        """
        
        fixedAsset_df, balanceSheet_dict = FA_checking(fixedAsset_df, balanceSheet_dict, last_year)
        
        """
            Working on Equity
        """
        
        Equity_df, balanceSheet_dict = equity_checking(Equity_df, balanceSheet_dict, last_year)
        
        updated_balanceSheet_df = pd.DataFrame(balanceSheet_dict)
        
        """
        
        """
        
        # Convert all column names to string
        updated_balanceSheet_df.columns = updated_balanceSheet_df.columns.astype(str)

        # Rearranging columns based on data type
        # Categorical and numerical identification
        categorical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype == object]
        numerical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype != object]

        # Ensuring specific order for year columns by checking if column names are all digits
        year_cols = [col for col in numerical_cols if col.isdigit()]
        other_numerical_cols = [col for col in numerical_cols if not col.isdigit()]

        # Define the specific order requested: [name, age, city, salary, years...]
        new_order = categorical_cols + other_numerical_cols + sorted(year_cols)
        
        # Rearrange the DataFrame according to the new order
        updated_balanceSheet_df = updated_balanceSheet_df.reindex(columns=new_order)
        
        temp_balanceSheet_df = process_sheet(updated_balanceSheet_df)
        
        temp_balanceSheet_dict = temp_balanceSheet_df.to_dict(orient = 'records')
        
        for index, bs_data in enumerate(temp_balanceSheet_dict):
            
            try:
                if int(bs_data['year']) > last_year:
                    bs_data['current assets'] = bs_data['trade receivables'] + bs_data['due from related parties'] + bs_data['inventories'] + bs_data['prepayments and other receivables']
                    bs_data['current liabilities'] = bs_data['short-term borrowings'] + bs_data['trade payables'] + bs_data['accrued expenses and other liabilities'] + bs_data['due to related parties'] + bs_data['zakat payable']
                    
                    bs_data['cash and cash equivalents'] = bs_data['current liabilities'] - bs_data['current assets']
                    bs_data['investments at fair value through profit or loss'] = 0
                    bs_data['equity accounted investment'] = 0
                    
                    if index != 0 and bs_data['other receivables'] != 0:
                        
                        bs_data['other receivables'] = temp_balanceSheet_dict[index - 1]['other receivables']
                    
                    bs_data['non-current assets'] = bs_data['property and equipment'] + bs_data['investments at fair value through profit or loss'] + bs_data['equity accounted investment'] + bs_data['other receivables']
                    bs_data['total assets'] = bs_data['current assets'] + bs_data['non-current assets']
                    
                    bs_data['employee termination benefits'] = temp_balanceSheet_dict[index - 1]['employee termination benefits'] # multiply by IS_CRNT value
                    bs_data['due to related parties(current liabilities)'] = 0
                    bs_data['non-current liabilities'] = bs_data['employee termination benefits'] + bs_data['due to related parties(current liabilities)']
                    
                    bs_data["shareholders' equity"] = bs_data['share capital'] + bs_data['statutory reserve'] + bs_data['retained earnings']
                    
                    bs_data['total liabilities & equity'] = bs_data['current liabilities'] + bs_data['non-current assets'] + bs_data["shareholders' equity"]
            except:
                pass
                
            temp_balanceSheet_df = pd.DataFrame(temp_balanceSheet_dict)
            temp_balanceSheet_df = tranposing(df=temp_balanceSheet_df, column_name="BALANCE SHEET")
            
            temp_balanceSheet_df = temp_balanceSheet_df.to_json(orient='records')
        
        return temp_balanceSheet_df

@app.route('/ga_assumption', methods=['GET'])
def get_ga_assumption():
    
    return get_assumption(), 200

@app.route('/g_a', methods=['POST'])
def GandA():
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        assumption_dict = data.get('df_assumption', None)
        
        df_ga = read_excel_file(file_path='', sheet_name='General and administrative exp')
    
        temp_ga = process_sheet(df_ga)
        
        year_ga = temp_ga['year'].to_list()
        last_year = year_ga[-1]
        
        df_ga = general_admin_exp(assumption_dict, df_ga, last_year)
        ga_json = df_ga.to_json(orient='records')
        return ga_json, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import numpy as np
import json
from modules.is_current import isCurrent
from modules.wc import working_capital_indicators, working_capital
from modules.bs import working_Capital, debt_checking, FA_checking, equity_checking
from modules.gen_admin import get_assumption, general_admin_exp

app = Flask(__name__)


def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    try:
        df = df.drop('Note', axis=1)
    except:
        pass
    return df

def process_assumption_sheet(df):
    
    try:
        df = df.drop('Select', axis=1)
        df = df.drop('BASE', axis=1)
    except:
        pass
    df = df.transpose().reset_index()
    
    new_header = df.iloc[-1].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[:-1]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    return df

def process_sheet(df):
    """
        Tranposing
    """
    
    df = df.transpose().reset_index()
    
    new_header = df.iloc[0].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    """
        END Tranposing
    """
    return df

def tranposing(df, column_name):
    df['year'] = df['year'].astype('str')
    df = df.rename(columns={df.columns[0]: column_name})
    
    # Now, transpose the DataFrame
    df = df.transpose().reset_index()

    new_header = df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)
        
    df = df[1:]
    df.columns = new_header
    df.set_index(df.columns[0], inplace=True)
    df = df.reset_index()
    
    return df

@app.route('/assumption_data', methods=['GET'])
def read_assumption_file(sheet_name='Sheet1'):
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption, sheet_name=sheet_name)
    
    new_column_position = 2  # Position after 'A'
    new_column_name = 'Select'
    new_column_values = True

    df_assumption.insert(loc=new_column_position, column=new_column_name, value=new_column_values)

    df_assumption['Select'] = True
    
    return df_assumption.to_json(orient='records')

@app.route('/is_crnt', methods = ['POST'])
def is_crnt():
    
    # df_assumption = read_assumption_file()
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
        
        if not df_assumption.empty:
            predicted_year = 8
                
        
        predicted_year = int(predicted_year)
        df_assumption = process_assumption_sheet(df_assumption)
        
        df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
        
        df_fs = process_sheet(df_fs)
        
        df = isCurrent(df_fs=df_fs, df_assumption=df_assumption, predicted_year=predicted_year)
        
        df = tranposing(df, 'components')
        
        df = df.to_json(orient='records')
        
        return df, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  

@app.route('/workingCapitalIndicators', methods=['POST'])
def workingCapitalIndicators(prediction_year = 4):

    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        
        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        
        is_crnt_df = is_crnt_df.reset_index()
        
        key_indicators_df = working_capital_indicators(is_crnt_df, workingCapital_df)
        key_indicators_df = key_indicators_df.to_json(orient='records')
        return key_indicators_df

@app.route('/workingCapital', methods=['POST'])
def workingCapital(prediction_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        key_indicators_df = data.get('key_indicators_df', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
            key_indicators_df = pd.DataFrame(key_indicators_df)
            
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        is_crnt_df = is_crnt_df.reset_index()
        
        workingCapital_predicted_df = working_capital(workingCapital_df, key_indicators_df, is_crnt_df, prediction_year)
        
        workingCapital_predicted_df = workingCapital_predicted_df.to_json(orient='records')
        
        return workingCapital_predicted_df
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/debt', methods=['GET'])
def debt(predicted_year = 4):
    
    debt_df = read_excel_file(file_path='', sheet_name='DEBT')
    
    last_year = int(debt_df.columns.to_list()[-1])
    
    transformed_debt_df = process_sheet(debt_df)
    
    debt_dict = transformed_debt_df.to_dict(orient='records')
    
    value = debt_dict[-1]['closing balance']
    temp_dict = {}
    temp_list = []
    
    for i in range(1, predicted_year+1):
        temp_dict['year'] = last_year+i
        temp_dict['opening balance'] = value
        temp_dict['loan proceeds - net'] = 0
        temp_dict['repayments - net'] = 0
        temp_dict['closing balance'] = temp_dict['opening balance'] + temp_dict['loan proceeds - net'] + temp_dict['repayments - net']
        value = value
        
        temp_list.append(temp_dict)
        temp_dict = {}
    
    temp_df = pd.DataFrame(temp_list)
    temp_df['year'] = temp_df['year'].astype('str')
    temp_df = temp_df.rename(columns={temp_df.columns[0]: 'DEBT'})
    
    # Now, transpose the DataFrame
    temp_df = temp_df.transpose().reset_index()

    new_header = temp_df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)

    # Assuming temp_df is your DataFrame and you want to remove the first row and reset the index
    temp_df = temp_df.iloc[1:].reset_index(drop=True)

    temp_df.columns = new_header
    
    temp_df.drop('DEBT', axis=1, inplace=True)
    
    debt_df = pd.concat([debt_df, temp_df], axis=1)
    
    debt_df = debt_df.to_json(orient='records')
    
    return debt_df

@app.route('/fixedAsset', methods=['POST'])
def fixedAsset(predicted_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
    
        fixedAsset_df = read_excel_file(file_path='', sheet_name='FA')
        
        transformed_fixedAsset_df = process_sheet(fixedAsset_df)
        
        fixedAsset_dict = transformed_fixedAsset_df.to_dict(orient='records')
        
        last_year = fixedAsset_df.columns.to_list()[-1]
        
        value_openingBalance = fixedAsset_dict[-1]['closing balance - nbv']
        
        temp_list = []
        for i in range(1, predicted_year+1):
            temp_dict = {}
            temp_dict['year'] = last_year + i
            temp_dict['opening balance - nbv'] = value_openingBalance
            value_2 = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * value_openingBalance
            temp_dict['additions during the year - net'] = value_2
            value_depreciation = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * (value_openingBalance + (value_2 * 6 / 12))
            temp_dict['Depreciation charge for the year'] = value_depreciation
            temp_dict['Closing Balance - NBV'] = value_openingBalance + value_2 + value_depreciation
            
            temp_list.append(temp_dict)
            
        temp_df = pd.DataFrame(temp_list)
        temp_df = tranposing(temp_df, 'FA')
        # temp_df = temp_df.reset_index()
        temp_df.drop('FA', axis=1, inplace=True)
        
        fixedAsset_df = pd.concat([fixedAsset_df, temp_df], axis=1)
        
        fixedAsset_df = fixedAsset_df.to_json(orient='records')
        
        return fixedAsset_df

@app.route('/Equity', methods=['GET'])
def Equity(predicted_year = 4):
    
    Equity_df = read_excel_file(file_path='', sheet_name='EQUITY')
    
    transformed_Equity_df = process_sheet(Equity_df)
    
    last_year = Equity_df.columns.to_list()[-1]
    Equity_dict = transformed_Equity_df.to_dict(orient = 'records')
    
    closingBalance_shareCapital_value = Equity_dict[-1]['closing balance - share capital']
    
    openingBalance_statutoryReserve_value = Equity_dict[-1]['closing balance - statutory reserve']
    
    openingBalance_retainedEarnings_value = Equity_dict[-1]['closing balance - retained earnings']
    
    temp_list = []
    for i in range(1, predicted_year+1):
        temp_dict = {}
        
        temp_dict['year'] = last_year + i
        
        """
            SHARE CAPITAL OPENING
        """
        
        temp_dict['opening balance - share capital'] = closingBalance_shareCapital_value
        temp_dict['capital increase/decrease'] = 0
        temp_dict['closing balance - share capital'] = temp_dict['opening balance - share capital'] + temp_dict['capital increase/decrease']
        
        closingBalance_shareCapital_value = temp_dict['closing balance - share capital']
        
        """
            SHARE CAPITAL CLOSING
        """
        
        """
            STATUTORY RESERVE OPENING
        """
        temp_dict['opening balance - statutory reserve'] = openingBalance_statutoryReserve_value
        temp_dict['transfer for the year'] = 0
        temp_dict['closing balance - statutory reserve'] = temp_dict['opening balance - statutory reserve'] + temp_dict['transfer for the year']
        
        openingBalance_statutoryReserve_value = temp_dict['closing balance - statutory reserve']
        
        """
            STATUTORY RESERVE CLOSING
        """
        
        """
            RETAINED EARNING OPENING
        """
        temp_dict['opening balance - retained earnings'] = openingBalance_retainedEarnings_value
        temp_dict['net income'] = 0 #should be drived from IS_CRNT
        temp_dict['dividends & oci movement'] = 0
        temp_dict['statutory reserve transfer'] = 0
        temp_dict['closing balance - retained earnings'] = temp_dict['opening balance - retained earnings'] + temp_dict['net income'] + temp_dict['dividends & oci movement'] + temp_dict['statutory reserve transfer']
        
        openingBalance_retainedEarnings_value = temp_dict['closing balance - retained earnings']
        """
            RETAINED EARNING CLOSING
        """
        
        temp_dict['share capital'] = temp_dict['closing balance - share capital']
        temp_dict['statutory reserve'] = temp_dict['closing balance - statutory reserve']
        temp_dict['retained earnings'] = temp_dict['closing balance - retained earnings']
        temp_dict['closing balance - equity'] = temp_dict['share capital'] + temp_dict['statutory reserve'] + temp_dict['retained earnings']
        
        temp_list.append(temp_dict)
        
    temp_df = pd.DataFrame(temp_list)
    columnList = transformed_Equity_df.columns.to_list()
    
    temp_df = temp_df[columnList]
    temp_df = tranposing(temp_df, 'EQUITY')
    
    temp_df.drop('EQUITY', axis=1, inplace=True)
    
    Equity_df = pd.concat([Equity_df, temp_df], axis=1)
    
    Equity_df = Equity_df.to_json(orient='records')
    
    return Equity_df

@app.route('/BalanceSheet', methods=['POST'])
def balanceSheet():
    
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        workingCapital_df = data.get('workingCapital', None)
        debt_df = data.get('debt', None)
        fixedAsset_df = data.get('fixedAsset', None)
        Equity_df = data.get('equity', None)
        
        if (workingCapital_df is not None) | (debt_df is not None) | (fixedAsset_df is not None) | (Equity_df is not None):
            # Process the df_assumption here
            try:
                workingCapital_df = pd.DataFrame(workingCapital_df)
                debt_df = pd.DataFrame(debt_df)
                fixedAsset_df = pd.DataFrame(fixedAsset_df)
                Equity_df = pd.DataFrame(Equity_df)
            except:
                workingCapital_df = pd.read_json(workingCapital_df)
                debt_df = pd.read_json(debt_df)
                fixedAsset_df = pd.read_json(fixedAsset_df)
                Equity_df = pd.read_json(Equity_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
            
        balanceSheet_df = read_excel_file(file_path='', sheet_name='BALANCESHEET')
        
        balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
        last_year = balanceSheet_df.columns.to_list()[-1]
        
        workingCapital_predicted_dict, balanceSheet_dict = working_Capital(balanceSheet_df, workingCapital_df, last_year)    
        
        """
            Working with Debt
        """
        
        debt_df, balanceSheet_dict = debt_checking(debt_df, balanceSheet_dict, last_year)
        
        """
            Working on Fixed Assets
        """
        
        fixedAsset_df, balanceSheet_dict = FA_checking(fixedAsset_df, balanceSheet_dict, last_year)
        
        """
            Working on Equity
        """
        
        Equity_df, balanceSheet_dict = equity_checking(Equity_df, balanceSheet_dict, last_year)
        
        updated_balanceSheet_df = pd.DataFrame(balanceSheet_dict)
        
        """
        
        """
        
        # Convert all column names to string
        updated_balanceSheet_df.columns = updated_balanceSheet_df.columns.astype(str)

        # Rearranging columns based on data type
        # Categorical and numerical identification
        categorical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype == object]
        numerical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype != object]

        # Ensuring specific order for year columns by checking if column names are all digits
        year_cols = [col for col in numerical_cols if col.isdigit()]
        other_numerical_cols = [col for col in numerical_cols if not col.isdigit()]

        # Define the specific order requested: [name, age, city, salary, years...]
        new_order = categorical_cols + other_numerical_cols + sorted(year_cols)
        
        # Rearrange the DataFrame according to the new order
        updated_balanceSheet_df = updated_balanceSheet_df.reindex(columns=new_order)
        
        temp_balanceSheet_df = process_sheet(updated_balanceSheet_df)
        
        temp_balanceSheet_dict = temp_balanceSheet_df.to_dict(orient = 'records')
        
        for index, bs_data in enumerate(temp_balanceSheet_dict):
            
            try:
                if int(bs_data['year']) > last_year:
                    bs_data['current assets'] = bs_data['trade receivables'] + bs_data['due from related parties'] + bs_data['inventories'] + bs_data['prepayments and other receivables']
                    bs_data['current liabilities'] = bs_data['short-term borrowings'] + bs_data['trade payables'] + bs_data['accrued expenses and other liabilities'] + bs_data['due to related parties'] + bs_data['zakat payable']
                    
                    bs_data['cash and cash equivalents'] = bs_data['current liabilities'] - bs_data['current assets']
                    bs_data['investments at fair value through profit or loss'] = 0
                    bs_data['equity accounted investment'] = 0
                    
                    if index != 0 and bs_data['other receivables'] != 0:
                        
                        bs_data['other receivables'] = temp_balanceSheet_dict[index - 1]['other receivables']
                    
                    bs_data['non-current assets'] = bs_data['property and equipment'] + bs_data['investments at fair value through profit or loss'] + bs_data['equity accounted investment'] + bs_data['other receivables']
                    bs_data['total assets'] = bs_data['current assets'] + bs_data['non-current assets']
                    
                    bs_data['employee termination benefits'] = temp_balanceSheet_dict[index - 1]['employee termination benefits'] # multiply by IS_CRNT value
                    bs_data['due to related parties(current liabilities)'] = 0
                    bs_data['non-current liabilities'] = bs_data['employee termination benefits'] + bs_data['due to related parties(current liabilities)']
                    
                    bs_data["shareholders' equity"] = bs_data['share capital'] + bs_data['statutory reserve'] + bs_data['retained earnings']
                    
                    bs_data['total liabilities & equity'] = bs_data['current liabilities'] + bs_data['non-current assets'] + bs_data["shareholders' equity"]
            except:
                pass
                
            temp_balanceSheet_df = pd.DataFrame(temp_balanceSheet_dict)
            temp_balanceSheet_df = tranposing(df=temp_balanceSheet_df, column_name="BALANCE SHEET")
            
            temp_balanceSheet_df = temp_balanceSheet_df.to_json(orient='records')
        
        return temp_balanceSheet_df

@app.route('/ga_assumption', methods=['GET'])
def get_ga_assumption():
    
    return get_assumption(), 200

@app.route('/g_a', methods=['POST'])
def GandA():
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        assumption_dict = data.get('df_assumption', None)
        
        df_ga = read_excel_file(file_path='', sheet_name='General and administrative exp')
    
        temp_ga = process_sheet(df_ga)
        
        year_ga = temp_ga['year'].to_list()
        last_year = year_ga[-1]
        
        df_ga = general_admin_exp(assumption_dict, df_ga, last_year)
        ga_json = df_ga.to_json(orient='records')
        return ga_json, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import numpy as np
import json
from modules.is_current import isCurrent
from modules.wc import working_capital_indicators, working_capital
from modules.bs import working_Capital, debt_checking, FA_checking, equity_checking
from modules.gen_admin import get_assumption, general_admin_exp

app = Flask(__name__)


def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    try:
        df = df.drop('Note', axis=1)
    except:
        pass
    return df

def process_assumption_sheet(df):
    
    try:
        df = df.drop('Select', axis=1)
        df = df.drop('BASE', axis=1)
    except:
        pass
    df = df.transpose().reset_index()
    
    new_header = df.iloc[-1].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[:-1]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    return df

def process_sheet(df):
    """
        Tranposing
    """
    
    df = df.transpose().reset_index()
    
    new_header = df.iloc[0].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    """
        END Tranposing
    """
    return df

def tranposing(df, column_name):
    df['year'] = df['year'].astype('str')
    df = df.rename(columns={df.columns[0]: column_name})
    
    # Now, transpose the DataFrame
    df = df.transpose().reset_index()

    new_header = df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)
        
    df = df[1:]
    df.columns = new_header
    df.set_index(df.columns[0], inplace=True)
    df = df.reset_index()
    
    return df

@app.route('/assumption_data', methods=['GET'])
def read_assumption_file(sheet_name='Sheet1'):
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption, sheet_name=sheet_name)
    
    new_column_position = 2  # Position after 'A'
    new_column_name = 'Select'
    new_column_values = True

    df_assumption.insert(loc=new_column_position, column=new_column_name, value=new_column_values)

    df_assumption['Select'] = True
    
    return df_assumption.to_json(orient='records')

@app.route('/is_crnt', methods = ['POST'])
def is_crnt():
    
    # df_assumption = read_assumption_file()
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
        
        if not df_assumption.empty:
            predicted_year = 8
                
        
        predicted_year = int(predicted_year)
        df_assumption = process_assumption_sheet(df_assumption)
        
        df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
        
        df_fs = process_sheet(df_fs)
        
        df = isCurrent(df_fs=df_fs, df_assumption=df_assumption, predicted_year=predicted_year)
        
        df = tranposing(df, 'components')
        
        df = df.to_json(orient='records')
        
        return df, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  

@app.route('/workingCapitalIndicators', methods=['POST'])
def workingCapitalIndicators(prediction_year = 4):

    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        
        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        
        is_crnt_df = is_crnt_df.reset_index()
        
        key_indicators_df = working_capital_indicators(is_crnt_df, workingCapital_df)
        key_indicators_df = key_indicators_df.to_json(orient='records')
        return key_indicators_df

@app.route('/workingCapital', methods=['POST'])
def workingCapital(prediction_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        key_indicators_df = data.get('key_indicators_df', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
            key_indicators_df = pd.DataFrame(key_indicators_df)
            
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        is_crnt_df = is_crnt_df.reset_index()
        
        workingCapital_predicted_df = working_capital(workingCapital_df, key_indicators_df, is_crnt_df, prediction_year)
        
        workingCapital_predicted_df = workingCapital_predicted_df.to_json(orient='records')
        
        return workingCapital_predicted_df
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/debt', methods=['GET'])
def debt(predicted_year = 4):
    
    debt_df = read_excel_file(file_path='', sheet_name='DEBT')
    
    last_year = int(debt_df.columns.to_list()[-1])
    
    transformed_debt_df = process_sheet(debt_df)
    
    debt_dict = transformed_debt_df.to_dict(orient='records')
    
    value = debt_dict[-1]['closing balance']
    temp_dict = {}
    temp_list = []
    
    for i in range(1, predicted_year+1):
        temp_dict['year'] = last_year+i
        temp_dict['opening balance'] = value
        temp_dict['loan proceeds - net'] = 0
        temp_dict['repayments - net'] = 0
        temp_dict['closing balance'] = temp_dict['opening balance'] + temp_dict['loan proceeds - net'] + temp_dict['repayments - net']
        value = value
        
        temp_list.append(temp_dict)
        temp_dict = {}
    
    temp_df = pd.DataFrame(temp_list)
    temp_df['year'] = temp_df['year'].astype('str')
    temp_df = temp_df.rename(columns={temp_df.columns[0]: 'DEBT'})
    
    # Now, transpose the DataFrame
    temp_df = temp_df.transpose().reset_index()

    new_header = temp_df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)

    # Assuming temp_df is your DataFrame and you want to remove the first row and reset the index
    temp_df = temp_df.iloc[1:].reset_index(drop=True)

    temp_df.columns = new_header
    
    temp_df.drop('DEBT', axis=1, inplace=True)
    
    debt_df = pd.concat([debt_df, temp_df], axis=1)
    
    debt_df = debt_df.to_json(orient='records')
    
    return debt_df

@app.route('/fixedAsset', methods=['POST'])
def fixedAsset(predicted_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
    
        fixedAsset_df = read_excel_file(file_path='', sheet_name='FA')
        
        transformed_fixedAsset_df = process_sheet(fixedAsset_df)
        
        fixedAsset_dict = transformed_fixedAsset_df.to_dict(orient='records')
        
        last_year = fixedAsset_df.columns.to_list()[-1]
        
        value_openingBalance = fixedAsset_dict[-1]['closing balance - nbv']
        
        temp_list = []
        for i in range(1, predicted_year+1):
            temp_dict = {}
            temp_dict['year'] = last_year + i
            temp_dict['opening balance - nbv'] = value_openingBalance
            value_2 = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * value_openingBalance
            temp_dict['additions during the year - net'] = value_2
            value_depreciation = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * (value_openingBalance + (value_2 * 6 / 12))
            temp_dict['Depreciation charge for the year'] = value_depreciation
            temp_dict['Closing Balance - NBV'] = value_openingBalance + value_2 + value_depreciation
            
            temp_list.append(temp_dict)
            
        temp_df = pd.DataFrame(temp_list)
        temp_df = tranposing(temp_df, 'FA')
        # temp_df = temp_df.reset_index()
        temp_df.drop('FA', axis=1, inplace=True)
        
        fixedAsset_df = pd.concat([fixedAsset_df, temp_df], axis=1)
        
        fixedAsset_df = fixedAsset_df.to_json(orient='records')
        
        return fixedAsset_df

@app.route('/Equity', methods=['GET'])
def Equity(predicted_year = 4):
    
    Equity_df = read_excel_file(file_path='', sheet_name='EQUITY')
    
    transformed_Equity_df = process_sheet(Equity_df)
    
    last_year = Equity_df.columns.to_list()[-1]
    Equity_dict = transformed_Equity_df.to_dict(orient = 'records')
    
    closingBalance_shareCapital_value = Equity_dict[-1]['closing balance - share capital']
    
    openingBalance_statutoryReserve_value = Equity_dict[-1]['closing balance - statutory reserve']
    
    openingBalance_retainedEarnings_value = Equity_dict[-1]['closing balance - retained earnings']
    
    temp_list = []
    for i in range(1, predicted_year+1):
        temp_dict = {}
        
        temp_dict['year'] = last_year + i
        
        """
            SHARE CAPITAL OPENING
        """
        
        temp_dict['opening balance - share capital'] = closingBalance_shareCapital_value
        temp_dict['capital increase/decrease'] = 0
        temp_dict['closing balance - share capital'] = temp_dict['opening balance - share capital'] + temp_dict['capital increase/decrease']
        
        closingBalance_shareCapital_value = temp_dict['closing balance - share capital']
        
        """
            SHARE CAPITAL CLOSING
        """
        
        """
            STATUTORY RESERVE OPENING
        """
        temp_dict['opening balance - statutory reserve'] = openingBalance_statutoryReserve_value
        temp_dict['transfer for the year'] = 0
        temp_dict['closing balance - statutory reserve'] = temp_dict['opening balance - statutory reserve'] + temp_dict['transfer for the year']
        
        openingBalance_statutoryReserve_value = temp_dict['closing balance - statutory reserve']
        
        """
            STATUTORY RESERVE CLOSING
        """
        
        """
            RETAINED EARNING OPENING
        """
        temp_dict['opening balance - retained earnings'] = openingBalance_retainedEarnings_value
        temp_dict['net income'] = 0 #should be drived from IS_CRNT
        temp_dict['dividends & oci movement'] = 0
        temp_dict['statutory reserve transfer'] = 0
        temp_dict['closing balance - retained earnings'] = temp_dict['opening balance - retained earnings'] + temp_dict['net income'] + temp_dict['dividends & oci movement'] + temp_dict['statutory reserve transfer']
        
        openingBalance_retainedEarnings_value = temp_dict['closing balance - retained earnings']
        """
            RETAINED EARNING CLOSING
        """
        
        temp_dict['share capital'] = temp_dict['closing balance - share capital']
        temp_dict['statutory reserve'] = temp_dict['closing balance - statutory reserve']
        temp_dict['retained earnings'] = temp_dict['closing balance - retained earnings']
        temp_dict['closing balance - equity'] = temp_dict['share capital'] + temp_dict['statutory reserve'] + temp_dict['retained earnings']
        
        temp_list.append(temp_dict)
        
    temp_df = pd.DataFrame(temp_list)
    columnList = transformed_Equity_df.columns.to_list()
    
    temp_df = temp_df[columnList]
    temp_df = tranposing(temp_df, 'EQUITY')
    
    temp_df.drop('EQUITY', axis=1, inplace=True)
    
    Equity_df = pd.concat([Equity_df, temp_df], axis=1)
    
    Equity_df = Equity_df.to_json(orient='records')
    
    return Equity_df

@app.route('/BalanceSheet', methods=['POST'])
def balanceSheet():
    
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        workingCapital_df = data.get('workingCapital', None)
        debt_df = data.get('debt', None)
        fixedAsset_df = data.get('fixedAsset', None)
        Equity_df = data.get('equity', None)
        
        if (workingCapital_df is not None) | (debt_df is not None) | (fixedAsset_df is not None) | (Equity_df is not None):
            # Process the df_assumption here
            try:
                workingCapital_df = pd.DataFrame(workingCapital_df)
                debt_df = pd.DataFrame(debt_df)
                fixedAsset_df = pd.DataFrame(fixedAsset_df)
                Equity_df = pd.DataFrame(Equity_df)
            except:
                workingCapital_df = pd.read_json(workingCapital_df)
                debt_df = pd.read_json(debt_df)
                fixedAsset_df = pd.read_json(fixedAsset_df)
                Equity_df = pd.read_json(Equity_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
            
        balanceSheet_df = read_excel_file(file_path='', sheet_name='BALANCESHEET')
        
        balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
        last_year = balanceSheet_df.columns.to_list()[-1]
        
        workingCapital_predicted_dict, balanceSheet_dict = working_Capital(balanceSheet_df, workingCapital_df, last_year)    
        
        """
            Working with Debt
        """
        
        debt_df, balanceSheet_dict = debt_checking(debt_df, balanceSheet_dict, last_year)
        
        """
            Working on Fixed Assets
        """
        
        fixedAsset_df, balanceSheet_dict = FA_checking(fixedAsset_df, balanceSheet_dict, last_year)
        
        """
            Working on Equity
        """
        
        Equity_df, balanceSheet_dict = equity_checking(Equity_df, balanceSheet_dict, last_year)
        
        updated_balanceSheet_df = pd.DataFrame(balanceSheet_dict)
        
        """
        
        """
        
        # Convert all column names to string
        updated_balanceSheet_df.columns = updated_balanceSheet_df.columns.astype(str)

        # Rearranging columns based on data type
        # Categorical and numerical identification
        categorical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype == object]
        numerical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype != object]

        # Ensuring specific order for year columns by checking if column names are all digits
        year_cols = [col for col in numerical_cols if col.isdigit()]
        other_numerical_cols = [col for col in numerical_cols if not col.isdigit()]

        # Define the specific order requested: [name, age, city, salary, years...]
        new_order = categorical_cols + other_numerical_cols + sorted(year_cols)
        
        # Rearrange the DataFrame according to the new order
        updated_balanceSheet_df = updated_balanceSheet_df.reindex(columns=new_order)
        
        temp_balanceSheet_df = process_sheet(updated_balanceSheet_df)
        
        temp_balanceSheet_dict = temp_balanceSheet_df.to_dict(orient = 'records')
        
        for index, bs_data in enumerate(temp_balanceSheet_dict):
            
            try:
                if int(bs_data['year']) > last_year:
                    bs_data['current assets'] = bs_data['trade receivables'] + bs_data['due from related parties'] + bs_data['inventories'] + bs_data['prepayments and other receivables']
                    bs_data['current liabilities'] = bs_data['short-term borrowings'] + bs_data['trade payables'] + bs_data['accrued expenses and other liabilities'] + bs_data['due to related parties'] + bs_data['zakat payable']
                    
                    bs_data['cash and cash equivalents'] = bs_data['current liabilities'] - bs_data['current assets']
                    bs_data['investments at fair value through profit or loss'] = 0
                    bs_data['equity accounted investment'] = 0
                    
                    if index != 0 and bs_data['other receivables'] != 0:
                        
                        bs_data['other receivables'] = temp_balanceSheet_dict[index - 1]['other receivables']
                    
                    bs_data['non-current assets'] = bs_data['property and equipment'] + bs_data['investments at fair value through profit or loss'] + bs_data['equity accounted investment'] + bs_data['other receivables']
                    bs_data['total assets'] = bs_data['current assets'] + bs_data['non-current assets']
                    
                    bs_data['employee termination benefits'] = temp_balanceSheet_dict[index - 1]['employee termination benefits'] # multiply by IS_CRNT value
                    bs_data['due to related parties(current liabilities)'] = 0
                    bs_data['non-current liabilities'] = bs_data['employee termination benefits'] + bs_data['due to related parties(current liabilities)']
                    
                    bs_data["shareholders' equity"] = bs_data['share capital'] + bs_data['statutory reserve'] + bs_data['retained earnings']
                    
                    bs_data['total liabilities & equity'] = bs_data['current liabilities'] + bs_data['non-current assets'] + bs_data["shareholders' equity"]
            except:
                pass
                
            temp_balanceSheet_df = pd.DataFrame(temp_balanceSheet_dict)
            temp_balanceSheet_df = tranposing(df=temp_balanceSheet_df, column_name="BALANCE SHEET")
            
            temp_balanceSheet_df = temp_balanceSheet_df.to_json(orient='records')
        
        return temp_balanceSheet_df

@app.route('/ga_assumption', methods=['GET'])
def get_ga_assumption():
    
    return get_assumption(), 200

@app.route('/g_a', methods=['POST'])
def GandA():
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        assumption_dict = data.get('df_assumption', None)
        
        df_ga = read_excel_file(file_path='', sheet_name='General and administrative exp')
    
        temp_ga = process_sheet(df_ga)
        
        year_ga = temp_ga['year'].to_list()
        last_year = year_ga[-1]
        
        df_ga = general_admin_exp(assumption_dict, df_ga, last_year)
        ga_json = df_ga.to_json(orient='records')
        return ga_json, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import numpy as np
import json
from modules.is_current import isCurrent
from modules.wc import working_capital_indicators, working_capital
from modules.bs import working_Capital, debt_checking, FA_checking, equity_checking
from modules.gen_admin import get_assumption, general_admin_exp

app = Flask(__name__)


def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    try:
        df = df.drop('Note', axis=1)
    except:
        pass
    return df

def process_assumption_sheet(df):
    
    try:
        df = df.drop('Select', axis=1)
        df = df.drop('BASE', axis=1)
    except:
        pass
    df = df.transpose().reset_index()
    
    new_header = df.iloc[-1].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[:-1]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    return df

def process_sheet(df):
    """
        Tranposing
    """
    
    df = df.transpose().reset_index()
    
    new_header = df.iloc[0].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    try:
        df['year'] = df['year'].astype('int')
    except:
        pass
    
    """
        END Tranposing
    """
    return df

def tranposing(df, column_name):
    df['year'] = df['year'].astype('str')
    df = df.rename(columns={df.columns[0]: column_name})
    
    # Now, transpose the DataFrame
    df = df.transpose().reset_index()

    new_header = df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)
        
    df = df[1:]
    df.columns = new_header
    df.set_index(df.columns[0], inplace=True)
    df = df.reset_index()
    
    return df

@app.route('/assumption_data', methods=['GET'])
def read_assumption_file(sheet_name='Sheet1'):
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption, sheet_name=sheet_name)
    
    new_column_position = 2  # Position after 'A'
    new_column_name = 'Select'
    new_column_values = True

    df_assumption.insert(loc=new_column_position, column=new_column_name, value=new_column_values)

    df_assumption['Select'] = True
    
    return df_assumption.to_json(orient='records')

@app.route('/is_crnt', methods = ['POST'])
def is_crnt():
    
    # df_assumption = read_assumption_file()
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
        
        if not df_assumption.empty:
            predicted_year = 8
                
        
        predicted_year = int(predicted_year)
        df_assumption = process_assumption_sheet(df_assumption)
        
        df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
        
        df_fs = process_sheet(df_fs)
        
        df = isCurrent(df_fs=df_fs, df_assumption=df_assumption, predicted_year=predicted_year)
        
        df = tranposing(df, 'components')
        
        df = df.to_json(orient='records')
        
        return df, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  

@app.route('/workingCapitalIndicators', methods=['POST'])
def workingCapitalIndicators(prediction_year = 4):

    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        
        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        
        is_crnt_df = is_crnt_df.reset_index()
        
        key_indicators_df = working_capital_indicators(is_crnt_df, workingCapital_df)
        key_indicators_df = key_indicators_df.to_json(orient='records')
        return key_indicators_df

@app.route('/workingCapital', methods=['POST'])
def workingCapital(prediction_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        is_crnt_df = data.get('is_crnt', None)
        key_indicators_df = data.get('key_indicators_df', None)
        
        if is_crnt_df is not None:
            # Process the df_assumption here
            is_crnt_df = pd.DataFrame(is_crnt_df)
            key_indicators_df = pd.DataFrame(key_indicators_df)
            
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing is_crnt data"}), 400
        
        try:
            is_crnt_df = pd.DataFrame(is_crnt_df)
        except:
            is_crnt_df = pd.read_json(is_crnt_df)

        workingCapital_df = read_excel_file(file_path='', sheet_name='WC')
        is_crnt_df = is_crnt_df.reset_index()
        
        workingCapital_predicted_df = working_capital(workingCapital_df, key_indicators_df, is_crnt_df, prediction_year)
        
        workingCapital_predicted_df = workingCapital_predicted_df.to_json(orient='records')
        
        return workingCapital_predicted_df
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/debt', methods=['GET'])
def debt(predicted_year = 4):
    
    debt_df = read_excel_file(file_path='', sheet_name='DEBT')
    
    last_year = int(debt_df.columns.to_list()[-1])
    
    transformed_debt_df = process_sheet(debt_df)
    
    debt_dict = transformed_debt_df.to_dict(orient='records')
    
    value = debt_dict[-1]['closing balance']
    temp_dict = {}
    temp_list = []
    
    for i in range(1, predicted_year+1):
        temp_dict['year'] = last_year+i
        temp_dict['opening balance'] = value
        temp_dict['loan proceeds - net'] = 0
        temp_dict['repayments - net'] = 0
        temp_dict['closing balance'] = temp_dict['opening balance'] + temp_dict['loan proceeds - net'] + temp_dict['repayments - net']
        value = value
        
        temp_list.append(temp_dict)
        temp_dict = {}
    
    temp_df = pd.DataFrame(temp_list)
    temp_df['year'] = temp_df['year'].astype('str')
    temp_df = temp_df.rename(columns={temp_df.columns[0]: 'DEBT'})
    
    # Now, transpose the DataFrame
    temp_df = temp_df.transpose().reset_index()

    new_header = temp_df.iloc[0].to_list()

    for i, value in enumerate(new_header):
        new_header[i] = str(value)

    # Assuming temp_df is your DataFrame and you want to remove the first row and reset the index
    temp_df = temp_df.iloc[1:].reset_index(drop=True)

    temp_df.columns = new_header
    
    temp_df.drop('DEBT', axis=1, inplace=True)
    
    debt_df = pd.concat([debt_df, temp_df], axis=1)
    
    debt_df = debt_df.to_json(orient='records')
    
    return debt_df

@app.route('/fixedAsset', methods=['POST'])
def fixedAsset(predicted_year = 4):
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        df_assumption = data.get('df_assumption', None)
        
        if df_assumption is not None:
            # Process the df_assumption here
            df_assumption = pd.DataFrame(df_assumption)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
        
        try:
            df_assumption = pd.DataFrame(df_assumption)
        except:
            df_assumption = pd.read_json(df_assumption)
        
        
        df_assumption = df_assumption[df_assumption['Select'] == True]
    
        fixedAsset_df = read_excel_file(file_path='', sheet_name='FA')
        
        transformed_fixedAsset_df = process_sheet(fixedAsset_df)
        
        fixedAsset_dict = transformed_fixedAsset_df.to_dict(orient='records')
        
        last_year = fixedAsset_df.columns.to_list()[-1]
        
        value_openingBalance = fixedAsset_dict[-1]['closing balance - nbv']
        
        temp_list = []
        for i in range(1, predicted_year+1):
            temp_dict = {}
            temp_dict['year'] = last_year + i
            temp_dict['opening balance - nbv'] = value_openingBalance
            value_2 = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * value_openingBalance
            temp_dict['additions during the year - net'] = value_2
            value_depreciation = df_assumption[df_assumption['COMPONENT'] == 'CAPEX'][str(last_year+i)].values[0] * (value_openingBalance + (value_2 * 6 / 12))
            temp_dict['Depreciation charge for the year'] = value_depreciation
            temp_dict['Closing Balance - NBV'] = value_openingBalance + value_2 + value_depreciation
            
            temp_list.append(temp_dict)
            
        temp_df = pd.DataFrame(temp_list)
        temp_df = tranposing(temp_df, 'FA')
        # temp_df = temp_df.reset_index()
        temp_df.drop('FA', axis=1, inplace=True)
        
        fixedAsset_df = pd.concat([fixedAsset_df, temp_df], axis=1)
        
        fixedAsset_df = fixedAsset_df.to_json(orient='records')
        
        return fixedAsset_df

@app.route('/Equity', methods=['GET'])
def Equity(predicted_year = 4):
    
    Equity_df = read_excel_file(file_path='', sheet_name='EQUITY')
    
    transformed_Equity_df = process_sheet(Equity_df)
    
    last_year = Equity_df.columns.to_list()[-1]
    Equity_dict = transformed_Equity_df.to_dict(orient = 'records')
    
    closingBalance_shareCapital_value = Equity_dict[-1]['closing balance - share capital']
    
    openingBalance_statutoryReserve_value = Equity_dict[-1]['closing balance - statutory reserve']
    
    openingBalance_retainedEarnings_value = Equity_dict[-1]['closing balance - retained earnings']
    
    temp_list = []
    for i in range(1, predicted_year+1):
        temp_dict = {}
        
        temp_dict['year'] = last_year + i
        
        """
            SHARE CAPITAL OPENING
        """
        
        temp_dict['opening balance - share capital'] = closingBalance_shareCapital_value
        temp_dict['capital increase/decrease'] = 0
        temp_dict['closing balance - share capital'] = temp_dict['opening balance - share capital'] + temp_dict['capital increase/decrease']
        
        closingBalance_shareCapital_value = temp_dict['closing balance - share capital']
        
        """
            SHARE CAPITAL CLOSING
        """
        
        """
            STATUTORY RESERVE OPENING
        """
        temp_dict['opening balance - statutory reserve'] = openingBalance_statutoryReserve_value
        temp_dict['transfer for the year'] = 0
        temp_dict['closing balance - statutory reserve'] = temp_dict['opening balance - statutory reserve'] + temp_dict['transfer for the year']
        
        openingBalance_statutoryReserve_value = temp_dict['closing balance - statutory reserve']
        
        """
            STATUTORY RESERVE CLOSING
        """
        
        """
            RETAINED EARNING OPENING
        """
        temp_dict['opening balance - retained earnings'] = openingBalance_retainedEarnings_value
        temp_dict['net income'] = 0 #should be drived from IS_CRNT
        temp_dict['dividends & oci movement'] = 0
        temp_dict['statutory reserve transfer'] = 0
        temp_dict['closing balance - retained earnings'] = temp_dict['opening balance - retained earnings'] + temp_dict['net income'] + temp_dict['dividends & oci movement'] + temp_dict['statutory reserve transfer']
        
        openingBalance_retainedEarnings_value = temp_dict['closing balance - retained earnings']
        """
            RETAINED EARNING CLOSING
        """
        
        temp_dict['share capital'] = temp_dict['closing balance - share capital']
        temp_dict['statutory reserve'] = temp_dict['closing balance - statutory reserve']
        temp_dict['retained earnings'] = temp_dict['closing balance - retained earnings']
        temp_dict['closing balance - equity'] = temp_dict['share capital'] + temp_dict['statutory reserve'] + temp_dict['retained earnings']
        
        temp_list.append(temp_dict)
        
    temp_df = pd.DataFrame(temp_list)
    columnList = transformed_Equity_df.columns.to_list()
    
    temp_df = temp_df[columnList]
    temp_df = tranposing(temp_df, 'EQUITY')
    
    temp_df.drop('EQUITY', axis=1, inplace=True)
    
    Equity_df = pd.concat([Equity_df, temp_df], axis=1)
    
    Equity_df = Equity_df.to_json(orient='records')
    
    return Equity_df

@app.route('/BalanceSheet', methods=['POST'])
def balanceSheet():
    
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        workingCapital_df = data.get('workingCapital', None)
        debt_df = data.get('debt', None)
        fixedAsset_df = data.get('fixedAsset', None)
        Equity_df = data.get('equity', None)
        
        if (workingCapital_df is not None) | (debt_df is not None) | (fixedAsset_df is not None) | (Equity_df is not None):
            # Process the df_assumption here
            try:
                workingCapital_df = pd.DataFrame(workingCapital_df)
                debt_df = pd.DataFrame(debt_df)
                fixedAsset_df = pd.DataFrame(fixedAsset_df)
                Equity_df = pd.DataFrame(Equity_df)
            except:
                workingCapital_df = pd.read_json(workingCapital_df)
                debt_df = pd.read_json(debt_df)
                fixedAsset_df = pd.read_json(fixedAsset_df)
                Equity_df = pd.read_json(Equity_df)
        else:
            # df_assumption wasn't provided
            return jsonify({"error": "Missing df_assumption data"}), 400
            
        balanceSheet_df = read_excel_file(file_path='', sheet_name='BALANCESHEET')
        
        balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
        last_year = balanceSheet_df.columns.to_list()[-1]
        
        workingCapital_predicted_dict, balanceSheet_dict = working_Capital(balanceSheet_df, workingCapital_df, last_year)    
        
        """
            Working with Debt
        """
        
        debt_df, balanceSheet_dict = debt_checking(debt_df, balanceSheet_dict, last_year)
        
        """
            Working on Fixed Assets
        """
        
        fixedAsset_df, balanceSheet_dict = FA_checking(fixedAsset_df, balanceSheet_dict, last_year)
        
        """
            Working on Equity
        """
        
        Equity_df, balanceSheet_dict = equity_checking(Equity_df, balanceSheet_dict, last_year)
        
        updated_balanceSheet_df = pd.DataFrame(balanceSheet_dict)
        
        """
        
        """
        
        # Convert all column names to string
        updated_balanceSheet_df.columns = updated_balanceSheet_df.columns.astype(str)

        # Rearranging columns based on data type
        # Categorical and numerical identification
        categorical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype == object]
        numerical_cols = [col for col in updated_balanceSheet_df.columns if updated_balanceSheet_df[col].dtype != object]

        # Ensuring specific order for year columns by checking if column names are all digits
        year_cols = [col for col in numerical_cols if col.isdigit()]
        other_numerical_cols = [col for col in numerical_cols if not col.isdigit()]

        # Define the specific order requested: [name, age, city, salary, years...]
        new_order = categorical_cols + other_numerical_cols + sorted(year_cols)
        
        # Rearrange the DataFrame according to the new order
        updated_balanceSheet_df = updated_balanceSheet_df.reindex(columns=new_order)
        
        temp_balanceSheet_df = process_sheet(updated_balanceSheet_df)
        
        temp_balanceSheet_dict = temp_balanceSheet_df.to_dict(orient = 'records')
        
        for index, bs_data in enumerate(temp_balanceSheet_dict):
            
            try:
                if int(bs_data['year']) > last_year:
                    bs_data['current assets'] = bs_data['trade receivables'] + bs_data['due from related parties'] + bs_data['inventories'] + bs_data['prepayments and other receivables']
                    bs_data['current liabilities'] = bs_data['short-term borrowings'] + bs_data['trade payables'] + bs_data['accrued expenses and other liabilities'] + bs_data['due to related parties'] + bs_data['zakat payable']
                    
                    bs_data['cash and cash equivalents'] = bs_data['current liabilities'] - bs_data['current assets']
                    bs_data['investments at fair value through profit or loss'] = 0
                    bs_data['equity accounted investment'] = 0
                    
                    if index != 0 and bs_data['other receivables'] != 0:
                        
                        bs_data['other receivables'] = temp_balanceSheet_dict[index - 1]['other receivables']
                    
                    bs_data['non-current assets'] = bs_data['property and equipment'] + bs_data['investments at fair value through profit or loss'] + bs_data['equity accounted investment'] + bs_data['other receivables']
                    bs_data['total assets'] = bs_data['current assets'] + bs_data['non-current assets']
                    
                    bs_data['employee termination benefits'] = temp_balanceSheet_dict[index - 1]['employee termination benefits'] # multiply by IS_CRNT value
                    bs_data['due to related parties(current liabilities)'] = 0
                    bs_data['non-current liabilities'] = bs_data['employee termination benefits'] + bs_data['due to related parties(current liabilities)']
                    
                    bs_data["shareholders' equity"] = bs_data['share capital'] + bs_data['statutory reserve'] + bs_data['retained earnings']
                    
                    bs_data['total liabilities & equity'] = bs_data['current liabilities'] + bs_data['non-current assets'] + bs_data["shareholders' equity"]
            except:
                pass
                
            temp_balanceSheet_df = pd.DataFrame(temp_balanceSheet_dict)
            temp_balanceSheet_df = tranposing(df=temp_balanceSheet_df, column_name="BALANCE SHEET")
            
            temp_balanceSheet_df = temp_balanceSheet_df.to_json(orient='records')
        
        return temp_balanceSheet_df

@app.route('/ga_assumption', methods=['GET'])
def get_ga_assumption():
    
    return get_assumption(), 200

@app.route('/g_a', methods=['POST'])
def GandA():
    if request.is_json:
        # Extract data from the JSON request
        data = request.get_json()
        assumption_dict = data.get('df_assumption', None)
        
        df_ga = read_excel_file(file_path='', sheet_name='General and administrative exp')
    
        temp_ga = process_sheet(df_ga)
        
        year_ga = temp_ga['year'].to_list()
        last_year = year_ga[-1]
        
        df_ga = general_admin_exp(assumption_dict, df_ga, last_year)
        ga_json = df_ga.to_json(orient='records')
        return ga_json, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400  
if __name__ == '__main__':
    app.run(debug=True)
