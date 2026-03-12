import maya.cmds as cmds
import rig_modules.controller_shape as cs
import rig_modules.mirror_tools as mr



        #create rest of the joints
def create_feather_joints(root_ctrl_ins='root_ctrl', feather_ctrl_ins='feather_ctrl'):
    '''root_ctrl_ins(str)    : the controller shape instance for the feather root ctrl
       feather_ctrl_ins(str) : the controller shape instance for the feather ctrls
       '''
    vtx_indices=[167,158,152,146]
    geo_grps = cmds.ls(selection=True)
    if not geo_grps:
        cmds.warning("Please select at least one geometry group.")
        return
    if not cmds.objExists(root_ctrl_ins) or not cmds.objExists(feather_ctrl_ins):
        cmds.warning("Please make sure both root_ctrl and feather_ctrl exist in the scene.")
        return
    for geo_grp in geo_grps:
        geo_list = cmds.listRelatives(geo_grp, allDescendents=True, type='mesh')
        ctrl_grp = cmds.createNode('transform', name=geo_grp.replace('geo','ctrl'))
        jnt_grp = cmds.createNode('transform', name=geo_grp.replace('geo','jnt'))
        for geo in geo_list:
            bind_joints=[]
            #define the name
            side = geo.split('_')[0]
            part = geo.split('_')[1]
            #get second joint
            root_pos = cmds.xform(f'{geo}.vtx[144]', q=True, ws=True, t=True)
            second_pos = cmds.xform(f'{geo}.vtx[161]', q=True, ws=True, t=True)

            root_joint = cmds.createNode('joint', name=f'{side}_{part}Root_joint_0001')
            cmds.xform(root_joint, ws=True, t=root_pos)
            cmds.matchTransform(root_joint, geo, rot=True)
            second_jnt = cmds.createNode('joint', name=f'{side}_{part}_joint_0001')
            cmds.xform(second_jnt, ws=True, t=second_pos)
            cmds.matchTransform(second_jnt, geo, rot=True)

            
            aimCon = cmds.aimConstraint(second_jnt, root_joint, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType=2,
                                        worldUpObject=second_jnt, worldUpVector=(0,1,0),mo=False)
            
            cmds.delete(aimCon)
            cmds.parent(second_jnt, root_joint)
            cmds.makeIdentity(root_joint, apply=True, rotate=True)
            cmds.makeIdentity(second_jnt, apply=True, rotate=True)
            cmds.joint(second_jnt, edit=True, orientJoint='xyz', secondaryAxisOrient='yup', zeroScaleOrient=True)

            bind_joints.append(root_joint)
            bind_joints.append(second_jnt)

            
            for j, vtx_index in enumerate(vtx_indices):
                parent_jnt = second_jnt if j == 0 else cmds.ls(selection=True)[0]
                vtx_pos = cmds.xform(f'{geo}.vtx[{vtx_index}]',q=True,ws=True,t=True)
                jnt = cmds.createNode('joint', name=f'{side}_{part}_joint_{j+2:04}')
                cmds.xform(jnt, ws=True, t=vtx_pos)
                #orient joint by using aim constraint
                if j!= len(vtx_indices):
                    aimCon = cmds.aimConstraint(jnt, parent_jnt, 
                                    aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType=4,
                                    worldUpVector=(0,1,0),mo=False)[0]
                    cmds.delete(aimCon)
                    cmds.makeIdentity(parent_jnt, apply=True, rotate=True)

                if j!= len(vtx_indices)-1:
                    bind_joints.append(jnt)
                cmds.parent(jnt, parent_jnt)
                    

                #if last joint zero the joint orientation
                if j == len(vtx_indices)-1:
                    cmds.setAttr(f'{jnt}.jointOrientX', 0)
                    cmds.setAttr(f'{jnt}.jointOrientY', 0)  
                    cmds.setAttr(f'{jnt}.jointOrientZ', 0)
                parent_jnt = jnt
            #bind the joints to the geo
            cmds.skinCluster(bind_joints, geo, toSelectedBones=True, maximumInfluences=3, normalizeWeights=1)
            #create ctrl for feather root joint
            cmds.select(root_joint)
            cs.create_ctrl_from_shape(root_ctrl_ins)
            root_ctrl = root_joint.replace('joint','ctrl')
            cmds.select(root_ctrl)
            cs.create_ctrlgrp_on_ctrl()
            root_ctrl_shape = cmds.listRelatives(root_ctrl, shapes=True)[0]
            cmds.setAttr(f"{root_ctrl_shape}.overrideColor", 18)
            root_subctrl = root_ctrl.replace('ctrl','subctrl')
            root_subctrl_shape = cmds.listRelatives(root_subctrl, shapes=True)[0]
            cmds.setAttr(f"{root_subctrl_shape}.overrideColor", 18)
            cmds.parentConstraint(f'output_{root_ctrl}', root_joint, mo=False)
            #create ctrl for the feathers 
            parent_ctrl = root_ctrl
            for  jnt in bind_joints[1:]:
                cmds.select(jnt)
                cs.create_ctrl_from_shape(feather_ctrl_ins)
                feather_ctrl = jnt.replace('joint','ctrl')
                cmds.select(feather_ctrl)
                cs.create_ctrlgrp_on_ctrl()
                cmds.parent(f'zero_{feather_ctrl}', f'output_{parent_ctrl}')
                cmds.parentConstraint(f'output_{feather_ctrl}', jnt, mo=False)
                parent_ctrl = feather_ctrl
            #parent the root ctrl under ctrl grp and  joint to joint grp 
            cmds.parent(f'zero_{root_ctrl}', ctrl_grp)
            cmds.parent(root_joint, jnt_grp)

