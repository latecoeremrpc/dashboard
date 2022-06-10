import datetime
from email import message
from io import StringIO
from operator import index
import os
from queue import Empty
from tkinter import FLAT
from django.shortcuts import render
import pandas as pd
import numpy as np
import psycopg2
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from os.path import exists
from django.http import HttpResponse



from ofpast.models import Coois,Koc4
from homepage.models import HomeKpi




def upload_files(request):
    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432') 
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    

    #Improt Files
    if current_week < 10:
        current_week=str(0)+str(current_week)
    coois_file=r"\\sp-is.lat.corp\sites\MRPC\Dashboard Data\web_dashboard\COOIS - OF PASSE\COOIS\COOIS_OF_PASSE_"+format(current_year)+format(current_week)+".XLSX"
    koc_file=r"\\sp-is.lat.corp\sites\MRPC\Dashboard Data\web_dashboard\COOIS - OF PASSE\KOC4\KOC4_OF_PASSE_"+format(current_year)+format(current_week)+".XLSX"

    coois_exists = exists(coois_file)
    koc_exists = exists(koc_file)
    message_error=''
    if coois_exists and koc_exists:
        import_coois(coois_file,current_year,current_week,conn)
        import_koc4(koc_file,current_year,current_week,conn) 

        return home(request)
    else:
        message_error='Unable to upload files, not exist or unreadable!'
        weekavailable=Coois.objects.all().values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
        week=[]

        return render(request,'ofpast/index.html',{'message_error':message_error,'weekavailable':weekavailable,'current_week':current_week,'current_year':current_year,'week':week})


def home(request):
    username=request.META['REMOTE_USER']
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    homekpi=list(HomeKpi.objects.all().filter(username=username).values_list('kpi',flat=True))

    division=[]
    profit_center=[]
    week=[]
    year=[]

    #Count per week per devision
    all_coois_data=Coois.objects.all()
    weekavailable=all_coois_data.values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
    yearavailable=all_coois_data.values_list('year',flat=True).distinct() #flat=True will remove the tuples and return the list  

    #Cost per week per devision
    all_koc4_data=Koc4.objects.all()
    # weekavailable=all_koc4_data.values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
    # yearavailable=all_koc4_data.values_list('year',flat=True).distinct() #flat=True will remove the tuples and return the list  

    # Get Data and convert to dataframe 
    dc=pd.DataFrame(list(all_coois_data.values()))
    dk=pd.DataFrame(list(all_koc4_data.values('material','cost_real')))
    # dc.merge(dk,on='material',suffixes=('_coois', '_koc4'))
    # dc.to_csv('merge_coois_koc4',index=False)
    #Global Count
    ofpast_divisions=dc.division.unique()
    ofpast_allweeks=dc.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    ofpast_count_per_week_per_division=dc.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    # Global Sum 
    # ofpast_sum_per_week_per_division=dc.groupby(['year','week','division']).agg({'cost_real':'sum'}).sort_values(by=['week']).reset_index()


    if request.method == 'POST':
        message_error=''
        division=request.POST.getlist('division')
        week=request.POST.getlist('week')
        profit_center=request.POST.getlist('profit_center')

    # coois_data=all_coois_data
    message_error=''
    if len(week) > 0:
        coois_data=all_coois_data.filter(week__in=week)
        if len(division) > 0:
            coois_data=coois_data.filter(division__in=division)
        if len(profit_center) > 0:
            coois_data=coois_data.filter(profit_centre__in=profit_center)
    else:
        coois_data=all_coois_data.filter(week=current_week)


    
    #Check if result is empty
    if not coois_data :
        message_error='There is no data with your selected filter'
        #Count
        ofpast_results.count = ""
        #Count per cause
        ofpast_results.count_per_cause=""
        #Count per division
        ofpast_results.count_per_division=""
        #Count per Profit center
        ofpast_results.count_per_profit_center=""
        #Sum  per week per division
        ofpast_results.ofpast_sum_per_week_per_division=""
    else:
        # Call Function to get ofpast_results
        ofpast_results(coois_data)


    return render(request,"ofpast/index.html",{'divisions':division,'profit_center':profit_center,'homekpi':homekpi,'ofpast_allweeks':ofpast_allweeks,
    'ofpast_divisions':ofpast_divisions,'current_week':current_week,'message_error':message_error,
    'weekavailable':weekavailable,'yearavailable':yearavailable,'ofpast_divisions':ofpast_divisions,'weeks':week,
    'username':username,'ofpast_count_per_cause':ofpast_results.count_per_cause,'ofpast_count':ofpast_results.count,
    'ofpast_count_per_division':ofpast_results.count_per_division,'ofpast_count_per_week_per_division':ofpast_count_per_week_per_division,
    'ofpast_count_per_profit_center':ofpast_results.count_per_profit_center})


