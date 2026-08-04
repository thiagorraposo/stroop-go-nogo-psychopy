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
            flow_names[:9],
            [
                "formulario_sessao",
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
        self.assertEqual(flow_names[9], "trial_pratica")

    def test_telas_antigas_de_instrucao_nao_estao_no_flow(self):
        flow_names = [item.get("name") for item in self.root.find("Flow")]
        for old_name in ["instr_regra", "instr_congruente", "instr_incongruente"]:
            self.assertNotIn(old_name, flow_names)

    def test_formulario_visual_e_a_primeira_rotina(self):
        first_routine = self.root.find("Flow")[0].get("name")
        self.assertEqual(first_routine, "formulario_sessao")
        form_routine = routine(self.root, "formulario_sessao")
        keeper = component(form_routine, "TextComponent", "formulario_manter_ativo")
        self.assertEqual(param(keeper, "units"), "height")
        self.assertEqual(param(keeper, "opacity"), "0")
        self.assertEqual(param(keeper, "stopVal"), "")
        form = component(form_routine, "CodeComponent", "controle_formulario_sessao")
        begin_routine = html.unescape(param(form, "Begin Routine"))
        each_frame = html.unescape(param(form, "Each Frame"))
        self.assertIn("visual.TextBox2", begin_routine)
        self.assertIn("editable=True", begin_routine)
        self.assertIn("win.mouseVisible = True", begin_routine)
        self.assertIn("global official_csv_path", begin_routine)
        self.assertIn("Iniciar tarefa", begin_routine)
        for label in [
            "Projeto",
            "ID do participante",
            "Nome do participante",
            "Iniciais",
            "Visita",
            "Avaliador(a)",
        ]:
            self.assertIn(label, begin_routine)
        self.assertIn("expInfo['assessment_id']", each_frame)
        self.assertIn("expInfo['assessment_date']", each_frame)
        self.assertIn("expInfo['started_at']", each_frame)
        self.assertIn("expInfo['test_code']", each_frame)
        self.assertIn("expInfo['test_version']", each_frame)

    def test_formulario_nao_usa_dialogo_ou_janela_externa(self):
        source = PSYEXP_PATH.read_text(encoding="utf-8-sig")
        for forbidden in ["gui.Dlg", "tkinter", "session_dlg", "addField("]:
            self.assertNotIn(forbidden, source)

    def test_formulario_usa_layout_responsivo_em_height(self):
        form = component(
            routine(self.root, "formulario_sessao"),
            "CodeComponent",
            "controle_formulario_sessao",
        )
        begin_routine = html.unescape(param(form, "Begin Routine"))
        self.assertIn("win.units = 'height'", begin_routine)
        self.assertIn("units='height'", begin_routine)
        self.assertIn("size=(1.18, 0.94)", begin_routine)
        self.assertIn("pos=(0, 0)", begin_routine)
        self.assertNotIn("pix", begin_routine.lower())
        self.assertNotIn("win.size", begin_routine)

    def test_validacoes_do_formulario_e_trim(self):
        form = component(
            routine(self.root, "formulario_sessao"),
            "CodeComponent",
            "controle_formulario_sessao",
        )
        each_frame = html.unescape(param(form, "Each Frame"))
        self.assertIn("str(field.text or '').strip()", each_frame)
        for required in ["project", "participant_id", "participant_name", "visit", "evaluator"]:
            self.assertIn(f"not session_values['{required}']", each_frame)
        self.assertNotIn("not session_values['initials']", each_frame)
        self.assertIn("PARTICIPANT_ID_PATTERN.fullmatch", each_frame)
        self.assertIn("len(session_values['participant_name']) < 2", each_frame)
        self.assertIn("len(session_values['participant_name']) > 120", each_frame)
        self.assertIn("if validation_errors:", each_frame)
        self.assertIn("continueRoutine = False", each_frame)

    def test_csv_oficial_usa_timestamp_sem_identificadores_no_nome(self):
        form = component(
            routine(self.root, "formulario_sessao"),
            "CodeComponent",
            "controle_formulario_sessao",
        )
        each_frame = html.unescape(param(form, "Each Frame"))
        filename_code = "\n".join(
            line for line in each_frame.splitlines()
            if "official_timestamp" in line or "official_csv_path" in line
        )
        self.assertIn(
            "_started_at.strftime('%Y-%m-%d_%Hh%Mm%Ss')", filename_code
        )
        self.assertIn(
            "f'{TEST_CODE}_{official_timestamp}_trials.csv'", filename_code
        )
        for participant_field in [
            "participant_id",
            "participant_name",
            "initials",
            "visit",
            "evaluator",
            "assessment_id",
        ]:
            self.assertNotIn(participant_field, filename_code)

        initializer = component(
            routine(self.root, "boas_vindas"),
            "CodeComponent",
            "inicializacao_sessao",
        )
        begin_experiment = html.unescape(param(initializer, "Begin Experiment"))
        self.assertIn("participant_name': expInfo['participant_name']", begin_experiment)

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
            begin_routine = param(code, "Begin Routine")
            self.assertIn("win.units = 'height'", begin_routine)
            self.assertLess(
                begin_routine.index("win.units = 'height'"),
                begin_routine.index("event.Mouse"),
            )
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

    def test_tela_cheia_e_sem_tamanho_fixo_no_builder(self):
        settings = self.root.find("Settings")
        self.assertEqual(param(settings, "Full-screen window"), "True")
        form = component(
            routine(self.root, "formulario_sessao"),
            "CodeComponent",
            "controle_formulario_sessao",
        )
        form_code = html.unescape(param(form, "Begin Routine"))
        self.assertNotIn("Window size", form_code)
        self.assertNotIn("win.size", form_code)

    def test_cursor_oculto_somente_nas_tentativas_stroop(self):
        for routine_name, code_name in [
            ("trial_pratica", "codigo_pratica"),
            ("trial_principal", "codigo_principal"),
        ]:
            code = component(routine(self.root, routine_name), "CodeComponent", code_name)
            self.assertIn("win.mouseVisible = False", html.unescape(param(code, "Begin Routine")))
            self.assertIn("win.mouseVisible = True", html.unescape(param(code, "End Routine")))

        for routine_name, code_name in [
            ("boas_vindas", "clique_abertura"),
            ("tutorial_regra", "clique_tutorial_regra"),
            ("pratica_inicio", "clique_pratica_inicio"),
            ("resultados", "codigo_resultados"),
        ]:
            code = component(routine(self.root, routine_name), "CodeComponent", code_name)
            self.assertIn("win.mouseVisible = True", html.unescape(param(code, "Begin Routine")))

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

    def test_telas_principais_nao_exibem_enter(self):
        trial_main = routine(self.root, "trial_principal")
        visible_texts = [
            param(item, "text")
            for item in trial_main.findall("TextComponent")
            if param(item, "text")
        ]
        self.assertTrue(all("Enter" not in text for text in visible_texts))
        self.assertTrue(all("ENTER" not in text for text in visible_texts))
        self.assertTrue(all("Continue" not in text for text in visible_texts))

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
