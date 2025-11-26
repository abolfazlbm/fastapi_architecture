import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class GenBusiness(Base):
    """Code generation business table"""

    __tablename__ = 'gen_business'

    id: Mapped[id_key] = mapped_column(init=False)
    app_name: Mapped[str] = mapped_column(sa.String(64), comment='Application name (English)')
    table_name: Mapped[str] = mapped_column(sa.String(256), unique=True, comment='Table name (English)')
    doc_comment: Mapped[str] = mapped_column(sa.String(256), comment='Documentation comments (for function/parameter documentation)')
    table_comment: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='Table description')
    # relate_model_fk: Mapped[int | None] = mapped_column(default=None, comment='Related table foreign key')
    class_name: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Base class name (default is English table name)')
    schema_name: Mapped[str | None] = mapped_column(
        sa.String(64), default=None, comment='Schema name (default is English table name)'
    )
    filename: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Base file name (default is English table name)')
    default_datetime_column: Mapped[bool] = mapped_column(default=True, comment='Is there a default time column?')
    api_version: Mapped[str] = mapped_column(sa.String(32), default='v1', comment='Code generation api version, default is v1')
    gen_path: Mapped[str | None] = mapped_column(
        sa.String(256), default=None, comment='Code generation path (default is app root path)'
    )
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remark')
