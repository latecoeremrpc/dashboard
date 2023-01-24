from msilib.schema import Directory
from django.http import HttpResponse
from django.shortcuts import render
from io import StringIO
import psycopg2
import pandas as pd
import numpy as np
from os.path import exists
import datetime
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory_accuracy.models import SQ00
import glob
import os

# Create your views here.
def cost(request):
    return render(request,'inventory_accuracy\cost.html') 
    
def upload_files(request):
    #get current year and week
    year=datetime.datetime.today().isocalendar()[0]
    week=datetime.datetime.today().isocalendar()[1]

    if week < 10:
        week='0'+str(week)
    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432')

    list_inv_file= r"\\centaure\Extract_SAP\SQ00-ZLIST_INV\ZLIST_INV_"+format(year)+format(week)+".xlsx"

    #get files with last modification
    directory_t001=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001\*")
    t001_file= max(directory_t001,key=os.path.getmtime)

    directory_t001k=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001K\*")
    t001k_file= max(directory_t001k,key=os.path.getmtime)

    directory_tcurr=glob.glob(r"\\centaure\Extract_SAP\SE16N-TCURR\*")
    tcurr_file=max(directory_tcurr,key=os.path.getmtime)

    list_inv_file_exists=exists(list_inv_file)
    t001_file_exists=exists(t001_file)
    t001k_file_exists=exists(t001k_file)
    tcurr_file_exists=exists(tcurr_file)

    message_error= ''

    if list_inv_file_exists == False:
        message_error= 'Unable to upload LIST INV File, not exist or unreadable!'
        return render(request,'inventory_accuracy\index.html',{'message_error':message_error})   
    if t001_file_exists == False:
        message_error= 'Unable to upload TOO1 File, not exist or unreadable!'
        return render(request,'inventory_accuracy\index.html',{'message_error':message_error})   
    if t001k_file_exists == False:
        message_error= 'Unable to upload TK001 File, not exist or unreadable!'
        return render(request,'inventory_accuracy\index.html',{'message_error':message_error}) 
    if tcurr_file_exists == False:
        message_error= 'Unable to upload TCURR File, not exist or unreadable!'
        return render(request,'inventory_accuracy\index.html',{'message_error':message_error}) 
    print('before delete')
    delete=SQ00.objects.all().delete()
    print('After delete')

    
    import_files(list_inv_file,t001_file,t001k_file,tcurr_file,year,week,conn)
    return home(request)


def home(request):
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    # username=request.META['REMOTE_USER']
    username=''

    all_sq00_data= SQ00.objects.all()
    weekavailable=all_sq00_data.values_list('week_date_cpt',flat=True).distinct().order_by('week_date_cpt') #flat=True will remove the tuples and return the list   
    yearavailable=all_sq00_data.values_list('year_date_cpt',flat=True).distinct().order_by('year_date_cpt') #flat=True will remove the tuples and return the list   
    division=[]
    profit_center=[]
    week=[]
    year=[]
    if request.method=='POST':
        division=request.POST.getlist('division')
        week=request.POST.getlist('week')
        year=request.POST.getlist('year')
        profit_center=request.POST.getlist('profit_center')
    
    message_error=''
    print(year,week)
    if len(year) > 0:
        sq00_data=all_sq00_data.filter(year_date_cpt__in=year)
        if len(week) > 0:
            sq00_data=all_sq00_data.filter(year_date_cpt__in=year,week_date_cpt__in=week)
            if len(division) > 0:
                sq00_data=sq00_data.filter(division__in=division)
            if len(profit_center) > 0:
                sq00_data=sq00_data.filter(profit_centre__in=profit_center)
    else:
        sq00_data=all_sq00_data.filter(week_date_cpt=current_week,year_date_cpt=current_year)

    print(SQ00.objects.all().filter(year_date_cpt=2022,week_date_cpt=41).count())
    if sq00_data:
        inventory_accuracy_results(sq00_data)
    else:
        message_error='There is no data with your selected filter'
        inventory_accuracy_results.total_count=''
        inventory_accuracy_results.accuracy=''
        inventory_accuracy_results.cost_per_division=''
        inventory_accuracy_results.total_deviation_cost=''
        inventory_accuracy_results.count_per_week=''
        inventory_accuracy_results.count_per_division=''
        inventory_accuracy_results.accuracy_per_division=''
        inventory_accuracy_results.cost_per_week=''

    return render(request,'inventory_accuracy\index.html',{'all_sq00_data':all_sq00_data,
    'username':username,'current_week':current_week,
    'weekavailable':weekavailable,'yearavailable':yearavailable,'message_error':message_error,'weeks':week,'years':year,'divisions':division,
    'inventory_accuracy_total_count':inventory_accuracy_results.total_count,
    'inventory_accuracy_accuracy':inventory_accuracy_results.accuracy,
    'inventory_accuracy_cost_per_division':inventory_accuracy_results.cost_per_division,
    'inventory_accuracy_total_deviation_cost':inventory_accuracy_results.total_deviation_cost,
    'inventory_accuracy_count_per_week':inventory_accuracy_results.count_per_week,
    'inventory_accuracy_count_per_division':inventory_accuracy_results.count_per_division,
    'inventory_accuracy_accuracy_per_division':inventory_accuracy_results.accuracy_per_division,
    'inventory_accuracy_cost_per_week':inventory_accuracy_results.cost_per_week
    
    })
    


