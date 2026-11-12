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
        for filters in ({'patient_search': 'SYNTHETIC'}, {'accuracy_min': 50}, {'status': 'invalidated'},
                        {'include_null_rt': False}, {'platform': ['legacy']}, {'visit': ['A'] * 101}):
            with self.subTest(filters=filters), self.assertRaises(ValidationError):
                AnalysisRequest.model_validate({**base, 'query': {'projects': [project], 'filters': filters}})
        for grouping in ({'level': 'trial', 'dimension': 'condition'},
                         {'level': 'assessment', 'dimension': 'project', 'metric_code': 'accuracy'}):
            with self.subTest(grouping=grouping), self.assertRaises(ValidationError):
                AnalysisRequest.model_validate({**base, 'grouping': grouping})
