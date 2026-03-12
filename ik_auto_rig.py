import maya.cmds as cmds
import rig_modules.controller_shape as cs
import rig_modules.mirror_tools as mr
import maya.OpenMaya as om
import maya.mel as mel
def build_ik_arm(poleDistance=1,ctrl_size=1):
    '''select wrist joint and upperarm joint to build ik arm rig'''
    #list the joints
    wrist_joint=cmds.ls(sl=True,type='joint')[0]
    upperarm_joint = cmds.ls(sl=True, type="joint")[1]
    elbow_joint=cmds.listRelatives(upperarm_joint, children=True, type="joint")[0]
    #define side
    side=wrist_joint.split("_")[0]
    #create ikHandle
    ik_handle = cmds.ikHandle(sj=upperarm_joint,ee=wrist_joint,sol='ikRPsolver',name=f'{side}_armIK_ikHandle')[0]
    #create wrist IK control
    wristIK_ctrl=cmds.createNode('joint',name=f'{side}_wristIK_ctrl_0001')
    cmds.setAttr(f'{wristIK_ctrl}.drawStyle', 2)
    #create ctrl shape
    ctrl=cs.create_cube_ctrl(name=f'{side}_wristIK_tmp',size=ctrl_size)
    ctrl_shape=cmds.listRelatives(ctrl,shapes=True,fullPath=True)[0]
    shape_name = cmds.rename(ctrl_shape, f'{side}_wristIK_ctrlShape')
    cmds.parent(shape_name, wristIK_ctrl,add=True,shape=True)
    cmds.matchTransform(wristIK_ctrl, wrist_joint)
     #create zero grp
    parent=None
    top_node=None
    for prefix in['zero','driven','connect']:
       new_name=f'{prefix}_{side}_wristIK_ctrl_0001'
       node=cmds.createNode('transform',name=new_name)

       cmds.matchTransform(node, wristIK_ctrl,pos=True,rot=False,scl=False)

       if parent:
           cmds.parent(node, parent)
       parent=node
       if not top_node:
           top_node=node

    #parent the wristIK_ctrl to ctrl grp
    cmds.parent(wristIK_ctrl, parent)

    #freeze the rotation on the ctrl
    cmds.delete(f'{side}_wristIK_tmp')
    cmds.makeIdentity(wristIK_ctrl, apply=True, translate=1, rotate=1, scale=1)
    cmds.delete(wristIK_ctrl, constructionHistory=True)

    wristIK_ctrl_shape = cmds.listRelatives(wristIK_ctrl,shapes=True)[0]

    #create sub controller
    sub=cmds.duplicate(wristIK_ctrl,name=wristIK_ctrl.replace('ctrl','subctrl'))[0]
    cmds.parent(sub,wristIK_ctrl)
    cmds.setAttr(f'{sub}.scale',0.85,0.85,0.85)
    cmds.setAttr(f'{sub}.overrideEnabled',1) 
    cmds.makeIdentity (sub,apply=True,t=1,r=1,s=1,n=0)
    sub_shape=cmds.listRelatives(sub,shapes=True,fullPath=True)[0]
    sub_shape_name = sub_shape.split('|')[-1].replace('ctrl','subctrl')
    sub_shape = cmds.rename(sub_shape,sub_shape_name)
    cmds.setAttr(f'{sub_shape}.lineWidth',1)
    cmds.setAttr(f'{wristIK_ctrl_shape}.lineWidth',2)
    print(wristIK_ctrl_shape)

    #set sub ctrl shape
    cmds.createNode('transform',name=f'output_{wristIK_ctrl}',parent=sub)
    cmds.setAttr(f'{wristIK_ctrl}.visibility',keyable=False,lock=True,channelBox=False)
    cmds.setAttr(f'{sub}.visibility',keyable=False,lock=True,channelBox=False)
    cmds.setAttr(f'{wristIK_ctrl}.rotateOrder',keyable=True)
    cmds.setAttr(f'{sub}.rotateOrder',keyable=True)

    #add attribute for the main controller
    cmds.addAttr(wristIK_ctrl,longName='subCtrlVis',attributeType='bool',keyable=False)
    cmds.setAttr(f'{wristIK_ctrl}.subCtrlVis',channelBox=True)
    cmds.connectAttr(f'{wristIK_ctrl}.subCtrlVis',f'{sub_shape}.visibility')
   
    
    #make wristIK_ctrl functional :)
    cmds.orientConstraint(f'output_{wristIK_ctrl}', wrist_joint,mo=True)
    cmds.parent(ik_handle, wristIK_ctrl)

    #hide and lock ikhandle
    cmds.setAttr(f'{ik_handle}.visibility', 0)
    cmds.setAttr(f'{ik_handle}.visibility', keyable=False, lock=True, channelBox=False)
    #color the control
    cmds.setAttr(f'{wristIK_ctrl}.overrideEnabled', 1)
    cmds.setAttr(f'{sub_shape}.overrideEnabled', 1)
    if side == "L":
        cmds.setAttr(f'{wristIK_ctrl}.overrideColor', 6)
        cmds.setAttr(f'{sub_shape}.overrideColor', 6)
    elif side == "C":
        cmds.setAttr(f'{wristIK_ctrl}.overrideColor', 17)
        cmds.setAttr(f'{sub_shape}.overrideColor', 17)
    elif side == "R":
        cmds.setAttr(f'{wristIK_ctrl}.overrideColor', 13)
        cmds.setAttr(f'{sub_shape}.overrideColor', 13)

    #create pole vector
    pole_vector = cs.create_cube_ctrl(name=f'{side}_armIKPV_ctrl_0001')
    cmds.matchTransform(pole_vector, elbow_joint)
    cmds.createNode('transform', name=f'zero_{side}_armIKPV_ctrl_0001')


    #place the pole vector control
    #p short for position 
    up=om.MVector(*cmds.xform(upperarm_joint,q=1,ws=1,t=1))
    ep=om.MVector(*cmds.xform(elbow_joint,q=1,ws=1,t=1))
    wp=om.MVector(*cmds.xform(wrist_joint,q=1,ws=1,t=1))

    #get the vectors
    ue_vector=ep-up
    uw_vector=wp-up

    #caculate projection point and projection length
    dotP=ue_vector * uw_vector
    proj_length=float(dotP)/float(uw_vector.length())

    uw_normalized=uw_vector.normal()
    proj_vector=uw_normalized*proj_length
    arrow_vector=ue_vector-proj_vector
    arrow_vector*= (poleDistance*uw_vector.length())
    final_vector=arrow_vector+up
    cmds.xform(pole_vector,ws=True,t=[final_vector.x, final_vector.y, final_vector.z] )

    #zero out pole vector
    cmds.matchTransform(f'zero_{side}_armIKPV_ctrl_0001', pole_vector)
    cmds.parent(pole_vector, f'zero_{side}_armIKPV_ctrl_0001')
    #fix rotation on PV ctrl
    cmds.setAttr(f'zero_{side}_armIKPV_ctrl_0001.rotateX', 0)
    cmds.setAttr(f'zero_{side}_armIKPV_ctrl_0001.rotateY', 0)
    cmds.setAttr(f'zero_{side}_armIKPV_ctrl_0001.rotateZ', 0)
    #pole vector constraint
    cmds.poleVectorConstraint(pole_vector, ik_handle)
    #create annotation 
    ann_shape=cmds.annotate(pole_vector,tx='') #this is shape node
    cmds.setAttr(f'{ann_shape}.overrideEnabled',1)
    cmds.setAttr(f'{ann_shape}.overrideDisplayType',2)
    #point constraint to the elbow joint
    ann=cmds.listRelatives(ann_shape,p=True)
    cmds.parent(ann,pole_vector)
    cmds.pointConstraint(elbow_joint,ann, mo=False)
    #set up color for the PV
    
    PV_shape=cmds.listRelatives(pole_vector,shapes=True)[0]
    cmds.setAttr(f'{PV_shape}.overrideEnabled', 1)
    if side == "L":
        cmds.setAttr(f'{PV_shape}.overrideColor', 6)
    elif side == "C":
        cmds.setAttr(f'{PV_shape}.overrideColor', 17)
    elif side == "R":
        cmds.setAttr(f'{PV_shape}.overrideColor', 13)
    cmds.setAttr(f'{PV_shape}.lineWidth', 2)