def inventory_accuracy_results(sq00_data):
    df=pd.DataFrame(list(sq00_data.values()))
    # df.to_csv('df_accuracy.csv')
    # total_count rows
    df_gap=df[df['catchment']=='X']
    inventory_accuracy_results.total_count=df_gap.shape[0]

    df_gap['stock_accuracy']=np.where((df_gap['refecrence_inventory'] == 'QTY_GAP') & (df_gap['deviation']!=0), 0 ,100)

    inventory_accuracy_results.data=df



    inventory_accuracy_results.accuracy=df_gap['stock_accuracy'].mean()
    inventory_accuracy_results.total_deviation_cost=df_gap['deviation_cost_euro'].sum()
    
    inventory_accuracy_results.accuracy_per_division=df_gap.groupby(['division'])['stock_accuracy'].mean().reset_index() 
    inventory_accuracy_results.count_per_division=df_gap.groupby(['division'])['id'].count().reset_index() 

    inventory_accuracy_results.cost_per_division=df_gap.groupby(['division'])['deviation_cost_euro'].sum().reset_index()
    inventory_accuracy_results.count_per_week=df_gap.groupby(['year_date_cpt','week_date_cpt'])['id'].count().reset_index()
    df_gap['year_date_cpt']=df_gap['year_date_cpt'].astype(int)
    inventory_accuracy_results.cost_per_week=df_gap.groupby(['year_date_cpt','week_date_cpt'])['deviation_cost_euro'].sum().reset_index()
    # inventory_accuracy_results.accuracy_per_week_division=df_gap.groupby(['year_date_cpt','week_date_cpt','division'])['stock_accuracy'].sum().unstack().fillna(0).stack().reset_index()

def details(request):
    all_inventory_data=SQ00.objects.all()
    inventory_accuracy_results(all_inventory_data)
    data=inventory_accuracy_results.data
    

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
        response['Content-Disposition'] = 'attachment; filename=inventory_accuracy_details_'+current_time+'.csv'
        # data.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
        data.to_csv(path_or_buf=response,index=False)
        return response
    return render(request,"inventory_accuracy/details.html",{'data':records,'message_success':message_success})
    
def import_files(list_inv_file,t001_file,t001k_file,tcurr_file,year,week,conn):
    df=pd.read_excel(list_inv_file)
    df_t001=pd.read_excel(t001_file)
    df_t001k=pd.read_excel(t001k_file)
    df_tcurr=pd.read_excel(tcurr_file)
    #dropping the duplicate  columns
    df=df.drop(df.columns[ [9,11,14,16] ],axis=1)

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

    df.rename(columns = {'Doc.inven.':'inventory_doc',
                        'Article':'material',
                        'Désignation article':'designation',
                        'TyAr':'type',
                        'UQ':'unit',
                        'Div.':'division',
                        'Mag.':'store',
                        'Fourn.':'supplier',
                        'Quantité théorique':'theoritical_quantity',
                        'Quantité saisie':'entred_quantity',
                        'écart enregistré':'deviation',
                        'Ecart (montant)':'deviation_cost',
                        'Dev..1':'dev',
                        'Sup':'delete',
                        'Dte cptage':'date_catchment',
                        'Rectifié par':'corrected_by',
                        'Cpt':'catchment',
                        'Réf.inventaire':'refecrence_inventory',
                        'N° inventaire':'inventory_number',
                        'TyS':'Tys'},  inplace = True)

    # df=df[~df['date_catchment'].isna()]
    #Adding the year and week columns
    #insert year and week in first and second position
    df.insert(0, 'year', year)
    df.insert(1, 'week', week)
    df["division"]=df["division"].fillna(0).astype(int)
    df["store"]=df["store"].fillna(0).astype(int)
    df["Tys"]=df["Tys"].fillna(0).astype(int)

    # Merge files
    # Get company from t0001k
    df_t001k_dict=dict(zip(df_t001k['division'],df_t001k['company']))
    df['company']=df['division'].map(df_t001k_dict)
    # Get currency from t001
    df_t001_dict=dict(zip(df_t001['company'],df_t001['currency']))
    df['currency']=df['company'].map(df_t001_dict)
    # Get rate  from tcurr
    df_tcurr_dict=dict(zip(df_tcurr['target_currency'],df_tcurr['rate']))
    df['rate']=df['currency'].map(df_tcurr_dict)
    df['rate'] = df['rate'].str.replace(',','.')
    df['rate']=df['rate'].fillna(1)
    # df['rate']=df['rate'].astype(float)
    #Calculate deviation_cost_euro
    #Check for TND !!!
    #check for precision in float
    df['deviation_cost_euro']=df['deviation_cost'].astype('float32')*df['rate'].astype('float32')
    #extract year and week from date_catchment
    df['week_date_cpt']=df['date_catchment'].dt.isocalendar().week
    df['year_date_cpt']=df['date_catchment'].dt.isocalendar().year

    list_inv = StringIO()
    #convert file to csv
    list_inv.write(df.to_csv( header=None, index=False ,sep=';'))
    # This will make the cursor at index 0
    list_inv.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=list_inv,
            #file name in DB
            table="inventory_accuracy_sq00",
            columns=[
                    'year',
                    'week',
                    'inventory_doc',
                    'material',
                    'designation',
                    'type',
                    'unit',
                    'division',
                    'store',
                    'supplier',
                    'theoritical_quantity',
                    'entred_quantity',
                    'deviation',
                    'deviation_cost',
                    'dev',  
                    'date_catchment',
                    'corrected_by',
                    'catchment',
                    'delete',
                    'refecrence_inventory',
                    'inventory_number',
                    'Tys',    
                    'company',
                    'currency',
                    'rate',
                    'deviation_cost_euro',  
                    'week_date_cpt',
                    'year_date_cpt'      
            ],
            null="",
            sep=";",
        )

    conn.commit()