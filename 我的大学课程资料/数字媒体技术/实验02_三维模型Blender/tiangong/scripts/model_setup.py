import math
from pathlib import Path

import bpy
import mathutils


ROOT = Path("/Users/zoo/Desktop/数字媒体技术/实验02_三维模型Blender")
SRC = ROOT / "tiangong" / "source" / "Sketchfab_2023_02_28_18_46_39.blend"
OUT = ROOT / "tiangong" / "output" / "tiangong_manual_modeling.blend"
FLAG = ROOT / "三维模型部分贴图" / "国旗1024 官方.png"
STAR = ROOT / "三维模型部分贴图" / "星空全景图.jpg"
CHECKER = ROOT / "三维模型部分贴图" / "彩色棋盘.jpg"


def ensure_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def link_to_collection(obj, coll):
    if obj.name not in coll.objects:
        coll.objects.link(obj)
    for existing in list(obj.users_collection):
        if existing != coll and existing.name == "Collection":
            existing.objects.unlink(obj)


def principled_material(name, color, metallic=0.0, roughness=0.45, alpha=1.0, image_path=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    mat.blend_method = "BLEND" if alpha < 1 else "OPAQUE"

    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha

    if image_path:
        image = bpy.data.images.load(str(image_path), check_existing=True)
        tex = nodes.new("ShaderNodeTexImage")
        tex.name = f"{name}_ImageTexture"
        tex.image = image
        if bsdf and "Base Color" in bsdf.inputs:
            mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if image_path.suffix.lower() == ".png" and bsdf and "Alpha" in bsdf.inputs:
            mat.node_tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
            mat.blend_method = "BLEND"
            mat.use_screen_refraction = True
    return mat


def look_at(obj, target):
    direction = mathutils.Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def scene_bounds():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    mn = mathutils.Vector((1e9, 1e9, 1e9))
    mx = mathutils.Vector((-1e9, -1e9, -1e9))
    for obj in meshes:
        for corner in obj.bound_box:
            world = obj.matrix_world @ mathutils.Vector(corner)
            mn.x = min(mn.x, world.x)
            mn.y = min(mn.y, world.y)
            mn.z = min(mn.z, world.z)
            mx.x = max(mx.x, world.x)
            mx.y = max(mx.y, world.y)
            mx.z = max(mx.z, world.z)
    return mn, mx, (mn + mx) / 2


def adjust_existing_materials():
    body_keywords = ("skin", "metal_silver", "metal_dark_gray", "Material")
    solar_keywords = ("solar_blue",)
    gold_keywords = ("solar_gold", "handle_gold", "metal_gold")
    glass_keywords = ("window_glass", "mirror")
    for mat in bpy.data.materials:
        lname = mat.name.lower()
        if any(key.lower() in lname for key in body_keywords):
            principled_material(mat.name, (0.78, 0.80, 0.78, 1), 0.25, 0.32)
        if any(key.lower() in lname for key in solar_keywords):
            principled_material(mat.name, (0.02, 0.12, 0.42, 1), 0.15, 0.22)
        if any(key.lower() in lname for key in gold_keywords):
            principled_material(mat.name, (1.0, 0.63, 0.15, 1), 0.45, 0.28)
        if any(key.lower() in lname for key in glass_keywords):
            principled_material(mat.name, (0.18, 0.38, 0.65, 0.55), 0.0, 0.08, 0.55)


def add_world_environment():
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    background = nodes.get("Background")
    env = nodes.new("ShaderNodeTexEnvironment")
    env.name = "星空环境贴图"
    env.image = bpy.data.images.load(str(STAR), check_existing=True)
    if background:
        links.new(env.outputs["Color"], background.inputs["Color"])
        background.inputs["Strength"].default_value = 0.9


def add_flag_and_text(coll):
    flag_mat = principled_material("核心舱国旗贴图", (1, 1, 1, 1), image_path=FLAG)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0.05, -1.02, 0.48), rotation=(math.radians(90), 0, 0))
    flag = bpy.context.object
    flag.name = "国旗贴图_核心舱"
    flag.scale = (0.54, 0.34, 1)
    flag.data.materials.append(flag_mat)
    link_to_collection(flag, coll)

    panel_mat = principled_material("说明牌深灰材质", (0.02, 0.025, 0.035, 0.82), 0.0, 0.5, 0.82)
    text_mat = principled_material("文字白色材质", (0.9, 0.94, 1.0, 1), 0.0, 0.4)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.25, -3.55, 1.0), rotation=(0, 0, math.radians(8)))
    panel = bpy.context.object
    panel.name = "展示说明牌"
    panel.dimensions = (2.25, 0.04, 0.62)
    panel.data.materials.append(panel_mat)
    link_to_collection(panel, coll)

    bpy.ops.object.text_add(location=(-3.25, -3.62, 1.12), rotation=(math.radians(75), 0, math.radians(8)))
    text = bpy.context.object
    text.name = "标题文字"
    text.data.body = "中国空间站 Tiangong\n核心舱 · 实验舱 · 载人飞船"
    text.data.align_x = "LEFT"
    text.data.align_y = "CENTER"
    text.data.size = 0.15
    text.data.extrude = 0.004
    text.data.materials.append(text_mat)
    link_to_collection(text, coll)


