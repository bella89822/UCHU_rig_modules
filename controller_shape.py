import maya.cmds as cmds



def create_circleX_ctrl(name="circleX_ctrl", size=1.0, sections=8):
    crv, make_node = cmds.circle(n=name, nr=(1,0,0), r=size, s=sections, ch=True)
    # force it to be just in case:))

    cmds.setAttr(make_node + ".normalX", 1)
    cmds.setAttr(make_node + ".normalY", 0)
    cmds.setAttr(make_node + ".normalZ", 0)
    return crv

def create_circleY_ctrl(name="circleY_ctrl", size=1.0, sections=8):
    crv, make_node = cmds.circle(n=name, nr=(0,1,0), r=size, s=sections, ch=True)
    cmds.setAttr(make_node + ".normalX", 0)
    cmds.setAttr(make_node + ".normalY", 1)
    cmds.setAttr(make_node + ".normalZ", 0)
    return crv

def create_circleZ_ctrl(name="circleZ_ctrl", size=1.0, sections=8):
    crv, make_node = cmds.circle(n=name, nr=(0,0,1), r=size, s=sections, ch=True)
    cmds.setAttr(make_node + ".normalX", 0)
    cmds.setAttr(make_node + ".normalY", 0)
    cmds.setAttr(make_node + ".normalZ", 1)
    return crv



def _build_pyramidX(name, size):
    """Internal function: builds the clean pyramid pointing +X."""
    cvs = [
        (0,   0.5, -0.5),
        (0,   0.5,  0.5),
        (0,  -0.5,  0.5),
        (0,  -0.5, -0.5),
        (0,   0.5, -0.5),
        (1,   0,    0),
        (0,  -0.5, -0.5),
        (1,   0,    0),
        (0,  -0.5,  0.5),
        (1,   0,    0),
        (0,   0.5,  0.5)
    ]

    scaled = [(x * size, y * size, z * size) for x, y, z in cvs]

    crv = cmds.curve(
        d=1,
        name=name,
        p=scaled,
        k=list(range(len(scaled)))
    )

    shape = cmds.listRelatives(crv, shapes=True)[0]
    cmds.rename(shape, f"{name}Shape")
    cmds.makeIdentity(crv, apply=True, t=1, r=1, s=1)
    return crv


# --- Public-facing builders -------------------------------------------

def create_pyramidX_ctrl(name="pyramidX_ctrl", size=1.0):
    """Pyramid pointing +X"""
    return _build_pyramidX(name, size)


def create_pyramidY_ctrl(name="pyramidY_ctrl", size=1.0):
    """Pyramid pointing +Y"""
    crv = _build_pyramidX(name, size)
    cmds.rotate(0, 0, -90, crv)      # X->Y
    cmds.makeIdentity(crv, apply=True, t=1, r=1, s=1)
    return crv


def create_pyramidZ_ctrl(name="pyramidZ_ctrl", size=1.0):
    """Pyramid pointing +Z"""
    crv = _build_pyramidX(name, size)
    cmds.rotate(0, 90, 0, crv)       # X->Z
    cmds.makeIdentity(crv, apply=True, t=1, r=1, s=1)
    return crv



def create_crossX_ctrl(name="crossX_ctrl", size=1.0):
    pts = [
        (0, 1, 1), (0, 3, 1), (0, 3, -1), (0, 1, -1),
        (0, 1, -3), (0, -1, -3), (0, -1, -1), (0, -3, -1),
        (0, -3, 1), (0, -1, 1), (0, -1, 3), (0, 1, 3),
        (0, 1, 1)
    ]
    scaled = [(x*size, y*size, z*size) for x, y, z in pts]
    return cmds.curve(d=1, p=scaled, name=name)


def create_crossY_ctrl(name="crossY_ctrl", size=1.0):
    pts = [
        (-1, 0, -1), (-1, 0, -3), (1, 0, -3), (1, 0, -1),
        (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3),
        (-1, 0, 3), (-1, 0, 1), (-3, 0, 1), (-3, 0, -1),
        (-1, 0, -1)
    ]
    scaled = [(x*size, y*size, z*size) for x, y, z in pts]
    return cmds.curve(d=1, p=scaled, name=name)


