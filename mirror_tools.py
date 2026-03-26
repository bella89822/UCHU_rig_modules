import maya.cmds as cmds
import maya.mel as mel
def mirror_ctrl(mode='normal'): 
    '''mode(str):
        normal : for usual joint mirroring(normal condition for limbs)
        mirrorX : for opposite X axis mirroring (for maybe face)
        posX : for position only mirroring(for pv or blend ctrl)'''
    selection = cmds.ls(selection=True,type='transform')
    if not selection:
        cmds.warning("Please select top controller grp.")
        return

    left_ctrl_grp = selection[0]
    
    if not 'L' in left_ctrl_grp:
        cmds.warning("Only L-side mirroring supported.")
        return

    #if type=transform
    # 1️ duplicate controller
    duplicated_ctrl_grp = cmds.duplicate(left_ctrl_grp, name=left_ctrl_grp)[0]

    # use maya search replace name
    cmds.select(duplicated_ctrl_grp, replace=True)
    
    mel.eval('searchReplaceNames "L" "R" "hierarchy";')

    # rename to R
    renamed_ctrl = duplicated_ctrl_grp.replace("L", "R")

    # fix the string number
    L_parts=left_ctrl_grp.split('_')
    top_prefix=L_parts[0]
    L_side=L_parts[1]
    L_string=L_parts[4]
    R_parts = renamed_ctrl.split("_")
    R_parts[4]=L_string

    
    right_ctrl_grp = "_".join(R_parts)

    # rename
    right_ctrl_grp = cmds.rename(renamed_ctrl, right_ctrl_grp)
    #clean up the constraints and ikhandles for the duplicated ctrl grp
    con_types = ['parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint','aimConstraint']
    for con_type in con_types:
        cons = cmds.listRelatives(right_ctrl_grp, ad=True, type=con_type) or []
        if cons:
            cmds.delete(cons)


    descendants = cmds.listRelatives(right_ctrl_grp, ad=True, type='transform') or []
    right_ctrl_grp = cmds.ls(right_ctrl_grp,shortNames=True) + list(reversed(descendants))
    
    
    right_ctrl_grp=[n for n in right_ctrl_grp 
                    if n.split('|')[-1].startswith(top_prefix)and 'Constraint' not in n and cmds.objExists(n)]
    for grp in right_ctrl_grp:
        grp_short = grp.split('|')[-1]
        parts=grp_short.split("_")
        prefix=parts[0]
        R_side=parts[1] #right side
        part=parts[2]
        typ=parts[3]
        number=parts[4]
        original_parent=None
        if 'ctrl' in typ:
            print('ctrl grp found' )
            if mode == 'normal':
                print('hi')
                pos_joint=cmds.createNode('joint',name=f'L_{part}_tmp_pos')
                cmds.matchTransform(pos_joint,f'{prefix}_{L_side}_{part}_{typ}_{number}')
                mirror_joint = cmds.mirrorJoint(
                    pos_joint,
                    mirrorYZ=True,
                    mirrorBehavior=True,
                    searchReplace=("L", "R")
                )[0]

                cmds.matchTransform(grp, mirror_joint)
                cmds.delete(pos_joint,mirror_joint)
                #list children and change the translate value to negative
                children = cmds.listRelatives(grp, allDescendents=True, type='transform') or []
                for child in children:
                    for axis in ['translateX','translateY','translateZ']:
                        val = cmds.getAttr(f'{child}.{axis}')
                        cmds.setAttr(f'{child}.{axis}', -val)
            elif mode == 'mirrorX':

                if cmds.listRelatives(grp_short,p=True):
                    original_parent=cmds.listRelatives(grp_short,p=True)[0]
                    grp=cmds.parent(grp,world=True)[0]

                pos_loc=cmds.spaceLocator(name=f'L_{part}_tmp_pos')
                cmds.matchTransform(pos_loc,grp_short.replace('R','L'))
                grp = cmds.createNode('transform')
                cmds.parent(pos_loc,grp)
                cmds.setAttr(f'{grp}.scaleX',-1)
                cmds.parent(pos_loc,world=True)
                pos_joint = cmds.createNode('joint')
                cmds.matchTransform(pos_joint,pos_loc)
                cmds.setAttr(f'{pos_joint}.scaleX',1)
                
        
                cmds.matchTransform(grp_short, pos_joint)               
                if original_parent:
                    cmds.parent(grp,original_parent)
                cmds.delete(pos_joint,pos_loc,grp)
            elif mode == 'posX':
                original_parent=None
                if cmds.listRelatives(grp_short,p=True):
                    original_parent=cmds.listRelatives(grp_short,p=True)[0]
                    grp=cmds.parent(grp,world=True)[0]

                pos_joint=cmds.createNode('joint',name=f'L_{part}_tmp_pos')
                cmds.matchTransform(pos_joint,grp_short.replace('R','L'))
                tx = cmds.getAttr(f'{pos_joint}.translateX')
                cmds.setAttr(f'{pos_joint}.translateX', -tx)
                cmds.matchTransform(grp_short, pos_joint)
                
                if original_parent:
                    cmds.parent(grp,original_parent)
                cmds.delete(pos_joint)
            left_ctrl = f'{L_side}_{part}_{typ}_{number}'
            right_ctrl = left_ctrl.replace('L','R')
            shape_L_list = cmds.listRelatives(left_ctrl, shapes=True)or[]
            shape_R_list = cmds.listRelatives(right_ctrl, shapes=True)or[]
            for shape_L, shape_R in zip(shape_L_list, shape_R_list):
                # correct the shape 
                for cv in cmds.ls(f'{shape_L}.cv[*]', flatten=True):
                    pos = cmds.xform(cv, q=True, t=True, ws=True)
                    cv_r = cv.replace(shape_L, shape_R)
                    cmds.xform(cv_r, t=[-pos[0], pos[1], pos[2]], ws=True)

                cmds.setAttr(f'{shape_R}.lineWidth', 2)
                #set red color for R ctrl
                cmds.setAttr(f'{shape_R}.overrideEnabled',1)
                cmds.setAttr(f'{shape_R}.overrideColor',13) #red color

                sub_L = left_ctrl.replace('ctrl','subctrl')
                print(sub_L)
                if cmds.objExists(sub_L):
                    print('sub ctrl exists')
                    sub_shape_L_list = cmds.listRelatives(sub_L, shapes=True, fullPath=True)or[]
                    sub_R = sub_L.replace('L','R')
                    sub_shape_R_list = cmds.listRelatives(sub_R, shapes=True, fullPath=True)or[]
                    for sub_shape_L, sub_shape_R in zip(sub_shape_L_list, sub_shape_R_list):
                        cmds.connectAttr(f'{right_ctrl}.subCtrlVis', f'{sub_shape_R}.visibility', force=True)
                        cmds.setAttr(f'{sub_shape_R}.lineWidth', 1)
                        cmds.setAttr(f'{sub_shape_R}.overrideEnabled',1)
                        cmds.setAttr(f'{sub_shape_R}.overrideColor',13) #red color
                        for cv in cmds.ls(f'{sub_shape_L}.cv[*]', flatten=True):
                            pos = cmds.xform(cv, q=True, t=True, ws=True)
                            cv_r = cv.replace(sub_shape_L, sub_shape_R)
                            cmds.xform(cv_r, t=[-pos[0], pos[1], pos[2]], ws=True)