def feather_weight_transfer(instance=None):
    '''instance(str) : the skinCluster instance to transfer weights from'''
    geo_grp = cmds.ls(selection=True)
    if not geo_grp:
        cmds.warning("Please select at least one geometry group.")
        return
    if not instance:
        cmds.warning("Please provide a valid skinCluster instance name.")
        return
    geo_grp_list= cmds.listRelatives(geo_grp,children=True,fullPath=False) or []
    for geo in geo_grp_list:
        skin_clusters = cmds.ls(cmds.listHistory(geo), type='skinCluster')
        if not skin_clusters:
            cmds.warning(f"No skinCluster found on {geo}.")
            continue
        skin_cluster = skin_clusters[0]
        cmds.copySkinWeights(ss=instance, ds=skin_cluster, noMirror=True, surfaceAssociation='closestPoint', 
                             influenceAssociation=[ 'closestJoint'])
    print("Weight transfer completed.")

def wing_spread_constraint(parentA=None, parentB=None,con_type='orient'):
    '''parentA(str) : the first parent for the constraint
       parentB(str) : the second parent for the constraint
       con_type(str): the type of constraint ('orient' or 'parent')'''
    sel_ctrls=cmds.ls(selection=True)
    if not sel_ctrls:
        cmds.warning("Please select at least one wing joint.")
        return
    if not parentA or not parentB:
        cmds.warning("Please provide both parentA and parentB for the constraint.")
        return
    for i ,ctrl in enumerate(sel_ctrls):
        if con_type=='orient':
            o_con = cmds.orientConstraint(parentA, parentB, f'driven_{ctrl}', mo=True)[0]
            cmds.setAttr(f'{o_con}.interpType', 2)
        elif con_type=='parent':
            o_con = cmds.parentConstraint(parentA, parentB, f'driven_{ctrl}', mo=True)[0]
            cmds.setAttr(f'{o_con}.interpType', 2)
        weight_value_B = i / (len(sel_ctrls) - 1) if len(sel_ctrls) > 1 else 0
        weight_value_A= 1 - weight_value_B
        cmds.setAttr(f'{o_con}.w0', weight_value_A)
        cmds.setAttr(f'{o_con}.w1', weight_value_B)


def create_loc_for_uvPin(curve=None,curve_up = None):
    '''select the feather ctrls first
       curve(str)     : the main curve to attach the locs on    
       curve_up(str)  : the up curve for the uv pin '''
    sels = cmds.ls(selection=True)
    if not sels:
        cmds.warning("Please select at least one feather ctrl.")
        return  
     #create uv pin 
    uvPin = cmds.createNode('uvPin', name=curve.replace('curve','uvPin'))
    cmds.connectAttr(f'{curve}.worldSpace', f'{uvPin}.deformedGeometry', force=True)
    cmds.connectAttr(f'{curve_up}.worldSpace', f'{uvPin}.railCurve', force=True)
    #adjust the attr for the uv pin
    cmds.setAttr(f'{uvPin}.tangentAxis',1) #Y axis
    cmds.setAttr(f'{uvPin}.normalAxis',2) #Z axis
    cmds.setAttr(f'{uvPin}.normalOverride',1) #use rail curve
    aimLoc_grp = cmds.createNode('transform', name=curve.replace('curve','aimLoc_grp'))
    for i, sel in enumerate(sels):
        #create loc for aim constraint
        aim_Loc = cmds.spaceLocator(name=sel.replace('ctrl','aimLoc'))[0]
        #find param first 
        para = 1.0 * i / (len(sels) - 1) if len(sels) > 1 else 0.0
        #connect to uv pin
        cmds.setAttr(f'{uvPin}.coordinate[{i}].coordinateU', para)
        cmds.connectAttr(f'{uvPin}.outputMatrix[{i}]', f'{aim_Loc}.offsetParentMatrix', force=True)
        #aim constraint the feather ctrl to the loc
        cmds.aimConstraint(aim_Loc, f'driven_{sel}', aimVector=(1, 0, 0), 
                           upVector=(0, 1, 0), worldUpType=4,
                            worldUpVector=(0,1,0),mo=True)
        cmds.parent(aim_Loc, aimLoc_grp)


