"""storage/database/postgres_alchemy/week_day_dish"""
from datetime import datetime
from typing import Union, List
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class WeekDayDishTable(Base):
    """Таблица с данными о меню
    Attr:
        id: идентификатор записи
        week_day: день недели в integer представлении
        dish_id: идентификатор блюда
        changing_dish_id: идентификатор сомневающегося блюда
    """

    __tablename__ = "week_day_dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    week_day: Mapped[int] = mapped_column(nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dish_table.id", ondelete="CASCADE"), nullable=False)
    changing_dish_id: Mapped[int] = mapped_column(ForeignKey("changing_dish_table.id", ondelete="CASCADE"),
                                                  nullable=False)


class WeekDayDishDAL(database.BaseWeekDayDish):
    async def get_dish_list_by_week_day_and_changing_id(
            self,
            changing_id: int,
            week_day: int
    ) -> Union[db_schemas.dish.DishListSchem, None]:
        """Извлечение списка блюд зависимых от дня недели
        Args:
            changing_id: идентификатор сомневающейся позиции
            week_day: день недели за который нужно извлечь позиции
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = text(f"""
                                SELECT * FROM dish_table AS d
                                JOIN week_day_dish_table AS w on d.id = w.dish_id
                                WHERE w.week_day = {week_day} AND w.changing_dish_id = {changing_id}
                            """)
                    res = await session.execute(query)
                    data = res.fetchall()
                    if data:
                        # Преобразование результата в список объектов DishSchem
                        list_of_dish = [
                            db_schemas.dish.DishSchem(
                                id=row[0],
                                name=row[1],
                                menu_id=row[2],
                                code_name=row[3],
                                type=row[4],
                                count_type=row[5],
                                count=row[6],
                                price=row[7],
                                changing_dish_id=row[8]
                            ) for row in data
                        ]
                        return db_schemas.dish.DishListSchem(dish_list=list_of_dish)
                    return None

        except Exception as _ex:
            logger.error(f"Ошибка при извлечении блюд по дню недели {week_day} и спорному продукту: {changing_id}  -> {_ex}")


