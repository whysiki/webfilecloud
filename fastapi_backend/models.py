# encoding: utf-8
# DB : PostgreSQL
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
from sqlalchemy import Column, String, Table, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

association_table = Table(
    "association",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id")),
    Column("file_id", String, ForeignKey("files.id")),
    # Column("user_id", String, ForeignKey("whyshi.users.id")),  # Ensure type is String
    # Column("file_id", String, ForeignKey("whyshi.files.id")),  # Ensure type is String
    # schema="whyshi",  # 配置了schema迁移时比较麻烦，不配置的话默认为public，但需要有权限。生产环境建议不建议配置schema，授予public权限即可
)


class User(Base):
    __tablename__ = "users"
    # __table_args__ = {"schema": "whyshi"}
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Not plain text password
    register_time = Column(String, default="")
    role = Column(String, default="user")
    profile = Column(String, default="")  # User profile
    profile_image = Column(String, default="")  # User profile image
    files = relationship("File", secondary=association_table, cascade="all, delete")


class File(Base):
    __tablename__ = "files"
    # __table_args__ = {"schema": "whyshi"}
    id = Column(String, primary_key=True, index=True)  # Ensure this is a String
    filename = Column(String, unique=False, index=True)
    file_path = Column(String)
    file_size = Column(String)
    file_owner_name = Column(String)
    file_create_time = Column(String)
    file_type = Column(String, default="binary")
    file_nodes = Column(ARRAY(String), default=[])
    file_preview_path = Column(String, default="")


# Create database engine
engine = create_engine(
    Config.DATABASE_URL,
    pool_size=200,  # The number of connections to keep open in the connection pool
    max_overflow=50,  # The maximum number of connections that can overflow the pool size
    pool_timeout=30,  # The maximum number of seconds to wait when requesting a connection from the pool
    pool_recycle=3600,  # The number of seconds after which a connection will be recycled
)


metadata = Base.metadata

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
