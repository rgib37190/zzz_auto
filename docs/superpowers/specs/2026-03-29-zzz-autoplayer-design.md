# ZZZ AutoPlayer — 絕區零自動化腳本設計規格

## 概述

一個基於 Python 的絕區零（Zenless Zone Zero）自動化腳本，支援日常任務全自動、智能反應式戰鬥、全副本自動刷本。透過 OCR + 模板比對的混合視覺辨識引擎實現高韌性的畫面辨識，對遊戲更新有良好的容忍度。

## 目標平台與環境

- **遊戲平台**：Windows PC 版
- **解析度**：1920x1080
- **語言**：繁體中文
- **開發環境**：Ubuntu
- **目標環境**：Windows（打包為 .exe）
- **運行模式**：專用模式（腳本運行時獨佔電腦）

## 整體架構

```
┌─────────────────────────────────────┐
│              GUI (PyQt6)            │
│  任務選擇 / 狀態顯示 / 開始停止     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Task Scheduler              │
│  排程引擎：依序執行選中的任務        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Task Modules                │
│  daily/ combat/ dungeon/            │
│  各模組獨立，實作各自的自動化邏輯     │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────────┐
│  Vision     │  │  Input Control  │
│  Engine     │  │  (PyAutoGUI)    │
│ OCR+模板比對 │  │  滑鼠/鍵盤操作   │
└─────────────┘  └─────────────────┘
```

### 核心分層

- **GUI 層**：使用者介面，勾選任務、查看日誌、開始/停止
- **排程層**：管理任務執行順序，處理任務間的依賴
- **任務模組層**：每個功能（日常、戰鬥、刷本）是獨立模組，方便擴充和維護
- **基礎設施層**：視覺辨識引擎和輸入控制，所有任務模組共用

### 設計原則

- 任務模組之間互不依賴，可以單獨開發、測試、更新
- 視覺辨識結果和操作邏輯分離 — 遊戲更新時只需調整辨識參數，不用改邏輯
- 所有可配置的值（座標、閾值、延遲）集中在 config 檔，不寫死在程式碼中

## 視覺辨識引擎

### 雙軌辨識系統

**OCR 路徑（PaddleOCR）：**
- 用途：選單文字、事件選項、任務名稱、數值（體力/貨幣）
- 優勢：遊戲改 UI 但文字不變 → 不受影響

**模板比對路徑（OpenCV matchTemplate）：**
- 用途：按鈕圖示、戰鬥視覺信號（閃避提示/大招可用）、小地圖標記、特定 UI 元素
- 容錯：多閾值匹配 + 灰階比對，降低色調變化的影響

### 辨識策略優先級

1. 文字場景優先用 OCR — 選單導航、事件選擇、任務確認
2. 視覺信號用模板比對 — 戰鬥中的即時反應（閃避提示是光效，沒有文字）
3. Fallback 機制 — 如果主要辨識方式失敗，嘗試備用方式；都失敗則暫停並通知使用者

### 截圖素材管理

- 所有模板圖片存放在 `assets/templates/` 目錄，按功能分資料夾
- 遊戲更新後只需替換對應的模板圖片，不用改程式碼
- 提供一個截圖工具，方便使用者自己擷取新模板

## 任務模組設計

### 日常任務模組 (`tasks/daily/`)

| 子任務 | 類別 | 說明 |
|--------|------|------|
| 每日活躍任務 | `ActiveMissions` | 偵測未完成任務 → 導航 → 執行 → 領獎 |
| 咖啡廳 | `CafeManager` | 收取營收 → 互動角色 |
| 刮刮樂 | `ScratchCard` | 自動刮開 |
| 影碟店 | `VideoStore` | 自動處理 |
| 郵件/免費抽 | `MailCollector` | 領取所有郵件 → 免費抽取 |

每個子任務是獨立的類別，`DailyTaskRunner` 依序呼叫，任一失敗不影響其他任務繼續執行。

### 戰鬥模組 (`tasks/combat/`)

使用**規則式狀態機**：

```
CombatController States:
  IDLE       — 等待戰鬥開始
  COMBO      — 執行當前角色的連招序列
  DODGE      — 偵測到閃避提示 → 極限閃避
  ULTIMATE   — 能量滿 → 施放大招
  SWITCH     — 連攜攻擊 / 切人時機
  QTE        — 偵測 QTE 提示 → 按鍵反應
  FINISHED   — 戰鬥結束

State Transitions:
  COMBO 中偵測到黃光 → DODGE
  DODGE 後 → 回到 COMBO
  偵測到能量滿 → ULTIMATE → 回到 COMBO
  偵測到連攜提示 → SWITCH
  偵測到 QTE → QTE → 回到 COMBO
```

#### 角色連招設定（YAML）

```yaml
# combos/ellen.yaml
character: "艾蓮"
combo_sequence:
  - { action: "attack", count: 3, interval: 0.15 }
  - { action: "skill", hold: true, duration: 0.5 }
  - { action: "attack", count: 2, interval: 0.15 }
  - { action: "dash", direction: "forward" }
priority_reactions:
  dodge_signal: 10    # 最高優先
  ultimate_ready: 8
  qte_prompt: 9
  switch_prompt: 7
```

架構上預留空間，未來可擴充強化學習作為進階戰鬥模組。

### 副本模組 (`tasks/dungeon/`)

| 副本 | 類別 | 流程 |
|------|------|------|
| 零號空洞 | `HollowZero` | 進入 → 選難度 → 探索節點 → 事件選擇(OCR) → 戰鬥 → 獎勵 → 下一層/結束 |
| 影像實戰 | `CombatSimulation` | 選副本 → 選難度 → 戰鬥 → 領獎 → 檢查體力 → 重複/結束 |
| 定期挑戰 | `PeriodicChallenge` | 選關卡 → 選隊伍 → 戰鬥 → 領獎 |

