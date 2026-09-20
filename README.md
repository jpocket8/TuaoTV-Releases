# 土澳TV 下载

[官网下载](https://tuaotv.com/#download) · [全部安装包](https://github.com/jpocket8/TuaoTV-Releases/releases/latest)

这里仅发布 Android 手机、电视、Windows 和 Mac 安装包，点击安装包后由浏览器管理下载。

Windows 请下载 `.exe` 安装程序；Mac 按芯片类型选择 ZIP。Android 手机选择 `mobile`，电视与电视盒选择 `tv`。

每个版本附带 `SHA256SUMS.txt` 校验文件。GitHub 自动生成的 Source code 文件不是应用安装包。

## 电视模拟器发布端

`tuaotv-tv-<版本>.apk` 同时用于电视盒和本机 Android 电视模拟器，包名为 `com.zhuiju.app.tv.dev`。它不是单独的桌面应用；安装 APK 不会默认开启持续更新。

开发电脑通过 `TUAOTV_CATALOGUE_PUBLISHER=1` 启动专用电视模拟器维护脚本后，会在首页显示“持续更新已开启”，持续更新公共节目列表，并在维护时自动升级和重启发布端。直接打开的 Mac 桌面版不会自动继承这个启动环境变量。

[项目源码与启动说明](https://github.com/jpocket8/ZhuijuUnified#本机电视模拟器发布端持续更新)。`catalogue-<时间戳>` Release 是独立节目列表数据；最新正式 Release 提供 App 安装包。
