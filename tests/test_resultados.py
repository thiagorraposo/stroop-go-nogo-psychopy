import html
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PSYEXP_PATH = ROOT / "stroop_go_nogo_ptbr.psyexp"
DARK_BACKGROUND_RGB = "[-0.914, -0.875, -0.749]"


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


class ResultadosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = parse_psyexp()
        cls.resultados = routine(cls.root, "resultados")
        cls.code = component(cls.resultados, "CodeComponent", "codigo_resultados")

    def test_resultados_fica_apos_loop_principal_e_encerra_o_flow(self):
        flow_names = [item.get("name") for item in self.root.find("Flow")]
        self.assertEqual(
            flow_names[-4:],
            ["principal_loop", "trial_principal", "principal_loop", "resultados"],
        )

    def test_resultados_usa_tema_escuro_e_componentes_em_height(self):
        settings = component(self.resultados, "RoutineSettingsComponent", "resultados")
        self.assertEqual(param(settings, "color"), DARK_BACKGROUND_RGB)
        begin_routine = param(self.code, "Begin Routine")
        self.assertIn("units='height'", begin_routine)
        self.assertIn("resultados_painel = visual.Rect", begin_routine)
        self.assertIn("resultados_circulo_fundo = visual.Circle", begin_routine)
        self.assertIn("resultados_circulo_destaque = visual.Circle", begin_routine)

    def test_textos_obrigatorios_estao_na_tela(self):
        begin_routine = param(self.code, "Begin Routine")
        for expected in [
            "Resumo da execução",
            "Dados descritivos desta execução da tarefa.",
            "Tempo de reação",
            "Hits:",
            "Omissões:",
            "Rejeições corretas:",
            "Comissões:",
            "Este resumo descreve apenas esta execução e não representa diagnóstico ou avaliação clínica.",
            "Finalizar",
        ]:
            self.assertIn(expected, begin_routine)

    def test_metricas_usam_registro_canonico_main_em_memoria(self):
        begin_routine = param(self.code, "Begin Routine")
        self.assertIn("main_result_rows = [row for row in official_trial_rows if row['block'] == 'main']", begin_routine)
        self.assertIn("hits = sum(1 for row in main_result_rows if row['error_type'] == 'hit')", begin_routine)
        self.assertIn("omissions = sum(1 for row in main_result_rows if row['error_type'] == 'omission')", begin_routine)
        self.assertIn("correct_rejections = sum(1 for row in main_result_rows if row['error_type'] == 'correct_rejection')", begin_routine)
        self.assertIn("commissions = sum(1 for row in main_result_rows if row['error_type'] == 'commission')", begin_routine)
        self.assertIn("((hits + correct_rejections) / total_main_trials) * 100", begin_routine)
        self.assertIn("round(", begin_routine)
        self.assertIn("if row['error_type'] == 'hit' and row['reaction_time']", begin_routine)
        self.assertIn("resultados_rt_mediana = f'{median_reaction_time:.3f} s'", begin_routine)
        self.assertIn("resultados_rt_mediana = '—'", begin_routine)
        self.assertNotIn("open(", begin_routine)
        self.assertNotIn("csv.", begin_routine)
        self.assertNotIn("read_csv", begin_routine)

    def test_resultados_grava_csv_sem_adicionar_linhas(self):
        all_code = "\n".join(
            param(self.code, name)
            for name in [
                "Begin Experiment",
                "Begin Routine",
                "Each Frame",
                "End Routine",
                "End Experiment",
            ]
        )
        self.assertNotIn("official_trial_rows.append", all_code)
        self.assertNotIn("thisExp.addData", all_code)
        self.assertEqual(param(self.code, "End Routine"), "write_official_csv()")

    def test_resultados_aceita_clique_espaco_e_enter(self):
        keyboard = component(self.resultados, "KeyboardComponent", "tecla_resultados")
        self.assertIn("space", param(keyboard, "allowedKeys"))
        self.assertIn("return", param(keyboard, "allowedKeys"))
        self.assertEqual(param(keyboard, "forceEndRoutine"), "True")
        self.assertEqual(param(keyboard, "discard previous"), "True")

        begin_routine = param(self.code, "Begin Routine")
        each_frame = param(self.code, "Each Frame")
        self.assertIn("resultados_mouse = event.Mouse(win=win)", begin_routine)
        self.assertIn("resultados_botao_area.contains(resultados_mouse)", each_frame)
        self.assertIn("continueRoutine = False", each_frame)

    def test_code_components_tem_sintaxe_python_valida(self):
        for code_component in self.root.findall(".//CodeComponent"):
            for field in [
                "Before Experiment",
                "Begin Experiment",
                "Begin Routine",
                "Each Frame",
                "End Routine",
                "End Experiment",
            ]:
                code = html.unescape(param(code_component, field))
                if code.strip():
                    compile(code, f"{code_component.get('name')}:{field}", "exec")

    def test_resultados_nao_importa_modulos_psychopy_dentro_do_run(self):
        for field in ["Begin Experiment", "Begin Routine", "Each Frame", "End Routine"]:
            code = html.unescape(param(self.code, field))
            self.assertNotIn("from psychopy import event", code)
            self.assertNotIn("from psychopy import visual", code)


if __name__ == "__main__":
    unittest.main()