def match_fkik_ts():
    sel = cmds.ls(selection=True)[0]
    side = 'L' if sel.startswith('L') else "R"
    S = side

    ctrlFK_list = [f'{S}_upperarmFK_ctrl_0001',
                   f'{S}_elbowFK_ctrl_0001',
                   f'{S}_wristFK_ctrl_0001']
    ctrlIK_list = [f'{S}_wristIK_ctrl_0001']

    if sel in ctrlFK_list:
        rot_upperarm = cmds.xform(f'{S}_upperarmFK_match_0001', q=True, rotation=True, worldSpace=True)
        rot_elbow    = cmds.xform(f'{S}_elbowFK_match_0001',    q=True, rotation=True, worldSpace=True)
        rot_wrist    = cmds.xform(f'{S}_wristFK_match_0001',    q=True, rotation=True, worldSpace=True)

        cmds.xform(f'{S}_upperarmFK_ctrl_0001', rotation=rot_upperarm, worldSpace=True)
        cmds.xform(f'{S}_elbowFK_ctrl_0001',    rotation=rot_elbow,    worldSpace=True)
        cmds.xform(f'{S}_wristFK_ctrl_0001',    rotation=rot_wrist,    worldSpace=True)

        cmds.setAttr(f'{S}_armIKBlend_ctrl_0001.ikFkBlend', 1)

    elif sel in ctrlIK_list:
        pos_ik = cmds.xform(f'{S}_wristIK_match_0001', q=True, t=True, worldSpace=True)
        rot_ik = cmds.xform(f'{S}_wristIK_match_0001', q=True, rotation=True, worldSpace=True)

        pos_pv = cmds.xform(f'{S}_armIKPV_match_0001', q=True, t=True, worldSpace=True)

        cmds.xform(f'{S}_wristIK_ctrl_0001', t=pos_ik, worldSpace=True)
        cmds.xform(f'{S}_wristIK_ctrl_0001', rotation=rot_ik, worldSpace=True)
        cmds.xform(f'{S}_armIKPV_ctrl_0001', t=pos_pv, worldSpace=True)

        cmds.setAttr(f'{S}_armIKBlend_ctrl_0001.ikFkBlend', 0)

    else:
        print('plz select an FK or IK ctrl')


def fkik_blend(con_typ = 'orient', finger_grp = None):
    
    blend_ctrl = cmds.ls(selection=True)[0]
    side = blend_ctrl.split('_')[0]
    part = blend_ctrl.split('_')[1]
    # color the controls
    blend_ctrl_shape=cmds.listRelatives(blend_ctrl, shapes=True)[0]
    cmds.setAttr(f'{blend_ctrl_shape}.overrideEnabled', 1)
    cmds.setAttr(f'{blend_ctrl_shape}.lineWidth', 2)
    if  'L'in side:
        cmds.setAttr(f'{blend_ctrl_shape}.overrideColor', 6)

    elif 'R' in side:
        cmds.setAttr(f'{blend_ctrl_shape}.overrideColor', 13)

    


    if 'arm' not in blend_ctrl and 'leg' not in blend_ctrl:
        print('make sure your naming is right!! must cost you an arm and a leg!')
    #set up blend ctrl attr 
    axis=['X', 'Y', 'Z']
    for ax in axis:
        cmds.setAttr(f'{blend_ctrl}.translate{ax}', keyable=False, lock=True, channelBox=False)
        cmds.setAttr(f'{blend_ctrl}.rotate{ax}', keyable=False, lock=True, channelBox=False)
        cmds.setAttr(f'{blend_ctrl}.scale{ax}', keyable=False, lock=True, channelBox=False)
    cmds.setAttr(f'{blend_ctrl}.visibility', 1,  keyable=False, channelBox=False)
    if not cmds.attributeQuery('ikFkBlend', node=blend_ctrl, exists=True):
        cmds.addAttr(blend_ctrl, longName='ikFkBlend', attributeType='float', min=0, max=1, defaultValue=0, keyable=True)
    if not cmds.attributeQuery('show_both_ctrls', node=blend_ctrl, exists=True):
        cmds.addAttr(blend_ctrl,longName='show_both_ctrls', attributeType='bool', defaultValue=1)
        cmds.setAttr(f'{blend_ctrl}.show_both_ctrls', keyable=False, channelBox=True)
    
    #orient constraint on main joint
    
    if 'arm' in part:
        print(part)
        
        fk_joints = [f'{side}_upperarmFK_joint_0001',f'{side}_elbowFK_joint_0001',f'{side}_wristFK_joint_0001']
        ik_joints = [f'{side}_upperarmIK_joint_0001',f'{side}_elbowIK_joint_0001',f'{side}_wristIK_joint_0001']
        main_joints = [f'{side}_upperarm_joint_0001',f'{side}_elbow_joint_0001', f'{side}_wrist_joint_0001']

        for i in range(3):
            #constraint the three joints without maintain offset 
            if con_typ == 'orient':
                cmds.orientConstraint(fk_joints[i], ik_joints[i], main_joints[i], mo=False, weight=1)
            if con_typ == 'parent':
                cmds.parentConstraint(fk_joints[i], ik_joints[i], main_joints[i], mo=False, weight=1)

        #create reverse node for blending
        reverse_node = cmds.createNode('reverse', name=f'{side}_{part}_ikFkBlend_reverse')
        cmds.connectAttr(f'{blend_ctrl}.ikFkBlend', f'{reverse_node}.inputX')
        # orient constraint
        for i in range(3):
            constraint_node=f'{main_joints[i]}_{con_typ}Constraint1'
            fk_target_attr=f'{constraint_node}.{fk_joints[i]}W0'
            ik_target_attr=f'{constraint_node}.{ik_joints[i]}W1'

            #connect orientConstraint
            
            cmds.connectAttr(f'{reverse_node}.outputX', fk_target_attr)
            cmds.connectAttr(f'{blend_ctrl}.ikFkBlend', ik_target_attr)

        # define the ctrl
        fk_top = f'zero_{fk_joints[0]}'.replace('joint', 'ctrl')
        ik_top = f'zero_{ik_joints[2]}'.replace('joint', 'ctrl')
        ik_pv = f'zero_{side}_armIKPV_ctrl_0001'

        #connect FK control visibility
        fk_add_node=cmds.createNode('plusMinusAverage',name=f'{side}_{part}_fkBlend_add')
        cmds.setAttr(f'{fk_add_node}.operation',1)
        cmds.connectAttr(f'{reverse_node}.outputX', f'{fk_add_node}.input1D[0]')
        cmds.connectAttr(f'{blend_ctrl}.show_both_ctrls', f'{fk_add_node}.input1D[1]')
        cmds.connectAttr(f'{fk_add_node}.output1D',f'{fk_top}.visibility')

        #connect IK controls visibility
        ik_add_node=cmds.createNode('plusMinusAverage',name=f'{side}_{part}_ikBlend_add')
        cmds.setAttr(f'{ik_add_node}.operation',1)
        cmds.connectAttr(f'{blend_ctrl}.ikFkBlend', f'{ik_add_node}.input1D[0]')
        cmds.connectAttr(f'{blend_ctrl}.show_both_ctrls', f'{ik_add_node}.input1D[1]')
        cmds.connectAttr(f'{ik_add_node}.output1D',f'{ik_top}.visibility')
        cmds.connectAttr(f'{ik_add_node}.output1D',f'{ik_pv}.visibility')

        #constraint the fingers
        cmds.parentConstraint(main_joints[2],finger_grp, mo=True)

    elif 'leg' in part:
        
        fk_joints = [f'{side}_thighFK_joint_0001', f'{side}_kneeFK_joint_0001', 
                     f'{side}_ankleFK_joint_0001',f'{side}_ballFK_joint_0001']
        ik_joints = [f'{side}_thighIK_joint_0001', f'{side}_kneeIK_joint_0001', 
                     f'{side}_ankleIK_joint_0001', f'{side}_ballIK_joint_0001']
        main_joints = [f'{side}_thigh_joint_0001', f'{side}_knee_joint_0001',
                       f'{side}_ankle_joint_0001', f'{side}_ball_joint_0001']

        for i in range(4):
            #constraint the three joints without maintain offset 
            if con_typ == 'orient':
                ocon = cmds.orientConstraint(fk_joints[i], ik_joints[i], main_joints[i], mo=False, weight=1)[0]
                cmds.setAttr(f'{ocon}.interpType', 2) #set to shortest
            if con_typ == 'parent':
                pcon = cmds.parentConstraint(fk_joints[i], ik_joints[i], main_joints[i], mo=False, weight=1)[0]

        #create reverse node for blending
        reverse_node = cmds.createNode('reverse', name=f'{side}_{part}_ikFkBlend_reverse')
        cmds.connectAttr(f'{blend_ctrl}.ikFkBlend', f'{reverse_node}.inputX')
        # orient constraint
        for i in range(4):
            constraint_node=f'{main_joints[i]}_{con_typ}Constraint1'
            fk_target_attr=f'{constraint_node}.{fk_joints[i]}W0'
            ik_target_attr=f'{constraint_node}.{ik_joints[i]}W1'

            #connect orientConstraint
            
            cmds.connectAttr(f'{reverse_node}.outputX', fk_target_attr)
            cmds.connectAttr(f'{blend_ctrl}.ikFkBlend', ik_target_attr)

        # define the ctrl
        fk_top = f'zero_{fk_joints[0]}'.replace('joint', 'ctrl')
        ik_top = f'zero_{ik_joints[2]}'.replace('joint', 'ctrl')
        ik_pv = f'zero_{side}_legIKPV_ctrl_0001'

        #connect FK control visibility
        fk_add_node=cmds.createNode('plusMinusAverage',name=f'{side}_{part}_fkBlend_add')
        cmds.setAttr(f'{fk_add_node}.operation',1)
        cmds.connectAttr(f'{reverse_node}.outputX', f'{fk_add_node}.input1D[0]')
        cmds.connectAttr(f'{blend_ctrl}.show_both_ctrls', f'{fk_add_node}.input1D[1]')
        cmds.connectAttr(f'{fk_add_node}.output1D',f'{fk_top}.visibility')

        #connect IK controls visibility
        ik_add_node=cmds.createNode('plusMinusAverage',name=f'{side}_{part}_ikBlend_add')
        cmds.setAttr(f'{ik_add_node}.operation',1)
        cmds.connectAttr(f'{blend_ctrl}.ikFkBlend', f'{ik_add_node}.input1D[0]')
        cmds.connectAttr(f'{blend_ctrl}.show_both_ctrls', f'{ik_add_node}.input1D[1]')
        cmds.connectAttr(f'{ik_add_node}.output1D',f'{ik_top}.visibility')
        cmds.connectAttr(f'{ik_add_node}.output1D',f'{ik_pv}.visibility')

