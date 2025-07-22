#!/usr/bin/env python3
"""
Urban Pulse - Complete Multi-Zone Spatial Analysis System
Web version with ALL original features preserved + Custom Strategy Creation
Fixed version for workshop deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime
import json
import math
import copy
import base64
from io import BytesIO
import zipfile

# Configure Streamlit page
st.set_page_config(
    page_title="Urban Pulse - Multi-Zone Analysis",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .zone-card {
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9f9f9;
    }
    .priority-emergency { border-left: 5px solid #FF0000; }
    .priority-critical { border-left: 5px solid #FF4500; }
    .priority-high { border-left: 5px solid #FFA500; }
    .priority-medium { border-left: 5px solid #32CD32; }
    .priority-low { border-left: 5px solid #808080; }
    .custom-strategy {
        background-color: #E8F4FD;
        border: 2px dashed #2E86AB;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# COMPLETE DATA STRUCTURES FROM ORIGINAL CODE
CITY_ZONES = {
    "city_center": {
        "name": "City Center",
        "type": "Mixed-Use Urban Core",
        "coordinates": [(3, 3), (7, 7)],
        "characteristics": {
            "density": "High",
            "condition": "Deteriorated",
            "land_uses": ["Commercial", "Mixed residential", "Some vacant"],
            "population_density": 850,
            "economic_activity": "High",
            "infrastructure_quality": "Poor"
        },
        "plots": 11,
        "priority_level": "Critical"
    },
    "commercial_district": {
        "name": "Commercial District", 
        "type": "Business & Commerce",
        "coordinates": [(1, 1), (3, 3)],
        "characteristics": {
            "density": "High",
            "condition": "Good",
            "land_uses": ["Commercial", "Office", "Services"],
            "population_density": 200,
            "economic_activity": "Very High",
            "infrastructure_quality": "Good"
        },
        "plots": 24,
        "priority_level": "High"
    },
    "rich_residential": {
        "name": "Rich Residential",
        "type": "High-Income Housing",
        "coordinates": [(7, 1), (10, 3)],
        "characteristics": {
            "density": "Medium",
            "condition": "Excellent",
            "land_uses": ["Single-family homes", "Luxury apartments"],
            "population_density": 300,
            "economic_activity": "Low",
            "infrastructure_quality": "Excellent"
        },
        "plots": 22,
        "priority_level": "Medium"
    },
    "middle_class": {
        "name": "Middle Class Areas",
        "type": "Middle-Income Housing",
        "coordinates": [(1, 7), (6, 10)],
        "characteristics": {
            "density": "Medium-High",
            "condition": "Good",
            "land_uses": ["Apartments", "Townhouses", "Local services"],
            "population_density": 600,
            "economic_activity": "Medium",
            "infrastructure_quality": "Good"
        },
        "plots": 48,
        "priority_level": "High"
    },
    "poor_areas": {
        "name": "Poor Residential",
        "type": "Low-Income Housing", 
        "coordinates": [(6, 7), (10, 12)],
        "characteristics": {
            "density": "High",
            "condition": "Fair",
            "land_uses": ["Social housing", "Informal settlements"],
            "population_density": 900,
            "economic_activity": "Low",
            "infrastructure_quality": "Fair"
        },
        "plots": 55,
        "priority_level": "Critical"
    },
    "formal_slums": {
        "name": "Formal Slums",
        "type": "Formal Low-Income",
        "coordinates": [(10, 7), (12, 9)],
        "characteristics": {
            "density": "Very High",
            "condition": "Poor",
            "land_uses": ["Formal low-income housing"],
            "population_density": 1200,
            "economic_activity": "Very Low",
            "infrastructure_quality": "Poor"
        },
        "plots": 18,
        "priority_level": "Critical"
    },
    "informal_slums": {
        "name": "Informal Slums",
        "type": "Informal Settlements",
        "coordinates": [(10, 9), (12, 11)],
        "characteristics": {
            "density": "Very High", 
            "condition": "Very Poor",
            "land_uses": ["Informal settlements"],
            "population_density": 1500,
            "economic_activity": "Very Low",
            "infrastructure_quality": "Very Poor"
        },
        "plots": 8,
        "priority_level": "Emergency"
    },
    "risky_slums": {
        "name": "Risky Slums",
        "type": "High-Risk Informal",
        "coordinates": [(11, 10), (12, 12)], 
        "characteristics": {
            "density": "Extreme",
            "condition": "Dangerous",
            "land_uses": ["High-risk informal settlements"],
            "population_density": 2000,
            "economic_activity": "Minimal",
            "infrastructure_quality": "Dangerous"
        },
        "plots": 8,
        "priority_level": "Emergency"
    },
    "central_park": {
        "name": "Central Park",
        "type": "Public Green Areas",
        "coordinates": [(4, 8), (6, 10)],
        "characteristics": {
            "density": "Low",
            "condition": "Good",
            "land_uses": ["Parks", "Green spaces", "Recreation"],
            "population_density": 0,
            "economic_activity": "None",
            "infrastructure_quality": "Good"
        },
        "plots": 3,
        "priority_level": "Medium"
    },
    "luxury_park": {
        "name": "Luxury Park",
        "type": "Premium Green Space",
        "coordinates": [(8, 1), (9, 2)],
        "characteristics": {
            "density": "Low",
            "condition": "Excellent",
            "land_uses": ["Premium parks", "Recreational facilities", "Cultural spaces"],
            "population_density": 0,
            "economic_activity": "Low",
            "infrastructure_quality": "Excellent"
        },
        "plots": 2,
        "priority_level": "Medium"
    },
    "periphery": {
        "name": "Periphery",
        "type": "Suburban/Rural Edge",
        "coordinates": [(12, 1), (15, 12)],
        "characteristics": {
            "density": "Low",
            "condition": "Variable",
            "land_uses": ["Rural", "Suburban", "Agricultural"],
            "population_density": 100,
            "economic_activity": "Low",
            "infrastructure_quality": "Poor"
        },
        "plots": 25,
        "priority_level": "Low"
    }
}

STRATEGIES = [
    {
        "Strategy": "Behavioral Activation Program", 
        "Actions": ["Community Engagement Events", "Public Space Social Programs", "Active Mobility Campaigns", "Social Vitality Enhancement"], 
        "Subsystems": ["Human-Social"], 
        "Loop_Impact": "System Driver", 
        "Evidence_Base": "Pure Human-Social loops 1,3,4,5 - Maximum leverage (8.2x)"
    },
    {
        "Strategy": "Green Infrastructure Expansion", 
        "Actions": ["Urban Tree Planting", "Green Roofs", "Rain Gardens", "Vertical Gardens", "Pocket Parks"], 
        "Subsystems": ["Spatial", "Thermal"], 
        "Loop_Impact": "Subsystem Specialist", 
        "Evidence_Base": "Technical optimization supporting behavioral changes"
    },
    {
        "Strategy": "Eco-Mobility Enhancement", 
        "Actions": ["Bike Infrastructure", "Public Transport Incentives", "Pedestrian Zones", "Car-Free Days", "Electric Vehicle Charging"], 
        "Subsystems": ["Spatial", "Air-Soundscape"], 
        "Loop_Impact": "System Driver", 
        "Evidence_Base": "Activates loops 4, 18 with high leverage"
    },
    {
        "Strategy": "Climate Resilient Zoning", 
        "Actions": ["Height Regulations", "Infill Development", "Mixed Land Use", "Urban Growth Boundaries", "Transit-Oriented Development"], 
        "Subsystems": ["Spatial"], 
        "Loop_Impact": "Cross-Subsystem Bridge", 
        "Evidence_Base": "Infrastructure enabling behavioral activation"
    },
    {
        "Strategy": "Sonic & Airspace Optimization", 
        "Actions": ["Noise Buffer Zones", "Soundproofing Materials", "Emission-Free Zones", "Air Quality Alerts", "Low Emission Transport"], 
        "Subsystems": ["Air-Soundscape"], 
        "Loop_Impact": "System Stabilizer", 
        "Evidence_Base": "Activates balancing loops for quality control"
    },
    {
        "Strategy": "Thermal Equity Participation", 
        "Actions": ["Cool Roof Coatings", "Shading Structures", "Nighttime Cooling", "Community Cool Zones", "Passive Cooling"], 
        "Subsystems": ["Thermal"], 
        "Loop_Impact": "System Stabilizer", 
        "Evidence_Base": "Environmental-Human hybrid loops for comfort regulation"
    },
    {
        "Strategy": "Social Innovation Hub", 
        "Actions": ["Community Centers", "Cultural Events", "Educational Programs", "Local Business Support", "Youth Engagement"], 
        "Subsystems": ["Human-Social"], 
        "Loop_Impact": "System Driver", 
        "Evidence_Base": "Pure Human-Social loops - Behavioral primacy principle"
    },
    {
        "Strategy": "Smart Urban Technology", 
        "Actions": ["Digital Participation Platforms", "Real-time Environmental Monitoring", "Smart Mobility Systems", "Energy Management Systems"], 
        "Subsystems": ["Spatial", "Air-Soundscape", "Thermal"], 
        "Loop_Impact": "Cross-Subsystem Bridge", 
        "Evidence_Base": "Technology enabling behavioral change"
    }
]

# Strategy Keywords for Custom Strategy Creation
STRATEGY_KEYWORDS = {
    "Human-Social": [
        "community", "social", "engagement", "participation", "behavioral", "cultural", "education", 
        "awareness", "involvement", "activation", "empowerment", "local", "neighborhood", "residents",
        "citizens", "public", "collaborative", "inclusive", "accessible", "democratic"
    ],
    "Spatial": [
        "infrastructure", "development", "planning", "zoning", "density", "layout", "design", 
        "construction", "building", "space", "land use", "urban form", "architecture", "transport",
        "connectivity", "accessibility", "mixed use", "compact", "walkable", "transit-oriented"
    ],
    "Air-Soundscape": [
        "air quality", "pollution", "emissions", "noise", "sound", "acoustic", "clean air", 
        "ventilation", "breathing", "atmosphere", "environment", "health", "toxic", "fresh",
        "quiet", "peaceful", "soundproofing", "buffer", "monitoring", "control"
    ],
    "Thermal": [
        "temperature", "heat", "cooling", "warm", "climate", "comfort", "energy", "thermal",
        "shading", "insulation", "ventilation", "passive", "solar", "green roof", "trees",
        "microclimate", "urban heat", "cool", "adaptation", "resilience"
    ]
}

# Action suggestions based on keywords
ACTION_SUGGESTIONS = {
    "community": ["Community Forums", "Neighborhood Assemblies", "Local Councils", "Resident Meetings"],
    "engagement": ["Participatory Workshops", "Public Consultations", "Stakeholder Meetings", "Town Halls"],
    "green": ["Tree Planting", "Green Walls", "Community Gardens", "Parks Development"],
    "mobility": ["Bike Lanes", "Walking Paths", "Public Transport", "Car-Free Zones"],
    "air": ["Emission Controls", "Air Monitoring", "Clean Zones", "Pollution Reduction"],
    "thermal": ["Cooling Centers", "Shading Structures", "Cool Roofs", "Thermal Comfort"],
    "noise": ["Sound Barriers", "Quiet Zones", "Noise Monitoring", "Acoustic Design"],
    "infrastructure": ["Road Improvements", "Utility Upgrades", "Digital Infrastructure", "Facility Development"],
    "social": ["Social Programs", "Cultural Events", "Youth Activities", "Senior Services"],
    "technology": ["Smart Systems", "Digital Platforms", "Monitoring Networks", "Data Analytics"]
}

ZONE_STRATEGY_MULTIPLIERS = {
    "Human-Social": {
        "city_center": 1.4, "commercial_district": 0.9, "rich_residential": 0.8, "middle_class": 1.2,
        "poor_areas": 1.6, "formal_slums": 1.8, "informal_slums": 2.0, "risky_slums": 2.2,
        "central_park": 1.4, "luxury_park": 1.1, "periphery": 0.7
    },
    "Spatial": {
        "city_center": 1.6, "commercial_district": 1.3, "rich_residential": 0.9, "middle_class": 1.2,
        "poor_areas": 1.5, "formal_slums": 1.7, "informal_slums": 1.9, "risky_slums": 2.1,
        "central_park": 1.3, "luxury_park": 1.0, "periphery": 1.4
    },
    "Air-Soundscape": {
        "city_center": 1.8, "commercial_district": 1.5, "rich_residential": 1.0, "middle_class": 1.3,
        "poor_areas": 1.6, "formal_slums": 1.8, "informal_slums": 2.0, "risky_slums": 2.2,
        "central_park": 0.8, "luxury_park": 0.7, "periphery": 0.9
    },
    "Thermal": {
        "city_center": 1.5, "commercial_district": 1.3, "rich_residential": 0.9, "middle_class": 1.2,
        "poor_areas": 1.6, "formal_slums": 1.8, "informal_slums": 2.0, "risky_slums": 2.2,
        "central_park": 0.7, "luxury_park": 0.6, "periphery": 0.8
    }
}

ZONE_ADJACENCY = {
    "city_center": ["commercial_district", "middle_class", "poor_areas", "central_park"],
    "commercial_district": ["city_center", "rich_residential", "middle_class"],
    "rich_residential": ["commercial_district", "middle_class", "luxury_park"],
    "middle_class": ["city_center", "commercial_district", "rich_residential", "poor_areas", "central_park"],
    "poor_areas": ["city_center", "middle_class", "formal_slums", "central_park"],
    "formal_slums": ["poor_areas", "informal_slums"],
    "informal_slums": ["formal_slums", "risky_slums"],
    "risky_slums": ["informal_slums"],
    "central_park": ["city_center", "middle_class", "poor_areas"],
    "luxury_park": ["rich_residential"],
    "periphery": ["poor_areas", "formal_slums"]
}

SCIENTIFIC_LOOP_DATA = {
    1: {"type": "R", "variables": ["Active attendance level in open/public spaces", "Active mobility tendency and usage"], 
        "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.147, "system_influence": 0.735, 
        "leverage": 1.275, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    3: {"type": "R", "variables": ["Active attendance level in open/public spaces", "recreational and social advantages rate"], 
        "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.146, "system_influence": 0.730, 
        "leverage": 1.263, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    4: {"type": "R", "variables": ["Active mobility tendency and usage", "Desire to walking"], 
        "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.145, "system_influence": 0.725, 
        "leverage": 1.251, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    5: {"type": "R", "variables": ["Active attendance level in open/public spaces", "Active mobility tendency and usage"], 
        "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.147, "system_influence": 0.735, 
        "leverage": 1.275, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    8: {"type": "R", "variables": ["Active attendance level in open/public spaces", "Local economic activities"], 
        "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.145, "system_influence": 0.725, 
        "leverage": 1.251, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    10: {"type": "R", "variables": ["Active attendance level in open/public spaces", "recreational and social advantages rate"], 
         "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.146, "system_influence": 0.730, 
         "leverage": 1.263, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    18: {"type": "R", "variables": ["Active mobility tendency and usage", "Desire to walking"], 
         "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.145, "system_influence": 0.725, 
         "leverage": 1.251, "role": "System Driver", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    19: {"type": "R", "variables": ["Active attendance level in open/public spaces", "social vitality", "Local economic activities"], 
         "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.119, "system_influence": 0.595, 
         "leverage": 1.012, "role": "System Stabilizer", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    20: {"type": "R", "variables": ["Active attendance level in open/public spaces", "social vitality", "recreational and social advantages rate"], 
         "identity": "Pure Human-Social", "purity_score": 1.000, "integration_rate": 0.119, "system_influence": 0.595, 
         "leverage": 1.012, "role": "System Stabilizer", "strategic_value": "Critical", "subsystems": ["Human-Social"]},
    21: {"type": "B", "variables": ["Active attendance level in open/public spaces", "Exposure possibility to air pollution", "motorized transport usage", "Active mobility tendency and usage"], 
         "identity": "Human-Social-Dominant", "purity_score": 0.750, "integration_rate": 0.102, "system_influence": 0.382, 
         "leverage": 0.578, "role": "System Stabilizer", "strategic_value": "Important", "subsystems": ["Human-Social", "Air-Soundscape"]},
    22: {"type": "B", "variables": ["Active attendance level in open/public spaces", "Exposure possibility to noise", "motorized transport usage", "Active mobility tendency and usage"], 
         "identity": "Human-Social-Dominant", "purity_score": 0.750, "integration_rate": 0.102, "system_influence": 0.382, 
         "leverage": 0.578, "role": "System Stabilizer", "strategic_value": "Important", "subsystems": ["Human-Social", "Air-Soundscape"]},
    12: {"type": "R", "variables": ["Building density", "High-density Mixed Land Use/Activities"], 
         "identity": "Pure Spatial", "purity_score": 1.000, "integration_rate": 0.087, "system_influence": 0.435, 
         "leverage": 0.624, "role": "Subsystem Specialist", "strategic_value": "Important", "subsystems": ["Spatial"]},
    13: {"type": "B", "variables": ["Building density", "Low-density/ Sprawl Growth"], 
         "identity": "Pure Spatial", "purity_score": 1.000, "integration_rate": 0.087, "system_influence": 0.435, 
         "leverage": 0.624, "role": "Subsystem Specialist", "strategic_value": "Important", "subsystems": ["Spatial"]},
    17: {"type": "R", "variables": ["Balanced allocation of green/public spaces", "Green and open spaces (area or accessibility)"], 
         "identity": "Pure Spatial", "purity_score": 1.000, "integration_rate": 0.071, "system_influence": 0.355, 
         "leverage": 0.497, "role": "Subsystem Specialist", "strategic_value": "Important", "subsystems": ["Spatial"]},
    14: {"type": "B", "variables": ["Exposure possibility to noise", "Exposure rate to noise"], 
         "identity": "Pure Environmental", "purity_score": 1.000, "integration_rate": 0.052, "system_influence": 0.260, 
         "leverage": 0.364, "role": "Subsystem Specialist", "strategic_value": "Moderate", "subsystems": ["Air-Soundscape"]},
    15: {"type": "B", "variables": ["Exposure rate to noise", "Soundscape quality level"], 
         "identity": "Pure Environmental", "purity_score": 1.000, "integration_rate": 0.052, "system_influence": 0.260, 
         "leverage": 0.364, "role": "Subsystem Specialist", "strategic_value": "Moderate", "subsystems": ["Air-Soundscape"]},
    16: {"type": "B", "variables": ["Exposure possibility to air pollution", "Exposure rate to air pollution"], 
         "identity": "Pure Environmental", "purity_score": 1.000, "integration_rate": 0.051, "system_influence": 0.255, 
         "leverage": 0.357, "role": "Subsystem Specialist", "strategic_value": "Moderate", "subsystems": ["Air-Soundscape"]}
}

UEC_SCALE = {
    "ranges": {
        (0, 1.0): {"level": "Very Poor", "color": "#8B0000", "description": "Critical intervention needed"},
        (1.0, 2.0): {"level": "Poor", "color": "#DC143C", "description": "Major improvements required"},
        (2.0, 3.0): {"level": "Below Average", "color": "#FF4500", "description": "Significant improvements needed"},
        (3.0, 4.0): {"level": "Average", "color": "#FFA500", "description": "Some improvements beneficial"},
        (4.0, 5.0): {"level": "Good", "color": "#32CD32", "description": "Solid performance with room for growth"},
        (5.0, 6.0): {"level": "Very Good", "color": "#228B22", "description": "Strong performance"},
        (6.0, 7.0): {"level": "Excellent", "color": "#006400", "description": "Outstanding performance"},
        (7.0, 10.0): {"level": "Exceptional", "color": "#004d00", "description": "World-class urban sustainability"}
    }
}

def get_uec_interpretation(score):
    """Get UEC score interpretation"""
    for (min_val, max_val), info in UEC_SCALE["ranges"].items():
        if min_val <= score < max_val:
            return info
    return UEC_SCALE["ranges"][(7.0, 10.0)]

# Initialize session state
def init_session_state():
    if 'game_manager' not in st.session_state:
        st.session_state.game_manager = MultiZoneGameManager()
    if 'team_name' not in st.session_state:
        st.session_state.team_name = ""
    if 'game_name' not in st.session_state:
        st.session_state.game_name = ""
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'custom_strategies' not in st.session_state:
        st.session_state.custom_strategies = {}

# COMPLETE CALCULATION ENGINE
class SpatialEffectsCalculator:
    def __init__(self):
        self.zones = CITY_ZONES
        self.adjacency = ZONE_ADJACENCY
        self.zone_multipliers = ZONE_STRATEGY_MULTIPLIERS
        self.loop_data = SCIENTIFIC_LOOP_DATA
    
    def calculate_euclidean_distance(self, zone1, zone2):
        """Calculate Euclidean distance between zone centers"""
        z1_coords = self.zones[zone1]["coordinates"]
        z2_coords = self.zones[zone2]["coordinates"]
        
        z1_center = ((z1_coords[0][0] + z1_coords[1][0]) / 2, (z1_coords[0][1] + z1_coords[1][1]) / 2)
        z2_center = ((z2_coords[0][0] + z2_coords[1][0]) / 2, (z2_coords[0][1] + z2_coords[1][1]) / 2)
        
        return math.sqrt((z1_center[0] - z2_center[0])**2 + (z1_center[1] - z2_center[1])**2)
    
    def calculate_loop_activation_score(self, actions, subsystems):
        """Calculate loop activation based on scientific analysis"""
        activation_score = 0
        activated_loops = []
        
        for loop_id, loop_data in self.loop_data.items():
            loop_subsystems = set(loop_data["subsystems"])
            action_subsystems = set(subsystems)
            
            overlap = loop_subsystems.intersection(action_subsystems)
            if overlap:
                overlap_ratio = len(overlap) / len(loop_subsystems)
                loop_influence = loop_data["system_influence"]
                loop_leverage = loop_data["leverage"]
                
                purity_bonus = 1.0 if loop_data["purity_score"] == 1.0 else 0.7
                
                activation = overlap_ratio * loop_influence * loop_leverage * purity_bonus
                activation_score += activation
                
                activated_loops.append({
                    "loop_id": loop_id,
                    "activation": activation,
                    "influence": loop_influence,
                    "leverage": loop_leverage,
                    "role": loop_data["role"],
                    "strategic_value": loop_data["strategic_value"]
                })
        
        return activation_score, activated_loops
    
    def calculate_multi_zone_effects(self, zone_actions_dict, round_number):
        """Calculate complete multi-zone effects"""
        total_effects = {
            "direct_effects": {},
            "spillover_effects": {},
            "cross_zone_synergies": {},
            "total_city_impact": {},
            "activated_loops": [],
            "zone_performance": {}
        }
        
        all_activated_loops = []
        zone_base_effects = {}
        
        # Calculate direct effects for each zone
        for zone, zone_data in zone_actions_dict.items():
            actions = zone_data.get("actions", [])
            strategies = zone_data.get("strategies", [])
            
            if not actions:
                continue
            
            subsystems = self._get_subsystems_from_strategies(strategies)
            activation_score, activated_loops = self.calculate_loop_activation_score(actions, subsystems)
            all_activated_loops.extend(activated_loops)
            
            zone_effects = self._calculate_zone_base_effects(subsystems, zone, activation_score, actions)
            zone_base_effects[zone] = zone_effects
            total_effects["direct_effects"][zone] = zone_effects
        
        # Calculate spillover effects between zones
        for source_zone, source_effects in zone_base_effects.items():
            for target_zone in self.zones.keys():
                if target_zone != source_zone:
                    spillover = self._calculate_spillover(source_zone, target_zone, source_effects, round_number)
                    
                    if target_zone not in total_effects["spillover_effects"]:
                        total_effects["spillover_effects"][target_zone] = {}
                    
                    total_effects["spillover_effects"][target_zone][source_zone] = spillover
        
        # Calculate cross-zone synergies
        if len(zone_actions_dict) > 1:
            total_effects["cross_zone_synergies"] = self._calculate_cross_zone_synergies(zone_actions_dict, zone_base_effects)
        
        # Calculate total city impact
        total_effects["total_city_impact"] = self._calculate_total_city_impact(
            total_effects["direct_effects"], 
            total_effects["spillover_effects"],
            total_effects["cross_zone_synergies"]
        )
        
        # Calculate zone performance metrics
        for zone in zone_actions_dict.keys():
            total_effects["zone_performance"][zone] = self._calculate_zone_performance(
                zone, zone_base_effects.get(zone, {}), total_effects
            )
        
        total_effects["activated_loops"] = all_activated_loops
        
        return total_effects
    
    def _get_subsystems_from_strategies(self, strategy_names):
        """Extract subsystems from strategies"""
        subsystems = set()
        
        for strategy_name in strategy_names:
            # Check predefined strategies
            for strat_data in STRATEGIES:
                if strat_data["Strategy"] == strategy_name:
                    subsystems.update(strat_data["Subsystems"])
                    break
            else:
                # Check custom strategies
                if strategy_name in st.session_state.custom_strategies:
                    custom_strategy = st.session_state.custom_strategies[strategy_name]
                    subsystems.update(custom_strategy.get("Subsystems", ["Human-Social"]))
        
        if not subsystems:
            subsystems.add("Human-Social")
        
        return list(subsystems)
    
    def _calculate_zone_base_effects(self, subsystems, zone, activation_score, actions):
        """Calculate base effects in target zone with scientific multipliers"""
        zone_effects = {}
        
        base_impact = len(actions) * 2.0
        loop_multiplier = 1.0 + (activation_score / 10.0)
        
        for subsystem in subsystems:
            zone_multiplier = self.zone_multipliers.get(subsystem, {}).get(zone, 1.0)
            
            if subsystem == "Human-Social":
                behavioral_multiplier = 8.2
            else:
                behavioral_multiplier = 1.0
            
            effect = base_impact * loop_multiplier * zone_multiplier * behavioral_multiplier
            zone_effects[subsystem] = effect
        
        return zone_effects
    
    def _calculate_spillover(self, source_zone, target_zone, source_effects, round_number):
        """Calculate spillover effects with scientific decay functions"""
        distance = self.calculate_euclidean_distance(source_zone, target_zone)
        
        if target_zone in self.adjacency.get(source_zone, []):
            category = "adjacent"
            decay_multiplier = 0.7 * np.exp(-0.5 * distance)
            delay_rounds = 1
        elif distance <= 3.0:
            category = "nearby"
            decay_multiplier = 0.4 * np.exp(-0.8 * distance)
            delay_rounds = 2
        elif distance <= 6.0:
            category = "distant"
            decay_multiplier = 0.15 * np.exp(-1.2 * distance)
            delay_rounds = 3
        else:
            category = "distant"
            decay_multiplier = 0.15 * np.exp(-1.2 * distance)
            delay_rounds = 3
        
        spillover_effects = {}
        for subsystem, effect in source_effects.items():
            spillover_effects[subsystem] = effect * decay_multiplier
        
        return {
            "effects": spillover_effects,
            "delay_rounds": delay_rounds,
            "distance_category": category,
            "distance": distance,
            "decay_multiplier": decay_multiplier,
            "effective_round": round_number + delay_rounds
        }
    
    def _calculate_cross_zone_synergies(self, zone_actions_dict, zone_base_effects):
        """Calculate synergistic effects between multiple zones"""
        synergies = {}
        zones = list(zone_actions_dict.keys())
        
        for i, zone1 in enumerate(zones):
            for j, zone2 in enumerate(zones):
                if i < j:
                    synergy_key = f"{zone1}-{zone2}"
                    
                    effects1 = zone_base_effects.get(zone1, {})
                    effects2 = zone_base_effects.get(zone2, {})
                    
                    synergy_score = 0
                    for subsystem in ["Human-Social", "Spatial", "Air-Soundscape", "Thermal"]:
                        effect1 = effects1.get(subsystem, 0)
                        effect2 = effects2.get(subsystem, 0)
                        
                        if effect1 > 0 and effect2 > 0:
                            synergy = math.sqrt(effect1 * effect2) * 0.3
                            synergy_score += synergy
                    
                    distance = self.calculate_euclidean_distance(zone1, zone2)
                    distance_factor = 1.0 / (1.0 + distance * 0.1)
                    
                    synergies[synergy_key] = {
                        "synergy_score": synergy_score * distance_factor,
                        "distance": distance,
                        "zones": [zone1, zone2]
                    }
        
        return synergies
    
    def _calculate_total_city_impact(self, direct_effects, spillover_effects, cross_zone_synergies):
        """Calculate total city-wide impact"""
        total_impact = {"Human-Social": 0, "Spatial": 0, "Air-Soundscape": 0, "Thermal": 0}
        
        for zone, effects in direct_effects.items():
            for subsystem, effect in effects.items():
                total_impact[subsystem] += effect
        
        for target_zone, source_effects in spillover_effects.items():
            for source_zone, spillover_data in source_effects.items():
                for subsystem, effect in spillover_data["effects"].items():
                    total_impact[subsystem] += effect
        
        for synergy_key, synergy_data in cross_zone_synergies.items():
            synergy_per_subsystem = synergy_data["synergy_score"] / 4
            for subsystem in total_impact.keys():
                total_impact[subsystem] += synergy_per_subsystem
        
        return total_impact
    
    def _calculate_zone_performance(self, zone, zone_effects, total_effects):
        """Calculate comprehensive zone performance metrics"""
        zone_info = self.zones.get(zone, {})
        
        total_zone_effect = sum(zone_effects.values()) if zone_effects else 0
        
        priority_multipliers = {
            "Emergency": 2.2, "Critical": 1.8, "High": 1.5, "Medium": 1.0, "Low": 0.8
        }
        priority_multiplier = priority_multipliers.get(zone_info.get("priority_level", "Medium"), 1.0)
        
        uec_score = total_zone_effect * priority_multiplier / 10.0
        
        return {
            "uec_score": uec_score,
            "priority_level": zone_info.get("priority_level", "Medium"),
            "priority_multiplier": priority_multiplier,
            "total_direct_effect": total_zone_effect,
            "performance_level": get_uec_interpretation(uec_score)["level"],
            "improvement_potential": max(0, 6.0 - uec_score)
        }

# MULTI-ZONE GAME MANAGER
class MultiZoneGameManager:
    def __init__(self):
        self.selected_zones = {}
        self.current_round = 1
        self.round_history = {}
        self.spatial_calculator = SpatialEffectsCalculator()
        self.game_id = None
        self.team_id = None
    
    def add_zone_selection(self, zone_id, strategies, actions):
        """Add or update zone selection"""
        if zone_id not in self.selected_zones:
            self.selected_zones[zone_id] = {"strategies": [], "actions": []}
        
        self.selected_zones[zone_id]["strategies"] = strategies.copy()
        self.selected_zones[zone_id]["actions"] = actions.copy()
    
    def calculate_round_effects(self):
        """Calculate effects for current round"""
        if not self.selected_zones:
            return None
        
        zone_actions_dict = {}
        
        for zone_id, zone_data in self.selected_zones.items():
            strategies = zone_data.get("strategies", [])
            actions = zone_data.get("actions", [])
            
            if strategies and actions:
                zone_actions_dict[zone_id] = {
                    "strategies": strategies,
                    "actions": actions
                }
        
        if not zone_actions_dict:
            return None
        
        return self.spatial_calculator.calculate_multi_zone_effects(zone_actions_dict, self.current_round)

def calculate_normalized_uec_score(effects):
    """Calculate normalized UEC score (0-100 scale)"""
    total_impact = effects.get("total_city_impact", {})
    
    max_values = {
        "Human-Social": 200.0,
        "Spatial": 150.0,
        "Air-Soundscape": 100.0,
        "Thermal": 100.0
    }
    
    normalized_scores = {}
    for subsystem, impact in total_impact.items():
        max_val = max_values.get(subsystem, 100.0)
        normalized_score = min((impact / max_val) * 100, 100)
        normalized_scores[subsystem] = normalized_score
    
    weights = {
        "Human-Social": 0.4,
        "Spatial": 0.25,
        "Air-Soundscape": 0.175,
        "Thermal": 0.175
    }
    
    overall_uec = sum(normalized_scores.get(sub, 0) * weight for sub, weight in weights.items())
    
    return {
        "overall_uec": overall_uec,
        "subsystem_scores": normalized_scores,
        "interpretation": get_performance_level(overall_uec)
    }

def get_performance_level(uec_score):
    """Get game-like performance interpretation"""
    if uec_score >= 90:
        return {"level": "🏆 LEGENDARY", "color": "#FFD700", "message": "World-class urban sustainability!"}
    elif uec_score >= 80:
        return {"level": "🚀 EXPERT", "color": "#00FF00", "message": "Exceptional urban planning!"}
    elif uec_score >= 65:
        return {"level": "⭐ SKILLED", "color": "#32CD32", "message": "Great strategic thinking!"}
    elif uec_score >= 50:
        return {"level": "📈 RISING", "color": "#FFA500", "message": "Good progress!"}
    elif uec_score >= 35:
        return {"level": "🔧 APPRENTICE", "color": "#FF6347", "message": "Learning the basics!"}
    else:
        return {"level": "🌱 BEGINNER", "color": "#FF4500", "message": "Focus on behavioral strategies!"}

def analyze_keywords_for_subsystem(text):
    """Analyze text keywords to determine subsystem focus"""
    text_lower = text.lower()
    subsystem_scores = {"Human-Social": 0, "Spatial": 0, "Air-Soundscape": 0, "Thermal": 0}
    
    for subsystem, keywords in STRATEGY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                subsystem_scores[subsystem] += 1
    
    # Determine primary subsystem(s)
    max_score = max(subsystem_scores.values())
    if max_score > 0:
        primary_subsystems = [sub for sub, score in subsystem_scores.items() if score == max_score]
        return primary_subsystems
    else:
        return ["Human-Social"]  # Default to behavioral

def suggest_actions_from_keywords(text):
    """Suggest actions based on keywords in text"""
    text_lower = text.lower()
    suggested_actions = set()
    
    for keyword, actions in ACTION_SUGGESTIONS.items():
        if keyword in text_lower:
            suggested_actions.update(actions[:2])  # Add top 2 actions per keyword
    
    return list(suggested_actions)[:6]  # Return max 6 suggestions

def create_custom_strategy(strategy_name, description, zone_id):
    """Create a custom strategy based on user input"""
    # Analyze keywords to determine subsystems
    subsystems = analyze_keywords_for_subsystem(description)
    
    # Suggest actions
    suggested_actions = suggest_actions_from_keywords(description)
    
    # Determine loop impact based on subsystems
    if len(subsystems) == 1 and subsystems[0] == "Human-Social":
        loop_impact = "System Driver"
        evidence_base = "Behavioral Primacy - Custom strategy focusing on human-centered interventions"
    elif len(subsystems) == 1:
        loop_impact = "Subsystem Specialist"
        evidence_base = f"Specialized {subsystems[0]} intervention strategy"
    else:
        loop_impact = "Cross-Subsystem Bridge"
        evidence_base = "Multi-subsystem integration strategy"
    
    custom_strategy = {
        "Strategy": strategy_name,
        "Description": description,
        "Actions": suggested_actions,
        "Subsystems": subsystems,
        "Loop_Impact": loop_impact,
        "Evidence_Base": evidence_base,
        "Created_For_Zone": CITY_ZONES[zone_id]["name"],
        "Custom": True
    }
    
    # Store in session state
    st.session_state.custom_strategies[strategy_name] = custom_strategy
    
    return custom_strategy

# MAIN APPLICATION
def main():
    init_session_state()
    
    st.markdown('<h1 class="main-header">🏙️ Urban Pulse - Multi-Zone Spatial Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎮 Navigation")
    page = st.sidebar.selectbox("Choose Page", [
        "🎯 Team Setup",
        "📖 City Introduction", 
        "🗺️ Interactive City Map",
        "⚙️ Zone Configuration",
        "✨ Custom Strategy Creator",
        "📊 Game Results Dashboard",
        "🌊 Spillover Analysis",
        "🔬 Scientific Loop Analysis",
        "📈 Multi-Round Comparison",
        "📋 Reports & Export"
    ])
    
    # Display current session info
    if st.session_state.team_name:
        st.sidebar.success(f"**Team:** {st.session_state.team_name}")
        st.sidebar.info(f"**Round:** {st.session_state.current_round}")
        st.sidebar.info(f"**Zones:** {len(st.session_state.game_manager.selected_zones)}")
        st.sidebar.info(f"**Custom Strategies:** {len(st.session_state.custom_strategies)}")
    
    # Route to appropriate page
    if page == "🎯 Team Setup":
        team_setup_page()
    elif page == "📖 City Introduction":
        city_introduction_page()
    elif page == "🗺️ Interactive City Map":
        city_map_page()
    elif page == "⚙️ Zone Configuration":
        zone_configuration_page()
    elif page == "✨ Custom Strategy Creator":
        custom_strategy_creator_page()
    elif page == "📊 Game Results Dashboard":
        results_dashboard_page()
    elif page == "🌊 Spillover Analysis":
        spillover_analysis_page()
    elif page == "🔬 Scientific Loop Analysis":
        loop_analysis_page()
    elif page == "📈 Multi-Round Comparison":
        multi_round_comparison_page()
    elif page == "📋 Reports & Export":
        reports_export_page()

def team_setup_page():
    st.header("🎯 Team Setup & Game Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Game Session Configuration")
        
        game_name = st.text_input("Game/City Name", value=st.session_state.game_name or "Urban Challenge 2025")
        team_name = st.text_input("Team Name", value=st.session_state.team_name or "")
        
        col_a, col_b = st.columns(2)
        with col_a:
            round_num = st.selectbox("Round", [1, 2, 3, 4], index=st.session_state.current_round-1)
        with col_b:
            parish_code = st.number_input("Parish Code", min_value=100, max_value=124, value=100)
        
        if st.button("🚀 Start Game Session", type="primary"):
            if team_name:
                st.session_state.team_name = team_name
                st.session_state.game_name = game_name
                st.session_state.current_round = round_num
                st.session_state.game_manager.current_round = round_num
                st.session_state.game_manager.team_id = team_name
                st.session_state.game_manager.game_id = game_name
                st.success(f"✅ Game session started! Team: {team_name}, Round: {round_num}")
                st.balloons()
            else:
                st.error("Please enter a team name!")
    
    with col2:
        st.subheader("🎮 Session Status")
        if st.session_state.team_name:
            st.success(f"**Active Team:** {st.session_state.team_name}")
            st.info(f"**Game:** {st.session_state.game_name}")
            st.info(f"**Current Round:** {st.session_state.current_round}")
            st.info(f"**Zones Selected:** {len(st.session_state.game_manager.selected_zones)}")
            
            # Calculate current UEC if zones are configured
            effects = st.session_state.game_manager.calculate_round_effects()
            if effects:
                uec_data = calculate_normalized_uec_score(effects)
                st.metric("Current UEC Score", f"{uec_data['overall_uec']:.1f}/100")
                st.write(f"**Level:** {uec_data['interpretation']['level']}")
            else:
                st.metric("Current UEC Score", "0.0/100")
                st.write("**Status:** Ready to configure")
        else:
            st.warning("No active session")
        
        st.subheader("🎯 Quick Actions")
        if st.button("🔄 Reset Session"):
            st.session_state.game_manager = MultiZoneGameManager()
            st.session_state.team_name = ""
            st.session_state.game_name = ""
            st.session_state.custom_strategies = {}
            st.rerun()

def city_introduction_page():
    st.header("📖 Urban Sustainability Challenge - City Overview")
    
    # Introduction content
    st.markdown("""
    ## 🏙️ Welcome to Urban Pulse
    
    You are about to engage with a comprehensive urban sustainability simulation based on scientific analysis of **113 feedback loops** that govern urban systems. This simulation represents a mid-sized city facing typical urban sustainability challenges.
    
    ### 🎯 Your Mission
    Transform this city's **Urban Environmental Comfort (UEC)** score from its current state to world-class levels by making strategic interventions that improve residents' daily environmental experience.
    """)
    
    # City zones overview
    st.subheader("🏘️ City Zones & Characteristics")
    
    # Group zones by priority
    priority_groups = {}
    for zone_id, zone_info in CITY_ZONES.items():
        priority = zone_info['priority_level']
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append((zone_id, zone_info))
    
    priority_order = ['Emergency', 'Critical', 'High', 'Medium', 'Low']
    priority_colors = {
        'Emergency': '🔴', 'Critical': '🟠', 'High': '🟡', 'Medium': '🟢', 'Low': '⚪'
    }
    
    for priority in priority_order:
        if priority in priority_groups:
            st.markdown(f"### {priority_colors[priority]} {priority} Priority Zones")
            
            cols = st.columns(min(len(priority_groups[priority]), 3))
            for i, (zone_id, zone_info) in enumerate(priority_groups[priority]):
                with cols[i % 3]:
                    with st.expander(f"{zone_info['name']}"):
                        st.write(f"**Type:** {zone_info['type']}")
                        st.write(f"**Population:** {zone_info['characteristics']['population_density']:,}/hectare")
                        st.write(f"**Condition:** {zone_info['characteristics']['condition']}")
                        st.write(f"**Infrastructure:** {zone_info['characteristics']['infrastructure_quality']}")
                        st.write(f"**Plots:** {zone_info['plots']}")
    
    # Game mechanics
    st.subheader("🎮 Game Mechanics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Multi-Zone Selection:**
        - Select multiple zones per round for targeted interventions
        - Each zone can have different strategies and actions
        - Cross-zone synergies provide additional benefits
        - Spillover effects spread interventions across the city
        
        **⚙️ Effect Calculation:**
        - Direct effects: Immediate impact in target zones
        - Spillover effects: Delayed effects in connected zones (1-4 rounds)
        - Synergy effects: Bonus from coordinated multi-zone interventions
        - Cumulative effects: Building impact across multiple rounds
        """)
    
    with col2:
        st.markdown("""
        **📊 UEC Score (0-100 Scale):**
        - 0-15: Critical intervention needed
        - 15-30: Major improvements required
        - 30-45: Some improvements beneficial
        - 45-60: Good performance with growth potential
        - 60-75: Strong performance
        - 75-90: Excellent performance
        - 90-100: World-class urban sustainability
        
        **🔬 Scientific Evidence:**
        - Behavioral strategies have **8.2x higher leverage**
        - Pure Human-Social loops control 51.3% of system influence
        - Complex approaches are 5.8x less effective than focused ones
        """)
    
    # Progress tracking
    if st.session_state.team_name:
        st.subheader("🎯 Your Progress")
        
        effects = st.session_state.game_manager.calculate_round_effects()
        if effects:
            uec_data = calculate_normalized_uec_score(effects)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current UEC", f"{uec_data['overall_uec']:.1f}/100")
            with col2:
                st.metric("Zones Selected", len(st.session_state.game_manager.selected_zones))
            with col3:
                st.metric("Round", st.session_state.current_round)
            with col4:
                st.metric("Activated Loops", len(effects.get('activated_loops', [])))
                
            # Performance level
            interpretation = uec_data['interpretation']
            st.success(f"**Performance Level:** {interpretation['level']} - {interpretation['message']}")
        else:
            st.info("Configure zones and strategies to see your progress!")
    
    # Next steps
    st.subheader("🚀 Ready to Begin?")
    st.markdown("""
    1. 🗺️ **Go to City Map** - Select zones for intervention
    2. ⚙️ **Configure Strategies** - Choose evidence-based interventions
    3. ✨ **Create Custom Strategies** - Design your own interventions based on keywords
    4. 📊 **View Results** - See your UEC score and city transformation
    5. 🔬 **Analyze Science** - Understand the feedback loops you activated
    
    Remember: You're not just playing a game - you're applying cutting-edge urban science!
    """)

