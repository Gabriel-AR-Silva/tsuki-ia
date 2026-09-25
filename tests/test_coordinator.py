import unittest

from app.core.coordinator import TsukiCoordinator


class FakeAssistant:
    def __init__(self):
        self.messages = []

    def process_message(self, message):
        self.messages.append(message)
        return f"processed:{message}"


class CoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.assistant = FakeAssistant()
        self.coordinator = TsukiCoordinator(self.assistant)

    def test_voice_ignores_normal_speech_in_standby(self):
        self.assertIsNone(self.coordinator.handle("olá", require_active=True))
        self.assertEqual(self.assistant.messages, [])

    def test_voice_activation_and_command(self):
        self.assertEqual(
            self.coordinator.handle("Tsuki Turn On", require_active=True),
            "Tsuki ativada.",
        )
        self.assertEqual(
            self.coordinator.handle("abra o FinanSys", require_active=True),
            "processed:abra o FinanSys",
        )

    def test_turn_off_stops_voice_commands(self):
        self.coordinator.handle("Tsuki Turn On", require_active=True)
        self.assertEqual(
            self.coordinator.handle("Tsuki Turn Off", require_active=True),
            "Tsuki em standby.",
        )
        self.assertIsNone(self.coordinator.handle("olá", require_active=True))


if __name__ == "__main__":
    unittest.main()
