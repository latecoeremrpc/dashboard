from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from io import StringIO
import psycopg2
import pandas as pd
import numpy as np
from os.path import exists
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory_stock.models import MaterialSheet
import dask.dataframe as dd
import glob
import os
from io import BytesIO

# Create your views here.
def upload_files(request):
    #get current year and week
    year=datetime.datetime.today().isocalendar()[0]
    week=datetime.datetime.today().isocalendar()[1]
    if week < 10:
        week='0'+str(week)



    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432')
    material_sheet_file=r"\\centaure\Extract_SAP\SQ00-FICHE_ARTICLE\IS_FICHE_ARTICLE_"+format(year)+format(week)+".xlsx"
    zpp_flg13_file=r"\\centaure\Extract_SAP\11-ZPP_FLG13 FULL\Z13_"+format(year)+format(week)+"_2.TXT"


    
    mb52_file=r"\\centaure\Extract_SAP\MB52\MB52_202301.xlsx"

    #get files with last modification
    directory_t001=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001\*")
    t001_file= max(directory_t001,key=os.path.getmtime)

    directory_t001k=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001K\*")
    t001k_file= max(directory_t001k,key=os.path.getmtime)

    directory_tcurr=glob.glob(r"\\centaure\Extract_SAP\SE16N-TCURR\*")
    tcurr_file=max(directory_tcurr,key=os.path.getmtime)
    
    material_sheet_file_exists=exists(material_sheet_file)
    zpp_flg13_file_exists=exists(zpp_flg13_file)
    mb52_file_exists=exists(mb52_file)
    t001_file_exists=exists(t001_file)
    t001k_file_exists=exists(t001k_file)
    tcurr_file_exists=exists(tcurr_file)

    message_error= ''
    if material_sheet_file_exists == False:
        message_error= 'Unable to upload SQ00-FICHE_ARTICLE File, not exist or unreadable!'
        return render(request,'inventory_stock\index.html',{'message_error':message_error})  
    if zpp_flg13_file_exists == False:
        zpp_flg13_file=r"\\centaure\Extract_SAP\11-ZPP_FLG13 FULL\Z13_"+format(year)+format(week)+"_1.TXT"
        zpp_flg13_file_1_exists = exists(zpp_flg13_file)
        if zpp_flg13_file_1_exists == False:
            message_error= 'Unable to upload ZPP FLG13 File, not exist or unreadable!'
            return render(request,'inventory_stock\index.html',{'message_error':message_error}) 
    if mb52_file_exists == False:
        message_error= 'Unable to upload MB52 File, not exist or unreadable!'
        return render(request,'inventory_stock\index.html',{'message_error':message_error})         
    if t001_file_exists == False:
        message_error= 'Unable to upload TOO1 File, not exist or unreadable!'
        return render(request,'inventory_stock\index.html',{'message_error':message_error})   
    if t001k_file_exists == False:
        message_error= 'Unable to upload TK001 File, not exist or unreadable!'
        return render(request,'inventory_stock\index.html',{'message_error':message_error}) 
    if tcurr_file_exists == False:
        message_error= 'Unable to upload TCURR File, not exist or unreadable!'
        return render(request,'inventory_stock\index.html',{'message_error':message_error}) 
    
    import_files(material_sheet_file,zpp_flg13_file,mb52_file,t001_file,t001k_file,tcurr_file,year,week,conn)
    return home(request)


