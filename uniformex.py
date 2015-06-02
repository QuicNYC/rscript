from django.shortcuts import get_object_or_404, render
from models import Sensor
from django import forms
from graph import Graph

from uni_form.helper import FormHelper
from uni_form.layout import Layout, Row, Div, Submit,MultiField,Column,Fieldset

class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label = "Do you like this website?",
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        initial = '1',
        required = True,
        localize=True
    )

    favorite_food = forms.CharField(
        label = "What is you favorite food?",
        max_length = 80,
        localize=(30,40),
        required = True,
    )

    favorite_color = forms.CharField(
        label = "What is you favorite color?",
        max_length = 80,
        required = True,
    )

    favorite_number = forms.IntegerField(
        label = "Favorite number",
        required = False,
    )

    notes = forms.CharField(
        label = "Additional notes or feedback",
        required = False,
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
        Fieldset(

                'like_website',
                'favorite_number',
                'favorite_color'

            ),
        Fieldset(

                'favorite_food',
                'notes'
                )

        )
        return super(ExampleForm, self).__init__(*args, **kwargs)
