import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from retrieval_window import explicit_window, parse_timestamp, window_presentation
import main as pipeline


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


planner = load_file('daily_window_planner', ROOT / 'scripts/daily_retrieval_window.py')
fetcher = load_file('fixed_window_fetcher', ROOT / 'src/maintain/fetchers/fetch_arxiv.py')
WINDOW_ENV = {'DPR_FETCH_START': '2026-11-11T22:00:00Z', 'DPR_FETCH_END': '2026-11-12T22:00:00Z'}


class DailyWindowTest(unittest.TestCase):
    def test_first_backfill_and_next_daily_window_join_exactly(self):
        start, end = planner.plan_window(parse_timestamp('2026-11-12T15:30:00Z'), 30)
        self.assertEqual(end, parse_timestamp('2026-11-11T22:00:00Z'))
        self.assertEqual(end - start, timedelta(days=30))
        next_start, next_end = planner.plan_window(parse_timestamp('2026-11-12T22:17:00Z'), 1, end.isoformat(), True)
        self.assertEqual(next_start, end)
        self.assertEqual(next_end, parse_timestamp('2026-11-12T22:00:00Z'))

    def test_failed_or_missed_day_is_caught_up(self):
        start, end = planner.plan_window(parse_timestamp('2026-11-14T23:00:00Z'), 1, '2026-11-11T22:00:00Z', True)
        self.assertEqual(end - start, timedelta(days=3))

    def test_before_six_uses_previous_cutoff(self):
        _, end = planner.plan_window(parse_timestamp('2026-11-12T21:59:59Z'), 1)
        self.assertEqual(end, parse_timestamp('2026-11-11T22:00:00Z'))

    def test_timezone_and_paired_boundary_validation(self):
        for env in ({'DPR_FETCH_START': '2026-11-11T22:00:00Z'}, {'DPR_FETCH_START': '2026-11-11', 'DPR_FETCH_END': '2026-11-12T22:00:00Z'}, {'DPR_FETCH_START': '2026-11-12T22:00:00Z', 'DPR_FETCH_END': '2026-11-11T22:00:00Z'}):
            with self.subTest(env=env), patch.dict(os.environ, env, clear=True), self.assertRaises(ValueError):
                explicit_window()

    def test_date_and_label_use_cutoff_in_local_timezone(self):
        with patch.dict(os.environ, WINDOW_ENV, clear=True):
            self.assertEqual(pipeline.resolve_run_date_token(1), '20261113')
            self.assertEqual(pipeline.resolve_sidebar_date_label(1), '2026-11-12 06:00 ~ 2026-11-13 06:00 (UTC+8)')

    def test_checkpoint_only_written_after_explicit_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state.json'
            with patch.dict(os.environ, WINDOW_ENV, clear=True):
                planner.write_checkpoint(state)
                self.assertFalse(state.exists())
                os.environ['DPR_CHECKPOINT_ENABLED'] = 'true'
                planner.write_checkpoint(state)
                self.assertEqual(json.loads(state.read_text())['completed_through'], '2026-11-12T22:00:00+00:00')
                os.environ['DPR_FETCH_START'] = '2026-11-09T22:00:00Z'
                os.environ['DPR_FETCH_END'] = '2026-11-10T22:00:00Z'
                planner.write_checkpoint(state)
                self.assertEqual(json.loads(state.read_text())['completed_through'], '2026-11-12T22:00:00+00:00')

    def test_prepare_exports_real_action_inputs(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'schedule', 'GITHUB_ENV': tmp + '/env', 'GITHUB_OUTPUT': tmp + '/out'}, clear=True), patch.object(planner, 'read_checkpoint', return_value={'completed_through': '2026-11-11T22:00:00Z'}):
            planner.prepare(parse_timestamp('2026-11-12T22:20:00Z'))
            exported = Path(tmp + '/env').read_text()
            self.assertIn('DPR_FETCH_START=2026-11-11T22:00:00+00:00', exported)
            self.assertIn('DPR_FETCH_END=2026-11-12T22:00:00+00:00', exported)
            self.assertIn('days=1', Path(tmp + '/out').read_text())
            self.assertIn('DPR_CHECKPOINT_ENABLED=true', exported)

    def test_prepare_preserves_manual_ten_day_and_publish_only_modes(self):
        for days, publish in (('10', 'false'), ('30', 'true')):
            with self.subTest(days=days, publish=publish), tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'REQUESTED_DAYS': days, 'PUBLISH_ONLY': publish, 'GITHUB_ENV': tmp + '/env', 'GITHUB_OUTPUT': tmp + '/out'}, clear=True):
                planner.prepare(parse_timestamp('2026-11-12T22:20:00Z'))
                self.assertNotIn('DPR_FETCH_START', Path(tmp + '/env').read_text())

    def test_selected_profile_cannot_advance_global_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'REQUESTED_DAYS': '30', 'REQUESTED_PROFILE': 'one-profile', 'GITHUB_ENV': tmp + '/env', 'GITHUB_OUTPUT': tmp + '/out'}, clear=True):
            planner.prepare(parse_timestamp('2026-11-12T15:30:00Z'))
            self.assertIn('DPR_CHECKPOINT_ENABLED=false', Path(tmp + '/env').read_text())

    def test_already_covered_window_skips_retrieval(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'schedule', 'GITHUB_ENV': tmp + '/env', 'GITHUB_OUTPUT': tmp + '/out'}, clear=True), patch.object(planner, 'read_checkpoint', return_value={'completed_through': '2026-11-12T22:00:00Z'}):
            planner.prepare(parse_timestamp('2026-11-12T22:20:00Z'))
            self.assertIn('skip_retrieval=true', Path(tmp + '/out').read_text())


