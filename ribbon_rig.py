



import maya.cmds as cmds
import rig_modules.controller_shape as cs

import maya.api.OpenMaya as om

def create_joints_on_uvPin(curve, curve_up, num_joints=5, prefix="Ribbon",ctrl_instance=None,color_index=17,side='L'):
    '''
    Args:
        curve (str): Main driver curve
        curve_up (str): Rail curve (up vector curve)
        num_joints (int): How many joints to create
        name_prefix (str): Prefix for the created joints
    '''
    
    if num_joints < 1:
        cmds.error("Number of joints must be at least 1")
        return
    #define name and color
    side = curve.split('_')[0]
    typ = curve.split('_')[1]

    #  create uvPin node
    uvPin = cmds.createNode('uvPin', name=f'{side}_{typ}{prefix}_uvPin')
    
    # connect curves

    cmds.connectAttr(f'{curve}.worldSpace', f'{uvPin}.deformedGeometry', force=True)
    cmds.connectAttr(f'{curve_up}.worldSpace', f'{uvPin}.railCurve', force=True)
    
    # Adjust uvPin attributes
    if 'R' in side:
        cmds.setAttr(f'{uvPin}.tangentAxis', 3)  #-X axis
    else:
        cmds.setAttr(f'{uvPin}.tangentAxis', 0)      # X axis

    
    cmds.setAttr(f'{uvPin}.normalAxis', 1)       # Y axis
    cmds.setAttr(f'{uvPin}.normalOverride', 1)   # Use rail curve

    
    minor_jnt_grp = cmds.createNode('transform', name=f'{side}_{typ}{prefix}Minor_jnt_grp')
    for i in range(num_joints):
        jnt_name = f'{side}_{typ}{prefix}Minor_joint_{i+1:04d}'
        cmds.select(clear=True) 
        # create Joint 
        if 'R' in side:
            jnt = cmds.createNode('joint', name=jnt_name)
            cmds.setAttr(f'{jnt}.rotateX',-180)
            cmds.makeIdentity(jnt,t=0,r=1,s=1)

        else:

            jnt = cmds.createNode('joint', name=jnt_name)
        #create grp and ctrl for each joint
        cmds.select(jnt)
        ctrl = cs.create_ctrl_from_shape(ctrl_instance)[0]
        cmds.select(ctrl)
        zero_grp = cs.create_ctrlgrp_on_ctrl()
        cmds.parent(zero_grp, minor_jnt_grp)
        cmds.parent(jnt,f'output_{ctrl}')
        sub_ctrl=ctrl.replace('ctrl','subctrl')
        cs.set_ctrl_color_width([ctrl,sub_ctrl],color_index,1)
        zero = 'zero_' +ctrl
        # If there is only 1 joint, place it in the middle (0.5); otherwise, distribute evenly
        if num_joints > 1:
            para = float(i) / (num_joints - 1)
        else:
            para = 0.5

        # --- Connect to UV Pin ---
        # Set the U coordinate for the UV Pin at this index
        cmds.setAttr(f'{uvPin}.coordinate[{i}].coordinateU', para)
        # V is usually set to 0.5 for centering (useful if using a Ribbon Mesh)
        cmds.setAttr(f'{uvPin}.coordinate[{i}].coordinateV', 0.5) 

        # Connect the Matrix to the Joint's offsetParentMatrix
        # This keeps the Joint's Transform values clean (0,0,0) while locking its position to the curve
        decomp = cmds.createNode('decomposeMatrix',name=jnt.replace('joint','decomp'))
        cmds.connectAttr(f'{uvPin}.outputMatrix[{i}]', f'{decomp}.inputMatrix', force=True)
        cmds.connectAttr(f'{decomp}.outputRotate',f'{zero}.rotate')
        cmds.connectAttr(f'{decomp}.outputTranslate',f'{zero}.translate')
        
        # Ensure the Joint's transform is zeroed out (since position is controlled by offsetParentMatrix)
        cmds.setAttr(f'{jnt}.translate', 0, 0, 0)
        cmds.setAttr(f'{jnt}.rotate', 0, 0, 0)
        

    return minor_jnt_grp


