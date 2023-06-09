# import subprocess
import pandas as pd
from pulp import *
# import math 
import numpy as np
# import xlrd
from array import *
import json
from flask import Flask, redirect, url_for, request, render_template, session
# import urllib
import os.path
from os import path
# import gmplot
import pickle
import os


app = Flask(__name__)
app.secret_key = 'aqswdefrgt'

@app.route('/')
def index():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("login.html")

@app.route('/upload')
def upload():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("upload.html")

@app.route('/results')
def results():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("result.html")

@app.route('/warehouse')
def warehouse():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("warehouse.html")

@app.route('/railhead')
def railhead():
    if 'username' not in session:
        return render_template("login.html")
    return render_template("railhead.html")

@app.route('/login',methods = ["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    data = {}
    if(username=="admin" and password=="admin"):
        data['status'] = 1
        session['username'] = username
    else:
        data['status'] = 0

    json_data = json.dumps(data)
    json_object = json.loads(json_data)
    return(json.dumps(json_object, indent = 1))

# log-out feature
@app.route("/logout")
# login_required
def logout():
    session.pop('username', None)
    return render_template("login.html")

# Cache clear
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/register')
def register():
    return render_template("result.html")

@app.route('/forgot')
def forgot():
    return render_template("result.html")

@app.route("/uploadConfigFile",methods = ["POST"])
def uploadConfigFile():
    data = {}
    try:
        file = request.files['uploadFile']
        filename = file.filename
        file.save("Input\\Input_Template.xlsx")
        data['status'] = 1
    except:
        data['status'] = 0
    
    json_data = json.dumps(data)
    json_object = json.loads(json_data)

    return(json.dumps(json_object, indent = 1))
    
@app.route("/processInputConfig",methods = ["POST"])
def processInputConfig():
    if 'username' not in session:
        return render_template("login.html")
    # data = {}
    try:
        f = open("Input\\input_config.json",'r')
        data = json.load(f)
        data["Status"] = 1
        Excel_sheet = data["SelectfromExcel"]["File"]
        non_consuming = pd.read_excel(Excel_sheet,sheet_name = 'Non Consuming States', header = None, index_col=0)
        consuming = pd.read_excel(Excel_sheet,sheet_name = 'Consuming States', header = None, index_col=0)
        data["SelectfromExcel"]["non_consuming"] = list(non_consuming.index)
        data["SelectfromExcel"]["consuming"] = list(consuming.index)

    except Exception as e:
        print(e)
        data = {"Status":0}
    
    json_data = json.dumps(data)
    json_object = json.loads(json_data)

    return(json.dumps(json_object, indent = 1))

@app.route("/processOutputConfig",methods = ["POST"])
def processOutputConfig():
    if 'username' not in session:
        return render_template("login.html")
    data_solved = {"Status":0,"Scenario":{}}
    try:
        f = open("Output\\output_config.json",'r')
        data = json.load(f)
        for scenario in data:
            if data[scenario]["Status"] != 0:
                data_solved["Scenario"][scenario] = data[scenario]
        if len(data_solved["Scenario"]) !=0:
            data_solved["Status"] = 1
    except Exception as e:
        print(e)
        data_solved = {"Status":0}
    
    json_data = json.dumps(data_solved)
    json_object = json.loads(json_data)

    return(json.dumps(json_object, indent = 1))

@app.route("/readResult",methods = ["POST","GET"])
def readResult():
    if 'username' not in session:
        return render_template("login.html")
    if request.method == "POST":        
        try: 
            data1 = json.load(open("Output\\output_config.json",'r'))
            request_data = request.get_json()
            f = open(data1[request_data["Scenario"]]["Result"],'r')
            data = json.load(f)
        except:
            data = {"Status":0}
    
        json_data = json.dumps(data)
        json_object = json.loads(json_data)

        return(json.dumps(json_object, indent = 1))
    else:
        return render_template("result.html")

@app.route("/readWarehouse",methods = ["POST","GET"])
def readWarehouse():
    if 'username' not in session:
        return render_template("login.html")
    if request.method == "POST":        
        try: 
            data1 = json.load(open("Output\\output_config.json",'r'))
            request_data = request.get_json()
            f = open(data1[request_data["Scenario"]]["Warehouse"],'r')
            data = json.load(f)
        except:
            data = {"Status":0}
    
        json_data = json.dumps(data)
        json_object = json.loads(json_data)

        return(json.dumps(json_object, indent = 1))
    else:
        return render_template("warehouse.html")

   
@app.route("/solve",methods = ["POST","GET"])
def solve():
    if 'username' not in session:
        return render_template("login.html")
    data1 = {}
    if request.method == "POST":
        try:
            indata = json.load(open("Input\\input_config.json",'r'))
            input_file = indata["Input_File"]
            request_data = request.get_json()
            scenario = indata["Scenario"][request_data["Scenario"]]["Code"]
            # input_file = indata["Input_File"][request_data["Input_File"]]
            beta = request_data["beta"] 
            rail_flag = request_data["rail_flag"]
            rail_cap = request_data["Rail_Cap"]
            wh_cap = request_data["WH_Cap"]
            n = request_data["policy_n"]
            non_consuming = request_data["non_consuming"]
            consuming = request_data["consuming"]
            output_file = json.load(open("Output\\output_config.json",'r'))[request_data["Scenario"]]["Excel"]
            os.system("python " + scenario + " " + input_file + " " + beta + " " + wh_cap + " " + rail_cap +' "' + str(non_consuming) + '" "' + str(consuming) + '" ' + output_file + " " + str(n) + " " + rail_flag)
            outdata = json.load(open("Output\\output_config.json",'r'))
            if outdata[request_data["Scenario"]]["Status"] != 0:
                Cov_wh = pd.read_excel(input_file, sheet_name = 'WH_Covered', header = 0, index_col = 0)
                Cov_rh = pd.read_excel(input_file, sheet_name = 'RH_Covered', header = 0, index_col = 0)
                IWH_Wheat = pd.read_excel(output_file,sheet_name="IWH_Wheat",header = 0, index_col =0)
                IWH_Rice = pd.read_excel(output_file,sheet_name="IWH_Rice",header = 0, index_col = 0)
                Proc_Wheat = pd.read_excel(output_file,sheet_name="Proc_Wheat",header = 0, index_col = 0)
                Proc_Rice = pd.read_excel(output_file,sheet_name="Proc_Rice",header = 0, index_col = 0)
                try: 
                    a_tw = pd.read_excel(output_file,sheet_name="a_tw",header = 0, index_col = 0)
                    Covered_Inc = pd.read_excel(output_file,sheet_name="Covered_Inc%",header = 0, index_col = 0)
                except:
                    pass
                
                IRH_Wheat = pd.read_excel(output_file,sheet_name="IRH_Wheat",header = 0, index_col =0)
                IRH_Rice = pd.read_excel(output_file,sheet_name="IRH_Rice",header = 0, index_col = 0)
                infl_wh = pd.read_excel(output_file, sheet_name = 'x_rw_wheat',header = 0,index_col= 0)
                outfl_wh = pd.read_excel(output_file, sheet_name = 'x_wr_wheat',header = 0,index_col= 0)
                infl_ri = pd.read_excel(output_file, sheet_name = 'x_rw_rice',header = 0,index_col= 0)
                outfl_ri = pd.read_excel(output_file, sheet_name = 'x_wr_rice',header = 0,index_col= 0)
                country = json.load(open("Input\\state.json",'r'))
                data_wh = {} ; data_rh = {}
                result_inv_wh = [] ; result_inv_ri = [] ; result_inv_tot = []
                result_atw = []
                result_infl_wh = [] ; result_infl_ri = []
                result_outfl_wh = [] ; result_outfl_ri = []
                result_outfl_tot = [] ; result_infl_tot = []
                Result =  json.load(open(outdata[request_data["Scenario"]]["Result"],'r'))                
                for state in country:
                    state_inv_wh = {"State": state}
                    state_inv_ri = {"State": state}
                    state_inv_tot = {"State": state}
                    state_atw = {"State":state}
                    state_infl_wh = {"State": state}
                    state_infl_ri = {"State": state}
                    state_outfl_wh = {"State": state}
                    state_outfl_ri = {"State": state}
                    state_infl_tot = {"State": state}
                    state_outfl_tot = {"State": state}
                    if state not in data_wh:
                        data_wh[state] = {}
                    for wh in country[state]["Warehouse"]:                        
                        data_wh[state][wh] = {}
                        try:
                            state_atw["Originl Covered Capacity"] = round(state_atw.get("Original Covered Capacity",0) + np.max(Cov_wh.loc[wh][:]),3)
                            state_atw["Additional Capacity"] = round(state_atw.get("Additional Capacity",0) + np.max(a_tw.loc[wh][:]),3)
                        except :
                            pass
                        for month in Cov_wh.columns:
                            state_inv_wh[month] = round(state_inv_wh.get(month,0) + IWH_Wheat.loc[wh][month],3)
                            state_inv_ri[month] = round(state_inv_ri.get(month,0) + IWH_Rice.loc[wh][month],3)
                            state_inv_tot[month] = round(state_inv_wh[month] + state_inv_ri[month],3)

                            data_wh[state][wh][month] = {
                                "Capacity": round(Cov_wh.loc[wh][month],3),
                                "Inventory":{"Wheat": round(IWH_Wheat.loc[wh][month],3), "Rice":round(IWH_Rice.loc[wh][month],3)},
                                "Procurement":{"Wheat":None,"Rice":None},
                                "A_tw":None, "Cov_inc": None
                            }
                            try:
                                if(month in a_tw.columns):
                                    data_wh[state][wh][month]["A_tw"] = round(a_tw.loc[wh][month],3)
                                    data_wh[state][wh][month]["Cov_inc"] = round(Covered_Inc.loc[wh][month],3)
                            except:
                                pass
                            if month in Proc_Wheat.columns:
                                data_wh[state][wh][month]["Procurement"] = {"Wheat":round(Proc_Wheat.loc[wh][month],3),"Rice":round(Proc_Rice.loc[wh][month],3)}
                                state_infl_wh[month] = round(state_infl_wh.get(month,0) + infl_wh.loc[wh][month], 3)
                                state_infl_ri[month] = round(state_infl_ri.get(month,0) + infl_ri.loc[wh][month], 3)
                                state_outfl_wh[month] = round(state_outfl_wh.get(month,0) + outfl_wh.loc[wh][month], 3)
                                state_outfl_ri[month] = round(state_outfl_ri.get(month,0) + outfl_ri.loc[wh][month], 3)
                                state_infl_tot[month] = round(state_infl_wh[month] + state_infl_ri[month],3)
                                state_outfl_tot[month] = round(state_outfl_wh[month] + state_outfl_ri[month],3)

                    state_atw["Percentage Increase"] = round(100*state_atw.get("Additional Capacity",0)/state_atw["Originl Covered Capacity"],0)
                    state_atw["Total Required Capacity"] = round(state_atw["Originl Covered Capacity"] + state_atw.get("Additional Capacity",0),3)
                    result_inv_wh.append(state_inv_wh)
                    result_inv_ri.append(state_inv_ri)
                    result_inv_tot.append(state_inv_tot)
                    result_atw.append(state_atw)
                    result_infl_wh.append(state_infl_wh)
                    result_infl_ri.append(state_infl_ri)
                    result_outfl_wh.append(state_outfl_wh)
                    result_outfl_ri.append(state_outfl_ri)
                    result_infl_tot.append(state_infl_tot)
                    result_outfl_tot.append(state_outfl_tot)
                # Result["beta"] = beta
                # Result['rail_cap'] = rail_cap
                # Result["wh_cap"] = wh_cap
                Result["Month"] = list(Cov_wh.columns)
                Result["Additional Capacity"] = result_atw
                Result["Inventory Wheat"]= result_inv_wh
                Result["Inventory Rice"] = result_inv_ri
                Result["Total Inventory"] = result_inv_tot
                Result["Inflow Wheat"] = result_infl_wh
                Result["Inflow Rice"] = result_infl_ri
                Result["Outflow Wheat"] = result_outfl_wh
                Result["Outflow Rice"] = result_outfl_ri
                Result["Total Inflow"] = result_infl_tot
                Result["Total Outflow"] = result_outfl_tot
                
                json.dump(Result,open(outdata[request_data["Scenario"]]["Result"],'w'),indent = 4)
                json.dump(data_wh,open(outdata[request_data["Scenario"]]["Warehouse"],'w'),indent = 4)
                data1["status"] = 1
            else:
                data1["status"] = 0
            # f2 = open("testing.json",'r')
            # data1 = json.load(f2)
        except Exception as e:
            print(e)
            data1["status"] = 0
        json_data = json.dumps(data1)
        json_object = json.loads(json_data)

        return(json.dumps(json_object, indent = 1))
    else:
        return render_template("upload.html")

if __name__ == '__main__':
    app.run()


# @app.route("/readOutput_IWH",methods = ["POST","GET"])
# def readOutput_IWH():
#     try:
#         IWH_Wheat = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="IWH_Wheat",header = 0, index_col =0)
#         IWH_Rice = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="IWH_Rice",header = 0, index_col = 0)
#         Proc_Wheat = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="Proc_Wheat",header = 0, index_col = 0)
#         Proc_Rice = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="Proc_Rice",header = 0, index_col = 0)
#         a_tw = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="a_tw",header = 0, index_col = 0)
#         Covered_Inc = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="Covered_Inc%",header = 0, index_col = 0)
#         IRH_Wheat = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="IRH_Wheat",header = 0, index_col =0)
#         IRH_Rice = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="IRH_Rice",header = 0, index_col = 0)
#         data = {"Wharehouse":{},"Railhead":{}}
#         for wh in IWH_Wheat.index:
#             data["Wharehouse"][wh] = {}
#             for month in IWH_Wheat.columns:
#                 data["Wharehouse"][wh][month] = {
#                     "Inventory":{"Wheat": IWH_Wheat.loc[wh][month], "Rice":IWH_Rice.loc[wh][month]},
#                     "Procurement":{"Wheat":Proc_Wheat.loc[wh][month],"Rice":Proc_Rice.loc[wh][month]},
#                     "A_tw":a_tw[wh][month],
#                     "Cov_inc": Covered_Inc[wh][month]
#                     }
#         for rh in IRH_Wheat.index:
#             data["Railhead"][rh] = {}
#             for month in IRH_Wheat.columns:
#                 data["Railhead"][rh][month] = {
#                     "Inventory":{"Wheat": IRH_Wheat.loc[wh][month], "Rice":IRH_Rice.loc[wh][month]}
#                     }
#     except:
#         data = {}
#         data["status"] = 0
#     return(json.dumps(data, indent = 1))

# @app.route("/readOutput_IRH",methods = ["POST","GET"])
# def readOutput_IRH():
#     try:
#         IRH_Wheat = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="IRH_Wheat",header = 0, index_col =0)
#         IRH_Rice = pd.read_excel('Allstates_upperbound_aw.xlsx',sheet_name="IRH_Rice",header = 0, index_col = 0)
#         data = {"Wharehouse":{},"Railhead":{}}
#         for wh in IRH_Wheat.index:
#             data[wh] = {}
#             for month in IRH_Wheat.columns:
#                 data[wh][month] = {"Wheat": IRH_Wheat.loc[wh][month], "Rice":IRH_Rice.loc[wh][month]}
#     except:
#         data = {}
#         data["status"] = 0
#     return(json.dumps(data, indent = 1))


# @app.route('/processDefaultFile',methods = ["POST"])
# def processDefaultFile():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
    
#     if(path.exists("configFile.json")==False):
#         data['status'] = 0
#         json_data = json.dumps(data)
#         json_object = json.loads(json_data)
#         return(json.dumps(json_object, indent = 1))

#     try:
#         data['status'] = 1
#         dbfile = open('districtPickle.pkl', 'rb')     
#         db = pickle.load(dbfile)
#         enableDisableDistrict = db['districtName']
#         districtCount = 0
#         print(enableDisableDistrict)
#         params = json.load(open("configFile.json","r"))
#         districtList = []
#         fileList = {}
#         for i in params["District"]:
#             if i in enableDisableDistrict:
#                 districtList.append(i)
#                 fileList["ParameterFile"] = params["District"][i]["ParameterFile"] 
#                 fileList["DistanceFile"] = params["District"][i]["DistanceFile"]
#                 data[i] = fileList
#                 fileList = {}
#                 districtCount = districtCount + 1
#         data['districtName'] = districtList
#         data['noOfFiles'] = districtCount
        
#         #for i in params['Enable']:
#             #print(i)
        
#     except:
#         data['status'] = 0
    
#     json_data = json.dumps(data)
#     json_object = json.loads(json_data)

#     return(json.dumps(json_object, indent = 1))


# @app.route("/uploadConfigFile",methods = ["POST"])
# def uploadConfigFile():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
#     try:
#         file = request.files['configFile']
#         filename = file.filename
#         file.save("configFile.json")
#         data['status'] = 1
#         params = json.load(open("configFile.json","r"))
#         data['noOfDistrict'] = len(params["District"])
#         districtList = []
#         for i in params["District"]:
#             districtList.append(i)
#         data['districtName'] = districtList
#     except:
#         data['status'] = 0
    
#     json_data = json.dumps(data)
#     json_object = json.loads(json_data)

#     return(json.dumps(json_object, indent = 1))


# @app.route("/processConfigFile",methods = ["POST"])
# def processConfigFile():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
#     try:
#         data['status'] = 1
#         params = json.load(open("configFile.json","r"))
#         data['noOfDistrict'] = len(params["District"])
#         districtList = []
#         for i in params["District"]:
#             districtList.append(i)
#         data['districtName'] = districtList
#     except:
#         data['status'] = 0
    
#     json_data = json.dumps(data)
#     json_object = json.loads(json_data)

#     return(json.dumps(json_object, indent = 1))

# @app.route("/processConfigFile2",methods = ["POST"])
# def processConfigFile2():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
#     try:
#         data['status'] = 1
#         params = json.load(open("configFile2.json","r"))
#         data['noOfDistrict'] = len(params["District"])
#         districtList = []
#         for i in params["District"]:
#             districtList.append(i)
#         data['districtName'] = districtList
#     except:
#         data['status'] = 0
    
#     json_data = json.dumps(data)
#     json_object = json.loads(json_data)

#     return(json.dumps(json_object, indent = 1))

# @app.route("/enableDisableDistrict",methods = ["POST"])
# def enableDisableDistrict():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
#     enableDisable = {}
#     try:
#         noOfDistrictEnabled = 0
#         params = json.load(open("configFile.json","r"))
#         for i in params["District"]:
#             temp = "enableDisable" + i
#             if temp in request.form:
#                 enableDisable[i] = 1
#                 noOfDistrictEnabled = noOfDistrictEnabled + 1
#             else:
#                 enableDisable[i] = 0

#         data['noOfDistrict'] = noOfDistrictEnabled
#         districtList = []
#         for i in params["District"]:
#             if enableDisable[i]==1:
#                 districtList.append(i)
#         data['districtName'] = districtList
        
#         enableDisableData = {}
#         enableDisableData['districtName'] = districtList
        
#         json_data1 = json.dumps(enableDisableData)
#         json_object1 = json.loads(json_data1) 

#         if os.path.exists("districtPickle.pkl"):
#             os.remove("districtPickle.pkl")

#         # open pickle file
#         dbfile = open('districtPickle.pkl', 'ab')

#         # save pickle data
#         pickle.dump(json_object1, dbfile)                     
#         dbfile.close()


#         data['status'] = 1
#     except:
#         data['status'] = 0
    
#     json_data = json.dumps(data)
#     json_object = json.loads(json_data)

#     return(json.dumps(json_object, indent = 1))

# @app.route("/uploadAllFile",methods = ["POST"])
# def uploadAllFile():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
#     try:
#         dbfile = open('districtPickle.pkl', 'rb')     
#         db = pickle.load(dbfile)
#         enableDisableDistrict = db['districtName']
        
#         params = json.load(open("configFile.json","r"))
#         for i in params["District"]:
#             if i in enableDisableDistrict:
#                 file = request.files["parameter"+i]
#                 filename = file.filename
#                 file.save(params["District"][i]["ParameterFile"])
#                 file = request.files["distance"+i]
#                 filename = file.filename
#                 file.save(params["District"][i]["DistanceFile"])
#         data['status'] = 1
#     except:
#         data['status'] = 0
    
#     json_data = json.dumps(data)
#     json_object = json.loads(json_data)

#     return(json.dumps(json_object, indent = 1))


# @app.route("/readPickle",methods = ["POST","GET"])
# def readPickle():
#     try:
#         dbfile = open('ouputPickle.pkl', 'rb')     
#         db = pickle.load(dbfile)
#         dbfile.close()
#     except:
#         db = {}
#         db["status"] = 0
#     return(json.dumps(db, indent = 1))

# @app.route("/processFile",methods = ["POST","GET"])
# def processFile():
#     if 'username' not in session:
#         return render_template("login.html")
#     data = {}
#     file = open("configFile.json","r")
#     params = json.load(file)
#     DistrictData = {}
    
#     dbfile = open('districtPickle.pkl', 'rb')     
#     db = pickle.load(dbfile)
#     enableDisableDistrict = db['districtName']

#     for district in params["District"]:
#         if district in enableDisableDistrict:
#             message = "Excel file is incorrect"
#             try:
#                 USN = pd.ExcelFile(params["District"][district]["ParameterFile"])
#             except:
#                 data = {}
#                 data["status"] = 0
#                 data["message"] = message
#                 data["district"] = district
#                 json_data = json.dumps(data)
#                 json_object = json.loads(json_data) 
#                 return(json.dumps(json_object, indent = 1))


#             message = "Cost matrix file is incorrect"
#             try:
#                 WKB = xlrd.open_workbook(params["District"][district]["DistanceFile"])
#             except:
#                 data = {}
#                 data["status"] = 0
#                 data["message"] = message
#                 data["district"] = district
#                 json_data = json.dumps(data)
#                 json_object = json.loads(json_data) 
#                 return(json.dumps(json_object, indent = 1))

#             Sheet1 = WKB.sheet_by_index(0)
#             Sheet2 = WKB.sheet_by_index(1)
#             Sheet3 = WKB.sheet_by_index(2)
#             Sheet4 = WKB.sheet_by_index(3)
#             Sheet5 = WKB.sheet_by_index(4)
#             Sheet6 = WKB.sheet_by_index(5)
#             Sheet7 = WKB.sheet_by_index(6)
#             Sheet8 = WKB.sheet_by_index(7)

#             Base_Godown = pd.read_excel(USN, sheet_name = 'Base_Godown', index_col = None)
#             Interior_Godown = pd.read_excel(USN, sheet_name = 'Interior_Godown', index_col = None)
#             FPS = pd.read_excel(USN, sheet_name = 'FPS', index_col = None)
#             FCI = pd.read_excel(USN, sheet_name = 'FCI', index_col = None)
#             Original_Tagging = pd.read_excel(USN, sheet_name = 'Original_Tagging', index_col = None)

#     #         additions for Map plot 
#             BG_set = set(Base_Godown["BG_Code"])

#             Coordinate = {}

#             for i in Base_Godown.index:
#                 Coordinate[Base_Godown["BG_Code"][i]] = {"lat": Base_Godown["BG_Lat"][i] , "long": Base_Godown["BG_Long"][i]}

#             for i in Interior_Godown.index:
#                 Coordinate[Interior_Godown["IG_Code"][i]] = {"lat": Interior_Godown["Interior_Lat"][i] , "long": Interior_Godown["Interior_Long"][i]}

#             for i in FPS.index:
#                 Coordinate[FPS["FPS_Code"][i]] = {"lat": FPS["FPS_Lat"][i] , "long": FPS["FPS_Long"][i]}

#             for i in FCI.index:
#                 Coordinate[FCI["FCI_Code"][i]] = {"lat": FCI["FCI_Lat"][i] , "long": FCI["FCI_Long"][i]}

#             mean_coord = {"lat": Base_Godown["BG_Lat"].mean(axis = 0), "long": Base_Godown["BG_Long"].mean(axis = 0)}

#             #Initialize LP Model 
#             model = LpProblem('Supply-Demand-Problem', LpMinimize)


#             Variable1 = []
#             Variable2 = []
#             Variable3 = []
#             Variable4 = []
#             Variable5 = []
#             Variable6 = []
#             Variable7 = []
#             Variable8 = []
#             Variable9 = []
#             Variable10 = []
#             Variable11 = []
#             Variable12 = []
#             Variable13 = []

#             Tehsil = {}
#             UniqueId = 0
#             Tehsil_temp = []
#             Tehsil_rev = {}

#             for i in FPS["Tehsil"]:
#                 Tehsil_temp.append(i)
#                 if i not in Tehsil:
#                     Tehsil[i] = UniqueId
#                     Tehsil_rev[UniqueId] = i
#                     UniqueId = UniqueId + 1


#             Tehsil_FPS = []
#             for i in range(len(FPS["FPS_Code"])):
#                 Tehsil_FPS.append(Tehsil[Tehsil_temp[i]])

#             Depot = {}
#             UniqueId = 0
#             Depot_temp = []
#             Depot_rev = {}

#             for i in Original_Tagging["Depot_code_org"]:
#                 Depot_temp.append(i)
#                 if i not in Depot:
#                     Depot[i] = UniqueId
#                     Depot_rev[UniqueId] = i
#                     UniqueId = UniqueId + 1


#             Depot_OriginalTagging = []
#             ogTagging_count = {}
#             for i in range(len(Original_Tagging["Depot_code_org"])):
#                 Depot_OriginalTagging.append(Depot[Depot_temp[i]])
#                 if (str(Original_Tagging["Depot_code_org"][i]) in ogTagging_count):
#                     pass
#                 else:
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])] = {}

