import unittest
import mock
import plantpredict


# this patch is applied to all methods
@mock.patch('plantpredict.utilities.convert_json', autospec=True)
class TestPlantPredictEntity(unittest.TestCase):

    def _make_mock_api(self):
        # I don't understand why `mock_convert_json` does not need to be an argument
        mock_api = mock.Mock()
        mock_api.base_url = "https://api.plantpredict.com/"
        mock_api.access_token = 'dummy_token'
        return mock_api
        
    @mock.patch('plantpredict.plant_predict_entity.requests.post', autospec=True)
    def test_create(self, mock_post, mock_convert_json):
        mock_api = self._make_mock_api()
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = '''{"id":"dummy_id"}'''
        ppe = plantpredict.plant_predict_entity.PlantPredictEntity(mock_api)
        ppe.create_url_suffix = 'dummy_url_suffix'
        response = ppe.create()
        mock_post.assert_called()

    @mock.patch('plantpredict.plant_predict_entity.requests.delete', autospec=True)
    def test_delete(self, mock_delete, mock_convert_json):
        mock_api = self._make_mock_api()
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.content = '''{"id":"dummy_id"}'''
        ppe = plantpredict.plant_predict_entity.PlantPredictEntity(mock_api)
        ppe.delete_url_suffix = 'dummy_url_suffix'
        response = ppe.delete()
        mock_delete.assert_called()

    @mock.patch('plantpredict.plant_predict_entity.requests.get', autospec=True)
    def test_get(self, mock_get, mock_convert_json):
        mock_api = self._make_mock_api()
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = '''{"id":"dummy_id"}'''
        ppe = plantpredict.plant_predict_entity.PlantPredictEntity(mock_api)
        ppe.get_url_suffix = 'dummy_url_suffix'
        response = ppe.get()
        mock_get.assert_called()
        self.assertTrue(ppe.id=='dummy_id')

    @mock.patch('plantpredict.plant_predict_entity.requests.put', autospec=True)
    def test_update(self, mock_put, mock_convert_json):
        mock_api = self._make_mock_api()
        mock_put.return_value.status_code = 200
        mock_put.return_value.content = '''{"id":"dummy_id"}'''
        ppe = plantpredict.plant_predict_entity.PlantPredictEntity(mock_api)
        ppe.update_url_suffix = 'dummy_url_suffix'
        response = ppe.update()
        mock_put.assert_called()


if __name__ == '__main__':
    unittest.main()
    
    