def ofpast_results(coois_data):

    dc=pd.DataFrame(list(coois_data.values()))  
    
    #Insert new column
    dc.insert(0,'RootCause',"",True)
    dc.insert(1,'date_end_real_business',"",True)
    #Format Column
    dc['date_end_real'] = pd.to_datetime(dc['date_end_real'],errors='ignore').dt.date
    
    #Check if date end real + 15 > now()
    try:
        dc.loc[dc['date_end_real']+datetime.timedelta(days=15) < datetime.datetime.now().date() ,"date_end_real_business" ] ='Inf to now'
        dc.loc[dc['date_end_real']+datetime.timedelta(days=15) > datetime.datetime.now().date() ,"date_end_real_business" ] ='Sup to now'
        
    except:
        pass


    dc.loc[( dc.system_status.str.contains("LIVR") ) & (dc.material.notna()) & ( dc.date_end_real_business == 'Inf to now') , "RootCause"] = "COGI is blocking CLSD status"
    dc.loc[ (dc.system_status.str.contains("LIVR") ) & (dc.material.notna()) & ( dc.date_end_real_business == 'Sup to now'), "RootCause"] = "WO confirmed less than 2 weeks ago"

    dc.loc[( dc.system_status.str.contains("CONF")) & ( dc.order.str.contains("CT") ) , "RootCause"]= 'LCT released, confirmed, but not CLSD'
    dc.loc[ (~dc.system_status.str.contains("CONF")) & ( dc.order.str.contains("CT") ) , "RootCause"] = 'LCT released and not confirmed'
    
    dc.loc[ (~dc.system_status.str.contains("CONF")) & ( (dc.order_type.str.contains("YP03")) | (dc.order_type.str.contains("YP04")) ) & (dc.material.notna()) , "RootCause"] = 'WO not confirmed'
    
    dc.loc[ ( dc.system_status.str.contains("LIVR") ) 
            & (dc.system_status.str.contains("CONF")) 
            & ( (dc.order_type.str.contains("YP03")) | (dc.order_type.str.contains("YP04")) ) 
            & (dc.material.notna()) , "RootCause"] = 'WO confirmed but no stk.entry'

    dc.loc [ ( (dc.order_type.str.contains("YP09")) | (dc.order_type.str.contains("YP10")) | (dc.order_type.str.contains("YP11"))) 
            &( dc.system_status.str.contains("UV") ),"RootCause"] ='Opened rush order not released'

    dc.loc [ ( (dc.order_type.str.contains("YP09")) | (dc.order_type.str.contains("YP10")) | (dc.order_type.str.contains("YP11"))) 
            &( ~dc.system_status.str.contains("CONF") )
            & (dc.material.notna()),"RootCause"] ='Rush order not confirmed and without stk.entry' 

    dc.loc [ ( (dc.order_type.str.contains("YP09")) | (dc.order_type.str.contains("YP10")) | (dc.order_type.str.contains("YP29"))) 
            &( ~dc.system_status.str.contains("CONF") )
            & (dc.material.isna()),"RootCause"] ='Rush order non confirmed and not CLSD'  

    dc.loc [ ( (dc.order_type.str.contains("YP09")) | (dc.order_type.str.contains("YP29"))) 
            &( dc.system_status.str.contains("CONF") )
            & (dc.material.isna()),"RootCause"] ='Rush order confirmed and not CLSD' 

    dc.loc [ ( (dc.order_type.str.contains("YP09")) | (dc.order_type.str.contains("YP10")) | (dc.order_type.str.contains("YP11")) | (dc.order_type.str.contains("YP29"))) 
            &( dc.system_status.str.contains("CONF") )
            & (dc.material.isna()),"RootCause"] ='Rush order confirmed but without stk.entry' 

    dc.loc [ ( (dc.order_type.str.contains("YP10")) | (dc.order_type.str.contains("YP11")) ) 
            & (dc.material.isna()),"RootCause"] ='Incorrect WO type : Rush order YP10 without article to manufacture' 

    dc.loc [ ( (dc.order_type.str.contains("YP23")) | (dc.order_type.str.contains("YP24")) ) 
            &( dc.system_status.str.contains("LIVR") )
            &( dc.system_status.str.contains("CONF") )
            & (dc.material.notna()),"RootCause"] ='WO confirmed but without stk.entry' 

    dc.loc [ ( (dc.order_type.str.contains("YP23")) | (dc.order_type.str.contains("YP24")) ) 
            &( ~dc.system_status.str.contains("CONF") )
            & (dc.material.notna()),"RootCause"] ='WO not confirmed : no rescheduling possible' 


    dc.loc[(dc.RootCause == ''),"RootCause"] = 'Undefined cause'

    #All data
    ofpast_results.data= dc.where(pd.notnull(dc), None)

    # if (current_week in weekavailable and current_year in yearavailable) or week :
    #Count
    ofpast_results.count = len(dc.index)
    #Count per cause
    ofpast_results.count_per_cause=dc.groupby(['RootCause']).agg({'id':'count'}).reset_index()

    #Count per division
    ofpast_results.count_per_division=dc.groupby(['division']).agg({'id':'count'}).reset_index()

    #Count per profit centre
    ofpast_results.count_per_profit_center=dc.groupby(['profit_centre']).agg({'id':'count'}).sort_values(by=['id'],ascending=False).reset_index()