def create_ribbon_curve(side=None,typ=None,num_joints=5,main_ctrl_instance=None,minor_ctrl_instance=None,
                        prefix='Ribbon',main_ctrl_color_index=17,minor_ctrl_color_index=17):
    '''
    Creates a ribbon curve with an up vector curve and joints driven by a uvPin.
    
    Args:
        side (str): Side prefix (e.g., 'L', 'R')
        typ (str): Type prefix (e.g., 'Arm', 'Spine')
        num_joints (int): Number of joints to create along the ribbon
        main_ctrl_instance: Controller instance for shape reference
    '''
    if not side or not typ:
        cmds.error("Side and Type must be specified")
        return
    
    #create main joints




    if 'R' in side:
        j1 = cmds.createNode('joint', name=f'{side}_{typ}{prefix}Main_joint_0001')
        cmds.setAttr(f'{j1}.translate', 2, 0, 0)
        j2 = cmds.createNode('joint', name=f'{side}_{typ}{prefix}Main_joint_0002')
        j3 = cmds.createNode('joint', name=f'{side}_{typ}{prefix}Main_joint_0003')
        cmds.setAttr(f'{j3}.translate', -2, 0, 0)
    else:
        j1 = cmds.createNode('joint', name=f'{side}_{typ}{prefix}Main_joint_0001')
        cmds.setAttr(f'{j1}.translate', -2, 0, 0)
        j2 = cmds.createNode('joint', name=f'{side}_{typ}{prefix}Main_joint_0002')
        j3 = cmds.createNode('joint', name=f'{side}_{typ}{prefix}Main_joint_0003')
        cmds.setAttr(f'{j3}.translate', 2, 0, 0)

    main_ctrl_grp = cmds.createNode('transform', name=f'{side}_{typ}{prefix}Main_ctrl_grp')
    cmds.matchTransform(main_ctrl_grp,j1)
    #create main ctrl
    for j in [j1,j2,j3]:
        cmds.select(j)
        main_ctrl = cs.create_ctrl_from_shape(main_ctrl_instance)[0]
        cmds.select(main_ctrl)
        zero_grp_main = cs.create_ctrlgrp_on_ctrl()

        cs.set_ctrl_color_width([main_ctrl],main_ctrl_color_index,1)
        cs.set_ctrl_color_width([main_ctrl.replace('ctrl','subctrl')],main_ctrl_color_index,1)
        cmds.parent(j,f'output_{main_ctrl}')
        cmds.hide(j)
        cmds.parent(zero_grp_main,main_ctrl_grp)
    
    #point constraint the middle main ctrl
    main_ctrl_name = f'{side}_{typ}{prefix}Main_ctrl'
    cmds.pointConstraint([f'output_{main_ctrl_name}_0001',f'output_{main_ctrl_name}_0003'],
                          f'driven_{main_ctrl_name}_0002', mo=False)
    #aim constraint the middle main ctrl

    if 'R' in side:
        cmds.aimConstraint(f'output_{main_ctrl_name}_0003',f'driven_{main_ctrl_name}_0002',
                        aimVector=(-1, 0, 0), upVector=(0, 1, 0), worldUpType='None', mo=False)
    else:
        cmds.aimConstraint(f'output_{main_ctrl_name}_0003',f'driven_{main_ctrl_name}_0002',
                    aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType='None', mo=False)


    #create ribbon curve on joint pos 

    if 'R' in side:
        curve = cmds.curve(
            d=3,
            p=[
                (2, 0, 0),
                (1.333333, 0, 0),
                (0, 0, 0),
                (-1.333333, 0, 0),
                (-2, 0, 0)
            ],
            k=[0, 0, 0, 1, 2, 2, 2])
    
    else:
        curve = cmds.curve(
            d=3,
            p=[
                (-2, 0, 0),
                (-1.333333, 0, 0),
                (0, 0, 0),
                (1.333333, 0, 0),
                (2, 0, 0)
            ],
            k=[0, 0, 0, 1, 2, 2, 2]
        )

    curve = cmds.rename(curve, f'{side}_{typ}_curve_0001')
    #rebuild curve to have more CVs for better deformation
    cmds.rebuildCurve(
    curve,
    ch=True,rpo=True,rt=0,end=True,
    kr=False,kcp=False,kep=True,kt=True,
    s=8,d=3,tol=0.01)
    #delete history to clean up construction nodes
    cmds.delete(curve, ch=True)
    cmds.makeIdentity(curve, apply=True, t=1, r=1, s=1, n=0)
    cmds.xform(curve, piv=(0, 0, 0), ws=True)
    curve_up = cmds.duplicate(curve, name=f'{side}_{typ}Up_curve_0001')[0]
    if 'R' in side:
        cmds.setAttr(f'{curve_up}.translateY',-0.5)
    else:    
        cmds.setAttr(f'{curve_up}.translateY',0.5)
    cmds.makeIdentity(curve_up, apply=True, t=1, r=1, s=1, n=0)
    cmds.xform(curve_up, piv=(0, 0, 0), ws=True)
    #bind skin to curve
    for c in curve,curve_up:

        skin_cluster = cmds.skinCluster(j1, j2, j3, c, tsb=True)[0]
        #set weight 
        weight_template = {

        0: (1.000, 0.000, 0.000),
        1: (1.000, 0.000, 0.000),
        2: (0.900, 0.100, 0.000),
        3: (0.500, 0.500, 0.000),
        4: (0.100, 0.900, 0.000),
        5: (0.000, 1.000, 0.000),
        6: (0.000, 0.900, 0.100),
        7: (0.000, 0.500, 0.500),
        8: (0.000, 0.100, 0.900),
        9: (0.000, 0.000, 1.000),
        10:(0.000, 0.000, 1.000),}


        cmds.setAttr(f"{skin_cluster}.normalizeWeights", 0)


        for i in weight_template:

            weights = weight_template[i]

            cmds.skinPercent(
                skin_cluster,
                f"{c}.cv[{i}]",
                transformValue=[
                    (j1, weights[0]),
                    (j2, weights[1]),
                    (j3, weights[2])
                ]
            )
    #create joints on curve using uvPin
    minor_grp= create_joints_on_uvPin(curve, curve_up, num_joints=num_joints, prefix=prefix,
                           ctrl_instance=minor_ctrl_instance,color_index=minor_ctrl_color_index,side=side)
    #orginize the outliner
    ribbon_grp = cmds.createNode('transform', name=f'{side}_{typ}{prefix}_grp')
    cmds.parent(main_ctrl_grp, ribbon_grp)
    cmds.parent(curve, curve_up, minor_grp, ribbon_grp)
    return ribbon_grp


