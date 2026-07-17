from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings


class StaticSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['web:index',
                #'web:about_us',
                #'web:contact',
                #'blog:blog'
                ]

    def location(self, item):
        return reverse(item)



"""class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return Blog.objects.all()

    def lastmod(self, obj):
        return obj.modified"""



