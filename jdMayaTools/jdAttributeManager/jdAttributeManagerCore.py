'''
author: David Jurine
mail: david.jurine@gmail.com
'''

from maya import cmds
# from python import logger

# - Init list of the default attr non modifiable
default_attr = ['visibility', 'translateX', 'translateY', 'translateZ',
                'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY',
                'scaleZ']

def getModifAttr(obj):
    '''
    Function to get all the attributes keyable except the default ones

    :param obj: object
    :type str
    :return list_attr_modif: list of all attributes that can be modified
    :type list
    '''
    # - Get all the attributes
    list_attr = cmds.listAttr(obj, k=True)
    # - Get just the modifiables attr
    list_attr_modif = [attr for attr in list_attr if attr not in default_attr]
    # - Return them
    return list_attr_modif

def copyAttr(source, dest, list_attr, applyChanges=False):
    '''
    Function to copy one attr to an other

    :param source: source object
    :type str
    :param dest: destination object
    :type str
    :param attr: list of attributes to copy
    :type list
    :return: None
    :type None
    '''
    # TODO : Essayer de copier les connections de l'attribute et tester le code

    list_error = []
    for attr in list_attr:
        if not cmds.objExist('{}.{}'.format(source, attr)):
            if attr in getModifAttr(source):
                # - Get short name, long name, type and default value
                attribute_name = '{}.{}'.format(source, attr)
                long_name = cmds.addAttr(attribute_name, q=True, ln=True)
                short_name = cmds.addAttr(attribute_name, q=True, sn=True)
                default_value = cmds.addAttr(attribute_name, q=True, dv=True)
                at_type = cmds.addAttr(attribute_name, q=True, at=True)
                hidden = cmds.addAttr(attribute_name, q=True, h=True)
                keyable = cmds.addAttr(attribute_name, q=True, k=True)
                # - Debug log
                # log.debug(
                #     'Long name : {}, Short name : {}, Default value : {}, Attribute type : {}'.format(long_name, short_name,
                #                                                                                       default_value,
                #                                                                                       at_type))
                # - Add the attr on the dest obj
                cmds.addAttr(dest, ln = long_name, sn=short_name, dv=default_value, at=at_type, h=hidden, k=keyable)
                new_attr = '{}.{}'.format(dest, str(long_name))
                if not at_type == 'typed':
                    if cmds.addAttr(attribute_name, q=True, hnv=True):
                        min_value = cmds.addAttr(attribute_name, q=True, min=True)
                        cmds.addAttr(new_attr, e=True, min=min_value)
                    if cmds.addAttr(attribute_name, q=True, hxv=True):
                        max_value = cmds.addAttr(attribute_name, q=True, max=True)
                        cmds.addAttr(new_attr, e=True, min=max_value)
                if applyChanges:
                    # - If not animated
                    # - TODO: when the attr is animated
                    value = cmds.getAttr(attribute_name)
                    cmds.setAttr(new_attr, value)

        else:
            # - Append list_error with attr that is not on the source object
            list_error.append(attr)
    # if list_error:
    #     # - Warning log to inform the user which attr wasn't copied
    #     log.warning("Cannot find {} on {}. Skipped.".format(', '.join(list_error), obj))
    # else:
    #     # - Info log to inform the user that all the attributes was copied
    #     log.info("Successfull copy of {} on {}".format(', '.join(list_error), obj))

def reOrderAttributes(dict_index):
    '''
    Function to reorder attributes

    :param dict_index: dictionary of all attributes with the index, ex: {1:'squash', 2:'stretch'}
    :type dict
    :return:
    '''
    # TODO: delete attribute, essayer de trouver un systeme plus performant que de tout delete et tout undo
    # TODO: Tester le code
    nbr_index = len(dict_index.keys())
    for i in enumerate(nbr_index):
        attr = dict_index[i]
        # - Delete attribute

        # - Undo
        cmds.undo()

def modifyAttribute(object, attribute, default_value, long_name, short_name, attr_type):
    '''
    Function to modify an attribute

    :param object: object which contain the attribute
    :type str
    :param attribute: attribute to modify
    :type str
    :param default_value: new default value
    :type int or float or bool or string or index
    :param long_name: new long name of the attribute
    :type str
    :param short_name: new short name of the attribute
    :type str
    :param attr_type: new type of the attribute
    :type str
    :return: None
    '''
    # - Tester si l'utilisateur veut changer le type ou pas
    attribute_name = '{}.{}'.format(object, attribute)
    if attr_type == cmds.addAttr(attribute_name, q=True, at=True):
        # - Simply edit the attribute
        cmds.addAttr(attribute_name, e=True, dv=default_value, ln=long_name, sn=short_name)
    else:
        # - Lister les connections de l'attribute
        sources = cmds.listConnections('pSphere1.bla', s=False, d=True, plugs=True, scn=True)
        destinations = cmds.listConnections('pSphere1.bla', s=True, d=False, plugs=True, scn=True)
        # - Delete l'attribute
        cmds.deleteAttr(attribute_name)
        # - Creer le nouveau
        cmds.addAttr(object, dv=default_value, ln=long_name, sn=short_name, at=attr_type)
        # - Reconnecter les connections si connection et si c'est possible
        for destination in destinations: cmds.connectAttr(attribute_name, destination)
        for source in sources: cmds.connectAttr(source, attribute_name)
        # - Info and warning log