def mirror_joint_ctrl():
    selection = cmds.ls(selection=True, type='joint')
    if not selection:
        cmds.warning("Please select a joint.")
        return

    left_ctrl = selection[0]
    if not left_ctrl.startswith('L_'):
        cmds.warning("Only L-side mirroring supported.")
        return
    #unparent ctrl from grp 
    cmds.parent(left_ctrl, world=True)
    # mirror joint 
    right_ctrl = cmds.mirrorJoint(
        left_ctrl,
        mirrorYZ=True,
        mirrorBehavior=True,
        searchReplace=("L_", "R_")
    )[0]
    #parent ctrl back to grp
    cmds.parent(left_ctrl, f'connect_{left_ctrl}')
    # renew shape
    shape_L = cmds.listRelatives(left_ctrl, shapes=True, path=True) or []
    shape_R = cmds.listRelatives(right_ctrl, shapes=True, path=True) or []

    if shape_L and shape_R:
        shape_L = shape_L[0]
        shape_R = shape_R[0]
        for cv in cmds.ls(f"{shape_L}.cv[*]", flatten=True):
            pos = cmds.xform(cv, q=True, ws=True, t=True)
            cv_r = cv.replace(shape_L, shape_R)
            cmds.xform(cv_r, ws=True, t=[-pos[0], pos[1], pos[2]])
        cmds.setAttr(f"{shape_R}.lineWidth", 2)

    # sub ctrl mirror
    sub_L = left_ctrl.replace('ctrl', 'subctrl')
    if cmds.objExists(sub_L):
        sub_shape_L = cmds.listRelatives(sub_L, shapes=True, path=True)[0]
        sub_R = sub_L.replace('L_', 'R_')
        if cmds.objExists(sub_R):
            sub_shape_R = cmds.listRelatives(sub_R, shapes=True, path=True)[0]
            for cv in cmds.ls(f"{sub_shape_L}.cv[*]", flatten=True):
                pos = cmds.xform(cv, q=True, ws=True, t=True)
                cv_r = cv.replace(sub_shape_L, sub_shape_R)
                cmds.xform(cv_r, ws=True, t=[-pos[0], pos[1], pos[2]])
            cmds.setAttr(f"{sub_shape_R}.lineWidth", 1)
            if cmds.attributeQuery('subCtrlVis', node=right_ctrl, exists=True):
                cmds.connectAttr(f"{right_ctrl}.subCtrlVis", f"{sub_shape_R}.visibility", f=True)

    # create zero/driven/connect hierarchy
    parent = None
    top_node = None
    for prefix in ['zero', 'driven', 'connect']:
        grp_name = f"{prefix}_{right_ctrl}"
        node = cmds.createNode('transform', name=grp_name)
        cmds.matchTransform(node, right_ctrl, pos=True, rot=False)
        if parent:
            cmds.parent(node, parent)
        else:
            top_node = node
        parent = node

    cmds.parent(right_ctrl, parent)
    cmds.delete(right_ctrl, constructionHistory=True)

    cmds.select(top_node)
    print(f"Mirrored joint hierarchy created: {top_node}")