def create_crossZ_ctrl(name="crossZ_ctrl", size=1.0):
    pts = [
        (-1, 1, 0), (-1, 3, 0), (1, 3, 0), (1, 1, 0),
        (3, 1, 0), (3, -1, 0), (1, -1, 0), (1, -3, 0),
        (-1, -3, 0), (-1, -1, 0), (-3, -1, 0), (-3, 1, 0),
        (-1, 1, 0)
    ]
    scaled = [(x*size, y*size, z*size) for x, y, z in pts]
    return cmds.curve(d=1, p=scaled, name=name)

def create_double_side_arrowZ(name="doubleSide_arrowZ_ctrl"):
    """
    Create Double Side Arrow controller facing Z axis.
    """
    arrow = cmds.curve(
        d=3,
        p=[
            (-1, -1, 0), (-1, 0, 0), (-1, 1, 0), (-1, 1, 0),
            (-2, 1, 0), (-2, 1, 0), (0, 3, 0), (0, 3, 0),
            (2, 1, 0), (2, 1, 0), (1, 1, 0), (1, 1, 0),
            (1, 0, 0), (1, -1, 0), (1, -1, 0),
            (2, -1, 0), (2, -1, 0), (0, -3, 0), (0, -3, 0),
            (-2, -1, 0), (-2, -1, 0), (-1, -1, 0), (-1, -1, 0)
        ],
        k=[
            0, 0, 0, 1, 2, 3, 4, 5, 6, 7,
            8, 9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 21, 21
        ],
        name=name
    )

    cmds.makeIdentity(arrow, apply=True, t=True, r=True, s=True, n=False)
    return arrow

def create_double_side_arrowX(name="doubleSide_arrowX_ctrl"):
    """
    Create Double Side Arrow controller facing X axis.
    """
    arrow = create_double_side_arrowZ(name)
    cmds.rotate(0, 90, 0, arrow, os=True, r=True)
    cmds.makeIdentity(arrow, apply=True, t=True, r=True, s=True, n=False)
    return arrow
def create_double_side_arrowY(name="doubleSide_arrowY_ctrl"):
    """
    Create Double Side Arrow controller facing Y axis.
    """
    arrow = create_double_side_arrowZ(name)
    cmds.rotate(-90, 0, 0, arrow, os=True, r=True)
    cmds.makeIdentity(arrow, apply=True, t=True, r=True, s=True, n=False)
    return arrow
def create_cone_arrowZ(name="coneArrowZ_ctrl", size=1.0):
    """
    Create a cone-arrow style NURBS curve controller facing Z axis.
    """
    cvs = [
        (0, 0, 0),
        (1, 0, 0),
        (1, 3, 0),
        (2.5, 3, 0),
        (1.5, 3.5, 0.5),
        (1.5, 3.5, -0.5),
        (2.5, 3, 0),
        (1.5, 2.5, -0.5),
        (1.5, 3.5, -0.5),
        (1.5, 2.5, -0.5),
        (1.5, 2.5, 0.5),
        (1.5, 3.5, 0.5),
        (1.5, 2.5, 0.5),
        (2.5, 3, 0)
    ]

    scaled_cvs = [(x * size, y * size, z * size) for x, y, z in cvs]

    crv = cmds.curve(
        name=name,
        d=1,
        p=scaled_cvs,
        k=list(range(len(scaled_cvs)))
    )

    shape = cmds.listRelatives(crv, shapes=True)[0]
    cmds.rename(shape, f"{name}Shape")

    cmds.makeIdentity(crv, apply=True, t=True, r=True, s=True, n=False)
    return crv
def create_cone_arrowX(name="coneArrowX_ctrl", size=1.0):
    """
    Create cone-arrow controller facing X axis.
    """
    crv = create_cone_arrowZ(name, size)
    cmds.rotate(0, 90, 0, crv, os=True, r=True)
    cmds.makeIdentity(crv, apply=True, t=True, r=True, s=True, n=False)
    return crv
def create_cone_arrowY(name="coneArrowY_ctrl", size=1.0):
    """
    Create cone-arrow controller facing Y axis.
    """
    crv = create_cone_arrowZ(name, size)
    cmds.rotate(-90, 0, 0, crv, os=True, r=True)
    cmds.makeIdentity(crv, apply=True, t=True, r=True, s=True, n=False)
    return crv
