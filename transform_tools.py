import maya.cmds as cmds

def create_locator(loc_name=None):
    sels = cmds.ls(selection=True)

    for obj in sels:
        side= obj.split('_')[0]
        part= obj.split('_')[1]
        string = obj.split('_')[-1]
        loc = cmds.spaceLocator(name=f'{side}_{part}_match_{string}')[0]
        #create zero grp on top 
        zero_grp = cmds.group(loc, name=f'zero_{loc}')
        cmds.matchTransform(zero_grp, obj)
        cmds.parent(zero_grp, obj)
        #hide locator
        cmds.hide(loc)

    if loc_name:
        cmds.rename(loc, loc_name)


def match_fkik_ts():
    sel = cmds.ls(selection=True)[0]
    side = 'L' if sel.startswith('L') else "R"
    S = side

    ctrlFK_list = [f'{S}_upperarmFK_ctrl_0001',
                   f'{S}_elbowFK_ctrl_0001',
                   f'{S}_wristFK_ctrl_0001']
    ctrlIK_list = [f'{S}_wristIK_ctrl_0001']

    if sel in ctrlIK_list:
        #match fk to ik 
        rot_upperarm = cmds.xform(f'{S}_upperarm_joint_0001', q=True, rotation=True, worldSpace=True)
        rot_elbow    = cmds.xform(f'{S}_elbow_joint_0001',    q=True, rotation=True, worldSpace=True)
        rot_wrist    = cmds.xform(f'{S}_wrist_joint_0001',    q=True, rotation=True, worldSpace=True)

         #rotate the scapula and clavicle for the pose reader
        #1 get the rot info first
        rot_clavicle = cmds.xform(f'{S}_clavicle_joint_0001',q= True, rotation=True, worldSpace=True)
        rot_scapula = cmds.xform(f'{S}_scapula_joint_0001',q= True, rotation=True, worldSpace=True)
        #match rotation to the ik
        cmds.xform(f'{S}_upperarmFK_ctrl_0001', rotation=rot_upperarm, worldSpace=True)
        cmds.xform(f'{S}_elbowFK_ctrl_0001',    rotation=rot_elbow,    worldSpace=True)
        cmds.xform(f'{S}_wristFK_ctrl_0001',    rotation=rot_wrist,    worldSpace=True)
        #set it to fk mode
        cmds.setAttr(f'{S}_armFKIKBlend_ctrl_0001.ikFkBlend', 0)
        #2 rotate the clavicle and scapula back 
        cmds.xform(f'{S}_clavicle_ctrl_0001', rotation=rot_clavicle, worldSpace=True)
        cmds.xform(f'{S}_scapula_ctrl_0001', rotation=rot_scapula, worldSpace=True)
        # find out the space of the fk ctrl 
        #if the space is clavicle we need to match multiple times to make it correct
        if cmds.getAttr(f'{S}_upperarmFK_ctrl_0001.space') == 1:
            for i in range(10):
                cmds.xform(f'{S}_upperarmFK_ctrl_0001', rotation=rot_upperarm, worldSpace=True)
                cmds.xform(f'{S}_elbowFK_ctrl_0001',    rotation=rot_elbow,    worldSpace=True)
                cmds.xform(f'{S}_wristFK_ctrl_0001',    rotation=rot_wrist,    worldSpace=True)

    elif sel in ctrlFK_list:
        #match ik to fk
        pos_ik = cmds.xform(f'{S}_wrist_joint_0001', q=True, t=True, worldSpace=True)
        rot_ik = cmds.xform(f'{S}_wrist_joint_0001', q=True, rotation=True, worldSpace=True)

        pos_pv = cmds.xform(f'{S}_armIKPV_match_0001', q=True, t=True, worldSpace=True)
        #rotate the scapula and clavicle for the pose reader
        #1 get the rot info first
        rot_clavicle = cmds.xform(f'{S}_clavicle_joint_0001',q= True, rotation=True, worldSpace=True)
        rot_scapula = cmds.xform(f'{S}_scapula_joint_0001',q= True, rotation=True, worldSpace=True)
        #match to the fk 
        cmds.xform(f'{S}_wristIK_ctrl_0001', t=pos_ik, worldSpace=True)
        cmds.xform(f'{S}_wristIK_ctrl_0001', rotation=rot_ik, worldSpace=True)
        cmds.xform(f'{S}_armIKPV_ctrl_0001', t=pos_pv, worldSpace=True)
        #set it to ik mode
        cmds.setAttr(f'{S}_armFKIKBlend_ctrl_0001.ikFkBlend', 1)
        #2 rotate the clavicle and scapula back 
        cmds.xform(f'{S}_clavicle_ctrl_0001', rotation=rot_clavicle, worldSpace=True)
        cmds.xform(f'{S}_scapula_ctrl_0001', rotation=rot_scapula, worldSpace=True)

    else:
        print('plz select an FK or IK ctrl')

   

import maya.cmds as cmds
def export_skeleton():
    sel=cmds.ls(selection=True)
    for skel in sel:
        if 'end' not in skel:
            parts=skel.split('_')
            side=parts[0]
            part=parts[1]
            typ=parts[2]
            string=parts[-1]

            joint_name=f'{side}_{part}_joint_{string}'
            print(joint_name)
            print(skel)
            cmds.pointConstraint(joint_name,skel,mo=False)
            cmds.orientConstraint(joint_name,skel,mo=False)
            cmds.connectAttr(f'{joint_name}.scale',f'{skel}.scale')




