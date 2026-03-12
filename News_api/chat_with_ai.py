"""
RAG-based chat module.
Single responsibility: manage per-session chat with retrieved context from
ChromaDB, backed by AWS Bedrock (Claude) and local HuggingFace embeddings.

Public API (matches app.py expectations):
  Chat.get_or_create(chat_id, urls=None) -> Chat instance
  instance.chat(text) -> str
  instance.save(chat_id) -> None
"""
import json
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from . import convert_db
from .llm_client import get_llm
from .embeddings_client import get_embeddings

_CHATS_DIR = Path("chats")
_HISTORY_FILE = _CHATS_DIR / "history.json"

_SYSTEM_PROMPT = (
    "You are a knowledgeable and friendly assistant. "
    "Use the retrieved context below to give a detailed, accurate response (10–13 lines). "
    "If the context does not fully address the question, supplement with your own accurate knowledge. "
    "Do not fabricate facts.\n\n"
    "Context:\n{context}"
)

_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_PROMPT),
    ("human", "{input}"),
])


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

_SESSIONS: dict[str, "Chat"] = {}
_URL_TO_SESSION: dict[str, str] = {}


class Chat:
    """One chat session backed by a ChromaDB retriever and Claude via Bedrock."""

    def __init__(self, persistent_dir: str) -> None:
        embeddings = get_embeddings()
        self._vdb = Chroma(
            persist_directory=persistent_dir,
            embedding_function=embeddings,
        )
        retriever = self._vdb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )
        llm = get_llm(temperature=0.5)
        # LCEL RAG pipeline: retrieve → format → prompt → LLM → parse
        self._rag_chain = (
            {"context": retriever | _format_docs, "input": RunnablePassthrough()}
            | _CHAT_PROMPT
            | llm
            | StrOutputParser()
        )
        self.conversation_history: list[str] = []

    # ── factory ─────────────────────────────────────────────────────────────

    @classmethod
    def get_or_create(cls, chat_id: str, urls: list | None = None) -> "Chat":
        """Return an existing session or create a new one."""
        if chat_id in _SESSIONS:
            return _SESSIONS[chat_id]

        _CHATS_DIR.mkdir(parents=True, exist_ok=True)
        if not _HISTORY_FILE.exists():
            _HISTORY_FILE.write_text(json.dumps({"history": []}))
        history = json.loads(_HISTORY_FILE.read_text())

        persistent_dir: str | None = None

        for entry in history["history"]:
            if str(entry.get("chat_id")) == str(chat_id):
                persistent_dir = entry["storage"]
                break

        if persistent_dir is None and urls is not None:
            url_key = ",".join(str(u) for u in sorted(urls))
            for entry in history["history"]:
                if entry.get("url_key") == url_key:
                    persistent_dir = entry["storage"]
                    break

        if persistent_dir is None:
            if urls is None:
                raise ValueError(f"No saved session for chat_id={chat_id!r} and no URLs provided")
            persistent_dir = convert_db.convert_db(urls)
            url_key = ",".join(str(u) for u in sorted(urls))
            history["history"].append({
                "chat_id": chat_id,
                "url_key": url_key,
                "storage": persistent_dir,
            })
            _HISTORY_FILE.write_text(json.dumps(history, indent=2))
            _URL_TO_SESSION[url_key] = chat_id

        instance = cls(persistent_dir)
        _SESSIONS[chat_id] = instance
        return instance

    # ── public API ───────────────────────────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """Run one RAG-powered turn and return the assistant's reply."""
        self.conversation_history.append(f"Human: {user_input}")
        answer: str = self._rag_chain.invoke(user_input)
        self.conversation_history.append(f"AI: {answer}")
        return answer

    def save(self, chat_id: str) -> None:
        """Persist conversation history to disk."""
        _CHATS_DIR.mkdir(parents=True, exist_ok=True)
        path = _CHATS_DIR / f"{chat_id}.json"
        path.write_text(json.dumps(self.conversation_history, indent=2))