from ast import Global
from glob import glob
from django import db
from django.db.models.aggregates import Sum
from django.db.models.expressions import Case, When
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
import pandas as pd
from pandas.core.dtypes.missing import notnull
from pandas.core.frame import DataFrame
import numpy as np 
# from sqlalchemy import create_engine
from .models import Zpp
from .models import Material 
from .models import Result 
from .models import Coois 
from django.db.models import Count
from datetime import datetime, time, timedelta,date
import time
import psycopg2
from io import StringIO
import os 

def calcul(request):
    # Connection to db
    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432')  
    
    # Get Current Week and Year
    week=(date.today().isocalendar()[1])
    year=date.today().isocalendar()[0]
    #for the last week in the year
    if week==0:
        week=52
        year=year-1

    # holidaysfile=r"\\sp-is.lat.corp\sites\PlanifProd\MasterDataPDP\CALENDRIER_SITE_2022_C.xlsx"
    holidaysfile=r"\\prfoufiler01\donnees$\Public\input_adherence_41\CALENDRIER_SITE_2022_D.xlsx"

    
    global dh #define calendar as global variable
    dh=pd.read_excel(holidaysfile)
    dh=dh.rename(columns={'FOU-2110':'2110','LAB-2000':'2000','LEC-2030':'2030','LIP-2020':'2020','COL-2010':'2010','HBG-2200':'2200','HER-2300':'2300','CAS-2400':'2400','BEL-2500':'2500','LAV-2600':'2600','QRO-2320':'2320'})
    
    for col in dh.columns:
        dh[col]= pd.to_datetime(dh[col],format='%d/%m/%Y').dt.date
    #upload files
    start_time = time.time()
    print('start import')
    upload_material(conn,week,year)
    upload_coois(conn,week,year)
    upload_zpp(conn,week,year)

    print('Time for upload files')
    end_import=time.time()
    print(end_import-start_time)

    start_time=time.time()
    #Get data from DB
    zpp_data=Zpp.objects.all().filter(week=week)
    coois_data=Coois.objects.all().filter(week=week)
    material_data=Material.objects.all().filter(week=week,manager='ISM')
    # convert tables to DataFrame
    dz=pd.DataFrame(list(zpp_data.values()))
    dc=pd.DataFrame(list(coois_data.values()))
    dm=pd.DataFrame(list(material_data.values()))

    #Merge COOIS and ZPP
    r1=pd.merge(dz,dc, on=["material","order","year","week"])
    r1['division_x']=r1['division_x'].astype(np.int64,errors='ignore')
    # r1.to_csv('r1.csv',index=False);
    #Merge Material and the result betwwen COOIS and ZPP
    merge=pd.merge(r1,dm, left_on=["material","division_x","year","week"],right_on=["material","division","year","week"])
    # merge.to_csv('merge.csv',index=False);

    #Apply formula 
    merge["H1_jo"]=merge["cycle_manuf"]+10
    merge["H2_jo"]=merge["cycle_manuf"]+merge["cycle_appro"]
    merge["H3_jo"]=merge["cycle_manuf"]+merge["H2_jo"]
    merge["H4_jo"]=merge["H3_jo"]+30
    
    print('end merge')

    start_time = time.time()
    datalist=[]
    for index,item in merge.iterrows():
        # print(index)
        H1=H2=H3=H4_global=after_H4_global=H1_M10=H1_M15=H1_M20=H1_unfix=H2_M10=H2_M15=H2_M20=H2_unfix=H3_M10=H3_M15=H3_M20=H3_unfix=after_H4_global_fix=H1_10_P=H2_10_P=H3_10_P=H1_15_P=H2_15_P=H3_15_P=0 
        #----------------------------------------------------------
        H1_end=add_working_days(date.today(),item["H1_jo"],item["division"])
        H2_end=add_working_days(date.today(),item["H2_jo"],item["division"])
        H3_end=add_working_days(date.today(),item["H3_jo"],item["division"])
        H4_end=add_working_days(date.today(),item["H4_jo"],item["division"])   

        H4_global_end=date(1990,1,1)  

        if item["date_reordo"] is None:
            date_reference=item["date_available"]
        elif item["date_available"] < item["date_reordo"]:
            date_reference=item["date_available"]
        else:
            date_reference=item["date_reordo"]
        if date_reference <= H1_end:
            H1=1
        if date_reference <= H2_end:
            H2=1
        if date_reference <= H3_end:
            H3=1

        if  H1==1 and item["message"] == 10:
            H1_M10=1
        if  H1==1 and item["message"] == 15:
            H1_M15=1
        if  H1==1 and item["message"] == 20:
            H1_M20=1
        # if  H1==1 and item["fixation"] == "X":
        #     H1_unfix=1
        if  (H1==1) and (item["fixation"] != "X") and (item["order_type"].startswith('K') or item["order_type"].startswith('L')):
            H1_unfix=1
        if  H2==1 and item["message"] == 10:
            H2_M10=1
        if  H2==1 and item["message"] == 15:
            H2_M15=1
        if  H2==1 and item["message"] == 20:
            H2_M20=1
        # if  H2==1 and item["fixation"] == "X":
        #     H2_unfix=1
        if  (H2==1) and (item["fixation"] != "X") and (item["order_type"].startswith('K') or item["order_type"].startswith('L')):
            H2_unfix=1
        if  H3==1 and item["message"] == 10:
            H3_M10=1
        if  H3==1 and item["message"] == 15:
            H3_M15=1
        if  H3==1 and item["message"] == 20:
            H3_M20=1
        # if  H3==1 and item["fixation"] == "X":
        #     H3_unfix=1
        if  (H3==1) and (item["fixation"] != "X") and (item["order_type"].startswith('K') or item["order_type"].startswith('L')):
            H3_unfix=1
        # profondeur=diff_date(item["date_available"],item["date_reordo"],item["division"])
        profondeur=diff_date(item["date_reordo"],item["date_available"],item["division"])
        if H1 == 1 and item["message"] ==10 and profondeur < -5 :
            H1_10_P=1
        if H2 == 1 and item["message"] ==10 and profondeur < -5 :
            H2_10_P=1
        if H2 == 1 and item["message"] ==10 and profondeur < -5 :
            H2_10_P=1
        if H3 == 1 and item["message"] ==10 and profondeur < -5 :
            H3_10_P=1
        if H1 == 1 and item["message"] ==15 and profondeur >20 and item["type"] == 'Banalisé' :
            H1_15_P=1
        if H1 == 1 and item["message"] ==15 and profondeur >10 and item["type"] == 'Individuel' :
            H1_15_P=1   
        if H2 == 1 and item["message"] ==15 and profondeur >20 and item["type"] == 'Banalisé' :
            H2_15_P=1
        if H2 == 1 and item["message"] ==15 and profondeur >10 and item["type"] == 'Individuel' :
            H2_15_P=1
        if H3 == 1 and item["message"] ==15 and profondeur >20 and item["type"] == 'Banalisé' :
            H3_15_P=1
        if H3 == 1 and item["message"]==15 and profondeur >10 and item["type"] == 'Individuel' :
            H3_15_P=1  


        data=[
            year,
            week,
            item["division"],
            item["profit_centre_y"],
            item["order"],
            item["material"],
            item["designation"],
            item["order_type"],
            item["order_quantity"],
            item["date_start_plan"],
            item["date_end_plan"], 
            item["fixation"],
            item["manager_y"],
            item["order_stat"],
            item["request"],
            item["date_end_real"],
            item["entered_by"],
            item["date_available"],
            item["date_reordo"],
            item["message"],
            item["element"],
            item["planning"],
            item["type"],
            item["H1_jo"],
            item["H2_jo"],
            item["H3_jo"],
            item["H4_jo"],
            H1_end,
            H2_end,
            H3_end,
            H4_end,
            H4_global_end,
            date_reference,
            H1,
            H2,
            H3,
            H4_global,
            after_H4_global,
            H1_M10,
            H1_M15,
            H1_M20,
            H1_unfix,
            H2_M10,
            H2_M15,
            H2_M20,
            H2_unfix,
            H3_M10,
            H3_M15,
            H3_M20,
            H3_unfix,
            after_H4_global_fix,
            profondeur,
            H1_10_P,
            H2_10_P,
            H3_10_P,
            H1_15_P,
            H2_15_P,
            H3_15_P
            ]
        datalist.append(data)
    end_time = time.time()

    
    dataResult=pd.DataFrame(data=datalist,columns=['year',
                                                'week',
                                                'division',
                                                'profit_centre',
                                                'order',
                                                'material',
                                                'designation',
                                                'order_type',
                                                'order_quantity',
                                                'date_start_plan',
                                                'date_end_plan',
                                                'fixation',
                                                'manager',
                                                'order_stat',
                                                'request',
                                                'date_end_real',
                                                'entered_by',
                                                'date_available',
                                                'date_reordo',
                                                'message',
                                                'element',
                                                'planning',
                                                'type',
                                                'H1_jo',
                                                'H2_jo',
                                                'H3_jo',
                                                'H4_jo',
                                                'H1_end',
                                                'H2_end',
                                                'H3_end',
                                                'H4_end',
                                                'H4_global_end',
                                                'date_reference',
                                                'H1',
                                                'H2',
                                                'H3',
                                                'H4_global',
                                                'after_H4_global',
                                                'H1_M10',
                                                'H1_M15',
                                                'H1_M20',
                                                'H1_unfix',
                                                'H2_M10',
                                                'H2_M15',
                                                'H2_M20',
                                                'H2_unfix',
                                                'H3_M10',
                                                'H3_M15',
                                                'H3_M20',
                                                'H3_unfix',
                                                'after_H4_global_fix',
                                                'profondeur',
                                                'H1_10_P',
                                                'H2_10_P',
                                                'H3_10_P',
                                                'H1_15_P',
                                                'H2_15_P',
                                                'H3_15_P'
                                                ])
    
    #Get the max and transform it into column
    # dataResult["H4_global_end"]=dataResult.groupby(['division','profit_centre','planning'])['H4_end'].transform(np.max)
    dataResult["H4_global_end"]=dataResult.groupby(['profit_centre','planning'])['H4_end'].transform(np.max)

    dataResult.loc[dataResult["date_reference"] <= dataResult["H4_global_end"], 'H4_global'] = 1
    dataResult.loc[dataResult["date_reference"] >= dataResult["H4_global_end"], 'after_H4_global'] = 1
    dataResult.loc[(dataResult["after_H4_global"] == 1) & (dataResult["fixation"] == "X"), 'after_H4_global_fix'] = 1  

    end_traitement = time.time()

    print('_____Time for Traitement _________')
    print(end_traitement - start_time)
    print('__________________________________')  
    start_time = time.time()


    result = StringIO()
    result.write(dataResult.to_csv(index=None, header=None))
    result.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=result,
            table="adherence_result",
            columns=[
                'year',
                'week',
                'division',
                'profit_centre',
                'order',
                'material',
                'designation',
                'order_type',
                'order_quantity',
                'date_start_plan',
                'date_end_plan',
                'fixation',
                'manager',
                'order_stat',
                'request',
                'date_end_real',
                'entered_by',
                'date_available',
                'date_reordo',
                'message',
                'element',
                'planning',
                'type',
                'H1_jo',
                'H2_jo',
                'H3_jo',
                'H4_jo',
                'H1_end',
                'H2_end',
                'H3_end',
                'H4_end',
                'H4_global_end',
                'date_reference',
                'H1',
                'H2',
                'H3',
                'H4_global',
                'after_H4_global',
                'H1_M10',
                'H1_M15',
                'H1_M20',
                'H1_unfix',
                'H2_M10',
                'H2_M15',
                'H2_M20',
                'H2_unfix',
                'H3_M10',
                'H3_M15',
                'H3_M20',
                'H3_unfix',
                'after_H4_global_fix',
                'profondeur',
                'H1_10_P',
                'H2_10_P',
                'H3_10_P',
                'H1_15_P',
                'H2_15_P',
                'H3_15_P'
            ],
            null="",
            sep=","
        )
    conn.commit()



    global total_time
    end_time = time.time()
    total_time = end_time - start_time
    print('_____Time for save Result_________')
    print("Time: ", total_time,' secondes')
    print('__________________________________')  


    return home(request)

