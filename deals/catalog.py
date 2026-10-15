"""What KDealz covers: consumer electronics, where the reviewer knows the products.

Each category has the spec fields that matter to a buyer, a value score (how much product per dollar),
and the price bands used for "best ... under $X" guides.
"""

CATEGORIES = {
    "phones": {"title": "Mobile phones", "icon": "📱", "bands": [500, 1000, 1500],
               "specs": ["storage_gb", "camera_mp", "battery_mah", "screen_in"],
               "weights": {"storage_gb": .25, "camera_mp": .25, "battery_mah": .3, "screen_in": .2}},
    "mobile-gear": {"title": "Mobile gear", "icon": "🔌", "bands": [50, 100, 200],
                    "specs": ["watts", "capacity_mah"], "weights": {"watts": .5, "capacity_mah": .5}},
    "wearables": {"title": "Wearables", "icon": "⌚", "bands": [200, 400, 800],
                  "specs": ["battery_days", "sensors", "screen_in"], "weights": {"battery_days": .45, "sensors": .4, "screen_in": .15}},
    "smart-home": {"title": "Smart home & IoT", "icon": "🏠", "bands": [100, 250, 500],
                   "specs": ["protocols", "rating"], "weights": {"protocols": .5, "rating": .5}},
    "laptops": {"title": "Laptops", "icon": "💻", "bands": [1000, 1500, 2500],
                "specs": ["ram_gb", "storage_gb", "battery_h", "screen_in"],
                "weights": {"ram_gb": .3, "storage_gb": .25, "battery_h": .3, "screen_in": .15}},
    "monitors": {"title": "Monitors & displays", "icon": "🖥️", "bands": [300, 600, 1200],
                 "specs": ["screen_in", "refresh_hz", "resolution_k"], "weights": {"screen_in": .35, "refresh_hz": .3, "resolution_k": .35}},
    "interactive": {"title": "Interactive displays", "icon": "🧑‍🏫", "bands": [2500, 5000, 9000],
                    "specs": ["screen_in", "touch_points", "resolution_k"], "weights": {"screen_in": .45, "touch_points": .25, "resolution_k": .3}},
}

SPEC_LABEL = {"storage_gb": "GB storage", "camera_mp": "MP camera", "battery_mah": "mAh battery", "screen_in": "″ screen",
              "watts": "W", "capacity_mah": "mAh", "battery_days": "days battery", "sensors": "health sensors",
              "protocols": "smart-home standards", "rating": "★ rating", "ram_gb": "GB RAM", "battery_h": "h battery",
              "refresh_hz": "Hz", "resolution_k": "K", "touch_points": "touch points"}
