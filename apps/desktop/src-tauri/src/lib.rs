use serde_json::Value;

/// 只读 IPC：返回内容库 JSON（T-SHELL-4）。
///
/// 目前直接内嵌构建期生成的 `src/generated/content.json`；
/// 后续可改为运行时从内容目录/用户数据目录读取与合并。
#[tauri::command]
fn content_load() -> Result<Value, String> {
    const RAW: &str = include_str!("../../src/generated/content.json");
    serde_json::from_str(RAW).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![content_load])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
