import mathutils

import bpy


SCREENSHOT_DIR = "/Users/zoo/Desktop/数字媒体技术/实验02_三维模型Blender/tiangong/screenshots"


def look_at(obj, target):
    direction = mathutils.Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_object_render_visibility(names, hidden):
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = hidden


def render_camera(camera_name, filename, hide_labels=False):
    scene = bpy.context.scene
    label_names = ["展示说明牌", "标题文字", "国旗贴图_核心舱"]
    set_object_render_visibility(label_names, hide_labels)
    scene.camera = bpy.data.objects[camera_name]
    scene.render.filepath = f"{SCREENSHOT_DIR}/{filename}"
    bpy.ops.render.render(write_still=True)
    set_object_render_visibility(label_names, False)
    print(f"RENDERED {scene.render.filepath}")


def make_checker_camera():
    if "相机03_贴图坐标观察区" in bpy.data.objects:
        return "相机03_贴图坐标观察区"
    camera_data = bpy.data.cameras.new("相机03_贴图坐标观察区")
    camera_data.lens = 58
    cam = bpy.data.objects.new("相机03_贴图坐标观察区", camera_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (-3.6, -0.9, 0.1)
    look_at(cam, (-3.6, 2.0, -1.25))
    return cam.name


def main():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"

    render_camera("相机01_国旗正面", "图1_国旗正面渲染.png", hide_labels=True)
    render_camera("相机02_空间站斜俯视", "图2_整体斜俯视渲染.png", hide_labels=True)
    render_camera(make_checker_camera(), "图5_贴图坐标观察区.png")


if __name__ == "__main__":
    main()
