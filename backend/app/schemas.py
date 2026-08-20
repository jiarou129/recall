"""Pydantic 数据模型（请求/响应）。"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    color: int = 1  # 1-8 对应 ly-design 错题本 8 色


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    count: int = 0


class MistakeBase(BaseModel):
    category_id: Optional[int] = None
    question: str
    answer: str = ""
    source: str = ""
    subject: str = ""
    knowledge_point: str = ""
    mastery: str = "unmastered"  # unmastered | reviewing | mastered


class MistakeCreate(MistakeBase):
    pass


class MistakeUpdate(BaseModel):
    category_id: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    source: Optional[str] = None
    subject: Optional[str] = None
    knowledge_point: Optional[str] = None
    mastery: Optional[str] = None
    snooze_until: Optional[str] = None


class MistakeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_color: int = 1
    question: str
    answer: str
    source: str
    subject: str
    knowledge_point: str
    review_count: int
    mastery: str
    snooze_until: str = ""
    created_at: str
    updated_at: str


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    created_at: str
    updated_at: str


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    role: str
    content: str
    created_at: str


class ChatSend(BaseModel):
    content: str


class SettingsUpdate(BaseModel):
    model_name: str
    api_key: str
    base_url: str


class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    model_name: str
    api_key: str
    base_url: str


class DashboardStats(BaseModel):
    total_questions: int
    total_reviews: int
    success_rate: float
    pending_review: int
    study_series: list[dict]  # 最近30天复习次数 [{date, count}]
    entry_series: list[dict]  # 最近30天错题录入 [{date, count}]
    by_subject: list[dict]    # 各学科错题数 [{subject, count}]


class HelpSection(BaseModel):
    title: str
    body: str


class HelpDoc(BaseModel):
    title: str
    intro: str
    sections: list[HelpSection]
