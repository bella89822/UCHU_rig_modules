import maya.cmds as cmds
import rig_modules.controller_shape as cs
def create_connect_fitBspline():
    curves=cmds.ls(selection=True)
    for curve in curves:
        fitBspline = cmds.createNode("fitBspline", name = curve.replace("curve","fitBspline"))
        curve = cmds.listRelatives(curve, shapes = True)[0]
        # connect curve local to fitBspline input curve
        cmds.connectAttr(f"{curve}.local", f"{fitBspline}.inputCurve")
import maya.api.OpenMaya as om
import maya.cmds as cmds


def get_param_on_curve(curve, position):

    sel = om.MSelectionList()
    sel.add(curve)

    dag = sel.getDagPath(0)

    curveFn = om.MFnNurbsCurve(dag)

    point = om.MPoint(position)

    param = curveFn.closestPoint(point, space=om.MSpace.kWorld)[1]

    return param


def create_loc_on_param(curve):

    vrts = cmds.ls(sl=True, flatten=True)
    vrts.sort()

    vrtPara = []

    # naming prefix
    side = curve.split('_')[0]
    part = curve.split('_')[1]

    grp = cmds.group(em=True, name=f"{side}_{part}_loc_grp")

    # -------- get parameters --------
    for vrt in vrts:

        vrtPos = cmds.pointPosition(vrt, world=True)

        parameter = get_param_on_curve(curve, vrtPos)

        vrtPara.append((vrt, parameter))

    # sort along curve
    vrtPara.sort(key=lambda x: x[1])

    # -------- create locators --------
    for i, (vrt, para) in enumerate(vrtPara):

        prefix = f"{side}_{part}_param_{i+1:04}"

        loc = cmds.spaceLocator(
            name=prefix.replace("param", "loc")
        )[0]

        cmds.parent(loc, grp)

        poci = cmds.createNode(
            "pointOnCurveInfo",
            name=f"{prefix}_POCI"
        )

        # keep raw parameter
        cmds.setAttr(f"{poci}.turnOnPercentage", 0)

        cmds.setAttr(f"{poci}.parameter", para)

        # connect curve
        cmds.connectAttr(
            f"{curve}.worldSpace[0]",
            f"{poci}.inputCurve",
            force=True
        )

        # connect locator
        cmds.connectAttr(
            f"{poci}.position",
            f"{loc}.translate",
            force=True
        )


#this one is for eyelid
def aim_at(center_loc,up_loc):
    if not center_loc or not up_loc:
        cmds.warning('Please type in center loc and  up loc.')
        return
    #prevent wrong order
    center_locY = cmds.getAttr(f"{center_loc}.translateY")
    up_locY = cmds.getAttr(f"{up_loc}.translateY")
    if center_locY > up_locY:
        cmds.warning('Center locator is above the up locator.')
        return
    loc_grp =cmds.ls(selection=True,type='transform')
    locs = cmds.listRelatives(loc_grp, ad=True, type='transform')
    if not loc_grp:
        cmds.warning('Please select a loc_grp.')
        return
    
    #create grp for aim loc
    side=locs[0].split('_')[0]
    part=locs[0].split('_')[1]    
    aim_grp = cmds.group( em = True, name = f"{side}_{part}_aimloc_grp" )
    for loc in locs:
        aimLoc = cmds.createNode("transform" , name = loc.replace("loc","aimLoc"))
        cmds.matchTransform(aimLoc , center_loc)

        cmds.aimConstraint(loc, aimLoc , worldUpObject = up_loc)
        jnt = cmds.createNode("joint" , name = loc.replace("loc","bindJoint") )
        cmds.matchTransform(jnt , loc)
        cmds.parent(jnt, aimLoc)
        cmds.parent(aimLoc, aim_grp)





