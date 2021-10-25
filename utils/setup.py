import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine

def load_env_vars(
    ENV_FILE_ID = 'rainy.fever.song',
    dotenv_path = './config/.env'
                 ):
    """
    Load environment variables or raise error if the file is not found
    """
    dotenv_path = Path(dotenv_path)
    load_dotenv(dotenv_path=dotenv_path)

    if os.getenv('ENV_FILE_ID') != ENV_FILE_ID:
        raise FileNotFoundError("""
        IMPORTANT
        An environment file holding the ENV_FILE_ID variable equal to 'rainy.fever.song'
        should have been found at the ./config/.env path.

        Is the script being run from the repository root (emap-helper/)?
        Did you convert the example 'env' file to the '.env' file?

        Please check the above and try again 
        """)
    else:
        return True
    
    
def make_emap_engine(db):
    # Load environment variables
    load_env_vars()
    
    if db == 'uds':
        # expects to run in HYLODE so these are part of this env
        host = os.getenv('EMAP_DB_HOST')
        name = os.getenv('EMAP_DB_NAME')
        port = os.getenv('EMAP_DB_PORT')
        user = os.getenv('EMAP_DB_USER')
        passwd = os.getenv('EMAP_DB_PASSWORD')
    elif db == 'ids':
        host = os.getenv('IDS_DB_HOST')
        name = os.getenv('IDS_DB_NAME')
        port = os.getenv('IDS_DB_PORT')
        user = os.getenv('IDS_DB_USER')
        passwd = os.getenv('IDS_DB_PASSWORD')
    else:
        raise ValueError("db is not recognised; should be one of 'uds' or 'ids'")
        
    # Construct the PostgreSQL connection
    emapdb_engine = create_engine(f'postgresql://{user}:{passwd}@{host}:{port}/{name}')
    return emapdb_engine

