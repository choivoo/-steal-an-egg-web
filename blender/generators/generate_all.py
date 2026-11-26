import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
import lib
from lib import *
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "public/assets/models")
stats = {}

def pet_moss_fox():
    reset()
    fur = mat("fur", (0.85,0.45,0.15), 0.9); cream = mat("cream",(0.96,0.9,0.75),0.9)
    moss = mat("moss",(0.2,0.6,0.25),0.95); dark = mat("dark",(0.05,0.04,0.04),0.4); wh = mat("wh",(1,1,1),0.3)
    sphere("body",(0,0,0.55),(0.38,0.6,0.36),fur)
    sphere("belly",(0,-0.05,0.45),(0.3,0.5,0.28),cream)
    sphere("head",(0,0.62,0.8),(0.34,0.3,0.3),fur)
    sphere("snout",(0,0.9,0.72),(0.15,0.2,0.12),cream)
    sphere("nose",(0,1.08,0.76),(0.05,0.04,0.04),dark,seg=8)
    ears=[cone("ear",(0.2,0.55,1.15),0.12,0.4,fur,rot=(math.radians(-10),0,math.radians(-15)),seg=6)]
    ears+=[cone("earin",(0.2,0.58,1.12),0.06,0.3,cream,rot=(math.radians(-10),0,math.radians(-15)),seg=6)]
    mirror_x(ears)
    eyes(0.86,0.88,0.14,wh,dark)
    legs=[cyl("leg",(0.2,0.3,0.2),0.08,0.4,fur),cyl("leg",(0.2,-0.35,0.2),0.08,0.4,fur)]
    mirror_x(legs)
    # big fluffy tail with moss tuft
    sphere("tail",(0,-0.85,0.7),(0.22,0.5,0.22),fur,rot=(math.radians(-35),0,0))
    sphere("tailtip",(0,-1.2,0.95),(0.16,0.2,0.16),cream)
    # moss patches + mushrooms on back
    for i,(x,y) in enumerate([(0.12,0.1),(-0.14,-0.2),(0.05,-0.45)]):
        sphere("moss",(x,y,0.88),(0.14,0.14,0.07),moss)
    for (x,y,h) in [(0.1,0.1,0.18),(-0.12,-0.25,0.12)]:
        cyl("stem",(x,y,0.95+h/2),0.03,h,cream,seg=8)
        sphere("cap",(x,y,0.95+h),(0.09,0.09,0.05),mat("cap",(0.85,0.2,0.2),0.5))
    return "pets/moss_fox.glb"

def pet_ember_drake():
    reset()
    sc=mat("scale",(0.8,0.15,0.1),0.45); bel=mat("bel",(1,0.7,0.3),0.6); horn=mat("horn",(0.95,0.9,0.8),0.4)
    glow=mat("glow",(1,0.4,0.05),0.3,emit=(1,0.4,0.05),es=4); wing=mat("wing",(0.55,0.08,0.1),0.7)
    dark=mat("dark",(0.03,0.02,0.02),0.4); gold=mat("gold",(0.1,0.8,0.9),0.2,emit=(0.2,0.9,1),es=2)
    sphere("body",(0,0,0.7),(0.4,0.65,0.4),sc)
    sphere("belly",(0,0.02,0.6),(0.3,0.55,0.3),bel)
    # neck + head
    sphere("neck",(0,0.6,1.0),(0.17,0.22,0.3),sc,rot=(math.radians(25),0,0))
    sphere("head",(0,0.8,1.3),(0.25,0.33,0.2),sc)
    sphere("jaw",(0,0.95,1.2),(0.18,0.25,0.07),bel)
    hs=[cone("horn",(0.12,0.72,1.5),0.05,0.4,horn,rot=(math.radians(-30),0,math.radians(-12)),seg=6)]
    hs+=[cone("horn2",(0.2,0.7,1.35),0.04,0.3,horn,rot=(math.radians(-45),0,math.radians(-40)),seg=6)]
    mirror_x(hs)
    eyes(1.07,1.36,0.12,glow,dark,r=0.07)
    # spine ridge flames
    for i in range(6):
        y=0.5-i*0.22; cone("spike",(0,y,1.12-i*0.05),0.07,0.28-i*0.025,glow,seg=5)
    # tail segments
    for i in range(6):
        r=0.2-i*0.028; sphere("tail",(0,-0.7-i*0.28,0.6-i*0.02),(r,0.22,r),sc)
    cone("tailflame",(0,-2.55,0.55),0.13,0.5,glow,rot=(math.radians(-90),0,0),seg=6)
    # legs with claws
    ls=[sphere("thigh",(0.3,0.3,0.4),(0.15,0.2,0.28),sc),sphere("thigh",(0.3,-0.35,0.4),(0.15,0.2,0.28),sc)]
    ls+=[cone("claw",(0.3,0.45,0.04),0.08,0.15,horn,rot=(math.radians(90),0,0),seg=5),cone("claw",(0.3,-0.2,0.04),0.08,0.15,horn,rot=(math.radians(90),0,0),seg=5)]
    mirror_x(ls)
    # wings: membranes via flattened cones + bone arms
    bone=sc
    for s in (1,-1):
        cyl("wbone",(s*0.55,-0.05,1.2),0.04,0.9,bone,rot=(0,math.radians(s*-60),0))
        for k,(dx,dy,dz,rz) in enumerate([(0.8,0.0,1.55,0),(1.0,-0.3,1.3,0.3),(0.95,-0.55,1.0,0.6)]):
            box("mem",(s*dx,dy-0.1,dz-0.1),(0.45,0.015,0.28),wing,rot=(0,math.radians(s*-20),math.radians(s*(20+k*25))),bevel=0.005)
    return "pets/ember_drake.glb"