def home(request):
    try:
        username=request.META['REMOTE_USER']
    except:
        username=''

    
    # username=''

    current_week=(date.today().isocalendar()[1])
    current_year=date.today().isocalendar()[0]

    overview=''
    indicatorweek=''
    indicator=''
    indicator_list_weeks=''
    year_weeks= Result.objects.values_list('year','week').distinct()
    yearavailable=set()
    weekavailable=set()
    for year,week in year_weeks:
        yearavailable.add(year)
        weekavailable.add(week)
    yearavailable=list(yearavailable)
    weekavailable=list(weekavailable)
    year=[]
    week=[]
    division=[]
    profit_center=[]
    if request.method == 'POST':
        division=request.POST.getlist('division')
        year=request.POST.getlist('year')
        week=request.POST.getlist('week')
        profit_center=request.POST.getlist('profit_center')

    # coois_data=all_coois_data
    message_error=''
    if len(year) > 0:
        result=Result.objects.all().filter(year__in=year,week__in=week)
        if len(division) > 0:
                result=result.filter(division__in=division)
        if len(profit_center) > 0:
                result=result.filter(profit_centre__in=profit_center)
    else:
        result=Result.objects.all().filter(year=current_year,week=current_week)  
    dr=pd.DataFrame(list(result.values()))

    # dr.to_csv('result.csv',index=False)
    if result:
        overview = dr.groupby(
                                ['year','week','division','profit_centre','planning']).agg({'profondeur':'mean'
                                                                                            , 'H1': 'sum'
                                                                                            , 'H2': 'sum'
                                                                                            , 'H3': 'sum'
                                                                                            ,'H4_global': 'sum'
                                                                                            ,'after_H4_global': 'sum'
                                                                                            ,'H1_M10': 'sum'
                                                                                            ,'H1_M15': 'sum'
                                                                                            ,'H1_M20': 'sum'
                                                                                            ,'H1_unfix': 'sum'
                                                                                            ,'H2_M10': 'sum'
                                                                                            ,'H2_M15': 'sum'
                                                                                            ,'H2_M20': 'sum'
                                                                                            ,'H2_unfix': 'sum'
                                                                                            ,'H3_M10': 'sum'
                                                                                            ,'H3_M15': 'sum'
                                                                                            ,'H3_M20': 'sum'
                                                                                            ,'H3_unfix': 'sum'
                                                                                            ,'after_H4_global_fix': 'sum'
                                                                                            ,'H1_10_P': 'sum'
                                                                                            ,'H2_10_P': 'sum'
                                                                                            ,'H3_10_P': 'sum'
                                                                                            ,'H1_15_P': 'sum'
                                                                                            ,'H2_15_P': 'sum'
                                                                                            ,'H3_15_P': 'sum'

                                                                                            }).reset_index()        
        
        #Severity Ordo calcul
        overview["severity_ordo"]=np.where(overview["H1"] >0,
        ((overview["H1"]-overview["H1_10_P"]-overview["H1_15_P"]-overview["H1_M20"]-overview["H1_unfix"])*100+(overview["H1_15_P"]*25))/overview["H1"],100)
        
        # # Severity MPS calcul 
        overview["severity_mps"]=np.where(((overview["H3"]-overview["H1"])+overview["after_H4_global_fix"]) >0,
        (((overview["H3"]-overview["H1"]) 
        - (overview["H3_10_P"]-overview["H1_10_P"])
        -(overview["H3_15_P"]-overview["H1_15_P"])
        -(overview["H3_M20"]-overview["H1_M20"])
        -(overview["H3_unfix"]-overview["H1_unfix"]))*100+((overview["H3_15_P"]-overview["H1_15_P"])*25+overview["after_H4_global_fix"]*37.5))
        /((overview["H3"]-overview["H1"])+(overview["after_H4_global_fix"])),
        100)

        #SCHED OK?
        overview["schedule"]=np.where((overview["H1_M10"] == 0) & (overview["H1_15_P"] ==0) & (overview["H1_M20"] == 0) & (overview["H1_unfix"] ==0),'True' ,'False')
        
        #MPS Ok?
        overview["mps"]=np.where(((overview["H3"]-overview["H1_M10"])< 20) & 
        ((overview["H3"]-overview["H1_15_P"]) <30 ) & 
        ((overview["H3"]-overview["H1_10_P"]) ==0 ) & 
        ((overview["H3"]-overview["H1_M20"]) == 0 ) & 
        ((overview["H3"]-overview["H1_unfix"]) == 0 ) & 
        (overview["after_H4_global_fix"] == 0 ),'True' ,'False')


        # indicator=overview.groupby(['division','year','week']).agg({'severity_ordo':'mean','severity_mps':'mean'}).reset_index().sort_values(by=['week'])
        indicator=overview.groupby(['year','week','division']).agg({'severity_ordo':'mean','severity_mps':'mean'}).unstack().fillna(0).stack().reset_index().sort_values(by=['year','week'])
        indicator['year_week']= indicator['year'].astype(str)+'_'+indicator['week'].astype(str)
        indicator_list_year_weeks=indicator.year_week.unique()
        indicator_list_division=indicator.division.unique()
        indicator_list_weeks=overview.week.unique()
        indicator_list_weeks=list(indicator_list_weeks)
        indicatorweek=overview.groupby(['division']).agg({'severity_ordo':'mean','severity_mps':'mean'}).reset_index() 
        print(indicator)
    return render (request,"adherence/index.html",{'username':username,'weekavailable':weekavailable,'yearavailable':yearavailable,'current_week':current_week,'current_year':current_year,
    'years':year,'weeks':week,'divisions':division,'profit_center':profit_center,'message_error':message_error,
    'overview':overview,'indicator':indicator,
    'indicatorweek':indicatorweek,'indicator_list_weeks':indicator_list_weeks,'indicator_list_year_weeks':indicator_list_year_weeks,'indicator_list_division':indicator_list_division
    })






