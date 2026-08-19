from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from itgc.models import ITGCControl, ItgcNarrative
from sox_controls.models import ProcessNarrative, SoxControl


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "yearly"

    def items(self):
        return [
            "about:about",
            "sox_controls:index",
            "itgc:index",
        ]

    def location(self, item):
        return reverse(item)


class SoxControlsSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.7

    def items(self):
        return SoxControl.objects.all()

    def location(self, obj):
        return reverse(
            "sox_controls:control_detail",
            kwargs={"control_id": obj.control_id},
        )


class ProcessNarrativeSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.7

    def items(self):
        return ProcessNarrative.objects.filter(is_published=True)

    def location(self, obj):
        return obj.get_absolute_url()


class ITGCSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.7

    def items(self):
        return ITGCControl.objects.all()

    def location(self, obj):
        return reverse(
            "itgc:control_detail",
            kwargs={"control_id": obj.control_id},
        )


class ITGCNarrativeSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.7

    def items(self):
        return ItgcNarrative.objects.filter(is_published=True)

    def location(self, obj):
        return obj.get_absolute_url()