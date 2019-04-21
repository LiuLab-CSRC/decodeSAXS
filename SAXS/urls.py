"""SAXS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from reconstruction_web import views as reconViews

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', reconViews.index),
    url(r'^submit/', reconViews.submit),
    url(r'^tutorial/', reconViews.totorial),
    url(r'^check/',reconViews.check),
    url(r'^history/',reconViews.history),
    url(r'^checkhistory/',reconViews.checkhistory),
    url(r'^getform/',reconViews.getform),
    url(r'^checkresult/',reconViews.checkresult),
]
