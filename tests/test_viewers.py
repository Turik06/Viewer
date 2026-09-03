"""!
@file test_viewers.py
@brief Unit tests for BaseViewerWidget, MessageViewerWidget, and ViewerFactory.
"""

import os
import unittest
from PyQt6.QtWidgets import QApplication, QLabel

from viewers.base import BaseViewerWidget, MessageViewerWidget
from viewers.factory import ViewerFactory

os.environ["QT_QPA_PLATFORM"] = "offscreen"


class MockTextViewer(BaseViewerWidget):
    """!
    @brief Concrete viewer implementation for testing.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.label = QLabel("Mock TextViewer", self)

    def load_file(self, filepath: str) -> bool:
        self._current_filepath = filepath
        return True


class FailingViewer(BaseViewerWidget):
    """!
    @brief Concrete viewer implementation that fails during instantiation.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        raise RuntimeError("Simulated instantiation failure")

    def load_file(self, filepath: str) -> bool:
        return False


class TestViewers(unittest.TestCase):
    """!
    @brief Unit tests for viewers base classes and factory.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        ViewerFactory.clear_registry()

    def tearDown(self) -> None:
        ViewerFactory.clear_registry()

    def test_cannot_instantiate_abstract_base_viewer(self) -> None:
        """!
        @brief Verify BaseViewerWidget cannot be instantiated directly.
        """
        with self.assertRaises(TypeError):
            BaseViewerWidget()

    def test_concrete_viewer_subclass(self) -> None:
        """!
        @brief Verify concrete subclass can be instantiated and load_file works.
        """
        viewer = MockTextViewer()
        self.assertIsNone(viewer.current_filepath)
        success = viewer.load_file("example.txt")
        self.assertTrue(success)
        self.assertEqual(viewer.current_filepath, "example.txt")
        viewer.clear()
        self.assertIsNone(viewer.current_filepath)
        viewer.close()

    def test_message_viewer_widget(self) -> None:
        """!
        @brief Verify MessageViewerWidget displays messages and handles load_file/clear.
        """
        viewer = MessageViewerWidget("Initial error")
        self.assertEqual(viewer.message(), "Initial error")
        viewer.set_message("New error message")
        self.assertEqual(viewer.message(), "New error message")
        self.assertFalse(viewer.load_file("test.unknown"))
        self.assertEqual(viewer.current_filepath, "test.unknown")
        viewer.clear()
        self.assertEqual(viewer.message(), "")
        self.assertIsNone(viewer.current_filepath)
        viewer.close()

    def test_factory_register_direct(self) -> None:
        """!
        @brief Verify programmatic registration of single and multiple extensions.
        """
        ViewerFactory.register(".txt", MockTextViewer)
        self.assertIs(ViewerFactory.get_viewer_class("file.txt"), MockTextViewer)
        self.assertIs(ViewerFactory.get_viewer_class("file.TXT"), MockTextViewer)
        self.assertIs(ViewerFactory.get_viewer_class("txt"), MockTextViewer)

        ViewerFactory.register(["md", ".py"], MockTextViewer)
        self.assertIs(ViewerFactory.get_viewer_class("readme.md"), MockTextViewer)
        self.assertIs(ViewerFactory.get_viewer_class("script.py"), MockTextViewer)

    def test_factory_decorator_registration(self) -> None:
        """!
        @brief Verify registration via decorator syntax.
        """

        @ViewerFactory.register([".custom", "special"])
        class CustomViewer(BaseViewerWidget):
            def load_file(self, filepath: str) -> bool:
                return True

        self.assertIs(ViewerFactory.get_viewer_class("data.custom"), CustomViewer)
        self.assertIs(ViewerFactory.get_viewer_class("data.special"), CustomViewer)

    def test_factory_compound_extension(self) -> None:
        """!
        @brief Verify multi-part extension resolution like .tar.gz.
        """

        class TarGzViewer(BaseViewerWidget):
            def load_file(self, filepath: str) -> bool:
                return True

        ViewerFactory.register(".tar.gz", TarGzViewer)
        ViewerFactory.register(".gz", MockTextViewer)

        self.assertIs(ViewerFactory.get_viewer_class("archive.tar.gz"), TarGzViewer)
        self.assertIs(ViewerFactory.get_viewer_class("other.gz"), MockTextViewer)

    def test_factory_exact_filename_matching(self) -> None:
        """!
        @brief Verify matching files without standard extensions (e.g. Dockerfile).
        """

        class ConfigViewer(BaseViewerWidget):
            def load_file(self, filepath: str) -> bool:
                return True

        ViewerFactory.register("Dockerfile", ConfigViewer)
        self.assertIs(ViewerFactory.get_viewer_class("/path/to/Dockerfile"), ConfigViewer)
        self.assertIs(ViewerFactory.get_viewer_class("dockerfile"), ConfigViewer)

    def test_factory_create_viewer(self) -> None:
        """!
        @brief Verify create_viewer instantiates the correct widget and handles exceptions.
        """
        ViewerFactory.register(".txt", MockTextViewer)
        ViewerFactory.register(".fail", FailingViewer)

        viewer = ViewerFactory.create_viewer("test.txt")
        self.assertIsInstance(viewer, MockTextViewer)
        viewer.close()

        # Unknown file type returns None
        unsupported = ViewerFactory.create_viewer("unknown.xyz")
        self.assertIsNone(unsupported)

        # Viewer instantiation failure caught safely
        failing = ViewerFactory.create_viewer("bad.fail")
        self.assertIsNone(failing)

    def test_factory_fallback_and_or_fallback(self) -> None:
        """!
        @brief Verify default fallback viewer behavior.
        """
        ViewerFactory.register_default(MessageViewerWidget)
        self.assertIs(ViewerFactory.get_default_viewer_class(), MessageViewerWidget)
        self.assertIs(ViewerFactory.get_viewer_class("unsupported.bin"), MessageViewerWidget)

        # create_viewer_or_fallback
        fallback_viewer = ViewerFactory.create_viewer_or_fallback("dummy.unknown")
        self.assertIsInstance(fallback_viewer, BaseViewerWidget)
        fallback_viewer.close()

    def test_factory_unregister_and_supported_extensions(self) -> None:
        """!
        @brief Verify unregistering and listing supported extensions.
        """
        ViewerFactory.register([".txt", ".md"], MockTextViewer)
        self.assertIn(".txt", ViewerFactory.supported_extensions())
        self.assertIn(".md", ViewerFactory.supported_extensions())

        ViewerFactory.unregister(".txt")
        self.assertNotIn(".txt", ViewerFactory.supported_extensions())
        self.assertIsNone(ViewerFactory.get_viewer_class("file.txt"))


if __name__ == "__main__":
    unittest.main()