def build_ik_leg(ankle_ctrl_shape=None,ball_ctrl_shape=None,toe_ctrl_shape=None,pv=None):
    end_jnt = cmds.ls(sl=True)[0]
    start_jnt = cmds.ls(sl=True)[1]
    side = end_jnt.split('_')[0]
    ball_jnt = f'{side}_ballIK_joint_0001'
    # create ik handle
    leg_ik_handle = cmds.ikHandle(sj = start_jnt, ee=end_jnt, sol='ikRPsolver', n=f'{side}_ankleIK_ikHandle_0001')[0]

    #create leg control shape
    if not ankle_ctrl_shape:
        leg_ctrl_tmp = cs.create_cube_ctrl(name = f'{side}_ankleIK_ctrl_tmp')
        leg_ctrl_tmp_shape = cmds.listRelatives(leg_ctrl_tmp, s =True)[0]
        leg_ctrl_tmp_shape = cmds.rename(leg_ctrl_tmp_shape, f'{side}_ankleIK_ctrl_tmpShape')
    else:
        leg_ctrl_tmp = cmds.duplicate(ankle_ctrl_shape, name=f'{side}_ankleIK_ctrl_tmp')[0]
        leg_ctrl_tmp_shape = cmds.listRelatives(leg_ctrl_tmp, s =True)[0]
        leg_ctrl_tmp_shape = cmds.rename(leg_ctrl_tmp_shape, f'{side}_ankleIK_ctrl_tmpShape')


    #create leg contoller (joint)

    leg_ctrl = cmds.createNode('joint', n=f'{side}_ankleIK_ctrl_0001')
    cmds.parent(leg_ctrl_tmp_shape, leg_ctrl, add=True, shape=True)
    #renamethe shape just in case
    leg_ctrl_shape = cmds.listRelatives(leg_ctrl, children=True, fullPath=True)[0]
    leg_ctrl_shape = cmds.rename(leg_ctrl_shape, f'{leg_ctrl}Shape')
    #match transformation for the ankle joint
    cmds.matchTransform(leg_ctrl, end_jnt, pos=True, rot=True)
    cmds.setAttr(f'{leg_ctrl}.drawStyle', 2)
    
    cmds.delete(leg_ctrl_tmp)
    #create loc to orient the leg control
    aim_loc = cmds.spaceLocator(n=f'{side}_leg_aim_loc')[0]
    cmds.matchTransform(aim_loc, end_jnt, pos=True)
    cmds.move(0, 1, 0, aim_loc, r=True, os=True)
    up_loc = cmds.spaceLocator(n=f'{side}_leg_up_loc')[0]
    #get correct pos for the up loc
    #get XY
    toe_pos = cmds.xform(f'{side}_toeIK_joint_0001', q=True, ws=True, t=True)
    X = toe_pos[0]
    Z= toe_pos[2]
    ankle_pos = cmds.xform(f'{side}_ankleIK_joint_0001', q=True, ws=True, t=True)
    Y = ankle_pos[1]
    cmds.move(X, Y, Z, up_loc, r=True, os=True)




    #orient the leg control
    cmds.aimConstraint(aim_loc, leg_ctrl, aimVector=[0, 1, 0], upVector=[1, 0, 0], worldUpType='object', worldUpObject=up_loc)
    cmds.delete(cmds.aimConstraint(aim_loc, leg_ctrl))
    cmds.delete(aim_loc, up_loc)
    cmds.makeIdentity(leg_ctrl,apply=True,r=1)

 
    #create zero group for the leg control
    prefix=['zero','driven','connect']
    top_node=None
    parent=None
    for p in prefix:
        grp = cmds.createNode('transform', n = f'{p}_{leg_ctrl}')
        cmds.matchTransform(grp, leg_ctrl, pos=True)
        if parent:
            cmds.parent(grp, parent)

        parent=grp
        if not top_node:
            top_node=grp

    #create sub ctrl and output for leg_ctrl
    leg_subctrl = cmds.duplicate(leg_ctrl, n=f'{side}_ankleIK_subctrl')[0]
    leg_output = cmds.createNode('transform', n=f'output_{leg_ctrl}')
    cmds.matchTransform(leg_output, leg_ctrl, pos=True, rot=True)

    #sub ctrl attr connection 
    cmds.addAttr(leg_ctrl,longName = 'subCtrlVis',attributeType='bool', keyable=False)
    cmds.setAttr(f'{leg_ctrl}.subCtrlVis', channelBox=True)
    leg_subctrl_shape = cmds.listRelatives(leg_subctrl, children=True, fullPath=True)[0]
    leg_subctrl_shape =cmds.rename(leg_subctrl_shape, f'{leg_subctrl}Shape')
    cmds.connectAttr(leg_ctrl + '.subCtrlVis', leg_subctrl_shape + '.visibility')
    # set color and line width for leg ctrl and sub ctrl
    cmds.setAttr(f'{leg_ctrl_shape}.overrideEnabled', 1)
    cmds.setAttr(f'{leg_subctrl_shape}.overrideEnabled', 1)
    if side.startswith('L'):
        cmds.setAttr(f'{leg_ctrl_shape}.overrideColor', 6)  # Set color to blue
        cmds.setAttr(f'{leg_subctrl_shape}.overrideColor', 6)  # Set color to blue
    elif side.startswith('C'):
        cmds.setAttr(f'{leg_ctrl_shape}.overrideColor', 17)  # Set color to yellow
        cmds.setAttr(f'{leg_subctrl_shape}.overrideColor', 17)  # Set color to yellow
    elif side.startswith('R'):
        cmds.setAttr(f'{leg_ctrl_shape}.overrideColor', 13)  # Set color to red
        cmds.setAttr(f'{leg_subctrl_shape}.overrideColor', 13)  # Set color to red  
    cmds.setAttr(f'{leg_ctrl_shape}.lineWidth', 2)
    cmds.setAttr(f'{leg_subctrl_shape}.lineWidth', 1)

    #parent leg ctrl hierarchy
    cmds.parent(leg_output, leg_subctrl)
    cmds.parent(leg_subctrl, leg_ctrl)
    cmds.parent(leg_ctrl,f'connect_{leg_ctrl}')
    #create ballIK control 
    cmds.select(clear=True)
    ballIK_match = cmds.joint(n=f'{side}_ballIK_match')
    cmds.matchTransform(ballIK_match, ball_jnt, pos=True, rot=True)
    ballIK_match_end = cmds.joint(n=f'{side}_ballIK_match_end')
    cmds.matchTransform(ballIK_match_end, f'{side}_ankleIK_joint_0001', pos=True, rot=True)
    cmds.makeIdentity(ballIK_match, apply=True, t=1, r=1, s=1)
    cmds.joint(ballIK_match, e=True, oj='xyz', sao='yup', aos=True)
    if not ball_ctrl_shape:
        ballIK_ctrl=cs.create_cube_ctrl(name=f'{side}_ballIK_ctrl_0001')
    else:
        ballIK_ctrl = cmds.duplicate(ball_ctrl_shape, name=f'{side}_ballIK_ctrl_0001')[0]
    
    cmds.matchTransform(ballIK_ctrl,ballIK_match, pos=True, rot=True)
    cmds.delete(ballIK_match)
    cmds.select(ballIK_ctrl)
    cs.create_ctrlgrp_on_ctrl()


    #parent ball ikHandle and leg ikHandle to ballIK ctrl
    cmds.parent(leg_ik_handle, f'output_{ballIK_ctrl}')
    ocon_ball = cmds.orientConstraint(f'output_{ballIK_ctrl}', end_jnt, mo=True)
    cmds.setAttr(f'{ocon_ball[0]}.interpType', 2) #set to shortest

    #create toeIK control
    if not toe_ctrl_shape:
        toeIK_ctrl=cs.create_cube_ctrl(name=f'{side}_toeIK_ctrl_0001')
    else:
        toeIK_ctrl = cmds.duplicate(toe_ctrl_shape, name=f'{side}_toeIK_ctrl_0001')[0]
    cmds.matchTransform(toeIK_ctrl,f'{side}_ballIK_joint_0001', pos=True, rot=True)
    cmds.select(toeIK_ctrl)
    cs.create_ctrlgrp_on_ctrl()
    o_con_toe = cmds.orientConstraint(f'output_{toeIK_ctrl}', ball_jnt, mo=True)
    cmds.setAttr(f'{o_con_toe[0]}.interpType', 2) #set to shortest
   

    #hide ik handles
    cmds.setAttr(f'{leg_ik_handle}.visibility', 0)
    #parent stuff 
    cmds.parent(f'zero_{side}_footBack_ctrl_0001', f'output_{side}_ankleIK_ctrl_0001')
    cmds.parent(f'zero_{ballIK_ctrl}',f'output_{side}_footOut_ctrl_0001')
    cmds.parent(f'zero_{toeIK_ctrl}',f'output_{side}_footOut_ctrl_0001')
    #pole vector constraint for the knee
    cmds.poleVectorConstraint(pv, leg_ik_handle)



