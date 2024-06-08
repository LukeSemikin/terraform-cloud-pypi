from src.tfcloud_sdk.workspaces import Workspaces
from os import environ
from unittest import main, TestCase, skip
from json import loads


class TestWorkspaces(TestCase):

    runner = Workspaces("luke_semikin", environ['tf_access_token'])
    test_workspace_name = "dummy_workspace"
    test_tags = ["test_tag"]
    test_ssh_key = "dummy_key"

    def setUp(self):
        self.runner.create_workspace(f"{self.test_workspace_name}-safe-delete")
        self.runner.create_workspace(f"{self.test_workspace_name}-force-delete")
        self.workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        self.rsc_workspace_id = loads(self.runner.show_workspace(f"{self.test_workspace_name}-rsc").content)['data']['id']

    def test_create_workspace(self):
        self.runner.create_workspace(self.test_workspace_name)
        response = self.runner.show_workspace(self.test_workspace_name)
        self.assertEqual(200, response.status_code)

    def test_list_workspaces_response(self):
        response, workspaces = self.runner.list_workspaces()
        self.assertEqual(200, response)

    def test_list_workspace_name(self):
        response, workspaces = self.runner.list_workspaces()
        for workspace in workspaces:
            if workspace['attributes']['name'] == self.test_workspace_name:
                break
        self.assertEqual(workspace['attributes']['name'],self.test_workspace_name)

    def test_show_workspace_response(self):
        self.assertEqual(200, self.runner.show_workspace(self.test_workspace_name).status_code)

    def test_show_workspace_name(self):
        self.assertEqual(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['name'],self.test_workspace_name)

    def test_lock_workspace(self):
        self.runner.lock_workspace(self.workspace_id, "Test Lock")
        self.assertTrue(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['locked'])

    def test_unlock_workspace(self):
        self.runner.unlock_workspace(self.workspace_id)
        self.assertFalse(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['locked'])

    def test_get_remote_state_consumers(self):
        self.assertEqual(self.runner.get_remote_state_consumers(self.workspace_id).status_code, 200)

    def test_add_remote_state_consumers(self):
        self.runner.create_workspace(f"{self.test_workspace_name}-rsc")
        self.assertEqual(204, self.runner.add_remote_state_consumers(self.workspace_id, self.rsc_workspace_id).status_code)

    def test_force_unlock_workspace(self):
        self.runner.lock_workspace(self.workspace_id, "Test Lock")
        self.runner.force_unlock_workspace(self.workspace_id)
        self.assertFalse(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['locked'])

    def test_add_tags(self):
        self.assertEqual(self.runner.add_tags(self.workspace_id, self.test_tags).status_code, 204)

    def test_get_workspace_tags(self):
        self.assertEqual(self.runner.get_workspace_tags(self.workspace_id).status_code, 200)

    def test_safe_delete_workspace(self):
        self.assertEqual(self.runner.safe_delete_workspace(workspace_name=f"{self.test_workspace_name}-safe-delete").status_code, 204)

    def test_force_delete_workspace(self):
        self.assertEqual(self.runner.force_delete_workspace(workspace_name=f"{self.test_workspace_name}-force-delete").status_code, 204)

    def test_update_remote_state_consumers(self):
        self.assertEqual(self.runner.update_remote_state_consumers(self.workspace_id, self.rsc_workspace_id).status_code, 204)

    def test_delete_remote_state_consumers(self):
        self.assertEqual(self.runner.delete_remote_state_consumers(self.workspace_id, self.rsc_workspace_id).status_code, 204)

    def test_delete_workspace_tags(self):
        self.assertEqual(self.runner.delete_workspace_tags(self.workspace_id, self.test_tags).status_code, 204)

    @skip("Requires SSH Key Library")
    def test_assign_ssh_key(self):
        self.assertEqual(self.runner.assign_ssh_key(self.workspace_id, self.test_ssh_key).content, 204)

    @skip("Requires SSH Key Library")
    def test_unassign_ssh_key(self):
        self.assertEqual(self.runner.unassign_ssh_key(self.workspace_id).status_code, 204)

if __name__ == '__main__':
    testsuite = main()