def add_working_days(start_date, added_days,division):

    days_elapsed = 0
    if start_date.weekday()!=0:
        start_date=start_date-timedelta(days=(start_date.weekday()))
    while days_elapsed < added_days:
        test_date = start_date+timedelta(days=1)
        start_date = test_date
        if test_date.weekday()>4 :
            continue
        # elif test_date in list(dh[str(division)]): 
        # elif (pd.Timestamp(test_date).date() == dh[str(division)]).any(): 
        elif pd.Timestamp(test_date).date() in dh[str(division)].values: 
            continue
        else:
            days_elapsed += 1

    return start_date

def diff_date(reordo,available,division):

    diff=0
    if reordo is None:
        diff=0
    else:
        if reordo < available:
            delta=available-reordo
            for i in range(delta.days):
                day = reordo + timedelta(days=i)
                # if day.weekday()>4 or day in division_holiday:
                # if division in ['2300','2320','2500']:
                #     if day.weekday()>5 or day in list(dh[str(division)]):
                        
                #         # if a weekend or  holiday, skip
                #         continue
                    #     # if a workday, count as a day
                if day.weekday()>4: 
                        # if a weekend or  holiday, skip
                        continue
                # elif (pd.Timestamp(day).date() == dh[str(division)]).any():
                elif pd.Timestamp(day).date() in dh[str(division)].values:
                    continue
                else:
                    # if a workday, count as a day
                    diff+= 1
        else:
            delta = reordo - available       # as timedelta
            for i in range(delta.days):
                day = available + timedelta(days=i)
                # if day.weekday()>4 or day in division_holiday:
                # if division in ['2300','2320','2500']:
                #     if day.weekday()>5 or day in list(dh[str(division)]):
                        
                #         # if a weekend or  holiday, skip
                #         continue
                    #     # if a workday, count as a day
                if day.weekday()>4: 
                        # if a weekend or  holiday, skip
                        continue
                # elif (pd.Timestamp(day).date() == dh[str(division)]).any():
                elif pd.Timestamp(day).date() in dh[str(division)].values:
                #     print(day)
                    continue
                else:
                    # if a workday, count as a day
                    diff+= 1


        if reordo < available:
            diff= diff*(-1)
    return diff


