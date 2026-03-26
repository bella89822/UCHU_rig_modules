import maya.cmds as cmds 

def add_twist_joint_ikhandle_skeleton(type= None):
    sels = cmds.ls(selection=True, type='joint')
    if len(sels) !=2:
        cmds.warning('Please select two joints')
        return
    #define joints and side
    jointA = sels[0]
    jointB = sels[1]
    side = jointA.split('_')[0]   

    if type == 'forearm' or type == 'shin':
        #create  twist joint and match transformation 
        twistA = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0001' ) 
        cmds.matchTransform(twistA, jointA, pos=True, rot=True)
        #freeze the joint
        cmds.makeIdentity(twistA, apply=True, t=1, r=1, s=1)
        twistB = cmds.duplicate(twistA,name=f'{side}_{type}Twist_joint_0002' )[0]
        cmds.matchTransform(twistB, jointB, pos=True, rot=False)
        #freeze the joint
        cmds.makeIdentity(twistB, apply=True, t=1, r=1, s=1)
        #parent twist joints
        cmds.parent(twistB, twistA) 
        #create IK handle 
        twistIK_handle = cmds.ikHandle(name=f'{side}_{type}Twist_ikhandle_0001', startJoint=twistA, endEffector=twistB, solver='ikSCsolver')[0]
        cmds.hide(twistIK_handle)
        #parent Ik handle to jointB
        cmds.parent(twistIK_handle, jointB)
        #parent twistA to jointA
        cmds.parent(twistA, jointA)
        #create twist joint for the skeleton and freeze them
        twistJoint_skelA = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0001' )
        cmds.matchTransform(twistJoint_skelA, jointA, pos=True, rot=True)
        cmds.makeIdentity(twistJoint_skelA, apply=True, t=1, r=1, s=1)
        twistJoint_skelB = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0002' )
        cmds.matchTransform(twistJoint_skelB, jointA, pos=True, rot=True)       
        cmds.makeIdentity(twistJoint_skelB, apply=True, t=1, r=1, s=1)
        #let's move twistjointB to the middle
        pC = cmds.pointConstraint(twistA, twistB, twistJoint_skelB, mo=False)[0]
        cmds.delete(pC)
        #orient constrain twistJoint_skelB to twistB
        cmds.orientConstraint(twistB, twistJoint_skelB, mo=True)
        #parent the skeleton joints
        cmds.parent(twistJoint_skelB, twistJoint_skelA)

    elif type== 'upperarm' or type == 'thigh':
        #create twist joint and match transformation
        #create  twist joint and match transformation 
        twistA = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0001' ) 
        cmds.matchTransform(twistA, jointA, pos=True, rot=True)
        #freeze the joint
        cmds.makeIdentity(twistA, apply=True, t=1, r=1, s=1)
        twistB = cmds.duplicate(twistA,name=f'{side}_{type}Twist_joint_0002' )[0]
        cmds.matchTransform(twistB, jointB, pos=True, rot=False)
        #freeze the joint
        cmds.makeIdentity(twistB, apply=True, t=1, r=1, s=1)
        #parent twist joints
        cmds.parent(twistB, twistA) 
        #create IK handle 
        twistIK_handle = cmds.ikHandle(name=f'{side}_{type}Twist_ikhandle_0001', startJoint=twistA, endEffector=twistB, solver='ikSCsolver')[0]
        cmds.hide(twistIK_handle)
        #parent Ik handle to jointA's parent
        parent_jointA = cmds.listRelatives(jointA, parent=True)[0]
        cmds.parent(twistIK_handle, parent_jointA)
        #point constraint ikHandle to jointB
        cmds.pointConstraint(jointB, twistIK_handle, mo=True)
        #parent twistA to jointA
        cmds.parent(twistA, jointA)
        #create twist joint for the skeleton 
        twistJoint_skelA = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0001' )
        #match transformation to twistA
        cmds.matchTransform(twistJoint_skelA, twistA, pos=True, rot=True)
        #freeze the joint
        cmds.makeIdentity(twistJoint_skelA, apply=True, t=1, r=1, s=1)
        #put it in the middle
        pC = cmds.pointConstraint(twistA, twistB, twistJoint_skelA, mo=False)[0]
        cmds.delete(pC)
        #orient constrain twistJoint_skelA to twistB
        cmds.orientConstraint(jointA, twistJoint_skelA, mo=False)