class FixedFetcherTest(unittest.TestCase):
    def paper(self, pid, published):
        return SimpleNamespace(published=parse_timestamp(published), get_short_id=lambda: pid, pdf_url='https://arxiv.org/pdf/' + pid, entry_id=pid, title='Title', summary='Abstract', authors=[], primary_category='cs.AI', categories=['cs.AI'])

    def test_includes_start_and_excludes_end_even_for_inclusive_api(self):
        papers = [self.paper('before', '2026-11-11T21:59:59Z'), self.paper('start', '2026-11-11T22:00:00Z'), self.paper('last', '2026-11-12T21:59:59Z'), self.paper('end', '2026-11-12T22:00:00Z')]
        client = SimpleNamespace(results=lambda search: iter(papers))
        found = {}
        with patch.dict(os.environ, WINDOW_ENV, clear=True):
            fetcher.fetch_category_in_windows(client, 'cs', [explicit_window()], set(), found)
        self.assertEqual(set(found), {'start', 'last'})

    def test_partial_api_failure_aborts_instead_of_checkpointing(self):
        def fail(search):
            yield self.paper('partial', '2026-11-12T01:00:00Z')
            raise OSError('API unavailable')
        with patch.dict(os.environ, WINDOW_ENV, clear=True), self.assertRaises(RuntimeError):
            fetcher.fetch_category_in_windows(SimpleNamespace(results=fail), 'cs', [explicit_window()], set(), {})

    def test_old_seen_state_cannot_shorten_fixed_window(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, WINDOW_ENV, clear=True), patch.object(fetcher, 'load_config', return_value={}), patch.object(fetcher, 'get_supabase_read_config', return_value={'enabled': False}), patch.object(fetcher, 'CATEGORIES_TO_FETCH', ['cs']), patch.object(fetcher, 'fetch_category_in_windows', return_value=None) as fetch, patch.object(fetcher, 'load_seen_state', side_effect=AssertionError('must not use old state')), patch.object(fetcher, 'save_seen_state'), patch.object(fetcher, 'save_last_crawl_at'):
            fetcher.fetch_all_domains_metadata_robust(days=1, output_file=tmp + '/raw.json')
            self.assertEqual(fetch.call_args.kwargs['windows'][0][0], parse_timestamp(WINDOW_ENV['DPR_FETCH_START']))
            self.assertEqual(json.loads(Path(tmp + '/raw.json').read_text()), [])


if __name__ == '__main__':
    unittest.main()