def city_map_page():
    st.header("🗺️ Interactive City Map & Zone Selection")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session in Team Setup first!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Select Zones for Intervention")
        
        # Create interactive zone grid
        st.markdown("Click the checkboxes to select zones for your intervention:")
        
        # Group zones by priority for better organization
        priority_groups = {}
        for zone_id, zone_info in CITY_ZONES.items():
            priority = zone_info['priority_level']
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append((zone_id, zone_info))
        
        priority_order = ['Emergency', 'Critical', 'High', 'Medium', 'Low']
        priority_colors = {
            'Emergency': '#FF0000', 'Critical': '#FF4500', 'High': '#FFA500', 
            'Medium': '#32CD32', 'Low': '#808080'
        }
        
        for priority in priority_order:
            if priority in priority_groups:
                with st.expander(f"📍 {priority} Priority Zones", expanded=(priority in ['Emergency', 'Critical'])):
                    for zone_id, zone_info in priority_groups[priority]:
                        # Create zone selection card
                        zone_col1, zone_col2 = st.columns([3, 1])
                        
                        with zone_col1:
                            st.markdown(f"""
                            **{zone_info['name']}** - {zone_info['type']}
                            - Population: {zone_info['characteristics']['population_density']:,}/hectare
                            - Condition: {zone_info['characteristics']['condition']}
                            - Infrastructure: {zone_info['characteristics']['infrastructure_quality']}
                            """)
                        
                        with zone_col2:
                            current_selection = zone_id in st.session_state.game_manager.selected_zones
                            selected = st.checkbox(
                                "Select", 
                                value=current_selection,
                                key=f"zone_select_{zone_id}",
                                help=f"Select {zone_info['name']} for intervention"
                            )
                            
                            # Update game manager
                            if selected and not current_selection:
                                st.session_state.game_manager.add_zone_selection(zone_id, [], [])
                                st.rerun()
                            elif not selected and current_selection:
                                del st.session_state.game_manager.selected_zones[zone_id]
                                st.rerun()
    
    with col2:
        st.subheader("📋 Selected Zones Summary")
        
        if st.session_state.game_manager.selected_zones:
            st.success(f"**{len(st.session_state.game_manager.selected_zones)} zones selected for Round {st.session_state.current_round}**")
            
            for zone_id in st.session_state.game_manager.selected_zones:
                zone_info = CITY_ZONES[zone_id]
                priority = zone_info['priority_level']
                
                # Display zone with priority color
                priority_emoji = {'Emergency': '🚨', 'Critical': '🔴', 'High': '🟡', 'Medium': '🟢', 'Low': '⚪'}
                st.write(f"{priority_emoji.get(priority, '📍')} **{zone_info['name']}** ({priority})")
            
            # Show configuration status
            st.subheader("⚙️ Configuration Status")
            configured_count = 0
            for zone_id, zone_data in st.session_state.game_manager.selected_zones.items():
                zone_name = CITY_ZONES[zone_id]['name']
                strategies = len(zone_data.get('strategies', []))
                actions = len(zone_data.get('actions', []))
                
                if strategies > 0 and actions > 0:
                    st.success(f"✅ {zone_name}: {strategies}S, {actions}A")
                    configured_count += 1
                else:
                    st.warning(f"⚠️ {zone_name}: Needs configuration")
            
            if configured_count == len(st.session_state.game_manager.selected_zones):
                st.success("🎉 All zones configured! Ready to calculate effects.")
            else:
                st.info(f"📝 Configure {len(st.session_state.game_manager.selected_zones) - configured_count} more zones")
        else:
            st.info("No zones selected yet")
            st.markdown("""
            **💡 Getting Started:**
            1. Select 1-2 **Emergency/Critical** priority zones first
            2. Focus on zones with high population density
            3. Choose adjacent zones for spillover effects
            4. Avoid selecting too many zones in your first round
            """)
        
        # City visualization
        st.subheader("🗺️ City Layout")
        
        # Create a simple city grid visualization
        fig = go.Figure()
        
        for zone_id, zone_info in CITY_ZONES.items():
            coords = zone_info['coordinates']
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            
            # Determine color based on selection and priority
            if zone_id in st.session_state.game_manager.selected_zones:
                color = '#FFD700'  # Gold for selected
                opacity = 0.8
            else:
                priority_colors_map = {
                    'Emergency': '#FF0000', 'Critical': '#FF4500', 'High': '#FFA500',
                    'Medium': '#32CD32', 'Low': '#808080'
                }
                color = priority_colors_map.get(zone_info['priority_level'], '#CCCCCC')
                opacity = 0.6
            
            # Add rectangle for zone
            fig.add_shape(
                type="rect",
                x0=x1, y0=y1, x1=x2, y1=y2,
                fillcolor=color,
                opacity=opacity,
                line=dict(color="black", width=2)
            )
            
            # Add zone label
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            fig.add_annotation(
                x=center_x, y=center_y,
                text=zone_info['name'].replace(' ', '<br>'),
                showarrow=False,
                font=dict(size=8, color="black"),
                bgcolor="white",
                bordercolor="black",
                borderwidth=1
            )
        
        fig.update_layout(
            title="City Zone Map",
            xaxis=dict(range=[0, 15], showgrid=True),
            yaxis=dict(range=[0, 12], showgrid=True),
            width=400,
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Legend
        st.markdown("""
        **Legend:**
        - 🟡 **Selected zones**
        - 🔴 Emergency priority
        - 🟠 Critical priority  
        - 🟡 High priority
        - 🟢 Medium priority
        - ⚪ Low priority
        """)

def zone_configuration_page():
    st.header("⚙️ Zone Configuration & Strategy Selection")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session in Team Setup first!")
        return
    
    if not st.session_state.game_manager.selected_zones:
        st.warning("📍 Please select zones in the City Map first!")
        return
    
    # Zone configuration tabs
    zone_names = [CITY_ZONES[zone_id]['name'] for zone_id in st.session_state.game_manager.selected_zones.keys()]
    zone_tabs = st.tabs(zone_names)
    
    for i, (zone_id, zone_tab) in enumerate(zip(st.session_state.game_manager.selected_zones.keys(), zone_tabs)):
        with zone_tab:
            configure_zone_detailed(zone_id)

def configure_zone_detailed(zone_id):
    zone_info = CITY_ZONES[zone_id]
    zone_data = st.session_state.game_manager.selected_zones[zone_id]
    
    st.subheader(f"🏘️ Configure {zone_info['name']}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Zone characteristics
        st.markdown("**📊 Zone Characteristics:**")
        st.info(f"""
        **Priority:** {zone_info['priority_level']}  
        **Type:** {zone_info['type']}  
        **Population:** {zone_info['characteristics']['population_density']:,}/hectare  
        **Condition:** {zone_info['characteristics']['condition']}  
        **Infrastructure:** {zone_info['characteristics']['infrastructure_quality']}  
        **Economic Activity:** {zone_info['characteristics']['economic_activity']}  
        **Plots:** {zone_info['plots']}
        """)
        
        # Strategy effectiveness preview
        st.markdown("**🎯 Strategy Effectiveness in This Zone:**")
        effectiveness_data = []
        for subsystem in ["Human-Social", "Spatial", "Air-Soundscape", "Thermal"]:
            multiplier = ZONE_STRATEGY_MULTIPLIERS.get(subsystem, {}).get(zone_id, 1.0)
            effectiveness_data.append({
                'Subsystem': subsystem,
                'Multiplier': f"{multiplier:.2f}x",
                'Effectiveness': 'High' if multiplier > 1.5 else 'Good' if multiplier > 1.0 else 'Moderate'
            })
        
        effectiveness_df = pd.DataFrame(effectiveness_data)
        st.dataframe(effectiveness_df, use_container_width=True)
        
        # Quick Custom Strategy Creator
        st.markdown("**✨ Create Custom Strategy for This Zone:**")
        with st.expander("🎯 Quick Strategy Creator", expanded=False):
            custom_strategy_name = st.text_input(
                "Strategy Name",
                placeholder=f"Custom strategy for {zone_info['name']}",
                key=f"custom_name_{zone_id}"
            )
            
            custom_description = st.text_area(
                "Strategy Description (use keywords)",
                placeholder="Describe your strategy using keywords like: community, engagement, green spaces, air quality, etc.",
                height=80,
                key=f"custom_desc_{zone_id}"
            )
            
            if st.button(f"✨ Create Strategy", key=f"create_custom_{zone_id}"):
                if custom_strategy_name and custom_description:
                    if custom_strategy_name not in st.session_state.custom_strategies:
                        # Create the custom strategy
                        custom_strategy = create_custom_strategy(custom_strategy_name, custom_description, zone_id)
                        st.success(f"✅ Custom strategy '{custom_strategy_name}' created!")
                        st.rerun()
                    else:
                        st.error(f"Strategy '{custom_strategy_name}' already exists!")
                else:
                    st.warning("Please fill in both name and description")
    
    with col2:
        # Strategy selection
        st.markdown("**🎯 Select Strategies:**")
        
        current_strategies = zone_data.get('strategies', [])
        
        # Create a mapping for strategy lookup
        strategy_lookup = {}
        strategy_options = []
        
        # Add predefined strategies
        for strategy in STRATEGIES:
            # Calculate effectiveness for this zone
            effectiveness = 1.0
            for subsystem in strategy['Subsystems']:
                multiplier = ZONE_STRATEGY_MULTIPLIERS.get(subsystem, {}).get(zone_id, 1.0)
                effectiveness *= multiplier
            
            avg_effectiveness = effectiveness ** (1.0 / len(strategy['Subsystems']))
            
            if avg_effectiveness > 1.5:
                indicator = "🔥 HIGH"
            elif avg_effectiveness > 1.0:
                indicator = "⚡ GOOD"
            else:
                indicator = "📊 MODERATE"
            
            display_name = f"{indicator} {strategy['Strategy']}"
            strategy_options.append(display_name)
            strategy_lookup[display_name] = strategy['Strategy']
        
        # Add custom strategies
        for custom_name, custom_strategy in st.session_state.custom_strategies.items():
            # Calculate effectiveness for this zone
            effectiveness = 1.0
            for subsystem in custom_strategy['Subsystems']:
                multiplier = ZONE_STRATEGY_MULTIPLIERS.get(subsystem, {}).get(zone_id, 1.0)
                effectiveness *= multiplier
            
            avg_effectiveness = effectiveness ** (1.0 / len(custom_strategy['Subsystems']))
            
            if avg_effectiveness > 1.5:
                indicator = "🔥 HIGH"
            elif avg_effectiveness > 1.0:
                indicator = "⚡ GOOD"
            else:
                indicator = "📊 MODERATE"
            
            display_name = f"{indicator} ✨ {custom_strategy['Strategy']}"
            strategy_options.append(display_name)
            strategy_lookup[display_name] = custom_strategy['Strategy']
        
        # Find currently selected options
        selected_display_names = []
        for strategy_name in current_strategies:
            for display_name, actual_name in strategy_lookup.items():
                if actual_name == strategy_name:
                    selected_display_names.append(display_name)
                    break
        
        selected_strategies_display = st.multiselect(
            "Choose strategies for this zone:",
            strategy_options,
            default=selected_display_names,
            key=f"strategies_{zone_id}",
            help="🔥 = High effectiveness, ⚡ = Good effectiveness, 📊 = Moderate effectiveness, ✨ = Custom strategy"
        )
        
        # Extract actual strategy names using lookup
        selected_strategies = []
        for display_name in selected_strategies_display:
            if display_name in strategy_lookup:
                selected_strategies.append(strategy_lookup[display_name])
        
        # Update zone data
        zone_data['strategies'] = selected_strategies
        
        # Action selection
        st.markdown("**⚙️ Select Actions:**")
        
        if selected_strategies:
            # Collect all available actions from selected strategies
            available_actions = []
            strategy_action_map = {}
            
            for strategy_name in selected_strategies:
                # Find strategy in predefined strategies
                strategy = None
                for strat_data in STRATEGIES:
                    if strat_data["Strategy"] == strategy_name:
                        strategy = strat_data
                        break
                
                # If not found, check custom strategies
                if strategy is None and strategy_name in st.session_state.custom_strategies:
                    strategy = st.session_state.custom_strategies[strategy_name]
                
                # Add actions if strategy found
                if strategy and "Actions" in strategy:
                    strategy_actions = strategy['Actions']
                    available_actions.extend(strategy_actions)
                    strategy_action_map[strategy_name] = strategy_actions
            
            # Remove duplicates while preserving order
            unique_actions = list(dict.fromkeys(available_actions))
            
            if unique_actions:
                current_actions = zone_data.get('actions', [])
                
                selected_actions = st.multiselect(
                    "Choose specific actions to implement:",
                    unique_actions,
                    default=[action for action in current_actions if action in unique_actions],
                    key=f"actions_{zone_id}",
                    help="Select specific actions that will be implemented in this zone"
                )
                
                zone_data['actions'] = selected_actions
            else:
                st.warning("No actions available for selected strategies")
                zone_data['actions'] = []
            
            # Show strategy details
            if selected_strategies:
                st.markdown("**📋 Selected Strategy Details:**")
                for strategy_name in selected_strategies:
                    # Find strategy details
                    strategy = None
                    
                    # Check predefined strategies
                    for strat_data in STRATEGIES:
                        if strat_data["Strategy"] == strategy_name:
                            strategy = strat_data
                            break
                    
                    # Check custom strategies
                    if strategy is None and strategy_name in st.session_state.custom_strategies:
                        strategy = st.session_state.custom_strategies[strategy_name]
                    
                    if strategy:
                        is_custom = strategy.get('Custom', False)
                        with st.expander(f"📖 {strategy_name} {'✨ (Custom)' if is_custom else ''}"):
                            st.write(f"**Subsystems:** {', '.join(strategy['Subsystems'])}")
                            st.write(f"**Loop Impact:** {strategy['Loop_Impact']}")
                            st.write(f"**Evidence Base:** {strategy['Evidence_Base']}")
                            if 'Description' in strategy:
                                st.write(f"**Description:** {strategy['Description']}")
                            if strategy_name in strategy_action_map:
                                st.write(f"**Available Actions:** {', '.join(strategy_action_map[strategy_name])}")
    
    # Configuration summary
    if zone_data.get('strategies') and zone_data.get('actions'):
        st.success(f"✅ Zone configured: {len(zone_data['strategies'])} strategies, {len(zone_data['actions'])} actions")
        
        # Show custom strategy count
        custom_count = sum(1 for strategy in zone_data['strategies'] if strategy in st.session_state.custom_strategies)
        if custom_count > 0:
            st.info(f"✨ {custom_count} custom strategies included")
        
        # Predict zone impact
        try:
            # Create temporary effects calculation
            temp_effects = st.session_state.game_manager.calculate_round_effects()
            if temp_effects and zone_id in temp_effects.get('zone_performance', {}):
                zone_performance = temp_effects['zone_performance'][zone_id]
                predicted_uec = zone_performance.get('uec_score', 0)
                
                st.info(f"🎯 **Predicted Zone UEC Score:** {predicted_uec:.2f}")
                
                if predicted_uec > 5.0:
                    st.success("🌟 Excellent predicted performance!")
                elif predicted_uec > 3.0:
                    st.warning("⚡ Good predicted performance")
                else:
                    st.warning("📈 Consider adding more behavioral strategies")
        except Exception:
            pass  # Skip prediction if calculation fails
    else:
        missing = []
        if not zone_data.get('strategies'):
            missing.append("strategies")
        if not zone_data.get('actions'):
            missing.append("actions")
        st.warning(f"⚠️ Please select {' and '.join(missing)}")
        
        # Show hint for creating custom strategies
        if not zone_data.get('strategies'):
            st.info("💡 **Tip:** You can create custom strategies tailored to this zone using the Quick Strategy Creator above!")

def custom_strategy_creator_page():
    st.header("✨ Custom Strategy Creator")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session first!")
        return
    
    st.markdown("""
    Create your own urban sustainability strategies based on keywords and evidence-based principles. 
    The system will automatically analyze your strategy description and suggest appropriate subsystems and actions.
    """)
    
    # Strategy creation form
    st.subheader("🎯 Create New Strategy")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        strategy_name = st.text_input(
            "Strategy Name",
            placeholder="e.g., Community-Led Green Infrastructure",
            help="Give your strategy a descriptive name"
        )
        
        strategy_description = st.text_area(
            "Strategy Description",
            placeholder="Describe your strategy using keywords like: community engagement, green spaces, social participation, thermal comfort, air quality, mobility, infrastructure, etc.",
            height=120,
            help="Use keywords related to urban systems. The AI will analyze your text to determine focus areas."
        )
        
        # Zone selection for strategy optimization
        if st.session_state.game_manager.selected_zones:
            target_zone = st.selectbox(
                "Optimize for Zone (optional)",
                ["Generic"] + [CITY_ZONES[zone_id]['name'] for zone_id in st.session_state.game_manager.selected_zones.keys()],
                help="Choose a specific zone to optimize this strategy for"
            )
        else:
            target_zone = "Generic"
            st.info("💡 Select zones in the City Map to optimize strategies for specific areas")
    
    with col2:
        st.markdown("**🔧 Strategy Building Tips:**")
        st.info("""
        **High-leverage keywords:**
        - 🎯 **Behavioral:** community, engagement, participation, social, cultural
        - 🏗️ **Spatial:** infrastructure, planning, development, connectivity
        - 🌬️ **Air/Sound:** air quality, noise, pollution, clean, quiet
        - 🌡️ **Thermal:** temperature, cooling, shading, comfort
        """)
        
        st.markdown("**📊 Keyword Analysis Preview:**")
        if strategy_description:
            # Real-time keyword analysis
            detected_subsystems = analyze_keywords_for_subsystem(strategy_description)
            suggested_actions = suggest_actions_from_keywords(strategy_description)
            
            st.success(f"**Detected Focus:** {', '.join(detected_subsystems)}")
            if suggested_actions:
                st.info(f"**Suggested Actions:** {len(suggested_actions)} actions detected")
        else:
            st.write("Type your description to see analysis...")
    
    # Create strategy button
    if st.button("🚀 Create Strategy", type="primary", disabled=not (strategy_name and strategy_description)):
        if strategy_name in st.session_state.custom_strategies:
            st.error(f"Strategy '{strategy_name}' already exists! Choose a different name.")
        else:
            # Find target zone ID
            target_zone_id = None
            if target_zone != "Generic":
                for zone_id, zone_info in CITY_ZONES.items():
                    if zone_info['name'] == target_zone:
                        target_zone_id = zone_id
                        break
            
            if target_zone_id is None:
                target_zone_id = list(CITY_ZONES.keys())[0]  # Default to first zone
            
            # Create the custom strategy
            custom_strategy = create_custom_strategy(strategy_name, strategy_description, target_zone_id)
            
            st.success(f"✅ Strategy '{strategy_name}' created successfully!")
            st.balloons()
            
            # Show created strategy details
            with st.expander(f"📖 View Created Strategy: {strategy_name}", expanded=True):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"""
                    **🎯 Strategy Details:**
                    - **Name:** {custom_strategy['Strategy']}
                    - **Subsystems:** {', '.join(custom_strategy['Subsystems'])}
                    - **Loop Impact:** {custom_strategy['Loop_Impact']}
                    - **Actions:** {len(custom_strategy['Actions'])}
                    """)
                
                with col_b:
                    st.markdown(f"""
                    **📊 System Analysis:**
                    - **Evidence Base:** {custom_strategy['Evidence_Base']}
                    - **Optimized For:** {custom_strategy['Created_For_Zone']}
                    - **Type:** Custom Strategy ✨
                    """)
                
                st.markdown(f"**📝 Description:** {custom_strategy['Description']}")
                st.markdown(f"**⚙️ Suggested Actions:** {', '.join(custom_strategy['Actions'])}")
    
    # Display existing custom strategies
    if st.session_state.custom_strategies:
        st.subheader("📚 Your Custom Strategies")
        
        for strategy_name, strategy_data in st.session_state.custom_strategies.items():
            with st.expander(f"✨ {strategy_name}"):
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    st.markdown(f"**Description:** {strategy_data['Description']}")
                    st.markdown(f"**Subsystems:** {', '.join(strategy_data['Subsystems'])}")
                    st.markdown(f"**Actions:** {', '.join(strategy_data['Actions'])}")
                
                with col_b:
                    st.markdown(f"""
                    **Impact:** {strategy_data['Loop_Impact']}  
                    **Zone:** {strategy_data['Created_For_Zone']}  
                    **Evidence:** {strategy_data['Evidence_Base'][:50]}...
                    """)
                
                with col_c:
                    if st.button(f"🗑️ Delete", key=f"delete_{strategy_name}"):
                        del st.session_state.custom_strategies[strategy_name]
                        st.rerun()
                    
                    # Usage statistics
                    usage_count = 0
                    for zone_data in st.session_state.game_manager.selected_zones.values():
                        if strategy_name in zone_data.get('strategies', []):
                            usage_count += 1
                    
                    st.metric("Zones Using", usage_count)
    
    else:
        st.info("🌱 No custom strategies created yet. Create your first strategy above!")
    
    # Keyword reference guide
    st.subheader("📖 Keyword Reference Guide")
    
    with st.expander("🎯 Complete Keyword Guide", expanded=False):
        for subsystem, keywords in STRATEGY_KEYWORDS.items():
            st.markdown(f"**{subsystem}:**")
            st.write(", ".join(keywords))
            st.write("")
        
        st.markdown("**💡 Pro Tips for Strategy Creation:**")
        st.markdown("""
        1. **Be specific:** Use concrete keywords rather than vague terms
        2. **Focus on behavior:** Include community/social keywords for 8.2x leverage
        3. **Mix subsystems:** Combine keywords from different areas for comprehensive strategies
        4. **Think local:** Consider the specific needs of your target zone
        5. **Evidence-based:** Use keywords that relate to proven urban interventions
        """)

def results_dashboard_page():
    st.header("📊 Game Results Dashboard")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session in Team Setup first!")
        return
    
    if not st.session_state.game_manager.selected_zones:
        st.warning("📍 Please select and configure zones first!")
        return
    
    # Calculate effects
    effects = st.session_state.game_manager.calculate_round_effects()
    
    if not effects:
        st.warning("⚙️ Please configure strategies and actions for your selected zones!")
        return
    
    # Calculate UEC score
    uec_data = calculate_normalized_uec_score(effects)
    overall_uec = uec_data['overall_uec']
    interpretation = uec_data['interpretation']
    
    # Main metrics dashboard
    st.subheader("🎯 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "UEC Score",
            f"{overall_uec:.1f}/100",
            help="Urban Environmental Comfort Score"
        )
    
    with col2:
        st.metric(
            "Performance Level", 
            interpretation['level'],
            help=interpretation['message']
        )
    
    with col3:
        st.metric(
            "Zones Configured",
            len(st.session_state.game_manager.selected_zones)
        )
    
    with col4:
        st.metric(
            "Activated Loops",
            len(effects.get('activated_loops', []))
        )
    
    # Performance visualization
    st.subheader("📈 Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # UEC Speedometer
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_uec,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "UEC Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': interpretation['color']},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 60], 'color': "yellow"},
                    {'range': [60, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300, title="Urban Environmental Comfort Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Subsystem breakdown
        subsystem_scores = uec_data['subsystem_scores']
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(subsystem_scores.keys()),
                y=list(subsystem_scores.values()),
                marker_color=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']
            )
        ])
        
        fig.update_layout(
            title="Subsystem Performance",
            yaxis_title="Score (0-100)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Zone performance comparison
    st.subheader("🏘️ Zone Performance Comparison")
    
    zone_performance = effects.get('zone_performance', {})
    if zone_performance:
        zone_data = []
        for zone_id, performance in zone_performance.items():
            zone_info = CITY_ZONES[zone_id]
            zone_data.append({
                'Zone': zone_info['name'],
                'UEC Score': performance.get('uec_score', 0),
                'Priority': zone_info['priority_level'],
                'Performance Level': performance.get('performance_level', 'Unknown')
            })
        
        zone_df = pd.DataFrame(zone_data)
        
        # Zone performance chart
        fig = px.bar(
            zone_df, 
            x='Zone', 
            y='UEC Score',
            color='Priority',
            title="Zone Performance by UEC Score",
            color_discrete_map={
                'Emergency': '#FF0000',
                'Critical': '#FF4500', 
                'High': '#FFA500',
                'Medium': '#32CD32',
                'Low': '#808080'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Zone performance table
        st.dataframe(zone_df, use_container_width=True)
    
    # Strategy usage analysis
    st.subheader("🎯 Strategy Usage Analysis")
    
    all_strategies = []
    custom_strategies_used = 0
    
    for zone_data in st.session_state.game_manager.selected_zones.values():
        strategies = zone_data.get('strategies', [])
        all_strategies.extend(strategies)
        
        for strategy in strategies:
            if strategy in st.session_state.custom_strategies:
                custom_strategies_used += 1
    
    unique_strategies = list(set(all_strategies))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Strategies Used", len(unique_strategies))
    with col2:
        st.metric("Custom Strategies", f"{custom_strategies_used}/{len(st.session_state.custom_strategies)}")
    with col3:
        predefined_used = len(unique_strategies) - custom_strategies_used
        st.metric("Predefined Strategies", f"{predefined_used}/{len(STRATEGIES)}")
    
    # Spillover effects preview
    st.subheader("🌊 Spillover Effects Preview")
    
    spillover_effects = effects.get('spillover_effects', {})
    if spillover_effects:
        spillover_count = len(spillover_effects)
        total_connections = sum(len(sources) for sources in spillover_effects.values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Zones Affected by Spillover", spillover_count)
        with col2:
            st.metric("Total Spillover Connections", total_connections)
        with col3:
            avg_spillover = np.mean([
                sum(spillover_data.get('effects', {}).values()) 
                for zone_spillovers in spillover_effects.values() 
                for spillover_data in zone_spillovers.values()
            ])
            st.metric("Average Spillover Strength", f"{avg_spillover:.2f}")
        
        st.info("📊 View detailed spillover analysis in the Spillover Analysis page")
    else:
        st.info("No spillover effects detected. Try selecting adjacent zones for spillover benefits!")
    
    # Scientific insights
    st.subheader("🔬 Scientific Insights")
    
    activated_loops = effects.get('activated_loops', [])
    if activated_loops:
        # Loop activation summary
        loop_roles = {}
        for loop in activated_loops:
            role = loop.get('role', 'Unknown')
            if role not in loop_roles:
                loop_roles[role] = 0
            loop_roles[role] += 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔄 Loop Activation by Role:**")
            for role, count in loop_roles.items():
                st.write(f"• {role}: {count} loops")
        
        with col2:
            total_leverage = sum(loop.get('leverage', 0) for loop in activated_loops)
            st.metric("Total System Leverage", f"{total_leverage:.3f}")
            
            behavioral_loops = [loop for loop in activated_loops if 'Human-Social' in str(loop)]
            if behavioral_loops:
                st.success("✅ Behavioral primacy applied!")
            else:
                st.warning("⚠️ Consider adding more behavioral strategies")
    
    # Recommendations
    st.subheader("💡 Strategic Recommendations")
    
    if overall_uec >= 80:
        st.success("🏆 **EXCEPTIONAL PERFORMANCE!** Your strategy is world-class. Consider scaling to other zones.")
    elif overall_uec >= 60:
        st.success("🚀 **EXCELLENT WORK!** Strong performance. Fine-tune and expand coverage.")
    elif overall_uec >= 40:
        st.warning("⚡ **GOOD PROGRESS!** Solid foundation. Focus more on behavioral strategies for higher impact.")
    elif overall_uec >= 20:
        st.warning("📈 **DEVELOPING!** Some improvement visible. Apply behavioral primacy principle (70% resources to Human-Social).")
    else:
        st.error("🔄 **NEEDS PIVOT!** Shift to Pure Human-Social strategies for 8.2x leverage advantage.")
    
    # Custom strategy recommendation
    if len(st.session_state.custom_strategies) < 2:
        st.info("💡 **Try creating custom strategies** in the Custom Strategy Creator for more targeted interventions!")

def spillover_analysis_page():
    st.header("🌊 Spillover Effects Analysis")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session first!")
        return
    
    effects = st.session_state.game_manager.calculate_round_effects()
    
    if not effects:
        st.warning("⚙️ Configure zones first to see spillover effects!")
        return
    
    spillover_effects = effects.get('spillover_effects', {})
    
    if not spillover_effects:
        st.info("🌊 No spillover effects detected yet.")
        st.markdown("""
        **💡 To create spillover effects:**
        - Select **adjacent zones** for stronger connections
        - Use **high-intensity** interventions
        - Focus on **behavioral strategies** (8.2x leverage)
        - Target **Emergency/Critical** priority zones
        """)
        return
    
    # Spillover network visualization
    st.subheader("🕸️ Spillover Network Visualization")
    
    # Create network graph
    G = nx.Graph()
    
    # Add all zones as nodes
    for zone_id in CITY_ZONES.keys():
        G.add_node(zone_id)
    
    # Add spillover edges
    edge_data = []
    for target_zone, source_effects in spillover_effects.items():
        for source_zone, spillover_data in source_effects.items():
            effects_dict = spillover_data.get('effects', {})
            avg_effect = np.mean(list(effects_dict.values())) if effects_dict else 0
            
            if avg_effect > 0.1:
                G.add_edge(source_zone, target_zone, weight=avg_effect)
                edge_data.append({
                    'Source': CITY_ZONES[source_zone]['name'],
                    'Target': CITY_ZONES[target_zone]['name'],
                    'Effect Strength': avg_effect,
                    'Distance': spillover_data.get('distance', 0),
                    'Delay': spillover_data.get('delay_rounds', 0)
                })
    
    # Create network visualization
    if edge_data:
        pos = nx.spring_layout(G, k=3, iterations=100)
        
        # Create plotly network
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = []
        node_y = []
        node_info = []
        node_colors = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            zone_info = CITY_ZONES[node]
            if node in st.session_state.game_manager.selected_zones:
                node_colors.append('#FFD700')  # Gold for source zones
                info = f"🎯 SOURCE: {zone_info['name']}<br>Priority: {zone_info['priority_level']}<br>Type: Intervention Zone"
            elif node in spillover_effects:
                node_colors.append('#FF9999')  # Light red for spillover targets
                info = f"🌊 SPILLOVER: {zone_info['name']}<br>Priority: {zone_info['priority_level']}<br>Type: Affected by spillover"
            else:
                node_colors.append('#CCCCCC')  # Gray for unaffected
                info = f"⚪ UNAFFECTED: {zone_info['name']}<br>Priority: {zone_info['priority_level']}<br>Type: No effects"
            
            node_info.append(info)
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='red'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[CITY_ZONES[node]['name'][:8] for node in G.nodes()],
            hovertext=node_info,
            textposition="middle center",
            marker=dict(
                size=20,
                color=node_colors,
                line=dict(width=2, color='black')
            )
        ))
        
        fig.update_layout(
            title="Spillover Network Map",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="🎯 Gold = Source zones, 🌊 Red = Spillover zones, ⚪ Gray = Unaffected",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor="left", yanchor="bottom",
                    font=dict(size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Spillover statistics
    st.subheader("📊 Spillover Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Zones Receiving Spillover", len(spillover_effects))
    
    with col2:
        total_connections = sum(len(sources) for sources in spillover_effects.values())
        st.metric("Total Connections", total_connections)
    
    with col3:
        if edge_data:
            avg_strength = np.mean([e['Effect Strength'] for e in edge_data])
            st.metric("Average Effect Strength", f"{avg_strength:.2f}")
    
    with col4:
        if edge_data:
            avg_delay = np.mean([e['Delay'] for e in edge_data])
            st.metric("Average Delay", f"{avg_delay:.1f} rounds")
    
    # Detailed spillover table
    st.subheader("📋 Detailed Spillover Effects")
    
    if edge_data:
        spillover_df = pd.DataFrame(edge_data)
        spillover_df = spillover_df.sort_values('Effect Strength', ascending=False)
        
        # Color code by strength
        def style_spillover(val):
            if val > 3.0:
                return 'background-color: #ffcccc'  # Strong
            elif val > 1.5:
                return 'background-color: #fff2cc'  # Medium
            else:
                return 'background-color: #f0f0f0'  # Weak
        
        styled_df = spillover_df.style.applymap(style_spillover, subset=['Effect Strength'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Spillover effectiveness analysis
        st.subheader("🎯 Spillover Effectiveness Analysis")
        
        strong_spillovers = len([e for e in edge_data if e['Effect Strength'] > 3.0])
        medium_spillovers = len([e for e in edge_data if 1.5 <= e['Effect Strength'] <= 3.0])
        weak_spillovers = len([e for e in edge_data if e['Effect Strength'] < 1.5])
        
        effectiveness_data = {
            'Strength Category': ['Strong (>3.0)', 'Medium (1.5-3.0)', 'Weak (<1.5)'],
            'Count': [strong_spillovers, medium_spillovers, weak_spillovers],
            'Percentage': [
                strong_spillovers/len(edge_data)*100,
                medium_spillovers/len(edge_data)*100,
                weak_spillovers/len(edge_data)*100
            ]
        }
        
        effectiveness_df = pd.DataFrame(effectiveness_data)
        
        fig = px.pie(
            effectiveness_df, 
            values='Count', 
            names='Strength Category',
            title="Spillover Effect Distribution",
            color_discrete_map={
                'Strong (>3.0)': '#FF6B6B',
                'Medium (1.5-3.0)': '#FFE66D', 
                'Weak (<1.5)': '#95E1D3'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)

def loop_analysis_page():
    st.header("🔬 Scientific Loop Analysis")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session first!")
        return
    
    effects = st.session_state.game_manager.calculate_round_effects()
    
    if not effects:
        st.warning("⚙️ Configure zones first to see loop activation!")
        return
    
    activated_loops = effects.get('activated_loops', [])
    
    if not activated_loops:
        st.info("🔄 No loops activated yet. Configure strategies to activate the 113-loop system!")
        return
    
    # Loop activation overview
    st.subheader("🎯 Loop Activation Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Loops Activated", f"{len(activated_loops)}/113")
    
    with col2:
        activation_rate = len(activated_loops) / 113 * 100
        st.metric("Activation Rate", f"{activation_rate:.1f}%")
    
    with col3:
        total_leverage = sum(loop.get('leverage', 0) for loop in activated_loops)
        st.metric("Total System Leverage", f"{total_leverage:.3f}")
    
    with col4:
        avg_leverage = total_leverage / len(activated_loops) if activated_loops else 0
        st.metric("Average Loop Leverage", f"{avg_leverage:.3f}")
    
    # Loop distribution by role
    st.subheader("📊 Loop Distribution by Role")
    
    loop_roles = {}
    loop_leverage_by_role = {}
    
    for loop in activated_loops:
        role = loop.get('role', 'Unknown')
        leverage = loop.get('leverage', 0)
        
        if role not in loop_roles:
            loop_roles[role] = 0
            loop_leverage_by_role[role] = 0
        
        loop_roles[role] += 1
        loop_leverage_by_role[role] += leverage
    
    role_data = []
    for role, count in loop_roles.items():
        role_data.append({
            'Role': role,
            'Count': count,
            'Total Leverage': loop_leverage_by_role[role],
            'Average Leverage': loop_leverage_by_role[role] / count
        })
    
    role_df = pd.DataFrame(role_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            role_df, 
            values='Count', 
            names='Role',
            title="Loop Count by Role"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            role_df,
            x='Role',
            y='Total Leverage',
            title="Total Leverage by Role"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Scientific insights
    st.subheader("🧠 Scientific Insights")
    
    # Behavioral primacy analysis
    behavioral_loops = [loop for loop in activated_loops if 'Human-Social' in SCIENTIFIC_LOOP_DATA.get(loop.get('loop_id', 0), {}).get('subsystems', [])]
    behavioral_leverage = sum(loop.get('leverage', 0) for loop in behavioral_loops)
    total_leverage = sum(loop.get('leverage', 0) for loop in activated_loops)
    
    if total_leverage > 0:
        behavioral_percentage = behavioral_leverage / total_leverage * 100
    else:
        behavioral_percentage = 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Behavioral Loops", len(behavioral_loops))
        if len(behavioral_loops) > len(activated_loops) * 0.5:
            st.success("✅ Strong behavioral focus!")
        else:
            st.warning("⚠️ Consider more behavioral strategies")
    
    with col2:
        st.metric("Behavioral Leverage", f"{behavioral_leverage:.3f}")
        if behavioral_percentage > 60:
            st.success("✅ Optimal behavioral leverage!")
        else:
            st.warning(f"📈 Only {behavioral_percentage:.1f}% behavioral")
    
    with col3:
        st.metric("Leverage Efficiency", f"{behavioral_percentage:.1f}%")
        if behavioral_percentage > 70:
            st.success("🔥 Applying behavioral primacy!")
        else:
            st.info("💡 Focus more on Human-Social strategies")

def multi_round_comparison_page():
    st.header("📈 Multi-Round Comparison Analysis")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session first!")
        return
    
    # Store current round data
    current_effects = st.session_state.game_manager.calculate_round_effects()
    current_round = st.session_state.current_round
    
    if current_effects and current_round not in st.session_state.game_manager.round_history:
        st.session_state.game_manager.round_history[current_round] = {
            'effects': current_effects,
            'zones': copy.deepcopy(st.session_state.game_manager.selected_zones),
            'timestamp': datetime.now().isoformat()
        }
    
    # Round selector
    st.subheader("🎯 Round Selection & Comparison")
    
    available_rounds = list(st.session_state.game_manager.round_history.keys())
    if current_effects:
        available_rounds.append(current_round)
    
    if len(available_rounds) < 2:
        st.info("🎮 Play multiple rounds to see comparison analysis!")
        st.markdown("""
        **💡 Multi-Round Strategy Tips:**
        - **Round 1:** Focus on highest priority zones (Emergency/Critical)
        - **Round 2:** Expand to adjacent zones for spillover effects
        - **Round 3:** Target remaining high-impact zones
        - **Round 4:** Fine-tune and optimize citywide coverage
        """)
        
        if current_effects:
            st.subheader("📊 Current Round Performance")
            uec_data = calculate_normalized_uec_score(current_effects)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("UEC Score", f"{uec_data['overall_uec']:.1f}/100")
            with col2:
                st.metric("Zones", len(st.session_state.game_manager.selected_zones))
            with col3:
                st.metric("Loops", len(current_effects.get('activated_loops', [])))
        return
    
    st.info("📊 Multi-round comparison available! Select rounds to compare above.")

def multi_round_comparison_page():
    st.header("📈 Multi-Round Comparison Analysis")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session first!")
        return
    
    # Store current round data
    current_effects = st.session_state.game_manager.calculate_round_effects()
    current_round = st.session_state.current_round
    
    if current_effects and current_round not in st.session_state.game_manager.round_history:
        st.session_state.game_manager.round_history[current_round] = {
            'effects': current_effects,
            'zones': copy.deepcopy(st.session_state.game_manager.selected_zones),
            'timestamp': datetime.now().isoformat()
        }
    
    # Round selector
    st.subheader("🎯 Round Selection & Comparison")
    
    available_rounds = list(st.session_state.game_manager.round_history.keys())
    if current_effects:
        available_rounds.append(current_round)
    
    if len(available_rounds) < 2:
        st.info("🎮 Play multiple rounds to see comparison analysis!")
        st.markdown("""
        **💡 Multi-Round Strategy Tips:**
        - **Round 1:** Focus on highest priority zones (Emergency/Critical)
        - **Round 2:** Expand to adjacent zones for spillover effects
        - **Round 3:** Target remaining high-impact zones
        - **Round 4:** Fine-tune and optimize citywide coverage
        """)
        
        if current_effects:
            st.subheader("📊 Current Round Performance")
            uec_data = calculate_normalized_uec_score(current_effects)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("UEC Score", f"{uec_data['overall_uec']:.1f}/100")
            with col2:
                st.metric("Zones", len(st.session_state.game_manager.selected_zones))
            with col3:
                st.metric("Loops", len(current_effects.get('activated_loops', [])))
        return
    
    # Round comparison controls
    col1, col2 = st.columns(2)
    
    with col1:
        compare_rounds = st.multiselect(
            "Select rounds to compare:",
            available_rounds,
            default=available_rounds[-2:] if len(available_rounds) >= 2 else available_rounds,
            help="Select 2-4 rounds for comparison"
        )
    
    with col2:
        if st.button("💾 Save Current Round"):
            if current_effects:
                st.session_state.game_manager.round_history[current_round] = {
                    'effects': current_effects,
                    'zones': copy.deepcopy(st.session_state.game_manager.selected_zones),
                    'timestamp': datetime.now().isoformat()
                }
                st.success(f"✅ Round {current_round} saved!")
                st.rerun()
    
    if not compare_rounds:
        st.warning("Please select rounds to compare")
        return
    
    # Performance comparison
    st.subheader("📊 Performance Comparison")
    
    comparison_data = []
    
    for round_num in compare_rounds:
        if round_num == current_round and current_effects:
            effects = current_effects
            zones = st.session_state.game_manager.selected_zones
        elif round_num in st.session_state.game_manager.round_history:
            round_data = st.session_state.game_manager.round_history[round_num]
            effects = round_data['effects']
            zones = round_data['zones']
        else:
            continue
        
        uec_data = calculate_normalized_uec_score(effects)
        
        comparison_data.append({
            'Round': f"Round {round_num}",
            'UEC Score': uec_data['overall_uec'],
            'Zones': len(zones),
            'Activated Loops': len(effects.get('activated_loops', [])),
            'Total Leverage': sum(loop.get('leverage', 0) for loop in effects.get('activated_loops', [])),
            'Human-Social': uec_data['subsystem_scores'].get('Human-Social', 0),
            'Spatial': uec_data['subsystem_scores'].get('Spatial', 0),
            'Air-Soundscape': uec_data['subsystem_scores'].get('Air-Soundscape', 0),
            'Thermal': uec_data['subsystem_scores'].get('Thermal', 0),
            'Performance Level': uec_data['interpretation']['level']
        })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        
        # UEC Score progression
        fig = px.line(
            comparison_df,
            x='Round',
            y='UEC Score',
            title="UEC Score Progression",
            markers=True,
            line_shape='linear'
        )
        fig.update_layout(yaxis_title="UEC Score (0-100)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Subsystem comparison
        subsystem_cols = ['Human-Social', 'Spatial', 'Air-Soundscape', 'Thermal']
        subsystem_df = comparison_df[['Round'] + subsystem_cols].melt(
            id_vars=['Round'], 
            var_name='Subsystem', 
            value_name='Score'
        )
        
        fig = px.bar(
            subsystem_df,
            x='Round',
            y='Score',
            color='Subsystem',
            title="Subsystem Performance by Round",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("📋 Detailed Round Comparison")
        
        # Style the dataframe for better visualization
        def style_uec_score(val):
            if val >= 80:
                return 'background-color: #90EE90'  # Light green
            elif val >= 60:
                return 'background-color: #FFFFE0'  # Light yellow
            elif val >= 40:
                return 'background-color: #FFE4B5'  # Light orange
            else:
                return 'background-color: #FFB6C1'  # Light red
        
        styled_df = comparison_df.style.applymap(style_uec_score, subset=['UEC Score'])
        st.dataframe(styled_df, use_container_width=True)

def reports_export_page():
    st.header("📋 Reports & Export Center")
    
    if not st.session_state.team_name:
        st.warning("⚠️ Please start a game session first!")
        return
    
    # Current session summary
    st.subheader("📊 Current Session Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **🎮 Game Session Information:**
        - **Team:** {st.session_state.team_name}
        - **Game:** {st.session_state.game_name}
        - **Current Round:** {st.session_state.current_round}
        - **Zones Selected:** {len(st.session_state.game_manager.selected_zones)}
        - **Custom Strategies:** {len(st.session_state.custom_strategies)}
        """)
    
    with col2:
        current_effects = st.session_state.game_manager.calculate_round_effects()
        if current_effects:
            uec_data = calculate_normalized_uec_score(current_effects)
            st.markdown(f"""
            **📈 Performance Metrics:**
            - **UEC Score:** {uec_data['overall_uec']:.1f}/100
            - **Performance Level:** {uec_data['interpretation']['level']}
            - **Activated Loops:** {len(current_effects.get('activated_loops', []))}
            - **Spillover Zones:** {len(current_effects.get('spillover_effects', {}))}
            """)
        else:
            st.info("Configure strategies to see performance metrics")
    
    # Report generation options
    st.subheader("📝 Report Generation")
    
    report_type = st.selectbox(
        "Choose report type:",
        [
            "📊 Executive Summary",
            "🔬 Scientific Analysis Report", 
            "🌊 Spillover Effects Report",
            "📈 Multi-Round Comparison",
            "🎯 Strategy Implementation Guide",
            "📋 Complete Game Report"
        ]
    )
    
    # Generate selected report
    if st.button("📋 Generate Report", type="primary"):
        report_content = generate_report(report_type, current_effects)
        
        if report_content:
            st.subheader("📄 Generated Report")
            
            # Display report
            st.markdown(report_content, unsafe_allow_html=True)
            
            # Download button
            report_filename = f"{st.session_state.team_name}_{report_type.split(' ')[-1]}_Round_{st.session_state.current_round}.md"
            
            st.download_button(
                label="💾 Download Report",
                data=report_content,
                file_name=report_filename,
                mime="text/markdown"
            )
    
    # Data export options
    st.subheader("💾 Data Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Current Results"):
            if current_effects:
                export_data = {
                    'team': st.session_state.team_name,
                    'round': st.session_state.current_round,
                    'zones': st.session_state.game_manager.selected_zones,
                    'custom_strategies': st.session_state.custom_strategies,
                    'effects': current_effects,
                    'timestamp': datetime.now().isoformat()
                }
                
                json_data = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name=f"{st.session_state.team_name}_Round_{st.session_state.current_round}.json",
                    mime="application/json"
                )
            else:
                st.warning("No data to export")
    
    with col2:
        if st.button("📈 Export All Rounds"):
            if st.session_state.game_manager.round_history:
                all_rounds_data = {
                    'team': st.session_state.team_name,
                    'game': st.session_state.game_name,
                    'rounds': st.session_state.game_manager.round_history,
                    'current_round': st.session_state.current_round,
                    'custom_strategies': st.session_state.custom_strategies,
                    'export_timestamp': datetime.now().isoformat()
                }
                
                json_data = json.dumps(all_rounds_data, indent=2, default=str)
                
                st.download_button(
                    label="💾 Download All Rounds",
                    data=json_data,
                    file_name=f"{st.session_state.team_name}_AllRounds.json",
                    mime="application/json"
                )
            else:
                st.warning("No round history to export")
    
    with col3:
        if st.button("📋 Export Strategy Summary"):
            strategy_summary = generate_strategy_summary()
            
            st.download_button(
                label="💾 Download Strategy CSV",
                data=strategy_summary,
                file_name=f"{st.session_state.team_name}_Strategies.csv",
                mime="text/csv"
            )
    
    # Workshop submission
    st.subheader("🎓 Workshop Submission")
    
    if current_effects:
        uec_data = calculate_normalized_uec_score(current_effects)
        
        submission_data = {
            "team_name": st.session_state.team_name,
            "final_uec_score": round(uec_data['overall_uec'], 2),
            "performance_level": uec_data['interpretation']['level'],
            "zones_used": len(st.session_state.game_manager.selected_zones),
            "strategies_implemented": len(set(
                strategy 
                for zone_data in st.session_state.game_manager.selected_zones.values() 
                for strategy in zone_data.get('strategies', [])
            )),
            "custom_strategies_created": len(st.session_state.custom_strategies),
            "activated_loops": len(current_effects.get('activated_loops', [])),
            "submission_timestamp": datetime.now().isoformat()
        }
        
        st.json(submission_data)
        
        # Achievement badges
        st.subheader("🏆 Achievement Badges")
        
        achievements = []
        
        if uec_data['overall_uec'] >= 90:
            achievements.append("🏆 **URBAN MASTER** - UEC Score 90+")
        elif uec_data['overall_uec'] >= 80:
            achievements.append("🚀 **EXPERT PLANNER** - UEC Score 80+")
        elif uec_data['overall_uec'] >= 65:
            achievements.append("⭐ **SKILLED STRATEGIST** - UEC Score 65+")
        elif uec_data['overall_uec'] >= 50:
            achievements.append("📈 **RISING PLANNER** - UEC Score 50+")
        
        if len(current_effects.get('activated_loops', [])) >= 20:
            achievements.append("🔄 **LOOP MASTER** - 20+ Activated Loops")
        
        if len(st.session_state.custom_strategies) >= 3:
            achievements.append("✨ **STRATEGY INNOVATOR** - 3+ Custom Strategies")
        
        behavioral_loops = [
            loop for loop in current_effects.get('activated_loops', []) 
            if 'Human-Social' in SCIENTIFIC_LOOP_DATA.get(loop.get('loop_id', 0), {}).get('subsystems', [])
        ]
        if len(behavioral_loops) >= 10:
            achievements.append("🎯 **BEHAVIORAL CHAMPION** - 10+ Behavioral Loops")
        
        if len(current_effects.get('spillover_effects', {})) >= 5:
            achievements.append("🌊 **SPILLOVER SPECIALIST** - 5+ Spillover Zones")
        
        if achievements:
            for achievement in achievements:
                st.success(achievement)
        else:
            st.info("🌱 Keep playing to unlock achievement badges!")

def generate_report(report_type, effects):
    """Generate different types of reports"""
    
    if not effects:
        return "No data available for report generation."
    
    uec_data = calculate_normalized_uec_score(effects)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if "Executive Summary" in report_type:
        return f"""
# Executive Summary - Urban Pulse Analysis

**Team:** {st.session_state.team_name}  
**Generated:** {timestamp}  
**Round:** {st.session_state.current_round}

## 🎯 Key Performance Indicators

- **Overall UEC Score:** {uec_data['overall_uec']:.1f}/100
- **Performance Level:** {uec_data['interpretation']['level']}
- **Zones Intervened:** {len(st.session_state.game_manager.selected_zones)}
- **Feedback Loops Activated:** {len(effects.get('activated_loops', []))}
- **Custom Strategies Created:** {len(st.session_state.custom_strategies)}

## 📊 Subsystem Performance

| Subsystem | Score | Performance |
|-----------|-------|-------------|
| Human-Social | {uec_data['subsystem_scores'].get('Human-Social', 0):.1f} | {'Excellent' if uec_data['subsystem_scores'].get('Human-Social', 0) > 70 else 'Good' if uec_data['subsystem_scores'].get('Human-Social', 0) > 50 else 'Needs Improvement'} |
| Spatial | {uec_data['subsystem_scores'].get('Spatial', 0):.1f} | {'Excellent' if uec_data['subsystem_scores'].get('Spatial', 0) > 70 else 'Good' if uec_data['subsystem_scores'].get('Spatial', 0) > 50 else 'Needs Improvement'} |
| Air-Soundscape | {uec_data['subsystem_scores'].get('Air-Soundscape', 0):.1f} | {'Excellent' if uec_data['subsystem_scores'].get('Air-Soundscape', 0) > 70 else 'Good' if uec_data['subsystem_scores'].get('Air-Soundscape', 0) > 50 else 'Needs Improvement'} |
| Thermal | {uec_data['subsystem_scores'].get('Thermal', 0):.1f} | {'Excellent' if uec_data['subsystem_scores'].get('Thermal', 0) > 70 else 'Good' if uec_data['subsystem_scores'].get('Thermal', 0) > 50 else 'Needs Improvement'} |

## 🎯 Strategic Recommendations

{get_strategic_recommendations(uec_data, effects)}

## ✨ Innovation Summary

**Custom Strategies Developed:** {len(st.session_state.custom_strategies)}
{chr(10).join([f"- {name}: {strategy.get('Description', 'No description')[:100]}..." for name, strategy in st.session_state.custom_strategies.items()])}

## 📈 Next Steps

1. **Focus Areas:** {'Behavioral strategies for higher leverage' if uec_data['subsystem_scores'].get('Human-Social', 0) < 60 else 'Expand to adjacent zones for spillover effects'}
2. **Optimization:** {'Reduce zone count and focus interventions' if len(st.session_state.game_manager.selected_zones) > 5 else 'Consider adding complementary zones'}
3. **Innovation:** {'Create more targeted custom strategies' if len(st.session_state.custom_strategies) < 3 else 'Refine existing custom strategies for maximum impact'}
"""
    
    elif "Scientific Analysis" in report_type:
        activated_loops = effects.get('activated_loops', [])
        total_leverage = sum(loop.get('leverage', 0) for loop in activated_loops)
        
        return f"""
# Scientific Analysis Report - Urban Pulse

**Team:** {st.session_state.team_name}  
**Generated:** {timestamp}  
**Round:** {st.session_state.current_round}

## 🔬 Loop System Analysis

### Activation Summary
- **Total Loops Activated:** {len(activated_loops)}/113 ({len(activated_loops)/113*100:.1f}%)
- **Total System Leverage:** {total_leverage:.3f}
- **Average Loop Leverage:** {total_leverage/len(activated_loops) if activated_loops else 0:.3f}

### Custom Strategy Innovation
**Strategies Created:** {len(st.session_state.custom_strategies)}
{chr(10).join([f"- **{name}:** {strategy.get('Evidence_Base', 'Custom evidence-based strategy')}" for name, strategy in st.session_state.custom_strategies.items()])}

### Behavioral Primacy Analysis
{get_behavioral_primacy_analysis(activated_loops)}

## 📊 Evidence-Based Insights

### Leverage Optimization
The scientific evidence shows that Pure Human-Social loops provide 8.2x higher leverage than complex multi-subsystem approaches. Your current strategy {'aligns well' if sum(1 for loop in activated_loops if 'Human-Social' in SCIENTIFIC_LOOP_DATA.get(loop.get('loop_id', 0), {}).get('subsystems', [])) > len(activated_loops)*0.6 else 'could better utilize'} this principle.

### Innovation Impact
Your {len(st.session_state.custom_strategies)} custom strategies demonstrate {'excellent' if len(st.session_state.custom_strategies) >= 3 else 'good' if len(st.session_state.custom_strategies) >= 1 else 'limited'} innovation in urban sustainability approaches.

## 🎯 Scientific Recommendations

{get_scientific_recommendations(activated_loops, uec_data)}
"""
    
    else:  # Complete Game Report
        return f"""
# Complete Urban Pulse Game Report

**Team:** {st.session_state.team_name}  
**Game:** {st.session_state.game_name}  
**Generated:** {timestamp}  
**Round:** {st.session_state.current_round}

## 🎮 Game Session Overview

### Performance Summary
- **Final UEC Score:** {uec_data['overall_uec']:.1f}/100
- **Achievement Level:** {uec_data['interpretation']['level']}
- **Message:** {uec_data['interpretation']['message']}

### Innovation Summary
- **Custom Strategies Created:** {len(st.session_state.custom_strategies)}
- **Total Unique Strategies Used:** {len(set(strategy for zone_data in st.session_state.game_manager.selected_zones.values() for strategy in zone_data.get('strategies', [])))}

### Zone Configuration
{get_zone_configuration_summary()}

## 📊 Detailed Analysis

### Custom Strategy Analysis
{get_custom_strategy_analysis()}

### Subsystem Performance
{get_subsystem_detailed_analysis(uec_data)}

### Scientific Loop Activation
{get_complete_loop_analysis(effects)}

## 🏆 Achievement Summary

{get_achievement_summary(uec_data, effects)}

## 📈 Learning Outcomes

Based on your gameplay, key learning outcomes include:
{get_learning_outcomes(uec_data, effects)}

## 🎯 Future Applications

{get_future_applications_guide(uec_data)}
"""

def get_strategic_recommendations(uec_data, effects):
    """Generate strategic recommendations based on performance"""
    recommendations = []
    
    if uec_data['overall_uec'] < 40:
        recommendations.append("• **Priority:** Shift to Pure Human-Social strategies for maximum leverage")
        recommendations.append("• **Focus:** Implement Behavioral Activation Programs in Emergency zones")
        recommendations.append("• **Innovation:** Create custom strategies focusing on community engagement keywords")
    elif uec_data['overall_uec'] < 70:
        recommendations.append("• **Expand:** Add adjacent zones for spillover network effects")
        recommendations.append("• **Intensify:** Increase action count in current zones")
        recommendations.append("• **Customize:** Develop zone-specific strategies using the Custom Strategy Creator")
    else:
        recommendations.append("• **Scale:** Consider city-wide implementation strategy")
        recommendations.append("• **Optimize:** Fine-tune existing interventions")
        recommendations.append("• **Share:** Your custom strategies could serve as templates for other teams")
    
    return "\n".join(recommendations) if recommendations else "• Continue current successful strategy"

def get_behavioral_primacy_analysis(activated_loops):
    """Analyze behavioral primacy in loop activation"""
    behavioral_loops = [
        loop for loop in activated_loops 
        if 'Human-Social' in SCIENTIFIC_LOOP_DATA.get(loop.get('loop_id', 0), {}).get('subsystems', [])
    ]
    
    behavioral_leverage = sum(loop.get('leverage', 0) for loop in behavioral_loops)
    total_leverage = sum(loop.get('leverage', 0) for loop in activated_loops)
    
    if total_leverage > 0:
        percentage = behavioral_leverage / total_leverage * 100
        return f"""
**Behavioral Loop Count:** {len(behavioral_loops)}/{len(activated_loops)} ({len(behavioral_loops)/len(activated_loops)*100:.1f}%)
**Behavioral Leverage Share:** {percentage:.1f}%
**Alignment with Science:** {'Excellent' if percentage > 70 else 'Good' if percentage > 50 else 'Needs Improvement'}
"""
    else:
        return "No leverage data available"

def get_scientific_recommendations(activated_loops, uec_data):
    """Generate science-based recommendations"""
    recommendations = []
    
    # Check behavioral primacy
    behavioral_loops = [
        loop for loop in activated_loops 
        if 'Human-Social' in SCIENTIFIC_LOOP_DATA.get(loop.get('loop_id', 0), {}).get('subsystems', [])
    ]
    
    if len(behavioral_loops) < len(activated_loops) * 0.6:
        recommendations.append("1. **Increase behavioral focus:** Target 70% of strategies on Human-Social interventions")
        recommendations.append("2. **Create custom behavioral strategies:** Use keywords like 'community', 'engagement', 'participation'")
    
    # Check innovation
    if len(st.session_state.custom_strategies) < 2:
        recommendations.append("3. **Boost innovation:** Create custom strategies tailored to your specific zones")
    
    # Check leverage optimization
    avg_leverage = sum(loop.get('leverage', 0) for loop in activated_loops) / len(activated_loops) if activated_loops else 0
    if avg_leverage < 0.8:
        recommendations.append("4. **Optimize leverage:** Choose strategies that activate high-leverage loops")
    
    return "\n".join(recommendations) if recommendations else "Current strategy is scientifically sound and innovative"

def get_zone_configuration_summary():
    """Generate zone configuration summary"""
    summary = []
    
    for zone_id, zone_data in st.session_state.game_manager.selected_zones.items():
        zone_info = CITY_ZONES[zone_id]
        strategies = zone_data.get('strategies', [])
        actions = zone_data.get('actions', [])
        
        custom_strategies = [s for s in strategies if s in st.session_state.custom_strategies]
        
        summary.append(f"""
**{zone_info['name']}** ({zone_info['priority_level']} Priority)
- Strategies: {len(strategies)} ({len(custom_strategies)} custom)
- Actions: {len(actions)}
- Population Density: {zone_info['characteristics']['population_density']:,}/hectare
- Custom Innovation: {len(custom_strategies)/len(strategies)*100:.0f}% if strategies else 0%
""")
    
    return "\n".join(summary)

def get_custom_strategy_analysis():
    """Generate custom strategy analysis"""
    if not st.session_state.custom_strategies:
        return "No custom strategies created."
    
    analysis = f"**Total Custom Strategies:** {len(st.session_state.custom_strategies)}\n\n"
    
    # Analyze by subsystem focus
    subsystem_counts = {"Human-Social": 0, "Spatial": 0, "Air-Soundscape": 0, "Thermal": 0}
    
    for strategy in st.session_state.custom_strategies.values():
        for subsystem in strategy.get('Subsystems', []):
            if subsystem in subsystem_counts:
                subsystem_counts[subsystem] += 1
    
    analysis += "**Custom Strategy Focus Distribution:**\n"
    for subsystem, count in subsystem_counts.items():
        analysis += f"- {subsystem}: {count} strategies\n"
    
    # Usage analysis
    total_usage = 0
    for zone_data in st.session_state.game_manager.selected_zones.values():
        for strategy in zone_data.get('strategies', []):
            if strategy in st.session_state.custom_strategies:
                total_usage += 1
    
    analysis += f"\n**Usage Rate:** {total_usage} custom strategy implementations across zones"
    
    return analysis

def get_subsystem_detailed_analysis(uec_data):
    """Generate detailed subsystem analysis"""
    analysis = []
    
    for subsystem, score in uec_data['subsystem_scores'].items():
        if score >= 80:
            performance = "🟢 Excellent"
        elif score >= 60:
            performance = "🟡 Good"
        elif score >= 40:
            performance = "🟠 Fair"
        else:
            performance = "🔴 Poor"
        
        analysis.append(f"**{subsystem}:** {score:.1f}/100 {performance}")
    
    return "\n".join(analysis)

def get_complete_loop_analysis(effects):
    """Generate complete loop analysis"""
    activated_loops = effects.get('activated_loops', [])
    
    if not activated_loops:
        return "No loops activated. Configure strategies to engage the feedback loop system."
    
    # Analyze by strategic value
    value_counts = {}
    for loop in activated_loops:
        value = loop.get('strategic_value', 'Unknown')
        value_counts[value] = value_counts.get(value, 0) + 1
    
    analysis = f"""
**Loop Activation Analysis:**
- Total Activated: {len(activated_loops)}/113 ({len(activated_loops)/113*100:.1f}%)
- Critical Value Loops: {value_counts.get('Critical', 0)}
- Important Value Loops: {value_counts.get('Important', 0)}
- Moderate Value Loops: {value_counts.get('Moderate', 0)}

**System Leverage:** {sum(loop.get('leverage', 0) for loop in activated_loops):.3f}
"""
    
    return analysis

def get_achievement_summary(uec_data, effects):
    """Generate achievement summary"""
    achievements = []
    
    if uec_data['overall_uec'] >= 90:
        achievements.append("🏆 **URBAN MASTER** - Achieved world-class UEC score")
    elif uec_data['overall_uec'] >= 80:
        achievements.append("🚀 **EXPERT PLANNER** - Excellent urban planning performance")
    elif uec_data['overall_uec'] >= 65:
        achievements.append("⭐ **SKILLED STRATEGIST** - Strong strategic thinking")
    
    if len(effects.get('activated_loops', [])) >= 20:
        achievements.append("🔄 **LOOP MASTER** - Activated 20+ feedback loops")
    
    if len(st.session_state.custom_strategies) >= 3:
        achievements.append("✨ **STRATEGY INNOVATOR** - Created 3+ custom strategies")
    
    if len(effects.get('spillover_effects', {})) >= 5:
        achievements.append("🌊 **SPILLOVER SPECIALIST** - Created extensive spillover network")
    
    return "\n".join(achievements) if achievements else "🌱 Continue playing to unlock achievements!"

def get_learning_outcomes(uec_data, effects):
    """Generate learning outcomes based on gameplay"""
    outcomes = []
    
    if uec_data['subsystem_scores'].get('Human-Social', 0) > 60:
        outcomes.append("• **Behavioral Primacy:** Successfully applied the principle that behavioral interventions have higher leverage")
    
    if len(effects.get('spillover_effects', {})) > 0:
        outcomes.append("• **Network Effects:** Understood how urban interventions create ripple effects across zones")
    
    if len(effects.get('activated_loops', [])) > 10:
        outcomes.append("• **Systems Thinking:** Demonstrated ability to activate multiple feedback loops for system change")
    
    if len(st.session_state.custom_strategies) >= 1:
        outcomes.append("• **Innovation Skills:** Created custom strategies using evidence-based keyword analysis")
    
    outcomes.append("• **Evidence-Based Planning:** Applied scientific research to urban sustainability challenges")
    outcomes.append("• **Multi-Zone Coordination:** Managed complex multi-zone intervention strategies")
    
    return "\n".join(outcomes)

def get_future_applications_guide(uec_data):
    """Generate guide for applying learnings in real contexts"""
    innovation_score = len(st.session_state.custom_strategies)
    
    if uec_data['overall_uec'] >= 70 and innovation_score >= 2:
        return """
**Real-World Application Readiness: HIGH**

Your strategy demonstrates strong potential for real-world application:
• Focus on community engagement and behavioral programs first
• Use spatial and infrastructure interventions to support behavioral change
• Implement pilot projects in high-priority areas before scaling
• Apply your custom strategy creation skills to develop context-specific interventions
• Use the keyword analysis approach to communicate with stakeholders effectively
• Apply the 70/30 rule: 70% behavioral, 30% technical interventions
"""
    else:
        return """
**Real-World Application Readiness: DEVELOPING**

Continue developing these competencies for real-world application:
• Strengthen focus on human-centered design approaches
• Practice creating custom strategies using keyword analysis
• Develop skills in community engagement and stakeholder involvement
• Learn to sequence interventions for maximum cumulative impact
• Study successful behavioral urban interventions globally
• Practice translating academic concepts into actionable strategies
"""

def generate_strategy_summary():
    """Generate CSV summary of strategies used"""
    rows = []
    rows.append("Zone,Strategy,Type,Subsystems,Actions,Priority,Custom")
    
    for zone_id, zone_data in st.session_state.game_manager.selected_zones.items():
        zone_info = CITY_ZONES[zone_id]
        strategies = zone_data.get('strategies', [])
        actions = zone_data.get('actions', [])
        
        for strategy in strategies:
            is_custom = strategy in st.session_state.custom_strategies
            
            if is_custom:
                strategy_info = st.session_state.custom_strategies[strategy]
            else:
                strategy_info = next((s for s in STRATEGIES if s['Strategy'] == strategy), {})
            
            subsystems = ';'.join(strategy_info.get('Subsystems', []))
            rows.append(f"{zone_info['name']},{strategy},{'Custom' if is_custom else 'Predefined'},{subsystems},{len(actions)},{zone_info['priority_level']},{is_custom}")
    
    return '\n'.join(rows)

if __name__ == "__main__":
    main()
