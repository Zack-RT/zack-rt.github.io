AUTHOR = 'HaokunZheng'
SITENAME = "Haokun's Blog"
SITEURL = ""

PATH = "content"

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    # ("Pelican", "https://getpelican.com/"),
    # ("Python.org", "https://www.python.org/"),
    # ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    # ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

STATIC_PATHS = ['image', 'static']
ARTICLE_EXCLUDES = ['static']

# Copy google verification file from static to root directory
EXTRA_PATH_METADATA = {
    'static/google3b3da8dd0049233f.html': {'path': 'google3b3da8dd0049233f.html'},
}

# Favicon configuration
FAVICON = 'image/favicon.svg'  # Modern browsers support SVG favicons
FAVICON_IE = 'image/favicon.ico'  # Legacy IE support

THEME = "themes/pelican-bootstrap3"

PLUGINS = ['i18n_subsites']

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_CATEGORIES_ON_SIDEBAR = False

JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

BOOTSTRAP_THEME = 'cosmo'

# DISPLAY_ARCHIVE_ON_SIDEBAR = True
# MONTH_ARCHIVE_SAVE_AS = '{date:%Y}/{date:%m}/index.html'