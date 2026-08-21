# 序升 · 部署到 Cloudflare Pages（公网 + 手机随时进）

目标：把站点部署成公网 HTTPS，手机任何网络下都能打开，断网也能进（Service Worker 已缓存应用壳）。

## 一、准备 GitHub 仓库
1. 打开 github.com，登录（没有就注册）。
2. 右上角 New repository，名字随便（如 `xusheng-pwa`），**不要**勾任何 README/.gitignore。
3. 创建后，本机在项目目录执行（把 `<用户名>/<仓库>` 换成你自己的）：

```
git remote add origin https://github.com/<用户名>/<仓库>.git
git branch -M main
git push -u origin main
```

## 二、Cloudflare 部署
1. 打开 dash.cloudflare.com，注册/登录（免费）。
2. 左侧 **Workers & Pages** → **Create** → **Pages** → **连接到 Git**。
3. 授权 GitHub，选刚才的仓库。
4. 设置：
   - Framework preset：**None**
   - Build command：**留空**
   - Build output directory：`.`（根目录）
5. 点 **Save and Deploy**，一两分钟后得到 `https://xxx.pages.dev` 域名。

## 三、手机使用
1. iPhone 用 Safari 打开该域名 → 底部分享 → **添加到主屏幕**。
2. 之后即使断网也能开（SW 已缓存）。
3. 安卓用 Chrome 打开 → 菜单 → 安装应用。

## 四、数据（重要）
- 数据存在手机浏览器 localStorage。iOS 会定期清理不常用网站数据，**务必定期备份**。
- 角色页有「导出数据备份 / 导入数据备份」：导出 JSON 存到云盘；换手机或清数据后，导入即可恢复。
- 本版为手动备份（已满足个人使用）。如需自动云同步，以后再接。

## 五、以后更新
改完代码 → `git push` → Cloudflare 自动重新部署（几十秒）。
手机上若没刷新，长按主屏图标删除、重新添加即可拉到最新。

## 备注
- manifest 已补 PNG 图标（iOS 主屏才能正常显示）。
- Sw.js 缓存策略：HTML/CSS/JS 联网优先，图片缓存优先，离线可用。
