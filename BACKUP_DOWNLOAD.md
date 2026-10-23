# 整个项目备份下载（2026-10-23）

本备份包含当前项目的全部工作文件：视频、图片、源码、文档、云端未推送工程和教学设计草稿、隐藏的制作中间文件，以及当前环境可取得的上传附件和生成图片。Git LFS 文件已补齐为真实文件。主分支没有因本备份而修改。

不包含 `.git` 内部数据库、历史版本及先前已按要求删除的错误融入版。教学设计草稿仍是草稿。本备份不是可直接运行的完整软件环境。

## 保存到 F 盘

1. 下载本目录的 `Windows_Download_Helper.zip`（文件页右上角 **Download raw file**，不要右键保存网页），解压。
2. 双击 `Start_Download_to_F.cmd`。它会下载、校验分包，并解压到 `F:\GUGUGAGA_Backup_20261023`。
3. F 盘请至少留出 14 GB。下载失败可再次运行；只有显示绿色 `DONE` 才表示完成。脚本需要 Windows PowerShell 和系统自带 curl。

脚本只会在上述备份目录写入及解压文件。若该目录已有同名备份文件，会以本次备份覆盖。脚本不会删除下载的压缩包。

若脚本下载被网络或私有仓库权限阻止：登录 GitHub 后，打开下面各分包的链接，点击 **Download raw file**，全部保存到同一个文件夹；把各个 ZIP 全部解压到同一个 F 盘目录。每个 ZIP 都能独立解压，无需合并压缩包。

文件目录：`GUGUGAGA` 为项目，`附件原件` 为当前环境中取得的用户附件，`生成图片原件` 为当前环境中保留的生成图片。云端之外未能取得的历史聊天附件不在本备份内。

`packages/manifest.json` 记录全部文件名、大小和 SHA256。分包只供下载，不要用 GitHub 的 **Download ZIP** 替代，后者可能包含 LFS 指针。

## 手动下载分包


备份共 **2771 个文件**，原文件合计 **6.22 GB**；**16 个独立 ZIP** 合计 **5.99 GB**。

- [GUGUGAGA_part_01.zip](packages/GUGUGAGA_part_01.zip)：452.1 MB
- [GUGUGAGA_part_02.zip](packages/GUGUGAGA_part_02.zip)：299.7 MB
- [GUGUGAGA_part_03.zip](packages/GUGUGAGA_part_03.zip)：462.0 MB
- [GUGUGAGA_part_04.zip](packages/GUGUGAGA_part_04.zip)：207.3 MB
- [GUGUGAGA_part_05.zip](packages/GUGUGAGA_part_05.zip)：416.5 MB
- [GUGUGAGA_part_06.zip](packages/GUGUGAGA_part_06.zip)：426.7 MB
- [GUGUGAGA_part_07.zip](packages/GUGUGAGA_part_07.zip)：445.6 MB
- [GUGUGAGA_part_08.zip](packages/GUGUGAGA_part_08.zip)：446.1 MB
- [GUGUGAGA_part_09.zip](packages/GUGUGAGA_part_09.zip)：346.1 MB
- [GUGUGAGA_part_10.zip](packages/GUGUGAGA_part_10.zip)：453.4 MB
- [GUGUGAGA_part_11.zip](packages/GUGUGAGA_part_11.zip)：286.4 MB
- [GUGUGAGA_part_12.zip](packages/GUGUGAGA_part_12.zip)：258.4 MB
- [GUGUGAGA_part_13.zip](packages/GUGUGAGA_part_13.zip)：256.7 MB
- [GUGUGAGA_part_14.zip](packages/GUGUGAGA_part_14.zip)：367.2 MB
- [GUGUGAGA_part_15.zip](packages/GUGUGAGA_part_15.zip)：440.7 MB
- [GUGUGAGA_part_16.zip](packages/GUGUGAGA_part_16.zip)：424.3 MB
