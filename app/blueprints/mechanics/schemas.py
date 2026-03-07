from app.extensions import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address_line1",
            "city",
            "state",
            "postal_code",
            "salary",
            "hire_date",
            "is_active",
        )


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
