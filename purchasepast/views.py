import datetime
from distutils import errors
from distutils.log import error
from io import StringIO
import os
from queue import Empty
from tokenize import Ignore
from unittest import result
from django.shortcuts import render
import pandas as pd
import numpy as np
import psycopg2
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from os.path import exists
from django.db.models import Q
from django.http import HttpResponse
import glob

from purchasepast.models import Purchase
from homepage.models import HomeKpi

# Create your views here.




def upload_files(request):
    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432') 
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year

        #Holidays / calendar
    # global dh #define calendar as global variable
    # holidaysfile=r"\\sp-is.lat.corp\sites\PlanifProd\MasterDataPDP\CALENDRIER_SITE_2022_C.xlsx"    

    #Improt Files
    if current_week < 10:
        current_week=str(0)+str(current_week)
    purchase_file=r"\\centaure\Extract_SAP\SE16N-EBAN-PAST_PURCHASE_REQUEST\PPR_"+format(current_year)+format(current_week)+".XLSX"

    directory_t001=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001\*")
    t001_file= max(directory_t001,key=os.path.getmtime)

    directory_t001k=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001K\*")
    t001k_file= max(directory_t001k,key=os.path.getmtime)

    directory_tcurr=glob.glob(r"\\centaure\Extract_SAP\SE16N-TCURR\*")
    tcurr_file=max(directory_tcurr,key=os.path.getmtime)
    
    t001_file_exists=exists(t001_file)
    t001k_file_exists=exists(t001k_file)
    tcurr_file_exists=exists(tcurr_file)
    purchase_exists = exists(purchase_file)
    # holidays_exists = exists(holidaysfile)
    if t001_file_exists == False:
        message_error= 'Unable to upload TOO1 File, not exist or unreadable!'
        return render(request,'purchasepast\index.html',{'message_error':message_error})   
    if t001k_file_exists == False:
        message_error= 'Unable to upload TK001 File, not exist or unreadable!'
        return render(request,'purchasepast\index.html',{'message_error':message_error}) 
    if tcurr_file_exists == False:
        message_error= 'Unable to upload TCURR File, not exist or unreadable!'
        return render(request,'purchasepast\index.html',{'message_error':message_error}) 
    if purchase_exists == False :
        message_error= 'Unable to upload PPR File, not exist or unreadable!'
        return render(request,'purchasepast\index.html',{'message_error':message_error}) 



    import_purchase(purchase_file,t001_file,t001k_file,tcurr_file,current_year,current_week,conn)


    return home(request)

