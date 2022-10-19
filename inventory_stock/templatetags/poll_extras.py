from django import template
register = template.Library()
@register.filter
def percent( value, arg ):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        value =  value 
        arg = arg 
        delta= value - arg
        if arg: return (delta/arg) * 100
    except: pass
    return ''
    
@register.filter
def diff( value, arg ):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    # try:
    #     value = int( value )
    #     arg = int( arg )
    #     if arg: return value - arg
    # except: pass
    # return ''
    value = int( value )
    arg = int( arg )
    return value - arg