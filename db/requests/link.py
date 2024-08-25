from sqlalchemy import select

from db.models.base import async_session
from db.models.channel import Link


async def get_all_links():
    async with async_session() as session:
        query = await session.execute(select(Link))
        return query.scalars().all()