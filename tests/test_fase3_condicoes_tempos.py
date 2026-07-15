import csv
import io
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PSYEXP_PATH = ROOT / "stroop_go_nogo_ptbr.psyexp"
PRACTICE_PATH = ROOT / "condicoes" / "pratica_stroop_go_nogo_ptbr.csv"
MAIN_PATH = ROOT / "condicoes" / "bloco_principal_stroop_go_nogo_ptbr.csv"

WORDS_TO_COLORS = {
    "VERDE": ("green", "#16A34A"),
    "AMARELO": ("yellow", "#B77900"),
    "ROSA": ("pink", "#DB2777"),
    "PRETO": ("black", "#111111"),
    "VERMELHO": ("red", "#DC2626"),
    "LARANJA": ("orange", "#EA580C"),
    "MARROM": ("brown", "#92400E"),
    "ROXO": ("purple", "#7C3AED"),
    "AZUL": ("blue", "#2563EB"),
    "CINZA": ("gray", "#64748B"),
}
DISPLAY_PALETTE = {
    "green": "#40FF00",
    "yellow": "#FFF200",
    "pink": "#FF5CCB",
    "black": "#000000",
    "red": "#FF0000",
    "orange": "#FF9000",
    "brown": "#965000",
    "purple": "#9A24FF",
    "blue": "#0062FF",
    "gray": "#808080",
}
OFFICIAL_WORDS = set(WORDS_TO_COLORS)
OFFICIAL_COLORS = {color for color, _ in WORDS_TO_COLORS.values()}
OFFICIAL_DISPLAYS = {display for _, display in WORDS_TO_COLORS.values()}
DARK_BACKGROUND_RGB = "[-0.914, -0.875, -0.749]"
CONDITION_COLUMNS = [
    "trial_number",
    "word",
    "ink_color",
    "ink_color_display",
    "condition",
    "correct_response",
]


def read_condition_csv(path):
    raw = path.read_bytes()
    raw.decode("utf-8")
    text = raw.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    widths = {len(row) for row in rows}
    assert widths == {len(CONDITION_COLUMNS)}
    header = rows[0]
    assert header == CONDITION_COLUMNS
    return [dict(zip(header, row)) for row in rows[1:]]


def parse_psyexp():
    return ET.parse(PSYEXP_PATH).getroot()


def routine(root, name):
    for item in root.findall(".//Routine"):
        if item.get("name") == name:
            return item
    raise AssertionError(f"Routine not found: {name}")


def component(routine_element, tag, name):
    for item in routine_element.findall(tag):
        if item.get("name") == name:
            return item
    raise AssertionError(f"Component not found: {name}")


def param(component_element, name):
    for item in component_element.findall("Param"):
        if item.get("name") == name:
            return item.get("val")
    raise AssertionError(f"Param not found: {name}")


