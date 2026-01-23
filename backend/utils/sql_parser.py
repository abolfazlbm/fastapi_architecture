import anyio

from anyio import open_file
from sqlparse import split

from backend.common.exception import errors


async def parse_sql_script(filepath: str) -> list[str]:
    """
    Parse SQL script

    :param filepath: script file path
    :return:
    """
    path = anyio.Path(filepath)
    if not await path.exists():
        raise errors.NotFoundError(msg='SQL script file does not exist')

    async with await open_file(filepath, encoding='utf-8') as f:
        contents = await f.read(1024)
        while additional_contents := await f.read(1024):
            contents += additional_contents

    statements = split(contents)
    for statement in statements:
        if not any(statement.lower().startswith(_) for _ in ['select', 'insert']):
            raise errors.RequestError(msg='There are illegal operations in the SQL script file, only SELECT and INSERT are allowed')

    return statements