def connect_locators_to_controls():
    ctrls= cmds.ls(selection=True)
    for ctrl in ctrls:
        loc=ctrl.replace('ctrl','loc')
        cmds.matchTransform(loc,ctrl)
        for axis in ['X','Y','Z']:
            cmds.connectAttr(f'{ctrl}.translate{axis}',f'{loc}.translate{axis}')
            cmds.connectAttr(f'{ctrl}.rotate{axis}',f'{loc}.rotate{axis}')


def simple_space_switch(typ=None,last_neck=3,constraint_type='parent'):
    if not last_neck:
        raise ValueError("last_neck is not defined or empty.")
    #list 
    arm_list = ['headIK','chestIK','cog','hip','world','clavicle']
    leg_list = ['cog','hip','world']
    head_list = ['neck','chestIK','cog','world']
    scapula_list = ['clavicle','chestIK']
    chest_list = ['pelvis','world']
    #dict the list
    list_dict = {
        'arm': arm_list,
        'leg': leg_list,
        'head': head_list,
        'scapula': scapula_list,
        'chest': chest_list
    }

    space_list = list_dict[typ]
    #warning to avoid dumb dumb 
    if typ not in list_dict:
        cmds.warning(f"Unknown type: {typ}")
        return
    ctrl = cmds.ls(sl=True)[0]
    
    side=ctrl.split('_')[0]
    part=ctrl.split('_')[1]
    #add enum attribute
    cmds.addAttr(ctrl,ln='space',at='enum',en=':'.join(space_list),k=True)
    #create space grp
    cmds.createNode('transform',n=f'space_{ctrl}')
    cmds.matchTransform(f'space_{ctrl}',ctrl)
    cmds.parent(f'connect_{ctrl}',f'space_{ctrl}')
    cmds.parent(f'space_{ctrl}',f'driven_{ctrl}')
    if typ== 'arm' or typ == 'leg':
        for i,item in enumerate(space_list):
            #create locators for the spaces 
            loc = cmds.spaceLocator(name=f'space_{side}_{part}_{item}_loc_0001')[0]
            #zero grp on top
            zero_grp = cmds.createNode('transform', name=f'space_{side}_{part}_{item}_zero_grp_0001')
            cmds.parent(loc, zero_grp)
            #hide the loc 
            cmds.hide(loc)
            #match loc transform to the ctrl
            cmds.matchTransform(zero_grp,ctrl,pos=True,rot=True)
            #parent loc to the part
            if item!='world':
                cmds.parent(zero_grp,f'output_C_{item}_ctrl_0001')
            elif item=='world':
                cmds.parent(zero_grp,f'C_{item}_ctrl_0001')
            #parent constraint the grp from the loc 
            if constraint_type=='parent':
                cmds.parentConstraint(loc,f'space_{ctrl}',mo=False)
            elif constraint_type=='orient':
                cmds.orientConstraint(loc,f'space_{ctrl}',mo=False)





            #connect enum attr to the constraint
            equal=cmds.createNode('equal',name=f'space_{ctrl}_{item}_equal_0001')
            cmds.connectAttr(f'{ctrl}.space',f'{equal}.input1')
            cmds.setAttr(f'{equal}.input2',space_list.index(item))
            cmds.connectAttr(f'{equal}.output',f'space_{ctrl}_parentConstraint1.{loc}W{space_list.index(item)}')
           
    if typ=='scapula':
        for i,item in enumerate(space_list):
            #create locators for the spaces 
            loc = cmds.spaceLocator(name=f'space_{side}_{part}_{item}_loc_0001')[0]
            #zero grp on top
            zero_grp = cmds.group(loc, name=f'space_{side}_{part}_{item}_zero_grp_0001')
            #hide the loc 
            cmds.hide(loc)
            #match loc transform to the ctrl
            cmds.matchTransform(zero_grp,ctrl,pos=True,rot=True)
            #parent loc to the part
            if item!='chestIK':
                cmds.parent(zero_grp,f'output_{side}_{item}_ctrl_0001')
            elif item=='chestIK':
                cmds.parent(zero_grp,f'output_C_{item}_ctrl_0001')
            #orient constraint the grp from the loc
            cmds.orientConstraint(loc,f'space_{ctrl}',mo=False)


            #connect enum attr to the constraint
            equal=cmds.createNode('equal',name=f'space_{ctrl}_{item}_equal_0001')
            cmds.connectAttr(f'{ctrl}.space',f'{equal}.input1')
            cmds.setAttr(f'{equal}.input2',space_list.index(item))
            cmds.connectAttr(f'{equal}.output',f'space_{ctrl}_orientConstraint1.{loc}W{space_list.index(item)}')

    elif typ=='head':
        for item in head_list:
            #create locators for the spaces 
            loc = cmds.spaceLocator(name=f'space_{side}_{part}_{item}_loc_0001')[0]
            #zero grp on top
            zero_grp = cmds.group(loc, name=f'space_{side}_{part}_{item}_zero_grp_0001')
            #match loc transform to the ctrl
            cmds.matchTransform(loc,ctrl,pos=True,rot=True)
            #hide loc
            cmds.hide(loc)
            #parent loc to the part
            if item=='neck':
                cmds.parent(zero_grp,f'output_C_neckBend_ctrl_{last_neck:04d}')

            elif item == 'world':
                cmds.parent(zero_grp,f'C_{item}_ctrl_0001')

            else: 
                cmds.parent(zero_grp,f'output_C_{item}_ctrl_0001')

            #orient constraint the grp from the loc
            cmds.orientConstraint(loc,f'space_{ctrl}',mo=False)


            #connect enum attr to the constraint
            equal=cmds.createNode('equal',name=f'space_{ctrl}_{item}_equal_0001')
            cmds.connectAttr(f'{ctrl}.space',f'{equal}.input1')
            cmds.setAttr(f'{equal}.input2',space_list.index(item))
            cmds.connectAttr(f'{equal}.output',f'space_{ctrl}_orientConstraint1.{loc}W{space_list.index(item)}')
            #create spaceA spaceB switch and blend
            cmds.addAttr(ctrl,ln='spaceA',at='enum',en=':'.join(space_list),k=True)
            cmds.addAttr(ctrl,ln='spaceB',at='enum',en=':'.join(space_list),k=True)
            cmds.addAttr(ctrl,ln='spaceBlend',at='float',min=0,max=1,dv=0,k=True)
            cmds.addAttr(ctrl,ln='spaceBlendT',at='float',min=0,max=1,dv=0,k=True)
            cmds.addAttr(ctrl,ln='spaceBlendR',at='float',min=0,max=1,dv=0,k=True)
    elif typ =='chest':
        for i,item in enumerate(space_list):
            #create locators for the spaces 
            loc = cmds.spaceLocator(name=f'space_{side}_{part}_{item}_loc_0001')[0]
            #zero grp on top
            zero_grp = cmds.createNode('transform', name=f'space_{side}_{part}_{item}_zero_grp_0001')
            cmds.parent(loc, zero_grp)
            #hide the loc 
            cmds.hide(loc)
            #match loc transform to the ctrl
            cmds.matchTransform(zero_grp,ctrl,pos=True,rot=True)
            #parent loc to the part
            if item!='world':
                cmds.parent(zero_grp,f'output_C_{item}_ctrl_0001')
            elif item=='world':
                cmds.parent(zero_grp,f'C_{item}_ctrl_0001')
            #parent constraint the grp from the loc 
            if constraint_type=='parent':
                cmds.parentConstraint(loc,f'space_{ctrl}',mo=False)






            #connect enum attr to the constraint
            equal=cmds.createNode('equal',name=f'space_{ctrl}_{item}_equal_0001')
            cmds.connectAttr(f'{ctrl}.space',f'{equal}.input1')
            cmds.setAttr(f'{equal}.input2',space_list.index(item))
            cmds.connectAttr(f'{equal}.output',f'space_{ctrl}_parentConstraint1.{loc}W{space_list.index(item)}')