#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["X"] = set()
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["Y"] = set()
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["X_amt"] = 0
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["Y_amt"] = 0

#                 if (Original_Tagging["Demand_Rice"][i] >0):
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["Y"].add(str(Original_Tagging["FPS_ID"][i]))
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["Y_amt"] += int(Original_Tagging["Demand_Rice"][i])

#                 if (Original_Tagging["Demand_Wheat"][i] >0):
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["X"].add(str(Original_Tagging["FPS_ID"][i]))
#                     ogTagging_count[str(Original_Tagging["Depot_code_org"][i])]["X_amt"] += int(Original_Tagging["Demand_Wheat"][i])


#             for i in ogTagging_count:
#                 ogTagging_count[i]["X"] = len(ogTagging_count[i]["X"])
#                 ogTagging_count[i]["Y"] = len(ogTagging_count[i]["Y"])


#             Depot_W = [[] for i in range(len(Depot))]
#             Depot_R = [[] for i in range(len(Depot))]
#             for i in range(len(Original_Tagging["Depot_code_org"])):
#                 Depot_W[Depot_OriginalTagging[i]].append(Original_Tagging["Demand_Wheat"][i])
#                 Depot_R[Depot_OriginalTagging[i]].append(Original_Tagging["Demand_Rice"][i])

