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

    def test_sandbox_write_requires_explicit_mode_and_allowlist(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        with mock.patch.dict(os.environ,{"PCFLOWS_MAKE_API_TOKEN":"secret-token"},clear=True):
            with self.assertRaises(make_runtime_client.MakeRuntimeError):
                client.update_sandbox_blueprint(111,{"flow":[]})

    def test_sandbox_update_fetches_backup_before_patch(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        calls=[]
        def fake_open(req,timeout):
            calls.append((req.method,req.full_url,req.data.decode("utf-8") if req.data else None))
            if req.method=="GET":
                return FakeResponse(b'{"blueprint":{"flow":[{"id":1,"module":"json:ParseJSON"}]}}')
            return FakeResponse(b'{"scenario":{"id":111}}')
        env={
            "PCFLOWS_MAKE_API_TOKEN":"secret-token",
            "PCFLOWS_MAKE_WRITE_MODE":"sandbox",
            "PCFLOWS_MAKE_ALLOWED_SCENARIO_IDS":"111",
        }
        with mock.patch.dict(os.environ,env,clear=True):
            with mock.patch("urllib.request.urlopen",fake_open):
                result=client.update_sandbox_blueprint(111,{"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]})
        self.assertEqual(calls[0][0],"GET")
        self.assertTrue(calls[0][1].endswith("/scenarios/111/blueprint"))
        self.assertEqual(calls[1][0],"PATCH")
        self.assertTrue(result["original_sha256"])

    def test_rollback_uses_allowlisted_original_blueprint(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        calls=[]
        def fake_open(req,timeout):
            calls.append(req)
            return FakeResponse(b'{"scenario":{"id":111}}')
        env={
            "PCFLOWS_MAKE_API_TOKEN":"secret-token",
            "PCFLOWS_MAKE_WRITE_MODE":"sandbox",
            "PCFLOWS_MAKE_ALLOWED_SCENARIO_IDS":"111",
        }
        with mock.patch.dict(os.environ,env,clear=True):
            with mock.patch("urllib.request.urlopen",fake_open):
                client.rollback_sandbox_blueprint(111,{"flow":[]})
        self.assertEqual(calls[0].method,"PATCH")


    def test_production_write_requires_explicit_customer_authorization(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        env={
            "PCFLOWS_MAKE_API_TOKEN":"secret-token",
            "PCFLOWS_MAKE_PRODUCTION_WRITE_ENABLED":"true",
            "PCFLOWS_MAKE_PRODUCTION_SCENARIO_IDS":"222",
        }
        with mock.patch.dict(os.environ,env,clear=True):
            with self.assertRaises(make_runtime_client.MakeRuntimeError):
                client.update_production_blueprint(222,{"flow":[]})

    def test_production_update_backs_up_only_allowlisted_authorized_scenario(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        calls=[]
        def fake_open(req,timeout):
            calls.append((req.method,req.full_url))
            if req.method=="GET":
                return FakeResponse(b'{"blueprint":{"flow":[{"id":1,"module":"json:ParseJSON"}]}}')
            return FakeResponse(b'{"scenario":{"id":222}}')
        env={
            "PCFLOWS_MAKE_API_TOKEN":"secret-token",
            "PCFLOWS_MAKE_PRODUCTION_WRITE_ENABLED":"true",
            "PCFLOWS_MAKE_PRODUCTION_SCENARIO_IDS":"222",
            "PCFLOWS_REPAIR_CASE_ID":"repair_case_001",
            "PCFLOWS_CUSTOMER_AUTHORIZATION_ID":"customer_auth_001",
        }
        with mock.patch.dict(os.environ,env,clear=True):
            with mock.patch("urllib.request.urlopen",fake_open):
                result=client.update_production_blueprint(
                    222,
                    {"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]},
                )
        self.assertEqual(calls[0][0],"GET")
        self.assertEqual(calls[1][0],"PATCH")
        self.assertEqual(result["repair_case_id"],"repair_case_001")
        self.assertEqual(result["customer_authorization_id"],"customer_auth_001")
        self.assertTrue(result["original_sha256"])

    def test_production_write_rejects_non_allowlisted_scenario(self):
        cfg=make_runtime_client.MakeRuntimeConfig("https://eu1.make.com")
        client=make_runtime_client.MakeRuntimeClient(cfg)
        env={
            "PCFLOWS_MAKE_API_TOKEN":"secret-token",
            "PCFLOWS_MAKE_PRODUCTION_WRITE_ENABLED":"true",
            "PCFLOWS_MAKE_PRODUCTION_SCENARIO_IDS":"333",
            "PCFLOWS_REPAIR_CASE_ID":"repair_case_001",
            "PCFLOWS_CUSTOMER_AUTHORIZATION_ID":"customer_auth_001",
        }
        with mock.patch.dict(os.environ,env,clear=True):
            with self.assertRaises(make_runtime_client.MakeRuntimeError):
                client.update_production_blueprint(222,{"flow":[]})



if __name__=="__main__":
    unittest.main()