def constraint_by_curve(curve=None, ctrl = 'CV_ctrl'):
    '''select parent first ,child last(plz select joint)
    ctrl(str) : the ctrl to instance create the ctrls
       curve(str) : the curve to attach the items on'''
    sels = cmds.ls(selection=True)
    if len(sels) < 3:
        cmds.warning("Please select at least three items: parent first, child last.")
        return  
    parentA_jnt = sels[0]
    parentB_jnt = sels[1]
    children_jnt = sels[2]
    #create ctrl for the cv joints
    cmds.select(parentA_jnt,parentB_jnt,children_jnt)
    ctrl_list = cs.create_ctrl_from_shape(ctrl)
    for ctrl in ctrl_list:
        cmds.select(ctrl)
        cs.create_ctrlgrp_on_ctrl()
    children = 'zero_' + children_jnt.replace('joint','ctrl')  
    POCI = cmds.createNode('pointOnCurveInfo', name=curve.replace('curve','POCI'))
    cmds.connectAttr(f'{curve}.worldSpace', f'{POCI}.inputCurve', force=True)
    cmds.setAttr(f'{POCI}.turnOnPercentage',1)
    #find param for the child
    cmds.setAttr(f'{POCI}.parameter', 0.5)
    
    cmds.connectAttr(f'{POCI}.position', f'{children}.translate', force=True)
    #parent the joint under the output transform 
    parentA_output = 'output_' + parentA_jnt.replace('joint','ctrl')
    parentB_output = 'output_' + parentB_jnt.replace('joint','ctrl') 
    children_output = 'output_' + children_jnt.replace('joint','ctrl')
    cmds.parent(children_jnt, children_output)
    cmds.parent(parentA_jnt, parentA_output)
    cmds.parent(parentB_jnt, parentB_output)       
    #hide joints
    cmds.setAttr(f'{parentA_jnt}.visibility',0) 
    cmds.setAttr(f'{parentB_jnt}.visibility',0)
    cmds.setAttr(f'{children_jnt}.visibility',0)

def create_loc_on_curve(curve=None,num_loc=6):
    '''curve(str) : the curve to attach the locs on'''
    side = curve.split('_')[0]
    part = curve.split('_')[1]  

    for i in range(num_loc):
        loc = cmds.spaceLocator(name=f'{side}_{part}_loc_{i+1:02}')[0]
        POCI = cmds.createNode('pointOnCurveInfo', name=curve.replace('curve','POCI')+f'_{i+1:02}')
        cmds.connectAttr(f'{curve}.worldSpace', f'{POCI}.inputCurve', force=True)
        cmds.setAttr(f'{POCI}.turnOnPercentage',1)
        para = 1.0 * i / (num_loc - 1) if num_loc > 1 else 0.0
        cmds.setAttr(f'{POCI}.parameter', para)
        cmds.connectAttr(f'{POCI}.position', f'{loc}.translate', force=True)

