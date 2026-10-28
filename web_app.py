import os
import json
import urllib.parse
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

DEFAULT_AFFILIATE_ID = "17335180070"

def resolve_url(url: str) -> str:
    """Giải mã các link rút gọn shp.ee / vn.shp.ee về link gốc Shopee."""
    clean = url.strip()
    if any(d in clean for d in ["shp.ee", "vn.shp.ee", "s.shopee.vn"]):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            res = requests.head(clean, allow_redirects=True, timeout=6, headers=headers)
            if res.url:
                clean = res.url
        except Exception:
            pass
    return clean

def build_affiliate_link(raw_url: str, affiliate_id: str, sub1: str = "", sub2: str = "") -> str:
    clean_url = resolve_url(raw_url)
    
    parsed = urllib.parse.urlparse(clean_url)
    clean_base = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    target_link = clean_base if clean_base.startswith("http") else clean_url

    encoded_origin = urllib.parse.quote(target_link, safe="")
    
    subs = [s.strip() for s in [sub1, sub2] if s.strip()]
    sub_tag = "-".join(subs)
    sub_param = f"&sub_id={sub_tag}" if sub_tag else ""
    
    aff_link = f"https://s.shopee.vn/an_redir?origin_link={encoded_origin}&affiliate_id={affiliate_id}{sub_param}"
    return aff_link

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#EE4D2D">
    <title>Shopee Affiliate App - Tạo Link Hoa Hồng</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #EE4D2D;
            --primary-gradient: linear-gradient(135deg, #EE4D2D 0%, #FF6533 100%);
            --primary-light: #FFF5F1;
            --bg: #F4F6F8;
            --card-bg: #FFFFFF;
            --text-main: #111827;
            --text-sub: #6B7280;
            --border: #E5E7EB;
            --success: #10B981;
            --radius-lg: 20px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --safe-bottom: env(safe-area-inset-bottom, 20px);
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            padding-bottom: calc(75px + var(--safe-bottom));
        }
        /* Mobile App Header */
        .app-header {
            background: var(--primary-gradient);
            color: white;
            padding: 20px 16px 24px;
            border-bottom-left-radius: 24px;
            border-bottom-right-radius: 24px;
            box-shadow: 0 4px 20px rgba(238, 77, 45, 0.25);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .app-title {
            font-size: 20px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.3px;
        }
        .account-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .dot {
            width: 7px;
            height: 7px;
            background: #4ADE80;
            border-radius: 50%;
            box-shadow: 0 0 6px #4ADE80;
        }
        .header-desc {
            font-size: 13px;
            opacity: 0.92;
            font-weight: 500;
        }
        /* Content Container */
        .app-container {
            max-width: 480px;
            width: 100%;
            margin: 16px auto 0;
            padding: 0 16px;
        }
        /* Tab Views */
        .tab-view {
            display: none;
        }
        .tab-view.active {
            display: block;
            animation: slideUp 0.25s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Cards */
        .mobile-card {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            border: 1px solid rgba(0,0,0,0.04);
            margin-bottom: 16px;
        }
        .input-title {
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .input-box-wrapper {
            position: relative;
            margin-bottom: 14px;
        }
        .url-input {
            width: 100%;
            padding: 14px 44px 14px 14px;
            font-size: 14px;
            border: 1.5px solid var(--border);
            border-radius: var(--radius-md);
            outline: none;
            transition: all 0.2s;
            background: #FAFAFA;
        }
        .url-input:focus {
            border-color: var(--primary);
            background: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(238, 77, 45, 0.12);
        }
        .clear-btn {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: #E5E7EB;
            color: #6B7280;
            border: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 12px;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
        }
        .quick-actions {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }
        .chip-btn {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-main);
            cursor: pointer;
            transition: all 0.15s;
        }
        .chip-btn.active, .chip-btn:hover {
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--primary);
        }
        .sub-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }
        .sub-field label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-sub);
            margin-bottom: 4px;
        }
        .sub-input {
            width: 100%;
            padding: 10px 12px;
            font-size: 13px;
            border: 1.5px solid var(--border);
            border-radius: var(--radius-sm);
            outline: none;
            background: #FAFAFA;
        }
        .sub-input:focus {
            border-color: var(--primary);
            background: white;
        }
        /* Big Action Button */
        .btn-create {
            width: 100%;
            padding: 16px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            font-size: 16px;
            font-weight: 800;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 16px rgba(238, 77, 45, 0.35);
            transition: all 0.2s;
        }
        .btn-create:active {
            transform: scale(0.98);
        }
        /* Result Box Mobile */
        .result-card {
            display: none;
            background: var(--primary-light);
            border: 1.5px dashed var(--primary);
            border-radius: var(--radius-lg);
            padding: 18px;
            margin-top: 16px;
            animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .result-card.show {
            display: block;
        }
        @keyframes popIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        .result-badge {
            font-size: 13px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .result-text-box {
            background: white;
            padding: 12px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 700;
            color: var(--primary);
            word-break: break-all;
            margin-bottom: 12px;
            border: 1px solid rgba(238,77,45,0.2);
        }
        .result-btn-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .btn-action-copy {
            background: var(--success);
            color: white;
            border: none;
            padding: 12px;
            border-radius: var(--radius-sm);
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .btn-action-share {
            background: #2563EB;
            color: white;
            border: none;
            padding: 12px;
            border-radius: var(--radius-sm);
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        /* History View */
        .history-item-card {
            background: white;
            border-radius: var(--radius-md);
            padding: 14px;
            margin-bottom: 10px;
            border: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }
        .history-main {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
        }
        .history-link {
            font-size: 13px;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
            display: block;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .history-time {
            font-size: 11px;
            color: var(--text-sub);
            margin-top: 2px;
        }
        .btn-mini-copy {
            background: #E5E7EB;
            color: var(--text-main);
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
        }
        /* Mobile Bottom Nav Bar */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 65px;
            background: white;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 1000;
            padding-bottom: var(--safe-bottom);
            box-shadow: 0 -2px 10px rgba(0,0,0,0.03);
        }
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            color: var(--text-sub);
            text-decoration: none;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            width: 33.33%;
            padding: 6px 0;
            transition: color 0.15s;
        }
        .nav-item.active {
            color: var(--primary);
        }
        .nav-icon {
            font-size: 20px;
        }
        /* Toast Notification */
        .toast {
            position: fixed;
            top: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: #111827;
            color: white;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            z-index: 2000;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .toast.show {
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>
    <div class="toast" id="toast">✅ Đã sao chép vào bộ nhớ tạm!</div>

    <!-- Mobile Header -->
    <header class="app-header">
        <div class="header-top">
            <div class="app-title">🛍️ Shopee Affiliate</div>
            <div class="account-badge">
                <span class="dot"></span>
                <span>ID: {{ default_id }}</span>
            </div>
        </div>
        <p class="header-desc">Tạo link hoa hồng cực nhanh • Tối ưu cho Điện Thoại</p>
    </header>

    <div class="app-container">
        <!-- TAB 1: CONVERTER (MAIN) -->
        <div class="tab-view active" id="tab-convert">
            <div class="mobile-card">
                <div class="input-title">
                    <span>Link sản phẩm Shopee:</span>
                    <span style="font-size: 12px; font-weight: 600; color: var(--primary); cursor: pointer;" onclick="pasteFromClipboard()">📋 Dán Nhanh</span>
                </div>

                <div class="input-box-wrapper">
                    <input type="text" id="url-input" class="url-input" placeholder="Dán link shopee.vn/... hoặc vn.shp.ee/..." oninput="checkInput()">
                    <button class="clear-btn" id="clear-btn" onclick="clearInput()">✕</button>
                </div>

                <div class="quick-actions">
                    <span style="font-size: 12px; font-weight: 600; color: var(--text-sub); display: flex; align-items: center;">Gợi ý Sub ID:</span>
                    <button class="chip-btn" onclick="setSub('fb')">Facebook</button>
                    <button class="chip-btn" onclick="setSub('tiktok')">TikTok</button>
                    <button class="chip-btn" onclick="setSub('zalo')">Zalo</button>
                    <button class="chip-btn" onclick="setSub('group')">Nhóm</button>
                </div>

                <div class="sub-row">
                    <div class="sub-field">
                        <label>Sub ID 1 (Kênh):</label>
                        <input type="text" id="sub1-input" class="sub-input" placeholder="fb, tiktok...">
                    </div>
                    <div class="sub-field">
                        <label>Sub ID 2 (Chiến dịch):</label>
                        <input type="text" id="sub2-input" class="sub-input" placeholder="sale, post01...">
                    </div>
                </div>

                <button class="btn-create" onclick="createAffiliateLink()" id="btn-submit">
                    <span>🚀 TẠO LINK HOA HỒNG NGAY</span>
                </button>

                <!-- Result Box -->
                <div class="result-card" id="result-card">
                    <div class="result-badge">🎉 LINK HOA HỒNG CỦA BẠN:</div>
                    <div class="result-text-box" id="result-text">https://s.shopee.vn/an_redir?...</div>
                    <div class="result-btn-row">
                        <button class="btn-action-copy" onclick="copyCreatedLink()">📋 Sao Chép</button>
                        <button class="btn-action-share" onclick="shareCreatedLink()">📲 Chia Sẻ</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: HISTORY -->
        <div class="tab-view" id="tab-history">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h3 style="font-size: 16px; font-weight: 800;">📜 Lịch Sử Đã Tạo</h3>
                <button onclick="clearHistory()" style="background: none; border: none; color: #EF4444; font-size: 13px; font-weight: 700; cursor: pointer;">Xóa hết</button>
            </div>
            <div id="history-container">
                <!-- Items dynamically loaded -->
            </div>
        </div>

        <!-- TAB 3: SETTINGS -->
        <div class="tab-view" id="tab-settings">
            <div class="mobile-card">
                <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 12px;">⚙️ Thông Tin Tài Khoản</h3>
                <div style="font-size: 13px; color: var(--text-sub); line-height: 1.5; margin-bottom: 16px;">
                    Mã <b>Affiliate ID</b> được dùng để ghi nhận 100% hoa hồng về tài khoản của bạn khi người khác click vào mua hàng.
                </div>
                <div class="sub-field" style="margin-bottom: 14px;">
                    <label>Affiliate ID của bạn:</label>
                    <input type="text" id="aff-id-input" class="url-input" value="{{ default_id }}" style="font-weight: 700; color: var(--primary);">
                </div>
                <button class="btn-create" style="padding: 12px; font-size: 14px;" onclick="saveAffId()">💾 Lưu Cài Đặt</button>
            </div>
        </div>
    </div>

    <!-- Mobile Bottom Navigation Bar -->
    <nav class="bottom-nav">
        <div class="nav-item active" onclick="switchTab('convert', this)">
            <span class="nav-icon">⚡</span>
            <span>Tạo Link</span>
        </div>
        <div class="nav-item" onclick="switchTab('history', this)">
            <span class="nav-icon">📜</span>
            <span>Lịch Sử</span>
        </div>
        <div class="nav-item" onclick="switchTab('settings', this)">
            <span class="nav-icon">⚙️</span>
            <span>Cài Đặt</span>
        </div>
    </nav>

    <script>
        let currentAffId = localStorage.getItem('shopee_aff_id') || "{{ default_id }}";
        let lastCreatedLink = "";

        document.getElementById('aff-id-input').value = currentAffId;

        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.classList.add('show');
            setTimeout(() => { toast.classList.remove('show'); }, 2000);
        }

        function switchTab(tabName, el) {
            document.querySelectorAll('.tab-view').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            el.classList.add('active');
            if (tabName === 'history') {
                renderHistory();
            }
        }

        function checkInput() {
            const val = document.getElementById('url-input').value;
            document.getElementById('clear-btn').style.display = val ? 'flex' : 'none';
        }

        function clearInput() {
            document.getElementById('url-input').value = '';
            document.getElementById('clear-btn').style.display = 'none';
        }

        async function pasteFromClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                if (text) {
                    document.getElementById('url-input').value = text.trim();
                    checkInput();
                    showToast('📋 Đã dán link!');
                }
            } catch (err) {
                alert('Vui lòng chạm giữ ô nhập liệu rồi chọn "Dán" (Paste).');
            }
        }

        function setSub(tag) {
            document.getElementById('sub1-input').value = tag;
        }

        async function createAffiliateLink() {
            const url = document.getElementById('url-input').value.trim();
            if (!url) {
                alert('Vui lòng dán link sản phẩm Shopee!');
                return;
            }

            const sub1 = document.getElementById('sub1-input').value.trim();
            const sub2 = document.getElementById('sub2-input').value.trim();
            const btn = document.getElementById('btn-submit');

            btn.disabled = true;
            btn.innerHTML = '<span>⏳ Đang tạo link...</span>';

            try {
                const res = await fetch('/api/convert', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: url,
                        affiliate_id: currentAffId,
                        sub1: sub1,
                        sub2: sub2
                    })
                });

                const data = await res.json();
                btn.disabled = false;
                btn.innerHTML = '<span>🚀 TẠO LINK HOA HỒNG NGAY</span>';

                if (data.success) {
                    lastCreatedLink = data.affiliate_link;
                    document.getElementById('result-text').innerText = lastCreatedLink;
                    document.getElementById('result-card').classList.add('show');

                    // Tự động sao chép
                    navigator.clipboard.writeText(lastCreatedLink).catch(() => {});
                    showToast('✅ Đã tạo & tự động sao chép!');

                    // Haptic feedback trên điện thoại
                    if (navigator.vibrate) navigator.vibrate(50);

                    // Lưu lịch sử
                    saveHistory(url, lastCreatedLink);
                } else {
                    alert('Lỗi: ' + (data.error || 'Không thể tạo link'));
                }
            } catch (err) {
                btn.disabled = false;
                btn.innerHTML = '<span>🚀 TẠO LINK HOA HỒNG NGAY</span>';
                alert('Lỗi kết nối máy chủ: ' + err.message);
            }
        }

        function copyCreatedLink() {
            if (lastCreatedLink) {
                navigator.clipboard.writeText(lastCreatedLink);
                showToast('📋 Đã sao chép link!');
            }
        }

        async function shareCreatedLink() {
            if (lastCreatedLink && navigator.share) {
                try {
                    await navigator.share({
                        title: 'Mua sắm Shopee',
                        text: 'Xem deal hot trên Shopee tại đây:',
                        url: lastCreatedLink
                    });
                } catch (err) {}
            } else {
                copyCreatedLink();
            }
        }

        function saveAffId() {
            const id = document.getElementById('aff-id-input').value.trim();
            if (!id) {
                alert('Vui lòng nhập Affiliate ID');
                return;
            }
            currentAffId = id;
            localStorage.setItem('shopee_aff_id', id);
            showToast('💾 Đã lưu Affiliate ID: ' + id);
            switchTab('convert', document.querySelectorAll('.nav-item')[0]);
        }

        function getHistoryList() {
            try {
                return JSON.parse(localStorage.getItem('shopee_m_history')) || [];
            } catch {
                return [];
            }
        }

        function saveHistory(orig, aff) {
            let hist = getHistoryList();
            hist.unshift({
                orig: orig,
                aff: aff,
                time: new Date().toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'})
            });
            hist = hist.slice(0, 30);
            localStorage.setItem('shopee_m_history', JSON.stringify(hist));
        }

        function clearHistory() {
            if (confirm('Bạn có chắc muốn xóa lịch sử?')) {
                localStorage.removeItem('shopee_m_history');
                renderHistory();
            }
        }

        function renderHistory() {
            const container = document.getElementById('history-container');
            const hist = getHistoryList();
            if (hist.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-sub); padding: 30px; font-size: 13px;">Chưa có link nào được tạo.</div>';
                return;
            }
            container.innerHTML = hist.map(item => `
                <div class="history-item-card">
                    <div class="history-main">
                        <a href="${item.aff}" target="_blank" class="history-link">${item.aff}</a>
                        <div class="history-time">🕒 ${item.time}</div>
                    </div>
                    <button class="btn-mini-copy" onclick="navigator.clipboard.writeText('${item.aff}'); showToast('📋 Đã chép link!');">Chép</button>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, default_id=DEFAULT_AFFILIATE_ID)

@app.route("/api/convert", methods=["POST"])
def api_convert():
    try:
        data = request.get_json() or {}
        raw_url = data.get("url", "").strip()
        aff_id = data.get("affiliate_id", DEFAULT_AFFILIATE_ID).strip() or DEFAULT_AFFILIATE_ID
        sub1 = data.get("sub1", "").strip()
        sub2 = data.get("sub2", "").strip()

        if not raw_url:
            return jsonify({"success": False, "error": "Vui lòng nhập đường link Shopee"}), 400

        aff_link = build_affiliate_link(raw_url, aff_id, sub1, sub2)
        return jsonify({
            "success": True,
            "affiliate_link": aff_link,
            "original_url": raw_url,
            "affiliate_id": aff_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