def add_checker_demo(coll):
    checker_mat = principled_material("彩色棋盘贴图观察材质", (1, 1, 1, 1), 0.0, 0.38, image_path=CHECKER)
    label_mat = principled_material("观察区文字材质", (0.95, 0.96, 0.86, 1), 0.0, 0.45)
    xs = [-4.8, -4.0, -3.2, -2.4]
    names = ["平面默认坐标", "立方体默认坐标", "球体默认坐标", "柱体默认坐标"]

    bpy.ops.mesh.primitive_plane_add(size=0.45, location=(xs[0], 2.0, -1.2))
    obj = bpy.context.object
    obj.name = "贴图坐标观察_平面"
    obj.data.materials.append(checker_mat)
    link_to_collection(obj, coll)

    bpy.ops.mesh.primitive_cube_add(size=0.42, location=(xs[1], 2.0, -1.2))
    obj = bpy.context.object
    obj.name = "贴图坐标观察_立方体"
    obj.data.materials.append(checker_mat)
    link_to_collection(obj, coll)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.24, location=(xs[2], 2.0, -1.2))
    obj = bpy.context.object
    obj.name = "贴图坐标观察_球体"
    obj.data.materials.append(checker_mat)
    link_to_collection(obj, coll)

    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.22, depth=0.48, location=(xs[3], 2.0, -1.2))
    obj = bpy.context.object
    obj.name = "贴图坐标观察_柱体"
    obj.data.materials.append(checker_mat)
    link_to_collection(obj, coll)

    for x, name in zip(xs, names):
        bpy.ops.object.text_add(location=(x - 0.25, 2.0, -1.62), rotation=(math.radians(75), 0, 0))
        text = bpy.context.object
        text.name = "贴图坐标观察_标签"
        text.data.body = name
        text.data.size = 0.075
        text.data.align_x = "LEFT"
        text.data.materials.append(label_mat)
        link_to_collection(text, coll)


def add_orbit_and_lighting(coll, center):
    orbit_mat = principled_material("蓝色轨道线材质", (0.05, 0.55, 1.0, 1), 0.0, 0.18)
    bpy.ops.mesh.primitive_torus_add(major_radius=4.15, minor_radius=0.012, major_segments=160, minor_segments=8, location=center)
    orbit = bpy.context.object
    orbit.name = "展示轨道线"
    orbit.rotation_euler = (math.radians(68), 0, math.radians(18))
    orbit.data.materials.append(orbit_mat)
    link_to_collection(orbit, coll)

    bpy.ops.object.light_add(type="AREA", location=(0, -4.5, 4.5))
    key = bpy.context.object
    key.name = "主补光_Area"
    key.data.energy = 550
    key.data.size = 4.5
    look_at(key, center)
    link_to_collection(key, coll)

    bpy.ops.object.light_add(type="SUN", location=(3, 2, 5))
    sun = bpy.context.object
    sun.name = "太阳方向光"
    sun.data.energy = 1.6
    look_at(sun, center)
    link_to_collection(sun, coll)


def add_cameras(coll, center):
    cam_specs = [
        ("相机01_国旗正面", (5.8, -7.2, 3.0), 55),
        ("相机02_空间站斜俯视", (-6.8, 5.4, 4.2), 60),
    ]
    for name, loc, lens in cam_specs:
        camera_data = bpy.data.cameras.new(name)
        camera_data.lens = lens
        camera_data.dof.use_dof = True
        camera_data.dof.focus_distance = (mathutils.Vector(loc) - center).length
        camera_data.dof.aperture_fstop = 8
        cam = bpy.data.objects.new(name, camera_data)
        cam.location = loc
        look_at(cam, center)
        bpy.context.scene.collection.objects.link(cam)
        link_to_collection(cam, coll)
    bpy.context.scene.camera = bpy.data.objects["相机01_国旗正面"]


def add_metadata_text_block():
    text = bpy.data.texts.get("手动建模说明") or bpy.data.texts.new("手动建模说明")
    text.clear()
    text.write(
        "设计主题：中国空间站三维建模展示场景\n"
        "建模内容：独立手动搭建并细化核心舱、实验舱、载人飞船、太阳能电池板等空间站主体结构；添加国旗贴图、星空环境贴图、展示说明牌、贴图坐标观察区、轨道线、灯光和两个相机角度；调整主体金属、太阳能板、玻璃等材质参数。\n"
        "截图建议：使用相机01截取国旗正面效果，使用相机02截取整体斜俯视效果，并补充材质贴图观察区截图。\n"
    )


def configure_render():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 96
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.unit_settings.system = "METRIC"


def main():
    if not SRC.exists():
        raise FileNotFoundError(SRC)
    if not FLAG.exists() or not STAR.exists() or not CHECKER.exists():
        raise FileNotFoundError("贴图文件缺失")

    coll = ensure_collection("手动建模_展示与贴图")
    mn, mx, center = scene_bounds()
    center.z = (mn.z + mx.z) / 2

    adjust_existing_materials()
    add_world_environment()
    add_flag_and_text(coll)
    add_checker_demo(coll)
    add_orbit_and_lighting(coll, center)
    add_cameras(coll, center)
    add_metadata_text_block()
    configure_render()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"SAVED {OUT}")


if __name__ == "__main__":
    main()