def add_connect_footctrl(target_ctrl=None):
    if not target_ctrl:
        target_ctrl = cmds.ls(selection=True)[0]

    
    side = target_ctrl.split('_')[0]
    #add vis attr to target ctrl 
    cmds.addAttr(target_ctrl, longName='footRollCtrlVis', attributeType='bool', defaultValue=0)
    cmds.setAttr(f'{target_ctrl}.footRollCtrlVis', channelBox=True, keyable=False)
    #connect foot roll Vis to target ctrl 
    foot_pos = ['Back','Front','In','Out']
    for pos in foot_pos:
        foot_ctrl_shape = cmds.listRelatives(f'{side}_foot{pos}_ctrl_0001', shapes=True)[0]
        cmds.connectAttr(f'{target_ctrl}.footRollCtrlVis', f'{foot_ctrl_shape}.visibility')
    
    #add attr for foot roll
    cmds.addAttr(target_ctrl, longName='footCtrl', attributeType='enum',enumName='---------------:')
    cmds.setAttr(f'{target_ctrl}.footCtrl', keyable=False, channelBox=True)
    footRoll_attr=['toeTap','ballRoll','footBank','toeRoll','heelRoll']
    for attr in footRoll_attr:
        cmds.addAttr(target_ctrl, longName=attr, attributeType='float', defaultValue=0, keyable=True)
    #connect evrything except foot bank
    cmds.connectAttr(f'{target_ctrl}.toeTap', f'driven_{side}_toeIK_ctrl_0001.rotateZ')
    cmds.connectAttr(f'{target_ctrl}.ballRoll', f'driven_{side}_ballIK_ctrl_0001.rotateZ')
    cmds.connectAttr(f'{target_ctrl}.heelRoll', f'driven_{side}_footBack_ctrl_0001.rotateZ')
    cmds.connectAttr(f'{target_ctrl}.toeRoll', f'driven_{side}_footFront_ctrl_0001.rotateZ')
    #connect_foot_bank is a bit tricky since it involves both footIn and footOut ctrl
    #we will use a condition node to drive the footIn and footOut ctrl based on the value of footBank attr
    condition_node = cmds.createNode('condition', name=f'{side}_footBank_condition_0001')
    cmds.connectAttr(f'{target_ctrl}.footBank', f'{condition_node}.firstTerm')
    cmds.setAttr(f'{condition_node}.secondTerm', 0)
    cmds.setAttr(f'{condition_node}.operation', 2) #greater than
    cmds.setAttr(f'{condition_node}.colorIfTrueR', 1)
    cmds.setAttr(f'{condition_node}.colorIfFalseR', 0)
    cmds.setAttr(f'{condition_node}.colorIfTrueG', 0)
    cmds.setAttr(f'{condition_node}.colorIfFalseG', -1)
    #connect condition node to footIn and footOut ctrl with multiply node
    md_node = cmds.createNode('multiplyDivide', name=f'{side}_footBank_md_0001')
    cmds.setAttr(f'{md_node}.operation', 1) #multiply
    
    cmds.connectAttr(f'{condition_node}.outColorR', f'{md_node}.input1X')
    cmds.connectAttr(f'{condition_node}.outColorG', f'{md_node}.input1Y')
    cmds.connectAttr(f'{target_ctrl}.footBank', f'{md_node}.input2X')
    cmds.connectAttr(f'{target_ctrl}.footBank', f'{md_node}.input2Y')
    cmds.connectAttr(f'{md_node}.outputX', f'driven_{side}_footOut_ctrl_0001.rotateZ')
    cmds.connectAttr(f'{md_node}.outputY', f'driven_{side}_footIn_ctrl_0001.rotateZ')


   

  
def set_footRoll_attr(target_ctrl=None, foot_lift_value=30, foot_straight_value=60):
    if not target_ctrl:
        target_ctrl = cmds.ls(selection=True)[0]
    side = target_ctrl.split('_')[0]
     
    #add foot Rooll attr 
    cmds.addAttr(target_ctrl, longName='FootRoll', attributeType='enum', enumName='---------------:')
    cmds.setAttr(f'{target_ctrl}.FootRoll', keyable=False, channelBox=True)
    #add attr foot roll lift and foot roll straight
    cmds.addAttr(target_ctrl, longName='footRoll', attributeType='float', defaultValue=0, min=0,keyable=True)
    cmds.addAttr(target_ctrl, longName='footLift', attributeType='float', defaultValue=foot_lift_value, keyable=True)
    cmds.addAttr(target_ctrl, longName='footStraight', attributeType='float', defaultValue=foot_straight_value, keyable=True)

    #create remap node for ball 
    remap_ball_01 = cmds.createNode('remapValue', name=f'{side}_ballRoll_remap_0001')
    cmds.connectAttr(f'{target_ctrl}.footRoll', f'{remap_ball_01}.inputValue')
    cmds.setAttr(f'{remap_ball_01}.inputMin', 0)
    cmds.connectAttr(f'{target_ctrl}.footLift', f'{remap_ball_01}.inputMax')
    cmds.connectAttr(f'{target_ctrl}.footLift', f'{remap_ball_01}.outputMax')
    remap_ball_02 = cmds.createNode('remapValue', name=f'{side}_ballRoll_remap_0002')
    cmds.connectAttr(f'{target_ctrl}.footRoll', f'{remap_ball_02}.inputValue')
    cmds.connectAttr(f'{target_ctrl}.footLift', f'{remap_ball_02}.inputMin')
    cmds.connectAttr(f'{target_ctrl}.footStraight', f'{remap_ball_02}.inputMax')
    cmds.connectAttr(f'{target_ctrl}.footLift', f'{remap_ball_02}.outputMax')
    #subtract remap_ball_02 from remap_ball_01 to get the final ball roll value
    ball_minus = cmds.createNode('plusMinusAverage', name=f'{side}_ballRoll_minus_0001')
    cmds.connectAttr(f'{remap_ball_01}.outValue', f'{ball_minus}.input1D[0]')
    cmds.connectAttr(f'{remap_ball_02}.outValue', f'{ball_minus}.input1D[1]')
    cmds.setAttr(f'{ball_minus}.operation', 2) #subtract
    cmds.connectAttr(f'{ball_minus}.output1D', f'connect_{side}_ballIK_ctrl_0001.rotateZ')
    #time to do the tip roll 
    remap_toe_01 = cmds.createNode('remapValue', name=f'{side}_tipRoll_remap_0001')
    cmds.connectAttr(f'{target_ctrl}.footRoll', f'{remap_toe_01}.inputValue')
    cmds.connectAttr(f'{target_ctrl}.footLift', f'{remap_toe_01}.inputMin')
    cmds.connectAttr(f'{target_ctrl}.footStraight', f'{remap_toe_01}.inputMax')
    cmds.setAttr(f'{remap_toe_01}.outputMax', 60)
    toe_minus = cmds.createNode('plusMinusAverage', name=f'{side}_toeRoll_minus_0001')
    cmds.connectAttr(f'{target_ctrl}.footRoll', f'{toe_minus}.input1D[0]')
    cmds.connectAttr(f'{target_ctrl}.footStraight', f'{toe_minus}.input1D[1]')
    cmds.setAttr(f'{toe_minus}.operation', 2) #subtract
    toe_clamp = cmds.createNode('clampRange', name=f'{side}_toeRoll_clamp_0001')
    cmds.connectAttr(f'{toe_minus}.output1D', f'{toe_clamp}.input')
    cmds.setAttr(f'{toe_clamp}.minimum', 0)
    cmds.setAttr(f'{toe_clamp}.maximum', 180)
    toe_add = cmds.createNode('plusMinusAverage', name=f'{side}_toeRoll_add_0001')
    cmds.connectAttr(f'{remap_toe_01}.outValue', f'{toe_add}.input1D[0]')
    cmds.connectAttr(f'{toe_clamp}.output', f'{toe_add}.input1D[1]')
    cmds.setAttr(f'{toe_add}.operation', 1) #add
    cmds.connectAttr(f'{toe_add}.output1D', f'connect_{side}_footFront_ctrl_0001.rotateZ')
    

   
    




    

    
    






