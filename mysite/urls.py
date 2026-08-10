"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django_ratelimit.decorators import ratelimit
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, SoxControlsSitemap, ITGCSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "sox_controls": SoxControlsSitemap,
    "itgc": ITGCSitemap,
}

admin.site.login = ratelimit(key="ip", rate="5/m")(admin.site.login)

admin.site.site_header = "SOX Dashboard"
admin.site.site_title = "SOX Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("about.urls")),
    path("blog/", include("blog.urls", namespace="blog")),
    path("sox_controls/", include("sox_controls.urls", namespace="sox_controls")),
    path("itgc/", include("itgc.urls", namespace="itgc")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]