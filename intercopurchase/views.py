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
    # purchase_file=r"\\sp-is.lat.corp\sites\MRPC\Outil\Documents partages\Dashboard\DA_PASSE.XLSX"
    purchase_exists = exists(purchase_file)
    # holidays_exists = exists(holidaysfile)

    if purchase_exists :
        import_purchase(purchase_file,current_year,current_week,conn)
        return home(request)
    else:
        message_error='Unable to upload files, not exist or unreadable!'
        weekavailable=Purchase.objects.all().values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
        week=[]

        return render(request,'intercopurchase\index.html',{'message_error':message_error,'weekavailable':weekavailable,'current_week':current_week,'current_year':current_year,'week':week})

def home(request):
    username=request.META['REMOTE_USER']
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    homekpi=list(HomeKpi.objects.all().filter(username=username).values_list('kpi',flat=True))


    division=[]
    week=[]
    year=[]
    intercopurchase_receive_divisions=""
    intercopurchase_convert_divisions=""
    intercopurchase_count_receive_per_week_per_division=""
    intercopurchase_count_convert_per_week_per_division=""
    # purchase_count_per_week_per_division=""




    #Count per week per devision
    all_intercopurchase_data=Purchase.objects.all().filter(purchasing_group__startswith='MR').exclude(store__startswith='209')
    weekavailable=all_intercopurchase_data.values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
    yearavailable=all_intercopurchase_data.values_list('year',flat=True).distinct() #flat=True will remove the tuples and return the list  

    dp=pd.DataFrame(list(all_intercopurchase_data.values()))
    intercopurchase_receive_divisions=dp.division.unique()
    intercopurchase_convert_divisions=dp.transferring_division.unique()
    intercopurchase_allweeks=dp.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    intercopurchase_count_receive_per_week_per_division=dp.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    intercopurchase_count_convert_per_week_per_division=dp.groupby(['year','week','transferring_division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()


    if request.method == 'POST':
        division=request.POST.getlist('division')
        week=request.POST.getlist('week')
        year=request.POST.getlist('year')

    message_error=''
    #Check Filter, if filter exist get result with filter if not get current week
    if len(year) > 0:
            intercopurchase_data=all_intercopurchase_data.filter(year__in=year)
            if len(week) > 0:
                intercopurchase_data=all_intercopurchase_data.filter(year__in=year,week__in=week)
                if len(division) > 0:
                    intercopurchase_data=intercopurchase_data.filter(division__in=division)
    else:
        intercopurchase_data=all_intercopurchase_data.filter(year=current_year,week=current_week)
    
    #Check if result is empty
    if not intercopurchase_data :
        message_error='There is no data with your selected filter'
        #Count
        intercopurchase_results.count = ""
        #value
        intercopurchase_results.value = ""
        #Count per cause
        intercopurchase_results.count_per_cause=""
        #Count to receive per division
        intercopurchase_results.count_receive_per_division=""
        #Count to convert per division
        intercopurchase_results.count_convert_per_division=""
    else:
        # Call Function to get intercopurchase_results
        intercopurchase_results(intercopurchase_data)

    return render(request,"intercopurchase\index.html",{'homekpi':homekpi,'intercopurchase_allweeks':intercopurchase_allweeks,
    'intercopurchase_receive_divisions':intercopurchase_receive_divisions,'intercopurchase_convert_divisions':intercopurchase_convert_divisions,'current_week':current_week,'message_error':message_error,
    'weekavailable':weekavailable,'yearavailable':yearavailable,'divisions':division,'weeks':week,'years':year,
    'username':username,'intercopurchase_count_per_cause':intercopurchase_results.count_per_cause,'intercopurchase_count':intercopurchase_results.count,
    'intercopurchase_count_receive_per_division':intercopurchase_results.count_receive_per_division,'intercopurchase_count_receive_per_week_per_division':intercopurchase_count_receive_per_week_per_division,
    'intercopurchase_count_convert_per_week_per_division':intercopurchase_count_convert_per_week_per_division,
    'intercopurchase_count_convert_per_division':intercopurchase_results.count_convert_per_division,'intercopurchase_value':intercopurchase_results.value})

def intercopurchase_results(intercopurchase_data):
    dp=pd.DataFrame(list(intercopurchase_data.values()))  
    
    #All data
    intercopurchase_results.data= dp.where(pd.notnull(dp), None)

    #Count
    intercopurchase_results.count = len(dp.index)

    #value
    dp['value']=(dp['valuation_price_euro'] / dp['base_price']) * dp['qte_requested']
    dp['value']=dp['value'].fillna(0)
    intercopurchase_results.value = dp['value'].sum()

    #Count per cause
    intercopurchase_results.count_per_cause=""
    #Count pruchase to receive per division
    intercopurchase_results.count_receive_per_division=dp.groupby(['division']).agg({'id':'count'}).reset_index()
    #Count pruchase to receive per division
    intercopurchase_results.count_convert_per_division=dp.groupby(['transferring_division']).agg({'id':'count'}).reset_index()

    #Count pruchase to receive per division
    intercopurchase_results.count_receive_per_division=dp.groupby(['division']).agg({'id':'count'}).reset_index()
    #Count pruchase to receive per division
    intercopurchase_results.count_convert_per_division=dp.groupby(['transferring_division']).agg({'id':'count'}).reset_index()
    
def details(request):
    all_intercopurchase_data=Purchase.objects.all().filter(Q(purchasing_group__startswith='MR'))
    intercopurchase_results(all_intercopurchase_data)
    data=intercopurchase_results.data
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
        response['Content-Disposition'] = 'attachment; filename=IntercointercopurchasePast_details_'+current_time+'.csv'
        # data.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
        data.to_csv(path_or_buf=response,index=False)
        return response

    return render(request,"intercopurchase/details.html",{'data':records,'message_success':message_success})


def import_purchase(file,year,week,conn):
    dp=pd.read_excel(file)
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
            ],
            null="",
            sep=",",
        )
    conn.commit()