import maya.cmds as cmds 
def connect_ctrl_to_shape(curve=None):
    ctrls=cmds.ls(selection=True,type='transform')
    if not curve:
        cmds.warning('Please select a curve.')
        return
    for i , ctrl in enumerate(ctrls):
        side=ctrl.split('_')[0]
        part=ctrl.split('_')[1]
        string = ctrl.split('_')[-1]
        output='output_'+ctrl
        # create multimatrix and decompose node
        cmds.createNode('multMatrix',name=f'{side}_{part}_multiMatrix_{string}')
        cmds.createNode('decomposeMatrix',name=f'{side}_{part}_decomposeMatrix_{string}')


        #connect ctrl to multMatrix and then decompose Matrix 
        cmds.connectAttr(f'{output}.worldMatrix[0]',f'{side}_{part}_multiMatrix_{string}.matrixIn[0]',force=True)
        cmds.connectAttr(f'{side}_{part}_multiMatrix_{string}.matrixSum',f'{side}_{part}_decomposeMatrix_{string}.inputMatrix',force=True)

        #connect decompose to curve control vertices
        cmds.connectAttr(f'{side}_{part}_decomposeMatrix_{string}.outputTranslate',f'{curve}.controlPoints[{i}]',force=True)



def lip_roll_aim_constraint():
    loc_grp = cmds.ls(selection=True,type='transform')
    locs = cmds.listRelatives(loc_grp, ad=True, type='transform')
    #organize
    locs.sort()
    for loc in locs:
        aim_loc = loc.replace('Lip','LipRoll')
        #create aim constraint node
        aim_con = cmds.createNode("aimConstraint", name=loc.replace("loc","aimCon"))

        #connection
        #lip roll loc to aim target
        cmds.connectAttr(aim_loc + ".translate", aim_con + ".target[0].targetTranslate",force=True)
        #lip loc t to constraint translate
        cmds.connectAttr(loc + ".translate", aim_con + ".constraintTranslate",force=True)
        #aimCon constraint rotate
        cmds.connectAttr(aim_con + ".constraintRotate",loc + ".rotate",force=True)

        #attributes
        #aimVector
        cmds.setAttr(aim_con + ".aimVector", 0, 1, 0)

        #up vector
        cmds.setAttr(aim_con + ".upVector", 0, 0, 0)

        #world up vector
        cmds.setAttr(aim_con + ".worldUpVector", 1, 0, 0)

        #world up type
        cmds.setAttr(aim_con + ".worldUpType", 3)



def create_joint_from_loc():
    loc_grp =cmds.ls(selection=True,type='transform')[0]
    locs = cmds.listRelatives(loc_grp, ad=True, type='transform')
    jnt_grp = cmds.createNode('transform', name=loc_grp.replace("loc","jnt"))
    #organize
    locs.sort()
    for loc in locs:

        jnt=cmds.createNode('joint',name=loc.replace("loc","bindjoint"))
        zero = cmds.createNode('transform', name=f'zero_{jnt}')
        driven = cmds.createNode('transform',name=zero.replace('zero','driven'))
        cmds.parent(jnt, driven)
        cmds.parent(driven,zero)
        cmds.connectAttr(loc + ".translate", zero + ".translate",force=True)
        cmds.connectAttr(loc + ".rotate", zero + ".rotate",force=True)
        cmds.parent(zero, jnt_grp)

import maya.cmds as cmds
import maya.api.OpenMaya as om

def normalize_curve_parameter(curve):

    shape = cmds.listRelatives(curve, shapes=True)[0]

    spans = cmds.getAttr(f"{shape}.spans")
    degree = cmds.getAttr(f"{shape}.degree")

    cmds.rebuildCurve(
        curve,
        ch=0,
        rpo=1,
        rt=0,
        end=1,
        kr=0,
        kcp=1,
        kep=1,
        kt=0,
        s=spans,
        d=degree,
        tol=0.01
    )


def get_param_on_curve(curve, position):

    sel = om.MSelectionList()
    sel.add(curve)

    dag = sel.getDagPath(0)
    curveFn = om.MFnNurbsCurve(dag)

    point = om.MPoint(position)

    param = curveFn.closestPoint(point, space=om.MSpace.kWorld)[1]

    return param


