"""MaterialMatch: an introductory engineering materials comparison website."""
from dataclasses import dataclass, field
from math import isfinite
from drafter import *


@dataclass
class Material:
    """Store approximate properties of one example material grade."""
    name: str
    density: float  # g/cm^3
    strength: float  # MPa, illustrative yield strength
    cost_per_kg: float  # USD/kg, illustrative only


@dataclass
class State:
    """Remember the user's materials, selection, volume, and priority."""
    materials: list[Material] = field(default_factory=list)
    selected_material: str = "Aluminum 6061-T6"
    volume: float = 100.0
    comparison_priority: str = "Lowest cost"
    message: str = ""


def initial_state() -> State:
    """Build a fresh starting state with illustrative reference values."""
    return State([
        Material("Aluminum 6061-T6", 2.70, 276.0, 5.0),
        Material("Steel A36", 7.85, 250.0, 2.0),
        Material("Copper C110", 8.96, 69.0, 10.0),
        Material("Titanium Grade 2", 4.51, 275.0, 30.0)
    ])


def mass_kg(material: Material, volume: float) -> float:
    """Convert density times volume from grams to kilograms."""
    return material.density * volume / 1000


def estimated_cost(material: Material, volume: float) -> float:
    """Estimate raw material cost using dollars per kilogram."""
    return mass_kg(material, volume) * material.cost_per_kg


def find_material(materials: list[Material], name: str) -> Material | None:
    """Find a material by its exact name, or return None."""
    for material in materials:
        if material.name == name:
            return material
    return None


def best_material(materials: list[Material], volume: float,
                  priority: str) -> Material | None:
    """Find the best material for a single chosen property."""
    if not materials:
        return None
    best = materials[0]
    for material in materials:
        if priority == "Lowest cost":
            if estimated_cost(material, volume) < estimated_cost(best, volume):
                best = material
        elif priority == "Lowest density":
            if material.density < best.density:
                best = material
        elif priority == "Highest strength":
            if material.strength > best.strength:
                best = material
    return best


def navigation() -> list:
    """Build the same navigation links on each page."""
    return [
        Button("Home", "index"),
        Button("Materials", "materials_page"),
        Button("Calculator", "calculator_page"),
        Button("Compare", "compare_page"),
        Button("Results", "results_page"),
        Button("Add Material", "add_material_page"),
        HorizontalRule()
    ]


def page_content(title: str, description: str) -> list:
    """Create the common heading and navigation for a page."""
    return [Header("MaterialMatch"), Paragraph("Engineering Materials Comparison"),
            *navigation(), Header(title, 2), Paragraph(description)]


@route

def index(state: State) -> Page:
    """Show the home page and explain what the site does."""
    return Page(state, page_content("Welcome", "Compare materials for a simple part.") + [
        Paragraph("Select a material, enter its volume in cubic centimeters, "
                  "and compare mass, estimated raw material cost, and yield strength."),
        Paragraph("This is an educational tool, not a structural design calculator."),
        Button("Start calculating", "calculator_page")
    ])


@route

def materials_page(state: State) -> Page:
    """Show all stored materials and their approximate properties."""
    contents = page_content("Materials library", "Example grades and reference properties:")
    for material in state.materials:
        contents.append(Header(material.name, 3))
        contents.append(Paragraph(
            f"Density: {material.density:.2f} g/cm3 | "
            f"Yield strength: {material.strength:.0f} MPa | "
            f"Estimated price: ${material.cost_per_kg:.2f}/kg"))
    contents.append(Paragraph("Values are illustrative and vary by supplier and condition."))
    return Page(state, contents)



@route
def calculator_page(state: State) -> Page:
    """Ask for a material and a positive part volume."""
    options = [material.name for material in state.materials]

    return Page(state, page_content(
        "Mass and cost calculator",
        [
            Paragraph(state.message),
            SelectBox("material_name", options, state.selected_material),
            Paragraph("Volume (cm3):"),
            TextBox("volume_text", str(state.volume)),
            Button("Calculate", "calculate_material")
        ]
    ))



@route
def calculate_material(
    state: State,
    material_name: str = "",
    volume_text: str = ""
) -> Page:
    """Validate and save the selected material and entered volume."""
    try:
        new_volume = float(volume_text)
    except ValueError:
        state.message = "Please enter a number for volume."
        return calculator_page(state)
    if not isfinite(new_volume) or new_volume <= 0:
        state.message = "Volume must be a positive, finite number."
        return calculator_page(state)
    if find_material(state.materials, material_name) is None:
        state.message = "Please select a valid material."
        return calculator_page(state)
    state.volume = new_volume
    state.selected_material = material_name
    state.message = "Calculation updated successfully."
    return results_page(state)


