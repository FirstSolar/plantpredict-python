import unittest
import mock
import plantpredict

'''
note: could not install mock through conda, used pip instead

'''

# this patch is applied to all methods
@mock.patch('plantpredict.api.requests.post', autospec=True)
class TestApi(unittest.TestCase):

    def test_init(self, mock_post):
        mock_post.return_value.ok = True
        mock_post.return_value.content = '''{"access_token":"dummy_access_token",
                                            "refresh_token":"dummy_refresh_token"}'''
        api = plantpredict.Api(username="FS123456@firstsolar.com.plantpredictapi",
                               password="0xt2Zf", client_id="0oakq", client_secret="IEdpr")

        mock_post.assert_called()
        api.refresh_access_token()
        self.assertTrue(mock_post.call_count==2)
        # todo: what else can I test for?


    def test_bad_password(self, mock_post):
        '''todo: this is currently not implemented in plantpredict.Api'''
        mock_post.return_value.ok = False
        mock_post.return_value.content = '{"error":"invalid_grant","error_description":"The credentials provided were invalid."}'
        api = plantpredict.Api(username="FS123456@firstsolar.com.plantpredictapi",
                           password="bad_password", client_id="0oakq", client_secret="IEdpr")
        mock_post.assert_called()



if __name__ == '__main__':
    unittest.main()
    
    