def advanced_space_switch(typ=None,last_neck=3):
    if not typ:
        raise ValueError("typ is not defined or empty.")
    #list 
    armIK_list = ['headIK','clavicle','chestIK','cog','world']
    armFK_list = ['clavicle','chestIK','cog','world']
    legIK_list = ['cog','hipIK','world']
    head_list = ['neck','chestIK','cog','world']
    scapula_list = ['chestIK','clavicle']
    #dict the list
    list_dict = {
        'armIK': armIK_list,
        'armFK': armFK_list,
        'legIK': legIK_list,
        'head': head_list,
        'scapula': scapula_list
    }

    space_list = list_dict[typ]
    #warning to avoid dumb dumb 
    if typ not in list_dict:
        cmds.warning(f"Unknown type: {typ}")
        return
    ctrl = cmds.ls(sl=True)[0]
    
    side=ctrl.split('_')[0]
    part=ctrl.split('_')[1]
    #create space grp
    cmds.createNode('transform',n=f'space_{ctrl}')
    cmds.matchTransform(f'space_{ctrl}',ctrl)
    cmds.parent(f'connect_{ctrl}',f'space_{ctrl}')
    cmds.parent(f'space_{ctrl}',f'driven_{ctrl}')
    if typ!='head':
        #create spaceA spaceB switch and blend
        cmds.addAttr(ctrl,ln='spaceA',at='enum',en=':'.join(space_list),k=True)
        cmds.addAttr(ctrl,ln='spaceB',at='enum',en=':'.join(space_list),k=True)
        cmds.addAttr(ctrl,ln='spaceBlend',at='float',min=0,max=1,dv=0,k=True)
        cmds.addAttr(ctrl,ln='spaceBlendT',at='float',min=0,max=1,dv=1,k=True)
        cmds.addAttr(ctrl,ln='spaceBlendR',at='float',min=0,max=1,dv=1,k=True)

        #create choice node
        choicA=cmds.createNode('choice',name=f'space_{ctrl}_choiceA_0001')
        choicB=cmds.createNode('choice',name=f'space_{ctrl}_choiceB_0001')
        #connect attr to choice node
        cmds.connectAttr(f'{ctrl}.spaceA',f'{choicA}.selector')
        cmds.connectAttr(f'{ctrl}.spaceB',f'{choicB}.selector')
        for i,item in enumerate(space_list):
            #create locators for the spaces 
            loc = cmds.spaceLocator(name=f'space_{side}_{part}_{item}_loc_0001')[0]
            #zero grp on top
            zero_grp = cmds.group(loc, name=f'space_{side}_{part}_{item}_zero_grp_0001')
            #hide the loc 
            cmds.hide(loc)
            #match loc transform to the ctrl
            cmds.matchTransform(zero_grp,ctrl,pos=True,rot=True)
            #parent loc to the part
            if item!='world' and item!='clavicle':
                cmds.parent(zero_grp,f'output_C_{item}_ctrl_0001')
            elif item=='world':
                cmds.parent(zero_grp,f'C_{item}_ctrl_0001')
            elif item=='clavicle':
                cmds.parent(zero_grp,f'output_{side}_{item}_ctrl_0001')
           
            #connect the loc to the choice node
            cmds.connectAttr(f'{loc}.worldMatrix[0]',f'{choicA}.input[{i}]')
            cmds.connectAttr(f'{loc}.worldMatrix[0]',f'{choicB}.input[{i}]')
        #create blend matrix node
        blend=cmds.createNode('blendMatrix',name=f'space_{ctrl}_blendMatrix_0001')
        #connect choice node to blend matrix
        cmds.connectAttr(f'{choicA}.output',f'{blend}.inputMatrix')
        cmds.connectAttr(f'{choicB}.output',f'{blend}.target[0].targetMatrix')
        cmds.connectAttr(f'{ctrl}.spaceBlend',f'{blend}.target[0].weight')
        cmds.connectAttr(f'{ctrl}.spaceBlendT',f'{blend}.target[0].translateWeight')
        cmds.connectAttr(f'{ctrl}.spaceBlendR',f'{blend}.target[0].rotateWeight')
        #connect space_grp to inverse matrix
        cmds.createNode('multMatrix',name=f'space_{ctrl}_multMatrix_0001')
        cmds.connectAttr(f'{blend}.outputMatrix',f'space_{ctrl}_multMatrix_0001.matrixIn[0]')
        cmds.connectAttr(f'space_{ctrl}.parentInverseMatrix[0]',f'space_{ctrl}_multMatrix_0001.matrixIn[1]')
        #create decompose matrix
        cmds.createNode('decomposeMatrix',name=f'space_{ctrl}_decomposeMatrix_0001')
        cmds.connectAttr(f'space_{ctrl}_multMatrix_0001.matrixSum',f'space_{ctrl}_decomposeMatrix_0001.inputMatrix')
        #connect translate and rotate
        cmds.connectAttr(f'space_{ctrl}_decomposeMatrix_0001.outputTranslate',f'space_{ctrl}.translate')
        cmds.connectAttr(f'space_{ctrl}_decomposeMatrix_0001.outputRotate',f'space_{ctrl}.rotate')


    elif typ=='head':
         #create spaceA spaceB switch and blend
            cmds.addAttr(ctrl,ln='spaceA',at='enum',en=':'.join(space_list),k=True)
            cmds.addAttr(ctrl,ln='spaceB',at='enum',en=':'.join(space_list),k=True)
            cmds.addAttr(ctrl,ln='spaceBlend',at='float',min=0,max=1,dv=0,k=True)
            cmds.addAttr(ctrl,ln='spaceBlendT',at='float',min=0,max=1,dv=1,k=True)
            cmds.addAttr(ctrl,ln='spaceBlendR',at='float',min=0,max=1,dv=1,k=True)

            #create choice node
            choicA=cmds.createNode('choice',name=f'space_{ctrl}_choiceA_0001')
            choicB=cmds.createNode('choice',name=f'space_{ctrl}_choiceB_0001')
            #connect attr to choice node
            cmds.connectAttr(f'{ctrl}.spaceA',f'{choicA}.selector')
            cmds.connectAttr(f'{ctrl}.spaceB',f'{choicB}.selector')
            for i, item in enumerate(head_list):
           
                #create locators for the spaces 
                loc = cmds.spaceLocator(name=f'space_{side}_{part}_{item}_loc_0001')[0]
                #zero grp on top
                zero_grp = cmds.group(loc, name=f'space_{side}_{part}_{item}_zero_grp_0001')
                #match loc transform to the ctrl
                cmds.matchTransform(zero_grp,ctrl,pos=True,rot=True)
                #hide loc
                cmds.hide(loc)
                #parent loc to the part
                if item=='neck':
                    cmds.parent(zero_grp,f'output_C_neckBend_ctrl_{last_neck:04d}')

                elif item == 'world':
                    cmds.parent(zero_grp,f'C_{item}_ctrl_0001')

                else: 
                    cmds.parent(zero_grp,f'output_C_{item}_ctrl_0001')



                #connect the loc to the choice node
                cmds.connectAttr(f'{loc}.worldMatrix[0]',f'{choicA}.input[{i}]')
                cmds.connectAttr(f'{loc}.worldMatrix[0]',f'{choicB}.input[{i}]')
                #create blend matrix node
                blend=cmds.createNode('blendMatrix',name=f'space_{ctrl}_blendMatrix_0001')
                #connect choice node to blend matrix
                cmds.connectAttr(f'{choicA}.output',f'{blend}.inputMatrix')
                cmds.connectAttr(f'{choicB}.output',f'{blend}.target[0].targetMatrix')
                cmds.connectAttr(f'{ctrl}.spaceBlend',f'{blend}.target[0].weight')
                cmds.connectAttr(f'{ctrl}.spaceBlendT',f'{blend}.target[0].translateWeight')
                cmds.connectAttr(f'{ctrl}.spaceBlendR',f'{blend}.target[0].rotateWeight')
                #connect space_grp to inverse matrix
                cmds.createNode('multMatrix',name=f'space_{ctrl}_multMatrix_0001')
                cmds.connectAttr(f'{blend}.outputMatrix',f'space_{ctrl}_multMatrix_0001.matrixIn[0]')
                cmds.connectAttr(f'space_{ctrl}.parentInverseMatrix[0]',f'space_{ctrl}_multMatrix_0001.matrixIn[1]')
                #create decompose matrix
                cmds.createNode('decomposeMatrix',name=f'space_{ctrl}_decomposeMatrix_0001')
                cmds.connectAttr(f'space_{ctrl}_multMatrix_0001.matrixSum',f'space_{ctrl}_decomposeMatrix_0001.inputMatrix')
                #connect translate and rotate
                cmds.connectAttr(f'space_{ctrl}_decomposeMatrix_0001.outputTranslate',f'space_{ctrl}.translate')
                cmds.connectAttr(f'space_{ctrl}_decomposeMatrix_0001.outputRotate',f'space_{ctrl}.rotate')


