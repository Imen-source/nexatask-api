import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session, engine, Base
from app.models import User, Workspace, WorkspaceMember, Project, Task, RefreshToken
from app.models.workspace import MemberRole
from app.models.task import TaskStatus, TaskPriority
from app.core.security import get_password_hash


async def seed():
    async with async_session() as session:
        # optional: ensure tables exist (safe in dev only)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 1. Create user
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.flush()  # get user.id

        # 2. Create workspace
        workspace = Workspace(
            name="Test Workspace",
            slug="test-workspace",
            owner_id=user.id,
        )
        session.add(workspace)
        await session.flush()

        # 3. Workspace member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=MemberRole.OWNER,
        )
        session.add(member)

        # 4. Project
        project = Project(
            workspace_id=workspace.id,
            name="Test Project",
            description="Seed project",
        )
        session.add(project)
        await session.flush()

        # 5. Task
        task = Task(
            project_id=project.id,
            created_by_id=user.id,
            title="First Task",
            description="Seed task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            position=0,
        )
        session.add(task)

        # 6. Refresh token
        token = RefreshToken(
            user_id=user.id,
            token_hash=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(days=7),
            device_info="seed-script",
        )
        session.add(token)

        await session.commit()

        print("Seed completed successfully ✔")


if __name__ == "__main__":
    asyncio.run(seed())