def create_sphere_ctrl(name="sphere_ctrl", size=1.0, degree=1):
    """
    Create a clean NURBS sphere controller (three great circles)
    with no color override, suitable for shape-library usage.

    Args:
        name (str): name of the controller transform.
        size (float): size of the sphere.
        degree (int): curve degree (1 or 3).

    Returns:
        str: the controller transform name
    """


    # 1. Create axis circles (building the sphere)

    # circle 1: XZ
    c1 = cmds.circle(n=f"{name}_X", nr=(1,0,0), r=size, d=degree)[0]
    # circle 2: XY
    c2 = cmds.circle(n=f"{name}_Y", nr=(0,0,1), r=size, d=degree)[0]
    # circle 3: YZ
    c3 = cmds.circle(n=f"{name}_Z", nr=(0,1,0), r=size, d=degree)[0]
    # 2. Consolidate shapes into a single transform

    ctrl = cmds.createNode("transform", name=name)

    for c in [c1, c2, c3]:
        shapes = cmds.listRelatives(c, s=True, f=True)
        cmds.parent(shapes, ctrl, add=True, shape=True)
        cmds.delete(c)

    # freeze ctrl (shape only, keeps transforms clean)
    cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)

    return ctrl

def create_cube_ctrl(name="cube_ctrl", size=1.0):
    """
    Create a clean, proper cube-shaped NURBS controller.
    This mimics a true wireframe cube with all 12 edges.

    Args:
        name (str): Name of the control.
        size (float): Uniform scale.
    
    Returns:
        str: The name of the created curve.
    """
    half = size * 0.5
    points = [ [-half, -half, -half],[-half, -half,  half],[-half,  half,  half],
    [-half,  half, -half],[-half, -half, -half],[ half, -half, -half],[ half, -half,  half],
    [-half, -half,  half],[ half, -half,  half],[ half,  half,  half],[-half,  half,  half],
    [ half,  half,  half],[ half,  half, -half],[-half,  half, -half],[ half,  half, -half],
    [ half, -half, -half]]

    # create segments for the curve
    segments = []
    for i in range(len(points) - 1):
        segments.append(points[i])
        segments.append(points[i + 1])
        segments.append([None, None, None])

    ctrl = cmds.curve(d=1, p=[pt for pt in segments if pt[0] is not None], name=name)
    ctrl_shape=cmds.listRelatives(ctrl,shapes=True)[0]
    ctrl_shape=cmds.rename(ctrl_shape,f'{ctrl}Shape')
    return ctrl

def create_niceCube_ctrl(v=1.1):
    sels = cmds.ls(selection=True)
    if not sels:
        cmds.warning("No item selected.")
        return None
    else:
        for item in sels:
            bbox = cmds.exactWorldBoundingBox(item)
            

            width = bbox[3] - bbox[0]
            height = bbox[4] - bbox[1]
            depth = bbox[5] - bbox[2]
            center = [  bbox[0]+bbox[3],
                       (bbox[1] + bbox[4]) / 2,
                       (bbox[2] + bbox[5]) / 2 ]

            p = [
                [bbox[0], bbox[1], bbox[2]], [bbox[3], bbox[1], bbox[2]],
                [bbox[3], bbox[4], bbox[2]], [bbox[0], bbox[4], bbox[2]],
                [bbox[0], bbox[1], bbox[2]],  # back face
                [bbox[0], bbox[1], bbox[5]], [bbox[3], bbox[1], bbox[5]],
                [bbox[3], bbox[4], bbox[5]], [bbox[0], bbox[4], bbox[5]],
                [bbox[0], bbox[1], bbox[5]], [bbox[3], bbox[1], bbox[5]],
                [bbox[3], bbox[1], bbox[2]], [bbox[3], bbox[4], bbox[2]],
                [bbox[3], bbox[4], bbox[5]], [bbox[0], bbox[4], bbox[5]],
                [bbox[0], bbox[4], bbox[2]], [bbox[0], bbox[1], bbox[2]]
            ]

            #create segments for the curve 
       

            ctrl = cmds.curve(d=1, p=p, name=f'{item}_ctrl')
            #center pivot
            cmds.xform(ctrl, centerPivots=True)
            #size it up a lil bit
            cmds.setAttr(f'{ctrl}.scale', v, v, v)
            cmds.makeIdentity(ctrl, apply=True, scale=True)
            #rename the shape node just in case
            shape = cmds.listRelatives(ctrl, shapes=True)[0]
            cmds.rename(shape, f'{item}_ctrlShape')
        return ctrl




