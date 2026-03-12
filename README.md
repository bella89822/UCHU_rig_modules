# UCHU_rig_modules
modules and workflow I designed for rigging
1. Technical Art Utilities (transform_tools.py, mirror_tools.py, naming.py)
Ensures pipeline consistency and workflow efficiency.

Space Switching: Implements a blendMatrix based switching system for seamless parenting (e.g., Head to World, Hand to Hip).

IK/FK Matching: Sophisticated matching scripts that handle world-space transformations for animator convenience.

SDK Mirroring: Specialized tools to mirror Set Driven Keys across the X-axis while handling directional attribute flipping.

Pipeline Naming: Standardizes shape node naming and handles procedural alphabetical indexing (e.g., mapping 0001 to A).

2. Core Rigging Automation (ik_auto_rig.py, fk_auto_rig.py, controller_shape.py)
The foundation of the rigging workflow.

Controller Library: Procedurally generates standard rigging shapes (Cube, Sphere, Cross) with automated hierarchical nesting (zero > driven > connect > ctrl).

IK/FK Systems: Automates RP/SC solver setups, including Pole Vector positioning with visual annotations.

Hand Pose System: Allows for automated pose-driven keys for complex finger articulation.

3. Advanced Deformation & Ribbons (ribbon_rig.py, deformation_tool.py)
Focuses on natural movement and skeletal stability.

Ribbon Rigging: Creates flip-free limbs using uvPin nodes and rail curves for superior interpolation.

Volume Preservation: Features a squash and stretch system that calculates curve length to drive joint scales and maintain character volume.

Twist Correction: Provides automated Twist Joint solutions using Matrix/Quaternion math to resolve Gimbal Lock in forearms and thighs.

4. Avian Wing System (wing_rig.py)
A specialized pipeline for high-density feathered wings.

Phase 1: Procedural Generation: Automates joint placement based on mesh topology and smart orientation using temporary aim constraints.

Phase 2: Spread Logic: Distributes rotation values across feather chains to create natural fanning effects.

Phase 3: Surface Pinning: Integrates uvPin nodes to keep feathers precisely attached to the wing surface during extreme deformation.

rig_modules/
├── transform_tools.py   # Space switching and matrix constraints
├── mirror_tools.py      # Mirroring logic for ctrls, joints, and SDKs
├── naming.py            # Batch renaming and shape node standardization
├── ik_auto_rig.py       # IK Arm/Leg and Spline IK setups
├── fk_auto_rig.py       # FK chains and hand pose automation
├── controller_shape.py  # Shape library and hierarchy builder
├── ribbon_rig.py        # Ribbon systems and volume preservation
├── deformation_tool.py  # Twist joints, muscle joints, and helper joints
├── wing_rig.py          # Feathered wing pipeline
├── face_rig.py          # Facial components (Eyelid, Lip roll, Zip lip)
└── __init__.py          # Module initialization and reloading