def pet_aqua_slime():
    reset()
    jelly=mat("jelly",(0.2,0.7,1.0),0.1); jelly.blend_method='BLEND'
    b=jelly.node_tree.nodes["Principled BSDF"]; b.inputs["Alpha"].default_value=0.75
    core=mat("core",(0.6,1,1),0.2,emit=(0.4,1,1),es=3); wh=mat("wh",(1,1,1),0.2); dark=mat("dark",(0.02,0.05,0.1),0.3)
    cr=mat("crystal",(0.5,0.9,1),0.05,0.2,emit=(0.3,0.8,1),es=1.5); blush=mat("bl",(1,0.5,0.6),0.8)
    sphere("body",(0,0,0.5),(0.55,0.55,0.5),jelly,seg=28)
    sphere("blob",(0.45,0.05,0.2),(0.22,0.22,0.2),jelly); sphere("blob",(-0.45,0.1,0.2),(0.2,0.2,0.18),jelly)
    sphere("core",(0,-0.05,0.5),(0.2,0.2,0.2),core)
    eyes(0.5,0.6,0.2,wh,dark,r=0.12)
    for s in (1,-1): sphere("blush",(s*0.33,0.48,0.45),(0.07,0.03,0.05),blush,seg=8)
    sphere("mouth",(0,0.53,0.42),(0.06,0.03,0.025),dark,seg=8)
    for (x,y,h,rx,rz) in [(0,-0.1,0.45,0,0),(0.2,-0.05,0.3,0.2,-0.4),(-0.2,-0.05,0.3,0.2,0.4)]:
        cone("crystal",(x,y,0.95+h*0.3),0.07,h,cr,rot=(rx,0,rz),seg=6,r2=0.0)
    return "pets/aqua_slime.glb"

def egg(name, base, accent, kind):
    reset()
    shell=mat("shell",base,0.4); acc=mat("acc",accent,0.35,emit=accent,es=0.6)
    sphere("egg",(0,0,0.5),(0.38,0.38,0.5),shell,seg=32)
    if kind=="forest":
        for i in range(5):
            a=i*math.tau/5; cone("leaf",(0.3*math.cos(a),0.3*math.sin(a),0.35+i*0.08),0.07,0.25,acc,rot=(math.sin(a)*0.8,-math.cos(a)*0.8,0),seg=4)
        sphere("moss",(0,0,0.97),(0.2,0.2,0.07),acc)
    elif kind=="lake":
        for i in range(6):
            a=i*math.tau/6; cone("cryst",(0.36*math.cos(a),0.36*math.sin(a),0.3+(i%2)*0.2),0.06,0.3,acc,rot=(math.sin(a)*1.0,-math.cos(a)*1.0,0),seg=5)
        for z in (0.3,0.55): cyl("ring",(0,0,z),0.37-abs(z-0.5)*0.2,0.03,acc,seg=24)
    else:  # volcano
        for i in range(4):
            a=i*math.tau/4+0.4; box("rock",(0.34*math.cos(a),0.34*math.sin(a),0.25+i*0.15),(0.1,0.1,0.14),mat("rock",(0.12,0.08,0.07),0.9),rot=(a,0.5,a))
        for i in range(5):
            a=i*1.3; box("crack",(0.37*math.cos(a),0.37*math.sin(a),0.2+i*0.17),(0.015,0.015,0.12),acc,rot=(0,0,a),bevel=0.002)
    return f"eggs/{name}.glb"

