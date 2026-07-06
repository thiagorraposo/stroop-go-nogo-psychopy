import html
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PSYEXP_PATH = ROOT / "stroop_go_nogo_ptbr.psyexp"
DARK_BACKGROUND_RGB = "[-0.914, -0.875, -0.749]"


def parse_psyexp():
    return ET.parse(PSYEXP_PATH).getroot()


def param(component, name):
    for item in component.findall("Param"):
        if item.get("name") == name:
            return item.get("val")
    raise AssertionError(f"Param not found: {name}")


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


class InterfacePrePraticaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = parse_psyexp()

    def test_flow_pre_pratica_na_ordem_esperada(self):
        flow_names = [item.get("name") for item in self.root.find("Flow")]
        self.assertEqual(
            flow_names[:8],
            [
                "boas_vindas",
                "tutorial_regra",
                "pratica_inicio",
                "regra_rapida",
                "contagem_pratica_loop",
                "contagem",
                "contagem_pratica_loop",
                "pratica_loop",
            ],
        )
        self.assertEqual(flow_names[8], "trial_pratica")

    def test_telas_antigas_de_instrucao_nao_estao_no_flow(self):
        flow_names = [item.get("name") for item in self.root.find("Flow")]
        for old_name in ["instr_regra", "instr_congruente", "instr_incongruente"]:
            self.assertNotIn(old_name, flow_names)

    def test_formulario_permanece_na_primeira_rotina(self):
        first_routine = self.root.find("Flow")[0].get("name")
        self.assertEqual(first_routine, "boas_vindas")
        form = component(routine(self.root, "boas_vindas"), "CodeComponent", "formulario_sessao")
        begin_experiment = param(form, "Begin Experiment")
        self.assertIn("Dados da sessão", begin_experiment)
        self.assertIn("expInfo['assessment_id']", begin_experiment)
        self.assertIn("TEST_VERSION = '0.2.0'", begin_experiment)

    def test_csv_oficial_usa_participant_id_no_nome(self):
        form = component(routine(self.root, "boas_vindas"), "CodeComponent", "formulario_sessao")
        begin_experiment = param(form, "Begin Experiment")
        self.assertIn("_official_participant_id = expInfo['participant_id']", begin_experiment)
        self.assertIn("official_csv_path = os.path.join('data', f'{_official_participant_id}.csv')", begin_experiment)
        self.assertNotIn("_official_assessment_id = expInfo['assessment_id']", begin_experiment)

    def test_telas_navegaveis_aceitam_clique_espaco_e_enter(self):
        specs = [
            ("boas_vindas", "tecla_abertura", "clique_abertura", "abertura_botao"),
            ("tutorial_regra", "tecla_tutorial_regra", "clique_tutorial_regra", "tutorial_botao"),
            ("pratica_inicio", "tecla_pratica_inicio", "clique_pratica_inicio", "pratica_inicio_botao"),
        ]
        for routine_name, key_name, code_name, button_name in specs:
            current = routine(self.root, routine_name)
            keyboard = component(current, "KeyboardComponent", key_name)
            self.assertIn("space", param(keyboard, "allowedKeys"))
            self.assertIn("return", param(keyboard, "allowedKeys"))
            self.assertEqual(param(keyboard, "forceEndRoutine"), "True")
            self.assertEqual(param(keyboard, "storeCorrect"), "False")

            code = component(current, "CodeComponent", code_name)
            self.assertIn("event.Mouse", param(code, "Begin Routine"))
            self.assertIn(f"{button_name}.contains(nav_mouse)", param(code, "Each Frame"))
            self.assertIn("continueRoutine = False", param(code, "Each Frame"))

    def test_regra_rapida_e_automatica_e_tem_15_segundo(self):
        current = routine(self.root, "regra_rapida")
        self.assertEqual(len(current.findall("KeyboardComponent")), 0)
        self.assertEqual(len(current.findall("CodeComponent")), 0)
        for name in ["regra_rapida_texto", "regra_rapida_secundario"]:
            item = component(current, "TextComponent", name)
            self.assertEqual(param(item, "stopVal"), "1.5")

    def test_textos_principais_estao_presentes(self):
        text = PSYEXP_PATH.read_text(encoding="utf-8-sig")
        for expected in [
            "Tarefa de Correspondência de Cores",
            "Iniciar tutorial",
            "Como responder",
            "RESPONDA",
            "NÃO RESPONDA",
            "Prática",
            "Começar prática",
            "PRESSIONE ESPAÇO APENAS QUANDO A PALAVRA E A COR COMBINAREM.",
        ]:
            self.assertIn(expected, html.unescape(text))

    def test_tema_escuro_e_cartao_claro_nas_tentativas(self):
        for routine_name in [
            "boas_vindas",
            "tutorial_regra",
            "pratica_inicio",
            "regra_rapida",
            "trial_pratica",
            "trial_principal",
        ]:
            settings = component(routine(self.root, routine_name), "RoutineSettingsComponent", routine_name)
            self.assertEqual(param(settings, "color"), DARK_BACKGROUND_RGB)
            self.assertFalse(param(settings, "color").startswith("#"))

        for routine_name, card_name in [
            ("trial_pratica", "stim_card_pratica"),
            ("trial_principal", "stim_card_principal"),
        ]:
            card = component(routine(self.root, routine_name), "TextComponent", card_name)
            self.assertEqual(param(card, "color"), "white")

    def test_hexadecimal_nao_e_usado_como_codigo_de_cor(self):
        for text_component in self.root.findall(".//TextComponent"):
            for item in text_component.findall("Param"):
                if item.get("name") == "color" and (item.get("val") or "").startswith("#"):
                    self.assertNotEqual(
                        item.get("valType"),
                        "code",
                        f"{text_component.get('name')} usa hexadecimal como codigo",
                    )


if __name__ == "__main__":
    unittest.main()