import maya.cmds as cmds


def connect_ctrl_to_joint(parent=None):

    ctrls = cmds.ls(selection=True)

    for ctrl in ctrls:

        joint = ctrl.replace("ctrl", "joint")
        output = f"output_{ctrl}"

        if not cmds.objExists(joint):
            cmds.warning(f"{joint} not found")
            continue

        if not cmds.objExists(output):
            cmds.warning(f"{output} not found")
            continue


        # -----------------------------
        # bake current transform
        # -----------------------------

        matrix = cmds.xform(joint, q=True, ws=True, m=True)

        cmds.setAttr(
            f"{joint}.offsetParentMatrix",
            matrix,
            type="matrix"
        )

        # zero transforms
        cmds.setAttr(f"{joint}.translate",0,0,0)
        cmds.setAttr(f"{joint}.rotate",0,0,0)
        cmds.setAttr(f"{joint}.scale",1,1,1)

        # zero joint orient
        cmds.setAttr(f"{joint}.jointOrientX",0)
        cmds.setAttr(f"{joint}.jointOrientY",0)
        cmds.setAttr(f"{joint}.jointOrientZ",0)

        # -----------------------------
        # matrix connection
        # -----------------------------

        mult = cmds.createNode(
            "multMatrix",
            name=ctrl.replace("ctrl","mtx")
        )

        cmds.connectAttr(
            f"{output}.worldMatrix[0]",
            f"{mult}.matrixIn[0]",
            force=True
        )

        cmds.connectAttr(
            f"{parent}.worldInverseMatrix[0]",
            f"{mult}.matrixIn[1]",
            force=True
        )

        cmds.connectAttr(
            f"{mult}.matrixSum",
            f"{joint}.offsetParentMatrix",
            force=True
        )

        print(f"{ctrl} → {joint} connected")

