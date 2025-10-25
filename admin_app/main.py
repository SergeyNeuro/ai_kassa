
from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin

import models
import model_view
from db_core import Base
from db_core import engine

# Base.metadata.create_all(engine)


# Создаем приложение Starlette
app = Starlette()

admin = Admin(engine, title="AI Kassa", base_url="/")

admin.add_view(model_view.CustomerModelView(models.CustomersTable, icon="fa fa-address-card", label="Заказчики"))
admin.add_view(model_view.AuthTokenModelView(models.AuthTokenTable, icon="fa fa-key", label="Токены доступа"))
admin.add_view(model_view.MenuModelView(models.MenuTable, icon="fa fa-list", label="Меню"))
admin.add_view(model_view.CategoriesView(models.CategoriesTable, icon="fa-solid fa-layer-group", label="Категории блюд"))
admin.add_view(model_view.DishModelView(models.DishTable, icon="fa fa-cutlery", label="Блюда"))
admin.add_view(model_view.ChangingDishModelView(models.ChangingDishTable, icon="fa fa-question", label="Сомневающиеся позиции"))
admin.add_view(model_view.WeekDayDishModelView(models.WeekDayDishTable, icon="fa fa-calendar", label="Блюда по дням недели"))
admin.add_view(model_view.FoodPointModelView(models.FoodPointTable, icon="fa fa-building", label="Точки приема пищи"))
admin.add_view(model_view.KassaView(models.KassaTable, icon="fa fa-shopping-cart", label="Касса"))
admin.add_view(model_view.HistoryView(models.HistoryTable, icon="fa fa-book", label="История покупок"))

admin.add_view(model_view.RKeeperCredentialsModelView(models.RKeeperCredentialsTable, icon="fa fa-registered", label="r-keeper авторизация"))
admin.add_view(model_view.RKeeperDishModelView(models.RKeeperDishTable, icon="fa fa-search-minus", label="Блюда r_keeper"))

# iiko
admin.add_view(model_view.IikoCredentialsView(models.IikoCredentialsTable, icon="fa-solid fa-keyboard", label="Iiko доступы"))
admin.add_view(model_view.IikoTerminalView(models.IikoTerminalsTable, icon="fa-solid fa-terminal", label="Терминал Iiko") )
admin.add_view(model_view.IikoDishView(models.IikoDishesTable, icon="fa-solid fa-display", label="Блюда IIKO"))

admin.add_view(model_view.DiscountAccountView(models.DiscountAccountTable, icon="fa fa-percent", label="Скидочный аккаунт"))
admin.add_view(model_view.DiscountTransactionView(models.DiscountTransactionTable, icon="fa fa-arrows-h", label="Транзакции баллов"))

admin.mount_to(app)