import tempfile
import unittest
from unittest.mock import MagicMock, patch

import app


class SnapshotApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.app.test_client()
        app.app.config["TESTING"] = True
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_snapshot_dir = app.SNAPSHOT_DIR
        self.original_log_file = app.LOG_FILE
        app.SNAPSHOT_DIR = self.temp_dir.name
        app.LOG_FILE = f"{self.temp_dir.name}/security.log"

    def tearDown(self) -> None:
        app.SNAPSHOT_DIR = self.original_snapshot_dir
        app.LOG_FILE = self.original_log_file
        self.temp_dir.cleanup()

    def test_snapshot_without_key_returns_403(self) -> None:
        response = self.client.get("/snapshot")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"], "Unauthorized")

    @patch("app.cv2.imwrite", return_value=True)
    @patch("app.cv2.VideoCapture")
    def test_snapshot_with_valid_key_returns_200(self, mock_capture, _mock_imwrite) -> None:
        fake_cap = MagicMock()
        fake_cap.isOpened.return_value = True
        fake_cap.read.return_value = (True, object())
        mock_capture.return_value = fake_cap

        response = self.client.get("/snapshot?key=supersecret123")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "success")
        self.assertIn("file", payload)

    @patch("app.cv2.VideoCapture")
    def test_snapshot_camera_not_opened_returns_500(self, mock_capture) -> None:
        fake_cap = MagicMock()
        fake_cap.isOpened.return_value = False
        mock_capture.return_value = fake_cap

        response = self.client.get("/snapshot?key=supersecret123")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["error"], "Camera access failed")


if __name__ == "__main__":
    unittest.main()