#             OR_Wheat = {}
#             for i in range(len(Depot)):
#                 OR_Wheat[str(Depot_rev[i])] = str(lpSum(Depot_W[i]))

#             OR_Rice = {}
#             for i in range(len(Depot)):
#                 OR_Rice[str(Depot_rev[i])] = str(lpSum(Depot_R[i]))


#             for i in range(len(Base_Godown["BG_Code"])):
#                 for j in range(len(FPS["FPS_Code"])):
#                     Variable1.append(str(Base_Godown["BG_Code"][i]) + "_" + str(FPS["FPS_Code"][j]) + "_Wheat")
#                     Variable2.append(str(Base_Godown["BG_Code"][i]) + "_" + str(FPS["FPS_Code"][j]) + "_Rice")
#                 for k in range(len(Base_Godown["BG_Code"])):
#                     Variable3.append(str(Base_Godown["BG_Code"][i]) + "_" + str(Base_Godown["BG_Code"][k]) + "_Wheat")
#                     Variable4.append(str(Base_Godown["BG_Code"][i]) + "_" + str(Base_Godown["BG_Code"][k]) + "_Rice")
#                 for l in range(len(Interior_Godown["IG_Code"])):
#                     Variable5.append(str(Base_Godown["BG_Code"][i]) + "_" + str(Interior_Godown["IG_Code"][l]) + "_Wheat")
#                     Variable6.append(str(Base_Godown["BG_Code"][i]) + "_" + str(Interior_Godown["IG_Code"][l]) + "_Rice")

