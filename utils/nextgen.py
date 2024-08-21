from typing import List


def get_next_item(current_item: str, items_list: List[str]):
    # Проверяем, есть ли текущий элемент в списке
    if current_item in items_list:
        # Получаем индекс текущего элемента
        current_index = items_list.index(current_item)
        # Рассчитываем индекс следующего элемента с учётом кольцевого перехода
        next_index = (current_index + 1) % len(items_list)
        # Возвращаем следующий элемент
        return items_list[next_index]
    else:
        # Если текущего элемента нет в списке, возвращаем None или другое значение по умолчанию
        return None