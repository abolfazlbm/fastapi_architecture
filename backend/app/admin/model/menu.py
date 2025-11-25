import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class Menu(Base):
    """Menu Table"""

    __tablename__ = 'sys_menu'

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(sa.String(64), comment='menu title')
    name: Mapped[str] = mapped_column(sa.String(64), comment='menu name')
    path: Mapped[str | None] = mapped_column(sa.String(200), comment='Route Address')
    sort: Mapped[int] = mapped_column(default=0, comment='Sort')
    icon: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='menu icon')
    type: Mapped[int] = mapped_column(default=0, comment='Menu type (0 directory 1 menu 2 buttons 3 embedded 4 external links)')
    component: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='Component Path')
    perms: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='Permission Identification')
    status: Mapped[int] = mapped_column(default=1, comment='menu status (0 is disabled 1 is normal)')
    display: Mapped[int] = mapped_column(default=1, comment='whether it is displayed (0 no 1 yes)')
    cache: Mapped[int] = mapped_column(default=1, comment='Whether to cache (0 No 1 Yes)')
    link: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='External link address')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remarks')

    # Parent menu
    parent_id: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, index=True, comment='Parent menu ID')
