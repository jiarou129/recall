"""ChromaDB 向量库封装：用于错题语义检索（相似题目推荐）。

说明：向量库为「增强能力」，其可用性与核心 CRUD 解耦——
若 ChromaDB 未安装或不可用，相关调用静默跳过，不影响错题的录入/编辑/删除。
"""
from pathlib import Path

from app.config import settings

_COLLECTION = "mistakes"
_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    import chromadb

    Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
    _client = chromadb.PersistentClient(path=settings.chroma_path)
    _collection = _client.get_or_create_collection(
        name=_COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    return _collection


def upsert_mistake(mid: int, text: str, metadata: dict) -> None:
    try:
        col = _get_collection()
        col.upsert(ids=[str(mid)], documents=[text], metadatas=[metadata])
    except Exception as e:
        # 向量库不可用（如未安装 chromadb）时跳过，不影响主流程
        print(f"[chroma] upsert skipped: {e}")


def delete_mistake(mid: int) -> None:
    try:
        col = _get_collection()
        col.delete(ids=[str(mid)])
    except Exception:
        pass


def query_similar(text: str, n: int = 5) -> list[int]:
    """返回与文本最相似的错题 id 列表；向量库不可用时返回空列表。"""
    try:
        col = _get_collection()
    except Exception as e:
        print(f"[chroma] query skipped: {e}")
        return []
    res = col.query(query_texts=[text], n_results=max(1, n))
    ids = res.get("ids", [[]])[0]
    out = []
    for i in ids:
        try:
            out.append(int(i))
        except (TypeError, ValueError):
            continue
    return out
