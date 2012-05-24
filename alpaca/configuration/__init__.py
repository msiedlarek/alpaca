from alpaca.configuration.local import *

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY configuration value is required.")
