from sqlalchemy import select, update, delete
from db.models.base import async_session, get_async_session
from db.models.channel import Link

async def get_all_links():
    async with async_session() as session:
        query = await session.execute(select(Link))
        return query.scalars().all()
    
    
async def add_url(new_link: str):
    async with async_session() as session:
        link = Link(url=new_link)
        session.add(link)
        await session.commit()


async def update_link(link_id, new_url):
    async with get_async_session() as session:
        await session.execute(
            update(Link)
            .where(Link.id == link_id)
            .values(url=new_url)
        )
        await session.commit()

async def delete_link(link_id):
    async with get_async_session() as session:
        await session.execute(
            delete(Link)
            .where(Link.id == link_id)
        )
        await session.commit()