class Fase3CondicoesTemposTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.practice_rows = read_condition_csv(PRACTICE_PATH)
        cls.main_rows = read_condition_csv(MAIN_PATH)
        cls.psyexp = parse_psyexp()

    def assert_condition_rules(self, rows):
        for index, row in enumerate(rows, start=1):
            self.assertEqual(int(row["trial_number"]), index)
            self.assertIn(row["word"], OFFICIAL_WORDS)
            self.assertIn(row["ink_color"], OFFICIAL_COLORS)
            self.assertIn(row["ink_color_display"], OFFICIAL_DISPLAYS)
            self.assertEqual(
                row["ink_color_display"],
                dict(WORDS_TO_COLORS.values())[row["ink_color"]],
            )
            if row["condition"] == "congruent":
                self.assertEqual(row["correct_response"], "space")
                self.assertEqual(row["ink_color"], WORDS_TO_COLORS[row["word"]][0])
            elif row["condition"] == "incongruent":
                self.assertEqual(row["correct_response"], "")
                self.assertNotEqual(row["ink_color"], WORDS_TO_COLORS[row["word"]][0])
            else:
                self.fail(f"Invalid condition: {row['condition']}")

    def test_pratica_tem_4_linhas_e_balanceamento_2_2(self):
        rows = self.practice_rows
        self.assertEqual(len(rows), 4)
        self.assertEqual(Counter(row["condition"] for row in rows), {"congruent": 2, "incongruent": 2})
        self.assert_condition_rules(rows)

    def test_principal_tem_16_linhas_balanceamento_8_8_e_10_cores(self):
        rows = self.main_rows
        self.assertEqual(len(rows), 16)
        self.assertEqual(Counter(row["condition"] for row in rows), {"congruent": 8, "incongruent": 8})
        self.assertEqual({row["ink_color"] for row in rows}, OFFICIAL_COLORS)
        self.assertLessEqual(max(Counter(row["word"] for row in rows).values()), 2)
        self.assertGreaterEqual(min(Counter(row["word"] for row in rows).values()), 1)
        self.assertLessEqual(max(Counter(row["ink_color"] for row in rows).values()), 3)
        self.assertGreaterEqual(min(Counter(row["ink_color"] for row in rows).values()), 1)
        self.assert_condition_rules(rows)

        incongruent_rows = [row for row in rows if row["condition"] == "incongruent"]
        self.assertEqual(
            len({(row["word"], row["ink_color"]) for row in incongruent_rows}),
            len(incongruent_rows),
        )
        for previous, current in zip(rows, rows[1:]):
            self.assertNotEqual(previous["word"], current["word"])
            self.assertNotEqual(previous["ink_color"], current["ink_color"])

    def test_csv_unificado_preserva_ink_color_logico_sem_display(self):
        text = PSYEXP_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("'word'", text)
        self.assertIn("'ink_color'", text)
        self.assertIn("'condition'", text)
        self.assertIn("'correct_response'", text)
        self.assertIn("'ink_color': trial_context['ink_color']", text)
        self.assertNotIn("'ink_color_display'", text.split("OFFICIAL_CSV_COLUMNS = [", 1)[1].split("]", 1)[0])
        self.assertNotIn("'_raw'", text.split("OFFICIAL_CSV_COLUMNS = [", 1)[1].split("]", 1)[0])

    def test_psyexp_usa_paleta_visual_por_chave_logica(self):
        practice = routine(self.psyexp, "trial_pratica")
        palette_code = param(
            component(practice, "CodeComponent", "renderizacao_cores_pratica"),
            "Before Experiment",
        )
        for logical_color, display_color in DISPLAY_PALETTE.items():
            self.assertIn(f"'{logical_color}': '{display_color}'", palette_code)

        self.assertEqual(set(DISPLAY_PALETTE), OFFICIAL_COLORS)
        self.assertEqual(len(set(DISPLAY_PALETTE.values())), 10)
        for routine_name, component_name in [
            ("trial_pratica", "stim_pratica"),
            ("trial_principal", "stim_principal"),
        ]:
            item = component(routine(self.psyexp, routine_name), "TextComponent", component_name)
            self.assertEqual(param(item, "color"), "$INK_COLOR_DISPLAY_MAP[ink_color]")
            self.assertEqual(param(item, "text"), "$word")

    def test_estimulos_tem_centralizacao_explicita_em_pratica_e_principal(self):
        for routine_name, code_name, stim_name in [
            ("trial_pratica", "renderizacao_cores_pratica", "stim_pratica"),
            ("trial_principal", "renderizacao_cores_principal", "stim_principal"),
        ]:
            code = param(
                component(routine(self.psyexp, routine_name), "CodeComponent", code_name),
                "Begin Routine",
            )
            self.assertIn(f"{stim_name}.alignText = 'center'", code)
            self.assertIn(f"{stim_name}.anchorHoriz = 'center'", code)
            self.assertIn(f"{stim_name}.anchorVert = 'center'", code)

    def test_cartao_e_estimulo_compartilham_posicao_central(self):
        for routine_name, card_name, stim_name in [
            ("trial_pratica", "stim_card_pratica", "stim_pratica"),
            ("trial_principal", "stim_card_principal", "stim_principal"),
        ]:
            trial = routine(self.psyexp, routine_name)
            card = component(trial, "TextComponent", card_name)
            stim = component(trial, "TextComponent", stim_name)
            fix = component(trial, "TextComponent", "fix_pratica" if routine_name == "trial_pratica" else "fix_principal")
            hold = component(trial, "TextComponent", "hold_pratica" if routine_name == "trial_pratica" else "hold_principal")

            self.assertEqual(param(card, "pos"), "[0, 0]")
            self.assertEqual(param(stim, "pos"), "[0, 0]")
            self.assertEqual(param(fix, "pos"), "[0, 0]")
            self.assertEqual(param(hold, "pos"), "[0, 0]")

    def test_paleta_visual_tem_10_cores_distintas(self):
        displays = list(DISPLAY_PALETTE.values())
        self.assertEqual(len(displays), 10)
        self.assertEqual(len(set(displays)), 10)
        for first, second in [
            ("black", "gray"),
            ("red", "pink"),
            ("orange", "brown"),
            ("blue", "purple"),
            ("yellow", "black"),
            ("yellow", "gray"),
        ]:
            self.assertNotEqual(DISPLAY_PALETTE[first], DISPLAY_PALETTE[second])

    def test_tempos_de_tentativa_pratica(self):
        trial = routine(self.psyexp, "trial_pratica")
        response = component(trial, "KeyboardComponent", "resp_pratica")
        fix = component(trial, "TextComponent", "fix_pratica")
        stim = component(trial, "TextComponent", "stim_pratica")
        reminder = component(trial, "TextComponent", "lembrete_pratica")
        hold = component(trial, "TextComponent", "hold_pratica")

        self.assertEqual(param(fix, "startVal"), "0")
        self.assertEqual(param(fix, "stopVal"), "0.3")
        self.assertEqual(param(stim, "startVal"), "0.3")
        self.assertEqual(param(stim, "stopVal"), "2.0")
        self.assertEqual(param(reminder, "startVal"), "0.3")
        self.assertEqual(param(reminder, "stopVal"), "2.0")
        self.assertEqual(param(response, "startVal"), "0.3")
        self.assertEqual(param(response, "stopVal"), "2.0")
        self.assertEqual(param(response, "forceEndRoutine"), "False")
        self.assertEqual(param(response, "discard previous"), "True")
        self.assertEqual(param(hold, "startVal"), "0")
        self.assertEqual(param(hold, "stopVal"), "2.8")

        feedback = component(routine(self.psyexp, "feedback_pratica"), "TextComponent", "texto_feedback")
        self.assertEqual(param(feedback, "stopVal"), "0.5")

    def test_tempos_de_tentativa_principal_e_duracao_de_60_segundos(self):
        trial = routine(self.psyexp, "trial_principal")
        response = component(trial, "KeyboardComponent", "resp_principal")
        fix = component(trial, "TextComponent", "fix_principal")
        stim = component(trial, "TextComponent", "stim_principal")
        hold = component(trial, "TextComponent", "hold_principal")

        self.assertEqual(param(fix, "startVal"), "0")
        self.assertEqual(param(fix, "stopVal"), "0.3")
        self.assertEqual(param(stim, "startVal"), "0.3")
        self.assertEqual(param(stim, "stopVal"), "2.5")
        self.assertEqual(param(response, "startVal"), "0.3")
        self.assertEqual(param(response, "stopVal"), "2.5")
        self.assertEqual(param(response, "forceEndRoutine"), "False")
        self.assertEqual(param(response, "discard previous"), "True")
        self.assertEqual(param(hold, "startVal"), "0")
        self.assertEqual(param(hold, "stopVal"), "3.75")
        self.assertEqual(len(self.main_rows) * 3.75, 60.0)

    def test_trial_principal_nao_tem_texto_instrucional_visivel(self):
        trial = routine(self.psyexp, "trial_principal")
        forbidden = [
            "pressione",
            "espaço",
            "espaco",
            "enter",
            "continue",
            "combinar",
        ]
        allowed_dynamic_texts = {
            "$word",
            "$main_accuracy_text",
            "$main_accuracy_bar",
            "$timer_text",
            "$progress_text",
        }
        for item in trial.findall("TextComponent"):
            text = param(item, "text") or ""
            disabled = param(item, "disabled")
            if disabled == "True":
                continue
            if text in allowed_dynamic_texts or text in ["+", "."]:
                continue
            lowered = text.lower()
            self.assertTrue(
                all(pattern not in lowered for pattern in forbidden),
                f"{item.get('name')} contem texto instrucional: {text!r}",
            )

    def test_hud_precisao_e_cronometro(self):
        practice = routine(self.psyexp, "trial_pratica")
        main = routine(self.psyexp, "trial_principal")

        self.assertEqual(param(component(practice, "TextComponent", "hud_pratica_precisao"), "text"), "$practice_accuracy_text")
        self.assertEqual(param(component(practice, "TextComponent", "hud_pratica_barra"), "text"), "$practice_accuracy_bar")
        self.assertEqual(param(component(practice, "TextComponent", "hud_pratica_tempo"), "text"), "Tempo: --:--")
        self.assertEqual(param(component(main, "TextComponent", "hud_principal_precisao"), "text"), "$main_accuracy_text")
        self.assertEqual(param(component(main, "TextComponent", "hud_principal_barra"), "text"), "$main_accuracy_bar")
        self.assertEqual(param(component(main, "TextComponent", "hud_principal_tempo"), "text"), "$timer_text")
        self.assertEqual(param(component(main, "TextComponent", "hud_principal_tempo"), "text"), "$timer_text")

        practice_code = component(practice, "CodeComponent", "codigo_pratica")
        main_code = component(main, "CodeComponent", "codigo_principal")
        self.assertIn("hud_state = {", param(practice_code, "Before Experiment"))
        self.assertIn("hud_state['practice_completed'] += 1", param(practice_code, "End Routine"))
        self.assertIn("hud_state['main_completed'] += 1", param(main_code, "End Routine"))
        self.assertNotIn("official_trial_rows.append", param(practice_code, "End Routine"))
        self.assertIn("official_trial_rows.append(trial_record)", param(main_code, "End Routine"))
        self.assertIn("if not hud_state['main_timer_started']:", param(main_code, "Begin Routine"))
        self.assertNotIn("global practice_completed", param(practice_code, "Begin Routine"))
        self.assertNotIn("global practice_completed", param(practice_code, "End Routine"))
        self.assertNotIn("global practice_completed", param(main_code, "Begin Routine"))
        self.assertNotIn("global practice_completed", param(main_code, "End Routine"))
        self.assertIn("timer_text = format_main_time()", param(main_code, "Each Frame"))

    def test_cor_de_fundo_global_e_lista_rgb_segura_para_builder(self):
        settings = self.psyexp.find("Settings")
        color = param(settings, "color")
        self.assertEqual(color, DARK_BACKGROUND_RGB)
        self.assertFalse(color.startswith("#"))


if __name__ == "__main__":
    unittest.main()
