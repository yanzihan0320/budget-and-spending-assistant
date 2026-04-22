from pathlib import Path
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.io import load_category_config
from src.models import CategoryManager


class TestCategoryConfig(unittest.TestCase):
    def setUp(self) -> None:
        CategoryManager.clear_custom_categories()

    def tearDown(self) -> None:
        CategoryManager.clear_custom_categories()

    def test_load_category_config_from_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "category_config.json"
            config_path.write_text(
                """{
  \"custom_categories\": [\"Travel\", \"Pets\", \"Catering\", \"Travel\", \"\"]
}
""",
                encoding="utf-8",
            )

            custom_categories = load_category_config(str(config_path))

        self.assertEqual(custom_categories, ["Travel", "Pets"])
        self.assertTrue(CategoryManager.is_valid_category("Travel"))
        self.assertTrue(CategoryManager.is_valid_category("Pets"))

    def test_load_category_config_malformed_json_clears_custom_categories(self) -> None:
        CategoryManager.add_category("Temporary")
        self.assertTrue(CategoryManager.is_valid_category("Temporary"))

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "category_config.json"
            config_path.write_text("{bad-json", encoding="utf-8")
            custom_categories = load_category_config(str(config_path))

        self.assertEqual(custom_categories, [])
        self.assertFalse(CategoryManager.is_valid_category("Temporary"))


if __name__ == "__main__":
    unittest.main()