def home(request):
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    try:
        username=request.META['REMOTE_USER']
    except:
        username=''
    all_MaterialSheet_data= MaterialSheet.objects.all().exclude(division=2100).order_by('year','week').values()
    df=pd.DataFrame(all_MaterialSheet_data)
    # df.to_csv('df_inventory_stock.csv')
    df['period']=df['year'].astype(str)+' '+df['week'].astype(str)
    divisions=df['division'].unique()
    divisions_list=sorted(divisions.tolist())
    periods= df['period'].unique()
    weekavailable=df['week'].unique()
    yearavailable=df['year'].unique()

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
    inventory_stock_results(df,year,week,division,profit_center)

    return render(request,'inventory_stock\index.html',{
    'username':username,'current_week':current_week,'profit_center':profit_center,
    'weekavailable':weekavailable,'yearavailable':yearavailable,'message_error':message_error,'weeks':week,'years':year,
    'divisions':divisions,'periods':periods,
    'divisions_list':divisions_list,
    'inventory_stock_results_total_count':inventory_stock_results.total_count,
    'inventory_stock_results_total_pmp_unit_euro':inventory_stock_results.total_pmp_unit_euro,
    'inventory_stock_results_total_ps_unit_euro_cost':inventory_stock_results.total_ps_unit_euro_cost,
    'inventory_stock_results_total_valuation_ps_euro_cost':inventory_stock_results.total_valuation_ps_euro_cost,
    'inventory_stock_results_total_valuation_pmp_euro_cost':inventory_stock_results.total_valuation_pmp_euro_cost,

    'inventory_stock_results_division_pmp_unit_euro':inventory_stock_results.division_pmp_unit_euro,
    'inventory_stock_results_division_ps_unit_euro_cost':inventory_stock_results.division_ps_unit_euro_cost,
    'inventory_stock_results_division_valuation_ps_euro_cost':inventory_stock_results.division_valuation_ps_euro_cost,
    'inventory_stock_results_division_valuation_pmp_euro_cost':inventory_stock_results.division_valuation_pmp_euro_cost,


    'inventory_stock_results_valuation_pmp_euro_cost_per_week_per_division':inventory_stock_results.valuation_pmp_euro_cost_per_week_per_division,
    'inventory_stock_results_valuation_ps_euro_cost_per_week_per_division':inventory_stock_results.valuation_ps_euro_cost_per_week_per_division,

    'inventory_stock_results_division_valuation_ps_pmp_euro_cost':inventory_stock_results.division_valuation_ps_pmp_euro_cost,
    'inventory_stock_results_valuation_ps_pmp_euro_cost_per_week_per_division':inventory_stock_results.valuation_ps_pmp_euro_cost_per_week_per_division,
    'inventory_stock_results_valuation_ps_pmp_euro_cost_per_week_per_division_json':inventory_stock_results.valuation_ps_pmp_euro_cost_per_week_per_division_json,

    })