def matrix_constraint_to_joint():
    ctrls = cmds.ls(selection=True)
    for ctrl in ctrls:
        output= f'output_{ctrl}'
        joint=ctrl.replace('ctrl','joint')
        #let's deal with translate first
        #create multmatrix and decompose matrix
        multT = cmds.createNode('multMatrix',name=ctrl.replace('ctrl','multTrans'))
        decompT = cmds.createNode('decomposeMatrix',name=ctrl.replace('ctrl','decompTrans'))
        #multiply the output with the parent inverse of the joint
        cmds.connectAttr(f'{output}.worldMatrix[0]', f'{multT}.matrixIn[0]')
        cmds.connectAttr(f'{joint}.parentInverseMatrix[0]', f'{multT}.matrixIn[1]')
        #connect the output of the multMatrix to the input of the decomposeMatrix
        cmds.connectAttr(f'{multT}.matrixSum', f'{decompT}.inputMatrix')
        #connect it back to the joint
        cmds.connectAttr(f'{decompT}.outputTranslate', f'{joint}.translate')
        #let's deal with rotation now
        #compose inverse scale and divide by the inverse scale
        compIS = cmds.createNode('composeMatrix',name=ctrl.replace('ctrl','composeInvScale'))
        divIS = cmds.createNode('multiplyDivide',name=ctrl.replace('ctrl','divInvScale'))
        cmds.setAttr(f'{divIS}.operation', 2)  # Set operation to 'divide'
        cmds.setAttr(f'{divIS}.input1X', 1)
        cmds.setAttr(f'{divIS}.input1Y', 1)
        cmds.setAttr(f'{divIS}.input1Z', 1)
        cmds.connectAttr(f'{joint}.inverseScale',f'{divIS}.input2' )
        cmds.connectAttr(f'{divIS}.output',f'{compIS}.inputScale' )
        #compose joint orientation
        compJO = cmds.createNode('composeMatrix',name=ctrl.replace('ctrl','composeJO'))
        cmds.connectAttr(f'{joint}.jointOrient', f'{compJO}.inputRotate')
        #mult the compJO with compIS
        multJOIS = cmds.createNode('multMatrix',name=ctrl.replace('ctrl','multJOIS'))
        cmds.connectAttr(f'{compJO}.outputMatrix', f'{multJOIS}.matrixIn[0]')
        cmds.connectAttr(f'{compIS}.outputMatrix', f'{multJOIS}.matrixIn[1]')
        #inverse the matrix
        invJOIS = cmds.createNode('inverseMatrix',name=ctrl.replace('ctrl','inverseJOIS'))
        cmds.connectAttr(f'{multJOIS}.matrixSum', f'{invJOIS}.inputMatrix')
        #mult translate and inverse JOIS
        multFinal = cmds.createNode('multMatrix',name=ctrl.replace('ctrl','multFinal'))
        cmds.connectAttr(f'{multT}.matrixSum', f'{multFinal}.matrixIn[0]')
        cmds.connectAttr(f'{invJOIS}.outputMatrix', f'{multFinal}.matrixIn[1]')
        #decompose result and connect to joint
        decompFinal = cmds.createNode('decomposeMatrix',name=ctrl.replace('ctrl','decompFinal'))
        cmds.connectAttr(f'{multFinal}.matrixSum', f'{decompFinal}.inputMatrix')
        cmds.connectAttr(f'{decompFinal}.outputRotate', f'{joint}.rotate')
        #absolute the scale 
        asX = cmds.createNode('absolute', name=ctrl.replace('ctrl', 'absScaleX'))
        asY = cmds.createNode('absolute', name=ctrl.replace('ctrl', 'absScaleY'))
        asZ = cmds.createNode('absolute', name=ctrl.replace('ctrl', 'absScaleZ'))
        cmds.connectAttr(f'{decompFinal}.outputScaleX', f'{asX}.input')
        cmds.connectAttr(f'{decompFinal}.outputScaleY', f'{asY}.input')
        cmds.connectAttr(f'{decompFinal}.outputScaleZ', f'{asZ}.input')
        cmds.connectAttr(f'{asX}.output', f'{joint}.scaleX')
        cmds.connectAttr(f'{asY}.output', f'{joint}.scaleY')
        cmds.connectAttr(f'{asZ}.output', f'{joint}.scaleZ')