def create_ctrlgrp_on_ctrl_base(ctrl=None,targets=None):
    #check if the selection is valid

    sels = cmds.ls(sl=True)
    if not sels:
        cmds.warning('please select a control curve')
        return
    
    #select top ctrl
    top_ctrl = cmds.ls(sl=True)[0]
    # list ctrl in order
    ctrl_list = cmds.listRelatives(top_ctrl, ad=True, fullPath=False,type='transform') or []
    ctrl_list = list(reversed(ctrl_list))
    ctrl_list = [top_ctrl] + list(ctrl_list)

    #list zero and output parents
    zero_list = []
    output_list = []
    #create ctrl_grp for each ctrl
    for ctrl in ctrl_list:

        parent = None
        top_node = None
        prefix_list = ['zero', 'driven', 'connect']
        for prefix in prefix_list:
            new_name = f'{prefix}_{ctrl}'

            node = cmds.createNode('transform', name=new_name)

            cmds.matchTransform(node, ctrl) 

            if parent:
                cmds.parent(node,parent)

            parent=node
            if not top_node:
                top_node=node


        cmds.parent(ctrl,parent)    
       
        cmds.delete(ctrl,constructionHistory=True)
        #rename ctrl shape
        ctrl_shape = cmds.listRelatives(ctrl,shapes=True)or[]
        for i,shape in enumerate(ctrl_shape):
            cmds.rename(shape,f'{ctrl}Shape{i+1}')
        #create sub ctrl
        sub = cmds.duplicate(ctrl, name=ctrl.replace('ctrl', 'subctrl'))[0]
        #delete duplicated children except the shape
        nodes = cmds.listRelatives(sub, children=True,type='transform', fullPath=True) or []

        cmds.delete(nodes)
        
        cmds.parent(sub, ctrl)

        #set attr for sub ctrl
        cmds.setAttr(f'{sub}.scale', 0.85, 0.85, 0.85)
        cmds.setAttr(f'{sub}.overrideEnabled', 1)
        cmds.makeIdentity(sub, apply=True, t=1, r=1, s=1, n=0)
        sub_shape = cmds.listRelatives(sub, children=True)[0]

         #clean up line width 
        cmds.setAttr(f'{sub_shape}.lineWidth', 1)
        for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
            cmds.setAttr(f'{ctrl_shape}.lineWidth', 2)

        #set color for sub ctrl
        if sub.startswith('L'):
            for shape in cmds.listRelatives(sub, shapes=True):
                cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f"{shape}.overrideColor", 6)
        elif sub.startswith('C'):
            for shape in cmds.listRelatives(sub, shapes=True):
                cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f"{shape}.overrideColor", 17)
        elif sub.startswith('R'):
            for shape in cmds.listRelatives(sub, shapes=True):
                cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f"{shape}.overrideColor", 13)

        # set ctrl color
        if ctrl.startswith('L'):
            for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f"{ctrl_shape}.overrideColor", 6)
        elif ctrl.startswith('C'):
            for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f"{ctrl_shape}.overrideColor", 17)
        elif ctrl.startswith('R'):
            for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f"{ctrl_shape}.overrideColor", 13)
            
        # create output group
        cmds.createNode('transform', name=f'output_{ctrl}', parent=sub)
        cmds.setAttr(f'{ctrl}.visibility', keyable=False, lock=True, channelBox=False)
        cmds.setAttr(f'{sub}.visibility', keyable=False, lock=True, channelBox=False)
        cmds.setAttr(f'{ctrl}.rotateOrder', keyable=True)
        cmds.setAttr(f'{sub}.rotateOrder', keyable=True)
        #set up sub ctrl vis attr
        cmds.addAttr(ctrl, longName='subCtrlVis', attributeType='bool', keyable=False)
        cmds.setAttr(f'{ctrl}.subCtrlVis', channelBox=True)
        for shape in cmds.listRelatives(sub, shapes=True):
            cmds.connectAttr(f'{ctrl}.subCtrlVis', f'{shape}.visibility')
        #create list for later parent
        
        zero_list.append(f'zero_{ctrl}')
        output_list.append(f'output_{ctrl}')

        #parent zero to prev output 
        for i in range(1, len(zero_list)):
            #start from one because the first one is the top grp 
            zero=zero_list[i]
            output=output_list[i-1]
            if cmds.objExists(zero) and cmds.objExists(output):

                cmds.parent(zero, output)