def add_twist_joint_matrix_skeleton(type= None):
    sels = cmds.ls(selection=True, type='joint')
    if len(sels) !=2:
        cmds.warning('Please select two joints')
        return
    #define joints and side
    jointA = sels[0]
    jointB = sels[1]
    side = jointA.split('_')[0]   

    if type == 'forearm' :
        #create  twist joint and match transformation 
        twistA = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0001' ) 
        cmds.matchTransform(twistA, jointA, pos=True, rot=True)
        twistB = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0002' )
        cmds.matchTransform(twistB, jointB, pos=True, rot=True)
        #parent twist joints
        cmds.parent(twistB, twistA) 
        #create eular nodes
        EtoQ = cmds.createNode('eulerToQuat', name=f'{side}_{type}Twist_EtoQ_0001')
        QtoE = cmds.createNode('quatToEuler', name=f'{side}_{type}Twist_QtoE_0001')
        cmds.connectAttr(f'{twistA}.rotate', f'{EtoQ}.input', force=True)
        cmds.connectAttr(f'{EtoQ}.outputQuatX', f'{QtoE}.inputQuatX', force=True)
        cmds.connectAttr(f'{EtoQ}.outputQuatW', f'{QtoE}.inputQuatW', force=True)
        #connectQtoE to twistB rotX
        cmds.connectAttr(f'{QtoE}.outputQuatX', f'{twistB}.rotateX', force=True)
        
        #parent twistA to jointA
        cmds.parent(twistA, jointA)
        #create twist joint for the skeleton 
        twistJoint_skelA = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0001' )
        cmds.matchTransform(twistJoint_skelA, jointA, pos=True, rot=True)
        twistJoint_skelB = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0002' )
        cmds.matchTransform(twistJoint_skelB, jointB, pos=True, rot=True)
        #let's move twistjointB to the middle
        pC = cmds.pointConstraint(twistA, twistB, twistJoint_skelB, mo=True)[0]
        cmds.delete(pC)
        #orient constrain twistJoint_skelB to twistB
        cmds.orientConstraint(twistB, twistJoint_skelB, mo=True)
    elif type == 'shin':

         #create  twist joint and match transformation 
        twistA = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0001' ) 
        cmds.matchTransform(twistA, jointA, pos=True, rot=True)
        twistB = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0002' )
        cmds.matchTransform(twistB, jointB, pos=True, rot=True)
        #parent twist joints
        cmds.parent(twistB, twistA) 
        #create eular nodes
        EtoQ = cmds.createNode('eulerToQuat', name=f'{side}_{type}Twist_EtoQ_0001')
        QtoE = cmds.createNode('quatToEuler', name=f'{side}_{type}Twist_QtoE_0001')
        cmds.connectAttr(f'{twistA}.rotate', f'{EtoQ}.input', force=True)
        cmds.connectAttr(f'{EtoQ}.outputQuatX', f'{QtoE}.inputQuatX', force=True)
        cmds.connectAttr(f'{EtoQ}.outputQuatW', f'{QtoE}.inputQuatW', force=True)
        #connectQtoE to twistB rotX
        cmds.connectAttr(f'{QtoE}.outputQuatX', f'{twistB}.rotateX', force=True)
        
        #parent twistA to jointA
        cmds.parent(twistA, jointA)
        #create twist joint for the skeleton 
        twistJoint_skelA = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0001' )
        cmds.matchTransform(twistJoint_skelA, jointA, pos=True, rot=True)
        twistJoint_skelB = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0002' )
        cmds.matchTransform(twistJoint_skelB, jointB, pos=True, rot=True)
        #let's move twistjointB to the middle
        pC = cmds.pointConstraint(twistA, twistB, twistJoint_skelB, mo=True)[0]
        cmds.delete(pC)
        #orient constrain twistJoint_skelB to twistB
        cmds.orientConstraint(twistB, twistJoint_skelB, mo=True)
    elif type== 'upperarm' or type == 'thigh':
        #create twist joint and match transformation
        #create  twist joint and match transformation 
        twistA = cmds.createNode('joint',name=f'{side}_{type}Twist_joint_0001' ) 
        cmds.matchTransform(twistA, jointA, pos=True, rot=True)
        #freeze the joint
        cmds.makeIdentity(twistA, apply=True, t=1, r=1, s=1)
        twistB = cmds.duplicate(twistA, name=f'{side}_{type}Twist_joint_0002')[0]
        cmds.matchTransform(twistB, jointB, pos=True, rot=False)
        #freeze the joint
        cmds.makeIdentity(twistB, apply=True, t=1, r=1, s=1)
        #parent twist joints
        cmds.parent(twistB, twistA) 
        #create euler nodes
        EtoQ = cmds.createNode('eulerToQuat', name=f'{side}_{type}Twist_EtoQ_0001')
        QtoE = cmds.createNode('quatToEuler', name=f'{side}_{type}Twist_QtoE_0001')
        cmds.connectAttr(f'{twistA}.rotate', f'{EtoQ}.inputRotate', force=True)
        cmds.connectAttr(f'{EtoQ}.outputQuatX', f'{QtoE}.inputQuatX', force=True)
        cmds.connectAttr(f'{EtoQ}.outputQuatW', f'{QtoE}.inputQuatW', force=True)
        #inverse rot X by minusing 
        #create md node 
        md_node = cmds.createNode('multiplyDivide', name=f'{side}_{type}Twist_md_0001')
        cmds.connectAttr(f'{QtoE}.outputRotateX', f'{md_node}.input1X', force=True)
        cmds.setAttr(f'{md_node}.operation', 1)  # Set operation to multiply
        cmds.setAttr(f'{md_node}.input2X', -1, force=True)
        #connect it back to the non twist jointA
        cmds.connectAttr(f'{md_node}.outputX', f'{jointA}.rotateX', force=True)

        #parent twistA to jointA
        cmds.parent(twistA, jointA)
        #create twist joint for the skeleton 
        twistJoint_skelA = cmds.createNode('joint',name=f'{side}_{type}Twist_skeleton_0001' )
        #match transformation to twistA
        cmds.matchTransform(twistJoint_skelA, twistA, pos=True, rot=True)
        #freeze the joint
        cmds.makeIdentity(twistJoint_skelA, apply=True, t=1, r=1, s=1)
        #put it in the middle
        pC = cmds.pointConstraint(twistA, twistB, twistJoint_skelA, mo=False)[0]
        cmds.delete(pC)
        #orient constrain twistJoint_skelA to twistB
        cmds.orientConstraint(jointA, twistJoint_skelA, mo=False)