def inventory_stock_results(df,year,week,division,profit_center):
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year

    df['ps_unit_div']=(df['standard_price'] / df['price_basis'])
    df['pmp_unit_div']=(df['pr_moy_pond'] / df['price_basis'])




    df['ps_unit_euro']=np.where( (df['currency'] == 'EUR') , (df['ps_unit_div'].astype(float)) , ( df['standard_price'].astype(float) / df['price_basis'].astype(float) /df['rate_budget'] ) )
    df['pmp_unit_euro']=np.where( (df['currency'] == 'EUR') , (df['pmp_unit_div'].astype(float)) , ( df['pr_moy_pond'].astype(float) / df['price_basis'].astype(float) /df['rate_last'] ) )


    df.replace([np.inf, -np.inf], 0, inplace=True)

    df['valuation_ps_div']=(df['returnable_stock'].astype(float)+df['stock'].astype(float)+df['lot_qm'].astype(float)+df['stock_transit'].astype(float)+ df['stock_blocked'].astype(float) ) * df['ps_unit_div']
    df['valuation_pmp_div']=(df['returnable_stock'].astype(float)+df['stock'].astype(float)+df['lot_qm'].astype(float)+df['stock_transit'].astype(float)+ df['stock_blocked'].astype(float) ) * df['pmp_unit_div']
    df['valuation_ps_euro']=(df['returnable_stock'].astype(float)+df['stock'].astype(float)+df['lot_qm'].astype(float)+df['stock_transit'].astype(float)+ df['stock_blocked'].astype(float) ) * df['ps_unit_euro']
    df['valuation_pmp_euro']=(df['returnable_stock'].astype(float)+df['stock'].astype(float)+df['lot_qm'].astype(float)+df['stock_transit'].astype(float)+ df['stock_blocked'].astype(float) ) * df['pmp_unit_euro']

    df['valuation_ps_euro']=np.where( (df['currency'] == 'TND') ,df['valuation_ps_euro'] / 100 , df['valuation_ps_euro'] )
    df['valuation_pmp_euro']=np.where( (df['currency'] == 'TND') , df['valuation_pmp_euro']/ 100 , df['valuation_pmp_euro'] )
    
    inventory_stock_results.valuation_pmp_euro_cost_per_week_per_division=df.groupby(['year','week','division'])['valuation_pmp_euro'].sum().unstack().fillna(0).stack().reset_index()
    inventory_stock_results.valuation_ps_euro_cost_per_week_per_division=df.groupby(['year','week','division'])['valuation_ps_euro'].sum().unstack().fillna(0).stack().reset_index()
    inventory_stock_results.valuation_ps_pmp_euro_cost_per_week_per_division=df.groupby(['year','week','division']).agg({'valuation_pmp_euro':'sum','valuation_ps_euro':'sum'}).unstack().fillna(0).stack().reset_index()
    inventory_stock_results.valuation_ps_pmp_euro_cost_per_week_per_division_json=inventory_stock_results.valuation_ps_pmp_euro_cost_per_week_per_division.to_json(orient="records")
    years = [int(i) for i in year]
    weeks = [int(i) for i in week]

    if len(year) > 0:
        df=df[(df['year'].isin(years) ) & (df['week'].isin(weeks))]
        if len(division) > 0:
            df=df[df['division'].isin(division)]
        if len(profit_center) > 0:
            df=df[df['profit_center'].isin(profit_center)]

    else:
        df=df[df['year'].isin([current_year]) & df['week'].isin([current_week])]


    inventory_stock_results.data= df

    inventory_stock_results.total_count=df.shape[0]
    inventory_stock_results.total_pmp_unit_euro=df['pmp_unit_euro'].sum()
    inventory_stock_results.total_ps_unit_euro_cost=df['ps_unit_euro'].sum()
    inventory_stock_results.total_valuation_ps_euro_cost=df['valuation_ps_euro'].sum()
    inventory_stock_results.total_valuation_pmp_euro_cost=df['valuation_pmp_euro'].sum()

    inventory_stock_results.division_pmp_unit_euro=df.groupby(['division'])['pmp_unit_euro'].sum().reset_index()

    inventory_stock_results.division_ps_unit_euro_cost=df.groupby(['division'])['ps_unit_euro'].sum().reset_index()
    inventory_stock_results.division_valuation_ps_euro_cost=df.groupby(['division'])['valuation_ps_euro'].sum().reset_index()
    inventory_stock_results.division_valuation_pmp_euro_cost=df.groupby(['division'])['valuation_pmp_euro'].sum().reset_index()

    inventory_stock_results.division_valuation_ps_pmp_euro_cost=df.groupby(['division']).agg({'valuation_ps_euro':'sum','valuation_pmp_euro':'sum'}).reset_index()





def details(request):
    data=MaterialSheet.objects.all()
    df=pd.DataFrame(data.values())

    division=[]
    profit_center=[]
    week=[]
    year=[]
    years = [int(i) for i in year]
    weeks = [int(i) for i in week]
    if len(year) > 0:
        df=df[(df['year'].isin(years) ) & (df['week'].isin(weeks))]
    if len(division) > 0:
        df=df[df['division'].isin(division)]
    if len(profit_center) > 0:
        df=df[df['profit_center'].isin(profit_center)]

    inventory_stock_results(df,year,week,division,profit_center)

    data=inventory_stock_results.data
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
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
        data=MaterialSheet.objects.all()
        df=pd.DataFrame(data.values())
        inventory_stock_results(df,year,week,division,profit_center)
        data=inventory_stock_results.data
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=inventory_stock_details_'+current_time+'.csv'
        # data.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
        data.to_csv(path_or_buf=response,index=False)
        return response
    return render(request,"inventory_stock/details.html",{'data':records,'message_success':message_success})