#             #Variables for Wheat from BG TO FPS  
#             DV_Variables1 = LpVariable.matrix("X",Variable1,cat="float",lowBound=0)
#             Allocation1 = np.array(DV_Variables1).reshape(len(Base_Godown["BG_Code"]),len(FPS["FPS_Code"]))

#             #Variables for rice from BG TO FPS
#             DV_Variables2 = LpVariable.matrix("Y",Variable2,cat="float",lowBound=0)
#             Allocation2 = np.array(DV_Variables2).reshape(len(Base_Godown["BG_Code"]),len(FPS["FPS_Code"]))

#             #Variables for Wheat from BG TO BG 
#             DV_Variables3 = LpVariable.matrix("X",Variable3,cat="float",lowBound=0)
#             Allocation3 = np.array(DV_Variables3).reshape(len(Base_Godown["BG_Code"]),len(Base_Godown["BG_Code"]))

#             #Variables for rice from BG TO BG
#             DV_Variables4 = LpVariable.matrix("Y",Variable4,cat="float",lowBound=0)
#             Allocation4 = np.array(DV_Variables4).reshape(len(Base_Godown["BG_Code"]),len(Base_Godown["BG_Code"]))

#             #Variables for Wheat from BG TO IG 
#             DV_Variables5 = LpVariable.matrix("X",Variable5,cat="float",lowBound=0)
#             Allocation5 = np.array(DV_Variables5).reshape(len(Base_Godown["BG_Code"]),len(Interior_Godown["IG_Code"]))

