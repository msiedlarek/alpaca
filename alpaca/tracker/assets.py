from flask.ext.assets import Bundle
from alpaca.ext import assets

assets.register('tracker_css', Bundle(
    'tracker/jquery/css/ui-lightness/jquery-ui-1.8.20.custom.css',
    'tracker/tagit/css/jquery.tagit.css',
    'tracker/google-code-prettify/css/prettify.css',
    'tracker/bootstrap/css/bootstrap.css',
    'tracker/alpaca/css/base.css',
    filters=['cssrewrite', 'cssmin'],
    output='tracker/compressed/%(version)s.css'
))

assets.register('tracker_js', Bundle(
    'tracker/jquery/js/jquery-1.7.2.js',
    'tracker/jquery/js/jquery-ui-1.8.20.custom.js',
    'tracker/tagit/js/tag-it.js',
    'tracker/google-code-prettify/js/prettify.js',
    'tracker/bootstrap/js/bootstrap.js',
    'tracker/bootstrap/js/bootstrap-tab.js',
    'tracker/bootstrap/js/bootstrap-collapse.js',
    filters='rjsmin',
    output='tracker/compressed/%(version)s.js'
))