def download(request):
    data=MaterialSheet.objects.all()
    now = datetime.datetime.now()
    current_time = now.strftime("%d_%m_%y_%H:%M:%S")
    division=[]
    profit_center=[]
    week=[]
    year=[]
    years = [int(i) for i in year]
    weeks = [int(i) for i in week]
    if request.method == 'POST':
        df=pd.DataFrame(data.values())
        inventory_stock_results(df,year,week,division,profit_center)
        data=inventory_stock_results.data
        with BytesIO() as b:
        # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            data.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            # Set up the Http response.
            filename = 'inventory_stock.xlsx'
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

        
def import_files(material_sheet_file,zpp_flg13_file,mb52_file,t001_file,t001k_file,tcurr_file,year,week,conn):
    print('Hello')
    df=pd.read_excel(material_sheet_file)
    print('End df')
    df_mb52=pd.read_excel(mb52_file)
    print('End df_mb52')
    df_t001=pd.read_excel(t001_file)
    print('End df_t001')
    df_t001k=pd.read_excel(t001k_file)
    print('End df_t001k')
    df_tcurr=pd.read_excel(tcurr_file)
    print('End df_tcurr')
    df_zpp_flg13=dd.read_csv(zpp_flg13_file,encoding='ANSI',sep=';', header=0, dtype={'Division': 'object','Gestionnaire':'object','Ty':'object','Type article':'object','Taille de lot maxi':'object'})
    print('End ZPP FLG13')
    new_columns = [
    "Division",
    "Ctr Pft",
    "Gestionnaire",
    "Desc. Tech.",
    "Grp acheteurs",
    "Référence article",
    "Ty",
    "St",
    "Gv",
    "Besoins",
    "Stock",
    "Consign. Stock",
    "Lot QM",
    "OF",
    "CDE",
    "OP",
    "DA",
    "Clé",
    "Lot fixe",
    "Sécurité",
    "Exédents",
    "Valorisation",
    "Délai sécu",
    "PMP-PS",
    "ABC",
    "Lot mini",
    "Cycle",
    "Tps récept.",
    "Taille de lot maxi",
    "Storage loc.",
    "Désignation article",
    "Unité",
    "Type article",
    "Appro Spe",
    "Vrac",
    "Type planif.",
    "Fournisseur 1",
    "Désignation Fournisseur 1",
    "Fournisseur 2",
    "Désignation Fournisseur 2",
    "Stock en Transit",
    "Quantité requise (1000)",
    "Quantité requise (1010)",
    "Quantité requise (1900)",
    "Quantité requise (3000)",
    "Quantité requise (3100)",
    "Quantité requise (4000)",
    "Quantité requise (5000)",
    "Pt découplage",
    "Stock VMI",
    "Point Commande",
    "Unité Planif",
    "Quantité requise (4020)"
    ]
    df_zpp_flg13 = df_zpp_flg13.rename(columns=dict(zip(df_zpp_flg13.columns, new_columns)))
    df_zpp_flg13=df_zpp_flg13.iloc[:,[0,1,5,10,11,12,32,40,51]]

    df_zpp_flg13['key']=df_zpp_flg13['Division'].astype('str').str.strip()+df_zpp_flg13['Référence article'].astype('str').str.strip()


    df["Division"]=df["Division"].fillna(0).astype(int)
    df['key']=df['Division'].astype('str').str.strip()+df['Article'].astype('str').str.strip()

    #Get individual_collective from df fiche article
    dict_df_individual_collective=dict(zip(df['key'],df['I/C']))
    df_zpp_flg13['individual_collective']=df_zpp_flg13['key'].map(dict_df_individual_collective)
    #Get standard_price from df fiche article
    dict_df_standard_price=dict(zip(df['key'],df['Prix standard']))
    df_zpp_flg13['standard_price']=df_zpp_flg13['key'].map(dict_df_standard_price)
    #Get price_basis from df fiche article
    dict_df_price_basis=dict(zip(df['key'],df['Base de prix']))
    df_zpp_flg13['price_basis']=df_zpp_flg13['key'].map(dict_df_price_basis)
    #Get pr_moy_pond from df fiche article
    dict_df_pr_moy_pond=dict(zip(df['key'],df['Pr.moy.pond']))
    df_zpp_flg13['pr_moy_pond']=df_zpp_flg13['key'].map(dict_df_pr_moy_pond)
    df_zpp_flg13['Type article']=df_zpp_flg13['Type article'].astype('str').str.strip()

    df_zpp_flg13=df_zpp_flg13[ ( df_zpp_flg13['Type article'].isin(['AF','CA']) ) & (df_zpp_flg13['individual_collective'] == 2.0 ) ]

        # Get exchange rate
    df_t001k = df_t001k.iloc[:, [0,1]]
    df_t001k.rename(columns={'Domaine valorisation':'division','Société':'company'},  inplace = True)

    df_t001=df_t001.iloc[:, [0,4]]
    df_t001.rename(columns={'Société':'company','Devise':'currency'},  inplace = True)

    df_tcurr=df_tcurr[ ( df_tcurr['Type de cours'].isin(['M','P']) ) & (df_tcurr['Devise cible']=='EUR') ]
    df_tcurr.rename(columns={'Dev. source':'target_currency','Début validité':'date','Taux':'rate'},  inplace = True)
    df_tcurr['date']=pd.to_datetime( df_tcurr['date'])
    df_tcurr=df_tcurr.sort_values(['target_currency', 'date'],ascending = [True, False])
    df_tcurr_budget=df_tcurr[df_tcurr['Type de cours']=='P']
    df_tcurr_last=df_tcurr[df_tcurr['Type de cours']=='M']

    df_tcurr_budget=df_tcurr_budget.groupby(['target_currency'])['rate'].first().reset_index() 
    df_tcurr_last=df_tcurr_last.groupby(['target_currency'])['rate'].first().reset_index() 

        # Get company from t0001k
    df_t001k_dict=dict(zip(df_t001k['division'],df_t001k['company']))
    df_zpp_flg13['company']=df_zpp_flg13['Division'].map(df_t001k_dict)
        # Get currency from t001
    df_t001_dict=dict(zip(df_t001['company'],df_t001['currency']))
    df_zpp_flg13['currency']=df_zpp_flg13['company'].map(df_t001_dict)
        # Get rate budget from tcurr
    df_tcurr_dict_budget=dict(zip(df_tcurr['target_currency'],df_tcurr['rate']))
    df_zpp_flg13['rate_budget']=df_zpp_flg13['currency'].map(df_tcurr_dict_budget)
    df_zpp_flg13['rate_budget'] = df_zpp_flg13['rate_budget'].str.replace(',','.')
    df_zpp_flg13['rate_budget'] = df_zpp_flg13['rate_budget'].str.lstrip('/').str[0:]
    df_zpp_flg13['rate_budget']=df_zpp_flg13['rate_budget'].fillna(1)
    df_zpp_flg13['rate_budget']=df_zpp_flg13['rate_budget'].astype(float)
            # Get rate last from tcurr
    df_tcurr_dict_last=dict(zip(df_tcurr['target_currency'],df_tcurr['rate']))
    df_zpp_flg13['rate_last']=df_zpp_flg13['currency'].map(df_tcurr_dict_last)
    df_zpp_flg13['rate_last'] = df_zpp_flg13['rate_last'].str.replace(',','.')
    df_zpp_flg13['rate_last'] = df_zpp_flg13['rate_last'].str.lstrip('/').str[0:]
    df_zpp_flg13['rate_last']=df_zpp_flg13['rate_last'].fillna(1)
    df_zpp_flg13['rate_last']=df_zpp_flg13['rate_last'].astype(float)

    df_mb52=df_mb52.iloc[:,[0,1,14]]
    df_mb52.columns =['Material', 'Division', 'bloqued']
    df_mb52['Division']=df_mb52['Division'].fillna(0)
    df_mb52['Division']=df_mb52['Division'].astype(int)
    df_mb52['key']=df_mb52['Division'].astype('str')+df_mb52["Material"].astype('str')
    df_mb52=df_mb52.groupby(['key'])['bloqued'].sum().reset_index()
    dict_df_mb52_stock_blocked=dict(zip(df_mb52['key'],df_mb52['bloqued']))
    df_zpp_flg13['stock_bloqued']=df_zpp_flg13['key'].map(dict_df_mb52_stock_blocked)
    df_zpp_flg13['stock_bloqued']=df_zpp_flg13['stock_bloqued'].fillna(0)
    #convert to pandas dataframe
    df_zpp_flg13=df_zpp_flg13.compute()
    df_zpp_flg13['Unité Planif']=df_zpp_flg13['Unité Planif'].str.strip()
    df_zpp_flg13['Unité Planif']=df_zpp_flg13['Unité Planif'].str.replace(' ','')
    df_zpp_flg13['Unité Planif']=df_zpp_flg13['Unité Planif'].str.slice(start=5)
    df_zpp_flg13['planif_unit']=np.where( ( df_zpp_flg13['Unité Planif'].isin(['2091','FTWZ','2092']) ), df_zpp_flg13['Unité Planif'], 0 )

    df_zpp_flg13['Division']=np.where((df_zpp_flg13['planif_unit']==0),df_zpp_flg13['Division'],df_zpp_flg13['planif_unit'])

    del df_zpp_flg13['key']
    del df_zpp_flg13['Unité Planif']
    del df_zpp_flg13['planif_unit']
    df_zpp_flg13.insert(0, 'year', year)
    df_zpp_flg13.insert(1, 'week', week)
    #Delete space in DF
    for column in df_zpp_flg13.columns:
        df_zpp_flg13[column]=df_zpp_flg13[column].astype(str)
        df_zpp_flg13[column]=df_zpp_flg13[column].str.strip()
    
    df_zpp_flg13['standard_price'] = df_zpp_flg13['standard_price'].str.replace(',','.')
    df_zpp_flg13['price_basis'] = df_zpp_flg13['price_basis'].str.replace(',','.')
    df_zpp_flg13['pr_moy_pond'] = df_zpp_flg13['pr_moy_pond'].str.replace(',','.')
    df_zpp_flg13['Stock'] = df_zpp_flg13['Stock'].str.replace(',','.')
    df_zpp_flg13['Consign. Stock'] = df_zpp_flg13['Consign. Stock'].str.replace(',','.')
    df_zpp_flg13['Lot QM'] = df_zpp_flg13['Lot QM'].str.replace(',','.')
    df_zpp_flg13['Stock en Transit'] = df_zpp_flg13['Stock en Transit'].str.replace(',','.')

    data = StringIO()
    #convert file to csv
    data.write(df_zpp_flg13.to_csv( header=None, index=False ,sep=';'))

    # This will make the cursor at index 0
    data.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=data,
            #file name in DB
            table="inventory_stock_materialsheet",
            columns=[
                'year',
                'week',
                'division',
                'profit_center',
                'material',
                'stock',
                'returnable_stock',
                'lot_qm',
                'material_type',
                'stock_transit',
                'individual_collective',
                'standard_price',
                'price_basis', 
                'pr_moy_pond',
                'company',
                'currency', 
                'rate_budget', 
                'rate_last',
                'stock_blocked',
            ],
            null="",
            sep=";",
        )

    conn.commit()
    