#             #Variables for rice from BG TO IG
#             DV_Variables6 = LpVariable.matrix("Y",Variable6,cat="float",lowBound=0)
#             Allocation6 = np.array(DV_Variables6).reshape(len(Base_Godown["BG_Code"]),len(Interior_Godown["IG_Code"]))


#             for i in range(len(Interior_Godown["IG_Code"])):
#                 for j in range(len(FPS["FPS_Code"])):
#                     Variable7.append(str(Interior_Godown["IG_Code"][i]) + "_" + str(FPS["FPS_Code"][j]) + "_Wheat")
#                     Variable8.append(str(Interior_Godown["IG_Code"][i]) + "_" + str(FPS["FPS_Code"][j]) + "_Rice")
#                 for k in range(len(Interior_Godown["IG_Code"])):
#                     Variable9.append(str(Interior_Godown["IG_Code"][i]) + "_" + str(Interior_Godown["IG_Code"][l]) + "_Wheat")
#                     Variable10.append(str(Interior_Godown["IG_Code"][i]) + "_" + str(Interior_Godown["IG_Code"][l]) + "_Rice")

#             #Variables for Wheat from IG TO FPS 
#             DV_Variables7 = LpVariable.matrix("X",Variable7,cat="float",lowBound=0)
#             Allocation7 = np.array(DV_Variables7).reshape(len(Interior_Godown["IG_Code"]),len(FPS["FPS_Code"]))

#             #Variables for rice from IG TO FPS
#             DV_Variables8 = LpVariable.matrix("Y",Variable8,cat="float",lowBound=0)
#             Allocation8 = np.array(DV_Variables8).reshape(len(Interior_Godown["IG_Code"]),len(FPS["FPS_Code"]))

#             #Variables for Wheat from IG TO IG 
#             DV_Variables10 = LpVariable.matrix("Y",Variable10,cat="float",lowBound=0)
#             Allocation10 = np.array(DV_Variables10).reshape(len(Interior_Godown["IG_Code"]),len(Interior_Godown["IG_Code"]))

#             for i in range(len(FCI["FCI_Code"])):
#                 for j in range(len(Base_Godown["BG_Code"])):
#                     Variable11.append(str(FCI["FCI_Code"][i]) + "_" + str(Base_Godown["BG_Code"][j]) + "_Wheat")
#                 for k in range(len(Interior_Godown["IG_Code"])):
#                     Variable12.append(str(FCI["FCI_Code"][i]) + "_" +str(Interior_Godown["IG_Code"][k]) + "_Wheat")
#                 for l in range(len(FPS["FPS_Code"])):
#                     Variable13.append(str(FCI["FCI_Code"][i]) + "_" +str(FPS["FPS_Code"][l]) + "_Wheat")

#             #Variables for Wheat from FCI TO BG 
#             DV_Variables11 = LpVariable.matrix("X",Variable11,cat="float",lowBound=0)
#             Allocation11 = np.array(DV_Variables11).reshape(len(FCI["FCI_Code"]),len(Base_Godown["BG_Code"]))

#             #Variables for rice from FCI TO IG
#             DV_Variables12 = LpVariable.matrix("Y",Variable12,cat="float",lowBound=0)
#             Allocation12 = np.array(DV_Variables12).reshape(len(FCI["FCI_Code"]),len(Interior_Godown["IG_Code"]))

#             #Variables for rice from FCI TO FPS
#             DV_Variables13 = LpVariable.matrix("Y",Variable13,cat="float",lowBound=0)
#             Allocation13 = np.array(DV_Variables13).reshape(len(FCI["FCI_Code"]),len(FPS["FPS_Code"]))


#             #Cost Matrix_BG_BG
#             BG_BG = []
#             for col in range(Sheet1.nrows):
#                 temp = []
#                 for row in range (Sheet1.ncols):
#                     temp.append(Sheet1.cell_value(col,row))
#                 BG_BG.append(temp)
#                 #print(BG_BG)

#             #Cost Matrix_BG_IG
#             BG_IG = []
#             for col in range(Sheet2.nrows):
#                 temp = []
#                 for row in range (Sheet2.ncols):
#                     temp.append(Sheet2.cell_value(col,row))
#                 BG_IG.append(temp)
#                 #print(BG_IG)

#             #Cost Matrix_BG_FPS
#             BG_FPS = []
#             for col in range(Sheet3.nrows):
#                 temp = []
#                 for row in range (Sheet3.ncols):
#                     temp.append(Sheet3.cell_value(col,row))
#                 BG_FPS.append(temp)
#                 #print(BG_FPS)

#             #Cost Matrix_IG_IG
#             IG_IG = []
#             for col in range(Sheet4.nrows):
#                 temp = []
#                 for row in range (Sheet4.ncols):
#                     temp.append(Sheet4.cell_value(col,row))
#                 IG_IG.append(temp)
#                 #print(IG_IG)