#define dictionar for each ctrl shape creation function
#structure: UI_name: function_name
ctrl_shape_dict = {
    'circle':{'X':create_circleX_ctrl,
              'Y':create_circleY_ctrl,
              'Z':create_circleZ_ctrl
              },
    'pyramid':{'X':create_pyramidX_ctrl,
               'Y':create_pyramidY_ctrl,
               'Z':create_pyramidZ_ctrl
               },
    'cross':{'X':create_crossX_ctrl,    
             'Y':create_crossY_ctrl,
             'Z':create_crossZ_ctrl
             },
    'double_side_arrow':{'X':create_double_side_arrowX,
                        'Y':create_double_side_arrowY,
                        'Z':create_double_side_arrowZ
                        },
    'cone_arrow':{'X':create_cone_arrowX,   
                  'Y':create_cone_arrowY,
                  'Z':create_cone_arrowZ
                  },
    'sphere':create_sphere_ctrl,
    'cube':create_cube_ctrl,

}


# sub funtion for create_ctrlgrp_on_ctrl
#1. grp building function
def build_groups(ctrl,prefix_list):
    '''prefix_list: list of prefix for group creation from the UI selection'''

    if not prefix_list:
            return None
    last_parent = None
    top_node = None

    for prefix in prefix_list:
        grp_name = f'{prefix}_{ctrl}'
        grp_node = cmds.createNode('transform', name=grp_name)
        cmds.matchTransform(grp_node, ctrl)
        if last_parent:
            cmds.parent(grp_node, last_parent)
        else:
            top_node = grp_node
        last_parent = grp_node

        #parent ctrl back to the last created group
    cmds.parent(ctrl, last_parent)
    return top_node

#2. build sub ctrl function
def build_sub_ctrl(ctrl,scale=0.85):
    '''build sub ctrl and connect visibility attr'''
    sub_name = ctrl.replace('ctrl', 'subctrl')
    sub_ctrl = cmds.duplicate(ctrl, name=sub_name)[0]  
    #create sub ctrl
    sub = cmds.duplicate(ctrl, name=ctrl.replace('ctrl', 'subctrl'))[0]
    #delete duplicated children except the shape
    nodes = cmds.listRelatives(sub, children=True,type='transform', fullPath=True) or []

    cmds.delete(nodes)
    
    cmds.parent(sub_ctrl, ctrl)

    #set attr for sub ctrl
    cmds.setAttr(f'{sub}.scale',scale, scale, scale)
    cmds.setAttr(f'{sub}.overrideEnabled', 1)
    cmds.makeIdentity(sub, apply=True, s=1)
    #check channel box for sub ctrl visibility
    if not cmds.attributeQuery('subCtrlVis', node=ctrl, exists=True):
        cmds.addAttr(ctrl, longName='subCtrlVis', attributeType='bool', keyable=False)
        cmds.setAttr(f'{ctrl}.subCtrlVis', channelBox=True)
    sub_shape = cmds.listRelatives(sub, children=True)
    for shape in sub_shape:
            #clean up line width 
        cmds.setAttr(f'{shape}.lineWidth', 1)
        cmds.connectAttr(f'{ctrl}.subCtrlVis', f'{shape}.visibility')

    return sub_ctrl

# 3. build color setting function 



def rename_ctrl_shapes(ctrl):
    '''rename ctrl shapes based on ctrl name'''
    shapes = cmds.listRelatives(ctrl, shapes=True, fullPath=True) or []
    for i, shape in enumerate(shapes):
        cmds.rename(shape, f'{ctrl}Shape{i+1}')

