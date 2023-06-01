import factory
from django.utils.text import slugify
from wagtail.models import Page


class PageFactory(factory.Factory):
    class Meta:
        model = Page

    title = "Title"
    slug = factory.LazyAttribute(lambda x: slugify(x.title))
