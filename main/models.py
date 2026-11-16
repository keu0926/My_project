from django.db import models

class Notice(models.Model):
    title = models.CharField("제목", max_length=200)
    category = models.CharField(
        "분류",
        max_length=20,
        choices=[
            ("학사일정", "학사일정"),
            ("생활안내", "생활안내"),
            ("입시정보", "입시정보"),
            ("일반공지", "일반공지"),
        ],
        default="일반공지",
    )
    content = models.TextField("내용")
    is_pinned = models.BooleanField("상단 중요 공지 고정", default=False)
    views = models.PositiveIntegerField("조회수", default=0)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "공지사항"
        verbose_name_plural = "공지사항 관리"
        # 중요 공지를 먼저 띄우고, 최신순으로 정렬
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title
