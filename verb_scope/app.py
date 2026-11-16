"""Gradio user interface for VerbScope."""

import html
import gradio as gr
from .analyzer import analyze_text


EXAMPLES = [
    ["Учора Марія читала книжку, а діти гралися у дворі."],
    ["Сьогодні студенти пишуть роботу та слухають викладача."],
    ["Завтра ми поїдемо до Львова і відвідаємо музей."],
]


def run_analysis(text):
    if not text or not text.strip():
        return "Введіть текст для аналізу.", [], "У тексті ще немає результатів."

    try:
        results = analyze_text(text)
    except Exception as exc:
        return f"Помилка аналізу: {exc}", [], html.escape(text)

    if not results:
        return "Дієслів не знайдено.", [], html.escape(text)

    # Highlight detected word forms in the original text, case-insensitively.
    # Replace whole-word matches only, preserving punctuation and spacing.
    import re
    highlighted = text
    unique_forms = sorted({item["word"] for item in results}, key=len, reverse=True)
    for form in unique_forms:
        pattern = r"(?<!\\w)" + re.escape(form) + r"(?!\\w)"
        highlighted = re.sub(
            pattern,
            lambda match: (
                '<mark style="background:#ffe08a;padding:2px 4px;'
                'border-radius:4px;font-weight:600;">'
                + html.escape(match.group(0)) + "</mark>"
            ),
            highlighted,
            flags=re.IGNORECASE,
        )

    table = [
        [
            item["word"],
            item["lemma"],
            item["time"],
            item["number"],
            item["gender"],
        ]
        for item in results
    ]
    count = len(results)
    return f"Знайдено дієслів: {count}", table, highlighted


def build_app():
    with gr.Blocks(title="VerbScope — аналізатор дієслів", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # VerbScope
            ### Аналізатор дієслів української мови

            Вставте текст українською мовою. Програма знайде дієслівні форми,
            підсвітить їх і спробує визначити граматичні характеристики.
            """
        )
        source = gr.Textbox(
            label="Текст для аналізу",
            placeholder="Наприклад: Учора я читала книжку, а сьогодні пишу конспект.",
            lines=6,
        )
        with gr.Row():
            analyze_btn = gr.Button("Проаналізувати", variant="primary")
            clear_btn = gr.ClearButton([source])
        status = gr.Markdown()
        table = gr.Dataframe(
            headers=["Дієслово", "Початкова форма", "Час", "Число", "Рід (минулий час)"],
            datatype=["str", "str", "str", "str", "str"],
            label="Результати морфологічного аналізу",
            interactive=False,
            wrap=True,
        )
        highlighted = gr.HTML(label="Текст із виділеними дієсловами")
        gr.Examples(examples=EXAMPLES, inputs=source, label="Тестові приклади")

        analyze_btn.click(
            fn=run_analysis,
            inputs=source,
            outputs=[status, table, highlighted],
        )
        source.submit(
            fn=run_analysis,
            inputs=source,
            outputs=[status, table, highlighted],
        )
    return demo


def launch():
    build_app().launch()
