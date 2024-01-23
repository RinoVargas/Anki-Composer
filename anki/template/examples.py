from anki.template import PredefinedTemplate

ENGLISH_GOLDEN_LIST = PredefinedTemplate(
    deck_name="English Golden List",
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
