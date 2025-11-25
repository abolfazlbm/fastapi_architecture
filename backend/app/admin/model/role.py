import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class Role(Base):
    """Role table"""

    __tablename__ = 'sys_role'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(32), unique=True, comment='Character name')
    status: Mapped[int] = mapped_column(default=1, comment='Character status (0 disabled 1 normal)')
    is_filter_scopes: Mapped[bool] = mapped_column(default=True, comment='Filter data permission (0 no 1 yes)')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remark')
