from django.http import HttpResponse
from django.shortcuts import render
from io import StringIO
import psycopg2
import pandas as pd
import numpy as np
from os.path import exists
import datetime
import requests
from inventory_accuracy.models import SQ00

# Create your views here.
def cost(request):
    return render(request,'inventory_accuracy\cost.html') 
    
def upload_files(request):
    #get current year and week
    year=datetime.datetime.today().isocalendar()[0]
    week=datetime.datetime.today().isocalendar()[1]
    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432')
    list_inv_file= r"\\prfoufiler01\donnees$\Public\2022 07 12 Z_LISTE_INV.xlsx"
    t001_file= r"\\prfoufiler01\donnees$\Public\T001_202229.xlsx"
    t001k_file= r"\\prfoufiler01\donnees$\Public\T001K_202229.XLSX "
    tcurr_file= r"\\prfoufiler01\donnees$\Public\TCURR_202229.XLSX"

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

    import_files(list_inv_file,t001_file,t001k_file,tcurr_file,year,week,conn)
    home(request)





    # if file_exists:
    #     import_files(file,year,week,conn)
    #     home(request)
    # else:
    #     return render(request,'inventory_accuracy\index.html',{'message_error':message_error})    
    # print('#'*50)
    # print(file_exists)
    # print('#'*50)
def home(request):
    current_week=datetime.datetime.now().isocalendar().week
    username=request.META['REMOTE_USER']

    all_sq00_data= SQ00.objects.all()
    weekavailable=all_sq00_data.values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
    division=[]
    profit_center=[]
    week=[]
    year=[]
    if request.method=='POST':
        division=request.POST.getlist('division')
        week=request.POST.getlist('week')
        profit_center=request.POST.getlist('profit_center')
    
    message_error=''
    if len(week) > 0:
        sq00_data=all_sq00_data.filter(week__in=week)
        if len(division) > 0:
            sq00_data=sq00_data.filter(division__in=division)
        if len(profit_center) > 0:
            sq00_data=sq00_data.filter(profit_centre__in=profit_center)
    else:
        sq00_data=all_sq00_data.filter(week=current_week)



    if sq00_data:
        inventory_accuracy_results(sq00_data)
    else:
        message_error='There is no data with your selected filter'
        inventory_accuracy_results.count=''
        inventory_accuracy_results.cost_per_division=''
        inventory_accuracy_results.total_deviation_cost=''

    return render(request,'inventory_accuracy\index.html',{'all_sq00_data':all_sq00_data,
    'username':username,
    'weekavailable':weekavailable,'message_error':message_error,'weeks':week,'divisions':division,
    'count':inventory_accuracy_results.count,
    'cost_per_division':inventory_accuracy_results.cost_per_division,
    'total_deviation_cost':inventory_accuracy_results.total_deviation_cost})
    


def inventory_accuracy_results(sq00_data):
    df=pd.DataFrame(list(sq00_data.values()))
    # count
    inventory_accuracy_results.count=df.shape[0]

    #new KPI   
    df['type_of_measurement']=np.where( ( (df['unit']=='G') | (df['unit']=='KG') ), 'weighd','counted')
    # Pour un article pesé : Stock accuracy = 100% si l’écart < 3% et l’écart < 250€ sinon la réf est considéré en écart
    df.insert(0, 'stock_accuracy', None)
    # df['stock_accuracy']=np.where ( ( (df['type_of_measurement']=='weighd') & (df['deviation'] < 0.03) & (df['deviation_cost_euro']< 250)) , 1 , df['stock_accuracy'] )
    # # Pour un article compté : Stock accuracy = 100% si l’écart < 1% et l’écart < 250€ sinon la réf est considéré en écart
    # df['stock_accuracy']=np.where ( ( (df['type_of_measurement']=='counted') & (df['deviation'] < 0.01) & (df['deviation_cost_euro']< 250)) , 1 , df['stock_accuracy'] )

    #deviation cost per division
    inventory_accuracy_results.cost_per_division=df.groupby(  ['year','week','division'])['deviation_cost_euro'].sum().reset_index() 
    inventory_accuracy_results.total_deviation_cost=df['deviation_cost'].sum()


def import_files(list_inv_file,t001_file,t001k_file,tcurr_file,year,week,conn):
    df=pd.read_excel(list_inv_file)
    df_t001=pd.read_excel(t001_file)
    df_t001k=pd.read_excel(t001k_file)
    df_tcurr=pd.read_excel(tcurr_file)
    #dropping the duplicate of columns
    df=df.drop(df.columns[ [9,11,14,16] ],axis=1)

    df_t001k = df_t001k.iloc[:, [0,1]]
    df_t001k.rename(columns={'Domaine valorisation':'division','Société':'company'},  inplace = True)

    df_t001=df_t001.iloc[:, [0,4]]
    df_t001.rename(columns={'Société':'company','Devise':'currency'},  inplace = True)

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
                        'Mag.':'store',
                        'Fourn.':'supplier',
                        'Quantité théorique':'theoritical_quantity',
                        'Quantité saisie':'entred_quantity',
                        'écart enregistré':'deviation',
                        'Ecart (montant)':'deviation_cost',
                        'Dev..1':'dev',
                        'Div.':'division',
                        'Sup':'delete',
                        'Dte cptage':'date_catchment',
                        'Rectifié par':'corrected_by',
                        'Cpt':'catchment',
                        'Réf.inventaire':'refecrence_inventory',
                        'N° inventaire':'inventory_number',
                        'TyS':'Tys'},  inplace = True)

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
            ],
            null="",
            sep=";",
        )

    conn.commit()