#             #Cost Matrix_IG_FPS
#             IG_FPS = []
#             for col in range(Sheet5.nrows):
#                 temp = []
#                 for row in range (Sheet5.ncols):
#                     temp.append(Sheet5.cell_value(col,row))
#                 IG_FPS.append(temp)
#                 #print(IG_FPS)

#             #Cost Matrix_FCI_BG
#             FCI_BG = []
#             for col in range(Sheet6.nrows):
#                 temp = []
#                 for row in range (Sheet6.ncols):
#                     temp.append(Sheet6.cell_value(col,row))
#                 FCI_BG.append(temp)
#                 #print(FCI_BG)

#             #Cost Matrix_FCI_IG
#             FCI_IG = []
#             for col in range(Sheet7.nrows):
#                 temp = []
#                 for row in range (Sheet7.ncols):
#                     temp.append(Sheet7.cell_value(col,row))
#                 FCI_IG.append(temp)
#                 #print(FCI_IG)

#              #Cost Matrix_FCI_IG

#             FCI_FPS = []
#             for col in range(Sheet8.nrows):
#                 temp = []
#                 for row in range (Sheet8.ncols):
#                     temp.append(Sheet8.cell_value(col,row))
#                 FCI_FPS.append(temp)
#                 #print(FCI_FPS)   


#             allCombination1 = []
#             allCombination2 = []
#             allCombination3 = []
#             allCombination4 = []
#             allCombination5 = []
#             allCombination6 = []
#             allCombination7 = []
#             allCombination8 = []
#             allCombination9 = []
#             allCombination10 = []
#             allCombination11 = []
#             allCombination12 = []
#             allCombination13 = []


#             for i in range(len(BG_BG)):
#                 for j in range(len(Base_Godown["BG_Code"])):
#                     allCombination3.append(Allocation3[i][j]*BG_BG[i][j])

#             for i in range(len(BG_BG)):
#                 for j in range(len(Base_Godown["BG_Code"])):
#                     allCombination4.append(Allocation4[i][j]*BG_BG[i][j])

#             for i in range(len(BG_IG)):
#                 for j in range(len(Interior_Godown["IG_Code"])):
#                     allCombination5.append(Allocation5[i][j]*BG_IG[i][j])

#             for i in range(len(BG_IG)):
#                 for j in range(len(Interior_Godown["IG_Code"])):
#                     allCombination6.append(Allocation6[i][j]*BG_IG[i][j])

#             for i in range(len(BG_FPS)):
#                 for j in range(len(FPS["FPS_Code"])):
#                     allCombination1.append(Allocation1[i][j]*BG_FPS[i][j])

#             for i in range(len(BG_FPS)):
#                 for j in range(len(FPS["FPS_Code"])):
#                     allCombination2.append(Allocation2[i][j]*BG_FPS[i][j])

#             for i in range(len(IG_IG)):
#                 for j in range(len(Interior_Godown["IG_Code"])):
#                     allCombination9.append(Allocation9[i][j]*IG_IG[i][j])

#             for i in range(len(IG_IG)):
#                 for j in range(len(Interior_Godown["IG_Code"])):
#                     allCombination10.append(Allocation10[i][j]*IG_IG[i][j])

#             for i in range(len(IG_FPS)):
#                 for j in range(len(FPS["FPS_Code"])):
#                     allCombination7.append(Allocation7[i][j]*IG_FPS[i][j])

#             for i in range(len(IG_FPS)):
#                 for j in range(len(FPS["FPS_Code"])):
#                     allCombination8.append(Allocation8[i][j]*IG_FPS[i][j])

#             for i in range(len(FCI_BG)):
#                 for j in range(len(Base_Godown["BG_Code"])):
#                     allCombination11.append(Allocation11[i][j]*FCI_BG[i][j])

#             for i in range(len(FCI_IG)):
#                 for j in range(len(Interior_Godown["IG_Code"])):
#                     allCombination12.append(Allocation12[i][j]*FCI_IG[i][j])

#             for i in range(len(FCI_FPS)):
#                 for j in range(len(FPS["FPS_Code"])):
#                     allCombination13.append(Allocation13[i][j]*FCI_FPS[i][j])


#             model += lpSum(allCombination1+allCombination2+allCombination3+allCombination4+allCombination5+allCombination6+allCombination7+allCombination8+allCombination9+allCombination10+allCombination11+allCombination12+allCombination13)


#             #Demand Constraints for Wheat in FPS
#             for i in range(len(FPS["FPS_Code"])): 
#                 #print(lpSum(Allocation1[j][i] for j in range(len(Base_Godown["BG_Code"])))+(lpSum(Allocation7[k][i] for j in range(len(Interior_Godown["IG_Code"]))))>=FPS["Demand_Wheat"][i])
#                 model+=(lpSum(Allocation1[j][i] for j in range(len(Base_Godown["BG_Code"])))+(lpSum(Allocation7[k][i] for j in range(len(Interior_Godown["IG_Code"]))))>=FPS["Demand_Wheat"][i])


#             #Demand Constraints for Rice in FPS
#             for i in range(len(FPS["FPS_Code"])): 
#                 #print(lpSum(Allocation2[j][i] for j in range(len(Base_Godown["BG_Code"])))+(lpSum(Allocation8[k][i] for j in range(len(Interior_Godown["IG_Code"]))))>=FPS["Demand_Rice"][i])
#                 model+=(lpSum(Allocation2[j][i] for j in range(len(Base_Godown["BG_Code"])))+(lpSum(Allocation8[k][i] for j in range(len(Interior_Godown["IG_Code"]))))>=FPS["Demand_Rice"][i])


#             #Capacity Constraints for Warehouses 
#             for i in range(len(Base_Godown["BG_Code"])):
#                 #print((lpSum(Allocation11[j][i] for j in range(len(FCI["FCI_Code"]))))+lpSum(Allocation3[k][i] for k in range(len(Base_Godown["BG_Code"])))+lpSum(Allocation4[l][i] for l in range(len(Base_Godown["BG_Code"])))-lpSum(Allocation1[i][m] for m in range(len(FPS["FPS_Code"])))-(lpSum(Allocation2[i][n] for n in range(len(FPS["FPS_Code"]))))-(lpSum(Allocation3[i][o] for o in range(len(Base_Godown["BG_Code"]))))-(lpSum(Allocation4[i][p] for p in range(len(Base_Godown["BG_Code"]))))-(lpSum(Allocation5[i][q] for q in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation6[i][r] for r in range(len(Interior_Godown["IG_Code"]))))<=Base_Godown["BG_Capacity"][i])
#                 model+=((lpSum(Allocation11[j][i] for j in range(len(FCI["FCI_Code"]))))+lpSum(Allocation3[k][i] for k in range(len(Base_Godown["BG_Code"])))+lpSum(Allocation4[l][i] for l in range(len(Base_Godown["BG_Code"])))-lpSum(Allocation1[i][m] for m in range(len(FPS["FPS_Code"])))-(lpSum(Allocation2[i][n] for n in range(len(FPS["FPS_Code"]))))-(lpSum(Allocation3[i][o] for o in range(len(Base_Godown["BG_Code"]))))-(lpSum(Allocation4[i][p] for p in range(len(Base_Godown["BG_Code"]))))-(lpSum(Allocation5[i][q] for q in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation6[i][r] for r in range(len(Interior_Godown["IG_Code"]))))<=Base_Godown["BG_Capacity"][i])



