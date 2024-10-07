from . import constants as c

connection = f"postgresql+psycopg://{c.POSTGRES_USER}:{c.POSTGRES_PASSWORD}@{c.POSTGRES_HOST}:{c.POSTGRES_PORT}/{c.POSTGRES_DB}"
