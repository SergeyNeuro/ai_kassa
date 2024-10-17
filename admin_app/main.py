
from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin

import models
import model_view
from db_core import Base
from db_core import engine

Base.metadata.create_all(engine)


# Создаем приложение Starlette
app = Starlette()

admin = Admin(engine, title="AI Kassa", base_url="/")

admin.add_view(model_view.CustomerModelView(models.CustomersTable, icon="fa fa-address-card", label="Заказчики"))
admin.add_view(model_view.AuthTokenModelView(models.AuthTokenTable, icon="fa fa-key", label="Токены доступа"))
admin.add_view(model_view.MenuModelView(models.MenuTable, icon="fa fa-list", label="Меню"))
admin.add_view(model_view.DishModelView(models.DishTable, icon="fa fa-cutlery", label="Блюда"))
admin.add_view(model_view.ChangingDishModelView(models.ChangingDishTable, icon="fa fa-question", label="Сомневающиеся позиции"))
admin.add_view(model_view.FoodPointModelView(models.FoodPointTable, icon="fa fa-building", label="Точки приема пищи"))

admin.mount_to(app)