#             #Supply of Wheat in interior Godown
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 #print((lpSum(Allocation7[i][j] for j in range(len(FPS["FPS_Code"])))) +(lpSum(Allocation9[i][l] for l in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation9[n][i] for n in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation5[p][i] for p in range(len(Base_Godown["BG_Code"]))))-(lpSum(Allocation12[q][i] for q in range(len(FCI["FCI_Code"]))))<=0)
#                 model+=((lpSum(Allocation7[i][j] for j in range(len(FPS["FPS_Code"])))) +(lpSum(Allocation9[i][l] for l in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation9[n][i] for n in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation5[p][i] for p in range(len(Base_Godown["BG_Code"]))))-(lpSum(Allocation12[q][i] for q in range(len(FCI["FCI_Code"]))))<=0)

#             #Supply of Rice in interior Godown
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 #print((lpSum(Allocation8[i][j] for j in range(len(FPS["FPS_Code"])))) +(lpSum(Allocation10[i][l] for l in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation10[n][i] for n in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation6[p][i] for p in range(len(Base_Godown["BG_Code"]))))<=0)
#                 model+=((lpSum(Allocation8[i][j] for j in range(len(FPS["FPS_Code"])))) +(lpSum(Allocation10[i][l] for l in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation10[n][i] for n in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation6[p][i] for p in range(len(Base_Godown["BG_Code"]))))<=0)



#             #Capacity of the Interior Warehouse 
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 #print(lpSum(Allocation12[j][i] for j in range(len(FCI["FCI_Code"])))+lpSum(Allocation5[k][i] for k in range(len(Base_Godown["BG_Code"])))+(lpSum(Allocation6[l][i] for l in range(len(Base_Godown["BG_Code"]))))+(lpSum(Allocation9[m][i] for m in range(len(Interior_Godown["IG_Code"]))))+(lpSum(Allocation10[n][i] for n in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation9[i][o] for o in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation10[i][p] for p in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation7[i][q] for q in range(len(FPS["FPS_Code"]))))-(lpSum(Allocation8[i][r] for r in range(len(FPS["FPS_Code"]))))<=Interior_Godown["IG_Capacity"][i])
#                 model+=(lpSum(Allocation12[j][i] for j in range(len(FCI["FCI_Code"])))+lpSum(Allocation5[k][i] for k in range(len(Base_Godown["BG_Code"])))+(lpSum(Allocation6[l][i] for l in range(len(Base_Godown["BG_Code"]))))+(lpSum(Allocation9[m][i] for m in range(len(Interior_Godown["IG_Code"]))))+(lpSum(Allocation10[n][i] for n in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation9[i][o] for o in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation10[i][p] for p in range(len(Interior_Godown["IG_Code"]))))-(lpSum(Allocation7[i][q] for q in range(len(FPS["FPS_Code"]))))-(lpSum(Allocation8[i][r] for r in range(len(FPS["FPS_Code"]))))<=Interior_Godown["IG_Capacity"][i])



#             #Capacity of FCI for USN
#             for i in range(len(FCI["FCI_Code"])):
#                 #print(lpSum(Allocation11[i][j] for j in range(len(Base_Godown["BG_Code"])))+lpSum(Allocation12[i][k] for k in range(len(Interior_Godown["IG_Code"])))+lpSum(Allocation13[i][l] for l in range(len(FPS["FPS_Code"])))<=FCI["FCI_Capacity"][i])
#                 model+=(lpSum(Allocation11[i][j] for j in range(len(Base_Godown["BG_Code"])))+lpSum(Allocation12[i][k] for k in range(len(Interior_Godown["IG_Code"])))+lpSum(Allocation13[i][l] for l in range(len(FPS["FPS_Code"])))<=FCI["FCI_Capacity"][i])



#             #Calling CBC_CMB Solver for model
#             model.solve(PULP_CBC_CMD())
#             Status = LpStatus[model.status]

#             #print(Status)
#             #print("Total distance:", model.objective.value())

#             Original_Cost=Original_Tagging["Total"]*Original_Tagging["bing_dist"]
#             total=0
#             for i in range(0, len(Original_Cost)):
#                 total = total + Original_Cost[i]


#             data = {}
#             data['status'] = 1
#             data['modelStatus'] = Status
#             data['totalCost'] = round(model.objective.value(), 2)
#             data["original"] = round(total, 2)
#             data["percentageReduction"] = round(((total - model.objective.value())/total), 4)*100


#             BGW = {}
#             BGR = {}
#             IGW = {}
#             IGR = {}
#             FCIW = {}
#             BGCapacity = {}

#             temp = {}
#             for i in range(len(Base_Godown["BG_Code"])):
#                 temp[str(Base_Godown["BG_Code"][i])] = str(Base_Godown["BG_Capacity"])
#             BGCapacity = temp


#             temp1 = {}
#             BG_FPS = [[] for i in range(len(Tehsil))]
#             for i in range(len(Base_Godown["BG_Code"])):
#                 for j in range(len(FPS['FPS_Code'])):
#                     BG_FPS[Tehsil_FPS[j]].append(Allocation1[i][j].value())
#                 temp1[str(Base_Godown["BG_Code"][i])] = str(lpSum(Allocation1[i][j].value() for j in range(len(FPS["FPS_Code"]))))
#                 BGCapacity[str(Base_Godown["BG_Code"][i])] = str(Base_Godown["BG_Capacity"][i])
#             BGW["FPS"] = temp1

#             BG_FPS_Wheat = {}
#             for i in range(len(Tehsil)):
#                 BG_FPS_Wheat[str(Tehsil_rev[i])] = str(lpSum(BG_FPS[i]))


#             temp2 = {}
#             BG_FPS = [[] for i in range(len(Tehsil))]
#             for i in range(len(Base_Godown["BG_Code"])):
#                 for j in range(len(FPS['FPS_Code'])):
#                     BG_FPS[Tehsil_FPS[j]].append(Allocation2[i][j].value())
#                 temp2[str(Base_Godown["BG_Code"][i])] = str(lpSum(Allocation2[i][j].value() for j in range(len(FPS["FPS_Code"]))))
#             BGR["FPS"] = temp2

#             BG_FPS_Rice = {}
#             for i in range(len(Tehsil)):
#                 BG_FPS_Rice[str(Tehsil_rev[i])] = str(lpSum(BG_FPS[i]))


#             temp3 = {}
#             for i in range(len(Base_Godown["BG_Code"])):
#                 temp3[str(Base_Godown["BG_Code"][i])] = str(lpSum(Allocation3[i][j].value() for j in range(len(Base_Godown["BG_Code"]))))
#             BGW["BG"] = temp3


#             temp4 = {}
#             for i in range(len(Base_Godown["BG_Code"])):
#                 temp4[str(Base_Godown["BG_Code"][i])] = str(lpSum(Allocation4[i][j].value() for j in range(len(Base_Godown["BG_Code"]))))
#             BGR["BG"] = temp4


