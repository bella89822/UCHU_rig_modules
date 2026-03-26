import maya.cmds as cmds


def rename_controller_shape():
    controllers=cmds.ls(selection=True, type='transform')
    
    for ctrl in controllers:
        shapes= cmds.listRelatives(ctrl,shapes=True,fullPath=False)or[]
        
        for shape in shapes:
            if cmds.objectType(shape)== 'nurbsCurve':
                new_shape_name=f'{ctrl}Shape'
                
                if shape!=new_shape_name:
                    try:
                        cmds.rename(shape,new_shape_name)
                        print(f'Renamed{shape}>>{new_shape_name}')
                    except Exception as e:
                        print(f'Failed to rename{shape}:{e}')

import maya.cmds as cmds
def rename_items(name):
    items=cmds.ls(selection=True)
    for i, item in enumerate(items) :
        i=i+1
        cmds.rename(item,f'{name}_{i:04}')

def rename_to_alphabetical():
    item_list = cmds.ls(selection = True)

    mapping = {str(i+1).zfill(4): chr(65+i) for i in range(26)}
    # {'0001':'A', '0002':'B', ...}

    

    for item in item_list:
        parts = item.split('_')
        number = parts[-1]  # 0001
        
        letter = mapping.get(number, "")
        
        new_name = item.replace(f"_{number}", '')
        new_name = f'{parts[0]}_{parts[1]}{letter}_{parts[2]}'
        cmds.rename(item, new_name)