def attach_zero_to_curve_poci(ctrl_grp, curve):
    normalize_curve_parameter(curve)

    shape = cmds.listRelatives(curve, shapes=True)[0]

    # 找所有 zero groups
    zeros = cmds.listRelatives(ctrl_grp, ad=True, type="transform")

    zeros = [z for z in zeros if z.startswith("zero_")]

    for zero in zeros:

        pos = cmds.xform(zero, q=True, ws=True, t=True)

        param = get_param_on_curve(curve, pos)

        poci = cmds.createNode(
            "pointOnCurveInfo",
            name=zero.replace("zero", "POCI")
        )

        cmds.connectAttr(
            f"{shape}.worldSpace[0]",
            f"{poci}.inputCurve",
            force=True
        )

        cmds.setAttr(f"{poci}.turnOnPercentage", 0)

        cmds.setAttr(f"{poci}.parameter", param)

        cmds.connectAttr(
            f"{poci}.position",
            f"{zero}.translate",
            force=True
        )

        print(f"{zero} connected to curve param {param}")




def create_and_connect_joints_on_locs():
    locs=cmds.ls(selection=True,type='transform')
    locs.sort()
    for loc in locs:
        jnt=cmds.createNode('joint',name=loc.replace("loc","joint"))
        cmds.connectAttr(loc + ".translate", jnt + ".translate",force=True)
        cmds.connectAttr(loc + ".rotate", jnt + ".rotate",force=True)


def lip_roll_ctrl_parent():
    zero_lipRoll = cmds.ls(selection=True,type='transform')
    for zero in zero_lipRoll:
        output_lipRoll = zero.replace('zero','output')
        zero_lip = zero.replace('lipRoll','lip') 
        cmds.parent(zero_lip, output_lipRoll)

def add_lip_roll_attr():
    lipRoll_ctrls = cmds.ls(selection=True,type='transform')

    for lipRoll in lipRoll_ctrls:
        #delete sub ctrls
        cmds.select(lipRoll)
        cs.remove_sub_ctrl()
        #hide ctrl shape
        cmds.select(lipRoll)
        cs.hide_shape()
        lip_ctrl = lipRoll.replace('lipRoll','lip')
        #delete lip sub ctrl 
        cmds.select(lip_ctrl)
        cs.remove_sub_ctrl()
        #add lipRoll attribute
        if not cmds.attributeQuery('lipRoll', node=lip_ctrl, exists=True):
            cmds.addAttr(lip_ctrl, longName='lipRoll', attributeType='float', min=-10, max=10, defaultValue=0, keyable=True)
        lipRoll_attr = f"{lip_ctrl}.lipRoll"
        #create remap node
        remap = cmds.createNode('remapValue', name=lipRoll.replace('_ctrl','_remap'))
        #set remap node value
        cmds.setAttr(f"{remap}.inputMin", 10)
        cmds.setAttr(f"{remap}.inputMax", -10)
        cmds.setAttr(f"{remap}.outputMin", -45)
        cmds.setAttr(f"{remap}.outputMax", 45)
        #connect them 
        cmds.connectAttr(lipRoll_attr, f"{remap}.inputValue", force=True)
        cmds.connectAttr(f"{remap}.outValue", f"{lipRoll}.rotateX", force=True)



