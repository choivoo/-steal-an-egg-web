import bpy, os, math, glob
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
for f in sorted(glob.glob(ROOT+"/public/assets/models/*/*.glb")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f)
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    import mathutils
    pts=[o.matrix_world@mathutils.Vector(c) for o in objs for c in o.bound_box]
    mn=mathutils.Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)));mx=mathutils.Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(mn+mx)/2;r=max((mx-mn).length,0.5)
    bpy.ops.object.camera_add(location=(c.x+r*0.9,c.y-r*1.1,c.z+r*0.5))
    cam=bpy.context.active_object;bpy.context.scene.camera=cam
    d=c-cam.location;cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.light_add(type='SUN',location=(3,-3,6));bpy.context.active_object.data.energy=3
    bpy.context.scene.world=bpy.data.worlds.new("w");bpy.context.scene.world.color=(0.35,0.4,0.5)
    s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL'
    s.render.resolution_x=s.render.resolution_y=384
    s.render.filepath=ROOT+"/renders/"+os.path.basename(f).replace(".glb",".png");bpy.ops.render.render(write_still=True)
    print("R",f)
