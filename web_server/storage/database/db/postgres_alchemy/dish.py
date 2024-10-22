"""storage/database/postgres_alchemy/dish"""
from datetime import datetime
from typing import Union, List
import logging

from sqlalchemy import text, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .alchemy_core import Base, async_session_maker
from storage.base_interface import database

from schemas import db_schemas


logger = logging.getLogger(f"app.{__name__}")


class DishTable(Base):
    """Таблица с данными о блюдах
    """

    __tablename__ = "dish_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu_table.id", ondelete="SET NULL"), nullable=False)
    code_name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[int] = mapped_column(nullable=False)
    count_type: Mapped[int] = mapped_column(default=1)
    count: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    changing_dish_id: Mapped[int] = mapped_column(ForeignKey("changing_dish_table.id", ondelete="SET NULL"), nullable=True)


class DishDAL(database.BaseDish):
    """Класс для работы с данными блюд"""

    async def get_data_by_menu_and_code_names(
            self,
            menu_id: int,
            code_names: list
    ) -> Union[List[db_schemas.dish.DishSchem], None]:
        """Извлечения списка блюд по кодовым названиям и идентификатору меню
        к которому они относятся
        Args:
            menu_id: (FK) идентификатор меню
            code_names: список кодовых имен блюд
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(DishTable).where(DishTable.menu_id == menu_id).where(DishTable.code_name.in_(code_names))
                    res = await session.execute(query)
                    data = res.all()
                    if data is not None:
                        list_of_dish = [
                            db_schemas.dish.DishSchem.model_validate(
                                from_attributes=True,
                                obj=data_queue_data[0]
                            ) for data_queue_data in data
                        ]

                        return list_of_dish if list_of_dish else None

        except Exception as _ex:
            logger.error(f"Ошибка при извлечении блюд из меню: {menu_id} и кодовым именам: {code_names} -> {_ex}")

    async def add_new_dish(
            self,
            name: str,
            menu_id: int,
            code_name: str,
            type: int,
            count_type: int,
            count: Union[int, None],
            price: int,
            changing_dish_id: Union[int, None]
    ) -> Union[db_schemas.dish.DishSchem, None]:
        """Добавления нового блюда в БД
        Args:
            name: наименования блюда
            menu_id: (FK) идентификатор меню к которому относится блюдо
            code_name: кодовое имя блюда (которое идентифицирует нейросеть)
            type: тип блюда
                (
                    1 - салат
                    2 - суп
                    3 - гарнир
                    4 - овощное блюдо
                    5 - рыбное блюдо
                    6 - блюдо из птицы
                    7 - блюдо из мяса
                    8 - выпечка
                    9 - напиток
                    10 - добавки
                    11 - неопределенное
                )
            count_type: тип количественной оценки блюда
                (
                    1 - измеряется в порциях
                    2 - измеряется в штуках
                    3 - измеряется в массе
                    4 - измеряется в объеме
                )
            count: единица кол-ва блюда
            price: стоимость единицы блюда
            changing_dish_id: (FK) сомнительная позиция, которую можно спутать с другой
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    new_dish = DishTable(
                        name=name,
                        menu_id=menu_id,
                        code_name=code_name,
                        type=type,
                        count_type=count_type,
                        count=count,
                        price=price,
                        changing_dish_id=changing_dish_id
                    )
                    session.add(new_dish)
                    await session.flush()
                    return db_schemas.dish.DishSchem.model_validate(
                        obj=new_dish,
                        from_attributes=True
                    )
        except Exception as _ex:
            logging.error(f"Ошибка при добавлении нового блюда. menu_id: {menu_id}, code_name: {code_name} -> {_ex}")

    async def get_data_by_menu_and_code_name(
            self,
            menu_id: int,
            code_name: str
    ) -> Union[db_schemas.dish.DishSchem, None]:
        """Извлечение одного блюда из БД
        Args:
            menu_id: (FK) идентификатор меню к которому относится блюдо
            code_name: кодовое имя блюда
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(DishTable).where(
                        (DishTable.menu_id == menu_id) &
                        (DishTable.code_name == code_name)
                    )
                    res = await session.execute(query)
                    data = res.fetchone()
                    if data is not None:
                        return db_schemas.dish.DishSchem.model_validate(
                            from_attributes=True,
                            obj=data[0],
                        )
        except Exception as _ex:
            logger.error(f'Ошибка при извлечении одного блюда. Меню: {menu_id}. {code_name} -> {_ex}')

    async def get_data_by_changing_id(self, changing_id: int) -> Union[db_schemas.dish.DishListSchem, None]:
        """Извлечение списка блюд по внешнему ключу ссылки на сомневающееся блюдо
        Args:
            changing_id: (FK) идентификатор сомнительного блюда
        """
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    query = select(DishTable).where(DishTable.changing_dish_id == changing_id)
                    res = await session.execute(query)
                    data = res.all()
                    if data is not None:
                        list_of_dish = [
                            db_schemas.dish.DishSchem.model_validate(
                                from_attributes=True,
                                obj=data_queue_data[0]
                            ) for data_queue_data in data
                        ]
                        if list_of_dish:
                            return db_schemas.dish.DishListSchem(dish_list=list_of_dish)
        except Exception as _ex:
            logger.error(f"Ошибка при извлечении сомневающихся блюд: {changing_id} -> {_ex}")