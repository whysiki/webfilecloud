@REM alembic init alembic
@REM alembic/env.py
@REM from models import metadata
@REM target_metadata = metadata
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
@REM 让Alembic运行迁移脚本，将你的数据库架构更新为与你的模型匹配。head表示最新的迁移脚本。

@REM D:\xraytest\fastapi_fileserver_backend>alembic revision --autogenerate -m "Initial migration" 
@REM INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
@REM INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
@REM Generating D:\xraytest\fastapi_fileserver_backend\alembic\versions\6ccd76090718_initial_migration.py ...  done

@REM D:\xraytest\fastapi_fileserver_backend>alembic upgrade head 
@REM INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
@REM INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
@REM INFO  [alembic.runtime.migration] Running upgrade  -> 6ccd76090718, Initial migration
@REM PS D:\xraytest\fastapi_fileserver_backend> 