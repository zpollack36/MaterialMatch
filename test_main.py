"""Run these tests after installing Drafter: python -m unittest test_main.py"""
import unittest
from main import (Material, initial_state, mass_kg, estimated_cost,
                  find_material, best_material, index, materials_page,
                  calculator_page, calculate_material, compare_page,
                  update_comparison, results_page, add_material_page,
                  save_material)


class MaterialMatchTests(unittest.TestCase):
    """Check calculations, validation, and every application route."""

    def test_calculations(self):
        material = Material("Example", 2.0, 100.0, 10.0)
        self.assertAlmostEqual(mass_kg(material, 500), 1.0)
        self.assertAlmostEqual(estimated_cost(material, 500), 10.0)
        self.assertIsNone(find_material([], "Example"))
        self.assertEqual(best_material([material], 500, "Lowest cost"), material)

    def test_home_route(self):
        self.assertIsNotNone(index(initial_state()))

    def test_materials_route(self):
        self.assertIsNotNone(materials_page(initial_state()))

    def test_calculator_route(self):
        self.assertIsNotNone(calculator_page(initial_state()))

    def test_calculate_route(self):
        state = initial_state()
        calculate_material(state, "Steel A36", "200")
        self.assertEqual(state.volume, 200.0)
        self.assertEqual(state.selected_material, "Steel A36")
        calculate_material(state, "Steel A36", "-2")
        self.assertEqual(state.volume, 200.0)
        calculate_material(state, "Steel A36", "abc")
        self.assertEqual(state.volume, 200.0)

    def test_compare_route(self):
        self.assertIsNotNone(compare_page(initial_state()))

    def test_update_comparison_route(self):
        state = initial_state()
        update_comparison(state, "Highest strength")
        self.assertEqual(state.comparison_priority, "Highest strength")
        update_comparison(state, "Unknown")
        self.assertEqual(state.comparison_priority, "Highest strength")

    def test_results_route(self):
        self.assertIsNotNone(results_page(initial_state()))

    def test_add_material_route(self):
        self.assertIsNotNone(add_material_page(initial_state()))

    def test_save_material_route(self):
        state = initial_state()
        count = len(state.materials)
        save_material(state, "Brass sample", "8.5", "120", "7")
        self.assertEqual(len(state.materials), count + 1)
        self.assertEqual(state.selected_material, "Brass sample")
        save_material(state, "Brass sample", "8.5", "120", "7")
        self.assertEqual(len(state.materials), count + 1)
        save_material(state, "Invalid", "no", "120", "7")
        self.assertEqual(len(state.materials), count + 1)


if __name__ == "__main__":
    unittest.main()
