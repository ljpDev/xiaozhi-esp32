# 自定义 240×240 桌宠表情

21 张 PNG 来自用户目录 `AIws/user/esp32/noto-color-emoji_240`，原样复制到 `images/`。后续在本工程的 `images/` 修改图片，外部原目录不再作为构建输入。

## 重新打包和编译

在项目根目录的 VS Code 终端运行：

```sh
source /Users/liangjiaping/.espressif/tools/activate_idf_v6.1.sh
python3 scripts/build_pet240.py
```

仅打包 UI 资源：`python3 scripts/build_pet240.py --pack-only`。

脚本调用项目的 `build_default_assets.py`，打包本目录图片和依赖组件中的中文字库，生成本目录 `assets.bin`。随后调用标准 `scripts/build.py` 构建 `atk-dnesp32s3-pet240` 版本；CMake 根据当前配置加入语音模型、校验分区大小，再生成可烧录固件。不修改 `managed_components`。

默认界面、中文、Flash Custom Assets 配置由板型 `config.json` 中的 `atk-dnesp32s3-pet240` 版本保存。`Custom Assets File` 为 `../custom_assets/pet240/assets.bin`；当前 CMake 实际相对于 `main/` 解析此路径，因此带有 `../`。

修改 `images/` 后必须先重新运行本脚本打包，再构建/烧录。只点击 VS Code 构建按钮不会重新读取原始 PNG 来更新自定义包。首次从全新克隆构建时需要先获取项目依赖，特别是 `78/xiaozhi-fonts`。

## 产物与烧录

- `custom_assets/pet240/assets.bin`：图片和中文字库的基础包。
- `build/configured_assets.bin`：加入当前语音模型后的实际烧录资源。
- `build/merged-binary.bin`：完整合并固件，写入地址 `0x0`。
- `releases/v2.5.3_alientek-atk-dnesp32s3-pet240.zip`：本次发布包；版本号随项目变化。

构建成功后，烧录当前工程可执行：

```sh
python3 "$IDF_PATH/tools/idf.py" -p /dev/cu.实际串口 flash
```

完整 `flash` 包含资源分区；`app-flash` 不更新图片。不要把单独的 `assets.bin` 写到 `0x0`。不必额外整片擦除 Flash。

新增版本使用独立 OTA 板型标识，需关注后续 OTA 服务对该名称的支持，自动更新也可能覆盖定制主题。

## 本次验证（2026-11-04）

- ESP-IDF v6.1，目标 ESP32-S3，板型 `atk-dnesp32s3-pet240`。
- 21 张图片全部为 240×240，保持原始 PNG 和透明度，没有缩放。
- 最终包内所有图片与工程源文件逐字节一致，包含中文字库与 `srmodels.bin`。
- `configured_assets.bin` 为 3,085,557 字节，小于 8MiB 分区。
- 合并固件 `0x800000` 处的数据与最终资源包一致。
- 详细校验值见 `verification.json`。
- 未烧录验证；240px 表情在 320×240 屏幕上占满高度，与状态栏及聊天文字的实际遮挡情况需上板观察。本次沿用原有布局。

`assets.bin` 属于生成文件，被项目 `.gitignore` 忽略；应保留图片、打包脚本和版本配置，以便重建。