def upload_material(conn,week,year):
    #Get Material File
    materialfile = r"\\prfoufiler01\donnees$\Public\input_adherence_41\Articles SAP - Identification Planif.xlsx"
    #Select column to use
    dm = pd.read_excel(materialfile,usecols="A:L")  
    #convert some column due to importing problems
    dm['Centre de profit'] = dm['Centre de profit'].fillna(0).astype(np.int64)
    dm['Division'] = dm['Division'].fillna(0).astype(np.int64)
    dm['Cycle manuf. JO'] = dm['Cycle manuf. JO'].fillna(0).astype(np.int64)
    dm["Clef d'horizon"] = dm["Clef d'horizon"].fillna(0).astype(np.int64)
    #Delete column with emty material
    dm = dm.dropna(subset=['Article'])
    #Add Columns Week and Year
    dm.insert(0,'week',week,True)
    dm.insert(1,'year',year,True)
    # Import to db
    material = StringIO()
    material.write(dm.to_csv(index=None,sep=";" , header=None))
    material.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=material,
            table="adherence_material",
            columns=[
                'week',
                'year',
                'profit_centre',
                'material',
                'division',
                'manager',
                'type',
                'planning',
                'comment',
                'cycle_appro',
                'cycle_manuf',	
                'key_horizon',
                'security_deadline',
                'reception_time'
            ],
            null="",
            sep=";"
        )
    conn.commit()