def home(request):
    try:
        username=request.META['REMOTE_USER']
    except:
        username=''
    # username='test'
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    homekpi=list(HomeKpi.objects.all().filter(username=username).values_list('kpi',flat=True))


    division=[]
    week=[]
    year=[]
    purchase_receive_divisions=""
    purchase_convert_divisions=""
    purchase_count_receive_per_week_per_division=""
    purchase_count_convert_per_week_per_division=""
    # purchase_count_per_week_per_division=""




    #Count per week per devision
    all_purchase_data=Purchase.objects.all().exclude(Q(purchasing_group__startswith='MR'))
    weekavailable=all_purchase_data.values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
    yearavailable=all_purchase_data.values_list('year',flat=True).distinct() #flat=True will remove the tuples and return the list  

    dp=pd.DataFrame(list(all_purchase_data.values()))
    purchase_receive_divisions=dp.division.unique()
    purchase_convert_divisions=dp.transferring_division.unique()
    purchase_allweeks=dp.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    purchase_count_receive_per_week_per_division=dp.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    purchase_count_convert_per_week_per_division=dp.groupby(['year','week','transferring_division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()


    if request.method == 'POST':
        division=request.POST.getlist('division')
        week=request.POST.getlist('week')
        year=request.POST.getlist('year')
        profit_center=request.POST.getlist('profit_center')

    message_error=''
    #Check Filter, if filter exist get result with filter if not get current week
    if len(year) > 0:
            purchase_data=all_purchase_data.filter(year__in=year)
            if len(week) > 0:
                purchase_data=all_purchase_data.filter(year__in=year,week__in=week)
                if len(division) > 0:
                    purchase_data=purchase_data.filter(division__in=division)
    else:
        purchase_data=all_purchase_data.filter(year=current_year,week=current_week)
    #Check if result is empty
    if not purchase_data :
        message_error='There is no data with your selected filter'
        #Count
        purchase_results.count = ""
        #value
        purchase_results.value = ""
        #Count per cause
        purchase_results.count_per_cause=""
        #Count to receive per division
        purchase_results.count_receive_per_division=""
        #Count to convert per division
        purchase_results.count_convert_per_division=""
    else:
        # Call Function to get purchase_results
        purchase_results(purchase_data)

    return render(request,"purchasepast\index.html",{'homekpi':homekpi,'purchase_allweeks':purchase_allweeks,
    'purchase_receive_divisions':purchase_receive_divisions,'purchase_convert_divisions':purchase_convert_divisions,'current_week':current_week,'message_error':message_error,
    'weekavailable':weekavailable,'yearavailable':yearavailable,'divisions':division,'weeks':week,'years':year,
    'username':username,'purchase_count_per_cause':purchase_results.count_per_cause,'purchase_count':purchase_results.count,
    'purchase_count_receive_per_division':purchase_results.count_receive_per_division,'purchase_count_receive_per_week_per_division':purchase_count_receive_per_week_per_division,
    'purchase_count_convert_per_week_per_division':purchase_count_convert_per_week_per_division,
    'purchase_count_convert_per_division':purchase_results.count_convert_per_division,'purchase_value':purchase_results.value})

def purchase_results(purchase_data):
    dp=pd.DataFrame(list(purchase_data.values()))  
    
    #All data
    # purchase_results.data= dp.where(pd.notnull(dp), None)

    #Count
    purchase_results.count = len(dp.index)

    #value
    # purchase_results.value = dp['valuation_price'].sum()

    dp['value']=(dp['valuation_price'] / dp['base_price']) * dp['qte_requested']
    dp['value']=dp['value'].fillna(0)
    purchase_results.value = dp['value'].sum()

    #Count per cause
    purchase_results.count_per_cause=""
    #Count pruchase to receive per division
    purchase_results.count_receive_per_division=dp.groupby(['division']).agg({'id':'count'}).reset_index()
    #Count pruchase to receive per division
    purchase_results.count_convert_per_division=dp.groupby(['transferring_division']).agg({'id':'count'}).reset_index()

    #Count pruchase to receive per division
    purchase_results.count_receive_per_division=dp.groupby(['division']).agg({'id':'count'}).reset_index()
    #Count pruchase to receive per division
    purchase_results.count_convert_per_division=dp.groupby(['transferring_division']).agg({'id':'count'}).reset_index()
    
def details(request):
    all_purchase_data=Purchase.objects.all().exclude(Q(purchasing_group__startswith='MR'))
    purchase_results(all_purchase_data)
    data=purchase_results.data
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
        response['Content-Disposition'] = 'attachment; filename=PurchasePast_details_'+current_time+'.csv'
        # data.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
        data.to_csv(path_or_buf=response,index=False)
        return response

    return render(request,"purchasepast/details.html",{'data':records,'message_success':message_success})


def import_purchase(file,t001_file,t001k_file,tcurr_file,year,week,conn):
    dp=pd.read_excel(file)
    df_t001=pd.read_excel(t001_file)
    df_t001k=pd.read_excel(t001k_file)
    df_tcurr=pd.read_excel(tcurr_file)



    df_t001k = df_t001k.iloc[:, [0,1]]
    df_t001k.rename(columns={'Domaine valorisation':'division','Société':'company'},  inplace = True)

    df_t001=df_t001.iloc[:, [0,4]]
    df_t001.rename(columns={'Société':'company','Devise':'currency'},  inplace = True)

    df_tcurr=df_tcurr[ ( df_tcurr['Type de cours'].isin(['M','P']) ) & (df_tcurr['Dev. source']=='EUR') ]
    df_tcurr=df_tcurr.iloc[:, [2,3,4]]
    df_tcurr.rename(columns={'Devise cible':'target_currency','Début validité':'date','Taux':'rate'},  inplace = True)
    df_tcurr['date']=pd.to_datetime( df_tcurr['date'])
    df_tcurr=df_tcurr.sort_values(['target_currency', 'date'],ascending = [True, False])
    df_tcurr=df_tcurr.groupby(['target_currency'])['rate'].first().reset_index() 
    
    df_t001k_dict=dict(zip(df_t001k['division'],df_t001k['company']))
    
    dp['company']=dp['Division'].map(df_t001k_dict)
    # Get currency from t001
    df_t001_dict=dict(zip(df_t001['company'],df_t001['currency']))
    dp['currency']=dp['company'].map(df_t001_dict)
    # Get rate  from tcurr
    df_tcurr_dict=dict(zip(df_tcurr['target_currency'],df_tcurr['rate']))
    dp['rate']=dp['currency'].map(df_tcurr_dict)
    dp['rate'] = dp['rate'].str.replace(',','.')
    dp['rate']=dp['rate'].fillna(1)
    dp['rate']=dp['rate'].astype(float)
    dp['valuation_price_euro']=dp['Prix de valorisation'].astype(float) / dp['rate']
    #Add Columns Week and Year
    # dp.rename(columns={'Division cédante':'transferring_division'})
    dp['Division cédante']=dp['Division cédante'].fillna(0).astype(np.int64)
    dp.insert(0,'year',year,True)
    dp.insert(1,'week',week,True)

    purchase = StringIO()
    purchase.write(dp.to_csv(index=None , header=None))
    purchase.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=purchase,
            table="purchasepast_purchase",
            columns=[
                'year',
                'week',
                'purchase_requisition',
                'item_of_requisition',
                'deletion_indicator',
                'purchasing_group',
                'material',
                'division',
                'store',
                'transferring_division',
                'qte_requested',
                'requisition_date',
                'release_date',
                'valuation_price',
                'base_price',
                'supplier',
                'outline_agreement',
                'principal_agmt_item',
                'purchase_order',
                'purchase_order_item',
                'company',
                'currency',
                'rate',
                'valuation_price_euro',
            ],
            null="",
            sep=",",
        )
    conn.commit()