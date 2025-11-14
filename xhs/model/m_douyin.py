


# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field


class VideoUrlInfo(BaseModel):
    """抖音视频URL信息"""
    aweme_id: str = Field(title="aweme id (video id)")
    url_type: str = Field(default="normal", title="url type: normal, short, modal")


class CreatorUrlInfo(BaseModel):
    """抖音创作者URL信息"""
    sec_user_id: str = Field(title="sec_user_id (creator id)")
