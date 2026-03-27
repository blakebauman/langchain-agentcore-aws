"""Tests for SQLite chat data layer."""

from chainlit.types import Feedback, Pagination, ThreadFilter
from chainlit.user import User

from agentic_ai.chat_data import SQLiteDataLayer


class TestSQLiteDataLayer:
    def _make_layer(self) -> SQLiteDataLayer:
        return SQLiteDataLayer(db_path=":memory:")

    async def test_create_and_get_user(self) -> None:
        layer = self._make_layer()
        user = User(identifier="testuser", metadata={"role": "admin"})
        result = await layer.create_user(user)
        assert result is not None
        assert result.identifier == "testuser"

        fetched = await layer.get_user("testuser")
        assert fetched is not None
        assert fetched.id == result.id

    async def test_create_user_idempotent(self) -> None:
        layer = self._make_layer()
        user = User(identifier="testuser", metadata={})
        first = await layer.create_user(user)
        second = await layer.create_user(user)
        assert first is not None
        assert second is not None
        assert first.id == second.id

    async def test_get_user_not_found(self) -> None:
        layer = self._make_layer()
        result = await layer.get_user("nonexistent")
        assert result is None

    async def test_update_and_get_thread(self) -> None:
        layer = self._make_layer()
        await layer.update_thread("thread-1", name="Test Chat", user_id="user-1")
        thread = await layer.get_thread("thread-1")
        assert thread is not None
        assert thread["name"] == "Test Chat"

    async def test_delete_thread(self) -> None:
        layer = self._make_layer()
        await layer.update_thread("thread-1", name="Test")
        await layer.delete_thread("thread-1")
        thread = await layer.get_thread("thread-1")
        assert thread is None

    async def test_list_threads(self) -> None:
        layer = self._make_layer()
        await layer.update_thread("t1", name="First")
        await layer.update_thread("t2", name="Second")

        result = await layer.list_threads(
            Pagination(first=10, cursor=None),
            ThreadFilter(),
        )
        assert len(result.data) == 2

    async def test_create_and_retrieve_step(self) -> None:
        layer = self._make_layer()
        await layer.update_thread("t1", name="Test")
        await layer.create_step(
            {
                "id": "s1",
                "threadId": "t1",
                "name": "user_message",
                "type": "user_message",
                "input": "Hello",
                "output": "Hi there",
            }
        )
        thread = await layer.get_thread("t1")
        assert thread is not None
        assert len(thread["steps"]) == 1
        assert thread["steps"][0]["name"] == "user_message"

    async def test_delete_step(self) -> None:
        layer = self._make_layer()
        await layer.update_thread("t1", name="Test")
        await layer.create_step({"id": "s1", "threadId": "t1", "name": "msg", "type": "run"})
        await layer.delete_step("s1")
        thread = await layer.get_thread("t1")
        assert thread is not None
        assert len(thread["steps"]) == 0

    async def test_upsert_and_delete_feedback(self) -> None:
        layer = self._make_layer()
        feedback = Feedback(forId="step-1", value=1, comment="Great!")
        fid = await layer.upsert_feedback(feedback)
        assert fid is not None

        deleted = await layer.delete_feedback(fid)
        assert deleted is True

    async def test_get_thread_author(self) -> None:
        layer = self._make_layer()
        user = User(identifier="alice", metadata={})
        persisted = await layer.create_user(user)
        assert persisted is not None
        await layer.update_thread("t1", name="Test", user_id=persisted.id)

        author = await layer.get_thread_author("t1")
        assert author == "alice"