def pole_vector_follow():
    sel = cmds.ls(sl=True)
    pv_ctrl=sel[0]
    side=pv_ctrl.split('_')[0]
    if 'arm'  in pv_ctrl:
        #create driven grp for pv
        driven_grp = cmds.group(pv_ctrl, name=f'driven_{side}_armIKPV_ctrl_0001')
        #create loc and match transform
        upperarm_aim = cmds.createNode('transform', name=f'{side}_upperarmIK_aim_0001')
        cmds.matchTransform(upperarm_aim, f'{side}_upperarm_joint_0001', pos=True, rot=True)
        #zero out the aim
        zero_upperarm_aim = cmds.duplicate(upperarm_aim, name=f'{side}_upperarm_aim_grp_0001')[0]
        cmds.parent(upperarm_aim, zero_upperarm_aim)

        #aim consytraint the grp
        aimCon =  cmds.aimConstraint(f'output_{side}_wristIK_ctrl_0001', upperarm_aim, mo=False, aimVector=(1, 0, 0), 
        upVector = (0,1,0), worldUpType="objectrotation", worldUpObject=f'{side}_upperarm_joint_0001')
        #change world up type to none
        cmds.setAttr(f'{aimCon[0]}.worldUpType', 4)
        #parent the grps to scapula
        cmds.parent(zero_upperarm_aim, f'{side}_scapula_joint_0001')
        #create loc for the pv
        pv_loc_follow = cmds.spaceLocator(name=f'{side}_armPV_loc_0001')[0]
        cmds.parent(pv_loc_follow, upperarm_aim)
        cmds.matchTransform(pv_loc_follow, f'{side}_armIKPV_ctrl_0001', pos=True, rot=True)
        cmds.setAttr(f'{pv_loc_follow}.visibility', 0)
        #point constrain the pv loc to the pv ctrl
        pc = cmds.pointConstraint( pv_loc_follow,driven_grp, mo=True)
        #create attr for pv
        cmds.addAttr(f'{side}_armIKPV_ctrl_0001', ln='pvFollow', at='float', min=0, max=1, dv=0, k=True)
        #connect attr to constraint
        cmds.connectAttr(f'{side}_armIKPV_ctrl_0001.pvFollow', f'{pc[0]}.{pv_loc_follow}W0')
    elif 'leg' in pv_ctrl:
        #create driven grp for pv
        driven_grp = cmds.group(pv_ctrl, name=f'driven_{side}_legIKPV_ctrl_0001')
        #create loc and match transform
        thigh_aim = cmds.createNode('transform', name=f'{side}_thighIK_aim_0001')
        cmds.matchTransform(thigh_aim, f'{side}_thighIK_joint_0001', pos=True, rot=True)
        #zero out the aim
        zero_thigh_aim = cmds.duplicate(thigh_aim, name=f'{side}_thigh_aim_grp_0001')[0]
        cmds.parent(thigh_aim, zero_thigh_aim)

        #aim consytraint the grp
        aimCon =  cmds.aimConstraint(f'output_{side}_wristIK_ctrl_0001', thigh_aim, mo=False, aimVector=(1, 0, 0), 
        upVector = (0,1,0), worldUpType="objectrotation", worldUpObject=f'{side}_thighIK_joint_0001')
        #change world up type to none
        cmds.setAttr(f'{aimCon[0]}.worldUpType', 4)
        #parent the grps to pelvis
        cmds.parent(zero_thigh_aim, 'C_pelvis_joint_0001')
        #create loc for the pv
        pv_loc_follow = cmds.spaceLocator(name=f'{side}_legPV_loc_0001')[0]
        cmds.matchTransform(pv_loc_follow, f'{side}_legIKPV_ctrl_0001', pos=True, rot=True)
        cmds.setAttr(f'{pv_loc_follow}.visibility', 0)
        cmds.parent(pv_loc_follow, thigh_aim)

        #point constrain the pv loc to the pv ctrl
        pc = cmds.pointConstraint( pv_loc_follow,driven_grp, mo=True)
        #create attr for pv
        cmds.addAttr(f'{side}_legIKPV_ctrl_0001', ln='pvFollow', at='float', min=0, max=1, dv=0, k=True)
        #connect attr to constraint
        cmds.connectAttr(f'{side}_legIKPV_ctrl_0001.pvFollow', f'{pc[0]}.{pv_loc_follow}W0')
def add_stretch_rpik(target_ctrl=None,typ='leg'):
    if not target_ctrl:
        target_ctrl = cmds.ls(selection=True)[0]
    side = target_ctrl.split('_')[0]
    part = target_ctrl.split('_')[1]
    if typ=='leg':
        start_jnt = f'{side}_thighIK_joint_0001'
        mid_jnt = f'{side}_kneeIK_joint_0001'
    elif typ=='arm':
        start_jnt = f'{side}_upperarmIK_joint_0001'
        mid_jnt = f'{side}_elbowIK_joint_0001'
    start_loc = cmds.spaceLocator(name=f'{side}_{part}_start_loc_0001')[0]
    start_loc_p = cmds.listRelatives(start_jnt, parent=True)[0]
    cmds.matchTransform(start_loc, start_jnt, pos=True)
    cmds.parent(start_loc, start_loc_p)
    cmds.hide(start_loc)
    end_loc = cmds.spaceLocator(name=f'{side}_{part}_end_loc_0001')[0]
    cmds.matchTransform(end_loc, f'output_{side}_{part}_ctrl_0001', pos=True)
    cmds.parent(end_loc, f'output_{side}_{part}_ctrl_0001')
    cmds.hide(end_loc)


    #create distance node
    dist_node = cmds.createNode('distanceBetween', name=f'{side}_{part}_stretch_distance_0001')
    cmds.connectAttr(f'{start_loc}.worldMatrix[0]', f'{dist_node}.inMatrix1')
    cmds.connectAttr(f'{end_loc}.worldMatrix[0]', f'{dist_node}.inMatrix2')
    #create divider and attr for stretch
    cmds.addAttr(target_ctrl, longName='Stretch', attributeType='enum', enumName='---------------:')
    cmds.setAttr(f'{target_ctrl}.Stretch', keyable=False, channelBox=True)
    cmds.addAttr(target_ctrl, longName='stretch', attributeType='bool', keyable=True)
    #create md to caculate scaleX
    md_node = cmds.createNode('multiplyDivide', name=f'{side}_{part}_stretch_md_0001')
    cmds.setAttr(f'{md_node}.operation', 2) #divide
    cmds.connectAttr(f'{dist_node}.distance', f'{md_node}.input1X')
    orig_dist = cmds.getAttr(f'{dist_node}.distance')
    cmds.setAttr(f'{md_node}.input2X', orig_dist)
    #create condition node to control stretch
    condition_node = cmds.createNode('condition', name=f'{side}_{part}_stretch_condition_0001')
    cmds.connectAttr(f'{target_ctrl}.stretch', f'{condition_node}.firstTerm')
    cmds.setAttr(f'{condition_node}.secondTerm', 1)
    cmds.connectAttr(f'{md_node}.outputX', f'{condition_node}.colorIfTrueR')
    cmds.setAttr(f'{condition_node}.colorIfFalseR', 1)
    cmds.connectAttr(f'{condition_node}.outColorR', f'{start_jnt}.scaleX')
    cmds.connectAttr(f'{condition_node}.outColorR', f'{mid_jnt}.scaleX')


def add_stretch_spineIK(target_ctrl=None,target_joint_prefix=None,):
    return 