def guardian_ironbeak():
    reset()
    ir=mat("iron",(0.35,0.4,0.42),0.35,0.8); bark=mat("bark",(0.3,0.2,0.1),0.9); leaf=mat("leaf",(0.15,0.5,0.15),0.8)
    beak=mat("beak",(0.8,0.65,0.15),0.3,0.9); glow=mat("glow",(1,0.15,0.1),0.3,emit=(1,0.1,0.05),es=6); dark=mat("dark",(0.03,0.03,0.03),0.5)
    S=2.2
    sphere("body",(0,0,2.2*S/2),(0.9,1.3,0.95),bark,seg=24).scale=(1,1,1)
    sphere("chest",(0,0.6,2.3),(0.7,0.6,0.7),ir)
    # armor plates on back
    for i in range(5): box("plate",(0,-0.2-i*0.3,3.1-i*0.15),(0.55-i*0.05,0.14,0.08),ir,rot=(math.radians(-20),0,0))
    # neck, head with beak
    sphere("neck",(0,1.2,3.0),(0.35,0.5,0.5),bark,rot=(math.radians(-30),0,0))
    sphere("head",(0,1.7,3.5),(0.55,0.6,0.55),ir)
    cone("beakU",(0,2.4,3.4),0.38,1.0,beak,rot=(math.radians(-90),0,0),seg=8)
    cone("beakL",(0,2.2,3.15),0.28,0.7,beak,rot=(math.radians(-90),0,0),seg=8)
    for s in (1,-1):
        sphere("eye",(s*0.3,2.0,3.7),(0.12,0.08,0.12),glow)
        cone("crest",(s*0.35,1.6,4.1),0.1,0.8,leaf,rot=(0,math.radians(s*20),0),seg=5)
    cone("crest",(0,1.5,4.3),0.12,1.0,leaf,seg=5)
    # wings: spread iron feathers
    for s in (1,-1):
        for k in range(6):
            box("feather",(s*(1.2+k*0.45),-0.3-k*0.12,2.9+k*0.1),(0.2,0.9,0.05),ir if k%2 else bark,rot=(0,math.radians(s*(-10-k*8)),math.radians(s*(25+k*5))),bevel=0.01)
    # legs with talons
    for s in (1,-1):
        cyl("leg",(s*0.55,0.2,0.9),0.22,1.8,bark,seg=10)
        for t in (-1,0,1): cone("talon",(s*0.55+t*0.2,0.65,0.1),0.1,0.5,beak,rot=(math.radians(90),0,0),seg=5)
    # tail feathers w/ glow tips
    for k in range(5):
        a=(k-2)*0.25; box("tail",(math.sin(a)*1.0,-1.8,2.6+abs(k-2)*-0.1),(0.12,0.9,0.04),bark,rot=(0,0,-a),bevel=0.005)
        sphere("tip",(math.sin(a)*1.3,-2.6,2.55),(0.1,0.1,0.1),glow,seg=8)
    return "guardians/ironbeak.glb"

jobs=[pet_moss_fox,pet_ember_drake,pet_aqua_slime,
 lambda: egg("forest_egg",(0.78,0.72,0.5),(0.2,0.75,0.25),"forest"),
 lambda: egg("lake_egg",(0.7,0.85,0.95),(0.3,0.8,1.0),"lake"),
 lambda: egg("volcano_egg",(0.25,0.1,0.08),(1.0,0.35,0.05),"volcano"),
 guardian_ironbeak]
manifest=[]
for j in jobs:
    rel=j(); path=os.path.join(OUT,rel); os.makedirs(os.path.dirname(path),exist_ok=True)
    tris=export(path)
    manifest.append({"path":"assets/models/"+rel,"polys":tris,"bytes":os.path.getsize(path)})
    print("OK",rel,tris,os.path.getsize(path))
os.makedirs(os.path.join(ROOT,"public/assets/manifests"),exist_ok=True)
json.dump(manifest,open(os.path.join(ROOT,"public/assets/manifests/models.json"),"w"),indent=1)