def get_param_on_curve(curve, target):
    pos = cmds.xform(target, q=True, ws=True, t=True)

    sel = om.MSelectionList()
    sel.add(curve)
    dag = sel.getDagPath(0)

    curveFn = om.MFnNurbsCurve(dag)
    point = om.MPoint(pos)

    # 更穩
    _, param = curveFn.closestPoint(point, space=om.MSpace.kWorld)

    return param


def ribbon_squash_stretch(ribbon_grp, target_ctrl=None, scale_source=None):

    side = ribbon_grp.split('_')[0]
    prefix = ribbon_grp.split('_')[1]
    part = prefix.replace('Ribbon', '')

    # =========================
    # ATTRIBUTES
    # =========================
    cmds.addAttr(target_ctrl, ln=f'{part}VolumePreserve', at='bool', dv=0, k=1)
    cmds.addAttr(target_ctrl, ln=f'{part}VolumeY', at='float', dv=0.5, k=1)
    cmds.addAttr(target_ctrl, ln=f'{part}VolumeZ', at='float', dv=0.5, k=1)
    cmds.addAttr(target_ctrl, ln=f'{part}VolumeCentered', at='float', min=0, max=1, dv=1, k=1)
    cmds.addAttr(target_ctrl, ln=f'{part}Center', at='float', min=0, max=1, dv=0.5, k=1)
    cmds.addAttr(target_ctrl, ln=f'{part}Falloff', at='float', min=0.001, dv=0.5, k=1)

    # =========================
    # LENGTH SETUP
    # =========================
    loc_start = cmds.spaceLocator(name=ribbon_grp.replace('_grp', '_start_loc'))[0]
    loc_end = cmds.spaceLocator(name=ribbon_grp.replace('_grp', '_end_loc'))[0]

    cmds.hide(loc_start, loc_end)

    target1 = cmds.ls(f'output_{side}_{prefix}Main_ctrl_0001', l=True)[0]
    target2 = cmds.ls(f'output_{side}_{prefix}Main_ctrl_0003', l=True)[0]

    cmds.parent(loc_start, target1)
    cmds.parent(loc_end, target2)

    cmds.setAttr(loc_start + ".translate", 0, 0, 0)
    cmds.setAttr(loc_end + ".translate", 0, 0, 0)

    dist_node = cmds.createNode('distanceBetween', name=f'{side}_{part}_distanceBetween')
    cmds.connectAttr(loc_start + ".worldPosition[0]", dist_node + ".point1")
    cmds.connectAttr(loc_end + ".worldPosition[0]", dist_node + ".point2")

    original_length = cmds.getAttr(dist_node + ".distance")

    rig_scale_md = cmds.createNode('multiplyDivide', name=f'{side}_{part}_rigscale_md')
    cmds.setAttr(rig_scale_md + ".operation", 1)
    cmds.setAttr(rig_scale_md + ".input1X", original_length)
    cmds.connectAttr(scale_source + ".scaleX", rig_scale_md + ".input2X")

    stretch_md = cmds.createNode('multiplyDivide', name=f'{side}_{part}_stretch_md')
    cmds.setAttr(stretch_md + ".operation", 2)
    cmds.connectAttr(dist_node + ".distance", stretch_md + ".input1X")
    cmds.connectAttr(rig_scale_md + ".outputX", stretch_md + ".input2X")

    squash_md = cmds.createNode('multiplyDivide', name=f'{side}_{part}_squash_md')
    cmds.setAttr(squash_md + ".operation", 2)
    cmds.connectAttr(rig_scale_md + ".outputX", squash_md + ".input1Y")
    cmds.connectAttr(rig_scale_md + ".outputX", squash_md + ".input1Z")
    cmds.connectAttr(dist_node + ".distance", squash_md + ".input2Y")
    cmds.connectAttr(dist_node + ".distance", squash_md + ".input2Z")

    power = cmds.createNode('multiplyDivide', name=f'{side}_{part}_power')
    cmds.setAttr(power + ".operation", 3)
    cmds.connectAttr(squash_md + ".outputY", power + ".input1Y")
    cmds.connectAttr(squash_md + ".outputZ", power + ".input1Z")
    cmds.connectAttr(f"{target_ctrl}.{part}VolumeY", power + ".input2Y")
    cmds.connectAttr(f"{target_ctrl}.{part}VolumeZ", power + ".input2Z")

    con = cmds.createNode('condition', name=f'{side}_{part}_volumePreserve_con')
    cmds.connectAttr(f"{target_ctrl}.{part}VolumePreserve", con + ".firstTerm")
    cmds.setAttr(con + ".secondTerm", 1)
    cmds.connectAttr(stretch_md + ".outputX", con + ".colorIfTrueR")
    cmds.connectAttr(power + ".outputY", con + ".colorIfTrueG")
    cmds.connectAttr(power + ".outputZ", con + ".colorIfTrueB")

    # =========================
    # JOINT LOOP
    # =========================
    minor_jnt_grp = f'{side}_{prefix}Minor_jnt_grp'
    minor_jnts = cmds.listRelatives(minor_jnt_grp, children=True)
    print(minor_jnts)

    curve = f'{side}_{part}_curve_0001'

    for i, jnt in enumerate(minor_jnts):

        param = get_param_on_curve(curve, jnt)

        # center distance
        center_dist = cmds.createNode("plusMinusAverage", name=f"{side}_{part}_centerDist_{i+1:04d}")
        cmds.setAttr(center_dist + ".operation", 2)
        cmds.setAttr(center_dist + ".input1D[0]", param)
        cmds.connectAttr(f"{target_ctrl}.{part}Center", center_dist + ".input1D[1]")

        # abs
        abs_node = cmds.createNode("multiplyDivide", name=f"{side}_{part}_abs_{i+1:04d}")
        cmds.setAttr(abs_node + ".operation", 3)
        cmds.connectAttr(center_dist + ".output1D", abs_node + ".input1X")
        cmds.setAttr(abs_node + ".input2X", 2)

        # remap
        remap = cmds.createNode("remapValue", name=f"{side}_{part}_remap_{i+1:04d}")
        cmds.connectAttr(abs_node + ".outputX", remap + ".inputValue")
        cmds.setAttr(remap + ".inputMin", 0)
        cmds.connectAttr(f"{target_ctrl}.{part}Falloff", remap + ".inputMax")

        cmds.setAttr(remap + ".value[0].value_Position", 0)
        cmds.setAttr(remap + ".value[0].value_FloatValue", 1)
        cmds.setAttr(remap + ".value[1].value_Position", 1)
        cmds.setAttr(remap + ".value[1].value_FloatValue", 0)

        # squash offset
        minusY = cmds.createNode("plusMinusAverage", name=f"{side}_{part}_minusY_{i+1:04d}")
        cmds.setAttr(minusY + ".operation", 2)
        cmds.connectAttr(con + ".outColorG", minusY + ".input1D[0]")
        cmds.setAttr(minusY + ".input1D[1]", 1)

        minusZ = cmds.createNode("plusMinusAverage", name=f"{side}_{part}_minusZ_{i+1:04d}")
        cmds.setAttr(minusZ + ".operation", 2)
        cmds.connectAttr(con + ".outColorB", minusZ + ".input1D[0]")
        cmds.setAttr(minusZ + ".input1D[1]", 1)

        # multiply
        mult = cmds.createNode("multiplyDivide", name=f"{side}_{part}_mult_{i+1:04d}")
        cmds.connectAttr(minusY + ".output1D", mult + ".input1Y")
        cmds.connectAttr(minusZ + ".output1D", mult + ".input1Z")
        cmds.connectAttr(remap + ".outValue", mult + ".input2Y")
        cmds.connectAttr(remap + ".outValue", mult + ".input2Z")

        # add back
        add = cmds.createNode("plusMinusAverage", name=f"{side}_{part}_add_{i+1:04d}")
        cmds.connectAttr(mult + ".outputY", add + ".input2D[0].input2Dx")
        cmds.connectAttr(mult + ".outputZ", add + ".input2D[0].input2Dy")

        cmds.setAttr(add + ".input2D[1].input2Dx", 1)
        cmds.setAttr(add + ".input2D[1].input2Dy", 1)

        # blend
        bc = cmds.createNode("blendColors", name=f"{side}_{part}_bc_{i+1:04d}")
        cmds.connectAttr(f"{target_ctrl}.{part}VolumeCentered", bc + ".blender")
        cmds.connectAttr(add + ".output2Dx", bc + ".color1G")
        cmds.connectAttr(add + ".output2Dy", bc + ".color1B")
        cmds.connectAttr(con + ".outColorG", bc + ".color2G")
        cmds.connectAttr(con + ".outColorB", bc + ".color2B")


        # output
        ctrl = f"driven_{side}_{prefix}Minor_ctrl_{i+1:04d}"

        cmds.connectAttr(bc + ".outputG", ctrl + ".scaleY", force=True)
        cmds.connectAttr(bc + ".outputB", ctrl + ".scaleZ", force=True)