def create_shape(shape_type='circle', axis='X', name=None, size=1.0, targets=None):
    """
    Create a controller shape based on the specified type and axis.

    Args:
        shape_type (str): The type of shape to create (e.g., 'circle', 'pyramid').
        axis (str): The axis orientation for the shape ('X', 'Y', 'Z').
        name (str): The name of the controller.
        size (float): The size of the controller.

    Returns:
        str: The name of the created controller shape.
    """
    # make sure what is our target 
    if not targets:
        targets = cmds.ls(selection=True)
    
    if not targets:
        cmds.warning("Please select at least one target object.")
        return None

    created_shapes = []

    for target in targets:
        #check naming len
        if len(target.split('_'))<4:
            cmds.warning(f"Selected item '{target}' does not follow naming convention. Skipping.")
            continue
        
        if not name:
            parts = target.split('_')
            side = parts[0]
            part = parts[1]
            string = parts[-1]
            ctrl_name = f'{side}_{part}_{shape_type}_ctrl_{string}'
        else:
            ctrl_name = name
        entry = ctrl_shape_dict.get(shape_type)
        if isinstance(entry, dict):
            func = entry.get(axis)
        else:
            func = entry
        if func:
            create_node = func(name=ctrl_name, size=size)
            if target:
                cmds.matchTransform(create_node, target, pos=True, rot=True)
                pass


            created_shapes.append(create_node)
    return created_shapes



def create_ctrl_grp(shape_type = 'circle',axis = 'X',size=1.0,
                    prefix_list = [None],use_sub_ctrl=True,L_color=6,C_color=17,R_color=13):
    targets = cmds.ls(selection=True)
    if not targets:
        cmds.warning("Please select at least one control to create group.")
        return
    
    #create shape 
    ctrls = create_shape(shape_type = shape_type, axis=axis, size=size, targets=targets)
    if not ctrls:
        return
    
    for ctrl in ctrls:
        rename_ctrl_shapes










def create_ctrlgrp_on_ctrl_base(target=None):
    '''target(str): the control you want to create group on, if None, it will use the current selection as target''' 
    #select top ctrl
    if not target:
        target = cmds.ls(selection=True)
    # list ctrl in order
    ctrl_list = cmds.listRelatives(target, ad=True, fullPath=False,type='transform') or []
    ctrl_list = list(reversed(ctrl_list))
    ctrl_list = [target] + list(ctrl_list)

    #list zero and output parents
    zero_list = []
    output_list = []
    #create ctrl_grp for each ctrl
    for ctrl in ctrl_list:

        parent = None
        top_node = None
        prefix_list = ['zero', 'driven', 'connect']
        for prefix in prefix_list:
            new_name = f'{prefix}_{ctrl}'

            node = cmds.createNode('transform', name=new_name)

            cmds.matchTransform(node, ctrl) 

            if parent:
                cmds.parent(node,parent)

            parent=node
            if not top_node:
                top_node=node


        cmds.parent(ctrl,parent)    
       
        cmds.delete(ctrl,constructionHistory=True)
        #rename ctrl shape
        ctrl_shape = cmds.listRelatives(ctrl,shapes=True,fullPath=True)or[]
        for i,shape in enumerate(ctrl_shape):
            cmds.rename(shape,f'{ctrl}Shape{i+1}')
        #create sub ctrl
        sub = cmds.duplicate(ctrl, name=ctrl.replace('ctrl', 'subctrl'))[0]
        #delete duplicated children except the shape
        nodes = cmds.listRelatives(sub, children=True,type='transform', fullPath=True) or []

        cmds.delete(nodes)
        
        cmds.parent(sub, ctrl)

        #set attr for sub ctrl
        cmds.setAttr(f'{sub}.scale', 0.85, 0.85, 0.85)
        cmds.setAttr(f'{sub}.overrideEnabled', 1)
        cmds.makeIdentity(sub, apply=True, t=1, r=1, s=1, n=0)
        sub_shape = cmds.listRelatives(sub, children=True)[0]

         #clean up line width 
        cmds.setAttr(f'{sub_shape}.lineWidth', 1)
        for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
            cmds.setAttr(f'{ctrl_shape}.lineWidth', 2)

        #set color for sub ctrl
        if sub.startswith('L'):
            for shape in cmds.listRelatives(sub, shapes=True):
                cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f"{shape}.overrideColor", 6)
        elif sub.startswith('C'):
            for shape in cmds.listRelatives(sub, shapes=True):
                cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f"{shape}.overrideColor", 17)
        elif sub.startswith('R'):
            for shape in cmds.listRelatives(sub, shapes=True):
                cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f"{shape}.overrideColor", 13)

        # set ctrl color
        if ctrl.startswith('L'):
            for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f"{ctrl_shape}.overrideColor", 6)
        elif ctrl.startswith('C'):
            for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f"{ctrl_shape}.overrideColor", 17)
        elif ctrl.startswith('R'):
            for ctrl_shape in cmds.listRelatives(ctrl, shapes=True):
                cmds.setAttr(f'{ctrl_shape}.overrideEnabled', 1)
                cmds.setAttr(f"{ctrl_shape}.overrideColor", 13)
            
        # create output group
        cmds.createNode('transform', name=f'output_{ctrl}', parent=sub)
        cmds.setAttr(f'{ctrl}.visibility', keyable=False, lock=True, channelBox=False)
        cmds.setAttr(f'{sub}.visibility', keyable=False, lock=True, channelBox=False)
        cmds.setAttr(f'{ctrl}.rotateOrder', keyable=True)
        cmds.setAttr(f'{sub}.rotateOrder', keyable=True)
        #set up sub ctrl vis attr
        cmds.addAttr(ctrl, longName='subCtrlVis', attributeType='bool', keyable=False)
        cmds.setAttr(f'{ctrl}.subCtrlVis', channelBox=True)
        for shape in cmds.listRelatives(sub, shapes=True):
            cmds.connectAttr(f'{ctrl}.subCtrlVis', f'{shape}.visibility')
        #create list for later parent
        
        zero_list.append(f'zero_{ctrl}')
        output_list.append(f'output_{ctrl}')

        #parent zero to prev output 
        for i in range(1, len(zero_list)):
            #start from one because the first one is the top grp 
            zero=zero_list[i]
            output=output_list[i-1]
            if cmds.objExists(zero) and cmds.objExists(output):

                cmds.parent(zero, output)
        return zero_list[0]

