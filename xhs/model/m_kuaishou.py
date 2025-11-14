


# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field


class VideoUrlInfo(BaseModel):
    """快手视频URL信息"""
    video_id: str = Field(title="video id (photo id)")
    url_type: str = Field(default="normal", title="url type: normal")


class CreatorUrlInfo(BaseModel):
    """快手创作者URL信息"""
    user_id: str = Field(title="user id (creator id)")