def upload_coois(conn,week,year):
    #Get Coois File
    cooisfile = r"\\prfoufiler01\donnees$\Public\input_adherence_41\COOIS_GLOBAL BEFORE MRP.XLSX"
    # cooisfile = r"\\prfoufiler01\donnees$\Public\coois\COOIS_GLOBAL BEFORE MRP.XLSX"
    # \\prfoufiler01\donnees$\Public\coois
    # cooisfile = r"http://sp-is.lat.corp/sites/MRPC/ExtractSAP/COOIS_GLOBAL%20BEFORE%20MRP%20202143.XLSX"
    
    dc = pd.read_excel(cooisfile)
    print("#"*50)
    print("COOIS File")
    print(dc.head())
    print("#"*50)

    #Rename columns
    dc=dc.rename(columns={
                        'Division':'division',
                        'Centre de profit':'profit_center',
                        'Order':'order',
                        'Numéro article':'material',	
                        'Désignation article':'designation'	,
                        "Type d'ordre":	'order_type',
                        "Quantité d'ordre (GMEIN)":	'order_quantity',
                        'Date début planifié':	'date_start_plan',
                        'Date fin planifiée':'date_end_plan',	
                        'Code fixation'	:'fixation',
                        'Gestionnaire':	'manager',
                        'Statut système': 'order_stat',
                        'Commande client':'order_stat',
                        'Date fin réelle': 'date_end_real',	
                        'Saisi par': 'entered_by'
                        })
    #Add Columns Week and Year
    dc.insert(0,'year',year,True)
    dc.insert(1,'week',week,True)
    #Format Column date_available and date_reordo To date format DB
    dc['date_start_plan'] = pd.to_datetime(dc['date_start_plan'],format='%d/%m/%Y').dt.date
    dc['date_end_plan'] =   pd.to_datetime(dc['date_end_plan'],format='%d/%m/%Y').dt.date
    dc['date_end_real'] =   pd.to_datetime(dc['date_end_real'],format='%d/%m/%Y').dt.date
    #Convert to csv and import, "convert to csv to copy with psycopg2"
    coois = StringIO()
    coois.write(dc.to_csv(index=None , header=None))
    coois.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=coois,
            table="adherence_coois",
            columns=[
                'year',
                'week',
                'division',
                'profit_centre',
                'order',
                'material', 
                'designation',
                'order_type',
                'order_quantity',
                'date_start_plan',
                'date_end_plan',
                'fixation',
                'manager',
                'order_stat',
                'request',
                'date_end_real',
                'entered_by'
            ],
            null="",
            sep=",",

        )
    conn.commit()