def space_switch_match(space_index = 0):

    ctrl = cmds.ls(selection=True)[0]
    space_grp = f'space_{ctrl}'

    if 'upperarmFK' in ctrl:
        clavicle_ctrl = ctrl.replace('upperarmFK', 'clavicle')
        scapula_ctrl = ctrl.replace('upperarmFK', 'scapula')

        rot_clavicle = cmds.xform(clavicle_ctrl, q=True, ws=True, ro=True)
        rot_scapula = cmds.xform(scapula_ctrl, q=True, ws=True, ro=True)
    else:
        clavicle_ctrl = None
        scapula_ctrl = None
        rot_clavicle = None
        rot_scapula = None

    #extra correction for the clavicle and scapula due to the pose reader correction
    if 'upperarmFK' in ctrl:

        cmds.xform(clavicle_ctrl, rotation=rot_clavicle, worldSpace=True)
        cmds.xform(scapula_ctrl, rotation=rot_scapula, worldSpace=True)
        #if the space is clavicle we need to match multiple times to make it correct 
        if space_index == 1:
            for  i in range(10):
                cmds.xform(ctrl, rotation=rot, worldSpace=True)
                cmds.xform(clavicle_ctrl, rotation=rot_clavicle, worldSpace=True)
                cmds.xform(scapula_ctrl, rotation=rot_scapula, worldSpace=True)
    #collect the attr for the ctrl
    pos = cmds.xform(ctrl, q=True, ws=True, t=True)
    rot = cmds.xform(ctrl, q=True, ws=True, ro=True)
    #set the space attribute to the new space attr 
    cmds.setAttr(f'{ctrl}.space',space_index)
    #check if there are any constraint to the translate attribute
    #match the translate
    if cmds.listConnections(f'{ctrl}.translateX', source=True, destination = False):
        cmds.xform(ctrl,translation = pos,worldSpace = True)
    #do it to the rotation also 
    if cmds.listConnections(f'{ctrl}.rotateX', source=True, destination = False):
        cmds.xform(ctrl, rotation=rot, worldSpace=True)






def add_sdk_grp():
    '''select offset grp to add sdk grp'''
    top_grps = cmds.ls(selection=True)
    for top in top_grps:
        prefix = top.split('_')[0]
        side = top.split('_')[1]
        part = top.split('_')[2]
        typ = top.split('_')[3]
        string = top.split('_')[-1]
        sdk_grp = cmds.createNode('transform', name=f'sdk_{side}_{part}_{typ}_{string}')
        connect_grp = sdk_grp.replace('sdk','connect')
        driven_grp = sdk_grp.replace('sdk','driven')
        cmds.matchTransform(sdk_grp, connect_grp)
        cmds.parent(connect_grp, sdk_grp)
        cmds.parent(sdk_grp, driven_grp)



