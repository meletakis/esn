
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader


##
# Handle 404 Errors
# @param request WSGIRequest list with all HTTP Request
def file_not_found_404(request):

    # 1. Load models for this view
    #from idgsupply.models import My404Method

    # 2. Generate Content for this view
    template = loader.get_template('404.html')
    context = Context({
        'message': 'All: %s' % request,
        })

    # 3. Return Template for this view + Data
    return HttpResponse(content=template.render(context), content_type='text/html; charset=utf-8', status=404)