def create_slider_joints():
    jnts = cmds.ls(selection=True,type='joint')

    for jnt in jnts:
        side = jnt.split('_')[0]
        part = jnt.split('_')[1]
        #create avg joint
        avg_jnt = cmds.createNode('joint',name=f'{side}_{part}Avg_joint_0001')
        cmds.matchTransform(avg_jnt, jnt, pos=True, rot=True)
        cmds.makeIdentity(avg_jnt, apply=True, t=1, r=1, s=1)
        cmds.parent(avg_jnt, jnt)
        #create slider joints
        slider_jntA = cmds.createNode('joint', name=f'{side}_{part}Slider_joint_0001')
        slider_jntB = cmds.createNode('joint', name=f'{side}_{part}Slider_joint_0002')
        cmds.matchTransform(slider_jntA, jnt, pos=True, rot=True)
        cmds.matchTransform(slider_jntB, jnt, pos=True, rot=True)
        cmds.makeIdentity(slider_jntA, apply=True, t=1, r=1, s=1)
        cmds.makeIdentity(slider_jntB, apply=True, t=1, r=1, s=1)
        cmds.parent(slider_jntB, avg_jnt)
        cmds.parent(slider_jntA, avg_jnt)
    
    
    




def create_muscle_joint(parent = None,driver_joint = None,pos_override = None, skip_translate = None,up_vector = None, 
                        volumeY=1,volumeZ=1,pos_limit = None, connect_driver = None,connect_attrs = None,
                          connect_weight = 1,mirror = True):
    '''Args:
    parent (str): parent of the loc 
    driver_joint(str): driver for muscle behavior 
    position_ovverride(str): if the muscle joint need to follow the other node's position
    but keep the space under the parent joint 
    skip_translate(list): skip translation for aim target 
    pos_limit(list): aim target's translation limit, the format will be like 
    [[xmin,xmax],[ymin,ymax],[zmin,zmax]], use None if no limitation value,
    for example:[[-1,None],....]
    connect_driver(str): if needed like bicep 
    connect_attrs: the attrs you wanna connect, for example:  [driverattr,drivenAttr]
    connect_weight(float): weight between driver and driven 
    mirror(bool): mirror setup from L to R   
    '''
    
    sels = cmds.ls(selection=True)
    if len(sels) != 2:
        cmds.warning("Please select exactly two objects.")
        return
    BPjointA = sels[0]
    BPjointB = sels[1]
    if cmds.listRelatives(BPjointA, children = True)[0] != BPjointB:
        cmds.warning('select parent first and then kid')

    #define side and parts 
    side = BPjointA.split('_')[0]

    
    #duplicate for the joints
    jointA = cmds.duplicate(BPjointA,name=BPjointA.replace('BPjoint','joint'))[0] 
    jointB = cmds.listRelatives(jointA,children= True,fullPath=True)[0]
    jointB= cmds.rename(jointB,BPjointB.replace('_BPjoint','_joint'))
    
    #create grp for joints 
    joint_grp = cmds.createNode("transform", name=f"{jointA}_grp")
    #match transform to jointA
    cmds.matchTransform(joint_grp, jointA)
    #put jointA and jointB under the group
    cmds.parent(jointA, joint_grp)
    #parent the joint grp under it's parent 
    cmds.parent(joint_grp,parent)
    
    #constraint if have node name in position override 
    if pos_override:
        cmds.parentConstraint(pos_override,jointA,mo=True,skipRotate=['x','y','z'])
        
    #create locator for stretch and squash
    target_loc = cmds.spaceLocator(name=jointA.replace('_joint', 'Target_loc'))[0]
    #create zero and driven grp
    zero = cmds.createNode("transform", name=f"zero_{target_loc}")
    driven = cmds.createNode("transform", name=f"driven_{target_loc}")
    connect = cmds.createNode("transform", name=f"connect_{target_loc}")
    cmds.parent(connect, driven)
    cmds.parent(driven, zero)
    cmds.parent(target_loc,driven)
    cmds.hide(target_loc)
    #match transform to jointB
    cmds.matchTransform(zero, jointB)
    #parent it to the joint_grp 
    cmds.parent(zero,joint_grp)
    #check the skip translate attr
    if skip_translate:
        skip_translate=skip_translate
    else:
        skip_translate='none' 
    
    #parent constraint the driven and break rot connection
    cmds.parentConstraint(driver_joint, driven, skipRotate = ['x', 'y', 'z'],skipTranslate=skip_translate, mo=True)
    for axis in ["X", "Y", "Z"]:
        attr = f"{driven}.rotate{axis}"
        connections = cmds.listConnections(attr, s=True, d=False)
        if connections:
            for conn in connections:
                cmds.disconnectAttr(conn, attr)

    #aim constraint jointA to locator
    tx_val = cmds.getAttr(f'{jointB}.translateX')
    if tx_val >=0:
        aim_vector = [1,0,0]
    else:
        aim_vector = [-1,0,0]
    if not up_vector:
        up_vector = [0,1,0]

    cmds.aimConstraint(target_loc, jointA, aimVector= aim_vector, upVector = up_vector , 
                       worldUpType='none', maintainOffset=False)
    #connect attribute for aimTarg's connect grp 
    if connect_driver and connect_attrs:
        mult = cmds.createNode('multDoubleLinear',name = jointA.replace('joint','mult'))
        cmds.connectAttr(f'{connect_driver}.{connect_attrs[0]}',f'{mult}.input1')
        cmds.setAttr(f'{mult}.input2',connect_weight)
        cmds.connectAttr(f'{mult}.output',f'{connect}.{connect_attrs[1]}')
    #set pos limitation 
    if pos_limit:
        pos_info = {}
        for axis, limits in zip(['x','y','z'],pos_limit):
            # [[x_min, x_max], [y_min, y_max], [z_min, z_max]]
            # x, [x_min, x_max]/None
            if limits:
                enable_limits = [False,False]
                limits_value = [-10,10]
                min = limits[0]
                max = limits[1]
                if min is not None:
                    enable_limits[0] = True
                    limits_value[0] = limits[0]
                elif max is not None:
                    enable_limits[1] = True
                    limits_value[1] = limits[1]
                
                #update dict 
                pos_info.update({'enable_'+axis:enable_limits,
                                 'limit_'+axis: limits_value })
        #give out default value just in case
        cmds.transformLimits(driven,translationX=pos_info.get('limit_x',[-100,100]),
                             enableTranslationX=pos_info.get('enable_x',[False,False]),
                             translationY=pos_info.get('limit_y',[-100,100]),
                             enableTranslationY=pos_info.get('enable_y',[False,False]),
                             translationZ=pos_info.get('limit_z',[-100,100]),
                             enableTranslationZ=pos_info.get('enable_z',[False,False]),
                             )






 

    #create loc to caculate distance
    distance_loc = cmds.spaceLocator(name=target_loc.replace('Target','Distance'))[0]
    cmds.parent(distance_loc, joint_grp)
    cmds.hide(distance_loc)
    #point constraint distance_loc to target loc
    cmds.pointConstraint(target_loc, distance_loc, mo=False)
    #caculate distance between jointA and distance_loc
    DB = cmds.createNode("distanceBetween", name=jointA.replace("Joint", "DB"))
    cmds.connectAttr(f"{jointA}.translate", f"{DB}.point1")
    cmds.connectAttr(f"{distance_loc}.translate", f"{DB}.point2")

    #create multidivide to caculate the ratio
    MD = cmds.createNode('multiplyDivide', name=jointA.replace("Joint", "Ratio"))
    cmds.setAttr(f"{MD}.operation", 2)  # Set to divide
    cmds.connectAttr(f"{DB}.distance", f"{MD}.input1X")
    cmds.connectAttr(f"{DB}.distance", f"{MD}.input2Y")
    originD = cmds.getAttr(f"{MD}.input1X")
    cmds.setAttr(f"{MD}.input2X", originD)
    cmds.setAttr(f"{MD}.input1Y", originD)
    #X is for scaleX, Y is for scaleY and scaleZ
    #create volume attr for jointA
    if not cmds.attributeQuery('volumeY',node=jointA,exists = True):
        cmds.addAttr(jointA, longName="volumeY", attributeType="float", defaultValue=volumeY, minValue=0.0, keyable=True)
        cmds.addAttr(jointA, longName="volumeZ", attributeType="float", defaultValue=volumeZ, minValue=0.0, keyable=True)

    #create power node for scale Y,Z
    POW = cmds.createNode('multiplyDivide', name=jointA.replace("Joint", "Power"))
    cmds.setAttr(f"{POW}.operation", 3)  # Set to power
    cmds.connectAttr(f"{MD}.outputY", f"{POW}.input1Y")
    cmds.connectAttr(f"{MD}.outputY", f"{POW}.input1Z")
    cmds.connectAttr(f"{jointA}.volumeY", f"{POW}.input2Y")
    cmds.connectAttr(f"{jointA}.volumeZ", f"{POW}.input2Z")
    #connect scaleX
    cmds.connectAttr(f"{MD}.outputX", f"{jointA}.scaleX")
    #connect scaleY and scaleZ
    cmds.connectAttr(f"{POW}.outputY", f"{jointA}.scaleY")
    cmds.connectAttr(f"{POW}.outputZ", f"{jointA}.scaleZ")

    pos_limit_mirror= []
    #check if it needs to be mirrored
    if mirror and side =='L':
        #mirror the value from for the pos limitation 
        #L_max*-1 = R_min 
        

        if pos_limit:
            for limits in pos_limit:
                if limits:
                    limits_mirror= [None,None]
                    min = limits[0]
                    max = limits[1]
                    if min is not None :
                        #limit mirror max
                        limits_mirror[1] = -min
                    if max is not None :
                        #limit mirror max
                        limits_mirror[0] = -max
                    pos_limit_mirror.append(limits_mirror)

                else:
                    pos_limit_mirror(None)
        #get mirrored pos_override
        pos_override_mirror = None
        if pos_override:
            pos_override_mirror = pos_override.replace('L','R')

        #get mirrored parent 
        connect_driver_mirror = None
        if connect_driver:
            connect_driver_mirror = connect_driver.replace('L','R') 
        #mirror joint
        cmds.mirrorJoint(BPjointA,mirrorYZ=True,mirrorBehavior = True ,searchReplace=['L_','R_'])
    
        
        #select new jointA and jointB 
        cmds.select(BPjointA.replace('L','R'),BPjointB.replace('L','R'))

        create_muscle_joint( parent = parent.replace('L','R'),driver_joint = driver_joint.replace('L','R'),pos_override= pos_override_mirror,
                            skip_translate = skip_translate,up_vector = up_vector, pos_limit = pos_limit_mirror, connect_driver = connect_driver_mirror,
                            connect_attrs = connect_attrs,connect_weight = connect_weight,mirror = False)