def mirror_joint_with_grps():
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("Please select a grp.")
        return


    for sel in selection:
        parts = sel.split('_')
        prefix = parts[0]
        side = parts[1]
        part = parts[2]
        typ = parts[3]
        number = parts[4]
        if side != 'L':
            cmds.warning("Only L-side mirroring supported.")
            return
        
        #create pos joint and then mirror
        pos_joint=cmds.createNode('joint',name=f'L_tmp_pos')
        cmds.matchTransform(pos_joint,sel)
        mirror_joint_pos = cmds.mirrorJoint(
            pos_joint,
            mirrorYZ=True,
            mirrorBehavior=True,
            searchReplace=("L", "R")
        )[0]
        
        R_joint_grp = cmds.duplicate(sel, name=f'{prefix}_R_{part}_{typ}_{number}')[0]
        #also rwename the children
        cmds.select(R_joint_grp,replace=True)
        mel.eval('searchReplaceNames "L" "R" "hierarchy";')
        #match the pos
        cmds.matchTransform(R_joint_grp, mirror_joint_pos)
        cmds.delete(pos_joint,mirror_joint_pos)
        #clean up the constraints
        con_types = ['parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint','aimConstraint']
        for con_type in con_types:
            cons = cmds.listRelatives(R_joint_grp, ad=True, type=con_type) or []
            if cons:
                cmds.delete(cons)



