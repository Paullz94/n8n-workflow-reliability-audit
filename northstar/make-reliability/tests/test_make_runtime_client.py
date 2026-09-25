import os
import unittest
from unittest import mock

import make_runtime_client


class FakeResponse:
    def __init__(self,payload):
        self.payload=payload
    def __enter__(self):
        return self
    def __exit__(self,*args):
        return False
    def read(self):
        return self.payload


class MakeRuntimeClientTests(unittest.TestCase):
    def test_rejects_unknown_zone(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://evil.example")
        with self.assertRaises(make_runtime_client.MakeRuntimeError):
            cfg.base_url()

    def test_token_only_from_environment(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        with mock.patch.dict(os.environ,{},clear=True):
            with self.assertRaises(make_runtime_client.MakeRuntimeError):
                cfg.token()

    def test_run_scenario_uses_responsive_api_without_exposing_token(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        captured={}
        def fake_open(req,timeout):
            captured["url"]=req.full_url
            captured["auth"]=req.headers.get("Authorization")
            captured["body"]=req.data.decode("utf-8")
            return FakeResponse(b'{"executionId":"exec_123","status":"1"}')
        with mock.patch.dict(os.environ,{"PCFLOWS_MAKE_API_TOKEN":"secret-token"},clear=True):
            with mock.patch("urllib.request.urlopen",fake_open):
                result=client.run_scenario(111,data={"case":"synthetic"},responsive=True)
        self.assertEqual(result["executionId"],"exec_123")
        self.assertEqual(captured["url"],"https://eu1.make.com/api/v2/scenarios/111/run")
        self.assertIn('"responsive": true',captured["body"])
        self.assertNotIn("secret-token",str(result))

    def test_replay_uses_execution_id_array(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        captured={}
        def fake_open(req,timeout):
            captured["body"]=req.data.decode("utf-8")
            return FakeResponse(b'')
        with mock.patch.dict(os.environ,{"PCFLOWS_MAKE_API_TOKEN":"secret-token"},clear=True):
            with mock.patch("urllib.request.urlopen",fake_open):
                client.replay_execution(111,"exec_123")
        self.assertIn('"executionIds": ["exec_123"]',captured["body"])


if __name__=="__main__":
    unittest.main()