def create_ctrlgrp_on_ctrl(target=None):
    '''target(list): the control you want to create group on, 
    if None, it will use the current selection as target'''
    top_list=[]
    
    if not target:
        target = cmds.ls(selection=True)
        for ctrl in target:
            zero_grp = create_ctrlgrp_on_ctrl_base(ctrl)
            top_list.append(zero_grp)
    return top_list



    


        


    







def create_ctrl_from_shape(shape):
    joints=cmds.ls(selection=True)
    shape_list = []
    for joint in joints:
        ctrl=cmds.duplicate(shape, name=joint.replace('joint','ctrl'))[0]
        cmds.matchTransform(ctrl,joint)
        parent = cmds.listRelatives(joint, parent=True)
        if  not parent:
            cmds.parent(ctrl,world=True)
        shape_list.append(ctrl)
    return shape_list



def hide_shape():
    ctrls=cmds.ls(selection=True,type='transform')
    for ctrl in ctrls:
        shape=cmds.listRelatives(ctrl,shapes=True,fullPath=True)[0]
        cmds.setAttr(f'{shape}.visibility',0)



def set_ctrl_color_width(target=None,color_index=1,width=2):
    '''
    target(list):target list you want to switch color 
    color_index(int): the color you want
    width(str):the line width you want to attempt'''
    if not target:
        target=cmds.ls(selection=True)
    if not target:
        cmds.warning('select at least one ctrl')
        return
    for ctrl in target:
        shapes = cmds.listRelatives(ctrl,c=True,shapes=True)or[]
        for shape in shapes: 
            cmds.setAttr(f'{shape}.lineWidth', width)
            cmds.setAttr(f'{shape}.overrideEnabled', 1)
            cmds.setAttr(f"{shape}.overrideColor", color_index)
#need to fix 
def flip_ctrl_shape(targets=None,axis='XY',world=False):
    shapes = cmds.ls(selection=True)
    for shape in shapes:
        for cv in cmds.ls(f'{shape}.cv[*]', flatten=True):
            pos = cmds.xform(cv, q=True, t=True, )
            cmds.xform(cv, t=[pos[0], pos[1], -pos[2]])