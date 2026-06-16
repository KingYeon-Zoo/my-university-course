# Logo 设置说明

## 如何添加你的 Logo

1. **准备logo图片**
   - 将你的logo图片文件命名为 `logo.png`（或其他常见格式如 `.jpg`, `.svg`）
   - 推荐尺寸：40x40px 或更高分辨率的正方形图片
   - 放置到 `src/assets/` 目录下

2. **修改导航栏代码**
   - 打开 `src/components/导航栏.tsx` 文件
   - 找到第5-6行的注释代码：
     ```tsx
     // 导入logo图片 - 请将你的logo文件放到 src/assets/ 目录下并命名为 logo.png
     // import logoImage from "../assets/logo.png";
     ```
   - 取消注释第6行（删除 `//` ）
   - 如果你的logo不是 `logo.png`，请修改路径

3. **启用logo显示**
   - 在同一文件中找到第22-28行：
     ```tsx
     {/* TODO: 取消注释下面这行并注释掉Sparkles图标，将你的logo文件放到 src/assets/logo.png */}
     {/* <img src={logoImage} alt="Logo" className="w-full h-full object-cover rounded-lg" /> */}
     
     {/* 临时占位符 - 有logo后可删除 */}
     <Sparkles className="w-5 h-5 text-white dark:text-black" />
     ```
   - 取消注释第23行（删除 `{/* */}`）
   - 注释掉第26行的 `<Sparkles>` 组件

4. **最终效果**
   - 你的logo将显示在导航栏左侧
   - 自动适配黑白主题
   - 圆角边框，适合品牌展示

## 示例文件结构
```
src/
├── assets/
│   ├── logo.png          # 你的logo文件
│   └── README.md         # 这个说明文件
└── components/
    └── 导航栏.tsx         # 需要修改的文件
```

## 注意事项
- logo图片会自动缩放到40x40px的容器中
- 支持常见的图片格式：PNG, JPG, SVG等
- 如果logo是SVG格式，建议使用专门的SVG导入方式 