"""Priority Gate tests — the core constraint."""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.priority import Priority, PriorityTrack, PriorityStatus
from app.schemas.priority import PriorityCreate
from app.services.priority_gate import add_priority, cut_priority, PriorityCapError


@pytest.mark.asyncio
async def test_add_first_technical_succeeds(db_session: AsyncSession, test_user: User):
    payload = PriorityCreate(
        title="Ship POS MVP",
        track=PriorityTrack.TECHNICAL,
        definition_of_done="Deployed with auth + time blocks",
    )
    priority = await add_priority(db_session, test_user.id, payload)
    assert priority.status == PriorityStatus.ACTIVE
    assert priority.track == PriorityTrack.TECHNICAL


@pytest.mark.asyncio
async def test_add_second_technical_raises_409(db_session: AsyncSession, test_user: User):
    # Add first
    p1 = PriorityCreate(
        title="First", track=PriorityTrack.TECHNICAL, definition_of_done="Done"
    )
    await add_priority(db_session, test_user.id, p1)

    # Add second — should raise PriorityCapError
    p2 = PriorityCreate(
        title="Second", track=PriorityTrack.TECHNICAL, definition_of_done="Done too"
    )
    with pytest.raises(PriorityCapError):
        await add_priority(db_session, test_user.id, p2)


@pytest.mark.asyncio
async def test_cut_then_add_succeeds(db_session: AsyncSession, test_user: User):
    p1 = PriorityCreate(
        title="First", track=PriorityTrack.TECHNICAL, definition_of_done="Done"
    )
    priority = await add_priority(db_session, test_user.id, p1)

    # Cut it
    await cut_priority(db_session, priority.id)

    # Now we can add another
    p2 = PriorityCreate(
        title="Second", track=PriorityTrack.TECHNICAL, definition_of_done="Done too"
    )
    new_priority = await add_priority(db_session, test_user.id, p2)
    assert new_priority.status == PriorityStatus.ACTIVE


@pytest.mark.asyncio
async def test_technical_and_language_independent(db_session: AsyncSession, test_user: User):
    p1 = PriorityCreate(
        title="Tech", track=PriorityTrack.TECHNICAL, definition_of_done="Done"
    )
    await add_priority(db_session, test_user.id, p1)

    p2 = PriorityCreate(
        title="French", track=PriorityTrack.LANGUAGE, definition_of_done="B1 writing"
    )
    lang = await add_priority(db_session, test_user.id, p2)
    assert lang.status == PriorityStatus.ACTIVE
