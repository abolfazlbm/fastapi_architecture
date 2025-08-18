#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from dataclasses import dataclass

from backend.common.dataclasses import SnowflakeInfo
from backend.common.exception import errors
from backend.core.conf import settings


@dataclass(frozen=True)
class SnowflakeConfig:
    """Snowflake algorithm configuration class"""

    # a bit of assignment
    WORKER_ID_BITS: int = 5
    DATACENTER_ID_BITS: int = 5
    SEQUENCE_BITS: int = 12

    # Maximum value
    MAX_WORKER_ID: int = (1 << WORKER_ID_BITS) - 1  # 31
    MAX_DATACENTER_ID: int = (1 << DATACENTER_ID_BITS) - 1  # 31
    SEQUENCE_MASK: int = (1 << SEQUENCE_BITS) - 1  # 4095

    # Displacement offset
    WORKER_ID_SHIFT: int = SEQUENCE_BITS
    DATACENTER_ID_SHIFT: int = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_LEFT_SHIFT: int = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

    # First year time stamp
    EPOCH: int = 1262275200000

    # default value
    DEFAULT_DATACENTER_ID: int = 1
    DEFAULT_WORKER_ID: int = 0
    DEFAULT_SEQUENCE: int = 0


class Snowflake:
    """Snowflake algorithm"""

    def __init__(
        self,
        cluster_id: int = SnowflakeConfig.DEFAULT_DATACENTER_ID,
        node_id: int = SnowflakeConfig.DEFAULT_WORKER_ID,
        sequence: int = SnowflakeConfig.DEFAULT_SEQUENCE,
    ):
        """
        Initialize Snowflake Algorithm Generator

        :param cluster_id: cluster ID (0-31)
        :param node_id: Node ID (0-31)
        :param sequence: Starting sequence number
        """
        if cluster_id < 0 or cluster_id > SnowflakeConfig.MAX_DATACENTER_ID:
            raise errors.RequestError(msg=f'Cluster number must be between 0-{SnowflakeConfig.MAX_DATACENTER_ID}')
        if node_id < 0 or node_id > SnowflakeConfig.MAX_WORKER_ID:
            raise errors.RequestError(msg=f'Node number must be between 0-{SnowflakeConfig.MAX_WORKER_ID}')

        self.node_id = node_id
        self.cluster_id = cluster_id
        self.sequence = sequence
        self.last_timestamp = -1

    @staticmethod
    def _current_millis() -> int:
        """Return the current millisecond timestamp"""
        return int(time.time() * 1000)

    def _next_millis(self, last_timestamp: int) -> int:
        """
        Wait until the next millisecond

        :param last_timestamp: The timestamp of the last ID generated
        :return:
        """
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            time.sleep((last_timestamp - timestamp + 1) / 1000.0)
            timestamp = self._current_millis()
        return timestamp

    def generate(self) -> int:
        """Generate Snowflake ID"""
        timestamp = self._current_millis()

        if timestamp < self.last_timestamp:
            raise errors.ServerError(msg=f'System time goes back, ID is refused to be generated until {self.last_timestamp}')

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SnowflakeConfig.SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self._next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return (
            ((timestamp - SnowflakeConfig.EPOCH) << SnowflakeConfig.TIMESTAMP_LEFT_SHIFT)
            | (self.cluster_id << SnowflakeConfig.DATACENTER_ID_SHIFT)
            | (self.node_id << SnowflakeConfig.WORKER_ID_SHIFT)
            | self.sequence
        )

    @staticmethod
    def parse_id(snowflake_id: int) -> SnowflakeInfo:
        """
        Parses the snowflake ID to get the detailed information it contains

        :param snowflake_id: Snowflake ID
        :return:
        """
        timestamp = (snowflake_id >> SnowflakeConfig.TIMESTAMP_LEFT_SHIFT) + SnowflakeConfig.EPOCH
        cluster_id = (snowflake_id >> SnowflakeConfig.DATACENTER_ID_SHIFT) & SnowflakeConfig.MAX_DATACENTER_ID
        node_id = (snowflake_id >> SnowflakeConfig.WORKER_ID_SHIFT) & SnowflakeConfig.MAX_WORKER_ID
        sequence = snowflake_id & SnowflakeConfig.SEQUENCE_MASK

        return SnowflakeInfo(
            timestamp=timestamp,
            datetime=time.strftime(settings.DATETIME_FORMAT, time.localtime(timestamp / 1000)),
            cluster_id=cluster_id,
            node_id=node_id,
            sequence=sequence,
        )


snowflake = Snowflake()