def constraint_and_falloff(defaultV=0.5,driver_typ=None,output=True):
    '''driver_typ (str):parentConstraint/pointConstraint/orientConstraint/scaleConstraint'''
    sels = cmds.ls(selection=True, type='transform')
    if output == True:
        driverA = f'{sels[0]}'
        driverB = f'{sels[1]}'
        driven = f'driven_{sels[2]}'
        driven_ctrl = sels[2]
    elif output == False:
        driverA = f'driven_{sels[0]}'
        driverB = f'driven_{sels[1]}'
        driven = f'driven_{sels[2]}'
        driven_ctrl = sels[2]
    #driver type list out 
    driver_types = ['parentConstraint','pointConstraint','orientConstraint','scaleConstraint']
    if driver_typ not in driver_types:
        cmds.warning('Please type in a valid driver type:parentConstraint/pointConstraint/orientConstraint/scaleConstraint')
        return
    #constaint the driven #support multiple constraint types
    if 'pointConstraint'in driver_typ:
        cmds.pointConstraint(driverA,driverB, driven, maintainOffset=True)
    elif 'orientConstraint' in driver_typ:
        cmds.orientConstraint(driverA,driverB, driven, maintainOffset=True)
    elif 'scaleConstraint' in driver_typ:
        cmds.scaleConstraint(driverA,driverB, driven, maintainOffset=True)
    elif 'parentConstraint' in driver_typ:                                 
        cmds.parentConstraint(driverA,driverB, driven, maintainOffset=True,skipRotate=['x','y','z'])
    #create fall off attribute
    if not cmds.attributeQuery('fallOff', node=driven_ctrl, exists=True):
        cmds.addAttr(driven_ctrl, longName='fallOff', attributeType='float', min=0, max=1, defaultValue= defaultV, keyable=True)
    #create reverse node and connect fall off to the constraint node
    reverse = cmds.createNode('reverse', name=f"{driven}_falloff_reverse")
    cmds.connectAttr(f"{driven_ctrl}.fallOff", f"{reverse}.inputX", force=True)
    cmds.connectAttr(f"{reverse}.outputX", f"{driven}_parentConstraint1.{driverB}W1", force=True)
    cmds.connectAttr(f'{driven_ctrl}.fallOff', f"{driven}_parentConstraint1.{driverA}W0", force=True)



def attach_joints_on_curve(drive_curve, aim_curve, up_object, aim_type):
    '''Attach joints to a curve with POCI
    drive_curve(str):the curve drive the joints
    aim_curve(str): the curve for the aiming nodes
    up_object(str):joints' ref up obj
    aim_type(str):obj/curve'''
    #get name parts 
    joints = cmds.ls(selection = True,type='transform')
    joints = cmds.listRelatives(joints, children=True, type='joint')
    #split names for the curve and name the grps
    side = drive_curve.split('_')[0]
    drive_part = drive_curve.split('_')[1]
    #aim type
    if aim_type =='curve':
        curves = [drive_curve,aim_curve,up_object]
    else:
        curves = [drive_curve,aim_curve]
    #create rig nodes group
    jnt_grp = cmds.createNode('transform', name=f"{side}_{drive_part}_jnt_grp")
    rig_nodes = cmds.createNode('transform', name=f"{side}_{drive_part}_rigNodes")
    #create grps to classify all our stuffs 
    attaches_grp = []
    for crv,part_name in zip(curves,['Drive','Aim','Up']):
        grp_attach = cmds.createNode('transform', 
                                     name=f"{side}_{drive_part}{part_name}_attach_grp",parent=rig_nodes)
        attaches_grp.append(grp_attach)
        #parent curves to node grp
        cmds.parent(crv, rig_nodes)

    #get fitBspline
    curve_shapes = []
    for crv in curves:
        if cmds.objExists(crv.replace('curve','fitBspline')):
            curve_shapes.append(crv.replace('curve','fitBspline'))
        else:
            cmds.createNode('fitBspline', name=crv.replace('curve','fitBspline'))
            cmds.connectAttr(crv + ".local", crv.replace('curve','fitBspline') + ".inputCurve", force=True)
            curve_shapes.append(crv.replace('curve','fitBspline'))
        # set fitBspline keep range 0 to 1
        cmds.setAttr(f"{crv.replace('curve','fitBspline')}.keepRange", 0)
        #set fitBspline tolerence
        cmds.setAttr(f"{crv.replace('curve','fitBspline')}.tolerance", 0.001)
    #attach joints on curve
    for jnt in joints :
        jnt_side = jnt.split('_')[0]
        jnt_part = jnt.split('_')[1]
        jnt_string = jnt.split('_')[-1]
        #get closest param on curve
        npoc = cmds.createNode('nearestPointOnCurve')
        jntPos = cmds.xform(jnt, q=True, ws=True, t=True)
        print(jntPos)
        cmds.setAttr(f"{npoc}.inPositionX", jntPos[0])
        cmds.setAttr(f"{npoc}.inPositionY", jntPos[1])
        cmds.setAttr(f"{npoc}.inPositionZ", jntPos[2])
        #connect curve to npoc node to get param data
        print(curve_shapes[0])
        cmds.connectAttr(f"{curve_shapes[0]}.outputCurve", f"{npoc}.inputCurve", force=True)
        param = cmds.getAttr(f"{npoc}.parameter")
        #delete the npoc
        cmds.disconnectAttr(f"{curve_shapes[0]}.outputCurve", f"{npoc}.inputCurve")
        cmds.delete(npoc)

        
        #create attach nodes
        attach_nodes=[]
        for curve_shape, part_name , grp in zip(curve_shapes, ['Drive','Aim','Up'], attaches_grp):
            attach_node = cmds.createNode('transform',
                                           name=f"{jnt_side}_{jnt_part}{part_name}Attach_grp_{jnt_string}")
            poci = cmds.createNode('pointOnCurveInfo', name=attach_node.replace('grp','poci'))
            cmds.setAttr(f"{poci}.turnOnPercentage", 1)
            cmds.setAttr(f"{poci}.parameter", param)
            cmds.connectAttr(f"{curve_shape}.outputCurve", f"{poci}.inputCurve", force=True)
            cmds.connectAttr(f"{poci}.result.position",f"{attach_node}.translate", force=True)
            attach_nodes.append(attach_node)

            
        #aim constraint the attachment 
        if aim_type=='curve':
            cmds.aimConstraint(attach_nodes[1], attach_nodes[0], aimVector=(1, 0, 0), 
                               upVector=(0, 1, 0), worldUpType="object", worldUpObject=attach_nodes[2],mo=False)
        else:
            cmds.aimConstraint(attach_nodes[1], attach_nodes[0], aimVector=(1, 0, 0), 
                               upVector=(0, 1, 0), worldUpType="object", worldUpObject=up_object,mo=False)
       
        #create joint zero grp and driven grp 

        jnt_zero_grp = cmds.createNode('transform', name=f'zero_{jnt}')
        cmds.parentConstraint(attach_nodes[0], jnt_zero_grp, maintainOffset=False)
        #create another layer for maybe zip or other stuff just in case   
        jnt_driven_grp = cmds.createNode('transform', name=f'driven_{jnt}')
        cmds.matchTransform(jnt_driven_grp, jnt, position=True, rotation=True)
        cmds.parent(jnt_driven_grp, jnt_zero_grp)
        cmds.parent(jnt,jnt_driven_grp)
        #orient joint to the driven grp's orientation 
        cmds.matchTransform(jnt, jnt_driven_grp, position=False, rotation=True)
        cmds.makeIdentity(jnt, apply=True, translate=True, rotate=True, scale=True)
        #put the zero in jnt grp
        cmds.parent(jnt_zero_grp, jnt_grp)
        #orginize nodes
        for attach_node, grp in zip(attach_nodes, attaches_grp):
            cmds.parent(attach_node, grp)

