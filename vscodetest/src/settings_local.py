import os
ROOTDIR = os.path.abspath(os.path.dirname(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cloudbolt',
        'USER': 'cb_dba',
        'PASSWORD': 'Lap3liTe',
        'HOST': 'localhost',
        'PORT': '3306',
        # uncomment the OPTIONS line to have django create tables
        # using the InnoDB engine as opposed to the MyISAM engine
        # Django will automatically create FK mappings and support
        # transactions when using InnoDB based tables
        # this option only affects the tables at schema creation time
        'OPTIONS': {
            "charset": "utf8mb4",
            "init_command": "SET DEFAULT_STORAGE_ENGINE=INNODB; SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"
        },
    }
}