#             temp5 = {}
#             for i in range(len(Base_Godown["BG_Code"])):
#                 temp5[str(Base_Godown["BG_Code"][i])] = str(lpSum(Allocation5[i][j].value() for j in range(len(Interior_Godown["IG_Code"]))))
#             BGW["IG"] = temp5


#             temp6 = {}
#             for i in range(len(Base_Godown["BG_Code"])):
#                 temp6[str(Base_Godown["BG_Code"][i])] = str(lpSum(Allocation6[i][j].value() for j in range(len(Interior_Godown["IG_Code"]))))
#             BGR["IG"] = temp6


#             temp7 = {}
#             IG_FPS = [[] for i in range(len(Tehsil))]
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 for j in range(len(FPS['FPS_Code'])):
#                     IG_FPS[Tehsil_FPS[j]].append(Allocation7[i][j].value())
#                 temp7[str(Interior_Godown["IG_Code"][i])] = str(lpSum(Allocation7[i][j].value() for j in range(len(FPS["FPS_Code"]))))
#             IGW["FPS"] = temp7
#             for i in range(len(Tehsil)):
#                 BG_FPS_Wheat[str(Tehsil_rev[i])] = str(float(BG_FPS_Wheat[str(Tehsil_rev[i])]) + lpSum(IG_FPS[i]))

#             temp8 = {}
#             IG_FPS = [[] for i in range(len(Tehsil))]
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 for j in range(len(FPS['FPS_Code'])):
#                     IG_FPS[Tehsil_FPS[j]].append(Allocation8[i][j].value())
#                 temp8[str(Interior_Godown["IG_Code"][i])] = str(lpSum(Allocation8[i][j].value() for j in range(len(FPS["FPS_Code"]))))
#             IGR["FPS"] = temp8

#             for i in range(len(Tehsil)):
#                 BG_FPS_Rice[str(Tehsil_rev[i])] = str(float(BG_FPS_Rice[str(Tehsil_rev[i])]) + lpSum(IG_FPS[i]))

#             temp9 = {}
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 temp9[str(Interior_Godown["IG_Code"][i])] = str(lpSum(Allocation9[i][j].value() for j in range(len(Interior_Godown["IG_Code"]))))
#             IGW["IG"] = temp9


#             temp10 = {}
#             for i in range(len(Interior_Godown["IG_Code"])):
#                 temp10[str(Interior_Godown["IG_Code"][i])] = str(lpSum(Allocation10[i][j].value() for j in range(len(Interior_Godown["IG_Code"]))))
#             IGR["IG"] = temp10


#             temp11 = {}
#             for i in range(len(FCI["FCI_Code"])):
#                 temp11[str(FCI["FCI_Code"][i])] = str(lpSum(Allocation11[i][j].value() for j in range(len(Base_Godown["BG_Code"]))))
#             FCIW["BG"] = temp11


#             temp12 = {}
#             for i in range(len(FCI["FCI_Code"])):
#                 temp12[str(FCI["FCI_Code"][i])] = str(lpSum(Allocation12[i][j].value() for j in range(len(Interior_Godown["IG_Code"]))))
#             FCIW["IR"] = temp12

#             temp13 = {}
#             for i in range(len(FCI["FCI_Code"])):
#                 temp13[str(FCI["FCI_Code"][i])] = str(lpSum(Allocation13[i][j].value() for j in range(len(Interior_Godown["IG_Code"]))))
#             FCIW["FPSR"] = temp13


#             data["BGW"] = BGW
#             data["BGR"] = BGR
#             data["IGW"] = IGW
#             data["IGR"] = IGR
#             data["FCIW"] = FCIW
#             data["FPSW"] = BG_FPS_Wheat
#             data["FPSR"] = BG_FPS_Rice
#             data["BGCapacity"] = BGCapacity
#             data["OTW"] = OR_Wheat
#             data["OTR"] = OR_Rice


#             gmap = gmplot.GoogleMapPlotter(mean_coord["lat"], mean_coord["long"] , 9)
#             colors = ['#9932CC',
#             '#FF0000',
#             '#7FFF00',
#             '#2F4F4F',
#             '#00BFFF',
#             '#1E90FF',
#             '#FF00FF',
#             '#F8F8FF',
#             '#DAA520',
#             '#008000',
#             '#808080',
#             '#FFDAB9',
#             '#9400D3',
#             '#FFC0CB',
#             '#B0E0E6',
#             '#663399',
#             '#BC8F8F']

#             color = 0


#             data2 = {}
#             BG_plotted= {}
#             Output_File = open(district+".csv","w")
#             data['outputFile'] = district+".csv"
#             #Writing Values in output file
#             for v in model.variables():
#                 #print(v.name)
#                 Output_File.write(v.name + "\t" + str(v.value()) + "\n")
#                 if(v.value()>0):
#                     if (v.name.split("_")[1] in data2):
#                         data2[v.name.split("_")[1]][v.name.split("_")[0]].add(v.name.split("_")[2])
#                     else:
#                         data2[v.name.split("_")[1]] = {}
#                         data2[v.name.split("_")[1]]["X"] = set()
#                         data2[v.name.split("_")[1]]["Y"] = set()

#                         data2[v.name.split("_")[1]][v.name.split("_")[0]].add(v.name.split("_")[2])

#                     if(int(v.name.split("_")[1]) in BG_set):
#                         lat_list = []
#                         long_list = []

#                         lat_list.append(Coordinate[int(v.name.split("_")[1])]['lat'])
#                         long_list.append(Coordinate[int(v.name.split("_")[1])]['long'])

#                         if(int(v.name.split("_")[1]) in BG_plotted):
#                             pass
#                         else:
#                             gmap.marker(lat_list[0], long_list[0], colors[color], size = 40, title= v.name.split("_")[1])
#                             BG_plotted[int(v.name.split("_")[1])] = colors[color]
#                             color +=1

#                         lat_list.append(Coordinate[int(v.name.split("_")[2])]['lat'])
#                         long_list.append(Coordinate[int(v.name.split("_")[2])]['long'])

#                         gmap.scatter(lat_list[0:2], long_list[0:2], marker = False)
#                         gmap.plot(lat_list[0:2], long_list[0:2], BG_plotted[int(v.name.split("_")[1])], edge_width = 3.0)


#             maps = district +".html"
#             gmap.draw(maps)


#             for i in data2:
#                 for j in data2[i]:
#                     data2[i][j] = len(data2[i][j])

#             data["tagging"] = data2
#             data["og_tagging"] = ogTagging_count
#             DistrictData[district] = data

#     json_data = json.dumps(DistrictData)
#     json_object = json.loads(json_data) 

    
#     if os.path.exists("ouputPickle.pkl"):
#         os.remove("ouputPickle.pkl")

#     # open pickle file
#     dbfile = open('ouputPickle.pkl', 'ab')
      
#     # save pickle data
#     pickle.dump(json_object, dbfile)                     
#     dbfile.close()
    
#     return(json.dumps(json_object, indent = 1))
