# 把作品集传到 GitHub（手把手版）

不用记命令，按顺序点就行。**预计 10 分钟。**

---

## 第 0 步：确认账号

如果你还没有 GitHub 账号：

1. 打开 https://github.com
2. 点右上角 **Sign up**
3. 填邮箱、密码、用户名（**用户名会出现在链接里，想好再定**，比如 `keing-z`）
4. 邮箱收验证码，完成验证

> 用户名建议用**英文或拼音**，不要用中文——链接里会带中文，别人点开容易出问题。

---

## 第 1 步：新建仓库

1. 登录后，点右上角的 **`+`** → **New repository**
2. 填写：
   - **Repository name**：`portfolio`
   - **Description**：`Data science & automation projects`
   - **Visibility**：选 **Public** ⚠️（**必须公开**，私有仓库审核员打不开）
3. **不要**勾选 "Add a README file"（我们已经有 README 了）
4. 点绿色按钮 **Create repository**

建好后会跳到一个空仓库页面，先放着别动。

---

## 第 2 步：上传文件（网页拖拽，最简单）

在空仓库页面，找到这一行：

> **`uploading an existing file`**

点它，进入上传页。

### 关键：上传整个文件夹

打开文件资源管理器，进入：

```
D:\money-ai\portfolio
```

**把里面的所有文件和文件夹全选**（Ctrl+A），**拖进网页的上传区域**。

> ⚠️ **不要拖 `portfolio` 文件夹本身**，要打开它，把**里面的内容**拖进去。
> 否则 Github 里会多一层 `portfolio/portfolio/`。

### 浏览器可能提示"文件夹太多"

Chrome 拖文件夹是支持的。如果拖拽失败，改用下面第 2 步备选方案。

### 检查一下上传列表

拖进去后，网页上会列出所有待上传文件，应该能看到：

```
README.md
.gitignore
resume.docx
mushroom-classification/
expense-tracker-miniapp/
web-scraper/
quick-capture-extension/
```

**数量应该在 70 个文件左右。** 如果明显少很多（比如只有几个），说明文件夹没拖全，重来一次。

### 提交

1. 页面底部 **Commit changes** 区域
2. 第一个输入框填：`Initial commit from local`
3. 点绿色按钮 **Commit changes**

等几秒，页面会跳到仓库主页，你能看到 README 被渲染出来了。

---

## 第 2 步·备选：如果拖拽不成功

用 GitHub Desktop（图形客户端，比命令行简单）：

1. 下载：https://desktop.github.com
2. 安装后登录你的 GitHub 账号
3. 菜单 **File → Add local repository**
4. 选择 `D:\money-ai\portfolio` 文件夹
   - 提示"不是 git 仓库"时，点 **create a repository**
5. 然后点右上角 **Publish repository**
6. **取消勾选** "Keep this code private"（要公开）
7. 点 **Publish repository**

这个方式会用上我已经做好的 git 提交记录，效果更好。

---

## 第 3 步：验证链接能打开

打开这个地址（替换你的用户名）：

```
https://github.com/[你的用户名]/portfolio
```

**必须确认这几件事**：

- [ ] 页面能打开，不是 404
- [ ] 首页能看到 README 的内容（有 "Hi, I'm..." 开头）
- [ ] 能看到 4 个文件夹
- [ ] 点进 `mushroom-classification` 能看到 `src`、`data`、`figures`

**全部通过，才算成功。** 有一条不对，先修好再填申请。

---

## 第 4 步：替换个人信息

仓库里还有两处占位符要改：

### ① README 里的

点开 `README.md`，点右上角的**铅笔图标**编辑，改这两处：

- 第一行 `[Your Name]` → 你的名字（拼音或英文名都行）
- 最后的 `@your-handle` 和 `your@email.com`

改完点 **Commit changes**。

### ② 简历里的

`resume.docx` 我生成的版本里也有占位符（`[你的姓名]`、`your@email.com`）。

**推荐做法**：下载下来，用 Word 改完，再重新上传覆盖。

或者告诉我你要填的名字和邮箱，**我重新生成一份给你**，更省事。

---

## 常见问题

**Q：仓库只能是 Public 吗？**
A：是。**Private 仓库审核员点开是 403**，等于没交。

**Q：上传后中文显示乱码？**
A：不会。我写文件时用的都是 UTF-8。

**Q：文件太大传不上去？**
A：最大的是数据集 CSV（1.7MB）和报告（2.9MB），都在 GitHub 限制内。

**Q：以后改了代码怎么更新？**
A：网页上点开对应文件 → 铅笔编辑 → 提交；或者用 GitHub Desktop 同步。

**Q：.gitignore 是干什么的？**
A：告诉 git 哪些文件不要传（比如 `__pycache__`、`node_modules`）。已经写好了，不用管。

---

## 做完之后

回到 TalentsAI，填：

| 项 | 填什么 |
|---|---|
| 过往个人代码仓链接 | `https://github.com/[你的用户名]/portfolio` |
| 个人简历 | 上传改好的 `resume.docx` |
| 个人介绍 | 复制 `TalentsAI-申请材料.md` 里第 ③ 段 |
| 补充说明 | 复制 `TalentsAI-申请材料.md` 里第 ④ 段 |

填完核对一遍，再点「申请项目」。
