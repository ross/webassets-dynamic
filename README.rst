webassets-dynamic is a library to allow you to use webassets with django
projects where django.views.static.serve is in use. This is common when static
files live in and are served out of shared "apps."

If your django app or its dependencies (django apps in those deps) have url
rules like the following, this is what you need.

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': join(dirname(__file__), 'static')}, name='static')


The module provides a single extral function dynamic_assets. It accepts two
parameters. The first is the static view's name ('static' in the above rule.)
The second parameter is the location of the file within the static-directory,
the same as you'd use when creating a url.

Generally this module is set up to manually create and check-in the bundled
files. To do that you'll just run the normal ./manage.py assets rebuild and then
check in the results.

You will need to configure the following values in your settings.py:

    # where you want to place the resulting output
    ASSETS_ROOT = os.path.join(ROOT_DIR, 'skin/static/')
    # the uri at which ^^ is served (can't dynamically get this b/c there may be
    # multiple statics)
    STATIC_URL = '/static/'
    # do not automatically update the packaged assets at runtime (they'll only
    # be creatd when you run ./manage.py assets rebuild) generating them on the
    # fly might work, but it's currently untested/not supported.
    ASSETS_UPDATER = False
    # by default set ASSETS_DEBUG to DEBUG, meaning that when we're in debug
    # mode we'll get the expanded list of individual js/css files with their
    # dynamic paths.
    ASSETS_DEBUG = DEBUG

An example assets.py using this module follows:

    from django_assets import Bundle, register
    from webassets_dynamic import dynamic_assets
    from os.path import join

    register('js_all', Bundle(
        dynamic_assets('sharedappjs', 'js/jquery.min.js'),
        dynamic_assets('sharedappjs', 'js/log.js'),
        dynamic_assets('static', 'js/app.js'),
        filters=['jsmin'], output=join('js', 'js_all.js')))

    register('css_all', Bundle(
        dynamic_assets('static', 'css/screen.css'),
        filters=['cssrewrite', 'cssmin'],
        output=join('css', 'css_all.css')))