def upload_zpp(conn,week,year):
    zppfile ={
        "2110":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2110 ZPP_MD_STOCK BEFORE MRP.xls",
        "2000":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2000 ZPP_MD_STOCK BEFORE MRP.xls",
        "2030":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2030 ZPP_MD_STOCK BEFORE MRP.xls",
        "2020":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2020 ZPP_MD_STOCK BEFORE MRP.xls",
        "2010":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2010 ZPP_MD_STOCK BEFORE MRP.xls",
        "2200":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2200 ZPP_MD_STOCK BEFORE MRP.xls",
        "2300":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2300 ZPP_MD_STOCK BEFORE MRP.xls",
        "2400":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2400 ZPP_MD_STOCK BEFORE MRP.xls",
        "2500":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2500 ZPP_MD_STOCK BEFORE MRP.xls",
        "2600":r"\\prfoufiler01\donnees$\Public\input_adherence_41\2600 ZPP_MD_STOCK BEFORE MRP.xls",
        # "2320":r"\\sp-is.lat.corp\sites\MRPC\ExtractSAP\2320 ZPP_MD_STOCK BEFORE MRP.xls",  #There's no production yet
        }
    for division,file in zppfile.items():
        # dz = pd.read_csv(file, sep='\t', encoding='utf-16le',names=['A','material','date_available', 'D', 'E','element', 'G', 'H', 'I','order','message','L','M','date_reordo','O','P'])
        dz = pd.read_csv(file, sep='\t', encoding='utf-16le',names=['A','material','date_available', 'D', 'E','element', 'G', 'H', 'I','order','message','L','M','date_reordo','O','P','Q','R','S'])
        dz=dz.drop(columns=['A', 'D', 'E', 'G', 'H', 'I','L','M','O','P','Q','R','S']) #Drop unused columns
        dz=dz.drop(dz[dz.material=='Article'].index) #Drop row contain article in column material
        dz=dz.drop(dz[dz.material==''].index) #Drop row null
        dz = dz.dropna(how='all') #Drop rows with all column is null
        dz['order']=dz['order'].str.split("/").str[0] #Split to get orders
        dz['order']=dz['order'].str.lstrip("0") #Remove the leading zero before a number
        # dz['order'] = dz['order'].fillna(0).astype(np.int64,errors='ignore')
        dz['message'] = pd.to_numeric(dz['message'], errors='ignore',downcast='signed').fillna(0).astype(np.int64) #convert to integer and replace Nan with 0
        #Format Column date_available and date_reordo To date format DB
        dz['date_available'] = pd.to_datetime(dz['date_available'], format='%d.%m.%Y').dt.date
        dz['date_reordo'] = pd.to_datetime(dz['date_reordo'], format='%d.%m.%Y').dt.date

        #Add Columns Week and Year
        dz.insert(3,'year',year,True)
        dz.insert(4,'week',week,True)
        dz.insert(5,'division',division,True)

        zpp = StringIO()
        zpp.write(dz.to_csv(index=None, header=None))
        zpp.seek(0)
        with conn.cursor() as c:
            c.copy_from(
                file=zpp,
                table="adherence_zpp",
                columns=[
                    "material",
                    "date_available",
                    "element",
                    "year",
                    "week",
                    "division",
                    "order",
                    "message",
                    "date_reordo"
                ],
                null="",
                sep=","
            )
        conn.commit()
    '''Time execution'''