**體力管理：** 所有需要消耗體力的任務共用一個體力追蹤器，體力不足時自動停止刷本任務。

## GUI 設計

使用 PyQt6，主視窗分為三個區域：

```
┌──────────────────────────────────────────────┐
│  ZZZ AutoPlayer                    ─  □  ✕   │
├──────────┬───────────────────────────────────┤
│          │                                   │
│ 任務列表  │         狀態/日誌區               │
│ ☑ 日常全部 │  [14:03:22] 開始執行日常任務...    │
│   ☑ 活躍  │  [14:03:25] 咖啡廳：收取營收完成   │
│   ☑ 咖啡廳│  [14:03:30] 郵件：領取 3 封        │
│   ☑ 刮刮樂│  [14:05:10] 開始影像實戰 - 第1輪   │
│   ☑ 影碟店│  [14:07:45] 戰鬥完成，獲得獎勵     │
│   ☑ 郵件  │  [14:07:50] 體力剩餘：120         │
│ ☑ 刷本    │                                   │
│   ☑ 影像  │                                   │
│   ☑ 零號  │                                   │
│   ☑ 定期  │                                   │
│ ☑ 戰鬥設定│                                   │
│          │                                   │
├──────────┴───────────────────────────────────┤
│  [▶ 開始]  [⏹ 停止]  [⚙ 設定]     體力: 240  │
└──────────────────────────────────────────────┘
```

- **左側**：樹狀任務勾選，支援全選/單選
- **右側**：即時日誌滾動顯示，帶時間戳
- **底部**：開始/停止按鈕、設定入口、體力顯示
- **設定視窗**：角色連招編輯、辨識閾值調整、延遲參數

### 執行緒設計

- GUI 跑在主執行緒
- 任務執行跑在獨立的 Worker 執行緒
- 透過 Qt Signal/Slot 通訊，避免 GUI 卡死

## 設定管理

### `config/settings.yaml`

```yaml
# 通用設定
game:
  resolution: [1920, 1080]
  language: "zh-TW"

# 辨識參數
vision:
  ocr_confidence: 0.75
  template_threshold: 0.80
  screenshot_interval: 0.1

# 操作參數
input:
  click_delay: 0.05
  action_delay: 0.2
  loading_timeout: 15

# 刷本設定
dungeon:
  max_stamina_usage: 240
  hollow_zero_difficulty: 3
  combat_sim_repeat: 6
```

## 容錯機制

| 錯誤類型 | 處理方式 |
|----------|----------|
| 畫面卡住（連續 N 秒無變化） | 嘗試按 ESC → 重新辨識 → 仍失敗則暫停通知 |
| 辨識失敗（找不到預期 UI） | 等待 2 秒重試 → 切換辨識方式（OCR↔模板） → 重試 3 次仍失敗 → 截圖保存 → 跳過 |
| 意外彈窗（公告/活動通知） | OCR 偵測「確認/關閉」按鈕 → 自動關閉 → 恢復流程 |
| 遊戲崩潰/斷線 | 偵測遊戲視窗消失 → 等待 → 重啟遊戲 → 從頭執行 |

## 日誌系統

- 所有操作寫入 `logs/YYYY-MM-DD.log`
- 辨識失敗時自動截圖保存到 `logs/screenshots/`，方便除錯
- GUI 即時顯示簡要日誌，完整日誌在檔案中

## 專案結構

```
zzz/
├── main.py                    # 入口點
├── requirements.txt
├── build.spec                 # PyInstaller 打包設定
│
├── gui/
│   ├── main_window.py         # 主視窗
│   ├── settings_dialog.py     # 設定視窗
│   └── worker.py              # 任務執行緒
│
├── core/
│   ├── vision.py              # 視覺辨識引擎（OCR + 模板比對）
│   ├── input_controller.py    # 滑鼠鍵盤控制
│   ├── game_state.py          # 遊戲狀態管理
│   └── scheduler.py           # 任務排程器
│
├── tasks/
│   ├── base_task.py           # 任務基底類別
│   ├── daily/
│   │   ├── active_missions.py
│   │   ├── cafe_manager.py
│   │   ├── scratch_card.py
│   │   ├── video_store.py
│   │   └── mail_collector.py
│   ├── combat/
│   │   ├── combat_controller.py  # 戰鬥狀態機
│   │   └── combo_loader.py       # 連招設定載入
│   └── dungeon/
│       ├── hollow_zero.py
│       ├── combat_simulation.py
│       └── periodic_challenge.py
│
├── config/
│   ├── settings.yaml
│   └── combos/
│       ├── ellen.yaml
│       └── ...
│
├── assets/
│   └── templates/
│       ├── combat/
│       ├── menus/
│       └── dungeons/
│
└── logs/
```

## 技術棧

| 用途 | 套件 |
|------|------|
| GUI | PyQt6 |
| 截圖 | mss |
| OCR | PaddleOCR |
| 模板比對 | OpenCV (cv2) |
| 滑鼠鍵盤 | PyAutoGUI |
| 設定檔 | PyYAML |
| 日誌 | logging (內建) |
| 打包 | PyInstaller |

## Windows 打包

在 Windows 上執行：

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller build.spec
```

產出在 `dist/ZZZ-AutoPlayer/` 資料夾，壓縮後即可分發。

### 打包產出結構

```
dist/
└── ZZZ-AutoPlayer/
    ├── ZZZ-AutoPlayer.exe
    ├── assets/
    │   └── templates/
    ├── config/
    │   ├── settings.yaml
    │   └── combos/
    └── logs/
```

使用者下載 zip → 解壓 → 雙擊 `.exe` → 直接用，不需要安裝 Python。
