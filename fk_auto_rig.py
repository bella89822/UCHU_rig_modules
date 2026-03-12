import maya.cmds as cmds
import rig_modules.controller_shape as cs


def fk_to_constraint(type='parent'):
    sel_joints=cmds.ls(selection=True,type='joint')
    if not sel_joints:
        cmds.warning("Please select at least one joint.")
        return
    for joint in sel_joints:
        if 'end ' in joint:
            continue
        output_ctrl = 'output_'+ joint.replace('joint','ctrl')

        if cmds.objExists(output_ctrl):
            if type=='parent':
                con = cmds.parentConstraint(output_ctrl, joint, mo=False)
                cmds.setAttr(f'{con[0]}.interpType', 2)
            elif type=='point':
                cmds.pointConstraint(output_ctrl, joint, mo=False)
            elif type=='orient':
                con = cmds.orientConstraint(output_ctrl, joint, mo=False)
                cmds.setAttr(f'{con[0]}.interpType', 2)
            elif type=='scale':
                cmds.scaleConstraint(output_ctrl, joint, mo=False)



def auto_splineFK(ctrl_shape=None):
    FK_list = cmds.ls(selection=True, type='joint')

    if not FK_list:
        cmds.warning("Please select at least one spine joint.")
        return

    parent_ctrl = None
    top_node = None
    for fk in FK_list:
        parts = fk.split('_')
        string = parts[-1]  # sequence number, e.g. 0001
        part = parts[1] if len(parts) > 1 else 'spine'

        # create FK ctrl
        ctrl = cs.create_ctrl_from_shape(ctrl_shape)[0]
        cmds.matchTransform(ctrl, fk, pos=True)

        # parent to previous FK ctrl
        if parent_ctrl:
            cmds.parent(ctrl, parent_ctrl)

        # update parent
        parent_ctrl = ctrl
        if not top_node:
            top_node = ctrl

    #create grp
    cmds.select(top_node)
    cs.create_ctrlgrp_on_ctrl()

def add_hand_pose(pose=None):
    L_pose_ctrl = cmds.ls(selection=True)[0]
    R_pose_ctrl = L_pose_ctrl.replace('L_', 'R_')
    # add pose for the ctrl
    cmds.addAttr(L_pose_ctrl, longName=f'{pose}', attributeType='float', min=0, max=1, defaultValue=0, keyable=True)
    cmds.addAttr(R_pose_ctrl, longName=f'{pose}', attributeType='float', min=0, max=1, defaultValue=0, keyable=True)
    L_fingers_list=['L_thumb_ctrl_0001','L_thumb_ctrl_0002','L_thumb_ctrl_0003',
                  'L_metacarpel_ctrl_0001','L_index_ctrl_0001','L_index_ctrl_0002','L_index_ctrl_0003',
                  'L_metacarpel_ctrl_0002','L_middle_ctrl_0001','L_middle_ctrl_0002','L_middle_ctrl_0003',
                  'L_metacarpel_ctrl_0003','L_ring_ctrl_0001','L_ring_ctrl_0002','L_ring_ctrl_0003',
                  'L_metacarpel_ctrl_0004','L_pinky_ctrl_0001','L_pinky_ctrl_0002','L_pinky_ctrl_0003',
                  ]
    R_fingers_list = [finger.replace('L_','R_') for finger in L_fingers_list]
    #loopside
    for finger in L_fingers_list:
        R_finger = finger.replace('L_','R_')
        connect_grp = f'connect_{finger}'
        R_connect_grp = connect_grp.replace('L_','R_')

        #loop XYZ axis
        for attr in ['rotateX','rotateY','rotateZ']:
            #get value from the ctrls
            val = cmds.getAttr(f'{finger}.{attr}')
            #to avoid 0 value being keyed
            if val != 0:
                #set driven key for L side
                cmds.setDrivenKeyframe(f'{connect_grp}.{attr}', cd=f'{L_pose_ctrl}.{pose}',dv=0,v=0)
                cmds.setDrivenKeyframe(f'{connect_grp}.{attr}', cd=f'{L_pose_ctrl}.{pose}',dv=1,v=val)
                #set driven key for R side
                cmds.setDrivenKeyframe(f'{R_connect_grp}.{attr}', cd=f'{R_pose_ctrl}.{pose}',dv=0,v=0)
                cmds.setDrivenKeyframe(f'{R_connect_grp}.{attr}', cd=f'{R_pose_ctrl}.{pose}',dv=1,v=val)
                #zero out fingers
                cmds.setAttr(f'{finger}.{attr}',0)
                cmds.setAttr(f'{R_finger}.{attr}',0)


def create_auto_breath(target=None):
    if not target:
        cmds.warning("Please provide a valid target object.")
        return
    #create attribute
    #create divider
    cmds.addAttr(target, longName='autoBreathDivider', attributeType='enum', enumName='autoBreathe')
    cmds.setAttr(f'{target}.autoBreathDivider', lock=True,channelBox=True)
    cmds.addAttr(target, longName='autoBreathe', attributeType='bool')
    cmds.setAttr(f'{target}.autoBreathe', keyable=True)
    # Amplitude
    cmds.addAttr(target, longName='Amplitude', attributeType='float', defaultValue=1, min=0, max=2)
    cmds.setAttr(f'{target}.Amplitude', keyable=True) 

    # Frequency
    cmds.addAttr(target, longName='Frequency', attributeType='float', defaultValue=1, min=0)
    cmds.setAttr(f'{target}.Frequency', keyable=True)

    # Offset
    cmds.addAttr(target, longName='Offset', attributeType='float', defaultValue=0)
    cmds.setAttr(f'{target}.Offset', keyable=True)
    #create nodes and connect
    time_node = 'time1'
    multiply_node = cmds.createNode('multiplyDivide', name='autoBreath_mult_frequency')
    cmds.connectAttr(f'{time_node}.outTime', f'{multiply_node}.input1X', force=True)
    cmds.connectAttr(f'{target}.Frequency', f'{multiply_node}.input2X', force=True)
    add_offset_node = cmds.createNode('addDoubleLinear', name='autoBreath_add_offset')
    sine_node = cmds.createNode('sin', name='autoBreath_sinNode')
    cmds.connectAttr(f'{multiply_node}.outputX', f'{add_offset_node}.input1', force=True)
    cmds.connectAttr(f'{target}.Offset', f'{add_offset_node}.input2', force=True)
    cmds.connectAttr(f'{add_offset_node}.output', f'{sine_node}.input', force=True)
    multiply_amplitude_node = cmds.createNode('multiply', name='autoBreath_mult_amplitude')
    cmds.connectAttr(f'{sine_node}.output', f'{multiply_amplitude_node}.input[0]', force=True)
    cmds.connectAttr(f'{target}.Amplitude', f'{multiply_amplitude_node}.input[1]', force=True)
    cmds.connectAttr(f'{target}.autoBreathe',  f'{multiply_amplitude_node}.input[2]', force=True)
    #connect to target connect grp translateY
    target_connect_grp = 'connect_' + target
    cmds.connectAttr(f'{multiply_amplitude_node}.output', f'{target_connect_grp}.translateY', force=True)
    add_ty = cmds.createNode('addDoubleLinear', name='autoBreath_add_translateY')
    cmds.connectAttr(f'{target_connect_grp}.translateY', f'{add_ty}.input1', force=True)
    cmds.connectAttr(f'{target}.translateY', f'{add_ty}.input2', force=True)
    cmds.connectAttr(f'{add_ty}.output', 'C_sternum_remap_0001.inputValue', force=True)