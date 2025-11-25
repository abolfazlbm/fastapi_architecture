import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class DataScope(Base):
    """Data range table"""

    __tablename__ = 'sys_data_scope'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), unique=True, comment='name')
    status: Mapped[int] = mapped_column(default=1, comment='Status (0 is disabled 1 is normal)')
