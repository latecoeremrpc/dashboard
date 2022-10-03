from urllib import request
from django.shortcuts import render
from os.path import exists
import datetime
import psycopg2
from io import StringIO
import pandas as pd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import datetime
from cogi.models import Cogi
from homepage.models import HomeKpi



# Create your views here.



def upload_files(request):
    conn = psycopg2.connect(host='localhost',dbname='latecoere',user='postgres',password='054Ibiza',port='5432') 
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year
    
    #Holidays / calendar
    global dh #define calendar as global variable
    holidaysfile=r"\\sp-is.lat.corp\sites\PlanifProd\MasterDataPDP\CALENDRIER_SITE_2022_C.xlsx"   

        #Improt Files
    if current_week < 10:
        current_week=str(0)+str(current_week)
    cogi_file=r"\\centaure\Extract_SAP\SE16N-AFFW\AFFW_"+format(current_year)+format(current_week)+".XLSX"
    # cogi_file=r"\\sp-is.lat.corp\sites\MRPC\Dashboard Data\PowerBI - Sources de données\COGI\COGI_2022W07.XLSX"
    cogi_exists = exists(cogi_file)
    if cogi_exists:
        import_cogi(conn,cogi_file,current_week,current_year)
        return home(request)
    else:
        message_error='Unable to upload files, not exist or unreadable!'
        return render(request,'cogi/index.html',{'message_error':message_error})


def home(request):
    username=request.META['REMOTE_USER']
    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year

    division=[]
    profit_center=[]
    week=[]
    year=[]

    if request.method == 'POST':
        division=request.POST.getlist('division')
        year=request.POST.getlist('year')
        week=request.POST.getlist('week')
        profit_center=request.POST.getlist('profit_center')


    #Count per week per division
    all_cogi_data=Cogi.objects.all()
    weekavailable=all_cogi_data.values_list('week',flat=True).distinct().order_by('week') #flat=True will remove the tuples and return the list   
    yearavailable=all_cogi_data.values_list('year',flat=True).distinct() #flat=True will remove the tuples and return the list  
    homekpi=list(HomeKpi.objects.all().filter(username=username).values_list('kpi',flat=True))


    dc=pd.DataFrame(list(all_cogi_data.values()))
    cogi_allweeks=dc.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
    cogi_divisions=dc.division.unique()
    cogi_count_per_week_per_division=dc.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()


    message_error=''
    #Check Filter, if filter exist get result with filter if not get current week
    # if len(week) > 0:
    #     cogi_data=all_cogi_data.filter(week__in=week)
    #     if len(division) > 0:
    #         cogi_data=cogi_data.filter(division__in=division)
    #     if len(profit_center) > 0:
    #         cogi_data=cogi_data.filter(profit_centre__in=profit_center)
    # else:
    #     cogi_data=all_cogi_data.filter(week=current_week)
    if len(year) > 0:
            cogi_data=all_cogi_data.filter(year__in=year)
            if len(week) > 0:
                cogi_data=all_cogi_data.filter(year__in=year,week__in=week)
                if len(division) > 0:
                    cogi_data=cogi_data.filter(division__in=division)
                if len(profit_center) > 0:
                    cogi_data=cogi_data.filter(profit_centre__in=profit_center)
    else:
        cogi_data=all_cogi_data.filter(year=current_year,week=current_week)

    
    #Check if result is empty
    if not cogi_data :
        message_error='There is no data with your selected filter'
        #Count
        cogi_results.count = ""
        #Count per cause
        cogi_results.count_per_code=""
        #Count per division
        cogi_results.count_per_week_per_division=""
        #Count par accountability
        cogi_results.count_per_accountability=""
    else:
        # Call Function to get cogi_results
        cogi_results(cogi_data)

    return render(request,'cogi\index.html',{'divisions':division,'message_error':message_error,'current_week':current_week,'username':username,'homekpi':homekpi,'cogi_allweeks':cogi_allweeks,'cogi_divisions':cogi_divisions,
    'cogi_count_per_week_per_division':cogi_count_per_week_per_division,'cogi_count':cogi_results.count,'weekavailable':weekavailable,'yearavailable':yearavailable,'years':year,
    'cogi_count_per_code':cogi_results.count_per_code,'cogi_count_per_accountability':cogi_results.count_per_accountability,'weeks':week})



def cogi_results(cogi_data):
    dc=pd.DataFrame(list(cogi_data.values()))  


    #Accountability
    #By default all accountability ar MRPC then check code msg if 18 or 21 or 667 it will be LOGISTICS
    dc.insert(0,'accountability','MRPC')
    dc.loc[(dc['message_number'] == '18') | (dc['message_number'] == '21') | (dc['message_number'] == '667'), "accountability"] = "LOGISTICS"
    
    #All data
    cogi_results.data= dc.where(pd.notnull(dc), None)
    #Count
    cogi_results.count = len(dc.index)
    #Count per code message
    cogi_results.count_per_code=dc.groupby(['message_number']).agg({'id':'count'}).sort_values(by=['id'],ascending=False).reset_index()
    #Count par accountability
    cogi_results.count_per_accountability=dc.groupby(['accountability']).agg({'id':'count'}).sort_values(by=['id'],ascending=False).reset_index()

def details(request):
    all_cogi_data=Cogi.objects.all()
    cogi_results(all_cogi_data)
    data=cogi_results.data
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
        response['Content-Disposition'] = 'attachment; filename=cogi_details_'+current_time+'.csv'
        # data.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
        data.to_csv(path_or_buf=response,index=False)
        return response

    return render(request,"cogi/details.html",{'data':records,'message_success':message_success})

def import_cogi(conn,file,current_week,current_year):

    dc=pd.read_excel(file)
    #Select Column need
    dc=dc.iloc[:,[0,2,61,49,62,37,10,6,7,8,23,13,14,60,18]]
    #Add new column not exist in file
    dc.insert(0,'treatment_status',None,True)
    dc.insert(8,'error_text',None,True)
    #Add Columns Week and Year
    dc.insert(0,'year',current_year,True)
    dc.insert(1,'week',current_week,True)


    cogi = StringIO()
    cogi.write(dc.to_csv(index=None , header=None,sep=';'))
    cogi.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=cogi,
            table="cogi_cogi",
            columns=[
                'year',
                'week',
                'treatment_status',
                'stock_movement_doc',
                'created_on',
                'time',
                'error_date',
                'time_error',
                'message_number',
                'movement_code',
                'error_text',
                'material',
                'division',
                'store',
                'order',
                'customer_order',
                'customer_order_item',
                'otp_element',
                'qty_unit_entered'
            ],
            null="",
            sep=";",  # not , beacause some column contains ',' 
        )
    conn.commit()
