import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class DataScope(Base):
    """Data range table"""

    __tablename__ = 'sys_data_scope'
    __table_args__ = (
        sa.UniqueConstraint('name', 'deleted', name='uk_sys_data_scope_name_deleted'),
        {'comment': 'Data Range Table'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), comment='name')
    status: Mapped[int] = mapped_column(default=1, comment='Status (0 is disabled 1 is normal)')