def sdk_on_keyframe(start_frame=1,end_frame=40,driver=None,driver_attr=None,driver_value=10,
                    driven_ctrl_list=None,driven_grp='sdk',mirror=True):
    '''
    start_frame(int):the start frame you want to bake
    end_frame(int) : the end frame for baking
    driver(str) : obj as driver
    driver_attr(str) : the attr you want to set as driver
    driven_ctrl_list(list) : item list you want do be driven,
                        the keyed attr will be detected automatically 
    driven_grp(str): grp you want to set driven key on 

    '''
    if not (driver and driver_attr and driven_ctrl_list):
        print('please enter driver,driver_attr and driven_list')
        return
    if not cmds.attributeQuery(f'{driver_attr}',node = driver,exists = True):
        print("plz check the driver's attr exist")



    side = driver.split('_')[0]
    

    if side.startswith('L') and mirror == True :
        R_driver = driver.replace('L','R')
    

    for driven_ctrl in driven_ctrl_list : 
        L_driven_grp = f'{driven_grp}_{driven_ctrl}'
        R_driven_grp = L_driven_grp.replace('L','R')
        #translate first remember they are opposite
        for attr in ['translateX','translateY','translateZ']:
            
            origin_val = cmds.getAttr(f'{driven_ctrl}.{attr}',time = start_frame)
            val = cmds.getAttr(f'{driven_ctrl}.{attr}',time = end_frame)
            if val!= origin_val:
                #sdk for L side 
                cmds.setDrivenKeyframe(f'{L_driven_grp}.{attr}',cd = f'{driver}.{driver_attr}',dv=0,v=origin_val)
                cmds.setDrivenKeyframe(f'{L_driven_grp}.{attr}',cd = f'{driver}.{driver_attr}',dv=driver_value,v=val)
                if side.startswith('L') and mirror == True :
                    #sdk for R side
                    cmds.setDrivenKeyframe(f'{R_driven_grp}.{attr}',cd = f'{R_driver}.{driver_attr}',dv=0,v=-origin_val)
                    cmds.setDrivenKeyframe(f'{R_driven_grp}.{attr}',cd = f'{R_driver}.{driver_attr}',dv=driver_value,v=-val)

        for attr in ['rotateX','rotateY','rotateZ']:
            origin_val = cmds.getAttr(f'{driven_ctrl}.{attr}',time = start_frame)
            val = cmds.getAttr(f'{driven_ctrl}.{attr}',time = end_frame)
            if val!= origin_val:
                #sdk for L side 
                cmds.setDrivenKeyframe(f'{L_driven_grp}.{attr}',cd = f'{driver}.{driver_attr}',dv=0,v=origin_val)
                cmds.setDrivenKeyframe(f'{L_driven_grp}.{attr}',cd = f'{driver}.{driver_attr}',dv=driver_value,v=val)
                if side.startswith('L') and mirror == True :
                    #sdk for  R side
                    cmds.setDrivenKeyframe(f'{R_driven_grp}.{attr}',cd = f'{R_driver}.{driver_attr}',dv=0,v=origin_val)
                    cmds.setDrivenKeyframe(f'{R_driven_grp}.{attr}',cd = f'{R_driver}.{driver_attr}',dv=driver_value,v=val)


        for attr in ['scaleX','scaleY','scaleZ']:
            origin_val = cmds.getAttr(f'{driven_ctrl}.{attr}',time = start_frame)
            val = cmds.getAttr(f'{driven_ctrl}.{attr}',time = end_frame)
            if val!= origin_val:
                #sdk for L side 
                cmds.setDrivenKeyframe(f'{L_driven_grp}.{attr}',cd = f'{driver}.{driver_attr}',dv=0,v=origin_val)
                cmds.setDrivenKeyframe(f'{L_driven_grp}.{attr}',cd = f'{driver}.{driver_attr}',dv=driver_value,v=val)
                if side.startswith('L') and mirror == True :
                    #sdk for  R side
                    cmds.setDrivenKeyframe(f'{R_driven_grp}.{attr}',cd = f'{R_driver}.{driver_attr}',dv=0,v=origin_val)
                    cmds.setDrivenKeyframe(f'{R_driven_grp}.{attr}',cd = f'{R_driver}.{driver_attr}',dv=driver_value,v=val)

        #clear the keyframes
        cmds.cutKey(driven_ctrl,time = (end_frame,end_frame),clear=True)
        cmds.cutKey(driven_ctrl,time = (start_frame,start_frame),clear=True)


            


import maya.cmds as cmds

