import unittest

from app.core.runtime import TsukiRuntime, TsukiState


class TsukiRuntimeTest(unittest.TestCase):
    def test_starts_in_standby(self):
        runtime = TsukiRuntime()
        self.assertEqual(runtime.state, TsukiState.STANDBY)

    def test_turn_on_requires_full_phrase(self):
        runtime = TsukiRuntime()
        self.assertIsNone(runtime.handle_control_phrase("Tsuki"))
        self.assertFalse(runtime.is_active)
        self.assertEqual(runtime.handle_control_phrase("Tsuki Turn On"), "activated")
        self.assertTrue(runtime.is_active)

    def test_turn_off_returns_to_standby(self):
        runtime = TsukiRuntime()
        runtime.handle_control_phrase("Tsuki Turn On")
        self.assertEqual(runtime.handle_control_phrase("Tsuki Turn Off"), "deactivated")
        self.assertFalse(runtime.is_active)


if __name__ == "__main__":
    unittest.main()
