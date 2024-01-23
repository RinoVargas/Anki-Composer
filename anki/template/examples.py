from anki.template import PredefinedTemplate, TemplateField

ENGLISH_GOLDEN_LIST = PredefinedTemplate(
    deck_name="English Golden List",
    fields=[
        TemplateField(name="EXPRESSION"),
        TemplateField(name="MEANING"),
        TemplateField(name="EXAMPLE 1"),
        TemplateField(name="EXAMPLE 2"),
        TemplateField(name="EXAMPLE 3"),
        TemplateField(name="AUDIO 1", field_type="AUDIO", related_text_field_name="EXAMPLE 1"),
        TemplateField(name="AUDIO 2", field_type="AUDIO", related_text_field_name="EXAMPLE 2"),
        TemplateField(name="AUDIO 3", field_type="AUDIO", related_text_field_name="EXAMPLE 3"),

    ],
    front_template="<div style='font-family: arial; font-size: 25px; text-align: center; color: white;'>{{EXPRESSION}}</div>",
    back_template="""
        <i>Meaning:</i> {{MEANING}}
        <hr id=answer>

        <i>Examples:</i> 
        <ul>
            <li>{{EXAMPLE 1}} {{AUDIO 1}}</li>
            <li>{{EXAMPLE 2}} {{AUDIO 2}}</li>
            <li>{{EXAMPLE 3}} {{AUDIO 3}}</li>
        </ul>""".strip()
)