def details(request):
    all_coois_data=Coois.objects.all()
    ofpast_results(all_coois_data)
    data=ofpast_results.data
    message_success=''

    now = datetime.datetime.now()
    current_time = now.strftime("%d_%m_%y_%H:%M:%S")

    # Convert dataframe to dic for paginitation
    records = data.to_dict(orient='records')

    paginator = Paginator(records, 50)
    page = request.GET.get('page')
    records = paginator.get_page(page)
    if request.method == 'POST':
        # Download file 
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=WoPast_details_'+current_time+'.csv'
        # data.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
        data.to_csv(path_or_buf=response,index=False)
        return response

    return render(request,"ofpast/details.html",{'data':records,'message_success':message_success})




def import_coois(file,year,week,conn):
    dc=pd.read_excel(file)
    #Add Columns Week and Year
    dc.insert(0,'year',year,True)
    dc.insert(1,'week',week,True)

    coois = StringIO()
    coois.write(dc.to_csv(index=None , header=None))
    coois.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=coois,
            table="ofpast_coois",
            columns=[
                'year',
                'week',
                'profit_centre',
                'order',
                'division',
                'material',
                'designation',
                'order_type',
                'otp_element',
                'manufacturing_version',
                'system_status',
                'customer_order',
                'range_operations_number',
                'entered_by',
                'nomenclature_status',
                'fixation',
                'order_quantity',
                'delivered_quantity',
                'confirmed_scrapmodels',
                'date_end_real',
                'date_end_plan',
                'date_start_plan',
                'date_plan_opening', 
                'date_request',
                'date_entry',
            ],
            null="",
            sep=",",
        )
    conn.commit()


def import_koc4(file,year,week,conn):
    # file=r"\\sp-is.lat.corp\sites\MRPC\Dashboard Data\PowerBI - Sources de données\KOC4\KOC4_"+format(year)+format(str(0)+str(week))+".XLSX"
    dk=pd.read_excel(file)
    #Add Columns Week and Year
    dk.insert(0,'year',year,True)
    dk.insert(1,'week',week,True)
    print(dk.head())

    coois = StringIO()
    coois.write(dk.to_csv(index=None , header=None))
    coois.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=coois,
            table="ofpast_koc4",
            columns=[
                'year',
                'week',
                'order',	
                'material',
                'cost_budget',
                'cost_real',
                'currency',	
                'quantity_produced_plan',	
                'quantity_produced_real',		
                'unit',
            ],
            null="",
            sep=",",
        )
    conn.commit()



#To delete
def calendar(request):

    return render(request,'ofpast/calendar.html')
