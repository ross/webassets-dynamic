from django.conf.urls.defaults import RegexURLPattern, RegexURLResolver
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.static import serve
from django_assets import Bundle, register
from webassets.filter import Filter, register_filter
from os.path import join
import sys

class URLPatternHelper:
    names_to_paths = {}

    def __init__(self):
        urls = __import__(settings.ROOT_URLCONF, globals(), locals(), 
                ['urlpatterns'], -1) 
        for url_pattern in urls.urlpatterns:
            self._walk(url_pattern)

    def _walk(self, url_pattern):
        if isinstance(url_pattern, RegexURLResolver):
            for url_pattern in url_pattern.url_patterns:
                self._walk(url_pattern)
        elif isinstance(url_pattern, RegexURLPattern):
            if url_pattern.callback == serve:
                self.names_to_paths[url_pattern.name] = \
                        url_pattern.default_args['document_root']

    def get_path(self, name):
        return self.names_to_paths[name]

helper = URLPatternHelper()

# TODO: should find a better way to get at this
# by default we're in 'serve' mode
mode = ''
try:
    # if there's an argv[1] grab it as it will tell us we're in assets mode
    mode = sys.argv[1]
except:
    pass

def dynamic_assets(name, file):
    if mode == 'assets':
        return join(helper.get_path(name), file)
    else:
        return reverse(name, args=[file])
