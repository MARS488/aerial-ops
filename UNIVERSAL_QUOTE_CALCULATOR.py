#!/usr/bin/env python3
"""
Marcus Jay Herring LLC — Universal Quote Calculator
Calculate margins and generate quotes for any service vertical.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import sys

@dataclass
class Service:
    name: str
    acres_min: float
    acres_max: float
    description: str
    base_price: float
    cost_model: str  # "simple" or "rental"

# Service definitions by vertical
VERTICALS = {
    "civilitysync": {
        "name": "CivilitySync",
        "services": {
            "storm": Service(
                name="Storm/Damage Assessment",
                acres_min=0,
                acres_max=5,
                description="Property damage documentation + improvement plan",
                base_price=1500,
                cost_model="simple"
            ),
            "scan": Service(
                name="Property Scan",
                acres_min=0,
                acres_max=20,
                description="Aerial orthomosaic + 3D model",
                base_price=1200,
                cost_model="simple"
            ),
            "lidar": Service(
                name="LiDAR Survey",
                acres_min=5,
                acres_max=500,
                description="Professional LiDAR capture + processing",
                base_price=2500,
                cost_model="rental"
            ),
        },
        "costs": {
            "simple": {
                "your_time_per_hour": 75,
                "flight_hours_per_acre": 0.25,
                "travel_cost": 50,
                "battery_wear": 30,
                "software_allocation": 50,
                "processing_time_hours": 1.5,
                "processing_rate": 40,
            },
            "rental": {
                "rental_half_day": 350,
                "processing_outsource_base": 1500,
                "travel_cost": 50,
            }
        }
    }
}

def get_service(vertical: str, service_type: str) -> Optional[Service]:
    """Get service definition."""
    if vertical not in VERTICALS:
        return None
    return VERTICALS[vertical]["services"].get(service_type)

def calculate_simple_costs(vertical: str, acres: float) -> Dict[str, float]:
    """Calculate costs for simple service model (time-based)."""
    costs = VERTICALS[vertical]["costs"]["simple"]
    result = {}

    flight_hours = max(1, acres * costs["flight_hours_per_acre"])
    result["flight_time"] = flight_hours * costs["your_time_per_hour"]
    result["travel"] = costs["travel_cost"]
    result["battery_wear"] = costs["battery_wear"]
    result["software_allocation"] = costs["software_allocation"]
    result["processing"] = costs["processing_time_hours"] * costs["processing_rate"]

    return result

def calculate_rental_costs(vertical: str, acres: float) -> Dict[str, float]:
    """Calculate costs for rental service model (equipment-based)."""
    costs = VERTICALS[vertical]["costs"]["rental"]
    result = {}

    # LiDAR rent allocation
    if acres <= 25:
        result["rental_allocation"] = costs["rental_half_day"]
        result["processing_outsource"] = costs["processing_outsource_base"]
    else:
        rental_days = max(1, acres / 250)
        result["rental_allocation"] = 700 * rental_days
        result["processing_outsource"] = costs["processing_outsource_base"] * (acres / 50)

    result["travel"] = costs["travel_cost"]
    return result

def calculate_costs(vertical: str, service_type: str, acres: float) -> Tuple[Dict[str, float], float]:
    """Calculate total costs based on service type."""
    service = get_service(vertical, service_type)
    if not service:
        return {}, 0

    if service.cost_model == "simple":
        costs = calculate_simple_costs(vertical, acres)
    else:
        costs = calculate_rental_costs(vertical, acres)

    total = sum(costs.values())
    return costs, total

def generate_quote(vertical: str, service_type: str, acres: float, custom_price: Optional[float] = None) -> Dict:
    """Generate a complete quote with margin analysis."""
    service = get_service(vertical, service_type)
    if not service:
        return {"error": f"Service {service_type} not found in {vertical}"}

    price = custom_price or service.base_price
    costs, total_cost = calculate_costs(vertical, service_type, acres)

    gross_margin = price - total_cost
    margin_percent = (gross_margin / price * 100) if price > 0 else 0

    # Deposit recommendation (for rental-based services)
    deposit = (total_cost * 1.1) if service.cost_model == "rental" else 0

    # Margin assessment
    if margin_percent < 25:
        health = "⚠️  THIN — consider higher price or skip"
    elif margin_percent < 40:
        health = "⚠️  CAUTION — doable but tight"
    elif margin_percent < 60:
        health = "✓ HEALTHY — good tier"
    else:
        health = "✓✓ STRONG — excellent tier"

    return {
        "vertical": vertical,
        "service_type": service_type,
        "acres": acres,
        "price": price,
        "costs": costs,
        "total_cost": total_cost,
        "gross_margin": gross_margin,
        "margin_percent": margin_percent,
        "deposit_recommended": deposit,
        "margin_health": health,
        "description": service.description,
    }

def format_proposal(quote: Dict) -> str:
    """Format as customer-facing proposal."""
    if "error" in quote:
        return f"Error: {quote['error']}"

    lines = [
        f"## Quote: {quote['service_type'].title()}",
        f"**Property Size:** {quote['acres']} acres",
        f"**Service:** {quote['description']}",
        f"",
        f"**Price:** ${quote['price']:,.2f}",
    ]

    if quote['deposit_recommended'] > 0:
        lines.append(f"**Deposit Required:** ${quote['deposit_recommended']:,.2f}")

    lines.extend([
        f"",
        f"### Includes",
        f"- Professional service delivery",
        f"- Standard report/deliverable",
        f"- One revision round",
        f"",
        f"### Timeline",
        f"- Scheduling: within 5 business days",
        f"- Execution: weather dependent",
        f"- Delivery: per agreement (typically 48 hours)",
    ])

    return "\n".join(lines)

def format_cost_breakdown(quote: Dict) -> str:
    """Format internal cost breakdown."""
    if "error" in quote:
        return f"Error: {quote['error']}"

    lines = [
        f"=== INTERNAL COST BREAKDOWN ===",
        f"Vertical: {quote['vertical'].upper()} | Service: {quote['service_type'].upper()} | Property: {quote['acres']} acres",
        f"",
    ]

    for cost_item, amount in quote['costs'].items():
        lines.append(f"  {cost_item.replace('_', ' ').title():<30} ${amount:>10,.2f}")

    lines.extend([
        f"  {'':30} {'----------':>10}",
        f"  {'Total Cost':<30} ${quote['total_cost']:>10,.2f}",
        f"",
        f"  {'Selling Price':<30} ${quote['price']:>10,.2f}",
        f"  {'Gross Margin':<30} ${quote['gross_margin']:>10,.2f}",
        f"  {'Margin %':<30} {quote['margin_percent']:>10.1f}%",
        f"",
        f"Margin Health: {quote['margin_health']}",
    ])

    if quote['deposit_recommended'] > 0:
        lines.append(f"Deposit recommendation (covers hard costs): ${quote['deposit_recommended']:,.2f}")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: UNIVERSAL_QUOTE_CALCULATOR.py <vertical> <service> <acres> [custom_price]")
        print("")
        print("Verticals and services:")
        for v_name, v_data in VERTICALS.items():
            print(f"  {v_name}:")
            for s_name, s_obj in v_data["services"].items():
                print(f"    - {s_name}: {s_obj.description}")
        print("")
        print("Examples:")
        print("  python3 UNIVERSAL_QUOTE_CALCULATOR.py civilitysync storm 3")
        print("  python3 UNIVERSAL_QUOTE_CALCULATOR.py civilitysync lidar 15")
        print("  python3 UNIVERSAL_QUOTE_CALCULATOR.py civilitysync lidar 15 5000")
        sys.exit(1)

    vertical = sys.argv[1].lower()
    service_type = sys.argv[2].lower()
    acres = float(sys.argv[3])
    custom_price = float(sys.argv[4]) if len(sys.argv) > 4 else None

    quote = generate_quote(vertical, service_type, acres, custom_price)

    print(format_proposal(quote))
    print("")
    print(format_cost_breakdown(quote))
