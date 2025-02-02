from starlette_admin.contrib.sqla import ModelView

from models import CustomersTable, AuthTokenTable, MenuTable
from models import ChangingDishTable, DishTable, FoodPointTable
from models import WeekDayDishTable, RKeeperCredentialsTable
from models import RKeeperDishTable


class CustomerModelView(ModelView):
    fields = [
        CustomersTable.id,
        CustomersTable.name,
        CustomersTable.phone,
        CustomersTable.email
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
        AuthTokenTable.update_at
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
        MenuTable.system_name
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
        DishTable.type,
        DishTable.count_type,
        DishTable.count,
        DishTable.price,
        DishTable.menu,
        DishTable.changing_dish,
    ]


class FoodPointModelView(ModelView):
    fields = [
        FoodPointTable.id,
        FoodPointTable.name,
        FoodPointTable.country,
        FoodPointTable.district,
        FoodPointTable.city,
        FoodPointTable.address,
        FoodPointTable.customer
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
        RKeeperDishTable.dish,
        RKeeperDishTable.menu
    ]