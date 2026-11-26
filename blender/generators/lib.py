import bpy, bmesh, math, random
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name, rgb, rough=0.6, metal=0.0, emit=None, es=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = es
    return m
def _fin(o, m, smooth=True, bevel=0.0):
    o.data.materials.append(m)
    if smooth: bpy.ops.object.shade_smooth()
    return o
def sphere(name, loc, sc, m, seg=20, rot=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg//2, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = sc; bpy.ops.object.transform_apply(scale=True, rotation=True)
    return _fin(o, m)
def cone(name, loc, r, h, m, rot=(0,0,0), seg=10, r2=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; bpy.ops.object.transform_apply(rotation=True)
    return _fin(o, m)
def cyl(name, loc, r, h, m, rot=(0,0,0), seg=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; bpy.ops.object.transform_apply(rotation=True)
    return _fin(o, m)
def box(name, loc, sc, m, rot=(0,0,0), bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = sc; bpy.ops.object.transform_apply(scale=True, rotation=True)
    md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    bpy.ops.object.modifier_apply(modifier="b")
    return _fin(o, m)
def mirror_x(objs):
    out = []
    for o in objs:
        c = o.copy(); c.data = o.data.copy(); bpy.context.collection.objects.link(c)
        c.location.x = -o.location.x; c.scale.x = -c.scale.x
        c.rotation_euler.y = -c.rotation_euler.y; c.rotation_euler.z = -c.rotation_euler.z
        out.append(c)
    return out
def eyes(y, z, x, m_white, m_pupil, r=0.09):
    objs = []
    for s in (1, -1):
        objs.append(sphere("eye", (s*x, y, z), (r, r*0.6, r*1.2), m_white))
        objs.append(sphere("pupil", (s*x, y-r*0.45, z), (r*0.5, r*0.3, r*0.7), m_pupil, seg=10))
    return objs
def export(path):
    bpy.ops.object.select_all(action='DESELECT')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    o = bpy.context.active_object; o.name = path.split('/')[-1].replace('.glb','')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_apply=True)
    return len(o.data.polygons)
