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


# SQlite数据库
# # encoding: utf-8
# from sqlalchemy.orm import sessionmaker, declarative_base
# from config import Config
# from sqlalchemy import Column, Integer, String, Table, ForeignKey,ARRAY
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine
# from sqlalchemy import exc
# from sqlalchemy.pool import QueuePool

# # 创建基础模型类
# Base = declarative_base()

# association_table = Table(
#     "association",
#     Base.metadata,
#     Column("user_id", String, ForeignKey("users.id")),
#     Column("file_id", String, ForeignKey("files.id")),
# )

# # 用户模型, SQLAlchemy 模型
# class User(Base):
#     __tablename__ = "users"
#     id = Column(String, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     password = Column(String)  # 不是明文密码
#     files = relationship("File", secondary=association_table)
#     register_time = Column(String, default="")


# # 文件模型, SQLAlchemy 模型
# class File(Base):
#     __tablename__ = "files"
#     id = Column(
#         String, primary_key=True, index=True
#     )  # 文件内容的哈希值 + hash(用户名)作为文件ID
#     filename = Column(String, unique=False, index=True)
#     file_path = Column(String)
#     file_size = Column(String)
#     file_owner_name = Column(String)
#     file_create_time = Column(String)
#     file_type = Column(String, default="binary")


# # 创建数据库引擎
# # engine = create_engine(Config.DATABASE_URL)
# engine = create_engine(Config.DATABASE_URL, pool_size=20, max_overflow=10, pool_timeout=30, pool_recycle=3600)


# metadata = Base.metadata

# # 创建所有的表
# Base.metadata.create_all(bind=engine)

# # 创建会话工厂
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 1. **`Config.DATABASE_URL`**: This parameter represents the URL string used to connect to the database. It typically includes information such as the dialect (e.g., PostgreSQL), username, password, host, port, and database name.

# 2. **`pool_size=20`**: This parameter sets the number of database connections to keep open in the connection pool. In this case, it's configured to keep a maximum of 20 connections open at a time.

# 3. **`max_overflow=10`**: This parameter determines the maximum number of connections that can overflow the pool size. If all connections in the pool are in use and a new connection is requested, and the number of connections has not exceeded the pool size plus the max overflow, a new connection will be created. In this case, it's configured to allow a maximum of 10 additional connections to be created beyond the pool size.

# 4. **`pool_timeout=30`**: This parameter specifies the maximum number of seconds to wait when requesting a connection from the pool. If all connections are in use and the pool timeout is reached, an exception will be raised. In this case, it's set to 30 seconds.

# 5. **`pool_recycle=3600`**: This parameter sets the number of seconds after which a connection will be recycled (i.e., closed and reopened) in the connection pool. This is useful for ensuring that connections do not become stale and can help prevent certain types of database errors. In this case, it's set to recycle connections every 3600 seconds (1 hour).

# Overall, these parameters are used to configure the behavior of the SQLAlchemy connection pool, which manages and reuses database connections to optimize performance and resource usage in database applications. Adjusting these parameters can help fine-tune the behavior of the connection pool based on the specific requirements and characteristics of the application and the underlying database system.
