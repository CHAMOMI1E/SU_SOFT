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


async def update_link(link_id: int, new_url: str):
    print(link_id, new_url)
    async with async_session() as session:
        await session.execute(
            update(Link).where(Link.id == link_id).values(url=new_url)
        )
        await session.commit()


async def delete_link(link_id: int):
    print(link_id)
    async with async_session() as session:
        try:
            await session.execute(delete(Link).where(Link.id == link_id))
            await session.commit()
        except Exception as e:
            print("Проблема в бд")


async def get_link_by_id(link_id: int):
    async with async_session() as session:
        query = await session.execute(select(Link).where(Link.id == link_id))
        return query.scalar_one_or_none()


async def get_next_url(link_id: int) -> Link | None:
    async with async_session() as session:
        # Получаем следующую ссылку по ID
        stmt_next = select(Link).where(Link.id > link_id).order_by(Link.id).limit(1)
        next_link = (await session.execute(stmt_next)).scalar_one_or_none()

        # Если следующая ссылка существует, возвращаем её, иначе возвращаем первую ссылку по ID
        if next_link:
            return next_link
        else:
            # Получаем первую ссылку по ID
            stmt_first = select(Link).order_by(Link.id).limit(1)
            first_link = (await session.execute(stmt_first)).scalar_one_or_none()
            return first_link


async def get_first_url() -> Link | None:
    async with async_session() as session:
        try:
            query = await session.execute(select(Link).order_by(Link.id))
            return query.scalars().first()
        except Exception as e:
            print(e)
            return None
