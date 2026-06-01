import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class DictData(Base):
    """Dictionary data table"""

    __tablename__ = 'sys_dict_data'
    __table_args__ = (
        sa.UniqueConstraint('type_code', 'label', 'deleted', name='uk_sys_dict_data_type_code_label_deleted'),
        {'comment': '字典数据表'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    type_code: Mapped[str] = mapped_column(sa.String(32), comment='Corresponding dictionary type code')
    label: Mapped[str] = mapped_column(sa.String(32), comment='Dictionary label')
    value: Mapped[str] = mapped_column(sa.String(32), comment='Dictionary value')
    color: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='label color')
    sort: Mapped[int] = mapped_column(default=0, comment='sort')
    status: Mapped[int] = mapped_column(default=1, comment='Status (0 disabled 1 normal)')
    remark: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Remark')

    # Logical foreign key
    type_id: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='Dictionary type association ID')
