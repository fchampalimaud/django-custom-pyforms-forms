from pyforms_web.basewidget import BaseWidget
from custom_forms.models import FormType, FormTypeObject, FieldValue
from pyforms.basewidget import no_columns, segment
import datetime

class CustomForm(BaseWidget):

    CUSTOM_FORM_CODE = None

    def __init__(self, *args, **kwargs):

        formtype = kwargs.get('form_type', None)
        formcode = kwargs.get('form_code', self.CUSTOM_FORM_CODE)

        if formtype is None and formcode:
            formtype = FormType.objects.get(form_code=formcode)

        if formtype is None:
            raise Exception('No form type defined')
        else:
            self.formtype = formtype

        kwargs['title'] = formtype.form_name

        super().__init__(*args, **kwargs)

        for i, field in enumerate(formtype.fields.all()):
            setattr(self, field.field_name, field.create_control() )

        if formtype.form_set:
            self.formset = eval(formtype.form_set)

    def save_custom_form(self, obj):
        form_obj, created = FormTypeObject.objects.get_or_create(
            content_type=self.formtype.content_type,
            object_id=obj.pk,
            form_type=self.formtype
        )

        # remove all existing register if the formtype was updated
        if created:
            FieldValue.objects.filter(formtype_object=form_obj).delete()

        for i, field in enumerate(self.formtype.fields.all()):
            pyforms_field = getattr(self, field.field_name)

            field_value, created = FieldValue.objects.get_or_create(formtype_object=form_obj, formtype_field=field)
            print(pyforms_field.value, type(pyforms_field.value))
            field_value.value = pyforms_field.value
            field_value.save()


    def load_custom_form(self, obj):
        form_obj = FormTypeObject.objects.get(
            form_type=self.formtype,
            object_id=obj.pk
        )

        for i, field in enumerate(self.formtype.fields.all()):
            pyforms_field = getattr(self, field.field_name)

            field_value = FieldValue.objects.filter(formtype_object=form_obj, formtype_field=field).first()
            print(field_value)
            if field_value:
                pyforms_field.value = field_value.value