def create_joint_at_center_loop():
    #get edges
    sel_edges = cmds.ls(sl=True, flatten=True)
    
    if not sel_edges or not cmds.filterExpand(sel_edges, selectionMask=32):
        #32 means edge

        cmds.warning("plz select at least one edge")
        return


    verts = cmds.polyListComponentConversion(sel_edges, toVertex=True)

    verts_expanded = cmds.filterExpand(verts, selectionMask=31)
    #31 means vertices
    
    if not verts_expanded:
        return

    # get all the points 
    count = len(verts_expanded)
    sum_x, sum_y, sum_z = 0.0, 0.0, 0.0

    for v in verts_expanded:
        #get every v world pos
        pos = cmds.pointPosition(v, world=True)
        sum_x += pos[0]
        sum_y += pos[1]
        sum_z += pos[2]

    #get the center
    center_point = (sum_x / count, sum_y / count, sum_z / count)

    # build joint
    cmds.select(clear=True) 
    jnt = cmds.joint(p=center_point, name='joint')
    
    return jnt


def create_joint_on_selected_vertices(name=None):
    sel_verts = cmds.ls(sl=True, flatten=True)
    
    if not sel_verts or not cmds.filterExpand(sel_verts, selectionMask=31):
        #31 means vertex
        cmds.warning("plz select at least one vertex")
        return

    joints = []
    for i, v in enumerate(sel_verts):
        pos = cmds.pointPosition(v, world=True)
        jnt = cmds.joint(p=pos, name=f'{name}_joint_{i:04d}' if name else 'joint')
        joints.append(jnt)

    return joints
        

import maya.cmds as cmds


def get_driven_data(node):
    sdk_data = {}
    attrs = cmds.listAttr(node, keyable=True)or[]
    for attr in attrs:
        node_plug = f'{node}.{attr}'

        #find sdk curve
        input_plugs = cmds.listConnections(
            node_plug, source=True, destination=False, 
            skipConversionNodes=True, plugs=False) or []
        
        if input_plugs:
            if cmds.nodeType(input_plugs[0]) == 'animCurve':
                driver, data = _get_anim_curve_data(input_plugs[0])
                sdk_data[attr] = {
                    'driver': driver,
                    'data': data}
            else:
                # multi set driven key curves
                curves = cmds.listConnections(
                    f'{input_plugs[0]}.input', type='animCurve', source=True, 
                    destination=False, skipConversionNodes=True, plugs=False) or []

                # also get used indices
                indices = cmds.getAttr(f'{input_plugs[0]}.input', multiIndices=True)

                data = []
                # loop into each curve and get curve data

                for crv, idx in zip(curves, indices):
                    driver, d = _get_anim_curve_data(crv)
                    if data:
                        # normal sdk curve
                        data.append(
                            {
                                'driver': driver,
                                'data': d})
                    else:
                        # maya has a bug, if only one keyframe on sdk, 
                        # seems won't return anything, 
                        # get input value instead, and set the value later
                        value = cmds.getAttr(f'{input_plugs[0]}.input[{idx}]')
                        data.append(value)

                sdk_data[attr] = data

    return sdk_data


def _get_anim_curve_data(curve):
    driver = cmds.listConnections(
        f'{curve}.input', source=True, destination=False, plugs=True)
    if driver:
        driver = driver[0]

    data = []
    keys = cmds.keyframe(curve, query=True, indexValue=True) or []
    for k in keys:
        dv = cmds.keyframe(curve, index=(k, k), query=True, floatChange=True)[0]
        v = cmds.keyframe(curve, index=(k, k), query=True, valueChange=True)[0]
        data.append([dv, v])

    return driver, data


def copy_sdk_data(node, sdk_data,source='F',replace='B'):
    # get mirror node
    node_mirror = node.replace(source, replace)

    for attr, data in sdk_data.items():
        offset = 1 
        plug = f'{node_mirror}.{attr}'
        if isinstance(data, dict):
            # simple sdk
            driver = data['driver'].replace(source, replace)
            for values in data['data']:
                cmds.setDrivenKeyframe(
                    plug, currentDriver=driver, 
                    driverValue=values[0], value=values[1] * offset)
        else:
            # weight blended node
            weight_blend = cmds.createNode('blendWeighted')
            cmds.connectAttr(f'{weight_blend}.output', plug)
            cmds.setAttr(f'{weight_blend}.current', -1)
            for i, d in enumerate(data):
                if isinstance(d, dict):
                    # simply sdk
                    driver = d['driver'].replace(source, replace)
                    for values in d['data']:
                        cmds.setDrivenKeyframe(
                            f'{weight_blend}.input[{i}]', 
                            currentDriver=driver, 
                            driverValue=values[0], value=values[1] * offset)
                else:
                    # direct set value
                    cmds.setAttr(f'{weight_blend}.input[{i}]', d)


def connect_ctrl_to_loc(source,target):
    sels = cmds.ls(selection=True)
    for sel in sels:
        axis=['X','Y','Z']
        for a in axis:
            loc = sel.replace(source,target)
            cmds.connectAttr(f'{sel}.translate{a}',f'{loc}.translate{a}')
            cmds.connectAttr(f'{sel}.rotate{a}',f'{loc}.rotate{a}')
            cmds.connectAttr(f'{sel}.scale{a}',f'{loc}.scale{a}')





def get_skin_joints(mesh):

    skin = cmds.ls(cmds.listHistory(mesh), type="skinCluster")
    
    if not skin:
        cmds.warning(f"No skinCluster found on {mesh}")
        return []
    
    skin = skin[0]

    joints = cmds.skinCluster(skin, q=True, influence=True)
    cmds.select(joints)

    return joints





