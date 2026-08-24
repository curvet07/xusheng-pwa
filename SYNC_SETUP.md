# 序升 · 云同步部署指南

数据之前只存在本地浏览器（localStorage），所以手机桌面快捷方式（PWA）和手机浏览器是两套独立存储，互不同步。
现在加了云端同步层：**Cloudflare Pages Functions + KV**，挂在现有 `xusheng-pwa.pages.dev` 同域（`/api/state`），免 CORS、随 git push 一起部署。

## 原理
- 你在「角色」页设一个**同步码**（任意字符串，自己记住）。
- 本地任何改动（增/删/改任务、打卡、记录进度）会在 0.8 秒后自动 `PUT` 到云端（按同步码隔离）。
- 打开 app 时自动从云端 `GET` 最新数据覆盖本地。
- localStorage 继续作为离线兜底，断网照常使用，联网自动补推。
- **多端、多入口（PWA / 浏览器）只要输入同一个同步码，数据就实时一致。**

## 部署步骤（只需做一次）

### 1. 创建 KV 命名空间
- 登录 Cloudflare 控制台 → 左侧「Workers 和 KV」→「KV」→「创建命名空间」。
- 名称随便填，例如 `xusheng-sync`。记下它。

### 2. 把 KV 绑定到 Pages 项目
- 控制台 → 你的 `xusheng-pwa` Pages 项目 →「设置」→「Functions」→「KV 绑定（或 Runtime 绑定）」。
- 变量名必须填：**`XUSHENG_KV`**（代码里写死了这个名字）。
- 命名空间选第 1 步建的那个。

### 3. 部署代码
仓库里已新增 `functions/api/state.js`，并改了 `app.js` / `index.html` / `sw.js` / `refinements.css`。
在本地项目目录执行：
```bash
git add .
git commit -m "feat: add cloud sync via Pages Functions + KV"
git push
```
git push 后 Pages 会自动构建并启用 `/api/state` 接口（无需 wrangler）。

## 验证是否成功
部署完成后，终端执行：
```bash
curl https://xusheng-pwa.pages.dev/api/state?code=test
```
- 返回 `{"state":null,"savedAt":0}` → 接口正常（code=test 还没数据，符合预期）。
- 若返回 `{"error":"missing code"}` 或 500 → 检查 KV 绑定变量名是否为 `XUSHENG_KV`。

## 使用
1. 打开 app（任意入口）→「角色」页最下方「云同步」框。
2. 输入一个只有你知道的同步码（例如 `zejing-2026`），点「启用同步」。
   - 首次启用会把你**当前这台设备**的本地数据推到云端，成为基准。
3. 在手机 PWA、手机浏览器、电脑浏览器等任何入口，输入**同一个同步码**启用。
4. 之后在任意一处增删改，其他处打开/刷新即自动同步。

## 注意事项
- 同步码就是你的「密码」：知道码的人能读/改你的数据。个人工具够用，别用真密码。
- 冲突策略为「后写覆盖（last-write-wins）」：两个设备**同时离线改、再联网**，较晚同步的那次会覆盖较早的。正常使用（一个设备改完再开另一个）不受影响。
- 想换同步码或停用：点「断开」，再输新码启用即可。
- 云端是权威副本；本地删除/重置也会同步到云端（重置 = 清空云端该码数据）。
