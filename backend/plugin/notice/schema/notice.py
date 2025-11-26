from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase
from backend.plugin.notice.enums import NoticeType


class NoticeSchemaBase(SchemaBase):
    """Notification and announcement basic model"""

    title: str = Field(description='title')
    type: NoticeType = Field(description='Type (0: Notice, 1: Announcement)')
    status: StatusType = Field(description='Status (0: hidden, 1: displayed)')
    content: str = Field(description='content')


class CreateNoticeParam(NoticeSchemaBase):
    """Create notification announcement parameters"""


class UpdateNoticeParam(NoticeSchemaBase):
    """Update notification announcement parameters"""


class DeleteNoticeParam(SchemaBase):
    """Delete notification announcement parameters"""

    pks: list[int] = Field(description='Notification announcement ID list')


class GetNoticeDetail(NoticeSchemaBase):
    """Notice announcement details"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Notification Announcement ID')
    created_time: datetime = Field(description='Creation time')
    updated_time: datetime | None = Field(None, description='Update time')