def create_twist_joints(typ=None):
    if typ not in ['forearm','upperarm','shin','thigh']:
        cmds.warning('Please provide correct type: forearm, upperarm, shin, thigh')
        return
    sels = cmds.ls(selection=True, type='joint')
    if len(sels) !=2:
        cmds.warning('Please select two joints')
        return
    #define joints and side
    jointA = sels[0]
    jointB = sels[1]
    if cmds.listRelatives(jointA, children = True)[0] != jointB:
        cmds.warning('select parent first and then kid')
    side = jointA.split('_')[0]
    #create twist guide joint and ikHandle 
    g_jointA = cmds.createNode('joint',name = f'{side}_{typ}Twist_joint_0001')
    cmds.matchTransform(g_jointA,jointA,pos=True,rot=True)
    cmds.parent(g_jointA,jointA)
    cmds.makeIdentity(g_jointA,t=0,r=1,apply=True)
    g_jointB = cmds.duplicate(g_jointA,name=f'{side}_{typ}Twist_joint_0002')[0]
    cmds.matchTransform(g_jointB,jointB,pos=True,rot=False)
    cmds.parent(g_jointB,g_jointA)
    cmds.hide(g_jointA,g_jointB)
    ikHandle = cmds.ikHandle(sj = g_jointA, ee = g_jointB,sol = 'ikSCsolver',name = f'{side}_{typ}Twist_ikHandle_0001')[0]
    cmds.hide(ikHandle)
    #create twist joints in between
    parent = jointA
    for i in range(5):
        twistJoint = cmds.createNode('joint',name=f'{side}_{typ}TwistBind_joint_{str(i+1).zfill(4)}' )
        cmds.hide(twistJoint)
        cmds.matchTransform(twistJoint,jointA)
        cmds.makeIdentity(twistJoint,t=0,r=1,s=1,apply=True)
        #position it in between
        factorB= i/4
        factorA= 1 - factorB  
        point_con = cmds.pointConstraint(jointA, jointB, twistJoint, mo=False)[0]
        cmds.setAttr(f'{point_con}.w0', factorA)
        cmds.setAttr(f'{point_con}.w1', factorB)
        cmds.delete(point_con) 

        cmds.parent(twistJoint,parent)
        parent= twistJoint
    if typ == 'forearm' or typ == 'shin':
        md = cmds.createNode('multiplyDivide',name = f'{side}_{typ}Twist_MD_0001')
        cmds.setAttr(f'{md}.input1X',0.25)
        cmds.setAttr(f'{md}.input1Y',0.5)
        cmds.setAttr(f'{md}.input1Z',0.5)
        cmds.connectAttr(f'{g_jointA}.rotateX',f'{side}_{typ}TwistBind_joint_0005.rotateX')
        axis = ['X','Y','Z'] 
        for i,a  in enumerate  (axis):
            cmds.connectAttr(f'{g_jointA}.rotateX',f'{md}.input2{a}')
            cmds.connectAttr(f'{md}.output{a}',f'{side}_{typ}TwistBind_joint_000{i+2}.rotateX')
        cmds.parent(ikHandle,jointB)

    if typ =='upperarm' or typ =='thigh':
        md = cmds.createNode('multiplyDivide',name = f'{side}_{typ}Twist_MD_0001')
        cmds.setAttr(f'{md}.input1X',0.75)
        cmds.setAttr(f'{md}.input1Y',0.5)
        cmds.setAttr(f'{md}.input1Z',0.25)
        cmds.connectAttr(f'{g_jointA}.rotateX',f'{side}_{typ}TwistBind_joint_0001.rotateX')
        axis = ['X','Y','Z'] 
        for i,a  in enumerate  (axis):
            cmds.connectAttr(f'{g_jointA}.rotateX',f'{md}.input2{a}')
            cmds.connectAttr(f'{md}.output{a}',f'{side}_{typ}TwistBind_joint_000{i+2}.rotateX')
        jointA_parent = cmds.listRelatives(jointA,parent=True)[0]
        cmds.parent(ikHandle,jointA_parent)

