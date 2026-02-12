"""
Learning Management System - Database Seed Script
Populates the database with courses, lessons, articles, simulations, and problems
"""

import json
import os
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from learning.models import (
    Discipline, Chapter, Lesson, Article, Simulation,
    SimulationControl, SimulationResult, PracticeProblem,
    ProblemChoice, LearningObjective, HelpCategory, HelpArticle
)


# Sample articles in Markdown format for Electrical Fundamentals
ELECTRICAL_ARTICLES = {
    "01-atomic-structure": """# Atomic Structure and Electricity

## Introduction

Electricity is fundamental to our modern world. From lighting our homes to powering smartphones and enabling industrial automation, electrical phenomena underpin nearly every aspect of contemporary life. To understand how electrical systems work, we must first explore the atomic structure of matter and how electrons behave at the most fundamental level.

This lesson provides the foundation for all subsequent electrical engineering concepts by examining the building blocks of matter and the nature of electrical charge.

---

## 1. Atomic Structure

### 1.1 The Structure of Atoms

All matter in the universe is composed of atoms—the fundamental units of chemical elements. Each atom consists of three primary particles:

- **Protons**: Positively charged particles located in the nucleus at the center of the atom
- **Neutrons**: Neutral particles (no charge) also located in the nucleus
- **Electrons**: Negatively charged particles that orbit the nucleus in energy shells or orbitals

The protons and neutrons are bound together in the nucleus, while electrons move in specific energy levels around the nucleus.

**Key Properties:**
- The number of protons in an atom determines its atomic number
- In a neutral atom, the number of electrons equals the number of protons
- The electrons in the outermost shell are called valence electrons

### 1.2 Energy Shells and Electron Configuration

Electrons orbit the nucleus in discrete energy levels, often depicted as shells (K, L, M, N...). Each shell can hold a maximum number of electrons:

| Shell | Maximum Electrons |
|-------|------------------|
| K (n=1) | 2 |
| L (n=2) | 8 |
| M (n=3) | 18 |
| N (n=4) | 32 |

The valence electrons in the outermost shell determine the chemical and electrical properties of the element.

---

## 2. Electrical Charge

### 2.1 The Nature of Electric Charge

Electric charge is a fundamental property of matter. There are two types of charge:

- **Positive (+)** - carried by protons
- **Negative (-)** - carried by electrons

**Key Principles:**
- Like charges repel; opposite charges attract
- Charge is conserved—it cannot be created or destroyed, only transferred
- The SI unit of charge is the **coulomb (C)**

### 2.2 Elementary Charge

The elementary charge (e) is the magnitude of charge on a single electron or proton:

$$e = 1.602 \\times 10^{-19} \\text{ C}$$

This means it takes approximately \\(6.24 \\times 10^{18}\\) electrons to make up one coulomb of charge.

### 2.3 Current Flow

When electrons move from one atom to another, we get an electric current. However, it's important to understand that:

- In metals, electrons are the charge carriers
- The direction of conventional current is opposite to electron flow
- Current is measured in **amperes (A)** or **amps**

---

## 3. Conductors, Semiconductors, and Insulators

### 3.1 Conductors

**Conductors** are materials that allow electric charge to flow easily. They have:

- Large numbers of free electrons
- Low electrical resistance
- Typically metallic materials

**Common Conductors:**
- Silver (best conductor, but expensive)
- Copper (most common, good balance of cost and conductivity)
- Aluminum (lighter, used in power transmission)
- Gold (excellent conductor, used for contacts)

The resistivity of copper at 20°C is approximately \\(1.68 \\times 10^{-8} \\Omega\\cdot\\text{m}\\).

### 3.2 Insulators

**Insulators** (or dielectrics) are materials that resist the flow of electric current. They have:

- Very few free electrons
- Very high electrical resistance
- Electrons tightly bound to atoms

**Common Insulators:**
- Rubber
- Glass
- Plastic
- Ceramics
- Dry air

### 3.3 Semiconductors

**Semiconductors** have electrical conductivity between conductors and insulators. Their key properties:

- Can be modified by doping (adding impurities)
- Conductivity increases with temperature (unlike metals)
- Form the basis of modern electronics

**Common Semiconductors:**
- Silicon (most widely used)
- Germanium
- Gallium Arsenide

---

## 4. The Photoelectric Effect

When light of sufficient frequency strikes a material, it can eject electrons from the surface. This phenomenon, called the **photoelectric effect**, demonstrates the particle nature of light and is fundamental to understanding how solar cells work.

$$E = hf = \\frac{hc}{\\lambda}$$

Where:
- E = energy of photon
- h = Planck's constant (6.626 × 10⁻³⁴ J·s)
- f = frequency of light
- c = speed of light
- λ = wavelength

---

## Key Takeaways

✓ Atoms consist of protons (+), neutrons, and electrons (-)
✓ The elementary charge is 1.6 × 10⁻¹⁹ C
✓ Conductors allow easy electron flow; insulators resist it
✓ Semiconductors have controllable conductivity
✓ Current is the flow of electric charge, measured in amperes

---

## Practice Problems

1. Calculate the number of electrons in 1 coulomb of charge.
2. Explain why copper is preferred over silver for most electrical wiring.
3. What is the main difference between a conductor and an insulator at the atomic level?

---

## Further Reading

- Halliday, Resnick & Walker - Fundamentals of Physics
- Serway & Jewett - Physics for Scientists and Engineers
- IEEE Standard Dictionary of Electrical and Electronics Terms
""",

    "02-voltage-current-resistance": """# Voltage, Current, and Resistance

## The Three Pillars of Circuit Analysis

Voltage, current, and resistance are the three fundamental quantities in electrical circuits. Understanding their definitions, relationships, and how to measure them is essential for all electrical engineering work.

---

## 1. Voltage (Potential Difference)

### 1.1 Definition

**Voltage**, also called **electromotive force (EMF)** or **potential difference**, is the electrical "pressure" that pushes electrons through a conductor. It represents the energy per unit charge:

$$V = \\frac{W}{Q}$$

Where:
- V = voltage in volts (V)
- W = energy in joules (J)
- Q = charge in coulombs (C)

**1 volt = 1 joule per coulomb**

### 1.2 Understanding Voltage

Think of voltage like water pressure in a pipe:
- Higher pressure (voltage) pushes more water (electrons) through the pipe
- Without pressure difference (voltage), water won't flow
- The unit of measurement is the **volt (V)**

### 1.3 Common Voltage Levels

| Application | Typical Voltage |
|-------------|----------------|
| AA Battery | 1.5 V |
| Car Battery | 12 V |
| USB Power | 5 V |
| Household AC | 120 V / 230 V |
| Power Transmission | 110 kV - 765 kV |

---

## 2. Current

### 2.1 Definition

**Current** is the rate of flow of electric charge through a conductor:

$$I = \\frac{Q}{t}$$

Where:
- I = current in amperes (A)
- Q = charge in coulombs (C)
- t = time in seconds (s)

**1 ampere = 1 coulomb per second**

### 2.2 Types of Current

#### Direct Current (DC)
- Current flows in one direction only
- Produced by batteries, solar cells
- Symbol: `⎓`

#### Alternating Current (AC)
- Current periodically reverses direction
- Used in power distribution
- Standard frequencies: 50 Hz (Europe), 60 Hz (Americas)
- Symbol: `~`

### 2.3 Current Flow vs Electron Flow

**Important Distinction:**
- **Conventional Current**: Flows from positive to negative (+ → -)
- **Electron Flow**: Actually flows from negative to positive (- → +)

We use conventional current in virtually all circuit analysis.

---

## 3. Resistance

### 3.1 Definition

**Resistance** is the opposition to the flow of current in a conductor:

$$R = \\frac{V}{I}$$

Where:
- R = resistance in ohms (Ω)
- V = voltage in volts (V)
- I = current in amperes (A)

**1 ohm = 1 volt per ampere**

### 3.2 Factors Affecting Resistance

The resistance of a conductor depends on:

$$R = \\rho \\frac{L}{A}$$

Where:
- ρ (rho) = resistivity of the material (Ω·m)
- L = length of conductor (m)
- A = cross-sectional area (m²)

**Resistance increases with:**
- Longer length
- Smaller cross-sectional area
- Higher temperature (for most conductors)

**Resistance decreases with:**
- Shorter length
- Larger cross-sectional area
- Lower temperature

### 3.3 Resistivity of Common Materials

| Material | Resistivity (Ω·m) at 20°C | Use Case |
|----------|---------------------------|----------|
| Silver | 1.59 × 10⁻⁸ | Premium contacts |
| Copper | 1.68 × 10⁻⁸ | General wiring |
| Gold | 2.44 × 10⁻⁸ | Connectors |
| Aluminum | 2.65 × 10⁻⁸ | Power lines |
| Carbon | 3.5 × 10⁻⁵ | Resistors |
| Glass | 10¹⁰ - 10¹⁴ | Insulation |

---

## 4. Ohm's Law

### 4.1 The Fundamental Relationship

Ohm's Law relates voltage, current, and resistance:

$$V = I \\times R$$

This can be rearranged:

$$I = \\frac{V}{R}$$

$$R = \\frac{V}{I}$$

### 4.2 The Ohm's Law Triangle

A useful memory aid:

```
        ┌───┐
        │ V │
        ├───┤
        │I×R│
        └───┘
```

Cover the unknown quantity to see the formula.

### 4.3 Example Calculations

**Example 1:** A 100Ω resistor has 2A of current. What is the voltage?

$$V = I \\times R = 2A \\times 100\\Omega = 200V$$

**Example 2:** A 12V battery is connected to a 6Ω resistor. What is the current?

$$I = \\frac{V}{R} = \\frac{12V}{6\\Omega} = 2A$$

**Example 3:** A device draws 0.5A at 120V. What is its resistance?

$$R = \\frac{V}{I} = \\frac{120V}{0.5A} = 240\\Omega$$

---

## 5. Practical Applications

### 5.1 Voltage Dividers

A voltage divider uses two resistors to create a specific voltage:

$$V_{out} = V_{in} \\times \\frac{R_2}{R_1 + R_2}$$

### 5.2 Current Limiting

Resistors limit current to protect components:

$$R = \\frac{V_{source} - V_{LED}}{I_{LED}}$$

### 5.3 Measuring Instruments

- **Voltmeter**: Connected in parallel, measures voltage
- **Ammeter**: Connected in series, measures current
- **Ohmmeter**: Measures resistance (with power off)

---

## Key Takeaways

✓ Voltage is electrical "pressure" measured in volts
✓ Current is the flow of charge measured in amperes
✓ Resistance opposes current flow, measured in ohms
✓ Ohm's Law: V = I × R
✓ Resistance depends on material, length, and cross-section

---

## Practice Problems

1. A circuit has 0.25A flowing through a 480Ω resistor. Calculate the voltage.
2. A 60W bulb operates at 120V. What current does it draw?
3. Why do long extension cords cause voltage drop?
4. A copper wire is 100m long with a cross-section of 2.5mm². Calculate its resistance at 20°C.

---

## Interactive Simulation

Use the Ohm's Law simulator to experiment with different voltage and resistance values and observe the resulting current.
""",

    "03-ohms-law-power": """# Ohm's Law and Power

## Introduction

Power is one of the most important concepts in electrical engineering. Every electrical device—from the smallest LED to the largest industrial motor—has a power rating that determines its performance and energy consumption. This lesson combines Ohm's Law with power formulas to give you a complete toolkit for circuit analysis.

---

## 1. Electrical Power

### 1.1 What is Power?

**Power** is the rate at which electrical energy is transferred or consumed. It represents how fast work is being done by the electrical system.

$$P = \\frac{W}{t}$$

Where:
- P = power in watts (W)
- W = energy in joules (J)
- t = time in seconds (s)

**1 watt = 1 joule per second**

### 1.2 Power in Electrical Circuits

From Ohm's Law, we derive three equivalent power formulas:

$$P = V \\times I$$

$$P = I^2 \\times R$$

$$P = \\frac{V^2}{R}$$

Choose the formula based on which quantities you know.

---

## 2. Understanding the Power Formulas

### 2.1 P = V × I (Voltage × Current)

**Most fundamental form**
- Directly relates power to voltage and current
- Applies to any electrical device
- Used for power consumption calculations

**Example:** A 120V circuit with 2A current:
$$P = 120V \\times 2A = 240W$$

### 2.2 P = I² × R (Current² × Resistance)

**Useful when current is known**
- Current is the same throughout a series circuit
- Shows that power loss increases with square of current
- Important for heating calculations

**Example:** 0.5A through 100Ω resistor:
$$P = (0.5)^2 \\times 100 = 0.25 \\times 100 = 25W$$

### 2.3 P = V² / R (Voltage² / Resistance)

**Useful when voltage is known**
- Parallel circuits have same voltage across branches
- Shows relationship between voltage and power
- Common in lighting calculations

**Example:** 12V across 6Ω load:
$$P = \\frac{12^2}{6} = \\frac{144}{6} = 24W$$

---

## 3. Energy and Power Billing

### 3.1 Electrical Energy

Energy is total power consumed over time:

$$E = P \\times t$$

The unit of electrical energy is the **watt-hour (Wh)** or **kilowatt-hour (kWh)**.

$$1 \\text{ kWh} = 1000 \\text{ watts} \\times 1 \\text{ hour}$$

### 3.2 Power Billing

Utilities bill for energy in kilowatt-hours:

| Appliance | Power | Time | Energy |
|-----------|-------|------|--------|
| LED Bulb | 10W | 10 hours | 100 Wh |
| Hair Dryer | 1500W | 0.5 hours | 750 Wh |
| AC Unit | 2000W | 8 hours | 16 kWh |
| Laptop | 65W | 8 hours | 520 Wh |

### 3.3 Calculating Monthly Cost

$$\\text{Cost} = \\text{Energy (kWh)} \\times \\text{Rate (\$/kWh)}$$

**Example:**
- Monthly consumption: 500 kWh
- Rate: $0.12/kWh
- Cost: 500 × 0.12 = $60/month

---

## 4. Efficiency

### 4.1 What is Efficiency?

Efficiency is the ratio of useful output power to input power:

$$\\eta = \\frac{P_{out}}{P_{in}} \\times 100\\%$$

No device is 100% efficient—some energy is always lost as heat.

### 4.2 Power Loss

Power loss primarily occurs as heat due to resistance:

$$P_{loss} = I^2 \\times R$$

**Reducing Power Loss:**
- Use lower resistance conductors
- Transmit at higher voltage (reduces current)
- Use efficient transformer designs

---

## 5. Practical Applications

### 5.1 Sizing Conductors

Conductor size must handle current without excessive heating:

$$I_{max} = \\sqrt{\\frac{P_{ allowable}}{R}}$$

NEC guidelines specify ampacity tables for common wire gauges.

### 5.2 Selecting Fuses and Breakers

Protection devices should:
- Handle normal operating current
- Trip before conductors overheat
- Coordinate with upstream devices

$$I_{rating} \\geq 1.25 \\times I_{load}$$

### 5.3 Battery Sizing

For battery backup systems:

$$Capacity (Ah) = \\frac{Power (W) \\times Time (h)}{Voltage (V) \\times DOD}$$

Where DOD = Depth of Discharge (typically 50-80% for lead-acid)

---

## 6. Real-World Examples

### 6.1 Electric Vehicle Charging

- Level 1: 1.4 kW (120V, 12A)
- Level 2: 7.2-22 kW (240V, 30-100A)
- DC Fast: 50-350 kW

### 6.2 Solar Power Systems

- Panel ratings: 300-600W per panel
- Inverter efficiency: 95-98%
- System sizing based on daily energy needs

### 6.3 Industrial Motors

Motor power in horsepower (hp):
$$1 \\text{ hp} = 746 \\text{ W}$$

Motor selection considers:
- Full-load current
- Starting current (5-7× running)
- Power factor correction

---

## Key Takeaways

✓ Power formulas: P = VI, P = I²R, P = V²/R
✓ Energy = Power × Time (measured in kWh)
✓ Efficiency = Pout/Pin × 100%
✓ Power loss increases with square of current
✓ Higher voltage transmission reduces I²R losses

---

## Practice Problems

1. A 1500W electric heater operates at 120V. Calculate:
   a) Current draw
   b) Resistance
   c) Daily energy consumption (8 hours)

2. A power line has 100A at 230V. If resistance is 0.1Ω, calculate:
   a) Power delivered
   b) Power loss in the line
   c) Efficiency

3. A factory uses 10,000 kWh/month at $0.08/kWh. What is the monthly bill?

4. Why do power companies use high voltage for transmission?

---

## Interactive Simulations

1. **Power Calculator**: Input any two values (V, I, R) to calculate the other two and power
2. **Energy Cost Calculator**: Calculate monthly costs for different appliances
3. **Wire Sizing Tool**: Determine minimum wire gauge for given current
""",

    "04-series-circuits": """# Series Circuits

## Understanding Series Circuit Configuration

A series circuit is the simplest circuit configuration where components are connected end-to-end, forming a single path for current to flow. Understanding series circuits is essential because the principles learned here apply to all circuit analysis.

---

## 1. Series Circuit Characteristics

### 1.1 Definition

In a **series circuit**, components are connected in a single loop, so the same current flows through each component.

**Key Characteristics:**

| Characteristic | Description |
|----------------|-------------|
| Current | Same through all components |
| Voltage | Divides across components |
| Resistance | Adds up (R_total = R1 + R2 + ...) |
| Power | Divides based on resistance |

### 1.2 Visual Representation

```
    ┌──────────┐
    │          │
    │         R1
    │          │
(+) [V]──────[R2]──────[R3]────── (-)
    │          │         │
    └──────────┴─────────┘
    
    Same current (I) through all components
    Voltage: V = V1 + V2 + V3
```

---

## 2. Total Resistance in Series

### 2.1 Formula

The total resistance of series-connected resistors is the sum of individual resistances:

$$R_{total} = R_1 + R_2 + R_3 + \\dots + R_n$$

### 2.2 Example Calculations

**Example 1:** Three resistors in series
- R1 = 100Ω, R2 = 200Ω, R3 = 300Ω
- R_total = 100 + 200 + 300 = **600Ω**

**Example 2:** Mixed with wire resistance
- R1 = 470Ω, R2 = 1kΩ, wire = 2Ω
- R_total = 470 + 1000 + 2 = **1472Ω**

### 2.3 Practical Implications

- Adding series resistance always increases total resistance
- The more components in series, the higher the total resistance
- Current decreases as more components are added

---

## 3. Voltage Division

### 3.1 Kirchhoff's Voltage Law

The sum of voltage drops around a closed loop equals zero:

$$\\sum V = 0$$

Or more practically for sources and drops:

$$V_{source} = V_1 + V_2 + V_3 + \\dots$$

### 3.2 Voltage Divider Rule

The voltage across any resistor in a series circuit is proportional to its resistance:

$$V_n = V_{total} \\times \\frac{R_n}{R_{total}}$$

### 3.3 Example: Voltage Division

**Circuit Parameters:**
- V_total = 12V
- R1 = 100Ω, R2 = 200Ω, R3 = 300Ω
- R_total = 600Ω

**Voltage Calculations:**
$$V_1 = 12 \\times \\frac{100}{600} = 2V$$
$$V_2 = 12 \\times \\frac{200}{600} = 4V$$
$$V_3 = 12 \\times \\frac{300}{600} = 6V$$

**Verification:** 2V + 4V + 6V = 12V ✓

---

## 4. Current in Series Circuits

### 4.1 Ohms Law Application

Since resistance is known and voltage is known:

$$I = \\frac{V_{total}}{R_{total}}$$

### 4.2 Current Example

Given: V = 12V, R1 = 100Ω, R2 = 200Ω, R3 = 300Ω

$$I = \\frac{12V}{600\\Omega} = 0.02A = 20mA$$

**Current through each component is 20mA**

---

## 5. Power Distribution

### 5.1 Power in Series

Power dissipated in each resistor:

$$P_n = I^2 \\times R_n$$

### 5.2 Power Example

$$P_1 = (0.02)^2 \\times 100 = 0.04W = 40mW$$
$$P_2 = (0.02)^2 \\times 200 = 0.08W = 80mW$$
$$P_3 = (0.02)^2 \\times 300 = 0.12W = 120mW$$

**Total Power:** P_total = 40 + 80 + 120 = **240mW**

**Verification:** P_total = V × I = 12V × 0.02A = 240mW ✓

---

## 6. Troubleshooting Series Circuits

### 6.1 Open Circuit (Most Common Fault)

**Symptoms:**
- No current flows
- Voltage present at source
- Voltage drop across the open point = source voltage

**Causes:**
- Broken wire
- Burned-out component
- Loose connection
- Blown fuse

### 6.2 Short Circuit

**Symptoms:**
- Increased current
- Reduced total resistance
- Voltage drop across short ≈ 0V

**Causes:**
- Wire insulation failure
- Component failure (internal short)
- Accidental contact

### 6.3 Diagnostic Approach

1. Check voltage at source
2. Measure voltage drop across each component
3. Sum of drops should equal source voltage
4. Current can be measured anywhere in series

---

## 7. Real-World Applications

### 7.1 Series resistor for LED

Current-limiting resistor in series with LED:

$$R = \\frac{V_{supply} - V_{LED}}{I_{LED}}$$

Example: 9V supply, LED Vf = 2V, I = 20mA
$$R = \\frac{9 - 2}{0.02} = \\frac{7}{0.02} = 350\\Omega$$

### 7.2 Voltage Reference

Creating specific voltage levels using resistor dividers:

$$V_{out} = V_{in} \\times \\frac{R_2}{R_1 + R_2}$$

### 7.3 String Lights

Old-style Christmas lights were in series:
- One bulb fails → whole string goes out
- Designed so failed bulb shorts (modern versions)

---

## Key Takeaways

✓ Series circuits have one current path
✓ Total resistance = sum of all resistances
✓ Same current through all components
✓ Voltage divides proportional to resistance
✓ V_total = V1 + V2 + V3 + ...

---

## Practice Problems

1. Three 100Ω resistors in series with 24V source:
   a) Calculate total resistance
   b) Calculate current
   c) Calculate voltage across each resistor

2. A 9V battery powers three LEDs in series. Each LED has Vf = 2.1V at 20mA.
   a) What resistor value is needed?
   b) What power rating for the resistor?

3. In a series circuit with R1=220Ω, R2=330Ω:
   a) If R1 has 4V, what is V2?
   b) What is the source voltage?

---

## Interactive Simulation

Experiment with:
- Different resistor values
- Voltage source changes
- Observe current and voltage distribution
- Test open/short circuit conditions
""",

    "05-parallel-circuits": """# Parallel Circuits

## Understanding Parallel Circuit Configuration

Parallel circuits provide multiple paths for current flow. This configuration is the most common in practical applications, including household wiring, automotive systems, and electronic devices.

---

## 1. Parallel Circuit Characteristics

### 1.1 Definition

In a **parallel circuit**, components are connected across the same voltage source, providing multiple paths for current flow.

**Key Characteristics:**

| Characteristic | Description |
|----------------|-------------|
| Voltage | Same across all components |
| Current | Divides among branches |
| Resistance | Decreases with more branches |
| Power | Adds up across branches |

### 1.2 Visual Representation

```
         ┌───[R1]───┐
         │          │
    (+) [V]──[R2]──[R3]── (-)
         │          │
         └──────────┘
    
    Same voltage across all components
    Current: I_total = I1 + I2 + I3
```

---

## 2. Total Resistance in Parallel

### 2.1 General Formula

For resistors in parallel:

$$\\frac{1}{R_{total}} = \\frac{1}{R_1} + \\frac{1}{R_2} + \\frac{1}{R_3} + \\dots + \\frac{1}{R_n}$$

### 2.2 Special Cases

**Two resistors only:**
$$R_{total} = \\frac{R_1 \\times R_2}{R_1 + R_2}$$

**Equal resistors (n of same value):**
$$R_{total} = \\frac{R}{n}$$

**Infinite parallel paths:**
$$R_{total} = 0$$ (ideal short circuit)

### 2.3 Example Calculations

**Example 1:** Two equal resistors
- R1 = R2 = 100Ω
- R_total = (100 × 100) / (100 + 100) = **10000/200 = 50Ω**

**Example 2:** Three different resistors
- R1 = 100Ω, R2 = 200Ω, R3 = 300Ω
- 1/R_total = 1/100 + 1/200 + 1/300 = 0.01 + 0.005 + 0.00333 = 0.01833
- R_total = 1/0.01833 = **54.5Ω**

**Example 3:** Four 100Ω in parallel
- R_total = 100/4 = **25Ω**

---

## 3. Current Division

### 3.1 Kirchhoff's Current Law

The sum of currents entering a node equals the sum leaving:

$$\\sum I_{in} = \\sum I_{out}$$

### 3.2 Current Divider Rule

The current through any branch is inversely proportional to its resistance:

$$I_n = I_{total} \\times \\frac{R_{total}}{R_n}$$

### 3.3 Example: Current Division

**Circuit Parameters:**
- V = 12V
- R1 = 100Ω, R2 = 200Ω, R3 = 300Ω
- R_total = 54.5Ω

**Total Current:**
$$I_{total} = \\frac{12V}{54.5\\Omega} = 220mA$$

**Branch Currents:**
$$I_1 = 220 \\times \\frac{54.5}{100} = 120mA$$
$$I_2 = 220 \\times \\frac{54.5}{200} = 60mA$$
$$I_3 = 220 \\times \\frac{54.5}{300} = 40mA$$

**Verification:** 120 + 60 + 40 = 220mA ✓

---

## 4. Voltage in Parallel

### 4.1 Same Voltage Principle

**Critical Point:** Voltage is identical across all parallel branches.

This is why:
- All outlets in your home provide 120V
- All car headlights get 12V
- Battery-powered devices maintain voltage as batteries deplete

### 4.2 Voltage Source Behavior

An ideal voltage source maintains constant voltage regardless of load:
- Current increases as more branches are added
- Total power delivery increases
- Source must handle maximum expected current

---

## 5. Power in Parallel Circuits

### 5.1 Power Calculation

Power in each branch:
$$P_n = \\frac{V^2}{R_n}$$

Total power:
$$P_{total} = P_1 + P_2 + P_3 + \\dots$$

### 5.2 Power Example

Using previous circuit (V = 12V):
$$P_1 = \\frac{12^2}{100} = 1.44W$$
$$P_2 = \\frac{12^2}{200} = 0.72W$$
$$P_3 = \\frac{12^2}{300} = 0.48W$$

**Total Power:** 1.44 + 0.72 + 0.48 = **2.64W**

**Verification:** P_total = V × I_total = 12V × 0.22A = 2.64W ✓

---

## 6. Advantages of Parallel Circuits

### 6.1 Independent Operation

Each branch operates independently:
- One component failing doesn't affect others
- Components can be switched on/off individually
- Full voltage available to each load

### 6.2 Voltage Consistency

- All loads receive same voltage
- Performance doesn't degrade with added loads
- Simplifies design and operation

### 6.3 Practical Examples

**Household Wiring:**
- 120V outlets throughout the home
- Each device operates independently
- Breaker trips affect only that circuit

**Automotive Systems:**
- 12V battery with multiple branches
- Lights, radio, accessories operate separately
- Parallel fuse for each circuit

---

## 7. Troubleshooting Parallel Circuits

### 7.1 Open Branch

**Symptoms:**
- Other branches unaffected
- Only the open branch loses voltage
- Current decreases in total

**Example:** One light bulb burns out in a string of parallel bulbs → others stay lit

### 7.2 Short Circuit (Dangerous!)

**Symptoms:**
- Massive current increase
- Voltage drops to near zero
- Protection device should trip

**Causes:**
- Wire insulation failure
- Component internal short
- Accidental metal contact

### 7.3 High Resistance Connection

**Symptoms:**
- Voltage drop at connection point
- Overheating at bad connection
- Reduced voltage to downstream loads

---

## 8. Series-Parallel Combinations

### 8.1 Identifying Combinations

Most real circuits combine series and parallel elements:

```
    ┌───[R1]──┐
    │         │
[+] [V]   [R2]──[R3]──[-]
    │         │
    └─────────┘
    
    R2 and R3 in series, parallel with R1
```

### 8.2 Analysis Strategy

1. Identify obvious series/parallel groups
2. Calculate equivalent resistance of each group
3. Redraw simplified circuit
4. Work backward to find all values

---

## Key Takeaways

✓ Parallel circuits have multiple current paths
✓ Voltage is the same across all branches
✓ Total resistance decreases with more branches
✓ Current divides inversely proportional to resistance
✓ Components operate independently

---

## Practice Problems

1. Two 100Ω resistors in parallel with 24V:
   a) Calculate total resistance
   b) Calculate total current
   c) Calculate current through each resistor

2. A 12V battery powers three parallel loads:
   - Load 1: 60W bulb
   - Load 2: 120W bulb
   - Load 3: 240W bulb
   
   Calculate:
   a) Resistance of each load
   b) Total resistance
   c) Total current from battery

3. Four identical lamps in parallel draw 2.4A from 12V:
   a) What is the resistance of one lamp?
   b) What is the power of one lamp?

---

## Interactive Simulation

Experiment with:
- Adding/removing parallel branches
- Different resistor values
- Open/short circuit scenarios
- Current and power distribution
""",

    "06-series-parallel-circuits": """# Series-Parallel Circuits

## Combining Series and Parallel Configurations

Most practical circuits combine series and parallel elements. Learning to analyze these hybrid circuits is essential for real-world electrical engineering.

---

## 1. Introduction to Combination Circuits

### 1.1 What Are Series-Parallel Circuits?

These circuits contain both series and parallel elements within the same network. They require systematic analysis techniques.

### 1.2 Example Configurations

**Configuration A: Parallel-Series**
```
    ┌───[R1]──┐
    │         │
[+] [V]   [R2]──[R3]──[-]
    │         │
    └─────────┘
    
    R2 and R3 in series, combined in parallel with R1
```

**Configuration B: Series-Parallel**
```
    ┌───[R1]──[R2]───┐
    │                │
[+] [V]          [R4]──[-]
    │                │
    └────[R3]────────┘
    
    R1 and R2 in series, parallel with R3, then series with R4
```

---

## 2. Step-by-Step Analysis Method

### 2.1 The Six-Step Process

1. **Identify Groups**: Find obvious series/parallel combinations
2. **Calculate Equivalents**: Replace groups with single resistors
3. **Simplify**: Redraw the circuit with equivalents
4. **Repeat**: Continue until single equivalent resistance
5. **Calculate Total**: Find total current and voltage
6. **Work Backward**: Calculate individual component values

### 2.2 Example Analysis

**Given Circuit:**
- V = 12V
- R1 = 100Ω (parallel group)
- R2 = 200Ω, R3 = 200Ω (series in parallel branch)

**Step 1:** R2 and R3 in series
$$R_{23} = 200 + 200 = 400\\Omega$$

**Step 2:** R1 and R23 in parallel
$$R_{total} = \\frac{100 \\times 400}{100 + 400} = \\frac{40000}{500} = 80\\Omega$$

**Step 3:** Total current
$$I_{total} = \\frac{12V}{80\\Omega} = 0.15A = 150mA$$

**Step 4:** Current through each branch
- Branch 1 (R1 only): I1 = 0.15A × (400/500) = 120mA
- Branch 2 (R23): I23 = 0.15A × (100/500) = 30mA

**Step 5:** Voltages
- V across R1 = 120mA × 100Ω = 12V
- V across R2+R3 = 30mA × 400Ω = 12V (same voltage)
- V across R2 = 30mA × 200Ω = 6V
- V across R3 = 30mA × 200Ω = 6V

---

## 3. Delta-Wye (Pi-Tee) Transformations

### 3.1 When Are They Needed?

For complex networks that cannot be simplified by series-parallel rules, use Delta-Wye (Y-Δ) transformations.

**Delta (Δ) Configuration:**
```
    R1
   /  \
R3│    │R2
   \\  /
    └─┘
    
    R1, R2, R3 form a triangle
```

**Wye (Y) Configuration:**
```
      R1
       │
   R3──●──R2
       │
      Neutral
    
    R1, R2, R3 form a Y
```

### 3.2 Delta to Wye Transformation

$$R_Y = \\frac{R_\\Delta \\times R_{\\Delta}}{Sum\\ of\\ all\\ R_\\Delta}$$

For a balanced Delta (all R equal):
$$R_Y = \\frac{R_\\Delta}{3}$$

### 3.3 Wye to Delta Transformation

For a balanced Wye:
$$R_\\Delta = 3 \\times R_Y$$

---

## 4. Bridge Circuits

### 4.1 Wheatstone Bridge

Used for precision resistance measurement:

```
    V_ex ──[R1]──[R2]──┐
              │        │
            [Rx]    [R3]
              │        │
            ──┴────────┘
              │
            Ground
```

**Balanced Condition:**
$$\\frac{R_1}{R_2} = \\frac{R_x}{R_3}$$

### 4.2 Bridge Analysis

When bridge is unbalanced (no component between midpoints):
- Use nodal analysis
- Or apply Delta-Wye transformation

---

## 5. Practical Applications

### 5.1 Resistive Sensor Networks

Temperature sensors often use Wheatstone bridge configuration for precision measurement.

### 5.2 Audio Systems

Volume controls use logarithmic potentiometer networks.

### 5.3 Measurement Instruments

Analog meters use series-parallel shunt resistors for different ranges.

---

## 6. Troubleshooting Tips

### 6.1 Simplify First

- Always reduce to simplest form before calculating
- Check for obvious shorts/opens
- Verify component values

### 6.2 Verify Results

- Total power should equal sum of all component powers
- Voltage division should be proportional to resistance
- Current division should be inverse to resistance

### 6.3 Common Mistakes

- Forgetting to recalculate after each simplification
- Mixing up series vs parallel rules
- Not accounting for all current paths

---

## Key Takeaways

✓ Series-parallel circuits require systematic analysis
✓ Simplify step by step, then work backward
✓ Delta-Wye transformations for complex networks
✓ Bridge circuits require special analysis techniques
✓ Always verify results with power calculations

---

## Practice Problems

1. Given: V = 24V, R1 = 50Ω, R2 = 100Ω, R3 = 100Ω (in series), R4 = 50Ω (in parallel with R2+R3)
   a) Draw the circuit
   b) Calculate R_total
   c) Calculate all currents and voltages

2. A balanced Delta network has each resistance = 300Ω. Convert to equivalent Wye.

3. Wheatstone bridge: R1 = 100Ω, R2 = 200Ω, R3 = 150Ω. Find Rx for balance.

---

## Interactive Simulation

Practice with:
- Various series-parallel combinations
- Bridge circuit analysis
- Delta-Wye transformations
- Troubleshooting scenarios
"""
}


