
from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin

import models
import model_view
from db_core import Base
from db_core import engine

Base.metadata.create_all(engine)


# Создаем приложение Starlette
app = Starlette()

admin = Admin(engine, title="AI Kassa")

admin.add_view(model_view.CustomerModelView(models.CustomersTable, icon="fa fa-address-card", label="Customers"))

admin.mount_to(app)