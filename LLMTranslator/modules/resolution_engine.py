import re
from typing import List, Tuple, Dict, Set
from collections import deque


class ResolutionEngine:
    """
    МОДУЛЬ 2: Улучшенный движок резолюций с приоритетом единичных клауз
    """

    def __init__(self):
        self.steps_log = []
        self.step_number = 0

    def _log_step(self, message: str):
        """Логирует шаг доказательства"""
        self.step_number += 1
        step_msg = f"Шаг {self.step_number}: {message}"
        self.steps_log.append(step_msg)
        print(f"⚡ {step_msg}")

    def parse_formula(self, formula: str) -> List[Tuple]:
        """
        Парсит логическую формулу в клаузы
        """
        formula = formula.strip()

        # Обработка импликации без квантора
        if '→' in formula and not formula.startswith('∀'):
            left, right = formula.split('→')
            left = left.strip()
            right = right.strip()
            # A → B преобразуется в ¬A ∨ B
            return self.parse_formula(f"¬{left} ∨ {right}")

        # Обработка универсального квантора
        if formula.startswith('∀'):
            match = re.match(r'∀x\s*\((.*)\)', formula)
            if match:
                body = match.group(1)
                if '→' in body:
                    left, right = body.split('→')
                    left = left.strip()
                    right = right.strip()
                    return self.parse_formula(f"¬{left} ∨ {right}")

        # Обработка дизъюнкции
        if '∨' in formula:
            parts = formula.split('∨')
            return [self._parse_literal(part.strip()) for part in parts]

        # Базовый случай: одиночный литерал
        return [self._parse_literal(formula)]
    def _parse_literal(self, literal: str) -> Tuple[str, List[str], bool]:
        """Парсит отдельный литерал"""
        literal = literal.strip()
        negated = literal.startswith('¬')

        if negated:
            literal = literal[1:].strip()

        # Парсинг предиката с аргументами
        match = re.match(r'(\w+)\(([^)]*)\)', literal)
        if match:
            predicate = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(',')]
            return (predicate, args, negated)
        else:
            # Простой предикат
            return (literal, [], negated)

    def unify(self, args1: List[str], args2: List[str]) -> Dict[str, str]:
        """Упрощенная унификация"""
        if len(args1) != len(args2):
            return None

        substitution = {}
        for a1, a2 in zip(args1, args2):
            if a1 != a2:
                if a1.islower() and a1 not in substitution:  # a1 - переменная
                    substitution[a1] = a2
                elif a2.islower() and a2 not in substitution:  # a2 - переменная
                    substitution[a2] = a1
                else:
                    return None  # Две разные константы или конфликт подстановок
        return substitution

    def apply_substitution(self, clause: List[Tuple], substitution: Dict) -> List[Tuple]:
        """Применяет подстановку к клаузе"""
        if not substitution:
            return clause

        new_clause = []
        for pred, args, neg in clause:
            new_args = [substitution.get(arg, arg) for arg in args]
            new_clause.append((pred, new_args, neg))
        return new_clause

    def _is_unit_clause(self, clause: List[Tuple]) -> bool:
        """Проверяет, является ли клауза единичной (содержит только один литерал)"""
        return len(clause) == 1

    def _resolve(self, clause1: List[Tuple], clause2: List[Tuple]) -> List[Tuple]:
        """Пытается применить резолюцию к двум клаузам"""
        for i, (pred1, args1, neg1) in enumerate(clause1):
            for j, (pred2, args2, neg2) in enumerate(clause2):
                if pred1 == pred2 and neg1 != neg2:
                    substitution = self.unify(args1, args2)
                    if substitution is not None:
                        # Создаем резольвенту
                        new_clause = []

                        # Добавляем литералы из clause1 кроме i-го
                        for k, lit in enumerate(clause1):
                            if k != i:
                                new_clause.append(lit)

                        # Добавляем литералы из clause2 кроме j-го
                        for k, lit in enumerate(clause2):
                            if k != j:
                                # Проверяем на дубликаты
                                if lit not in new_clause:
                                    new_clause.append(lit)

                        # Применяем подстановку
                        resolved = self.apply_substitution(new_clause, substitution)
                        return resolved
        return None

    def _clause_to_str(self, clause: List[Tuple]) -> str:
        """Преобразует клаузу в строку"""
        if not clause:
            return "◻"  # Пустая клауза (противоречие)

        literals = []
        for pred, args, neg in clause:
            literal = ("¬" if neg else "") + pred
            if args:
                literal += f"({', '.join(args)})"
            literals.append(literal)

        return " ∨ ".join(literals)

    def prove(self, formulas: List[str]) -> Tuple[bool, List[str]]:
        """
        Улучшенный алгоритм доказательства методом резолюций с приоритетом единичных клауз
        """
        print("🧮 Модуль 2: Начинаю формальное доказательство...")
        self.steps_log = []
        self.step_number = 0

        # Парсинг всех формул
        clauses = []
        for formula in formulas:
            try:
                parsed = self.parse_formula(formula)
                if isinstance(parsed[0], list):  # Если вернулся список клауз
                    clauses.extend(parsed)
                else:  # Если вернулась одна клауза
                    clauses.append(parsed)
                self._log_step(f"Добавлена клауза: {self._clause_to_str(parsed)}")
            except Exception as e:
                self._log_step(f"Ошибка парсинга формулы '{formula}': {e}")

        if not clauses:
            self._log_step("Нет корректных клауз для доказательства")
            return False, self.steps_log

        # Разделяем клаузы на единичные и составные
        unit_clauses = [c for c in clauses if self._is_unit_clause(c)]
        non_unit_clauses = [c for c in clauses if not self._is_unit_clause(c)]

        self._log_step(f"Найдено {len(unit_clauses)} единичных и {len(non_unit_clauses)} составных клауз")

        # Создаем очереди с приоритетом для единичных клауз
        new_unit_queue = deque(unit_clauses)
        new_non_unit_queue = deque(non_unit_clauses)

        all_clauses = clauses.copy()
        all_clauses_set = set(self._clause_to_str(c) for c in clauses)

        max_steps = 50
        steps = 0

        while (new_unit_queue or new_non_unit_queue) and steps < max_steps:
            steps += 1

            # ПРИОРИТЕТ 1: Сначала берем единичные клаузы
            if new_unit_queue:
                current = new_unit_queue.popleft()
                clauses_to_check = all_clauses  # Проверяем со всеми клаузами
            elif new_non_unit_queue:
                current = new_non_unit_queue.popleft()
                # Для составных клауз проверяем только с единичными (стратегия unit preference)
                clauses_to_check = [c for c in all_clauses if self._is_unit_clause(c)]
                if not clauses_to_check:
                    clauses_to_check = all_clauses
            else:
                break

            for existing in clauses_to_check:
                if current == existing:
                    continue

                resolvent = self._resolve(current, existing)
                if resolvent is not None:
                    resolvent_str = self._clause_to_str(resolvent)

                    # ПРОВЕРКА НА ПУСТУЮ КЛАУЗУ (ПРОТИВОРЕЧИЕ)
                    if not resolvent:
                        self._log_step(
                            f"Резолюция: {self._clause_to_str(current)} и {self._clause_to_str(existing)} -> ◻")
                        self._log_step("🎉 НАЙДЕНО ПРОТИВОРЕЧИЕ! Доказательство завершено.")
                        return True, self.steps_log

                    # Если это новая клауза, добавляем ее
                    if resolvent_str not in all_clauses_set:
                        self._log_step(
                            f"Резолюция: {self._clause_to_str(current)} и {self._clause_to_str(existing)} -> {resolvent_str}")
                        all_clauses_set.add(resolvent_str)
                        all_clauses.append(resolvent)

                        # Добавляем в соответствующую очередь с приоритетом
                        if self._is_unit_clause(resolvent):
                            new_unit_queue.appendleft(resolvent)  # Единичные - в начало
                            self._log_step(f"→ Новая единичная клауза, добавляется в приоритетную очередь")
                        else:
                            new_non_unit_queue.append(resolvent)  # Составные - в конец

        self._log_step(f"Достигнут лимит в {max_steps} шагов. Противоречие не найдено.")
        self._log_step(f"Всего обработано клауз: {len(all_clauses)}")
        return False, self.steps_log

    def _remove_tautologies(self, clauses: List[List[Tuple]]) -> List[List[Tuple]]:
        """
        Удаляет тавтологии (клаузы, содержащие A и ¬A)
        """
        non_tautologies = []
        for clause in clauses:
            is_tautology = False
            for i, (pred1, args1, neg1) in enumerate(clause):
                for j, (pred2, args2, neg2) in enumerate(clause):
                    if i != j and pred1 == pred2 and neg1 != neg2:
                        # Проверяем унификацию аргументов
                        if self.unify(args1, args2) is not None:
                            is_tautology = True
                            break
                if is_tautology:
                    break
            if not is_tautology:
                non_tautologies.append(clause)
        return non_tautologies