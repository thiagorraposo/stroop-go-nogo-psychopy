"""Contrato estrito da borda analítica, sem fontes operacionais."""
import unittest
from uuid import uuid4

from pydantic import ValidationError

from api.analysis import AnalysisRequest, QuerySelection, normalize
from api.errors import APIError


class AnalysisSchemaTests(unittest.TestCase):
    def test_aliases_equivalentes_e_limites_sem_coercao(self):
        project = str(uuid4())
        first, filters = normalize(QuerySelection.model_validate({'projects': [project], 'filters': {
            'start_date': '2026-11-11', 'participant_id': ['B', 'A', 'A'], 'platform': ['psychopy']}}))
        second, _ = normalize(QuerySelection.model_validate({'projects': [project], 'filters': {
            'date_from': '2026-11-11', 'participant_code': ['A', 'B'], 'platform': ['psychopy_local']}}))
        self.assertEqual(first, second)
        self.assertEqual(filters, {'start_date': '2026-11-11', 'participant_id': ['A', 'B'], 'platform': ['psychopy']})
        for query in ({'projects': [project, project], 'filters': {}},
                      {'projects': [project], 'filters': {'date_from': ''}},
                      {'projects': [project], 'filters': {'date_from': '2026-02-30'}},
                      {'projects': [project], 'filters': {'participant_id': ['A'], 'participant_code': ['B']}}):
            with self.subTest(query=query), self.assertRaises(APIError):
                normalize(QuerySelection.model_validate(query))
        base = {'query': {'projects': [project], 'filters': {}},
                'grouping': {'level': 'assessment', 'dimension': 'project'}, 'page': {}}
        for page in ({'size': True}, {'size': '10'}, {'size': 101}, {'size': 0}, {'cursor': ''}, {'sort': 'unknown'}):
            with self.subTest(page=page), self.assertRaises(ValidationError):
                AnalysisRequest.model_validate({**base, 'page': page})
        for filters in ({'patient_id': 'SYNTHETIC'}, {'accuracy_min': True}, {'status': 'invalidated'},
                        {'include_null_rt': 'false'}, {'platform': ['legacy']}, {'visit': ['A'] * 101}):
            with self.subTest(filters=filters), self.assertRaises(ValidationError):
                AnalysisRequest.model_validate({**base, 'query': {'projects': [project], 'filters': filters}})
        for grouping in ({'level': 'trial', 'dimension': 'condition'},
                         {'level': 'assessment', 'dimension': 'project', 'metric_code': 'accuracy'}):
            with self.subTest(grouping=grouping), self.assertRaises(ValidationError):
                AnalysisRequest.model_validate({**base, 'grouping': grouping})

    def test_metricas_exigem_capacidade_faixas_finitas_e_busca_apenas_codigo(self):
        project = str(uuid4())
        for filters in ({'accuracy_min': 50}, {'include_null_rt': False},
                        {'test_code': ['stroop_go_nogo_ptbr'], 'accuracy_min': 80, 'accuracy_max': 50},
                        {'patient_search': 'CODIGO\x00'}):
            with self.subTest(filters=filters), self.assertRaises(APIError):
                normalize(QuerySelection.model_validate({'projects': [project], 'filters': filters}))
        query, filters = normalize(QuerySelection.model_validate({'projects': [project], 'filters': {
            'test_code': ['stroop_go_nogo_ptbr'], 'patient_search': '  SYNTH  ', 'accuracy_min': 50,
            'rt_median_max_ms': 1000, 'include_null_rt': False}}))
        self.assertEqual(query['filters']['patient_search'], 'synth')
        self.assertEqual(filters['patient_search'], 'synth')
        for value in (float('nan'), float('inf'), '50', True):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                QuerySelection.model_validate({'projects': [project], 'filters': {'accuracy_min': value}})
