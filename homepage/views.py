from django.shortcuts import render,redirect
import datetime
from homepage.models import HomeKpi
import pandas as pd
from django.db.models import Q
from cogi.models import Cogi
from cogi.views import cogi_results
from ofpast.views import ofpast_results
from ofpast.models import Coois,Koc4
from purchasepast.models import Purchase
from purchasepast.views import purchase_results
from intercopurchase.views import intercopurchase_results
from inventory_stock.models import MaterialSheet
from inventory_stock.views import inventory_stock_results , inventory_stock_results_week
import os

def homesettings(request):
    username=request.META['REMOTE_USER'].split('\\')[1]
    # username=os.environ.get("REMOTE_USER")
    
    request_url=''
    kpis=[]
    cols=[]
    homekpi=HomeKpi.objects.all().filter(username=username)
    if request.method == 'POST':
        # Get the request origin url : if is come from setting page then delete and save again to get the new order
        #if is come from the like button save without delete data
        request_url=request.META['HTTP_REFERER']
        if request_url=='http://mrpc/dashboard/home/settings':
            data=HomeKpi.objects.all().filter(username=username).delete()


        kpis=request.POST.getlist('kpi')
        cols=request.POST.getlist('col')
        form = dict(zip(kpis, cols))
        for kpi,col in form.items():
            homekpi=HomeKpi()
            check_html=kpi[-4:]
            if check_html == 'html':
                homekpi.kpi=kpi
            else:
                homekpi.kpi=kpi+'.html'
            # homekpi.kpi=kpi
            homekpi.col=col
            homekpi.theme=kpi.split('\\')[0]
            homekpi.username=username
            homekpi.save()
        homekpi=HomeKpi.objects.all()

        return redirect('homepage')
        # return render(request,'homepage/settings.html',{'username':username,'homekpi':homekpi,'request_url':request_url,'check':check})


    return render(request,'homepage/settings.html',{'username':username,'homekpi':homekpi,'request_url':request_url})


