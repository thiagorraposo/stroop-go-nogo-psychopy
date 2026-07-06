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
    "VERDE": ("green", "#1BAE55"),
    "AMARELO": ("yellow", "#B8860B"),
    "ROSA": ("pink", "#D42E88"),
    "PRETO": ("black", "#1A1A1A"),
    "VERMELHO": ("red", "#CF2E2E"),
    "LARANJA": ("orange", "#E56A00"),
    "MARROM": ("brown", "#6D4027"),
    "ROXO": ("purple", "#7837B8"),
    "AZUL": ("blue", "#1976D2"),
    "CINZA": ("gray", "#626870"),
}
OFFICIAL_WORDS = set(WORDS_TO_COLORS)
OFFICIAL_COLORS = {color for color, _ in WORDS_TO_COLORS.values()}
OFFICIAL_DISPLAYS = {display for _, display in WORDS_TO_COLORS.values()}
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

    def test_pratica_tem_10_cores_e_balanceamento_5_5(self):
        rows = self.practice_rows
        self.assertEqual(len(rows), 10)
        self.assertEqual({row["word"] for row in rows}, OFFICIAL_WORDS)
        self.assertEqual({row["ink_color"] for row in rows}, OFFICIAL_COLORS)
        self.assertEqual(Counter(row["word"] for row in rows), Counter(OFFICIAL_WORDS))
        self.assertEqual(Counter(row["ink_color"] for row in rows), Counter(OFFICIAL_COLORS))
        self.assertEqual(Counter(row["condition"] for row in rows), {"congruent": 5, "incongruent": 5})
        self.assert_condition_rules(rows)

    def test_principal_tem_60_linhas_e_balanceamento_40_20(self):
        rows = self.main_rows
        self.assertEqual(len(rows), 60)
        self.assertEqual(Counter(row["condition"] for row in rows), {"congruent": 40, "incongruent": 20})
        self.assertEqual(Counter(row["word"] for row in rows), {word: 6 for word in OFFICIAL_WORDS})
        self.assertEqual(Counter(row["ink_color"] for row in rows), {color: 6 for color in OFFICIAL_COLORS})
        self.assert_condition_rules(rows)

        congruent_rows = [row for row in rows if row["condition"] == "congruent"]
        incongruent_rows = [row for row in rows if row["condition"] == "incongruent"]
        self.assertEqual(Counter(row["word"] for row in congruent_rows), {word: 4 for word in OFFICIAL_WORDS})
        self.assertEqual(Counter(row["word"] for row in incongruent_rows), {word: 2 for word in OFFICIAL_WORDS})
        self.assertEqual(Counter(row["ink_color"] for row in congruent_rows), {color: 4 for color in OFFICIAL_COLORS})
        self.assertEqual(Counter(row["ink_color"] for row in incongruent_rows), {color: 2 for color in OFFICIAL_COLORS})
        self.assertEqual(
            len({(row["word"], row["ink_color"]) for row in incongruent_rows}),
            len(incongruent_rows),
        )

    def test_csv_unificado_preserva_ink_color_logico_sem_display(self):
        text = PSYEXP_PATH.read_text(encoding="utf-8-sig")
        self.assertIn("'word'", text)
        self.assertIn("'ink_color'", text)
        self.assertIn("'condition'", text)
        self.assertIn("'correct_response'", text)
        self.assertIn("'ink_color': trial_context['ink_color']", text)
        self.assertNotIn("'ink_color_display'", text.split("OFFICIAL_CSV_COLUMNS = [", 1)[1].split("]", 1)[0])

    def test_psyexp_usa_hexadecimal_para_renderizar_estimulos(self):
        for routine_name, component_name in [
            ("trial_pratica", "stim_pratica"),
            ("trial_principal", "stim_principal"),
        ]:
            item = component(routine(self.psyexp, routine_name), "TextComponent", component_name)
            self.assertEqual(param(item, "color"), "$ink_color_display")
            self.assertEqual(param(item, "text"), "$word")

    def test_tempos_de_tentativa_pratica_e_principal(self):
        for routine_name, response_name, fix_name, stim_name, reminder_name, hold_name in [
            ("trial_pratica", "resp_pratica", "fix_pratica", "stim_pratica", "lembrete_pratica", "hold_pratica"),
            ("trial_principal", "resp_principal", "fix_principal", "stim_principal", "lembrete_principal", "hold_principal"),
        ]:
            trial = routine(self.psyexp, routine_name)
            response = component(trial, "KeyboardComponent", response_name)
            fix = component(trial, "TextComponent", fix_name)
            stim = component(trial, "TextComponent", stim_name)
            reminder = component(trial, "TextComponent", reminder_name)
            hold = component(trial, "TextComponent", hold_name)

            self.assertEqual(param(fix, "startVal"), "0")
            self.assertEqual(param(fix, "stopVal"), "0.3")
            self.assertEqual(param(stim, "startVal"), "0.3")
            self.assertEqual(param(stim, "stopVal"), "1.5")
            self.assertEqual(param(reminder, "startVal"), "0.3")
            self.assertEqual(param(reminder, "stopVal"), "1.5")
            self.assertEqual(param(response, "startVal"), "0.3")
            self.assertEqual(param(response, "stopVal"), "1.5")
            self.assertEqual(param(response, "forceEndRoutine"), "False")
            self.assertEqual(param(response, "discard previous"), "True")
            self.assertEqual(param(hold, "startVal"), "0")
            self.assertEqual(param(hold, "stopVal"), "2.0")

    def test_bloco_principal_dura_aproximadamente_120_segundos(self):
        self.assertEqual(len(self.main_rows) * 2.0, 120.0)


if __name__ == "__main__":
    unittest.main()
