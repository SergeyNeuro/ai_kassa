"""
filters.py — модуль фильтрации детекций.

Задача:
  - Исключить все контейнеры (тег 'empty_bbox')
  - Исключить все блюда, центры которых попадают внутрь контейнеров

Используется в yolo_predicter.py после инференса YOLO.
"""

from dataclasses import dataclass
from typing import List, Tuple

# Константа — тег контейнера (класс YOLO)
IGNORE_TAG = "empty_bbox"


# --------------------------- КЛАССЫ -----------------------------------
@dataclass(frozen=True)
class BBox:
    """Прямоугольная область (x1, y1, x2, y2)."""
    x1: int
    y1: int
    x2: int
    y2: int

    def center(self) -> Tuple[int, int]:
        """Вычисляет центр прямоугольника (cx, cy)."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def contains_point(self, x: int, y: int) -> bool:
        """Проверяет, находится ли точка (x, y) внутри bbox."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


@dataclass(frozen=True)
class RawDet:
    """
    Сырая детекция из модели YOLO (до маппинга на блюдо).
    Используется для фильтрации.
    """
    class_name: str  # название класса (например, 'borsch' или 'empty_bbox')
    conf: float      # уверенность модели
    bbox: BBox       # координаты прямоугольника


class EmptyBoxFilter:
    """
    Фильтр, исключающий контейнеры и блюда внутри контейнеров (empty_bbox).
    """

    def __init__(self, ignore_tag: str = IGNORE_TAG):
        """
        Args:
            ignore_tag: имя тега, который обозначает контейнер (по умолчанию 'empty_bbox')
        """
        self.ignore_tag = ignore_tag

    def filter(self, detections: List[RawDet]) -> List[RawDet]:
        """
        Основной метод фильтрации. На вход получает список детекций YOLO, удаляет те, 
        центр которых находится внутри контейнера (empty_bbox).

        Args:
            detections: список всех детекций (RawDet)

        Returns:
            Новый список детекций без контейнеров и без объектов,
            центры которых попадают внутрь контейнеров.
        """
        if not detections:
            return detections

        # Отбираем контейнеры и обычные объекты
        containers = [d for d in detections if d.class_name == self.ignore_tag]
        others = [d for d in detections if d.class_name != self.ignore_tag]

        if not containers:
            # Контейнеров нет — возвращаем как есть
            return others

        # Проверяем каждую детекцию: не лежит ли центр внутри контейнера
        kept = []
        for det in others:
            cx, cy = det.bbox.center()
            inside_any = any(c.bbox.contains_point(cx, cy) for c in containers)
            if not inside_any:
                kept.append(det)

        return kept