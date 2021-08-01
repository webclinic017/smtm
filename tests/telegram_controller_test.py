import unittest
import requests
from smtm import TelegramController
from unittest.mock import *


class TelegramControllerTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_main_should_call__start_get_updates_loop(self):
        tcb = TelegramController()
        tcb.terminating = True  # for Test
        tcb._start_get_updates_loop = MagicMock()
        tcb.main()

        tcb._start_get_updates_loop.assert_called_once()

    def test__terminate_should_set_terminating_flag_True(self):
        tcb = TelegramController()
        tcb.post_worker = MagicMock()
        tcb._terminate()
        self.assertEqual(tcb.terminating, True)
        tcb.post_worker.stop.assert_called_once()

    def test__create_command_should_fill_command_list_correctly(self):
        tcb = TelegramController()
        tcb.command_list = []
        tcb._create_command()
        self.assertEqual(len(tcb.command_list), 5)

    def test__execute_command_should_call_action_correctly(self):
        tcb = TelegramController()
        tcb._send_text_message = MagicMock()
        tcb.main_keyboard = "mango keyboard"
        dummy_command_list = [
            {
                "guide": "{0:15}자동 거래 시작".format("1. 시작"),
                "cmd": ["시작", "1", "1. 시작"],
                "action": MagicMock(),
            },
            {
                "guide": "{0:15}자동 거래 중지".format("2. 중지"),
                "cmd": ["중지", "2", "2. 중지"],
                "action": MagicMock(),
            },
        ]
        tcb.command_list = dummy_command_list
        tcb._execute_command("안녕~")
        tcb._send_text_message.assert_called_once_with(
            "자동 거래 시작 전입니다.\n명령어를 입력해주세요.", "mango keyboard"
        )

        tcb._execute_command("1")
        dummy_command_list[0]["action"].assert_called_with("1")

        tcb._execute_command("시작")
        dummy_command_list[0]["action"].assert_called_with("시작")

        tcb._execute_command("2")
        dummy_command_list[1]["action"].assert_called_with("2")

        tcb._execute_command("중지")
        dummy_command_list[1]["action"].assert_called_with("중지")

        dummy_in_progress = MagicMock()
        tcb.in_progress = dummy_in_progress
        tcb._execute_command("2. 중지")
        dummy_in_progress.assert_called_once_with("2. 중지")

    @patch("threading.Thread")
    def test__start_get_updates_loop_start_thread_correctly(self, mock_thread):
        dummy_thread = MagicMock()
        mock_thread.return_value = dummy_thread
        tcb = TelegramController()
        tcb._handle_message = MagicMock()
        tcb.terminating = True  # for Test
        tcb._start_get_updates_loop()

        dummy_thread.start.assert_called()
        self.assertEqual(mock_thread.call_args[1]["name"], "get updates")
        self.assertEqual(mock_thread.call_args[1]["daemon"], True)

    def test__handle_message_call__execute_command_with_correct_commands(self):
        tcb = TelegramController()
        tcb.CHAT_ID = 1234567890
        tcb._execute_command = MagicMock()
        tcb._get_updates = MagicMock(
            return_value={
                "ok": True,
                "result": [
                    {
                        "update_id": 402107588,
                        "message": {
                            "message_id": 11,
                            "from": {
                                "id": 1234567890,
                                "is_bot": False,
                                "first_name": "msaltnet",
                                "language_code": "ko",
                            },
                            "chat": {"id": 1234567890, "first_name": "msaltnet", "type": "private"},
                            "date": 1627694419,
                            "text": "3",
                        },
                    },
                    {
                        "update_id": 402107589,
                        "message": {
                            "message_id": 12,
                            "from": {
                                "id": 1234567891,
                                "is_bot": False,
                                "first_name": "msaltnet",
                                "language_code": "ko",
                            },
                            "chat": {"id": 1234567891, "first_name": "msaltnet", "type": "private"},
                            "date": 1627694420,
                            "text": "4",
                        },
                    },
                    {
                        "update_id": 402107590,
                        "message": {
                            "message_id": 13,
                            "from": {
                                "id": 1234567890,
                                "is_bot": False,
                                "first_name": "msaltnet",
                                "language_code": "ko",
                            },
                            "chat": {"id": 1234567890, "first_name": "msaltnet", "type": "private"},
                            "date": 1627694420,
                            "text": "5",
                        },
                    },
                ],
            }
        )
        tcb._handle_message()

        self.assertEqual(tcb._execute_command.call_args_list[0][0][0], "3")
        self.assertEqual(tcb._execute_command.call_args_list[1][0][0], "5")
        self.assertEqual(tcb.last_update_id, 402107590)

    def test__send_image_message_shoul_call_sendMessage_api_correctly(self):
        tcb = TelegramController()
        tcb.post_worker = MagicMock()
        tcb.TOKEN = "banana"
        tcb.CHAT_ID = "to_banana"
        tcb._send_http = MagicMock()
        tcb._send_image_message("banana_file")
        tcb.post_worker.post_task.assert_called_once_with(ANY)
        task = tcb.post_worker.post_task.call_args[0][0]
        tcb.post_worker.post_task.call_args[0][0]["runnable"](task)

        tcb._send_http.assert_called_once_with(
            "https://api.telegram.org/banana/sendPhoto?chat_id=to_banana", True, "banana_file"
        )

    def test__send_text_message_shoul_call_sendMessage_api_correctly(self):
        tcb = TelegramController()
        tcb.post_worker = MagicMock()
        tcb.TOKEN = "banana"
        tcb.CHAT_ID = "to_banana"
        tcb._send_http = MagicMock()
        tcb._send_text_message("hello~ banana")
        tcb.post_worker.post_task.assert_called_once_with(ANY)
        task = tcb.post_worker.post_task.call_args[0][0]
        tcb.post_worker.post_task.call_args[0][0]["runnable"](task)

        tcb._send_http.assert_called_once_with(
            "https://api.telegram.org/banana/sendMessage?chat_id=to_banana&text=hello%7E%20banana"
        )

    def test__send_text_message_shoul_call_sendMessage_api_correctly_with_keyboard(self):
        tcb = TelegramController()
        tcb.post_worker = MagicMock()
        tcb.TOKEN = "banana"
        tcb.CHAT_ID = "to_banana"
        tcb._send_http = MagicMock()
        tcb._send_text_message("hello~ banana", "banana_keyboard_markup")
        tcb.post_worker.post_task.assert_called_once_with(ANY)
        task = tcb.post_worker.post_task.call_args[0][0]
        tcb.post_worker.post_task.call_args[0][0]["runnable"](task)

        tcb._send_http.assert_called_once_with(
            "https://api.telegram.org/banana/sendMessage?chat_id=to_banana&text=hello%7E%20banana&reply_markup=banana_keyboard_markup"
        )

    def test__get_updates_call_getUpdates_api_correctly(self):
        tcb = TelegramController()
        tcb.TOKEN = "banana"
        expected_response = "banana_result"
        tcb._send_http = MagicMock(return_value=expected_response)
        updates = tcb._get_updates()
        self.assertEqual(updates, expected_response)
        tcb._send_http.assert_called_once_with(
            "https://api.telegram.org/banana/getUpdates?offset=1&timeout=10"
        )

    @patch("builtins.open", new_callable=mock_open)
    @patch("requests.post")
    def test__send_http_should_call_requests_post_with_file_and_return_result(
        self, mock_post, mock_file
    ):
        tcb = TelegramController()
        expected_response = {"dummy"}
        dummy_response = MagicMock()
        dummy_response.json.return_value = expected_response
        mock_post.return_value = dummy_response
        updates = tcb._send_http("test_url", True, "mango")
        mock_file.assert_called_with("mango", "rb")
        self.assertEqual(updates, expected_response)
        self.assertEqual(mock_post.call_args[0][0].find("test_url"), 0)
        self.assertEqual(mock_post.call_args[1]["files"], {"photo": ANY})

    @patch("requests.post")
    def test__send_http_should_call_requests_post_when_is_post_True(self, mock_post):
        tcb = TelegramController()
        expected_response = {"dummy"}
        dummy_response = MagicMock()
        dummy_response.json.return_value = expected_response
        mock_post.return_value = dummy_response
        updates = tcb._send_http("test_url", True)
        self.assertEqual(updates, expected_response)
        self.assertEqual(mock_post.call_args[0][0].find("test_url"), 0)

    @patch("requests.get")
    def test__send_http_should_call_requests_get_when_is_post_False(self, mock_get):
        tcb = TelegramController()
        expected_response = {"dummy"}
        dummy_response = MagicMock()
        dummy_response.json.return_value = expected_response
        mock_get.return_value = dummy_response
        updates = tcb._send_http("test_url")
        self.assertEqual(updates, expected_response)
        self.assertEqual(mock_get.call_args[0][0].find("test_url"), 0)

    @patch("requests.get")
    def test__send_http_should_return_None_when_receive_invalid_data(self, mock_get):
        tcb = TelegramController()
        dummy_response = MagicMock()
        dummy_response.json.side_effect = ValueError()
        mock_get.return_value = dummy_response

        updates = tcb._send_http("test_url")
        self.assertEqual(updates, None)

    @patch("requests.get")
    def test__send_http_should_return_None_when_receive_response_error(self, mock_get):
        tcb = TelegramController()
        dummy_response = MagicMock()
        dummy_response.json.return_value = "dummy_result"
        dummy_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "HTTPError dummy exception"
        )
        mock_get.return_value = dummy_response

        updates = tcb._send_http("test_url")
        self.assertEqual(updates, None)

    @patch("requests.get")
    def test__send_http_should_return_None_when_connection_fail(self, mock_get):
        tcb = TelegramController()
        dummy_response = MagicMock()
        dummy_response.json.return_value = "dummy_result"
        dummy_response.raise_for_status.side_effect = requests.exceptions.RequestException(
            "RequestException dummy exception"
        )
        mock_get.return_value = dummy_response

        updates = tcb._send_http("test_url")
        self.assertEqual(updates, None)

    def test__query_state_should_call__send_text_message_with_correct_message(self):
        tcb = TelegramController()
        tcb._send_text_message = MagicMock()
        tcb._query_state("state")
        tcb._send_text_message.assert_called_with("자동 거래 시작 전입니다.")

        tcb.operator = "mango"
        tcb._query_state("state")
        tcb._send_text_message.assert_called_with("자동 거래 운영 중입니다.")
