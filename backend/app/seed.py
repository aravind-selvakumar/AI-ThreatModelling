"""Seed the database with an initial admin user."""
import asyncio

from app.auth.auth_handler import hash_password
from app.db.models import User
from app.db.session import async_session_factory


async def seed():
    async with async_session_factory() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return

        admin = User(
            username="admin",
            password_hash=hash_password("admin"),
            role="admin",
        )
        session.add(admin)
        await session.commit()
        print("Admin user created: username=admin, password=admin")


if __name__ == "__main__":
    asyncio.run(seed())