def add_curl_for_feather(ctrl=None,typ=None):
    '''ctrl(str) : the feather ctrl to add curl attribute
       typ(str)  : the type of curl attribute('primary','secondary','tertiary')'''
    if not ctrl:
        cmds.warning("Please provide a valid feather ctrl.")
        return
    if typ not in ['primary','secondary','tertiary','tail']:
        cmds.warning("Please provide a valid type: 'primary','secondary','tertiary'.")
        return
    attr_name = f'featherCurl'
    if not cmds.attributeQuery(attr_name, node=ctrl, exists=True):
        cmds.addAttr(ctrl, longName=attr_name, attributeType='float',defaultValue=0.0, keyable=True)
        print(f'Curl attribute added to {ctrl}.')

    ctrl_side = ctrl.split('_')[0]
    if 'L' in ctrl_side:
        ctrl_side='L'
        feather_side = ['LU','L','LD']
    elif 'R' in ctrl_side:
        ctrl_side='R'
        feather_side = ['RU','R','RD']
    all_feather_ctrls=[]
    all_root_ctrls=[]
    for side in feather_side:
        all_ctrls = cmds.ls(f'{side}_{typ}*_ctrl_*',type='transform')
        for c in all_ctrls:
            if 'Root' in c:
                all_root_ctrls.append(c)
            else:
                all_feather_ctrls.append(c)
    typ_root_ctrls = list(set(all_root_ctrls))
    typ_root_ctrls.sort()
    typ_feather_ctrls = []
    #add root rotateZ connection 
    for position in ['Middle','Up','Down']:
        for axis in ['X','Y','Z']:
            if not cmds.attributeQuery(f'{position}Rot{axis}', node=ctrl, exists=True):
                cmds.addAttr(ctrl, longName=f'{position}Rot{axis}', attributeType='float',defaultValue=0.0, keyable=True)

    #connect position attr to each root ctrl connect grp 

    for  root_ctrl in typ_root_ctrls:
        if f'{ctrl_side}_' in root_ctrl:
            cmds.connectAttr(f'{ctrl}.MiddleRotX',f'connect_{root_ctrl}.rotateX' , force=True)
            cmds.connectAttr(f'{ctrl}.MiddleRotY',f'connect_{root_ctrl}.rotateY' , force=True)
            cmds.connectAttr(f'{ctrl}.MiddleRotZ',f'connect_{root_ctrl}.rotateZ' , force=True)
        elif f'{ctrl_side}U_' in root_ctrl:
            cmds.connectAttr(f'{ctrl}.UpRotX',f'connect_{root_ctrl}.rotateX' , force=True)
            cmds.connectAttr(f'{ctrl}.UpRotY',f'connect_{root_ctrl}.rotateY' , force=True)
            cmds.connectAttr(f'{ctrl}.UpRotZ',f'connect_{root_ctrl}.rotateZ' , force=True)
        elif f'{ctrl_side}D_' in root_ctrl:
            cmds.connectAttr(f'{ctrl}.DownRotX',f'connect_{root_ctrl}.rotateX' , force=True)
            cmds.connectAttr(f'{ctrl}.DownRotY',f'connect_{root_ctrl}.rotateY' , force=True)
            cmds.connectAttr(f'{ctrl}.DownRotZ',f'connect_{root_ctrl}.rotateZ' , force=True)
        
        



    for feather_ctrl in all_feather_ctrls:
        #clean up the string number
        feather_ctrl = feather_ctrl.split('_')[0] + '_' + feather_ctrl.split('_')[1] + '_' + feather_ctrl.split('_')[2]
        typ_feather_ctrls.append(feather_ctrl)

    typ_feather_ctrls = list(set(typ_feather_ctrls))
    typ_feather_ctrls.sort()
    
    for  feather_ctrl in typ_feather_ctrls:
        #create multiply divide node
        multi = cmds.createNode('multiplyDivide', name=feather_ctrl.replace('ctrl','curl_multi'))
        for axis in ['X','Y','Z']:
            cmds.connectAttr(f'{ctrl}.{attr_name}', f'{multi}.input1{axis}', force=True)
        cmds.setAttr(f'{multi}.input2X', 0.75)
        cmds.setAttr(f'{multi}.input2Y', 0.5)
        cmds.setAttr(f'{multi}.input2Z', 0.25)
        cmds.connectAttr(f'{ctrl}.{attr_name}',f'connect_{feather_ctrl}_0001.rotateZ' , force=True)
        cmds.connectAttr(f'{multi}.outputX',f'connect_{feather_ctrl}_0002.rotateZ' , force=True)
        cmds.connectAttr(f'{multi}.outputY',f'connect_{feather_ctrl}_0003.rotateZ' , force=True)
        cmds.connectAttr(f'{multi}.outputZ',f'connect_{feather_ctrl}_0004.rotateZ' , force=True)


def mirror_feather_ctrls( typ=None):
    '''mirror the feather ctrls from L to R side
       typ(str) : the type of feather('primary','secondary','tertial','alula')'''
    if typ not in ['primary','secondary','tertial','alula']:
        cmds.warning("Please provide a valid type: 'primary','secondary','tertia1")
        return
    
    L_feather_ctrl_grps = cmds.ls(f'offset_LU_{typ}*_ctrl_*',type='transform')
    L_feather_ctrl_grps += cmds.ls(f'offset_L_{typ}*_ctrl_*',type='transform') 
    L_feather_ctrl_grps += cmds.ls(f'offset_LD_{typ}*_ctrl_*',type='transform')
    print(L_feather_ctrl_grps)
    for L_ctrl_grp in L_feather_ctrl_grps:
        cmds.select(L_ctrl_grp)
        mr.mirror_ctrl('normal')
        prefix = L_ctrl_grp.split('_')[0]
        side = L_ctrl_grp.split('_')[1]
        part = L_ctrl_grp.split('_')[2]
        function = L_ctrl_grp.split('_')[3]
        string_num = L_ctrl_grp.split('_')[-1]
        L_ctrl = f'{side}_{part}_{function}_{string_num}'
        R_ctrl = L_ctrl.replace('L','R')
        output_R_ctrl = f'output_{R_ctrl}'
        #constraint the joints
        feather_jnt = R_ctrl.replace('ctrl','joint')


        cmds.parentConstraint(output_R_ctrl, feather_jnt, mo=False)


    