def create_zip_lip(left_ctrl=None,right_ctrl=None,jaw_ctrl=None,zip_height=0.5,fallOff=3):
    upper_jnts = cmds.ls(selection=True)
    downer_jnts = [jnt.replace('Upper','Downer') for jnt in upper_jnts]
    #add attr for the ctrls
    for ctrl in [left_ctrl, right_ctrl]:
        if ctrl:
            cmds.addAttr(ctrl, longName='zip', attributeType='float', minValue=0, 
                         maxValue=10, defaultValue=0,keyable=True)
    cmds.addAttr(jaw_ctrl, longName='zipHeight', attributeType='float', minValue=0, 
                 maxValue=1, defaultValue=zip_height,keyable=True)
    #get joint number for zip weight
    jnts_num = len(upper_jnts)
    zip_weight = 1/float(jnts_num) if jnts_num > 0 else 0
    #create grp for zip locs
    zip_grp = cmds.createNode('transform', name='zip_grp')
    #create rev node for the zip height
    zip_height_rev = cmds.createNode('reverse', name='zip_height_rev')
    cmds.connectAttr(f'{jaw_ctrl}.zipHeight', f'{zip_height_rev}.inputX')
    #loop for each joints
    i=1
    for upper_jnt,downer_jnt in zip(upper_jnts,downer_jnts):
        #define parts
        zero_jnt=f'zero_{upper_jnt}'
        driven_jnt = f'driven_{upper_jnt}'
        down_jnt = downer_jnt
        zero_down_jnt = f'zero_{down_jnt}'
        driven_down_jnt = f'driven_{down_jnt}'
        #create locator for the zip 
        upper_loc = cmds.spaceLocator(name=upper_jnt.replace('joint','loc'))[0]
        cmds.matchTransform(upper_loc, upper_jnt, position=True, rotation=True)
        cmds.parent(upper_loc,zero_jnt)
        down_loc = cmds.spaceLocator(name=down_jnt.replace('joint','loc'))[0]
        cmds.matchTransform(down_loc, down_jnt, position=True, rotation=True)
        cmds.parent(down_loc,zero_down_jnt)
        zip_loc = cmds.spaceLocator(name=upper_jnt.replace('joint','loc').replace('Upper','Zip'))[0]
        cmds.parent(zip_loc,zip_grp)
        height_con = cmds.parentConstraint(upper_loc, down_loc, zip_loc, maintainOffset=False)[0]
        cmds.setAttr(f'{height_con}.interpType', 2)
        cmds.connectAttr(f'{jaw_ctrl}.zipHeight',f'{height_con}.{upper_loc}W0')
        cmds.connectAttr(f'{zip_height_rev}.outputX', f'{height_con}.{down_loc}W1')
        #create remap node for left and right zip attr 
        remap_L = cmds.createNode('remapValue', name=upper_jnt.replace('joint','remap').replace('Upper','ZipWeight'))
        remap_R = cmds.createNode('remapValue', name=upper_jnt.replace('joint','remap').replace('Upper','ZipWeight'))
        #commect the remap to the zip 
        cmds.connectAttr(f'{left_ctrl}.zip', f'{remap_L}.inputValue')
        cmds.connectAttr(f'{right_ctrl}.zip', f'{remap_R}.inputValue')
        #set remap ramp node for L and R 
        cmds.setAttr(f'{remap_L}.value[0].value_Position', max([0,zip_weight*(i-fallOff)]))
        cmds.setAttr(f'{remap_L}.value[1].value_Position', zip_weight*i)
        cmds.setAttr(f'{remap_R}.value[0].value_Position', max([0,zip_weight*(jnts_num-i+1-fallOff)]))
        cmds.setAttr(f'{remap_R}.value[1].value_Position', zip_weight*(jnts_num-i+1))
        #sum and clamp the weight
        add = cmds.createNode('addDoubleLinear', name=upper_jnt.replace('joint','add').replace('Upper','ZipWeight'))
        cmds.connectAttr(remap_L + '.outValue', add + '.input1')
        cmds.connectAttr(remap_R + '.outValue', add + '.input2')

        clamp = cmds.createNode('clamp', name=add.replace('add','clamp'))
        cmds.connectAttr(add + '.output', clamp + '.inputR')
        cmds.setAttr(clamp + '.maxR', 1)


        #get reverse weight 
        rvs = cmds.createNode('reverse', name=clamp.replace('clamp','reverse'))
        cmds.connectAttr(clamp + '.outputR', rvs + '.inputX')

        #blend lip joint 
        parent_con_up = cmds.straint(zip_loc,driven_jnt,upper_jnt, maintainOffset=False)[0]
        cmds.setAttr(f'{parent_con_up}.interpType', 2)
        parent_con_down = cmds.parentConstraint(zip_loc,driven_down_jnt, down_jnt, maintainOffset=False)[0]
        cmds.setAttr(f'{parent_con_down}.interpType', 2)
        cmds.connectAttr(clamp + '.outputR', f'{parent_con_up}.{zip_loc}W0', force=True)
        cmds.connectAttr(rvs + '.outputX', f'{parent_con_up}.{driven_jnt}W1', force=True)
        cmds.connectAttr(clamp + '.outputR', f'{parent_con_down}.{zip_loc}W0', force=True)
        cmds.connectAttr(rvs + '.outputX', f'{parent_con_down}.{driven_down_jnt}W1', force=True)
        i+=1
        