def build_splineIK(typ='spine',name=None,middle_jnt_num=3,size=5):
    start_jnt = cmds.ls(sl=True)[0]
    end_jnt = cmds.ls(sl=True)[1]
    side = start_jnt.split('_')[0]
    part = start_jnt.split('_')[1]
    print(part)
    mid_jnt = f'{side}_{part}_joint_{middle_jnt_num:04d}'
    jnts_total=int(end_jnt.split('_')[-1])
    ikh, eff, crv = cmds.ikHandle(
        sj=start_jnt,
        ee=end_jnt,
        sol='ikSplineSolver',
        roc=True,             # Root on curve (checked)
        ccv=True,             # Auto create curve (checked)
        pcv=False,            # Auto parent curve (unchecked)
        scv=False,            # Auto simplify curve (unchecked)
        ns=jnts_total,       # Number of spans (radio)
        twistType='linear',   # Twist type: Linear
        rootTwistMode=False,  # Root twist mode (unchecked)
        name=f'{side}_{part}IK_ikHandle')
    
    #rename the results
    cmds.rename(ikh, f'{side}_{part}_ikHandle_0001')
    cmds.rename(eff, f'{side}_{part}_effector_0001')
    cmds.rename(crv, f'{side}_{part}_ikCurve_0001')

    #create bind joints and match transformation
    bot_bind = cmds.createNode('joint', name=f'{side}_{part}IK_bind_0001')
    cmds.matchTransform(bot_bind, start_jnt, pos=True)
    mid_bind = cmds.createNode('joint', name=f'{side}_{part}IK_bind_0002')
    cmds.matchTransform(mid_bind, mid_jnt, pos=True)
    top_bind = cmds.createNode('joint', name=f'{side}_{part}IK_bind_0003')
    cmds.matchTransform(top_bind, end_jnt, pos=True)
    #bind joints to ikcurve
    sc = cmds.skinCluster(bot_bind, mid_bind, top_bind, f'{side}_{part}_ikCurve_0001', mi=2, tsb=True)
    #create twist loc
    twist_loc_bot = cmds.spaceLocator(name=f'{side}_{part}IKTwist_loc_0001')[0]
    cmds.matchTransform(twist_loc_bot, start_jnt, pos=True, rot=True)
    twist_loc_top = cmds.spaceLocator(name=f'{side}_{part}IKTwist_loc_0002')[0]
    cmds.matchTransform(twist_loc_top, end_jnt, pos=True, rot=True)
    #create zero grp for locs
    twist_loc_bot_zero= cmds.createNode('transform', name=f'zero_{side}_{part}IKTwist_loc_0001')
    cmds.matchTransform(twist_loc_bot_zero, twist_loc_bot, pos=True, rot=True)
    cmds.parent(twist_loc_bot, twist_loc_bot_zero)
    twist_loc_top_zero= cmds.createNode('transform', name=f'zero_{side}_{part}IKTwist_loc_0002')

    cmds.matchTransform(twist_loc_top_zero, twist_loc_top, pos=True, rot=True)
    cmds.parent(twist_loc_top, twist_loc_top_zero)

    #turn on advanced twist
    cmds.setAttr(f'{side}_{part}_ikHandle_0001.dTwistControlEnable', 1) #L_spine_ikHandle_0001.dTwistControlEnable
    #world up type
    cmds.setAttr(f'{side}_{part}_ikHandle_0001.dWorldUpType', 4)
    #forward axis positiveX
    cmds.setAttr(f'{side}_{part}_ikHandle_0001.dForwardAxis', 0)
    #world up axis positiveY
    cmds.setAttr(f'{side}_{part}_ikHandle_0001.dWorldUpAxis', 0)
    cmds.connectAttr(f'{side}_{part}IKTwist_loc_0001.worldMatrix[0]', f'{side}_{part}_ikHandle_0001.dWorldUpMatrix', f=True)
    cmds.connectAttr(f'{side}_{part}IKTwist_loc_0002.worldMatrix[0]', f'{side}_{part}_ikHandle_0001.dWorldUpMatrixEnd', f=True)
    #create ctrl for the bind joints
    if typ=='spine':
        bot_ctrl = cs.create_cube_ctrl(name=f'{side}_hipIK_ctrl_0001',size=size)
        cmds.matchTransform(bot_ctrl, bot_bind, pos=True, rot=True)
        mid_ctrl = cs.create_cube_ctrl(name=f'{side}_waistIK_ctrl_0001',size=size)
        cmds.matchTransform(mid_ctrl, mid_bind, pos=True, rot=True)
        top_ctrl = cs.create_cube_ctrl(name=f'{side}_chestIK_ctrl_0001',size=size)
        cmds.matchTransform(top_ctrl, top_bind, pos=True, rot=True)
    elif typ=='neck':
        bot_ctrl = None
        mid_ctrl = cs.create_circle_ctrl(name=f'{side}_midNeckIK_ctrl_0001',size=size)
        cmds.matchTransform(mid_ctrl, mid_bind, pos=True, rot=True)
        top_ctrl = cs.create_cube_ctrl(name=f'{side}_headIK_ctrl_0001',size=size)
        cmds.matchTransform(top_ctrl, top_bind, pos=True, rot=True)
    elif typ=='other':
        bot_ctrl = None
        mid_ctrl = cs.create_circleX_ctrl(name=f'{side}_{name}IK_ctrl_0001',size=size)
        cmds.matchTransform(mid_ctrl, mid_bind, pos=True, rot=True)
        top_ctrl = cs.create_circleX_ctrl(name=f'{side}_{name}IK_ctrl_0002',size=size)
        cmds.matchTransform(top_ctrl, top_bind, pos=True, rot=True)
    #create_ctrl grp
    for ctrl in [bot_ctrl, mid_ctrl, top_ctrl]:
        if ctrl is None:
            continue
        cmds.select(ctrl)
        cs.create_ctrlgrp_on_ctrl()
    #parent the bind joints to the output grp
    if bot_ctrl:
        cmds.parent(bot_bind, f'output_{bot_ctrl}')
    cmds.parent(mid_bind, f'output_{mid_ctrl}')
    cmds.parent(top_bind, f'output_{top_ctrl}')
    #hide the bind joints
    cmds.hide(bot_bind)
    cmds.hide(mid_bind)
    cmds.hide(top_bind)
    #orient constraint top and bot ctrl
    if bot_ctrl:
        cmds.orientConstraint(bot_ctrl,start_jnt , mo=True)
    cmds.orientConstraint(top_ctrl,end_jnt , mo=True)






   
