from django.conf.urls.defaults import RegexURLPattern, RegexURLResolver
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.static import serve
from django_assets import Bundle, register
from webassets.filter import Filter, register_filter
from webassets.script import CommandLineEnvironment
from os import stat
from os.path import isfile, join
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

## add in our check helper command

def check(self):
    """Check to see if assets need to be rebuilt.

    A non-zero exit status will be returned if any of the input files are
    newer (based on mtime) than their output file. This is intended to be used
    in pre-commit hooks.
    """
    from pprint import pprint
    self.log.debug('Checking:')
    needsupdate = False
    for bundle in self.environment:
        outputname = join(self.environment.directory, bundle.output)
        outputtime = None
        self.log.debug('  asset: %s', outputname)
        if not isfile(outputname):
            self.log.warn('%s does not exist', outputname)
            needsupdate = True
        else:
            outputtime = stat(outputname).st_mtime
            for filename in bundle.get_files():
                inputtime = stat(filename).st_mtime
                self.log.debug('    %s', filename)
                if inputtime > outputtime:
                    self.log.warn('%s is newer than %s', filename, outputname)
                    needsupdate = True
    if needsupdate:
        sys.exit(-1)

CommandLineEnvironment.Commands['check'] = check
