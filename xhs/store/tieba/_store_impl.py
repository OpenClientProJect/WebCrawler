


# -*- coding: utf-8 -*-
# @Author  : persist1@126.com
# @Time    : 2025/9/5 19:34
# @Desc    : 贴吧存储实现类
import os
from typing import Dict

import aiofiles
import config
from base.base_crawler import AbstractStore
from database.db_session import get_session
from database.models import TiebaNote, TiebaComment, TiebaCreator
from database.mongodb_store_base import MongoDBStoreBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tools import utils, words
from tools.async_file_writer import AsyncFileWriter
from var import crawler_type_var


def calculate_number_of_files(file_store_path: str) -> int:
    """计算数据保存文件的前部分排序数字，支持每次运行代码不写到同一个文件中
    Args:
        file_store_path;
    Returns:
        file nums
    """
    if not os.path.exists(file_store_path):
        return 1
    try:
        return max([int(file_name.split("_")[0]) for file_name in os.listdir(file_store_path)]) + 1
    except ValueError:
        return 1


class TieBaCsvStoreImplement(AbstractStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = AsyncFileWriter(platform="tieba", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        """
        tieba content CSV storage implementation
        Args:
            content_item: note item dict

        Returns:

        """
        await self.writer.write_to_csv(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        """
        tieba comment CSV storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        await self.writer.write_to_csv(item_type="comments", item=comment_item)

    async def store_creator(self, creator: Dict):
        """
        tieba content CSV storage implementation
        Args:
            creator: creator dict

        Returns:

        """
        await self.writer.write_to_csv(item_type="creators", item=creator)


class TieBaDbStoreImplement(AbstractStore):
    async def store_content(self, content_item: Dict):
        """
        tieba content DB storage implementation
        Args:
            content_item: content item dict
        """
        note_id = content_item.get("note_id")
        async with get_session() as session:
            stmt = select(TiebaNote).where(TiebaNote.note_id == note_id)
            res = await session.execute(stmt)
            db_note = res.scalar_one_or_none()
            if db_note:
                for key, value in content_item.items():
                    setattr(db_note, key, value)
            else:
                db_note = TiebaNote(**content_item)
                session.add(db_note)
            await session.commit()

    async def store_comment(self, comment_item: Dict):
        """
        tieba content DB storage implementation
        Args:
            comment_item: comment item dict
        """
        comment_id = comment_item.get("comment_id")
        async with get_session() as session:
            stmt = select(TiebaComment).where(TiebaComment.comment_id == comment_id)
            res = await session.execute(stmt)
            db_comment = res.scalar_one_or_none()
            if db_comment:
                for key, value in comment_item.items():
                    setattr(db_comment, key, value)
            else:
                db_comment = TiebaComment(**comment_item)
                session.add(db_comment)
            await session.commit()

    async def store_creator(self, creator: Dict):
        """
        tieba content DB storage implementation
        Args:
            creator: creator dict
        """
        user_id = creator.get("user_id")
        async with get_session() as session:
            stmt = select(TiebaCreator).where(TiebaCreator.user_id == user_id)
            res = await session.execute(stmt)
            db_creator = res.scalar_one_or_none()
            if db_creator:
                for key, value in creator.items():
                    setattr(db_creator, key, value)
            else:
                db_creator = TiebaCreator(**creator)
                session.add(db_creator)
            await session.commit()


class TieBaJsonStoreImplement(AbstractStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = AsyncFileWriter(platform="tieba", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        """
        tieba content JSON storage implementation
        Args:
            content_item: note item dict

        Returns:

        """
        await self.writer.write_single_item_to_json(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        """
        tieba comment JSON storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        await self.writer.write_single_item_to_json(item_type="comments", item=comment_item)

    async def store_creator(self, creator: Dict):
        """
        tieba content JSON storage implementation
        Args:
            creator: creator dict

        Returns:

        """
        await self.writer.write_single_item_to_json(item_type="creators", item=creator)


class TieBaSqliteStoreImplement(TieBaDbStoreImplement):
    """
    Tieba sqlite store implement
    """
    pass


class TieBaMongoStoreImplement(AbstractStore):
    """贴吧MongoDB存储实现"""
    
    def __init__(self):
        self.mongo_store = MongoDBStoreBase(collection_prefix="tieba")

    async def store_content(self, content_item: Dict):
        """
        存储帖子内容到MongoDB
        Args:
            content_item: 帖子内容数据
        """
        note_id = content_item.get("note_id")
        if not note_id:
            return
        
        await self.mongo_store.save_or_update(
            collection_suffix="contents",
            query={"note_id": note_id},
            data=content_item
        )
        utils.logger.info(f"[TieBaMongoStoreImplement.store_content] Saved note {note_id} to MongoDB")

    async def store_comment(self, comment_item: Dict):
        """
        存储评论到MongoDB
        Args:
            comment_item: 评论数据
        """
        comment_id = comment_item.get("comment_id")
        if not comment_id:
            return
        
        await self.mongo_store.save_or_update(
            collection_suffix="comments",
            query={"comment_id": comment_id},
            data=comment_item
        )
        utils.logger.info(f"[TieBaMongoStoreImplement.store_comment] Saved comment {comment_id} to MongoDB")

    async def store_creator(self, creator_item: Dict):
        """
        存储创作者信息到MongoDB
        Args:
            creator_item: 创作者数据
        """
        user_id = creator_item.get("user_id")
        if not user_id:
            return
        
        await self.mongo_store.save_or_update(
            collection_suffix="creators",
            query={"user_id": user_id},
            data=creator_item
        )
        utils.logger.info(f"[TieBaMongoStoreImplement.store_creator] Saved creator {user_id} to MongoDB")
