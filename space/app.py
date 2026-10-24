import gradio as gr

from pt2barranquenho import translate

EXAMPLES = [
    "A minha mãe disse-me que o leite estava frio.",
    "Ontem fomos à feira e comprámos três quilos de feijão.",
    "Não consigo encontrar nenhum alarme.",
    "O tempo amanhã vai estar nublado com aguaceiros.",
    "Eu não gosto do mar.",
    "Hoje cheguei tarde e ele saiu.",
    "Faz vinte anos que vivo em Barrancos.",
    "Lembra-me de comprar pão às cinco horas.",
]

ABOUT = """\
Barranquenho is the language of Barrancos, on the Portuguese border with Spain. This page converts European
Portuguese into Barranquenho with hand-written rules from the *Convenção Ortográfica do Barranquenho* and the
*Gramática Básica de Barranquenho* (Gonçalves, Navas, Correia; Universidade de Évora, 2025).

The output follows the spelling and grammar rules of the two books. It is not a native translation: no speaker has
reviewed it, and Barranquenho has words and turns of phrase that rules cannot predict. Each line is converted on its
own.
"""


def convert(text: str) -> str:
    return "\n".join(translate(line) for line in text.split("\n"))


with gr.Blocks(title="Português → Barranquenho") as demo:
    gr.Markdown("# Português → Barranquenho")
    gr.Markdown(ABOUT)
    with gr.Row():
        source = gr.Textbox(label="Português", lines=6, placeholder="Escreva uma frase em português europeu.")
        target = gr.Textbox(label="Barranquenho", lines=6, interactive=False)
    button = gr.Button("Converter", variant="primary")
    button.click(convert, source, target)
    source.submit(convert, source, target)
    gr.Examples(EXAMPLES, source, target, convert, run_on_click=True)

if __name__ == "__main__":
    demo.launch()
