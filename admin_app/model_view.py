from starlette_admin.contrib.sqla import ModelView

from models import CustomersTable


class CustomerModelView(ModelView):
    icon = "fa fa-address-card"

    fields = [
        CustomersTable.id,
        CustomersTable.name,
        CustomersTable.phone,
        CustomersTable.email
    ]