def seed_learning_data():
    """Seed the database with learning content from JSON files"""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    
    try:
        # Create disciplines
        disciplines = [
            {
                "key": "electrical",
                "name": "Electrical Engineering",
                "icon": "fa-bolt",
                "color": "#f59e0b",
                "description": "Master electrical circuits, power systems, electronics, and modern electrical technologies"
            },
            {
                "key": "mechanical",
                "name": "Mechanical Engineering", 
                "icon": "fa-cogs",
                "color": "#3b82f6",
                "description": "Master mechanics, thermodynamics, materials, and mechanical systems design"
            },
            {
                "key": "civil",
                "name": "Civil Engineering",
                "icon": "fa-hard-hat",
                "color": "#22c55e",
                "description": "Master structural analysis, geotechnics, construction, and infrastructure design"
            }
        ]
        
        # Create disciplines and their chapters
        for disc_data in disciplines:
            existing = db.query(Discipline).filter(Discipline.key == disc_data["key"]).first()
            if not existing:
                discipline = Discipline(**disc_data)
                db.add(discipline)
                db.flush()
            else:
                discipline = existing
            
            # Create chapters based on discipline
            chapters_data = get_chapters_for_discipline(discipline.key)
            for ch_data in chapters_data:
                existing_ch = db.query(Chapter).filter(
                    Chapter.discipline_id == discipline.id,
                    Chapter.slug == ch_data["slug"]
                ).first()
                if not existing_ch:
                    ch_data["discipline_id"] = discipline.id
                    chapter = Chapter(**ch_data)
                    db.add(chapter)
                    db.flush()
                    
                    # Create lessons for this chapter
                    lessons_data = get_lessons_for_chapter(discipline.key, chapter.slug)
                    for les_data in lessons_data:
                        les_data["chapter_id"] = chapter.id
                        create_lesson(db, les_data)
        
        db.commit()
        print("Learning data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


def get_chapters_for_discipline(key):
    """Return chapter data for each discipline"""
    if key == "electrical":
        return [
            {"title": "Electrical Fundamentals", "slug": "01-fundamentals", "icon": "fa-star", "description": "Core concepts of electricity, circuit analysis, and basic laws"},
            {"title": "Circuit Analysis", "slug": "02-circuit-analysis", "icon": "fa-wave-square", "description": "Advanced methods for analyzing complex circuits"},
            {"title": "Power Systems", "slug": "03-power-systems", "icon": "fa-plug", "description": "Generation, transmission, and distribution of electrical power"},
            {"title": "Electronics", "slug": "04-electronics", "icon": "fa-microchip", "description": "Semiconductor devices and electronic circuits"},
            {"title": "Digital Electronics", "slug": "05-digital-electronics", "icon": "fa-binary", "description": "Binary logic, digital circuits, and microprocessors"}
        ]
    elif key == "mechanical":
        return [
            {"title": "Mechanical Fundamentals", "slug": "01-fundamentals", "icon": "fa-ruler-combined", "description": "Core principles of mechanics, forces, and energy"},
            {"title": "Thermodynamics", "slug": "02-thermodynamics", "icon": "fa-fire", "description": "Heat, energy, and power systems"},
            {"title": "Mechanics of Materials", "slug": "03-mechanics", "icon": "fa-puzzle-piece", "description": "Stress, strain, and deformation analysis"},
            {"title": "Engineering Materials", "slug": "04-materials", "icon": "fa-cubes", "description": "Material properties, selection, and testing"}
        ]
    elif key == "civil":
        return [
            {"title": "Civil Engineering Fundamentals", "slug": "01-fundamentals", "icon": "fa-ruler-horizontal", "description": "Core principles of statics, materials, and structural analysis"},
            {"title": "Structural Analysis", "slug": "02-structural", "icon": "fa-archway", "description": "Analysis of beams, frames, and trusses"},
            {"title": "Geotechnical Engineering", "slug": "03-geotechnical", "icon": "fa-mountain", "description": "Soil mechanics, foundations, and earthworks"},
            {"title": "Construction Engineering", "slug": "04-construction", "icon": "fa-truck-loading", "description": "Construction methods and management"}
        ]
    return []


def get_lessons_for_chapter(discipline_key, chapter_slug):
    """Return lesson data for each chapter"""
    if discipline_key == "electrical" and chapter_slug == "01-fundamentals":
        return [
            {
                "title": "Atomic Structure and Electricity",
                "slug": "01-atomic-structure",
                "duration_minutes": 15,
                "level": "Beginner",
                "type": "theory",
                "order": 1,
                "is_published": True,
                "objectives": [
                    "Understand the structure of atoms and electron behavior",
                    "Explain the concept of electrical charge",
                    "Differentiate between conductors, semiconductors, and insulators"
                ],
                "article_content": ELECTRICAL_ARTICLES["01-atomic-structure"],
                "summary": "Learn about atomic structure, electrical charge, and material conductivity types."
            },
            {
                "title": "Voltage, Current, and Resistance",
                "slug": "02-voltage-current-resistance",
                "duration_minutes": 20,
                "level": "Beginner",
                "type": "theory",
                "order": 2,
                "is_published": True,
                "objectives": [
                    "Define voltage, current, and resistance",
                    "Understand the relationship between these three quantities"
                ],
                "article_content": ELECTRICAL_ARTICLES["02-voltage-current-resistance"],
                "summary": "Master the three fundamental electrical quantities and Ohm's Law."
            },
            {
                "title": "Ohm's Law and Power",
                "slug": "03-ohms-law-power",
                "duration_minutes": 25,
                "level": "Beginner",
                "type": "mixed",
                "order": 3,
                "is_published": True,
                "objectives": [
                    "Master Ohm's Law and its applications",
                    "Calculate power in electrical circuits"
                ],
                "article_content": ELECTRICAL_ARTICLES["03-ohms-law-power"],
                "summary": "Learn power calculations and energy consumption for circuits.",
                "simulations": [
                    {
                        "name": "Ohm's Law Calculator",
                        "type": "ohms-law",
                        "config": {"controls": ["voltage", "resistance"], "results": ["current", "power"]}
                    }
                ]
            },
            {
                "title": "Series Circuits",
                "slug": "04-series-circuits",
                "duration_minutes": 25,
                "level": "Intermediate",
                "type": "theory",
                "order": 4,
                "is_published": True,
                "objectives": [
                    "Identify series circuit characteristics",
                    "Calculate total resistance in series"
                ],
                "article_content": ELECTRICAL_ARTICLES["04-series-circuits"],
                "summary": "Analyze series circuits with voltage division and current calculations.",
                "simulations": [
                    {
                        "name": "Series Circuit Analysis",
                        "type": "series-circuit",
                        "config": {"controls": ["vsource", "r1", "r2", "r3"], "results": ["r_total", "current", "v1", "v2", "v3"]}
                    }
                ]
            },
            {
                "title": "Parallel Circuits",
                "slug": "05-parallel-circuits",
                "duration_minutes": 25,
                "level": "Intermediate",
                "type": "theory",
                "order": 5,
                "is_published": True,
                "objectives": [
                    "Identify parallel circuit characteristics",
                    "Calculate total resistance in parallel"
                ],
                "article_content": ELECTRICAL_ARTICLES["05-parallel-circuits"],
                "summary": "Master parallel circuits with current division and power distribution.",
                "simulations": [
                    {
                        "name": "Parallel Circuit Analysis",
                        "type": "parallel-circuit",
                        "config": {"controls": ["vsource", "r1", "r2", "r3"], "results": ["r_total", "i_total", "i1", "i2", "i3"]}
                    }
                ]
            },
            {
                "title": "Series-Parallel Circuits",
                "slug": "06-series-parallel-circuits",
                "duration_minutes": 30,
                "level": "Intermediate",
                "type": "theory",
                "order": 6,
                "is_published": True,
                "objectives": [
                    "Identify combined series-parallel configurations",
                    "Simplify complex circuits step-by-step"
                ],
                "article_content": ELECTRICAL_ARTICLES["06-series-parallel-circuits"],
                "summary": "Analyze complex circuits using systematic simplification methods."
            }
        ]
    return []


def create_lesson(db, lesson_data):
    """Create a lesson with all related data"""
    objectives = lesson_data.pop("objectives", [])
    article_content = lesson_data.pop("article_content", "")
    summary = lesson_data.pop("summary", "")
    simulations_data = lesson_data.pop("simulations", [])
    problems_data = lesson_data.pop("problems", [])
    
    lesson = Lesson(**lesson_data)
    db.add(lesson)
    db.flush()
    
    # Create objectives
    for idx, obj in enumerate(objectives):
        objective = LearningObjective(
            lesson_id=lesson.id,
            objective=obj,
            order=idx + 1
        )
        db.add(objective)
    
    # Create article
    article = Article(
        lesson_id=lesson.id,
        content_type="markdown",
        content=article_content,
        summary=summary,
        reading_time=lesson_data.get("duration_minutes", 15)
    )
    db.add(article)
    
    # Create simulations
    for sim_data in simulations_data:
        sim = Simulation(
            lesson_id=lesson.id,
            name=sim_data["name"],
            type=sim_data["type"],
            config=sim_data["config"]
        )
        db.add(sim)
        db.flush()
        
        # Add controls based on type
        if sim.type == "ohms-law":
            sim.controls = [
                SimulationControl(simulation_id=sim.id, name="voltage", label="Voltage", control_type="slider", min_value=1, max_value=24, default_value=12, unit="V"),
                SimulationControl(simulation_id=sim.id, name="resistance", label="Resistance", control_type="slider", min_value=10, max_value=1000, default_value=100, unit="Ω")
            ]
            sim.results = [
                SimulationResult(simulation_id=sim.id, name="current", label="Current", unit="A"),
                SimulationResult(simulation_id=sim.id, name="power", label="Power", unit="W")
            ]
        elif sim.type == "series-circuit":
            sim.controls = [
                SimulationControl(simulation_id=sim.id, name="vsource", label="Source Voltage", control_type="slider", min_value=1, max_value=24, default_value=12, unit="V"),
                SimulationControl(simulation_id=sim.id, name="r1", label="R1", control_type="slider", min_value=10, max_value=1000, default_value=100, unit="Ω"),
                SimulationControl(simulation_id=sim.id, name="r2", label="R2", control_type="slider", min_value=10, max_value=1000, default_value=200, unit="Ω"),
                SimulationControl(simulation_id=sim.id, name="r3", label="R3", control_type="slider", min_value=10, max_value=1000, default_value=300, unit="Ω")
            ]
            sim.results = [
                SimulationResult(simulation_id=sim.id, name="r_total", label="Total R", unit="Ω"),
                SimulationResult(simulation_id=sim.id, name="current", label="Current", unit="mA"),
                SimulationResult(simulation_id=sim.id, name="v1", label="V1", unit="V"),
                SimulationResult(simulation_id=sim.id, name="v2", label="V2", unit="V"),
                SimulationResult(simulation_id=sim.id, name="v3", label="V3", unit="V")
            ]
        elif sim.type == "parallel-circuit":
            sim.controls = [
                SimulationControl(simulation_id=sim.id, name="vsource", label="Source Voltage", control_type="slider", min_value=1, max_value=24, default_value=12, unit="V"),
                SimulationControl(simulation_id=sim.id, name="r1", label="R1", control_type="slider", min_value=10, max_value=1000, default_value=100, unit="Ω"),
                SimulationControl(simulation_id=sim.id, name="r2", label="R2", control_type="slider", min_value=10, max_value=1000, default_value=200, unit="Ω"),
                SimulationControl(simulation_id=sim.id, name="r3", label="R3", control_type="slider", min_value=10, max_value=1000, default_value=300, unit="Ω")
            ]
            sim.results = [
                SimulationResult(simulation_id=sim.id, name="r_total", label="Total R", unit="Ω"),
                SimulationResult(simulation_id=sim.id, name="i_total", label="Total I", unit="mA"),
                SimulationResult(simulation_id=sim.id, name="i1", label="I1", unit="mA"),
                SimulationResult(simulation_id=sim.id, name="i2", label="I2", unit="mA"),
                SimulationResult(simulation_id=sim.id, name="i3", label="I3", unit="mA")
            ]
    
    return lesson


if __name__ == "__main__":
    seed_learning_data()