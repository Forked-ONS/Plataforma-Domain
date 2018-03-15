import psycopg2
import log
from alembic.operations import Operations
import sqlalchemy as sa
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from settings.loader import Loader
from database import db_name, Base, engine
import glob
import yaml
from uuid import uuid4
import datetime

env = Loader().load()


def sync_db(name = db_name):
    if should_create_database(name):
        create_database(name)
        log.info("created database")
        Base.metadata.create_all(bind=engine)
        log.info("database synchronized")
    else:
        migrate(name)


def create_database(db_name):
    con = psycopg2.connect(host=env["database"]["host"], database="postgres",
                           user=env["database"]["user"], password=env["database"]["password"])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    sql = f'create database "{db_name}"'
    cur.execute(sql)
    con.close()

def drop_database(db_name):
    con = psycopg2.connect(host=env["database"]["host"], database="postgres",
                           user=env["database"]["user"], password=env["database"]["password"])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    sql = f'drop database "{db_name}"'
    cur.execute(sql)
    con.close()

def raw_sql(db_name, sql):
    con = psycopg2.connect(host=env["database"]["host"], database=db_name,
                           user=env["database"]["user"], password=env["database"]["password"])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(sql)
    recset = cur.fetchall()
    con.close()
    return recset

def raw_execute(db_name, sql):
    con = psycopg2.connect(host=env["database"]["host"], database=db_name,
                           user=env["database"]["user"], password=env["database"]["password"])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(sql)
    con.close()


def should_create_database(db_name):
    con = psycopg2.connect(host=env["database"]["host"], database="postgres",
                           user=env["database"]["user"], password=env["database"]["password"])
    cur = con.cursor()
    cur.execute(
        f"SELECT datname FROM pg_database where datname='{db_name}'")
    recset = cur.fetchall()
    result = []
    for rec in recset:
        result.append(rec)
    con.close()
    return not result


def migrate(db_name):
    log.info("migrating")
    migrations_to_execute = diff_migrations()
    for migration in migrations_to_execute:
        process_migration(db_name, migration)


def process_migration(db_name, migration):
    log.info(f'Executing migration {migration["name"]}')
    if "create_table" in migration["content"]:
        create_table(db_name, migration)
    elif "add_column" in migration["content"]:
        create_column(db_name, migration)
    else:
        log.info(f'Invalid migration { migration["name"] }')


def create_table(db_name, migration):
    """
        TODO: Finish
    """
    if not "name" in migration["content"]["create_table"]:
        log.critical(f'Table not found at migration file: { migration["name"] }')
        return
    elif not "columns" in migration["content"]["create_table"]:
        log.critical(f'Columns not defined at migration:{migration["nome"]}')
        return
    name = migration["content"]["create_table"]["name"]
    conn = con = psycopg2.connect(host=env["database"]["host"], database=db_name,
                           user=env["database"]["user"], password=env["database"]["password"])


def create_column(db_name, migration):
    """
    TODO: Finish
    """

def diff_migrations():
    """
    diff how migrations should be executed or not
    """
    migrations = get_executed_migrations()
    files = get_migration_files()
    for f in files:
        if f["name"] not in migrations:
            yield f

def get_executed_migrations():
    for r in raw_sql(env["app"]["name"], "select name from migrationhistory"):
        yield r[0]


def insert_new_migration(name):
    raw_execute(env["app"]["name"],f"insert into migrationhistory (id,name,created_date) values('{uuid4()}','{name}','{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}')")

def get_migration_files():
    """
    returns all migration files
    """
    local_source = "migrations"
    names = glob.glob(f"./{local_source}/*.yaml")
    files = []
    for name in names:
        n = name.replace(f"./{local_source}","")
        n = n.replace("\\","")
        n = n.replace("/","")
        n = n.replace(".yaml","")
        data = {
            "name":n,
            "content":yaml.load(open(f"{name}", "r").read())
        }
        files.append(data)
    return files

