from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import json

app = Flask(__name__)


def read_excel_file(file_path, sheet_name=None):
    file_path = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Financial Statement - Copy.xlsx"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    try:
        df = df.drop('Note', axis=1)
    except:
        pass
    return df

def process_sheet(df):
    
    try:
        df = df.drop('Select', axis=1)
        df = df.drop('BASE', axis=1)
    except:
        pass
    
    df = df.transpose().reset_index()
    new_header = df.iloc[0].to_list()
    
    for i, value in enumerate(new_header):
        new_header[i] = str(value).lower().strip()
    
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)
    df = df.rename(columns={df.columns[0]: 'year'})
    
    # change from int to str
    df['year'] = df['year'].astype('int')
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
def read_assumption_file():
    filePath_assumption = "E:/MaazProducts/Fiverr/Platform/advisors/Statis DashBoard/SourceData/NSC/Assumption.xlsx"
    df_assumption = pd.read_excel(filePath_assumption)
    
    new_column_position = 2  # Position after 'A'
    new_column_name = 'Select'
    new_column_values = True

    df_assumption.insert(loc=new_column_position, column=new_column_name, value=new_column_values)

    df_assumption['Select'] = True
    
    return df_assumption.to_json(orient='records')

@app.route('/is_crnt', methods = ['POST'])
def is_crnt(predicted_year = 8):
    
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
        df_assumption = process_sheet(df_assumption)
        
        df_fs = read_excel_file(file_path='', sheet_name='INCOME STATEMENT')
        df_fs = process_sheet(df_fs)
        
        year_fs = df_fs['year'].to_list()
        last_year = year_fs[-1]
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
        
        df = df.to_json(orient='records')
        
        # return df, df_copy
        return df, 200

    else:
        return jsonify({"error": "Request must be JSON"}), 400   

@app.route('/workingCapital', methods=['GET'])
def workingCapital(prediction_year = 4):

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
        
        last_year = workingCapital_df.columns.to_list()[-1]
        
        revenue = is_crnt_df.loc[[0, 1, 4], : str(last_year)]
        
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
        
        avg = key_indicators_df.iloc[:, 2:].mean(axis=1)  # Exclude the two column ('component') in the mean calculation

        # Prepare new data for future years
        new_data = {}
        for i in range(1, prediction_year + 1):  # Assuming you want to add 5 years of data
            new_year = str(last_year + i)
            new_data[new_year] = avg.values  # Use avg.values to directly assign the array to the new year
    
        # Create a DataFrame from the new data
        new_df = pd.DataFrame(new_data)

        # Concatenate the original DataFrame with the new DataFrame along columns (axis=1)
        key_indicators_df = pd.concat([key_indicators_df, new_df], axis=1)
        
        
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
        
        # st.dataframe(workingCapital_predicted_df, hide_index=True)
        # st.dataframe(key_indicators_df, hide_index=True)
        
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
        
        return fixedAsset_df

@app.route('/Equity', methods=['POST'])
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
    
    return Equity_df

def balanceSheet():
    
    
    if request.is_json:
        
        # Extract data from the JSON request
        data = request.get_json()
        workingCapital_df = data.get('workingCapital_df', None)
        debt_df = data.get('debt_df', None)
        fixedAsset_df = data.get('fixedAsset_df', None)
        Equity_df = data.get('Equity_df', None)
        
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
            
            
    balanceSheet_df = read_excel_file(file_path='', sheet_name='BALANCESHEET')
    
    balanceSheet_dict = balanceSheet_df.to_dict(orient='records')
    
    last_year = balanceSheet_df.columns.to_list()[-1]
    
    """
        Working with WC
    """
    
    workingCapital_predicted_df = workingCapital_df.loc[:, str(last_year+1): ]
    workingCapital_predicted_df = pd.concat([workingCapital_df.iloc[:, : 1], workingCapital_predicted_df], axis=1)
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
    
    """
        Working with Debt
    """
    
    debt_df = debt_df[debt_df['DEBT'] == 'Closing Balance']
    debt_df = debt_df.loc[:, str(last_year+1): ]
    
    if not debt_df.empty:
        debt_dict = debt_df.to_dict(orient='records')[0]
        
        for data in balanceSheet_dict:
            if data['BALANCE SHEET'] == "Short-term borrowings":
                data.update(debt_dict)
                break
    
    """
        Working on Fixed Assets
    """
    
    fixedAsset_df = fixedAsset_df[fixedAsset_df['FA'] == 'Closing Balance - NBV']
    fixedAsset_df = fixedAsset_df.loc[:, str(last_year+1): ]
    
    if not fixedAsset_df.empty:
        fixedAsset_dict = fixedAsset_df.to_dict(orient='records')[0]
        
        for data in balanceSheet_dict:
            if data['BALANCE SHEET'] == "Property and equipment":
                data.update(fixedAsset_dict)
                break
    
    """
        Working on Equity
    """
    
    Equity_df = Equity_df[Equity_df['EQUITY'].isin(['Share capital','Statutory reserve','Retained earnings'])]
    
    if not Equity_df.empty:
        
        for data in balanceSheet_dict:
            if data['BALANCE SHEET'] == 'Share capital':
                data.update(Equity_df[Equity_df['EQUITY'] == 'Share capital'].loc[:, str(last_year+1): ].to_dict(orient='records')[0])
            
            elif data['BALANCE SHEET'] == 'Statutory reserve':
                data.update(Equity_df[Equity_df['EQUITY'] == 'Statutory reserve'].loc[:, str(last_year+1): ].to_dict(orient='records')[0])
            
            elif data['BALANCE SHEET'] == 'Retained earnings':
                data.update(Equity_df[Equity_df['EQUITY'] == 'Retained earnings'].loc[:, str(last_year+1): ].to_dict(orient='records')[0])
    
    updated_balanceSheet_df = pd.DataFrame(balanceSheet_dict)
    
    temp_balanceSheet_df = process_sheet(updated_balanceSheet_df)
    # st.dataframe(temp_balanceSheet_df, hide_index=True)
    
    temp_balanceSheet_dict = temp_balanceSheet_df.to_dict(orient = 'records')
    
    for index, bs_data in enumerate(temp_balanceSheet_dict):
        
        if bs_data['year'] > last_year:
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
    
    temp_balanceSheet_df = pd.DataFrame(temp_balanceSheet_dict)
    temp_balanceSheet_df = tranposing(df=temp_balanceSheet_df, column_name="BALANCE SHEET")
    # st.write(temp_balanceSheet_df)

if __name__ == '__main__':
    app.run(debug=True)