def build_ik_finger(blend_ctrl='FingerBlend_ctrl_0001'):
    top_joint = cmds.ls(selection=True)[0]
    side = top_joint.split('_')[0]
    blend_ctrl = f'{side}_{blend_ctrl}'
    joint_list = cmds.listRelatives(top_joint, ad=True, type='joint') or []
    if len(joint_list) == 4:
        cmds.warning("Please select a valid finger joint.")
        return
    second_joint = joint_list[2]
    third_joint = joint_list[1]
    end_joint = joint_list[0]
    print(joint_list)
    #duplicate joint chain

    IK_joints= cmds.duplicate(top_joint,rc=True,fullPath=False)
    IK_top_joint = IK_joints[0]
    #rename joints
    IK_joints = cmds.listRelatives(IK_joints[0], ad=True,type='joint')or []
    IK_joints=reversed(list((IK_joints)+[IK_top_joint]))
    for i,j in enumerate(IK_joints):
        side = j.split('_')[0]
        part = j.split('_')[1]
        typ = j.split('_')[2]
        string = j.split('_')[-1]
        if 'end' in j:
            new = f'{side}_{part}IK_end_joint'
        else:
            new = f'{side}_{part}IK_joint_{(i+1):04d}'

        cmds.rename(j, new)


    #create driven joints
    #duplicate joint chain

    Driven_joints= cmds.duplicate(top_joint,rc=True,fullPath=False)
    Driven_top_joint = Driven_joints[0]
    #rename joints
    Driven_joints = cmds.listRelatives(Driven_joints[0], ad=True,type='joint')or []
    Driven_joints=reversed(list((Driven_joints)+[Driven_top_joint]))
    for i,j in enumerate(Driven_joints):
        side = j.split('_')[0]
        part = j.split('_')[1]
        typ = j.split('_')[2]
        if 'end' in j:
            new = f'{side}_{part}IK_end_driven'
        else:
            new = f'{side}_{part}IK_driven_{(i+1):04d}'

        cmds.rename(j, new)
    #create single chain ik
    IK_top_joint = top_joint.replace("_joint","IK_joint")
    IK_second_joint = second_joint.replace("_joint","IK_joint")
    IK_third_joint = third_joint.replace("_joint","IK_joint")
    IK_end_joint = end_joint.replace("_end_joint","IK_end_joint")
    print(IK_end_joint, IK_end_joint)
    ik_handleA = cmds.ikHandle(sj=f'{IK_top_joint}',ee=f'{IK_third_joint}',
                               name=top_joint.replace('_joint','_ikHandle'),sol='ikSCsolver')[0]
    #create ctrl
    ctrl = cmds.circle(name=top_joint.replace('_joint','RtIK_ctrl'),radius=2,nr=[0,0,1])[0]
    cmds.matchTransform(ctrl, IK_end_joint, pos=True, rot=True)
    #adjust the orientation 
    cmds.parent(ctrl, end_joint)
    cmds.setAttr(f'{ctrl}.rotateZ', 180)
    cmds.parent(ctrl, world=True)
    #create ctrl grp 
    cmds.select(ctrl)
    cs.create_ctrlgrp_on_ctrl()
    #lock attr for ctrl and sub ctrl
    sub_ctrl = ctrl.replace('_ctrl','_subctrl')
    cmds.setAttr(f'{ctrl}.translateX', lock=True)
    cmds.setAttr(f'{ctrl}.translateY', lock=True)
    cmds.setAttr(f'{ctrl}.translateZ', lock=True)
    cmds.setAttr(f'{ctrl}.scaleX', lock=True)
    cmds.setAttr(f'{ctrl}.scaleY', lock=True)
    cmds.setAttr(f'{ctrl}.scaleZ', lock=True)
    cmds.setAttr(f'{sub_ctrl}.translateX', lock=True)
    cmds.setAttr(f'{sub_ctrl}.translateY', lock=True)
    cmds.setAttr(f'{sub_ctrl}.translateZ', lock=True)
    cmds.setAttr(f'{sub_ctrl}.scaleX', lock=True)
    cmds.setAttr(f'{sub_ctrl}.scaleY', lock=True)
    cmds.setAttr(f'{sub_ctrl}.scaleZ', lock=True)
    #orient constraint the ctrl to the third joint
    cmds.orientConstraint(ctrl, IK_third_joint, mo=True)
    #parent the ik handle to the output grp
    cmds.parent(ik_handleA, f'output_{ctrl}')
    cmds.hide(ik_handleA)
    # hide the ik joints
    cmds.hide(IK_top_joint)
    #create ik handle for the driven joints
    driven_top= IK_top_joint.replace("_joint","_driven")
    driven_second = IK_second_joint.replace("_joint","_driven")
    driven_end = IK_end_joint.replace("_joint","_driven")

    ik_handleB = cmds.ikHandle(sj=f'{driven_top}',ee=f'{driven_end}',
                            name=top_joint.replace('_joint','_driven_ikHandle'),sol='ikRPsolver')[0]
    #create ctrl
    ctrl_T = cs.create_cube_ctrl(name=top_joint.replace('_joint','TIK_ctrl'))
    cmds.matchTransform(ctrl_T, driven_end, pos=True, rot=True)
    #create ctrl grp
    cmds.select(ctrl_T)
    cs.create_ctrlgrp_on_ctrl()
    #hide driven joints
    cmds.hide(driven_top)
    #lock attr for ctrl_T and sub ctrl
    sub_ctrl_T = ctrl_T.replace('TIK_ctrl','TIK_subctrl')
    cmds.setAttr(f'{ctrl_T}.rotateX', lock=True)
    cmds.setAttr(f'{ctrl_T}.rotateY', lock=True)
    cmds.setAttr(f'{ctrl_T}.rotateZ', lock=True)
    cmds.setAttr(f'{ctrl_T}.scaleX', lock=True)
    cmds.setAttr(f'{ctrl_T}.scaleY', lock=True)
    cmds.setAttr(f'{ctrl_T}.scaleZ', lock=True)
    cmds.setAttr(f'{sub_ctrl_T}.rotateX', lock=True)
    cmds.setAttr(f'{sub_ctrl_T}.rotateY', lock=True)
    cmds.setAttr(f'{sub_ctrl_T}.rotateZ', lock=True)
    cmds.setAttr(f'{sub_ctrl_T}.scaleX', lock=True)
    cmds.setAttr(f'{sub_ctrl_T}.scaleY', lock=True)
    cmds.setAttr(f'{sub_ctrl_T}.scaleZ', lock=True)
    #create pole vector 
    pv = cs.create_cube_ctrl(name=IK_top_joint.replace('_joint','PV_ctrl'))
    cmds.matchTransform(pv, driven_second, pos=True, rot=True)
    cmds.parent(pv, driven_second)
    if side == 'L':
        cmds.setAttr(f'{pv}.translateY', 2)
    elif side == 'R':
        cmds.setAttr(f'{pv}.translateY', -2)
    cmds.parent(pv, world=True)
    cmds.select(pv)
    cs.create_ctrlgrp_on_ctrl()
 
    #create annotation
    ann_shape=cmds.annotate(pv,tx='') 
    cmds.setAttr(f'{ann_shape}.overrideEnabled',1)
    cmds.setAttr(f'{ann_shape}.overrideDisplayType',2)
    #point constraint to the elbow joint
    ann=cmds.listRelatives(ann_shape,p=True)
    cmds.parent(ann,pv)
    cmds.pointConstraint(driven_second, ann, mo=False)
    #parent the ik handle to the output grp
    cmds.parent(ik_handleB, f'output_{ctrl_T}')
    cmds.hide(ik_handleB)
    #create pole vector constraint
    cmds.poleVectorConstraint(pv, ik_handleB)
    #constraint the driven end joint to the ctrl
    cmds.parentConstraint(driven_end,f'driven_{ctrl}', mo=True)
    #set up ikFkBlend
    #add attr for the blend ctrl
    part = top_joint.split('_')[1]
    print(part)
    cmds.addAttr(blend_ctrl, longName=f'{part}IkFkBlend', attributeType='float',
                  min=0, max=1, defaultValue=0, keyable=True)


    fk_joints = [f'{side}_{part}FK_joint_0001',f'{side}_{part}FK_joint_0002',f'{side}_{part}FK_joint_0003']
    ik_joints = [f'{side}_{part}IK_joint_0001',f'{side}_{part}IK_joint_0002',f'{side}_{part}IK_joint_0003']
    main_joints = [f'{side}_{part}_joint_0001',f'{side}_{part}_joint_0002', f'{side}_{part}_joint_0003']

    for i in range(3):
        #constraint the three joints without maintain offset 
        cmds.orientConstraint(fk_joints[i], ik_joints[i], main_joints[i], mo=False, weight=1)

    #create reverse node for blending
    reverse_node = cmds.createNode('reverse', name=f'{side}_{part}_ikFkBlend_reverse')
    cmds.connectAttr(f'{blend_ctrl}.{part}IkFkBlend', f'{reverse_node}.inputX')
    # orient constraint
    for i in range(3):
        constraint_node=f'{main_joints[i]}_orientConstraint1'
        fk_target_attr=f'{constraint_node}.{fk_joints[i]}W0'
        ik_target_attr=f'{constraint_node}.{ik_joints[i]}W1'

        #connect orientConstraint
        
        cmds.connectAttr(f'{reverse_node}.outputX', fk_target_attr)
        cmds.connectAttr(f'{blend_ctrl}.{part}IkFkBlend', ik_target_attr)

    # define the ctrl
    fk_top = f'zero_{fk_joints[0]}'.replace('joint', 'ctrl')
    ik_top = f'zero_{ik_joints[2]}'.replace('joint', 'ctrl')
    ik_pv = f'zero_{side}_{part}IKPV_ctrl_0001'

    #connect FK control visibility
    cmds.connectAttr(f'{reverse_node}.outputX', f'{fk_top}.visibility')
    
    #connect IK controls visibility
    cmds.connectAttr(f'{blend_ctrl}.{part}IkFkBlend', f'zero_{ctrl}.visibility')
    cmds.connectAttr(f'{blend_ctrl}.{part}IkFkBlend', f'zero_{ctrl_T}.visibility')
    cmds.connectAttr(f'{blend_ctrl}.{part}IkFkBlend', f'{ik_pv}.visibility')