@route

def compare_page(state: State) -> Page:
    """Let the user choose the property to prioritize."""
    return Page(state, page_content("Compare materials", "Choose one comparison goal.") + [
        SelectBox("new_priority", ["Lowest cost", "Lowest density", "Highest strength"],
                  state.comparison_priority),
        Button("Compare now", "update_comparison")
    ])


@route

def update_comparison(state: State, new_priority: str) -> Page:
    """Save a valid comparison priority and display the results."""
    if new_priority in ["Lowest cost", "Lowest density", "Highest strength"]:
        state.comparison_priority = new_priority
        state.message = "Comparison preference updated."
    else:
        state.message = "Please choose a valid comparison goal."
    return results_page(state)


@route

def results_page(state: State) -> Page:
    """Show the selected calculation and compare every stored material."""
    selected = find_material(state.materials, state.selected_material)
    contents = page_content("Results", "Mass and raw material cost estimates.")
    contents.append(Paragraph(state.message))
    if selected is None:
        contents.append(Paragraph("No selected material was found."))
        return Page(state, contents)
    contents.extend([
        Header("Selected material", 3),
        Paragraph(f"{selected.name} for {state.volume:.2f} cm3:"),
        Paragraph(f"Mass: {mass_kg(selected, state.volume):.3f} kg"),
        Paragraph(f"Estimated raw cost: ${estimated_cost(selected, state.volume):.2f}"),
        Paragraph(f"Approximate yield strength: {selected.strength:.0f} MPa"),
        Header("All materials", 3)
    ])
    for material in state.materials:
        contents.append(Paragraph(
            f"{material.name}: {mass_kg(material, state.volume):.3f} kg; "
            f"${estimated_cost(material, state.volume):.2f}; "
            f"{material.strength:.0f} MPa"))
    winner = best_material(state.materials, state.volume, state.comparison_priority)
    if winner is not None:
        contents.append(Header("Best match", 3))
        contents.append(Paragraph(f"{state.comparison_priority}: {winner.name}"))
    contents.append(Paragraph("Prices and strengths are approximate educational values. "
                              "This ranking considers only one property."))
    return Page(state, contents)


@route

def add_material_page(state: State) -> Page:
    """Show a form for creating a custom material."""
    return Page(state, page_content("Add a custom material", "Enter your own reference values.") + [
        Paragraph(state.message),
        Paragraph("Material name:"), TextBox("new_name", ""),
        Paragraph("Density (g/cm3):"), TextBox("new_density", ""),
        Paragraph("Yield strength (MPa):"), TextBox("new_strength", ""),
        Paragraph("Estimated cost (USD/kg):"), TextBox("new_cost", ""),
        Button("Save material", "save_material")
    ])


@route

def save_material(state: State, new_name: str, new_density: str,
                  new_strength: str, new_cost: str) -> Page:
    """Validate the new properties and add a Material instance to State."""
    name = new_name.strip()
    if not name or find_material(state.materials, name) is not None:
        state.message = "Enter a unique, nonempty material name."
        return add_material_page(state)
    try:
        density = float(new_density)
        strength = float(new_strength)
        cost = float(new_cost)
    except ValueError:
        state.message = "Density, strength, and cost must be numbers."
        return add_material_page(state)
    if not all(isfinite(number) for number in [density, strength, cost]):
        state.message = "Enter finite numbers for all properties."
        return add_material_page(state)
    if density <= 0 or strength <= 0 or cost < 0:
        state.message = "Density and strength must be positive; cost cannot be negative."
        return add_material_page(state)
    state.materials.append(Material(name, density, strength, cost))
    state.selected_material = name
    state.message = name + " was added successfully."
    return materials_page(state)


set_website_title("MaterialMatch | Engineering Materials")
set_site_information(
    author="Zachary Pollack",
    description="An educational tool to compare engineering materials by density, strength and cost.",
    sources="Drafter documentation; illustrative material property estimates.",
    planning=["project_0.pdf", "project_1.pdf"],
    links=[]
)

if __name__ == "__main__":
    start_server(initial_state())

