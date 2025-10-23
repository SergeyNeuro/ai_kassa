from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import EnumField

from models import (
    CustomersTable, AuthTokenTable, MenuTable, ChangingDishTable, DishTable,
    FoodPointTable, WeekDayDishTable, RKeeperCredentialsTable, RKeeperDishTable,
    DiscountAccountTable, KassaTable, HistoryTable, DiscountTransactionTable,
    IikoCredentialsTable
)


class CustomerModelView(ModelView):
    fields = [
        CustomersTable.id,
        CustomersTable.name,
        CustomersTable.phone,
        CustomersTable.email,
        EnumField("discount_type", choices=[
            (1, "Без скидок"),
            (2, "Столовая 67")
        ]),

        CustomersTable.token,
        CustomersTable.menu,
        CustomersTable.food_point
    ]


class AuthTokenModelView(ModelView):
    fields = [
        AuthTokenTable.id,
        AuthTokenTable.name,
        AuthTokenTable.token,
        AuthTokenTable.customer,
        AuthTokenTable.role,
        AuthTokenTable.details,
        AuthTokenTable.created_at,
        AuthTokenTable.update_at,
    ]

    exclude_fields_from_create = [AuthTokenTable.created_at, AuthTokenTable.update_at]
    exclude_fields_from_edit = [AuthTokenTable.created_at, AuthTokenTable.update_at]


class MenuModelView(ModelView):
    fields = [
        MenuTable.id,
        MenuTable.name,
        MenuTable.customer,
        MenuTable.ai_model_name,
        MenuTable.details,
        EnumField("system_name", choices=[
            ("r-keeper", "r-keeper"),
            ("iiko", "iiko")
        ]),
        MenuTable.iiko,
        MenuTable.dish
    ]


class ChangingDishModelView(ModelView):
    fields = [
        ChangingDishTable.id,
        ChangingDishTable.name,
        ChangingDishTable.menu,
        ChangingDishTable.strategy
    ]


class DishModelView(ModelView):
    fields = [
        DishTable.id,
        DishTable.name,
        DishTable.code_name,
        EnumField(
            "type",
            choices=[
                (1, "салат"),
                (2, "суп"),
                (3, "гарнир"),
                (4, "овощное блюдо"),
                (5, "рыбное блюдо"),
                (6, "блюдо из птицы"),
                (7, "блюдо из мяса"),
                (8, "выпечка"),
                (9, "напиток"),
                (10, "добавки"),
                (11, "неопределенное")
            ],
            coerce=int
        ),
        EnumField(
            "count_type",
            choices=[
                (1, "порций (неизм)"),
                (2, "шт (неизм)"),
                (3, "грамм (неизм)"),
                (4, "мл (неизм)"),
                (11, "порций"),
                (12, "шт"),
                (13, "грамм"),
                (14, "мл"),
            ],
            coerce=int
        ),
        DishTable.count,
        DishTable.price,
        DishTable.menu,
        DishTable.changing_dish,
        DishTable.barcode,

    ]


class FoodPointModelView(ModelView):
    fields = [
        FoodPointTable.id,
        FoodPointTable.name,
        FoodPointTable.country,
        FoodPointTable.district,
        FoodPointTable.city,
        FoodPointTable.address,
        FoodPointTable.customer,
        FoodPointTable.kassa
    ]


class WeekDayDishModelView(ModelView):
    fields = [
        WeekDayDishTable.id,
        WeekDayDishTable.week_day,
        WeekDayDishTable.dish,
        WeekDayDishTable.changing_dish
    ]


class RKeeperCredentialsModelView(ModelView):
    fields = [
        RKeeperCredentialsTable.id,
        RKeeperCredentialsTable.name,
        RKeeperCredentialsTable.token,
        RKeeperCredentialsTable.object_id,
        RKeeperCredentialsTable.menu,
        RKeeperCredentialsTable.created_at,
        RKeeperCredentialsTable.update_at,
    ]

    exclude_fields_from_create = [RKeeperCredentialsTable.created_at, RKeeperCredentialsTable.update_at]
    exclude_fields_from_edit = [RKeeperCredentialsTable.created_at, RKeeperCredentialsTable.update_at]


class RKeeperDishModelView(ModelView):
    fields = [
        RKeeperDishTable.id,
        RKeeperDishTable.name,
        RKeeperDishTable.r_keeper_id,
        RKeeperDishTable.dish,
        RKeeperDishTable.menu
    ]

class IikoCredentialsView(ModelView):
    pass


class IikoTerminalView(ModelView):
    pass


class IikoDishView(ModelView):
    pass


class DiscountAccountView(ModelView):
    fields = [
        DiscountAccountTable.id,
        DiscountAccountTable.discount_id,
        EnumField("type", choices=[
            (2, "Столовая 67")
        ]),
        DiscountAccountTable.email,
        DiscountAccountTable.phone,
        DiscountAccountTable.balance,
        DiscountAccountTable.created_at,
        DiscountAccountTable.update_at,
        DiscountAccountTable.customer
    ]

    exclude_fields_from_create = [DiscountAccountTable.created_at, DiscountAccountTable.update_at]
    exclude_fields_from_edit = [DiscountAccountTable.created_at, DiscountAccountTable.update_at]


class KassaView(ModelView):
    fields = [
        KassaTable.id,
        KassaTable.name,
        KassaTable.login,
        KassaTable.password,
        KassaTable.address,
        KassaTable.food_point
    ]


class HistoryView(ModelView):
    fields = [
        HistoryTable.id,
        HistoryTable.kassa,
        HistoryTable.value,
        HistoryTable.products,
        HistoryTable.created_at
    ]

    exclude_fields_from_create = [HistoryTable.created_at]
    exclude_fields_from_edit = [HistoryTable.created_at]


class DiscountTransactionView(ModelView):
    fields = [
        DiscountTransactionTable.id,
        DiscountTransactionTable.kassa,
        EnumField("way", choices=[(1, "Трата баллов"), (2, "Пополнение баллов")]),
        DiscountTransactionTable.value,
        DiscountTransactionTable.created_at
    ]

    exclude_fields_from_create = [DiscountTransactionTable.created_at]
    exclude_fields_from_edit = [DiscountTransactionTable.created_at]