def build_springIK_leg(sp_pv=None,rp_pv=None):
    '''sp_pv(str):springIK's pole vector
    rp_pv(str):rotate plane pole vector
    '''
    sels = cmds.ls(selection=True,type='joint')
    if not sels or len(sels) < 2:
        cmds.warning("Please select at least two joints (hip and ankle).")
        return
    if not sp_pv or not rp_pv:
        cmds.warning("Please provide both sp_pv and rp_pv.")
        return
    #define the joints
    hip_joint = sels[0] #hip joint
    ankle_joint = sels[1] #ankle joint
    thigh_joint= cmds.listRelatives(hip_joint, c=True, type='joint')[0] #thigh joint
    shin_joint= cmds.listRelatives(thigh_joint, c=True, type='joint')[0] #shin joint
    ball_joint= cmds.listRelatives(ankle_joint, c=True, type='joint')[0] #ball joint
    toe_joint= cmds.listRelatives(ball_joint, c=True, type='joint')[0] #toe joint
    side =  hip_joint.split('_')[0]
    #duplicate joint chain and clean effectors
    hip_driver = cmds.duplicate(hip_joint,rc=True)[0]
    print(hip_driver)
    #clean up the string number
    hip_driver = cmds.rename(hip_driver,hip_joint.replace('_joint', 'Driver_joint').replace('0002','0001'))
    children = cmds.listRelatives(hip_driver, ad=True, type='joint') or []
    for child in children:
        cmds.rename(child,child.replace('_joint', 'Driver_joint').replace('0002','0001'))
    #get the ankle driver
    shin_driver = shin_joint.replace('_joint', 'Driver_joint')
    ankle_driver = ankle_joint.replace('_joint', 'Driver_joint')
    #delete the rest of the joint 
    cmds.delete(cmds.listRelatives(ankle_driver, c=True, type='joint',f=True)[0])
    #create spring IK handle
    spring_ik = cmds.ikHandle(n = f'{side}_legDriverIK_ikHandle_0001',
                              sj=hip_driver, ee=ankle_driver, solver='ikSpringSolver')[0]
    cmds.poleVectorConstraint(sp_pv, spring_ik)
    #create single chain Ik handles for toe,ball,ankle 
    toe_ik = cmds.ikHandle(n = f'{side}_toeIK_ikHandle_0001', 
                           solver='ikSCsolver',sj = ball_joint,ee=toe_joint)[0]
    ball_ik = cmds.ikHandle(n = f'{side}_ballIK_ikHandle_0001', 
                           solver='ikSCsolver',sj = ankle_joint,ee=ball_joint)[0]
    ankle_ik = cmds.ikHandle(n = f'{side}_ankleIK_ikHandle_0001', 
                           solver='ikSCsolver',sj = shin_joint,ee=ankle_joint)[0]
    #create rotate plane ikHandle for shin 
    shin_ik = cmds.ikHandle(n = f'{side}_shinIK_ikHandle_0001',
                            sj=hip_joint,ee=shin_joint, solver='ikRPsolver')[0]
    cmds.poleVectorConstraint(rp_pv, shin_ik)
    #create pos joint for the ball ctrl 
    ball_pos_P = cmds.createNode('joint', name='ball_pos_P')
    cmds.matchTransform(ball_pos_P, ball_joint)
    cmds.makeIdentity(ball_pos_P,apply=True,r=True)
    ball_pos_C = cmds.createNode('joint',name='ball_pos_C')
    cmds.matchTransform(ball_pos_C, ankle_joint)
    cmds.makeIdentity(ball_pos_C,apply=True,r=True)
    cmds.parent(ball_pos_C, ball_pos_P)
    cmds.select(ball_pos_P)
    cmds.joint(e=True, zso=True,aos=True, oj='xyz', sao='zup')
    #create pos joint for shin ctrl 
    shin_pos_P = cmds.createNode('joint', name='shin_pos_P')
    cmds.matchTransform(shin_pos_P, ankle_joint)
    cmds.makeIdentity(shin_pos_P,apply=True,r=True)
    shin_pos_C = cmds.createNode('joint', name='shin_pos_C')
    cmds.matchTransform(shin_pos_C, shin_joint)
    cmds.makeIdentity(shin_pos_C,apply=True,r=True)
    cmds.parent(shin_pos_C, shin_pos_P)
    cmds.select(shin_pos_P)
    cmds.joint(e=True, zso=True,aos=True, oj='xyz', sao='zup')
    #create ctrl for each part 
    leg_ctrl = cs.create_cube_ctrl(name=f'{side}_legIK_ctrl_0001', size=1.5)
    cmds.matchTransform(leg_ctrl, ankle_joint, pos=True, rot=False)
    cmds.select(leg_ctrl)
    cs.create_ctrlgrp_on_ctrl()
    #oreint constraint to ankle joint
    ankle_o_con = cmds.orientConstraint(f'output_{leg_ctrl}', ankle_joint, mo=True)[0]
    cmds.setAttr(f'{ankle_o_con}.interpType', 2) #set to shortest
    shin_ctrl = cs.create_cone_arrow(name=f'{side}_shinIK_ctrl_0001', size=1)
    shin_ctrl= f'{side}_shinIK_ctrl_0001'
    cmds.matchTransform(shin_ctrl, 'shin_pos_P', pos=True, rot=True)
    cmds.select(shin_ctrl)
    cs.create_ctrlgrp_on_ctrl()
    ball_ctrl = cs.create_cube_ctrl(name=f'{side}_ballIK_ctrl_0001', size=1.5)
    cmds.matchTransform(ball_ctrl, 'ball_pos_P', pos=True, rot=True)
    cmds.select(ball_ctrl)
    cs.create_ctrlgrp_on_ctrl()
    toe_ctrl = cs.create_cube_ctrl(name=f'{side}_toeIK_ctrl_0001', size=1)
    cmds.matchTransform(toe_ctrl, ball_joint, pos=True, rot=True)
    cmds.select(toe_ctrl)
    cs.create_ctrlgrp_on_ctrl()
    shin_pos_ctrl = cs.create_sphere_ctrl(name=f'{side}_shinPos_ctrl_0001', radius = 1)
    cmds.matchTransform(shin_pos_ctrl, shin_joint, pos=True, rot=True)
    cmds.select(shin_pos_ctrl)
    cs.create_ctrlgrp_on_ctrl()
    #delete the pos joints 
    cmds.delete(ball_pos_P, shin_pos_P)
    #parent the ctrls 
    for ctrl in [toe_ctrl, ball_ctrl, shin_ctrl]:
        cmds.parent(f'zero_{ctrl}', f'output_{leg_ctrl}')
    cmds.parent(f'zero_{shin_pos_ctrl}', f'output_{shin_ctrl}')
    #parent the ikHandles
    cmds.parent(ball_ik,ankle_ik,spring_ik,f'output_{ball_ctrl}')
    cmds.parent(shin_ik,f'output_{shin_ctrl}')
    cmds.parent(toe_ik,f'output_{toe_ctrl}')
    #hide ikHandles
    for ik in [ball_ik, ankle_ik, spring_ik, shin_ik, toe_ik]:
        cmds.setAttr(f'{ik}.visibility', 0)
    #create locater for aim constraint 
    aim_loc = cmds.spaceLocator(n=f'{side}_legAim_loc_0001')[0]
    cmds.matchTransform(aim_loc, shin_ctrl, pos=True)
    #create zero grp for the loc 
    zero_aim_loc = cmds.createNode('transform', n=f'zero_{aim_loc}')
    cmds.matchTransform(zero_aim_loc, aim_loc, pos=True, rot=True)
    cmds.parent(aim_loc, zero_aim_loc)
    cmds.hide(aim_loc)
    cmds.parent(zero_aim_loc,f'zero_{shin_ctrl}')

    #aim constraint loc to shin driver 
    cmds.aimConstraint(shin_driver, aim_loc , aimVector=[1, 0, 0], upVector=[0, 1, 0],
                       worldUpType=1, worldUpObject=rp_pv)
    #create offset grp for the loc 
    offsetA = cmds.createNode('transform', n=f'{side}_shinAim_locOffset_0001')
    cmds.matchTransform(offsetA, aim_loc, pos=True)
    offsetB = cmds.duplicate(offsetA)[0]
    cmds.parent(offsetB, offsetA)
    cmds.parent(offsetA,aim_loc)
    #aim constraint loc to driver shin 
    o_con = cmds.orientConstraint(offsetB,f'driven_{shin_ctrl}', mo=True)[0]
    cmds.setAttr(f'{o_con}.interpType', 2) #set to shortest
    #point constraint the shinIK handle to the shin pos 
    cmds.pointConstraint(f'output_{shin_pos_ctrl}', shin_ik, mo=False)
    #point constraint the ankle driver to the zero shin ctrl
    cmds.pointConstraint( ankle_driver,f'zero_{shin_ctrl}', mo=True)

    # constraint both sides spring driver to the hip driver
    pelvis_joint = cmds.listRelatives(hip_joint, p=True)[0]
    L_driver_grp = cmds.createNode('transform', n=f'L_legDriver_grp')

    cmds.matchTransform(L_driver_grp, hip_driver, pos=True)
  
    cmds.parent(hip_driver, L_driver_grp)

    cmds.parentConstraint(pelvis_joint, L_driver_grp, mo=True)


    #print complete message
    print("Spring IK leg rig L side complete.")
    print('plz adjust the shape of the ctrls and then mirror it later')
    