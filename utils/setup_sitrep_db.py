import sqlalchemy as sa
from sqlalchemy.orm import registry
import argparse

import sys 
# TODO: this feels ugly; find better way of organising code
# on the plus side it means that conf needs only be defined in one place
sys.path.append("..") # relative imports
sys.path.append(".") # relative imports
from app.config import ConfigFactory
conf = ConfigFactory.factory()

# parse command line args
parser = argparse.ArgumentParser(description="Prepare database to hold user edits")
parser.add_argument('--drop_old', help='Drops old table including data (DESTRUCTIVE)', action="store_true")
args = parser.parse_args()

# ORM approach
engine = conf.USER_DATA_SOURCE
mapper_registry = registry()
Base = mapper_registry.generate_base()


class SitRepEdits(Base):
    __tablename__ = "sitrep_edits"
    id = sa.Column(sa.Integer, primary_key=True)
    ward_code = sa.Column(sa.String, nullable=False)
    mrn = sa.Column(sa.String, nullable=False)
    compared_at = sa.Column(sa.TIMESTAMP, nullable=False)
    data_source = sa.Column(sa.String, nullable=False)
    variable = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.String)   

if args.drop_old:
    mapper_registry.metadata.drop_all(engine)
mapper_registry.metadata.create_all(engine)
