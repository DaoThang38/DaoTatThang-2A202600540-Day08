import json
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

articles = [
    {
        "url": "https://vnexpress.net/khoi-to-ca-si-chi-dan-an-tay-vi-tang-tru-ma-tuy-4827561.html",
        "title": "Khởi tố ca sĩ Chi Dân và người mẫu An Tây vì tàng trữ ma túy",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Khởi tố ca sĩ Chi Dân và người mẫu An Tây vì tàng trữ ma túy

Ca sĩ Chi Dân (tên thật Nguyễn Trọng Hiếu) và người mẫu An Tây (tên thật Trần Thị Ngọc Bích) bị Cơ quan CSĐT Công an TP HCM khởi tố, bắt tạm giam về tội tàng trữ trái phép chất ma túy.

Ngày 14/11/2024, Cơ quan Cảnh sát điều tra Công an TP HCM ra quyết định khởi tố vụ án, khởi tố bị can và thực hiện lệnh bắt bị can để tạm giam đối với Nguyễn Trọng Hiếu (sinh năm 1987, nghệ danh Chi Dân) và Trần Thị Ngọc Bích (sinh năm 1996, nghệ danh An Tây) về tội Tàng trữ trái phép chất ma túy, theo khoản 2 Điều 249 Bộ luật Hình sự.

Theo tài liệu điều tra, tối ngày 13/11/2024, lực lượng công an phát hiện tại căn hộ ở TP HCM nơi Chi Dân và An Tây đang có mặt, có chứa các chất bị nghi là ma túy tổng hợp. Qua kiểm tra, cơ quan điều tra thu giữ một số chất ma túy gồm ketamine và một số loại ma túy tổng hợp khác.

Chi Dân là ca sĩ nổi tiếng với các bài hit như Người Tôi Yêu, Chưa Bao Giờ. An Tây là người mẫu, influencer có hàng triệu người theo dõi trên mạng xã hội. Cả hai đang bị tạm giam để phục vụ công tác điều tra.

Đây là vụ việc gây chấn động làng giải trí Việt Nam cuối năm 2024, một lần nữa gióng lên hồi chuông cảnh báo về tệ nạn ma túy trong giới nghệ sĩ.
""",
    },
    {
        "url": "https://vnexpress.net/huu-tin-linh-7-nam-6-thang-tu-4601099.html",
        "title": "Diễn viên Hữu Tín lĩnh 7 năm 6 tháng tù vì tổ chức sử dụng ma túy",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Diễn viên Hữu Tín lĩnh 7 năm 6 tháng tù vì tổ chức sử dụng ma túy

TAND TP HCM tuyên phạt diễn viên Nguyễn Hữu Tín 7 năm 6 tháng tù giam về tội Tổ chức sử dụng trái phép chất ma túy.

Ngày 28/4/2023, TAND TP HCM đã mở phiên toà xét xử và tuyên phạt diễn viên Nguyễn Hữu Tín (sinh năm 1986) mức án 7 năm 6 tháng tù giam về tội Tổ chức sử dụng trái phép chất ma túy theo khoản 2 Điều 255 Bộ luật Hình sự.

Theo cáo trạng, từ tháng 1 đến tháng 3/2022, Hữu Tín đã tổ chức cho nhiều người sử dụng ma túy tại căn hộ do anh ta thuê tại TP HCM. Cơ quan điều tra đã thu giữ nhiều tang vật gồm ma túy tổng hợp và các dụng cụ sử dụng ma túy.

Hữu Tín từng được biết đến qua nhiều bộ phim truyền hình. Vụ việc xảy ra đã khiến nhiều người trong giới showbiz và khán giả bàng hoàng.
""",
    },
    {
        "url": "https://vnexpress.net/chau-viet-cuong-linh-13-nam-tu-4365729.html",
        "title": "Châu Việt Cường lĩnh 13 năm tù vì nhét tỏi vào miệng cô gái đến chết",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Châu Việt Cường lĩnh 13 năm tù vì nhét tỏi vào miệng cô gái đến chết

Ca sĩ Châu Việt Cường bị TAND TP HCM tuyên phạt 13 năm tù về tội Giết người, trong tình trạng sử dụng ma túy.

Ngày 13/9/2021, TAND TP HCM tuyên phạt ca sĩ Châu Việt Cường (sinh năm 1987) 13 năm tù về tội Giết người. Theo bản án, vào tháng 3/2019, sau khi sử dụng ma túy (ketamine), Châu Việt Cường đã nhét tỏi vào miệng và mũi một cô gái khiến nạn nhân tử vong.

Cơ quan điều tra xác định trong lúc bị ảo giác do sử dụng ma túy, Châu Việt Cường đã có hành vi cực kỳ nguy hiểm dẫn đến cái chết của nạn nhân. Đây là một trong những vụ án nghiêm trọng nhất liên quan đến nghệ sĩ và ma túy tại Việt Nam.

Châu Việt Cường từng là ca sĩ nổi tiếng với ca khúc Tình Yêu Màu Hồng, trước khi bị bắt giữ vào năm 2019.
""",
    },
    {
        "url": "https://vnexpress.net/nghi-pham-ma-tuy-showbiz-bi-xu-ly-the-nao-4234040.html",
        "title": "Nghệ sĩ Việt dính líu ma túy bị xử lý như thế nào theo pháp luật?",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Nghệ sĩ Việt dính líu ma túy bị xử lý như thế nào theo pháp luật?

Hàng loạt nghệ sĩ Việt Nam bị xử lý hình sự vì liên quan đến ma túy những năm gần đây, với các mức án từ vài năm đến hơn chục năm tù.

Theo Bộ luật Hình sự 2015 (sửa đổi 2017), các tội danh liên quan đến ma túy trong giới nghệ sĩ thường gặp bao gồm:

- **Tàng trữ trái phép chất ma túy** (Điều 249): Phạt tù từ 1 đến 5 năm với lượng nhỏ; từ 5 đến 10 năm với lượng lớn hơn.
- **Tổ chức sử dụng trái phép chất ma túy** (Điều 255): Phạt tù từ 2 đến 7 năm; từ 7 đến 15 năm với tình tiết tăng nặng.

Các nghệ sĩ đã bị xử lý hình sự:
- Ca sĩ Chi Dân, người mẫu An Tây: bị khởi tố tội tàng trữ ma túy năm 2024.
- Diễn viên Hữu Tín: 7 năm 6 tháng tù vì tổ chức sử dụng ma túy.
- Ca sĩ Châu Việt Cường: 13 năm tù vì giết người trong lúc sử dụng ma túy.
""",
    },
    {
        "url": "https://vnexpress.net/tong-hop-nhung-nghe-si-viet-dinh-lieu-ma-tuy-4012040.html",
        "title": "Tổng hợp những nghệ sĩ Việt dính líu ma túy",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": """# Tổng hợp những nghệ sĩ Việt dính líu ma túy

Nhiều nghệ sĩ nổi tiếng Việt Nam đã bị bắt giữ, khởi tố hoặc kết án vì liên quan đến ma túy trong những năm gần đây.

## Danh sách nghệ sĩ bị bắt vì ma túy

**1. Chi Dân (Nguyễn Trọng Hiếu)** - Ca sĩ
Bị khởi tố và bắt tạm giam ngày 14/11/2024 về tội tàng trữ trái phép chất ma túy. Công an TP HCM thu giữ ketamine và ma túy tổng hợp tại căn hộ của Chi Dân.

**2. An Tây (Trần Thị Ngọc Bích)** - Người mẫu, influencer
Bị bắt cùng thời điểm với Chi Dân, bị khởi tố về tội tàng trữ trái phép chất ma túy năm 2024.

**3. Hữu Tín (Nguyễn Hữu Tín)** - Diễn viên
Bị kết án 7 năm 6 tháng tù năm 2023 vì tổ chức sử dụng trái phép chất ma túy tại căn hộ ở TP HCM.

**4. Châu Việt Cường** - Ca sĩ
Bị kết án 13 năm tù năm 2021 vì tội giết người sau khi sử dụng ma túy (ketamine) và gây ra cái chết cho nạn nhân.

Những vụ việc này đặt ra câu hỏi về văn hóa sử dụng chất kích thích trong giới giải trí và trách nhiệm của người nổi tiếng đối với xã hội.
""",
    },
]

out = Path("data/landing/news")
out.mkdir(parents=True, exist_ok=True)
for i, a in enumerate(articles, 1):
    f = out / f"article_{i:02d}.json"
    f.write_text(json.dumps(a, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {f.name} ({len(a['content_markdown'])} chars)")

print("Done! 5 articles created.")
