class TemplateDefinition:
    def __init__(self, name, fields, front_template, back_template):
        self.name = name
        self.fields = fields  # e.g., [{"id": "expression", "label": "Expression", "audio_allowed": False}]
        self.front_template = front_template
        self.back_template = back_template

TEMPLATES = [
    TemplateDefinition(
        name="Default Idioms Template",
        fields=[
            {"id": "expression", "label": "Expression", "audio_allowed": False},
            {"id": "meaning", "label": "Meaning", "audio_allowed": False},
            {"id": "example", "label": "Example Sentence", "audio_allowed": True},
        ],
        front_template="<div style='font-family: Arial; font-size: 26px; text-align: center; color: #4A90E2; font-weight: bold;'>{{EXPRESSION}}</div>",
        back_template="<div style='font-family: Arial; font-size: 20px; text-align: center; margin-bottom: 15px;'><b>Significado:</b> {{MEANING}}</div><hr id=answer><div style='font-size: 18px; color: #333; margin-top: 15px;'><i>Ejemplo:</i> {{EXAMPLE}} {{$_EXAMPLE}}</div>"
    )
]

def get_template_names():
    return [t.name for t in TEMPLATES]

def get_template_by_name(name):
    for t in TEMPLATES:
        if t.name == name:
            return t
    return None
