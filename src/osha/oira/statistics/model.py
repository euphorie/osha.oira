# -*- coding: utf-8 -*-
from App.config import getConfiguration
from euphorie.client.enum import Enum
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import functions

import logging


log = logging.getLogger(__name__)

Base = declarative_base()

STATISTICS_DATABASE_PATTERN = "statistics_{suffix}"


def get_postgres_url():
    configuration = getConfiguration()
    if not hasattr(configuration, "product_config"):
        msg = "No product config found! Database connection cannot be set up"
        log.error(msg)
        return None
    conf = configuration.product_config.get("osha.oira")
    postgres_url_statistics = conf.get("postgres-url-statistics", "")
    return postgres_url_statistics


def create_session(database_url):
    engine = create_engine(database_url)
    if engine is None:
        return None
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class AccountStatistics(Base):
    """Statistically relevant data concerning an account."""

    __tablename__ = "account"

    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    account_type = schema.Column(
        Enum([u"guest", u"converted", "full"]), default="full", nullable=True
    )
    creation_date = schema.Column(
        types.DateTime, nullable=True, default=functions.now()
    )


class SurveySessionStatistics(Base):
    """Statistically relevant data concerning a session."""

    __tablename__ = "assessment"

    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    start_date = schema.Column(types.DateTime, nullable=False, default=functions.now())
    completion_percentage = schema.Column(types.Integer, nullable=True, default=0)
    country = schema.Column(types.String(512), nullable=False)
    sector = schema.Column(types.String(512), nullable=False)
    tool = schema.Column(types.String(512), nullable=False)
    account_type = schema.Column(
        Enum([u"guest", u"converted", "full"]), default="full", nullable=True
    )


class CompanyStatistics(Base):
    """Statistically relevant data concerning a company."""

    __tablename__ = "company"

    id = schema.Column(types.Integer(), primary_key=True, autoincrement=True)
    session_id = schema.Column(
        types.Integer(),
        schema.ForeignKey("assessment.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    country = schema.Column(types.String(3))
    employees = schema.Column(Enum([None, "1-9", "10-49", "50-249", "250+"]))
    conductor = schema.Column(Enum([None, "staff", "third-party", "both"]))
    referer = schema.Column(
        Enum(
            [
                None,
                "employers-organisation",
                "trade-union",
                "national-public-institution",
                "eu-institution",
                "health-safety-experts",
                "other",
            ]
        )
    )
    workers_participated = schema.Column(types.Boolean())
    needs_met = schema.Column(types.Boolean())
    recommend_tool = schema.Column(types.Boolean())
