from webassets import Bundle

BUNDLES = {
    'base_css': Bundle(
        'jquery-ui/css/ui-lightness/jquery-ui-1.8.23.custom.css',
        'jquery-tagit/css/jquery.tagit.css',
        'google-code-prettify/prettify.css',
        'bootstrap/css/bootstrap.min.css',
        'alpaca/css/base.css',
        filters=('cssrewrite', 'cssmin',),
        output='compressed/base.css'
    ),
    'base_js': Bundle(
        'jquery/js/jquery-1.8.1.min.js',
        'jquery-ui/js/jquery-ui-1.8.23.custom.min.js',
        'jquery-tagit/js/tag-it.js',
        'google-code-prettify/prettify.js',
        'bootstrap/js/bootstrap.min.js',
        filters='rjsmin',
        output='compressed/base.js'
    ),
}
