import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class GenBusiness(Base):
    """Code generation business table"""

    __tablename__ = 'gen_business'

    id: Mapped[id_key] = mapped_column(init=False)
    app_name: Mapped[str] = mapped_column(sa.String(64), comment='Application name')
    table_name: Mapped[str] = mapped_column(sa.String(256), unique=True, comment='TableName')
    doc_comment: Mapped[str] = mapped_column(sa.String(256), comment='Documentation comments')
    table_comment: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='Table description')
    class_name: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='BaseClassName')
    schema_name: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Schema name')
    filename: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Base File Name')
    datetime_mixin: Mapped[bool] = mapped_column(default=True, comment='Whether to include the time Mixin column')
    api_version: Mapped[str] = mapped_column(sa.String(32), default='v1', comment='API version')
    tag: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='API label')
    gen_path: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='Generate path')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remark')
