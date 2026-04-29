/**
 * PostCSS 配置文件
 * 用于处理 CSS 文件的自动前缀和 Tailwind CSS 编译
 * 路径：project_one/static/postcss.config.js
 */

module.exports = {
  plugins: {
    // Tailwind CSS 插件
    tailwindcss: {},
    // Autoprefixer 插件 - 自动添加浏览器前缀
    autoprefixer: {},
  },
}
