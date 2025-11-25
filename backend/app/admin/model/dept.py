import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Dept(Base):
    """Department table"""

    __tablename__ = 'sys_dept'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(64), comment='Department Name')
    sort: Mapped[int] = mapped_column(default=0, comment='Sort')
    leader: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='Person in charge')
    phone: Mapped[str | None] = mapped_column(sa.String(11), default=None, comment='Mobile')
    email: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='email')
    status: Mapped[int] = mapped_column(default=1, comment='District status (0 is deactivated 1 is normal)')
    del_flag: Mapped[bool] = mapped_column(default=False, comment='Delete flag (0 delete 1 exists)')

    # parent department
    parent_id: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, index=True, comment='Parent department ID')