def connect_twist_joint_to_ribbon(side='L',typ=None,prefix='Ribbon'):
    for i in range (5):
        i=i+1
        twist = f'{side}_{typ}TwistBind_joint_000{i}'
        connect_ribbon = f'connect_{side}_{typ}{prefix}Minor_ctrl_000{i}'
        cmds.connectAttr(f'{twist}.rotateX',f'{connect_ribbon}.rotateX')

def copy_curve_skin_L_to_R(source_curve, target_curve,source_side='L',target_side='R'):
    
    def get_skin(obj):
        h = cmds.listHistory(obj)
        s = cmds.ls(h, type='skinCluster')
        return s[0] if s else None

    source_skin = get_skin(source_curve)
    target_skin = get_skin(target_curve)

    if not source_skin or not target_skin:
        print("Missing skinCluster")
        return

    source_infs = cmds.skinCluster(source_skin, q=True, inf=True)
    target_infs = cmds.skinCluster(target_skin, q=True, inf=True)

    # close normalize
    cmds.setAttr(target_skin + ".normalizeWeights", 0)

    spans = cmds.getAttr(source_curve + ".spans")
    degree = cmds.getAttr(source_curve + ".degree")
    cv_count = spans + degree

    for i in range(cv_count):

        weights = cmds.skinPercent(
            source_skin,
            f"{source_curve}.cv[{i}]",
            q=True,
            v=True
        )
        #clean up 
        for inf in target_infs:
            cmds.skinPercent(
                target_skin,
                f"{target_curve}.cv[{i}]",
                transformValue=[(inf, 0)]
            )

        for inf, w in zip(source_infs, weights):

            new_inf = inf.replace(source_side, target_side, 1)

            if new_inf in target_infs:

                cmds.skinPercent(
                    target_skin,
                    f"{target_curve}.cv[{i}]",
                    transformValue=[(new_inf, w)]
                )

    cmds.setAttr(target_skin + ".normalizeWeights", 1)