def mirror_sdk():
    #select driven obj
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("Please select at least one driven object.")
        return
    for L_driven in selection:
        R_driven = L_driven.replace('L_', 'R_')
        if not cmds.objExists(R_driven):
            cmds.warning(f"{R_driven} does not exist.")
            continue
        # get keyable attr 
        attrs = cmds.listAttr(L_driven, keyable=True) or []
        for attr in attrs:
            L_driven_plug = f'{L_driven}.{attr}'
            all_curves = []
            #find sdk curve
            L_driven_curves = cmds.listConnections(L_driven_plug, s=True, d=False,scn =True) or []
            if len(L_driven_curves)==0:
                continue
            for node in L_driven_curves:
                if cmds.nodeType(node) == 'animCurve':
                    all_curves.append(node)
                else:
                    #search for the other animCurve connected to the node
                    sub_curves = cmds.listConnections(f'{node}.input', type='animCurve', s=True, d=False,scn=True) or []
                    all_curves.extend(sub_curves)


            for crv in list(set(all_curves)):
                driver_connections = cmds.listConnections(f'{crv}.input', plugs=True, s=True, d=False,scn=True)
                print(driver_connections)
                if driver_connections:
                    source_plug = driver_connections[0]
                L_driver_plug = source_plug
                if not driver_connections:
                    continue
                R_driver_plug = L_driver_plug.replace('L','R')
                print(R_driver_plug)
                #ensure R driver exists, if not create attribute
                R_driver_node, R_driver_attr = R_driver_plug.split('.')
                if not cmds.objExists(R_driver_node):
                    continue
                base_attr = R_driver_attr.split('[')[0]
                if not cmds.attributeQuery(base_attr, node=R_driver_node, exists=True):
                    print('plz check if R side driver attr exists')

                    
 
                #get keyframe and recreate on R side
                R_driven_plug = f'{R_driven}.{attr}'
                keys = cmds.keyframe(crv, query=True, indexValue=True)or []
                for i in keys:
                    dv = cmds.keyframe(crv, index=(i,i), query=True, floatChange=True)[0]
                    v = cmds.keyframe(crv, index=(i,i), query=True, valueChange=True)[0]
                    #set sdk
                    if attr in ['translateX','translateY','translateZ']:
                        #special case for translate, only translates are opposite
                        cmds.setDrivenKeyframe(R_driven_plug, cd=R_driver_plug, dv=dv, v=-v)
                    else:
                        cmds.setDrivenKeyframe(R_driven_plug, cd=R_driver_plug, dv=dv, v=v)
                    # cd: current driver 
                    # dv: driver value
                    # v: driven value  

def mirror_constraint(target_list=None):
    '''target_list(list): the top grps of driven ctrls'''
    if not target_list:
        print("target list doesn't exist ")

        return
    
    for target in target_list:

        all_children = cmds.listRelatives(target,ad=True)or[]
        all_nodes = [target]+ all_children[::-1]
        for node in all_nodes:
            # find constraint
            cons = cmds.listRelatives(node,type = 'constraint',children=True)

            if not cons:
                continue 

            for con in cons:
                if cmds.nodeType(con) == 'parentConstraint':
                    drivers = cmds.parentConstraint(con,q=True,targetList=True)
                
                elif cmds.nodeType(con) =='orientConstraint':
                    drivers = cmds.orientConstraint(con,q=True,targetList=True)
                
                elif cmds.nodeType(con) =='pointConstraint':
                    drivers = cmds.pointConstraint(con,q=True,targetList=True)


                R_drivers = [driver.replace('L','R') for driver in drivers]
                if drivers[0].startswith('C'):
                    R_drivers=drivers
                R_node = node.replace('L','R')
                print(R_drivers)
                if all (cmds.objExists(d) for d in R_drivers) and cmds.objExists(R_node):
                    con_type = cmds.nodeType(con)

                    if con_type == 'parentConstraint':
                        new_con = cmds.parentConstraint(R_drivers,R_node,mo=True)[0]
                        cmds.setAttr(f'{new_con}.interpType',2)
                    elif con_type == 'orientConstraint':
                        new_con = cmds.orientConstraint(R_drivers,R_node,mo=True)[0]
                        cmds.setAttr(f'{new_con}.interpType',2)
                    elif con_type == 'pointConstraint':
                        new_con = cmds.pointConstraint(R_drivers,R_node,mo=True)[0]


                    for i, driver in enumerate(drivers):
                        try:
                            w = cmds.getAttr(f"{con}.{driver}W{i}")

                            cmds.setAttr(f"{new_con}.{R_drivers}W{i}",w)

                        except:
                            pass






    

