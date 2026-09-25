from app.memory.repository import MemoryRepository


class MemoryTools:
    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def remember(self, content: str) -> int:
        return self.repository.save(content)

    def list_all(self) -> list[dict]:
        return self.repository.list_all()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        return self.repository.search(
            query=query,
            limit=limit,
        )

    def forget(self, memory_id: int) -> bool:
        return self.repository.delete(memory_id)