def homeview(request):
    username=request.META['REMOTE_USER'].split('\\')[1]

    current_week=datetime.datetime.now().isocalendar().week
    current_year=datetime.datetime.now().isocalendar().year

    #Reinitialtion all data
    #"""""""""""""Cogi App"""""""""""""""""

    cogi_results.count = ""
    cogi_results.count_per_code=""
    cogi_results.count_per_week_per_division=""
    cogi_results.count_per_accountability=""
    cogi_allweeks=""
    cogi_divisions=""
    cogi_count_per_week_per_division=""
    #"""""""""""""""""""""""""""""""""""""""

    #"""""""""""""Of PAST App"""""""""""""""
    ofpast_results.count = ""
    ofpast_results.count_per_cause=""
    ofpast_results.count_per_division=""
    ofpast_results.count_per_profit_center=""
    ofpast_count_per_week_per_division=""
    ofpast_divisions=''
    ofpast_allweeks=''
    #"""""""""""""""""""""""""""""""""""""""

    #"""""""""""""Purchase PAST App"""""""""""""""
    purchase_allweeks=""
    purchase_divisions=""
    purchase_results.count = ""
    purchase_results.count_per_cause=""
    purchase_results.count_per_division=""
    purchase_count_per_week_per_division=""
    purchase_results.count_receive_per_division=""
    purchase_results.count_convert_per_division=""
    purchase_receive_divisions=""
    purchase_convert_divisions=""
    purchase_count_receive_per_week_per_division=""
    purchase_count_convert_per_week_per_division=""

    #"""""""""""""interco Purchase PAST App"""""""""""""""
    intercopurchase_allweeks=""
    intercopurchase_divisions=""
    intercopurchase_results.count = ""
    intercopurchase_results.count_per_cause=""
    intercopurchase_results.count_per_division=""
    intercopurchase_count_per_week_per_division=""
    intercopurchase_results.count_receive_per_division=""
    intercopurchase_results.count_convert_per_division=""
    intercopurchase_receive_divisions=""
    intercopurchase_convert_divisions=""
    intercopurchase_count_receive_per_week_per_division=""
    intercopurchase_count_convert_per_week_per_division=""

    #"""""""""""""Inventory Stok App"""""""""""""""
    inventory_stock_results_week.division_valuation_ps_euro_cost=None
    inventory_stock_results_week.division_valuation_pmp_euro_cost=None
    inventory_stock_results_week.before_division_valuation_ps_euro_cost=None
    inventory_stock_results_week.before_division_valuation_pmp_euro_cost=None
    inventory_stock_results.total_count=None
    inventory_stock_results.total_pmp_unit_euro=None
    inventory_stock_results.total_ps_unit_euro_cost=None
    inventory_stock_results.total_valuation_ps_euro_cost=None
    inventory_stock_results.total_valuation_pmp_euro_cost=None
    inventory_stock_results.division_pmp_unit_euro=None
    inventory_stock_results.division_ps_unit_euro_cost=None
    inventory_stock_results.division_valuation_ps_euro_cost=None
    inventory_stock_results.division_valuation_pmp_euro_cost=None
    #-------------------------------------------------
    #Get kpis choosen from the user
    kpis=HomeKpi.objects.all().filter(username=username)

    division=[]
    week=[]
    year=[]
    profit_center=[]
    if request.method == 'POST':
        division=request.POST.getlist('division')
        profit_center=request.POST.getlist('profit_center')
        week=request.POST.getlist('week')
        year=request.POST.getlist('year')
        profit_center=request.POST.getlist('profit_center')

    range_week=range(current_week-7,current_week+1)
    # for week in range_week:
    weekavailable=[week for week in range_week]

    range_year=range(current_year-1,current_year+1)
    # for year in range_year:
    yearavailable=[year for year in range_year]

    for kpi in kpis:
        if kpi.theme=='cogi':
            #Count per week per division
            all_cogi_data=Cogi.objects.all()
            dc=pd.DataFrame(list(all_cogi_data.values()))
            cogi_allweeks=dc.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            cogi_divisions=dc.division.unique()
            cogi_count_per_week_per_division=dc.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            # message_error=''
            #Check Filter, if filter exist get result with filter if not get current week
            #Check Filter, if filter exist get result with filter if not get current week
            if len(week) > 0:
                cogi_data=all_cogi_data.filter(week__in=week)
                if len(division) > 0:
                    cogi_data=cogi_data.filter(division__in=division)
                if len(profit_center) > 0:
                    cogi_data=cogi_data.filter(profit_centre__in=profit_center)
            else:
                cogi_data=all_cogi_data.filter(week=current_week)
            
            #Check if result is empty
            if not cogi_data :
                # message_error='There is no data with your selected filter'
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
        if kpi.theme=='ofpast':
            #Count per week per devision
            all_coois_data=Coois.objects.all()
            dof=pd.DataFrame(list(all_coois_data.values()))
            ofpast_divisions=dof.division.unique()
            ofpast_allweeks=dof.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            ofpast_count_per_week_per_division=dof.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()

            #Check Filter, if filter exist get result with filter if not get current week
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
                #Count
                ofpast_results.count = ""
                #Count per cause
                ofpast_results.count_per_cause=""
                #Count per division
                ofpast_results.count_per_division=""
                #Count profit center 
                ofpast_results.count_per_profit_center=""

            else:
                # Call Function to get ofpast_results
                ofpast_results(coois_data)
        if kpi.theme=='purchasepast':
            #Count per week per devision
            all_purchase_data=Purchase.objects.all().exclude(Q(purchasing_group__startswith='MR'))


            dp=pd.DataFrame(list(all_purchase_data.values()))
            purchase_allweeks=dp.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            purchase_receive_divisions=dp.division.unique()
            purchase_convert_divisions=dp.transferring_division.unique()
            purchase_count_receive_per_week_per_division=dp.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            purchase_count_convert_per_week_per_division=dp.groupby(['year','week','transferring_division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()


            #Check Filter, if filter exist get result with filter if not get current week
            if week and division:
                purchase_data=all_purchase_data.filter(division__in=division).filter(week__in=week)
            elif week:
                purchase_data=all_purchase_data.filter(week__in=week)
            elif division:
                purchase_data=all_purchase_data.filter(division__in=division)
            else:
                purchase_data=all_purchase_data.filter(week=current_week)
            
            #Check if result is empty
            if not purchase_data :
                #Count
                purchase_results.count = ""
                #Count per cause
                purchase_results.count_per_cause=""
                #Count to receive per division
                purchase_results.count_receive_per_division=""
                #Count to convert per division
                purchase_results.count_convert_per_division=""

            else:
                # Call Function to get purchase_results
                purchase_results(purchase_data)
        if kpi.theme=='intercopurchase':
            #Count per week per devision
            all_intercopurchase_data=Purchase.objects.all().filter(Q(purchasing_group__startswith='MR'))


            dip=pd.DataFrame(list(all_intercopurchase_data.values()))
            intercopurchase_allweeks=dip.groupby(['year','week']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            intercopurchase_receive_divisions=dip.division.unique()
            intercopurchase_convert_divisions=dip.transferring_division.unique()
            intercopurchase_count_receive_per_week_per_division=dip.groupby(['year','week','division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()
            intercopurchase_count_convert_per_week_per_division=dip.groupby(['year','week','transferring_division']).agg({'id':'count'}).sort_values(by=['week']).reset_index()


            #Check Filter, if filter exist get result with filter if not get current week
            if week and division:
                intercopurchase_data=all_intercopurchase_data.filter(division__in=division).filter(week__in=week)
            elif week:
                intercopurchase_data=all_intercopurchase_data.filter(week__in=week)
            elif division:
                intercopurchase_data=all_intercopurchase_data.filter(division__in=division)
            else:
                intercopurchase_data=all_intercopurchase_data.filter(week=current_week)
            
            #Check if result is empty
            if not intercopurchase_data :
                #Count
                intercopurchase_results.count = ""
                #Count per cause
                intercopurchase_results.count_per_cause=""
                #Count to receive per division
                intercopurchase_results.count_receive_per_division=""
                #Count to convert per division
                intercopurchase_results.count_convert_per_division=""

            else:
                # Call Function to get intercopurchase_results
                intercopurchase_results(intercopurchase_data)
        
        if kpi.theme=='inventory_stock':

            all_MaterialSheet_data= MaterialSheet.objects.all()
            if len(year) > 0:
                MaterialSheet_data=all_MaterialSheet_data.filter(year__in=year)
                if len(week) > 0:
                    MaterialSheet_data=all_MaterialSheet_data.filter(year__in=year,week__in=week)
                    if len(division) > 0:
                        MaterialSheet_data=MaterialSheet_data.filter(division__in=division)
                    if len(profit_center) > 0:
                        MaterialSheet_data=MaterialSheet_data.filter(profit_center__in=profit_center)
            else:
                MaterialSheet_data=all_MaterialSheet_data.filter(week=current_week,year=current_year)
            if all_MaterialSheet_data:
                inventory_stock_results_week(all_MaterialSheet_data)
            else:
                inventory_stock_results_week.division_valuation_ps_euro_cost=None
                inventory_stock_results_week.division_valuation_pmp_euro_cost=None
                inventory_stock_results_week.before_division_valuation_ps_euro_cost=None
                inventory_stock_results_week.before_division_valuation_pmp_euro_cost=None
            
            if MaterialSheet_data:
                inventory_stock_results(MaterialSheet_data)
            else:
                inventory_stock_results.total_count=None
                inventory_stock_results.total_pmp_unit_euro=None
                inventory_stock_results.total_ps_unit_euro_cost=None
                inventory_stock_results.total_valuation_ps_euro_cost=None
                inventory_stock_results.total_valuation_pmp_euro_cost=None
                inventory_stock_results.division_pmp_unit_euro=None
                inventory_stock_results.division_ps_unit_euro_cost=None
                inventory_stock_results.division_valuation_ps_euro_cost=None
                inventory_stock_results.division_valuation_pmp_euro_cost=None


    
    
    
    
    return render (request, "homepage\index.html",{'current_week':current_week,'current_year':current_year,'yearavailable':yearavailable,'weeks':week,'years':year,'profit_center':profit_center,'weekavailable':weekavailable,'username':username,'kpis':kpis,'divisions':division,
    'cogi_count':cogi_results.count,'cogi_count_per_code':cogi_results.count_per_code,'cogi_count_per_accountability':cogi_results.count_per_accountability,
    'cogi_allweeks':cogi_allweeks,'cogi_divisions':cogi_divisions,'cogi_count_per_week_per_division':cogi_count_per_week_per_division,

    'ofpast_count':ofpast_results.count, 'ofpast_count_per_cause':ofpast_results.count_per_cause, 'ofpast_count_per_division':ofpast_results.count_per_division,
    'ofpast_count_per_week_per_division':ofpast_count_per_week_per_division,'ofpast_divisions':ofpast_divisions,'ofpast_allweeks':ofpast_allweeks,
    'ofpast_count_per_profit_center':ofpast_results.count_per_profit_center,
    
    'purchase_count':purchase_results.count,'purchase_count_receive_per_division':purchase_results.count_receive_per_division,
    'purchase_allweeks':purchase_allweeks,'purchase_convert_divisions':purchase_convert_divisions,'purchase_receive_divisions':purchase_receive_divisions,
    'purchase_count_convert_per_division':purchase_results.count_convert_per_division,
    'purchase_count_receive_per_week_per_division':purchase_count_receive_per_week_per_division,
    'purchase_count_convert_per_week_per_division':purchase_count_convert_per_week_per_division,
    
    'intercopurchase_count':intercopurchase_results.count,'intercopurchase_count_receive_per_division':intercopurchase_results.count_receive_per_division,
    'intercopurchase_allweeks':intercopurchase_allweeks,'intercopurchase_convert_divisions':intercopurchase_convert_divisions,'intercopurchase_receive_divisions':intercopurchase_receive_divisions,
    'intercopurchase_count_convert_per_division':intercopurchase_results.count_convert_per_division,
    'intercopurchase_count_receive_per_week_per_division':intercopurchase_count_receive_per_week_per_division,
    'intercopurchase_count_convert_per_week_per_division':intercopurchase_count_convert_per_week_per_division,

    'inventory_stock_results_total_count':inventory_stock_results.total_count,
    'inventory_stock_results_total_pmp_unit_euro':inventory_stock_results.total_pmp_unit_euro,
    'inventory_stock_results_total_ps_unit_euro_cost':inventory_stock_results.total_ps_unit_euro_cost,
    'inventory_stock_results_total_valuation_ps_euro_cost':inventory_stock_results.total_valuation_ps_euro_cost,
    'inventory_stock_results_total_valuation_pmp_euro_cost':inventory_stock_results.total_valuation_pmp_euro_cost,

    'inventory_stock_results_division_pmp_unit_euro':inventory_stock_results.division_pmp_unit_euro,
    'inventory_stock_results_division_ps_unit_euro_cost':inventory_stock_results.division_ps_unit_euro_cost,
    'inventory_stock_results_division_valuation_ps_euro_cost':inventory_stock_results.division_valuation_ps_euro_cost,
    'inventory_stock_results_division_valuation_pmp_euro_cost':inventory_stock_results.division_valuation_pmp_euro_cost,

    'inventory_stock_results_week_division_valuation_ps_euro_cost':inventory_stock_results_week.division_valuation_ps_euro_cost,
    'inventory_stock_results_week_division_valuation_pmp_euro_cost':inventory_stock_results_week.division_valuation_pmp_euro_cost,
    'inventory_stock_results_week_before_division_valuation_ps_euro_cost':inventory_stock_results_week.before_division_valuation_ps_euro_cost,
    'inventory_stock_results_week_before_division_valuation_pmp_euro_cost':inventory_stock_results_week.before_division_valuation_pmp_euro_cost,

    })




#About Page
def contact(request):
    return render(request,'homepage/contact.html')