def create_helper_joints(side='L',part=None):
    if not part:
        cmds.warning('put in part ')
    sels= cmds.ls(selection=True,type='joint')
    for sel in sels:
        cmds.select(sel)
        In = cmds.joint(name=f'{side}_{part}Helper_in_0001')
        Out = cmds.joint(name=f'{side}_{part}Helper_out_0001')
        cmds.makeIdentity(In,t=0,r=1,s=1,apply=True)
        cmds.makeIdentity(Out,t=0,r=1,s=1,apply=True)
        #create sdk grp for the joints
        for jnt  in [In,Out]:
            sdk_grp = cmds.createNode('transform',name=f'sdk_{jnt}')
            cmds.matchTransform(sdk_grp,jnt)
            cmds.parent(jnt,sdk_grp)
            cmds.parent(sdk_grp,sel)        


def distribute_rotation(driver=None):
    ctrls = cmds.ls(selection=True)
    count =len(ctrls)

    for i ,ctrl in enumerate(ctrls):
        i=i+1
        driven = f'driven_{ctrl}'
        weight = (1/count)
        md = cmds.createNode('multiplyDivide',name=ctrl.replace('ctrl','md'))
        for a in ['X','Y','Z']:
            cmds.setAttr(f'{md}.input2{a}',weight)
            cmds.connectAttr(f'{driver}.rotate{a}',f'{md}.input1{a}')
            cmds.connectAttr(f'{md}.output{a}',f'{driven}.rotate{a}')

