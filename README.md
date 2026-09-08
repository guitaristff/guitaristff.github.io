# 杜兆丰 · Zhaofeng Du

个人主页：**[https://guitaristff.github.io/](https://guitaristff.github.io/)** · [English](https://guitaristff.github.io/?lang=en)

仿照 [Meng Xu 的学术主页](https://mengxu95.github.io/) 的信息结构制作：顶部导航、左侧个人资料、中间学术内容、右侧兴趣互动。纯静态 HTML/CSS/JavaScript，默认中文，可切换英文并记住选择。全站采用中性暖白 `#EFEEE9`、暖灰卡片 `#E7E6E1`、炭黑文字 `#20211F`、冷铝灰 `#A9ABAA` 和钢蓝 `#315B78`；旧金色 `#9B865F` 点缀少量标签、年份与焦点边框。骑行卡片及其收起按钮单独保留原配色。

## 本地预览

```powershell
python scripts/serve.py
```

访问 <http://localhost:4173>。也可以直接打开 `index.html`。服务仅监听本机，只提供 `_site/` 中的网站文件。

## 内容

- 个人简介：GitHub 骑行头像、目标状态估计与目标跟踪等研究兴趣、单位、导师及联系方式。博士生导师陈晨教授（国家优青），硕士生导师辛斌教授（国家杰青）。
- 实验室：自主智能无人系统全国重点实验室（State Key Lab of Autonomous Intelligent Unmanned Systems），在中英文简介中注明成员身份。
- 研究：仅 FBSR、RAFT 两项，各保留一句简介与一张项目原图；FBSR 展示无人机传感器与目标跟踪场景，RAFT 使用论文 Fig. 1，展示相对位姿参考的放松与恢复。点击图片可查看完整原图；FBSR 链接到公开数据集。
- 实物平台：从原 CV 中提取的三张真实无人机照片，可放大、前后切换，并支持键盘方向键。
- 教育、荣誉：依据 CV 整理，未添加未经确认的论文或成果。
- 骑行：BMW R nineT 原创矢量插画；骑行区保留绿山、暖阳配色，支持追踪、协同、暂停，没有遮挡选项，页面不显示车型名称和动画说明句。
- 音乐：黑色播放按钮直接在页面内播放网易云《四相》（约 5 分 9 秒），支持暂停和进度控制；封面和歌曲页面链接可前往网易云。歌曲通过网易云公开外链地址串流播放，不将录音文件打包到网站。
- 手机浮窗：首次打开即在底部并排展示完整骑行动画与《四相》播放器，动画直接运行，音乐按钮点击一次即可播放。两个窗口可独立收起、恢复，同一标签页记住各自状态；收起音乐窗口不打断播放。正文仍可滚动，底部预留浮窗高度。桌面端继续使用原侧栏，关闭 JavaScript 时保留原页面布局。
- 联系邮箱：`zhaofeng_du@bit.edu.cn`。
- ORCID：`0009-0005-8216-6980`，位于左侧联系方式与简介链接区，指向无需登录的公开主页。
- 没有简历下载按钮、CV 导航或公开简历页面。

页面中的照片和封面均保存在本地。点击播放时从 `https://music.163.com/song/media/outer/url?id=439121264.mp3` 加载音频；使用稳定的网易云外链入口，不保存会变化的 CDN 跳转地址。页面设置 `upgrade-insecure-requests`，将可能返回的 HTTP 音频跳转升级到 HTTPS，兼容 HTTPS 部署。播放器提供 12 秒加载超时、取消加载及失败后的重新加载，并区分网络、音源、解码和浏览器权限问题。错误提示随语言切换；主动暂停、取消或切换页面不显示播放失败。外部音源不可用时可通过网易云歌曲页面收听。

## 修改内容

| 文件 | 内容 |
| --- | --- |
| `index.html` | 页面布局、中英文文字、研究概览、平台展示与兴趣内容 |
| `styles.css` | 三栏布局、响应式样式与视觉效果 |
| `app.js` | 语言切换、平台图库、动画、音乐播放器、邮箱复制 |
| `assets/bmw-r-ninet.svg` | BMW R nineT 原创侧面插画 |
| `assets/uav-platform-01.png` ～ `03.png` | 三张实物平台照片 |
| `assets/sixiang-cover.jpg` | 《今日青年》专辑封面 |
| `assets/fbsr-scene.png`、`assets/raft-fig1.png` | 项目原图的完整渲染，用作研究缩略图 |
| `scripts/build.py` | 发布文件白名单与压缩打包 |

中文正文保存在 HTML 元素中，英文位于同一元素的 `data-en` 属性。研究部分不包含详情弹窗。RAFT 暂未添加未经提供或核实的外部地址。

## 发布包

```powershell
python scripts/build.py
```

生成 `_site/` 与 `zhaofeng-du-website.zip`，仅包含 13 个公开网页及资源文件。原始 CV 和开发检查文件不在发布包中。

源码仓库：[guitaristff/guitaristff.github.io](https://github.com/guitaristff/guitaristff.github.io)。GitHub Pages 使用 **GitHub Actions** 作为发布来源，配置在 `.github/workflows/pages.yml`。每次向 `main` 分支推送后，自动运行 `scripts/build.py`，仅上传 `_site/` 中的公开文件并部署主页；原始 CV、开发工具、检查截图和本地压缩包均通过 `.gitignore` 排除。

更新网页后，先本地预览，再提交并推送：

```powershell
python scripts/build.py
git add index.html styles.css app.js assets
git commit -m "Update personal homepage"
git push
```

部署进度见仓库的 [Actions 页面](https://github.com/guitaristff/guitaristff.github.io/actions)。工作流采用 [GitHub Pages 官方部署方式](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

## 浏览器检查

运行网站本身不需要 Python 扩展包。自动浏览器检查使用本机 Chrome 与 Playwright：

```powershell
python -m pip install --target .tools playwright
python scripts/build.py
python scripts/preview_check.py
python scripts/mobile_check.py
```

检查语言与偏好记忆、FBSR/RAFT 范围、邮箱复制、平台图片及放大切换、BMW 插画和两种动画模式、实际音频播放与进度、手机导航、减少动态效果、320–1440 像素布局、无公开 CV。截图和结果写入 `.preview/`。

播放器额外检查：网易云实际播放与约 309 秒时长、中断外部音源后的错误提示与真实重试播放、持续加载时取消、加载超时，以及浏览器拒绝播放时的提示。另在 HTTPS 页面环境检查真实播放和 CDN 跳转升级。

原 PDF 平台图片的提取步骤在 `scripts/extract_platforms.py`：使用 `pdfimages -j` 提取图片与透明遮罩后，按原 PDF 的遮罩还原，不生成或修改设备细节。仅重新提取时需要 Pillow；日常运行不需要。

## 素材与来源

- 布局参考：[Meng Xu](https://mengxu95.github.io/)，本站代码与插画独立实现。
- 头像：[GitHub @guitaristff](https://github.com/guitaristff)。
- 平台照片：用户提供 CV 中“自建平台”一栏，保留原图范围和透明遮罩；人物头像仍使用 GitHub 头像。
- FBSR：[公开测量数据集](https://github.com/guitaristff/fbsr_measurement_dataset)。
- FBSR 配图：本地 `../fbsr_tim_package_lidar_rgb/paper/figs/fig1_scenario.pdf`；RAFT 配图：论文 Fig. 1 对应的 `../RAFT/fig/overall_architecture.pdf`。均完整渲染为 PNG，保留图中标注及内容，未裁剪或生成研究结果。
- ORCID：[0009-0005-8216-6980](https://orcid.org/0009-0005-8216-6980)，由本人提供。
- BMW R nineT 插画参考 [BMW 官方车型介绍](https://www.press.bmwgroup.com/usa/article/detail/T0150745EN_US/the-new-bmw-r-ninet) 的拳击手发动机、圆灯、金色倒立前叉、辐条轮与双排气特征；页面动画仅为概念示意。
- 《四相》：[网易云音乐歌曲页面](https://music.163.com/song?id=439121264)，歌曲编号、歌手及专辑已通过网易云公开元数据核对；音频与封面均使用网易云公开来源。
